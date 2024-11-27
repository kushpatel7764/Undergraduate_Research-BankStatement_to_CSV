import Utility2

def convert_pdf_to_table(pages_arry):
    """_summary_

    Args:
        pages_arry (_type_): _description_
        
    return: [pages[tables[table[rows[]]]]]
    """
    formatted_text = []
    table_Names = []
    for i,page in enumerate(pages_arry):
        if i == 0:
            formated_first_page = Utility2.formate_first_page_text(page, "Account summary")
            table_Names = Utility2.getStructureOfPDF(formated_first_page)
            formatted_text.append(formated_first_page)
            if table_Names == []:
                return None
        else:
            not_last_index = True if i != len(pages_arry)-1 else False
            if not_last_index:
                formated_reg_page = Utility2.formate_reg_page_text(page, pages_arry[i+1], table_Names)
            else:
                formated_reg_page = Utility2.formate_reg_page_text(page, None, tableNames=table_Names)
            formatted_text.append(formated_reg_page)
    return formatted_text
        

