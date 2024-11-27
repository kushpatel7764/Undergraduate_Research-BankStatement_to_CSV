import re;

def index_table_names(table_names, page):
    """_summary_: will return a tuple with the names of table on this page in the x and their string index on y.
        Args:table_names (list): names of all the tables in this array. 
        page (string): the full text of page on this pdf.
    """
    return_arry = []
    for name in table_names:
        if page.find(name) != -1:
            return_arry.append((name, page.find(name)))
    return return_arry

def sortTableNameTuple(tuple):
    """_summary_: will sorted the given tuple

    Args:
        tuple (array): a tuple list where a given tuples has name of table on this page and a number for where the name is on the page

    Returns:
        array of tuples: stored list of tuples on the y axis 
    """
    sorted_data = sorted(tuple, key=lambda x: x[1])
    return sorted_data
 

def sort_table_names_list(table_names, page):
    """_summary_: Given a list of all possible names of tables in a list, this function will 
    return a list all table names on this page in a sorted order from top to bottom.
    

    Args:
        table_names (list): names of all the tables in this array. 
        page (string): the full text of page on this pdf.
    """
    indexed_table_names = index_table_names(table_names, page)
    if indexed_table_names != []:
        sorted_indexed_table_names = sortTableNameTuple(indexed_table_names)
        return sorted_indexed_table_names    
    else:
        return None
    
def get_section_between_names(page, name1, name2):
    """Given a whole page this function return a section of this page the is between the two names

    Args:
        page (String):  it has all the content of current page
        name1 (String): table_name on top
        name2 (String): table_name on bottm
    """
    # Split the text into parts based on the top name
    page_after_name1_array = page.split(name1 + "\n") 
    # do no need anything above name1
    page_after_name1_array.pop(0)
    if name2 != None:
        whole_bottom_section = page_after_name1_array[0]
        section = whole_bottom_section.split(name2 + "\n")
        section.pop(1)
    else: 
        section = page_after_name1_array
    return section[0]
    
def make_formatted_array(section, tableName):
    """(MUST BE GIVEN AN SECTION OF PAGE WITH ONLY ONE TABLE) return a array with rows (another array) inside it. Each index of the row array is a cell. 

    Args:
        section (String): section of page with information for only one table
        tableName (String): name of current table that is being formatted
    """
    formatted_text = []
    formatted_text.append([tableName])
    formatted_text.append(["Date", "Description", "Amount"])
    amount_regex = r"\-?\$?[0-9]*\,?[0-9]*\.{1}[0-9]{2}"
    date_regex = r"^\d{2}/\d{2}/\d{2}"
    for line in section.splitlines():  # Process each line separately
            line.strip()
            test1 = True if re.search(date_regex, line) else False
            test2 = True if re.search(amount_regex, line) else False
            if re.search(date_regex, line) and re.search(amount_regex, line): #date and amount are on this line then be need this line
                start_date,end_date = re.search(date_regex, line).span() 
                start_amount, end_amount = re.search(amount_regex, line).span() 
                formatted_text.append([line[start_date:end_date].strip(), line[end_date: start_amount].strip(), line[start_amount:end_amount]])  # Add the matched line to the output
            #Add the Total amount line 
            if line.lower().find(tableName.lower()) != -1:
                start_amount, end_amount = re.search(amount_regex, line).span() 
                formatted_text.append([line[0:start_amount], line[start_amount:end_amount]])
            
    return formatted_text

def check_next_page(next_page_text, table_name):
    """check if next_page has the "- continued". if it does we need to finished current page's table 

    Args:
        next_page_text (String): full string of the next page
        table_name (String): Current table name
    """
    string_to_find = f"{table_name} - continued"
    for line in next_page_text.splitlines():
        line.strip()
        if line.find(string_to_find) != -1:
            return False
        else:
            return True
    
    
def get_continued_table(section_lines, table_name):
    to_return = []
    for line in section_lines:
        to_return.append(line)
        if line.find(table_name) != -1:
            break
    return to_return
            

