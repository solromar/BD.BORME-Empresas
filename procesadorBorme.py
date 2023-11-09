import PyPDF2

def extract_text_from_pdf(pdf_path):
    text = ""
    pdf = PyPDF2.PdfReader(pdf_path)
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        text += page.extract_text()
    return text

if __name__ == "__main__":
    pdf_path = "files/BORME-A-2010-210-13.pdf"  # Reemplaza con la ruta de tu archivo PDF
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)
