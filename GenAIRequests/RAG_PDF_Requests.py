from pypdf import PdfReader # importing the loader files
from ProfessorProficient.GenAIRequests.quiz_ai_requests import API_KEY


# 1. Load PDF with PyPDF

def extract_pages_pdfreader(pdf_path, drop_first=7, drop_last=5):
    """This function extracts the desired pages from the PDF and loads it into a string variable using PyPDF """
    reader = PdfReader(pdf_path)
    total = len(reader.pages)

    start = drop_first
    end = total - drop_last

    extracted_pages = []

    for i in range(start, end):
        page = reader.pages[i]
        text = page.extract_text() or ""
        extracted_pages.append(text)

    return extracted_pages


# 2. Cleaning the text to get rid of non ASCII characters
import re
import unicodedata

# Symbols we ALLOW in logic / CS textbooks
ALLOWED_SYMBOLS = set("+-=*/()[]{}<>≤≥≈≠→←↔∧∨¬|&^.,:;")

def clean_text(text):
    """This function is meant to remove all the unwanted characters from the text using the Regular
    Expressions (re) module"""

    # Remove non-ASCII characters except new line and tabs using the sub method which finds and replaces the desired
    # characters and then modifies the original string 'text'
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # These (cid:##) sequences are common in OCR-extracted PDFs and represent missing glyphs or corrupted characters
    text = re.sub(r"\(cid:\d+\)", " ", text)

    # Normalize Unicode (fix ligatures like ﬁ → fi)
    text = unicodedata.normalize("NFKD", text)

    text = re.sub(r'\t+', ' ', text)  # remove tabs
    text = re.sub(r'\s{2,}', ' ', text)  # collapse extra spaces

    cleaned_lines = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        total = len(line)
        if total == 0:
            continue

        letters = sum(c.isalnum() for c in line)
        allowed = sum(c in ALLOWED_SYMBOLS for c in line)
        spaces = line.count(" ")
        junk = total - letters - allowed - spaces

        # Detecting OCR or barcode
        junk_ratio = junk / total
        letter_ratio = letters / total

        # remove OCR garbage lines
        if junk_ratio > 0.45:
            continue
        if letter_ratio < 0.2:
            continue
        if len(line) < 4:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


# 3. Splitting using Langchain Splitters
from langchain_text_splitters import CharacterTextSplitter

paragraph_splitter = CharacterTextSplitter(
    separator="\n\n",       # key setting: split on empty line
    chunk_size=500,         # or 1000 or whatever you want
    chunk_overlap=50,
    length_function=len,    # means that the size of chunk is based on number of characters. i.e. length of the text
)
# Chunking or making meaningful sections of the text based of splitter we just created


pages = extract_pages_pdfreader("TBQ_Feher_DigitalLogicbw.pdf")
cleaned_pages = [clean_text(p) for p in pages] # cleaning the text page wise

from langchain.schema import Document


documents = []

for page_idx, page_text in enumerate(cleaned_pages):
    chunks = paragraph_splitter.split_text(page_text)

    for chunk_idx, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "page": page_idx + 1,
                    "chunk": chunk_idx
                }
            )
        )

print("Total chunks:", len(documents))


# Embedding and storing, i.e. Creating the vector store using FAISS
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

vectorstore = FAISS.from_documents(documents=documents, embedding=OpenAIEmbeddings(model= "text-embedding-3-small",api_key=API_KEY))

retriever = vectorstore.as_retriever() # setup retriever


# Printing the results

for i, doc in enumerate(documents[:5]):
    print(f"\n--- Chunk {i} ---")
    print("Page:", doc["metadata"]["page"])
    print(doc["text"][:])
