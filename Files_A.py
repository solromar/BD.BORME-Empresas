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


# Función para extraer texto en negrita del PDF
def extract_bold_text(pdf_path):
    bold_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for char in page.chars:
                if 'Bold' in char['fontname']:
                    bold_text += char['text']
    return bold_text

def find_bold_for_inscription(inscription, bold_text):
    # Extraer el número de inscripción
    inscription_number_match = re.search(r'^(\d+)', inscription)
    if not inscription_number_match:
        return "No disponible"

    inscription_number = inscription_number_match.group(1)

    # Buscar el patrón en el texto en negrita
    pattern = fr'{inscription_number} - [^\.]+?\.(.*?)(?=\d+ - [^\.]+?\.|$)'
    bold_match = re.search(pattern, bold_text)

    if bold_match:
        # Limpiar el texto capturado para eliminar cualquier texto no deseado al final
        bold_text_captured = bold_match.group(1).strip()
        # Eliminar cualquier texto no relacionado que pueda haberse capturado al final
        clean_text = re.sub(r'BOLETÍN OFICIAL DEL REGISTRO MERCANTIL.*', '', bold_text_captured)
        return clean_text
    else:
        return "No disponible"
    
 
# -------------------------------------------------- PROCESAMIENTO BORME A --------------------------------------------------------------

def file_type_a(pdf_path):
    companies = []
    
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    bold_text = extract_bold_text(pdf_path)
   
    
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

    # Buscar la provincia del Acto
    inscription_commercial_registry_pattern = r'^Actos inscritos\n([A-Z\/ÁÉÍÓÚÜ\s]+)\n'
    inscription_commercial_registry_match = re.search(inscription_commercial_registry_pattern, texto_del_pdf, re.MULTILINE)
    inscription_commercial_registry = inscription_commercial_registry_match.group(1) if inscription_commercial_registry_match else "No encontrado"

    # Buscar Sección del Acto
    inscription_section_pattern = r'Pág\.\s+\d+\s+SECCIÓN\s+(PRIMERA|SEGUNDA)'
    inscription_section_match = re.search(inscription_section_pattern, texto_del_pdf)
    inscription_section = inscription_section_match.group(1) if inscription_section_match else "No encontrado"

    # Buscar Categoria del Acto
    inscription_category_pattern = r'Empresarios\s+(.*)\s+'
    inscription_category_match = re.search(inscription_category_pattern, texto_del_pdf)
    inscription_category = inscription_category_match.group(1) if inscription_category_match else "No encontrado"

    # Buscar todos los actos inscritos y extraer informacion
    inscription_pattern = r'^(\d+ - .+?\(\s*\d{1,2}\.\d{1,2}\.\d{2,4}\s*\)\.)'
    inscriptions = re.findall(inscription_pattern, texto_del_pdf, re.MULTILINE | re.DOTALL)

    for inscription in inscriptions:
    # Expresión regular para buscar el número de inscripción
        inscription_number_pattern = r'^(\d+)'
        number_match = re.search(inscription_number_pattern, inscription)
        if number_match:
         inscription_number = number_match.group(1)
        else:
         inscription_number = 'Número no encontrado'

    # Expresión regular para buscar la denominación social completa
        full_name_pattern = r'^\d+ - (.*?)(?:\.\n|$)'
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
            
    # Expresión regular para extraer los datos registrales
        registry_data_pattern = r'Datos\s*registrales\.(.*?)\s*\('
        registry_data_match = re.search(registry_data_pattern, inscription, re.DOTALL)
    
        if registry_data_match:
         inscription_registry_data = " ".join(registry_data_match.group(1).split())
        else:
         inscription_registry_data = 'Datos registrales no encontrados'

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
        inscription_name = find_bold_for_inscription(inscription, bold_text)
        
