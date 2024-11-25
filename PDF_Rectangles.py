from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from io import BytesIO


# Function to draw multiple rectangles on a page
def add_rectangles_to_page(pdf_page, rectangles):
    # Create a memory buffer
    packet = BytesIO()
    can = canvas.Canvas(packet)

    # Draw rectangles
    for rect_coords in rectangles:
        x, y, width, height = rect_coords
        can.setStrokeColorRGB(1, 0, 0)  # Red outline
        can.setLineWidth(2)
        can.rect(x, y, width, height, fill=0)  # No fill

    can.save()
    packet.seek(0)

    # Merge the rectangles onto the original page
    overlay_pdf = PdfReader(packet)
    pdf_page.merge_page(overlay_pdf.pages[0])
    return pdf_page


def add_rectangles_to_pdf(input_pdf, rectangles, page_numbers):
    """
    Add rectangles to specified pages of a PDF.

    :param input_pdf: Path to the input PDF.
    :param rectangles: A dictionary where keys are page numbers (0-based) 
                       and values are lists of rectangle coordinates [(x, y, width, height), ...].
    :param page_numbers: List of page numbers (0-based) to which the rectangles should be added.
    """
    # Load the PDF
    output_pdf = "output_with_rectangles.pdf"
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Iterate through pages and add rectangles where specified
    for page_number, page in enumerate(reader.pages):
        if page_number in page_numbers:
            # Apply rectangles to the specified page
            modified_page = add_rectangles_to_page(page, rectangles[page_number])
        else:
            modified_page = page  # Keep the page unchanged
        writer.add_page(modified_page)

    # Save the output PDF
    with open(output_pdf, "wb") as f:
        writer.write(f)

    print(f"Rectangles added to {output_pdf}")

