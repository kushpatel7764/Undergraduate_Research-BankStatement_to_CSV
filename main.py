import Extract_Text_pdfplumer
import Formate_Text_as_Table
import Excel_Converter

def main():
    pdf_path = "./bankstatement.pdf"  # Replace with your PDF file path
    Extract_Text_pdfplumer.extract_text_from_pdf(pdf_path)
    with open("output.txt", "r") as f:
        text = f.read()
        pages_arry = text.split("--- Page ---\n")
        pages_arry.pop(0)
        formatted_text = Formate_Text_as_Table.convert_pdf_to_table(pages_arry=pages_arry)
        print(formatted_text)
        excelOutput = Excel_Converter.ExcelOutput(formatted_text)
        excelOutput.start()
        
    
    
main()
