import re

def split_words_digits(array_of_text):
    words = []
    numbers = [] 
    for text in array_of_text:
        if isNumber(text): 
            numbers.append(text)
        else:
            words.append(text)
    return words, numbers


def isNumber(text):
    try:
        float(text.replace("$", "").replace(",", ""))
        return True
    except ValueError:
        return False
""" letter_attribute = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "/"]
text = [char.lower() for char in text]
for letter in letter_attribute:
    if  letter in text:
        return False
return True """
def isDate(line):
    if re.match("^\d{2}/\d{2}/\d{2}$", line):
        return True
    else:
        return False

def getDate_cat(lines, structure_name, structure_list):
    return_arry = []
    structure_list.remove(structure_name)
    for line in lines:
        if line.strip().replace("\n", "") in structure_list:
            break
        if re.match("^\d{2}/\d{2}/\d{2}$", line):
            return_arry.append(line)
    return return_arry

def getAmount_cat(lines, structure_name, structure_list):
    return_arry = []
    #structure_list.remove(structure_name)
    for line in lines:
        if line.strip().replace("\n", "") in structure_list:
            break
        if isNumber(line) and line.find("$") == -1:
            return_arry.append(line)
    return return_arry
            
def getDescription_cat(lines, structure_name, structure_list):
    return_arry = []
    #structure_list.remove(structure_name)
    for line in lines:
        #Do not get anything after another structure name comes up 
        if line.strip().replace("\n", "") in structure_list:
            break
        if (re.match("^[^a-z]+$", line) or re.search("(?i)payment+", line)) and (not isNumber(line)) and (not isDate(line)):
            return_arry.append(line)
    return return_arry

def getAmountOfStructInPage(page, struct_List):
    return_arry = []
    for struct_Name in struct_List:
        if page.find(struct_Name) != -1:
            return_arry.append((struct_Name, page.find(struct_Name)))
    return return_arry
    
def sortStructTuple(tuple):
    sorted_data = sorted(tuple, key=lambda x: x[1])
    return sorted_data
 
def initialize_reg_page(page_text, structure_tuple, structure_list):
    """_summary_

    Args:
        page_text (_type_): _description_
        structure_tuple (_type_): [(name, location in page),...]

    Returns:
        None: if no structure found or if arrays do not match up
    """
    tables = []
    sorted_struct_tuple = sortStructTuple(structure_tuple)
    if len(structure_tuple) < 1:
        return None
    else:
        
        for structure_name, location in sorted_struct_tuple:
            page_formated_text = ""
            page_text_lower_bound_arry = page_text.split(structure_name)
            page_text_lower_bound_arry.pop(0) #remove the upper bound in array
            #Get page text in line form
            page_lower_bound_lines = page_text_lower_bound_arry[0].split("\n")
            
            dates = getDate_cat(page_lower_bound_lines, structure_name, structure_list)
            description = getDescription_cat(page_lower_bound_lines, structure_name, structure_list)
            amount = getAmount_cat(page_lower_bound_lines, structure_name, structure_list)
            
            #check that all the arrays are of same size
            if (len(dates) == len(description)) and (len(description) == len(amount)):
                page_formated_text += f" | {structure_name} | \n"
                page_formated_text += f"Date | Description | Amount \n"
                for i, date in enumerate(dates):
                    page_formated_text += f"{date} | {description[i]} | {amount[i]} \n"
                tables.append(page_formated_text)
            else:
                print("Different size arrays")
                return None
        return tables
                

def initialize_first_page_text_and_structure(first_page_text, structure_First_Name):
    page_formated_text = ""
    page_text_lower_bound_arry = first_page_text.split(structure_First_Name + "\n")
    page_text_lower_bound_arry.pop(0) #remove the upper bound in array
    #Get page text in line form
    
    page_lower_bound_lines = page_text_lower_bound_arry[0].strip().split("\n")
    #Sperate digits from words 
    words, nums = split_words_digits(page_lower_bound_lines)
    #words.pop(0) if nums[0] == "" else nums
    #Loop through nums array and make a table formatted string that can be easily converted to csv, also get a bank statement structure for rest of the tables.
    for i, num in enumerate(nums):
        page_formated_text +=  words[i] + " | " + num + "\n"
    structure = getStructureOfPage(page_formated_text)
        
    return page_formated_text, structure
    

def getStructureOfPage(firstPageFormattedText):
    #Everything in first page table except first and last line had a sub_table in the bank statement
    #so everthing in the first page table except first and last line are needed to be set as structure of bank statement
    #it does not need to be set as bank statment structure if it is 0 since then it will not have a table.
    structure = []
    
    table_lines = firstPageFormattedText.strip().split("\n")
    table_lines.pop(0) #First line is not needed since it is just the table name
    
    for i,line in enumerate(table_lines):
        table_colums = line.split(" | ") # [[Row Name],[values]]
        name = table_colums[0]
        value = table_colums[1]
        value = value.replace("$", "") if "$" in value else value
        value = value.replace(",", "") if "," in value else value
        if i < len(table_lines) - 1 and float(value) != 0: #If not on first line of table or last line then do something, we dont want to add first or last line in structure because they do not have there own table. 
            curr_word = name
            structure.append(curr_word) 
            
    return structure
    
"""    
#TODO: Break this big function in smaller functions 
def fullText_to_tableText(full_pdf_text):
    structures = ["Account summary"]
    final_text = [] 
    for k,structure in enumerate(structures):
        text = ""
        text += structure + "\n"
        
        for i,page in enumerate(full_pdf_text):
            #if this page has the structure word in it then run code otherwise do not
            if re.search(rf"\b{re.escape(structure)}\b", page, re.IGNORECASE) is not None:
                #From all the text only get the stuff after "Account summary"
                table_text = page.split(structure) 
                table_text.pop(0)
                if len(table_text) != 0:
                    #Get lines from all the text
                    split_table_text = table_text[0].split("\n")
                    #Sperate digits from words 
                    words, nums = Utility.split_words_digits(split_table_text)
                    #From nums remove an empty string created by split_text_digits functions
                    nums.pop(0) #TODO:temp fix
                    #Loop thorugh nums array and make an table formatted string that can be easily converted to csv
                    for j,num in enumerate(nums):
                        text  +=  words[j] + " | " + num + "\n"
                        if structure == "Account summary":
                            if j > 0 and j < len(nums) - 1:
                                num = num.replace("$", "") if "$" in num else num
                                if float(num) != 0:
                                    structures.append(words[j]) 
                              
                final_text.append(text)
                                
    print(final_text)
    return final_text
"""