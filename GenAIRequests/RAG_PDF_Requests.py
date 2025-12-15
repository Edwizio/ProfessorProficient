import os
from dotenv import load_dotenv

# 1. Load PDF with PyPDF
from pypdf import PdfReader # importing the relevant files

reader = PdfReader("TBQ_Feher_DigitalLogicbw.pdf")
full_text = ""
for page in reader.pages:
    full_text += page.extract_text() + "\n"


def extract_pages_pdfreader(pdf_path, drop_first=5, drop_last=12):
    """This function etracts the desired pages from the PDF and loads it into a string variable using PyPDF """
    reader = PdfReader(pdf_path)
    total = len(reader.pages)

    start = drop_first
    end = total - drop_last

    extracted_pages = ""

    for i in range(start, end):
        page = reader.pages[i]
        text = page.extract_text() + "\n"
        extracted_pages += text

    return extracted_pages


# 2. Cleaning the text to get rid of non ASCII characters

def clean_text(text):
    """This function is meant to remove all the unwanted characters from the text using the Regular
    Expressions (re) module"""

    # Remove non-ASCII characters except new line and tabs using the sub method which finds and replaces the desired
    # characters and then modifies the original string 'text'
    text = re.sub(r"[^\x00-\x7F\n\t]+", " ", text)

    # These (cid:##) sequences are common in OCR-extracted PDFs and represent missing glyphs or corrupted characters
    text = re.sub(r"\(cid:\d+\)", " ", text)

    # Removes everything from the first occurrence of "Appendix" to the end
    #text = re.sub(r"(?is)appendix.*$", "", text)

    # Normalize Unicode (fix ligatures like ﬁ → fi)
    #text = unicodedata.normalize("NFKD", text)

    return text.strip()


# Usage:
pages = extract_pages_pdfreader("TBQ_Feher_DigitalLogicbw.pdf")
print(len(pages))
print(pages)