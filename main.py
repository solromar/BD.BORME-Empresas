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
    company_social_denomination_block_pattern = r'\n\d+\s+([A-ZÁÉÍÓÚÑ\s\d&.,()\x27-]+?)\n(?:[A-Z][a-z]|D\.|D\.ª|M\.|M\.ª)'
    company_social_denomination_block_match = re.search(company_social_denomination_block_pattern, inscription, re.MULTILINE | re.DOTALL)
    if company_social_denomination_block_match:
        company_social_denomination_block = " ".join(company_social_denomination_block_match.group(1).split()).replace(',', ', ')
    return company_social_denomination_block


def process_company_block(company_block):
    # Dividir la cadena usando ' Y ' como delimitador
    company_social_denomination_list = re.split(r'\s+Y\s+', company_block)

    # Limpiar y filtrar la lista para eliminar elementos vacíos o espacios adicionales
    company_social_denomination_list = [social_denomination.strip() for social_denomination in company_social_denomination_list if social_denomination]

    return company_social_denomination_list         
   
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
    
     
    # TODO: hacer company_name
   
       
    
    company_social_denomination_block_pattern = r'\n\d+\s+([A-ZÁÉÍÓÚÑ\s\d&.,()\x27-]+?)\n(?:[A-Z][a-z]|D\.|D\.ª|M\.|M\.ª)'
    company_social_denomination_block_match = re.search(company_social_denomination_block_pattern, inscription, re.MULTILINE | re.DOTALL)
    if company_social_denomination_block_match:
        company_block = company_social_denomination_block_match.group(1)
        company_social_denomination_list = process_company_block(company_block)
        print(company_social_denomination_list)
    
         
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
    
    companies = []  # Asegúrate de que esto esté fuera del bucle 
    for company_social_denomination in company_social_denomination_list:
        company = {
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "companySocialDenomination": company_social_denomination,
                #"companyName": company_name,
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
   
    
    #print(f"Agregado: {company}")  # Para depuración
    print("Compañías procesadas:", companies)
    return companies
    

@app.route('/')  # Defino la ruta
def home():
    pdf_path = "files/2009/12/01/pdfs/BORME-C-2009-35104.pdf"
    company = file_type_c(pdf_path)
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    
    
    return jsonify(company)


if __name__ == '__main__':
    app.run(debug=True)