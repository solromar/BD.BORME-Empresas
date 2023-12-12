from flask import Flask, jsonify
import pdfplumber
import re
import os
from datetime import datetime


app = Flask(__name__)

# Defino la función para extraer texto
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text    

def extract_company_block(inscription):
    company_social_denomination_block_pattern = r'\n\d+\s+([A-ZÁÉÍÓÚÑÀÈÌÒÙ´’\s\d&.,()\x27-]+?)\n(?:[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|D\.|D\.ª|M\.|M\.ª|Dña\.|\"[A-ZÁÉÍÓÚÑÀÈÌÒÙ]{2}\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|A\s+[a-záéíóúñàèìòù]|1\.\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù])'
    #company_social_denomination_block_pattern = r'\n\d+\s+([A-ZÁÉÍÓÚÑÀÈÌÒÙ´\s\d&.,()\'\x27-]+(?:\sST\.)?)[^)]*?\n(?:[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|D\.|D\.ª|M\.|M\.ª|Dña\.|\"[A-ZÁÉÍÓÚÑÀÈÌÒÙ]{2}\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|A\s+[a-záéíóúñàèìòù]|1\.\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù])'

    company_social_denomination_block_match = re.search(company_social_denomination_block_pattern, inscription, re.MULTILINE | re.DOTALL)
    if company_social_denomination_block_match:
        company_social_denomination_block = " ".join(company_social_denomination_block_match.group(1).split()).replace(',', ', ')
    return company_social_denomination_block

def process_company_block(company_block):
    # Reemplazar comas y saltos de línea con dos espacios
    company_block = company_block.replace(',\n', '  ').replace('\n', '  ').replace(',', '  ')
    
    # Eliminar contenido específico entre paréntesis
    phrases_to_exclude = r'\((SOCIEDAD ABSORBENTE|SOCIEDAD ABSORBIDA|SOCIEDADES ABSORBIDAS|SOCIEDAD BENEFICIARIA|SOCIEDAD ESCINDIDA|SOCIEDAD PARCIALMENTE ESCINDIDA|SOCIEDAD SEGREGADA|)[^)]*\)\.?'
    company_block = re.sub(phrases_to_exclude, '', company_block)

    # Definir la expresión regular para tipos de sociedades y 'Y' o 'E' como separadores
    company_types_and_y_e_pattern = r'(S\.L\.U\.|S\.A\.U\.|S\.L\.P\.| S\.L\. SOCIEDAD UNIPERSONAL|S\.A\. SOCIEDAD UNIPERSONAL|S\.L\.|S\.A\.|S\.C\.|S\.Coop\.|S\.LL\.|S\.C\.R\.L\.|FRANQUICIA INMOBILIARIA|SOCIEDAD LIMITADA|COMUNIDAD DE BIENES|SOCIEDAD ANONIMA|SOCIEDAD ANÓNIMA)(\s+(Y|E)\s+)'

    # Reemplazar 'Y' o 'E' que sigue a un tipo de sociedad con un espacio
    company_block = re.sub(company_types_and_y_e_pattern, r'\1 ', company_block)

    # Definir la expresión regular para tipos de sociedades
    company_types_pattern = r'(S\.L\.U\.|SCR, S\.A\.|S\.A\.U\.|S\.C\.P\.|S\.L\.P\.|S\.A\.L\.| S\.L\. SOCIEDAD UNIPERSONAL|S\.L\.  SOCIEDAD UNIPERSONAL|S\.A\. SOCIEDAD UNIPERSONAL|SOCIEDAD ANÓNIMA UNIPERSONAL|S\.L\.|S\.L|S\.A\.|S\. A\.|S\.C\.|S\.Coop\.|S\.LL\.|S\.C\.R\.L\.|FRANQUICIA INMOBILIARIA|SOCIEDAD LIMITADA| SOCIEDAD LIMITADA LABORAL|COMUNIDAD DE BIENES|SOCIEDAD ANONIMA|SOCIEDAD ANÓNIMA| SOCIEDAD LIMITADA UNIPERSONAL|SOCIEDAD COOPERATIVA ANDALUZA)'

    # Dividir la cadena usando los tipos de sociedades como delimitador
    company_social_denomination_list = re.split(company_types_pattern, company_block)

    # Reconstruir cada compañía y filtrar nombres no válidos o vacíos
    processed_companies = []
    company_names = []
    for i in range(0, len(company_social_denomination_list), 2):
        name = company_social_denomination_list[i].strip()
        type = company_social_denomination_list[i + 1].strip() if i + 1 < len(company_social_denomination_list) else ''

        if name and name != ".":
            full_name = f"{name} {type}" if type else name
            processed_companies.append(full_name)
            company_names.append(name)
            print(processed_companies,company_names )

    return processed_companies, company_names


# -------------------------------------------------- PROCESAMIENTO BORME C --------------------------------------------------------------

