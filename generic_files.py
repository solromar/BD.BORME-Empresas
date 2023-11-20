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

    


def generic_files(texto_del_pdf):
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

    extracted_info.append({
            'Categoria': inscription_category,
            'Fecha del Borme': formatted_date,
            'Registro Comercial': constitution_commercial_registry,
            'Sección': inscription_section, 
        })
    return extracted_info




@app.route('/generic')  # Defino la ruta
def home():
    pdf_path = "files/BORME-A-2010-210-13.pdf"
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    extracted_info = generic_files(texto_del_pdf)
    
    return jsonify(extracted_info)


if __name__ == '__generic_files__':
    app.run()