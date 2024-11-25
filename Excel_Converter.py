
import xlwt
class ExcelOutput:
    def __init__(self, text):
        self.text = text
    def start(self):

        workbook = xlwt.Workbook()
        #Sheet name is header of table
        sheet = workbook.add_sheet(self.text.split("\n")[0])

        ExcelOutput.Excel_Write_Data(self, sheet)
        fileName = "ExcelOutput.xls"
        # Save the workbook to a file
        workbook.save(fileName)
        print(f"\nExcel file \"{fileName}\" created successfully.\n")
        
    def Excel_Write_Data(self, sheet):
        """
        Writes data to the Excel sheet. The first loop picks a row and the second loop sets a columbs at a row from the first loop. 

        Parameters:
        - sheet: An Excel sheet object.
        """        
        text_lines = self.text.split("\n")
        for row, line in enumerate(text_lines):
            col_val = line.split(" | ")
            for col, value in enumerate(col_val):
                sheet.write(row, col, value)
