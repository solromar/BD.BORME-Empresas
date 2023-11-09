import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

if __name__ == "__main__":
    pdf_path = "files/BORME-A-2010-210-13.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)
