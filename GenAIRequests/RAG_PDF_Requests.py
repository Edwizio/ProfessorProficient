from langchain_community.callbacks import get_openai_callback
from pypdf import PdfReader # importing the loader files
from ProfessorProficient.GenAIRequests.quiz_ai_requests import API_KEY, QuizResponse, QuizRequest, Question
import re # importing re(regex for cleaning)
import unicodedata # to clean the Unicode data
from langchain_text_splitters import CharacterTextSplitter

from langchain_openai import ChatOpenAI, OpenAIEmbeddings # for AI model object and embeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser # parsing the Pydantic models using langchain parsers

from langchain_community.vectorstores import FAISS # for embedding and vector stores

from langchain_core.documents import Document # for the chunking model

import time # for latency calculations


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

paragraph_splitter = CharacterTextSplitter(
    separator="\n\n",       # key setting: split on empty line
    chunk_size=500,         # or 1000 or whatever you want
    chunk_overlap=50,
    length_function=len,    # means that the size of chunk is based on number of characters. i.e. length of the text
)
# Chunking or making meaningful sections of the text based of splitter we just created


pages = extract_pages_pdfreader("TBQ_Feher_DigitalLogicbw.pdf")
cleaned_pages = [clean_text(p) for p in pages] # cleaning the text page wise

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

vectorstore = FAISS.from_documents(documents=documents, embedding=OpenAIEmbeddings(model= "text-embedding-3-small",api_key=API_KEY))

retriever = vectorstore.as_retriever() # setup retriever

# Creating the output parser to be used in the RAG
parser = PydanticOutputParser(pydantic_object=QuizResponse)

# Defining the LLM with low temperature initially
llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0.3,
    api_key=API_KEY
)

# Defining the prompt using ChatPromptTemplate to use variables inside the prompt
prompt = ChatPromptTemplate.from_template("""
You are an undergrad level instructor of Digital Logic Design creating a multiple-choice quiz.

CONTEXT:
{context}

QUIZ PARAMETERS:
Topic: {topic}
Number of questions: {num_questions}
Total marks: {total_marks}

{format_instructions}
""")


def generate_quiz_rag_plus_llm(request, retriever):
    """This function implements the RAG functionality to generate the quiz taking the QuizRequest and retriever"""

    # Retrieving relevant chunks
    docs = retriever.invoke(request.topic)

    # Combining retrieved context
    context = "\n\n".join(
        f"(Page {d.metadata['page']}) {d.page_content}"
        for d in docs
    )

    # Building the prompt

    messages = prompt.format_messages(
        context=context,
        topic=request.topic,
        num_questions=request.num_questions,
        total_marks=request.total_marks,
        format_instructions=parser.get_format_instructions(),
    )

    start = time.perf_counter()

    # Tracking the cost and generating the quiz using context with in the prompt
    with get_openai_callback() as cb:
        response = llm.invoke(messages)

    end = time.perf_counter()
    latency = end -  start

    cost_info = {
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "total_tokens": cb.total_tokens,
        "cost_usd": f"{cb.total_cost:.6f}",
        "Latency (time taken)": f"{latency:.2f}"
    }

    # returning the parsed response
    return parser.parse(response.content), cost_info


def generate_quiz_rag_only(request, retriever):
    """This function instructs the prompt to use the RAG only"""
    query = request.model_dump_json()
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Augmenting the context in the prompt
    prompt_text = f"""
    You are an undergrad level instructor of Digital Logic Design.

    Use ONLY the following context to generate a quiz.
    CONTEXT:
    {context}

    QUIZ
    PARAMETERS:
    Topic: {request.topic}
    Number
    of
    questions: {request.num_questions}
    Total
    marks: {request.total_marks}

    {parser.get_format_instructions()}
    """
    start = time.perf_counter()

    # Tracking the cost and generating the quiz using context with in the prompt
    with get_openai_callback() as cb:
        response = llm.invoke(prompt_text)

    end = time.perf_counter()
    latency = end - start

    cost_info = {
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "total_tokens": cb.total_tokens,
        "cost_usd": f"{cb.total_cost :.6f}",
        "Latency (time taken)": f"{latency:.2f}"
    }

    return parser.parse(response.content), cost_info # parsing the response to get the correct structure


# the dunder main
if __name__ == "__main__":

    # Printing the results
    #for i, doc in enumerate(documents[:5]):
        #print(f"\n--- Chunk {i} ---")
        #print("Page:", doc.metadata["page"])
        #print(doc.page_content[:])

    quiz_request = QuizRequest(
        topic="logic gates",
        num_questions=10,
        total_marks=10
    )

    quiz, costs = generate_quiz_rag_plus_llm(quiz_request, retriever)

    print(f"model: {llm.model_name}")
    print(costs)
    print(quiz.title)
    for q in quiz.questions:
        print("\nQ:", q.question)
        for opt in q.options:
            print("-", opt)
        print("✔ Answer:", q.correct_answer)



