
"""
Extracts all the text from a PDF file and joins it into one big string.

Steps:
1. Open the PDF with PdfReader - this reads the file and lets us access
   each page separately (reader.pages is a list of page objects).
2. Create an empty string, all_text, to collect the text as we go.
3. Loop through every page in the PDF.
4. Call page.extract_text() - this pulls the readable text out of that page.
   It can return None if the page has no extractable text (e.g. a scanned
   image), which is why we check "if text:" before using it.
5. Add the page's text to all_text, plus a newline so pages don't run
   together.
6. After the loop, print the combined text of the whole document.
"""

from pypdf import PdfReader
from backend.constants import DATA_PATH


def extract_text_from_pdf(path) -> str:
    all_text = ""

    reader = PdfReader("data/Netherland_Dwarf_rabbit.pdf")

    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"
    return all_text


def export_txt(text, path):
    """
    Saves a string of text out to a .txt file.
    """
    with open(path, 'w') as f:
        f.write(text)

# Only runs when this script is executed directly, e.g. "python -m backend.pdfs_to_text"

if __name__ == "__main__":
    for pdf_path in DATA_PATH.glob("*pdf"):  # find every pdf in folder
        pdf_text = extract_text_from_pdf(pdf_path)  # get its text

        filename = f"{pdf_path.stem.casefold()}.txt"   # same name as the PDF, lowercased, with .txt instead of .pdf

        export_txt(pdf_text, DATA_PATH / filename)  # save it next to the original PDF