def file_type_c(pdf_path):
    companies = []    
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    
    
    # Extraer la fecha del Borme
    borme_date_pattern = r'(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s+(\d+)\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})'
    borme_date_match = re.search(borme_date_pattern, texto_del_pdf)
    
    if borme_date_match:
    # Extraemos el día, mes (en texto) y año
     day, month_text, year = borme_date_match.groups()[1:]
    # Convertimos el mes a su correspondiente número
     months = {"enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
              "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
              "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"}
     month = months[month_text.lower()]     
    # Formatear la fecha al formato DD/MM/YYYY
     borme_date = f"{day.zfill(2)}/{month}/{year}"     
    else:
     borme_date = "Fecha no encontrada"
     
        
    # Buscar Sección del Acto
    inscription_section_pattern = r'Pág\.\s+\d+\s+SECCIÓN\s+(PRIMERA|SEGUNDA)'
    inscription_section_match = re.search(inscription_section_pattern, texto_del_pdf)
    inscription_section = inscription_section_match.group(1) if inscription_section_match else "No encontrado"
    
    # Buscar Categoria del Acto
    inscription_category_pattern = r"SECCIÓN SEGUNDA -\s(.*?)\n"
    inscription_category_match = re.search(inscription_category_pattern, texto_del_pdf)
    inscription_category = inscription_category_match.group(1) if inscription_category_match else "No encontrado"    
    
    # Buscar Nombre del Acto
    inscription_name_pattern = r"SECCIÓN SEGUNDA - Anuncios y avisos legales\s+(.*?)\n[A-Z0-9]"
    inscription_name_match = re.search(inscription_name_pattern, texto_del_pdf)
    inscription_name = inscription_name_match.group(1) if inscription_name_match else "No encontrado"
    
    # Expresión regular para capturar cada acto en un texto plano
    inscription_pattern = r"SECCIÓN SEGUNDA - Anuncios y avisos legales\s+(.*?)\nID:"
    inscription_matches = re.search(inscription_pattern, texto_del_pdf, re.MULTILINE | re.DOTALL)
    inscription = inscription_matches.group(1) if inscription_matches else "No encontrado"
    
    # Extraer la fecha de la inscripcion
    inscription_date_original_pattern = r'(\d{1,2} de [a-z]+ de \d{4})\.-'
    inscription_date_original_match = re.search(inscription_date_original_pattern, inscription, re.IGNORECASE)
    inscription_date_original = inscription_date_original_match.group(1) if inscription_date_original_match else "No encontrada"
    # Diccionario para convertir el nombre del mes a número
    meses = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
}
# Expresión regular para extraer el día, mes y año desde el extraido originalmente
    inscription_date_pattern = r'(\d{1,2}) de ([a-z]+) de (\d{4})'
    inscription_date_match = re.search(inscription_date_pattern, inscription_date_original, re.IGNORECASE)
    if inscription_date_match:
     dia, mes_texto, año = inscription_date_match.groups()
     mes = meses[mes_texto.lower()]
     inscription_date = f"{dia.zfill(2)}/{mes}/{año}"
    else:
     inscription_date = "Fecha no válida"
    
    # Extraer el número de acto
    inscription_number_pattern = r'^(\d+)'
    inscription_number_match = re.search(inscription_number_pattern, inscription, re.MULTILINE)
    inscription_number= inscription_number_match.group(1)if inscription_number_match else "No encontrado"   
       
    
    
    company_social_denomination_block_pattern = r'\n\d+\s+([A-ZÁÉÍÓÚÑÀÈÌÒÙ´’\s\d&.,()\x27-]+?)\n(?:[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|D\.|D\.ª|M\.|M\.ª|Dña\.|\"[A-ZÁÉÍÓÚÑÀÈÌÒÙ]{2}\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|A\s+[a-záéíóúñàèìòù]|1\.\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù])'
    
    #company_social_denomination_block_pattern = r'\n\d+\s+([A-ZÁÉÍÓÚÑÀÈÌÒÙ´\s\d&.,()\'\x27-]+(?:\sST\.)?)[^)]*?\n(?:[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|D\.|D\.ª|M\.|M\.ª|Dña\.|\"[A-ZÁÉÍÓÚÑÀÈÌÒÙ]{2}\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù]|A\s+[a-záéíóúñàèìòù]|1\.\s+[A-ZÁÉÍÓÚÑÀÈÌÒÙ][a-záéíóúñàèìòù])'
    company_social_denomination_block_match = re.search(company_social_denomination_block_pattern, inscription, re.MULTILINE | re.DOTALL)
    if company_social_denomination_block_match:
        company_block = company_social_denomination_block_match.group(1)
        full_company_names, company_names = process_company_block(company_block)
        
    
         
        company_inscription = {
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inscriptionCommercialRegistry": None,
                "inscriptionNumber": inscription_number,
                "inscriptionSection": inscription_section,
                "inscriptionCategory": inscription_category,
                "inscriptionName": inscription_name,
                "inscriptionDate": inscription_date,
                "inscriptionRegistryData": None,
                "inscription": inscription,
                "bormeDate": borme_date,
                "inscriptionFile": os.path.basename(pdf_path)
            } 
    
    companies = []  
    for company_social_denomination, company_name in zip(full_company_names, company_names):
        company = {
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "companySocialDenomination": company_social_denomination,
                "companyName": company_name,
                "companyNif": None,
                "companyCurrentAddress": None,
                "companyCurrentSocialObject": None,
                "companyCurrentSocialCapital": None,
                "companyPhoneNumber": None,
                "companyEmail": None,
                "companyWeb": None,
                "companyEmployeesNumber": None,
                "companyParent": None,
                "constitutionCommercialRegistry": None ,
                "constitutionDate": None,
                "constitutionRegistryData": None,
                "constitutionInscription": None, 
                "operationsStartDate": None,
                "companyDuration": None,
                "constitutionAddress": None,
                "constitutionSocialObject": None,
                "constitutionSocialCapital":None,
                "constitutionFile": None,          
                "companyState": None,
                "administration": None,
                "administratorsList": None,
                "administrationAppointmentDate": None,
                "administrationAppointmentInscription": None,
                "administrationAppointmentFile": None,
                "companyInscription": [company_inscription]
            }
        companies.append(company)
    
    return companies
    

@app.route('/')  # Defino la ruta
def home():
    pdf_path = "files/2023/10/26/pdfs/BORME-C-2023-6352.pdf"
    company = file_type_c(pdf_path)
    
    return jsonify(company)


if __name__ == '__main__':
    app.run(debug=True)