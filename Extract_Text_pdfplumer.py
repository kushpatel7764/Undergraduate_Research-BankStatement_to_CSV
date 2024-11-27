import pdfplumber
import os
from PIL import Image

def extract_text_from_pdf(pdf_path, output_file="output.txt"):
    extracted_text = ""

    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            extracted_text += f"--- Page ---\n{text}\n\n"
    
    # save the extracted text to a file
    if output_file:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(extracted_text)
        print(f"Extracted text saved to {output_file}")