#--------------------------OBTENER LOS DATOS DE CONSTITUCION DE LA COMPANY -------------------------------------------------------------------------        
    # Verificar si la inscripción contiene 'Constitución'
        is_constitution = 'Constitución' in inscription

        # Extracción de datos específicos de constitución si es necesario
        constitution_date, constitution_registry_data, constitution_inscription, operation_start_date, constitution_address, constitution_social_object, constitution_social_capital = (None,)*7
        if is_constitution:
    # Extraer la fecha de inicio de operaciones
         operation_start_date_pattern = r'Comienzo de operaciones:\s*(\d{1,2}\.\d{1,2}\.\d{2,4})\.'
         operation_start_date_match = re.search(operation_start_date_pattern, inscription)
         operation_start_date = operation_start_date_match.group(1) if operation_start_date_match else "No disponible"
             

    # Extraer el objeto social
        constitution_social_object_pattern = r'Objeto social:\s*(.+?)\.\s*Domicilio:'
        constitution_social_object_match = re.search(constitution_social_object_pattern, inscription, re.DOTALL)
        constitution_social_object = constitution_social_object_match.group(1).strip() if constitution_social_object_match else "No disponible"

    # Extraer el domicilio
        constitution_address_pattern = r'Domicilio:\s*(.+?)\.\s*Capital:'
        constitution_address_match = re.search(constitution_address_pattern, inscription, re.DOTALL)
        constitution_address = constitution_address_match.group(1).replace('\n', ' ').strip() if constitution_address_match else "No disponible"

    # Extraer el capital
        constitution_social_capital_pattern = r'Capital:\s*([\d.,]+)\s*Euros\.'
        constitution_social_capital_match = re.search(constitution_social_capital_pattern, inscription, re.DOTALL)
        constitution_social_capital = constitution_social_capital_match.group(1).strip() if constitution_social_capital_match else "No disponible"
        
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
         constitution_date = f"{day}/{month}/{year}"
        else:
          constitution_date = 'Fecha no encontrada' 
          
    # Expresión regular para extraer los datos registrales
        registry_data_pattern = r'Datos\s*registrales\.(.*?)\s*\('
        registry_data_match = re.search(registry_data_pattern, inscription, re.DOTALL)
    
        if registry_data_match:
         constitution_registry_data = " ".join(registry_data_match.group(1).split())
        else:
         constitution_registry_data = 'Datos registrales no encontrados'  
         
         # Asignar los campos relacionados con la constitución
        constitution_inscription = inscription
        constitution_file = os.path.basename(pdf_path)
        
        
        # Buscar la provincia del Acto
        constitution_commercial_registry_pattern = r'^Actos inscritos\n([A-Z\/ÁÉÍÓÚÜ\s]+)\n'
        constitution_commercial_registry_match = re.search(constitution_commercial_registry_pattern, texto_del_pdf, re.MULTILINE)
        constitution_commercial_registry = constitution_commercial_registry_match.group(1) if constitution_commercial_registry_match else "No encontrado"
       
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
            "constitutionCommercialRegistry": constitution_commercial_registry if is_constitution else "No disponible",
            "constitutionDate": constitution_date if is_constitution else "No disponible",
            "constitutionRegistryData": constitution_registry_data if is_constitution else "No disponible",
            "constitutionInscription": constitution_inscription if is_constitution else "No disponible",
            "operationsStartDate": operation_start_date if is_constitution else "No disponible",
            "companyDuration": None,
            "constitutionAddress": constitution_address if is_constitution else "No disponible",
            "constitutionSocialObject": constitution_social_object if is_constitution else "No disponible",
            "constitutionSocialCapital": constitution_social_capital if is_constitution else "No disponible",
            "constitutionFile": constitution_file if is_constitution else "No disponible",            
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
                "inscriptionRegistryData": inscription_registry_data,
                "inscription": inscription,
                "bormeDate": borme_date,
                "inscriptionFile": os.path.basename(pdf_path)
                }
            
        company["companyInscription"].append(company_inscription)
        companies.append(company)

    return companies


@app.route('/')  # Defino la ruta
def home():
    pdf_path = "/home/soledad/BD.BORME-Empresas/files/prueba/2010/11/02/pdfs/BORME-A-2010-210-13.pdf"
    #texto_del_pdf = extract_text_from_pdf(pdf_path)
    #boldWords = extract_bold_text(pdf_path)
    company = file_type_a(pdf_path)
    
    return jsonify(company)


if __name__ == '__main__':
    app.run(debug=True)

