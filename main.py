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
    
    # Buscar fecha del Borme 
    borme_date_pattern = r'(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s+(\d+)\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})'
    borme_date_match = re.search(borme_date_pattern, texto_del_pdf)
    borme_date = borme_date_match.group(0) if borme_date_match else "No encontrado"

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
    inscription_pattern = r'^(\d+ - .+?)\n(?=\d+ - |\Z)'
    inscriptions = re.findall(inscription_pattern, texto_del_pdf, re.MULTILINE | re.DOTALL)

    for inscription in inscriptions:
        # Buscar el nombre de la sociedad y el número de inscripción en cada acto Inscrito
        inscription_info_pattern = r'^(\d+) - ([A-Z\s,]+)\.'
        match = re.search(inscription_info_pattern, inscription)
        if match:
            inscription_number = match.group(1)
            company_name = match.group(2)
        else:
            company_name = 'Nombre no encontrado'
            inscription_number = 'Número no encontrado'

        # Extraer el nombre de la inscripción de la segunda línea, si está disponible
        lines = inscription.split("\n")
        inscription_name = ''
        if len(lines) > 1:
            second_line_pattern = r'^[^\.|:]+'
            second_line_match = re.search(second_line_pattern, lines[1])
            inscription_name = second_line_match.group(
                0) if second_line_match else 'ERROR'

        extracted_info.append({
            'Fecha del Borme': borme_date,
            'Registro Comercial': commercial_registry,
            'Numero de Acto inscrito': inscription_number,
            'Nombre Sociedad': company_name,
            'Nombre Acto Inscrito': inscription_name,
            "Sección": inscription_section,
            "Categoria": inscription_category
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
