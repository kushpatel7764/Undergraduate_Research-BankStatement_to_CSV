
import xlwt
class ExcelOutput:
    def __init__(self, table_arry):
        self.table_arry = table_arry
    def start(self):

        workbook = xlwt.Workbook()
        #Sheet name is header of table
        for i,page in enumerate(self.table_arry):
            if page == None:
                continue
            if i == 0:
                sheet = workbook.add_sheet(page[0][0])
                ExcelOutput.Excel_Write_Data(self, sheet, page)
            else:
                for tables in page:
                    sheet = workbook.add_sheet(tables[0][0])
                    ExcelOutput.Excel_Write_Data(self, sheet, tables)
                        
                        
        fileName = "ExcelOutput.xls"
        # Save the workbook to a file
        workbook.save(fileName)
        print(f"\nExcel file \"{fileName}\" created successfully.\n")
        
    def Excel_Write_Data(self, sheet, table):
        """
        Writes data to the Excel sheet. The first loop picks a row and the second loop sets a columbs at a row from the first loop. 

        Parameters:
        - sheet: An Excel sheet object.
        """        
        for row, line in enumerate(table):
            for col, value in enumerate(line):
                sheet.write(row, col, value)
