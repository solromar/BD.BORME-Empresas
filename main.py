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

def extract_italic_titles(pdf_path):
    titles = []
    current_title = ""
    title_started = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for char in page.chars:
                if 'Italic' in char['fontname']:
                    current_title += char['text']
                    title_started = True
                elif title_started:
                    titles.append(current_title.strip())
                    current_title = ""
                    title_started = False

    # Asegurarse de añadir el último título si termina en la última página
    if current_title:
        titles.append(current_title.strip())

    return titles
 
# -------------------------------------------------- PROCESAMIENTO BORME B --------------------------------------------------------------

def file_type_b(pdf_path):
    companies = []
    
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    
    #print (texto_del_pdf)
    
    
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
     print(borme_date)
    else:
     borme_date = "Fecha no encontrada"
     
    # Buscar la provincia del Acto
    inscription_commercial_registry_pattern = r'Empresarios\s+Otros actos publicados en el Registro Mercantil\s+([A-ZÁÉÍÓÚÜ\s]+)\n'
    inscription_commercial_registry_match = re.search(inscription_commercial_registry_pattern, texto_del_pdf)
    inscription_commercial_registry = inscription_commercial_registry_match.group(1) if inscription_commercial_registry_match else "No encontrado"
    print(inscription_commercial_registry)
    # Buscar Sección del Acto
    inscription_section_pattern = r'Pág\.\s+\d+\s+SECCIÓN\s+(PRIMERA|SEGUNDA)'
    inscription_section_match = re.search(inscription_section_pattern, texto_del_pdf)
    inscription_section = inscription_section_match.group(1) if inscription_section_match else "No encontrado"
    print(inscription_section)
    # Buscar Categoria del Acto
    inscription_category_pattern = r'Empresarios\s+(.*)\s+'
    inscription_category_match = re.search(inscription_category_pattern, texto_del_pdf)
    inscription_category = inscription_category_match.group(1) if inscription_category_match else "No encontrado"
    print(inscription_category)
    
    # Buscar todos los actos inscritos y extraer informacion
    inscription_pattern = r'(\d{5}) - ([^(\n]+) \((\d{4})\)'
    inscriptions = re.findall(inscription_pattern, texto_del_pdf)
    print(inscriptions)
    
    for inscription in inscriptions:
    # Expresión regular para buscar el número de inscripción
        inscription_number_pattern = r'/^\d+/m'
        number_match = re.search(inscription_number_pattern, inscription)
        if number_match:
         inscription_number = number_match.group(1)
        else:
         inscription_number = 'Número no encontrado'
            
    # Expresión regular para buscar la denominación social completa
        full_name_pattern = r'/^\d+\s-\s(.*)(\R|$)/m'
        full_name_match = re.search(full_name_pattern, inscription, re.IGNORECASE)
    
        if full_name_match:
         company_social_denomination = full_name_match.group(1).strip()
        else:
         company_social_denomination = 'Denominación no encontrada'
    # Expresión regular para buscar solo el nombre de la empresa (sin SL, Sociedad Limitada, etc.)
        name_pattern = r'^\d+ - (.*?)(?:,? (SOCIEDAD LIMITADA|SL|SLL|SL EN LIQUIDACION|SLNE|SLNE EN LIQUIDACION|SA|SA EN LIQUIDACION|SOCIEDAD LIMITADA LABORAL|SOCIEDAD ANONIMA|S\.L\.|S\.L\.L\.|S\.A\.|S\.A\.A\.|S\.L\.L\.))?\.\n'
        name_match = re.search(name_pattern, inscription, re.IGNORECASE)
    
        if name_match:
         company_name = name_match.group(1).strip()
        else:
         company_name = 'Nombre no encontrado' 

    # Expresión regular para extraer la fecha
        date_pattern = r'\(\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})\)'
        date_match = re.search(date_pattern, inscription)

        if date_match:
         day, month, year = date_match.groups()
    # Asegurar que el día y el mes tengan dos dígitos
         day = day.zfill(2)
         month = month.zfill(2)

    # Ajustar el año para que tenga cuatro dígitos
         year = "20" + year if len(year) == 2 else year

    # Formatear la fecha al formato DD/MM/YYYY
         inscription_date = f"{day}/{month}/{year}"
        else:
          inscription_date = 'Fecha no encontrada' 
            
    # Relaciona cada acto con las palabras en negrita de inscription        
        inscription_name =  "italic_text"
        

       
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
            "constitutionCommercialRegistry": None,
            "constitutionDate":  None,
            "constitutionRegistryData": None,
            "constitutionInscription": None,
            "operationsStartDate": None,
            "companyDuration": None,
            "constitutionAddress":None,
            "constitutionSocialObject": None,
            "constitutionSocialCapital": None,
            "constitutionFile": None,            
            "companyState": None,
            "administration": None,
            "administratorsList": None,
            "administrationAppointmentDate": None,
            "administrationAppointmentInscription": None,
            "administrationAppointmentFile": None,
            "companyInscription": []
        }
        # Crear y agregar la inscripción a la empresa correspondiente
        company_inscription  = {
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inscriptionCommercialRegistry": inscription_commercial_registry,
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
            
        company["companyInscription"].append(company_inscription)
        companies.append(company)

    return companies


@app.route('/')  # Defino la ruta
def home():
    pdf_path = "files/pruebas chicas/prueba_B/2009/02/11/pdfs/BORME-B-2009-28-35.pdf"
    texto_del_pdf = extract_text_from_pdf(pdf_path)    
    company = file_type_b(pdf_path)
    italic_titles = extract_italic_titles(pdf_path)
    for title in italic_titles:
     print(title)  
    
    return jsonify(company)


if __name__ == '__main__':
    app.run(debug=True)

