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

def extract_inscriptions_with_titles(texto_del_pdf, pdf_path):    
    italic_titles = extract_italic_titles(pdf_path)
    inscriptions = []
    current_inscription = ''
    exclude_patterns = ["https://www.boe.es", "EMROB","BOLETÍN OFICIAL DEL REGISTRO MERCANTIL", "Núm." , "Pág. ", "SECCIÓN", "Empresarios", "Otros actos publicados en el Registro Mercantil", "ILLES BALEARS"]
    
    for line in texto_del_pdf.split('\n'):
        if any(exclude_pattern in line for exclude_pattern in exclude_patterns):
            # Si encontramos alguna de las líneas de exclusión, finalizamos la inscripción actual y continuamos con la siguiente
            if current_inscription:
                inscriptions.append(current_inscription.strip())
                current_inscription = ''
            continue

        if line in italic_titles and current_inscription:
            # Si encontramos un nuevo título en cursiva y hay una inscripción en curso, la guardamos
            inscriptions.append(current_inscription.strip())
            current_inscription = ''

        current_inscription += line + '\n'

    if current_inscription:
        inscriptions.append(current_inscription.strip())

    return inscriptions


def process_inscription(inscription):
    lines = inscription.split('\n')    
    inscription_name = lines[0]  # El nombre de la inscripción es la primera línea del bloque
    extracted_data = []
        
    for line in lines[1:]:
        if line.strip() and '-' in line:
            parts = line.split('-', 1)
            if len(parts) == 2:
                inscription_number = parts[0].strip()
                company_data = parts[1].strip()
                company_social_denomination = company_data.split('(')[0].strip()
                # Extraer el nombre de la empresa sin el tipo de compañía
                # Modificamos la expresión regular para ser más flexible
                company_name_match = re.search(r'(.*?)(?:\s+(SOCIEDAD LIMITADA|SOCIEDAD LIMITADA EN LIQUIDACION|SL|SLL|SL EN LIQUIDACION|SLNE|SLNE EN LIQUIDACION|SA|SA EN LIQUIDACION|SOCIEDAD LIMITADA LABORAL|SOCIEDAD ANONIMA|S\.L\.|S\.L\.L\.|S\.A\.|S\.A\.A\.|S\.L\.L\.))?(?:\s*\(.+\))?\s*\.?$', company_social_denomination, re.IGNORECASE)
                if company_name_match:
                    company_name = company_name_match.group(1).strip()
                else:
                    company_name = 'Nombre no encontrado'
            
            # Extraer la fecha
                date_match = re.search(r'\(((\d{1,2}/\d{1,2}/\d{2,4})|(\d{4}))\)', company_data)
                inscription_date = date_match.group(1) if date_match else "Fecha no encontrada"

                extracted_data.append((inscription_name, inscription_number, company_social_denomination, company_name, inscription_date, line))
   
    return extracted_data
    
   
# -------------------------------------------------- PROCESAMIENTO BORME B --------------------------------------------------------------

def file_type_b(pdf_path):
    companies = []
    
    texto_del_pdf = extract_text_from_pdf(pdf_path)
    inscriptions = extract_inscriptions_with_titles(texto_del_pdf, pdf_path)
    
    
    
    
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
    inscription_commercial_registry_pattern = r'Empresarios\s+Otros actos publicados en el Registro Mercantil\s+([A-ZÁÉÍÓÚÜ\s]+)\n'
    inscription_commercial_registry_match = re.search(inscription_commercial_registry_pattern, texto_del_pdf)
    inscription_commercial_registry = inscription_commercial_registry_match.group(1) if inscription_commercial_registry_match else "No encontrado"
    
    # Buscar Sección del Acto
    inscription_section_pattern = r'Pág\.\s+\d+\s+SECCIÓN\s+(PRIMERA|SEGUNDA)'
    inscription_section_match = re.search(inscription_section_pattern, texto_del_pdf)
    inscription_section = inscription_section_match.group(1) if inscription_section_match else "No encontrado"
  
    # Buscar Categoria del Acto
    inscription_category_pattern = r'Empresarios\s+(.*)\s+'
    inscription_category_match = re.search(inscription_category_pattern, texto_del_pdf)
    inscription_category = inscription_category_match.group(1) if inscription_category_match else "No encontrado"
   
    
    for inscription in inscriptions:
        processed_data = process_inscription(inscription)
        for inscription_name, inscription_number, company_social_denomination, company_name, inscription_date, lines in processed_data:
            company_inscription = {
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inscriptionCommercialRegistry": inscription_commercial_registry,
                "inscriptionNumber": inscription_number,
                "inscriptionSection": inscription_section,
                "inscriptionCategory": inscription_category,
                "inscriptionName": inscription_name,
                "inscriptionDate": inscription_date,
                "inscriptionRegistryData": None,
                "inscription": lines,
                "bormeDate": borme_date,
                "inscriptionFile": os.path.basename(pdf_path)
            }

            company = {
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "companySocialDenomination": company_social_denomination,
                "companyName": company_name,
                "companyInscription": [company_inscription]
            }

            companies.append(company)

    return companies


@app.route('/')  # Defino la ruta
def home():
    pdf_path = "files/pruebas chicas/prueba_B/2009/02/11/pdfs/BORME-B-2009-28-48.pdf"
    company = file_type_b(pdf_path)
    #texto_del_pdf = extract_text_from_pdf(pdf_path)
    #italic_titles = extract_italic_titles(pdf_path)
    
    return jsonify(company)


if __name__ == '__main__':
    app.run(debug=True)