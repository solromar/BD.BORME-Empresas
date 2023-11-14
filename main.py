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


def file_type_a(texto_del_pdf):
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
    commercial_registry_pattern = r'^Actos inscritos\n([A-Z\/ÁÉÍÓÚÜ\s]+)\n'
    commercial_registry_match = re.search(commercial_registry_pattern, texto_del_pdf, re.MULTILINE)
    commercial_registry = commercial_registry_match.group(1) if commercial_registry_match else "No encontrado"

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

    # Extraer el nombre de la inscripción de la segunda línea, si está disponible
        lines = inscription.split("\n")
        inscription_name = ''
        if len(lines) > 1:
            second_line_pattern = r'^[^\.|:]+'
            second_line_match = re.search(second_line_pattern, lines[1])
            inscription_name = second_line_match.group(
                0) if second_line_match else 'ERROR'
            
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
        if "CONSTITUCIÓN" in inscription.upper():
    # Extraer la fecha de inicio de operaciones
         inicio_operaciones_pattern = r'Comienzo de operaciones:\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})\.'
         inicio_operaciones_match = re.search(inicio_operaciones_pattern, inscription)
        if inicio_operaciones_match:
             day, month, year = inicio_operaciones_match.groups()
             # Asegurar que el día y el mes tengan dos dígitos
             day = day.zfill(2)
             month = month.zfill(2)
             # Ajustar el año para que tenga cuatro dígitos
             year = "20" + year if len(year) == 2 else year
             # Formatear la fecha al formato DD/MM/YYYY
             inicio_operaciones = f"{day}/{month}/{year}"
        else:
             inicio_operaciones = 'No disponible'    

    # Extraer el objeto social
        objeto_social_pattern = r'Objeto social:\s*(.+?)\. Domicilio:'
        objeto_social_match = re.search(objeto_social_pattern, inscription, re.DOTALL)
        objeto_social = objeto_social_match.group(1).strip() if objeto_social_match else "No disponible"

    # Extraer el domicilio
        domicilio_pattern = r'Domicilio:\s*(.+?)\.\s*Capital:'
        domicilio_match = re.search(domicilio_pattern, inscription, re.DOTALL)
        domicilio = domicilio_match.group(1).strip() if domicilio_match else "No disponible"

    # Extraer el capital
        capital_pattern = r'Capital:\s*([\d.,]+)\s*Euros\.'
        capital_match = re.search(capital_pattern, inscription, re.DOTALL)
        capital = capital_match.group(1).strip() if capital_match else "No disponible"         

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
            'Registro Comercial': commercial_registry,
            'Sección': inscription_section, 
            'Inicio Operacion': inicio_operaciones,
            'Objeto Social':objeto_social,
            'Domicilio':domicilio,
            'Capital': capital                     
            
        })

    return extracted_info


@app.route('/')  # Defino la ruta
def home():
    pdf_path = "files/BORME-A-2010-210-13.pdf"
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    extracted_info = file_type_a(texto_del_pdf)

    return jsonify(extracted_info)


if __name__ == '__main__':
    app.run()
