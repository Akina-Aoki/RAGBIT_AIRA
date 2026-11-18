
"""
Stage 1 of the ingestion pipeline: converts each PDF in DATA_PATH into a
plain-text .txt file sitting next to it. ingestion.py (stage 2) later reads
those .txt files into the vector database — this script never touches the
database itself.

Run directly with `uv run pdfs_to_text.py` (see the __main__ block below).
"""

from pypdf import PdfReader
from backend.constants import DATA_PATH


def extract_text_from_pdf(path) -> str:
    """
    Reads a single PDF and returns all of its text as one string.

    Steps:
    1. Open the PDF with PdfReader — this reads the file and lets us access
       each page separately (reader.pages is a list of page objects).
    2. Create an empty string, all_text, to collect the text as we go.
    3. Loop through every page in the PDF.
    4. Call page.extract_text() — this pulls the readable text out of that
       page. It can return None if the page has no extractable text (e.g.
       a scanned image), which is why we check "if text:" before using it.
    5. Add the page's text to all_text, plus a newline so pages don't run
       together.

    BUG: the `path` argument is accepted but never used — the line below
    always opens "data/Netherland_Dwarf_rabbit.pdf" no matter which file
    was passed in. That's why, as of this writing, every generated .txt
    file in data/ contains the same Netherland Dwarf rabbit text. To fix,
    change the PdfReader(...) line to `PdfReader(path)`.
    """
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

# Only runs when this script is executed directly (e.g. "uv run pdfs_to_text.py"),
# not when some other script imports functions from this file.
if __name__ == "__main__":
    for pdf_path in DATA_PATH.glob("*pdf"):  # find every PDF in DATA_PATH
        pdf_text = extract_text_from_pdf(pdf_path)  # get its text

        filename = f"{pdf_path.stem.casefold()}.txt"   # same name as the PDF, lowercased, with .txt instead of .pdf

        export_txt(pdf_text, DATA_PATH / filename)  # save it next to the original PDF