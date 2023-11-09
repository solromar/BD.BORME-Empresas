import pdfplumber
import re


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


if __name__ == "__main__":
    pdf_path = "files/BORME-A-2010-210-13.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    
# Patrón para buscar líneas que comienzan con números de inscripción
    inscription_pattern = r'^(\d+ - .+?)\n(?=\d+ - |\Z)'
    inscriptions = re.findall(inscription_pattern, extracted_text, re.MULTILINE | re.DOTALL)

    # Imprimir las líneas encontradas
    for inscription in inscriptions:
        # Expresión regular para buscar el número de inscripción
        inscriptionNumber_pattern = r'^(\d+) - ([A-Z\s,]+)\.'
        matches = re.search(inscriptionNumber_pattern, inscription)

        # Verificar si se encontró el número de inscripción
        if matches:
            inscription_number = matches.group(1)
            social_denomination = matches.group(2)
            
            print(f"Numero de Acto Inscrito: {inscription_number}")
            print(f"Denominacion Social: {social_denomination}")
            
            lines = inscription.split('\n')
        second_line = lines[1] if len(lines) > 1 else ''
        inscription_name = ''

        if second_line:
            pattern = r'^[^.:]+'
            name_matches = re.match(pattern, second_line)
            inscription_name = name_matches.group() if name_matches else 'ERROR'

        print(f"Inscription Name: {inscription_name}")


       