def formate_reg_page_text(curr_page_text, next_page_text, tableNames):
    """_summary_: First sorted the tableNames on this page in a top to down way. Then loop through all the sorted tablenames
    and get the area of just one table on the page. Then make an formatted array that has all the neccesary content from this one section of the page. Then do this for all sections of the page. 
    TODO:Working on how to hand the "- continued". May be at the end of the final table name. peek the next page and put everything from "- continued" on the current page.
    and if on the current page the "- continued" tage comes then do not handle that page 
    Args:
        reg_page_text (string): it has all the content of current page
        tableNames (array): contain names of all the table in the pdf

    Returns:
        array[array]: array with array of formatted tables inside. 
    """
    formatted_text = []     
    sorted_table_names = sort_table_names_list(table_names=tableNames,page=curr_page_text)
    if sorted_table_names == None:
        return None
    #Preprocess tableNames so the "- continued" table names are not in tableNames list as they will already so completed. 
    name,index = sorted_table_names[0]
    curr_page_lines = curr_page_text.splitlines()
    for line in curr_page_lines:
        if line.find(name + " - continued") != -1:
            sorted_table_names.pop(0)
            break
    if sorted_table_names == []:
        return None
    for i,table_name_index in enumerate(sorted_table_names):
        table_name, index = table_name_index
        not_last_index = True if i != len(sorted_table_names)-1 else False
        if not_last_index:
            section = get_section_between_names(curr_page_text,name1=table_name,name2=sorted_table_names[i+1][0])
        else:
            section = get_section_between_names(curr_page_text,name1=table_name, name2=None)
        formatted_text.append(make_formatted_array(section, table_name))
        #Peek next page for "{table_name} - continued"
        if next_page_text != None and not_last_index == False:
            if check_next_page(next_page_text, table_name):
                section = get_section_between_names(next_page_text, name1=table_name + " - continued", name2=None)
                #TODO: improve logic here
                #Find last row of current table
                section_lines = section.splitlines()
                continued_table_lines = get_continued_table(section_lines, table_name)
                continued_table_lines_string = "\n".join(continued_table_lines)
                continued_table_formated = make_formatted_array(continued_table_lines_string, table_name)
                for row in continued_table_formated:
                    formatted_text[-1].append(row)
                
    return formatted_text


def formate_first_page_text(first_page_text, tableName):
    formatted_text = []
    formatted_text.append(["Account summary"])
    # Split the text into parts based on the tableName
    page_after_tableName_array = first_page_text.split(tableName + "\n")  
    
    if len(page_after_tableName_array) <= 1:
        # If tableName is not found or there's no content after it
        return "Table name not found or no content available."

    page_after_tableName_array.pop(0) #remove the upper bound in array
    #Get page text in line form
    regex = r"\-?\$?[0-9]*\,?[0-9]*\.{1}[0-9]{2}"
    #regex = r"\.{1}[0-9]+"
    for section in page_after_tableName_array:
        for line in section.splitlines():  # Process each line separately
            line.strip()
            
            if re.search(regex, line):
                start,end = re.search(regex, line).span()
                formatted_text.append([line[0:start].strip(), line[start:end]])  # Add the matched line to the output
    return formatted_text
    #page_lower_half_lines = page_after_tableName_arry[0].strip()
    #Sperate digits from words 
    #words, nums = split_words_digits(page_lower_half_lines)
    #words.pop(0) if nums[0] == "" else nums
    #Loop through nums array and make a table formatted string that can be easily converted to csv, also get a bank statement structure for rest of the tables.
    #for i, num in enumerate(nums):
    #    formated_text +=  words[i] + " | " + num + "\n"
    #structure = getStructureOfPage(formated_text)
        
    #return formated_text, structure

def getStructureOfPDF(firstPageTableArry):
    #Everything in first page table except first and last line had a sub_table in the bank statement
    #so everthing in the first page table except first and last line are needed to be set as structure of bank statement
    #it does not need to be set as bank statment structure if it is 0 since then it will not have a table.
    structure = []
    for i,line in enumerate(firstPageTableArry):
        try:
            value = line[1]
        except IndexError:
            continue
        
        value = value.replace("$", "") if "$" in value else value
        value = value.replace(",", "") if "," in value else value
        if i > 0 and i < len(firstPageTableArry)-1 and float(value) !=0 : #If not on first line of table or last line then do something, we dont want to add first or last line in structure because they do not have there own table. 
            structure.append(line[0]) 
            
    return structure


