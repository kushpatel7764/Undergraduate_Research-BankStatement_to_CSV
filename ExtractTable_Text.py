#Need to assign google api key here
import os 
import json
import re
from google.cloud import vision
from google.cloud import storage
import PDF_Rectangles
import Utility
import Excel_Converter

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./semiotic-lamp-431814-j7-9de307902d88.json"

#Beauty full soup
#Youtube video playist was used, YouTube Video Title: Google Vision API in Python by Jie Jenn

def detect_document_text(gcs_source_uri, gcs_destination_uri):
    mime_type = "application/pdf"

    batch_size = 4
    #Initiates image annotator client 
    client = vision.ImageAnnotatorClient()
    #Get the type of detection to perform
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    #Set the location to read the input fiels from 
    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    #Set the desired input location and metadata.
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)
    #set the out put location 
    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    #Set the desired input location and metadata.
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size
    )
    #Give file annotation request 
    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config, output_config=output_config
    )
    #Annotate PDF file for all the pages 
    operation = client.async_batch_annotate_files(requests=[async_request])

    print("Waiting for the operation to finish.")
    operation.result(timeout=420)

    # Get the google cloud storage client so we can make api requests later to get_bucket
    storage_client = storage.Client()
    #Google cloud URI: gs://bucket-name/object-path
    #Cloud_location splits: ["gs:", "bucket-name/object-path"] 
    cloud_location_split = gcs_destination_uri.split("//")
    print(f" cloud_location is {cloud_location_split}")
    cloud_location = cloud_location_split[1].split("/")
    #First part of cloudlocation is bucket name
    bucket_name = cloud_location[0]
    #the rest is prefix
    prefix = "/".join(cloud_location[1:])

    
    #Get the bucket using bucket name
    bucket = storage_client.get_bucket(bucket_name)

    # List objects with the given prefix, filtering out folders.
    blob_list = [
        blob
        for blob in list(bucket.list_blobs(prefix=prefix))
        if not blob.name.endswith("/")
    ]


    # Process the first output file from GCS.
    # Since we specified batch_size=5, the first response contains
    # the first five pages of the input file.
    output = blob_list[0]

    
    json_string = output.download_as_bytes().decode("utf-8")
    #response contain "responses" which are like arrays = len(page)
    #so responses[0] is page 1 then responses[1] is page 2 and so on
    #At each index of reponses there is content which has info like pagenumber and URI
    #Then there also "fullTextAnotation" which has info about pages which contains things like bounding boxes and width and height of the page
    #"fullTextAnnotation" also has a text attribute which contains all the extracted text 
    response = json.loads(json_string)
    full_pdf_text = []
    for i in range(response["responses"][-1]["context"]["pageNumber"]):
        # The actual response for the first page of the input file.
        page_response = response["responses"][i]
        annotation = page_response["fullTextAnnotation"]
        print(f"Page {i + 1} \n {annotation["text"]}")
        #Table Structure array: 
        full_pdf_text.append(annotation["text"])
    #Annotating PDF
    """ rectangles = []
    for i in range(4):
        rectangle = []
        for block in response["responses"][i]["fullTextAnnotation"]["pages"][0]["blocks"]:
            vertex_x1 = (block["boundingBox"]["normalizedVertices"][0]["x"]) * annotation["pages"][0]["width"]
            vertex_y1 = (block["boundingBox"]["normalizedVertices"][0]["y"]) * annotation["pages"][0]["height"]
            vertex_x2 = (block["boundingBox"]["normalizedVertices"][2]["x"]) * annotation["pages"][0]["width"]
            vertex_y2 = (block["boundingBox"]["normalizedVertices"][2]["y"]) * annotation["pages"][0]["height"]
            width = vertex_x2 - vertex_x1
            height = vertex_y2 - vertex_y1
            rectangle.append((vertex_x1, vertex_y1, width, height))
        rectangles.append(rectangle)
    PDF_Rectangles.add_rectangles_to_pdf("./bankstatement.pdf", rectangles,[0, 1, 2, 3])
     """
        
    # Here we print the full text from the first page.
    # The response contains more information:
    # annotation/pages/blocks/paragraphs/words/symbols
    # including confidence scores and bounding boxes
    
    #full_pdf_text is an array with contains all pages of text in pdf 
    return full_pdf_text


def Text_to_tableText(full_pdf_text):
    #full_pdf_text is an array with each element containing all text from each page of pdf
    table_text_per_page = [] #formated text to table from each page of pdf
    first_page_formatted_text, structure = Utility.initialize_first_page_text_and_structure(full_pdf_text[0], "Account summary")
    table_text_per_page.append(first_page_formatted_text)
    #Since first_page is initialzed, I no longer need first page text 
    full_pdf_text.pop(0)
    #loop through full_pdf_text 
    for pdf_page in full_pdf_text:
        tuple_structure = Utility.getAmountOfStructInPage(pdf_page, structure)
        reg_formated_text = Utility.initialize_reg_page(pdf_page, tuple_structure, structure) #can be NONE
        table_text_per_page.append(reg_formated_text)
    return table_text_per_page
    
    
    

def text_to_csv(text):
    toExecl = Excel_Converter.ExcelOutput(text)
    toExecl.start()

    
        
    
    

#Input URI: gs://semiotic-lamp-431814-j7.appspot.com/bankstatement.pdf
#Output URI: semiotic-lamp-431814-j7.appspot.com/output
full_pdf_text = detect_document_text("gs://semiotic-lamp-431814-j7.appspot.com/bankstatement.pdf", "gs://semiotic-lamp-431814-j7.appspot.com/output/")
table_text = Text_to_tableText(full_pdf_text)
print(table_text)
text_to_csv(table_text)
