from flask import Flask, jsonify
import pdfplumber
import re


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



def file_type_a(texto_del_pdf, bold_text):
    extracted_info = []
    
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
     formatted_date = f"{day.zfill(2)}/{month}/{year}"
    else:
     formatted_date = "Fecha no encontrada"

    # Buscar la provincia del Acto
    constitution_commercial_registry_pattern = r'^Actos inscritos\n([A-Z\/ÁÉÍÓÚÜ\s]+)\n'
    constitution_commercial_registry_match = re.search(constitution_commercial_registry_pattern, texto_del_pdf, re.MULTILINE)
    constitution_commercial_registry = constitution_commercial_registry_match.group(1) if constitution_commercial_registry_match else "No encontrado"

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
        name_pattern = r'^\d+ - (.*?)(?:,? (SOCIEDAD LIMITADA|SL|SOCIEDAD LIMITADA LABORAL|S\.L\.|S\.L\.L\.))?\.\n'
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
          
    # Si el acto es una constitucion
        if re.search(r'constituci(?:ó|o)n', inscription, re.IGNORECASE):
    # Extraer la fecha de inicio de operaciones
         operation_start_date_pattern = r'Comienzo de operaciones:\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})\.'
         operation_start_date_match = re.search(operation_start_date_pattern, inscription)
        if operation_start_date_match:
             day, month, year = operation_start_date_match.groups()
             # Asegurar que el día y el mes tengan dos dígitos
             day = day.zfill(2)
             month = month.zfill(2)
             # Ajustar el año para que tenga cuatro dígitos
             year = "20" + year if len(year) == 2 else year
             # Formatear la fecha al formato DD/MM/YYYY
             operation_start_date = f"{day}/{month}/{year}"
        else:
             operation_start_date = 'No disponible'    

    # Extraer el objeto social
        constitution_social_object_pattern = r'Objeto social:\s*(.+?)\. Domicilio:'
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
        
    # Encuentra las palabras en negrita dentro de esta inscripción
        start_index = texto_del_pdf.find(inscription)
        end_index = start_index + len(inscription)
        inscription_bold_text = bold_text[start_index:end_index]

        inscription_name = inscription_bold_text            

        extracted_info.append({
            'Acto Inscripcion': inscription,
            'Categoria': inscription_category,
            'Datos Registrales': inscription_registry_data,
            'Denominación Social': company_social_denomination,
            'Fecha del Borme': formatted_date,
            'Fecha del Acto': inscription_date,
            "Nombre de la Sociedad": company_name,
            'Numero de Acto inscrito': inscription_number,
            'Nombre Acto Inscrito': inscription_name,
            'Registro Comercial': constitution_commercial_registry,
            'Sección': inscription_section, 
            'Comienzo de Operaciones': operation_start_date,
            'Objeto Social':constitution_social_object,
            'Domicilio':constitution_address,
            'Capital': constitution_social_capital                     
            
        })

    return extracted_info


@app.route('/')  # Defino la ruta
def home():
    pdf_path = "files/BORME-A-2010-210-13.pdf"
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    bold_text = extract_bold_text(pdf_path)
    extracted_info = file_type_a(texto_del_pdf, bold_text)
    
    return jsonify(extracted_info)


if __name__ == '__main__':
    app.run()

