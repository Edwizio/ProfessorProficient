# AND_Logic.txt
'''
Logic gates are the basic building blocks of digital circuits. They take one or more input signals and produce a single output based on a specific logical rule. Every action performed by a computer, from simple calculations to running complex software, ultimately depends on these tiny electronic decision-makers.

The most common logic gates include AND, OR, and NOT. An AND gate outputs 1 only when all its inputs are 1, while an OR gate outputs 1 if at least one input is 1. The NOT gate is different because it has only one input and simply flips it—turning a 1 into a 0 and a 0 into a 1.

More advanced gates such as NAND, NOR, XOR, and XNOR are combinations of the basic ones. For example, a NAND gate is an AND gate followed by a NOT, which means it outputs 0 only when all inputs are 1. These gates allow more complex logical operations, making them essential in designing processors, memory units, and control systems.

Logic gates are implemented using tiny transistors on microchips. As technology advances, these transistors continue to shrink, allowing more gates to fit into a single chip and enabling faster and more powerful electronic devices. Even though they operate on simple rules, the collective behavior of millions or billions of logic gates is what makes modern computing possible.
'''
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from ProfessorProficient.GenAIRequests.quiz_ai_requests import QuizRequest, QuizResponse, MODEL_PRICING
from langchain_community.callbacks import get_openai_callback
import time


load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


def setup_rag_components(model_name: str = "gpt-4.1-mini", temperature: float = 0.3):
    """This function sets up the basic RAG components to be used in the subsequent requests"""
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "AND_Logic.txt")

    # 1. Load
    loader = TextLoader(file_path)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents!")

    # 2. Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"Document split into {len(chunks)} chunks!")

    # 3. Embed & 4. Store
    print("Creating vector store")
    vectorstore = FAISS.from_documents(documents=chunks, embedding=OpenAIEmbeddings(model= "text-embedding-3-small",api_key=API_KEY))
    print("Vector store created successfully")

    model = ChatOpenAI(model=model_name, api_key=API_KEY, temperature=temperature)
    print(f"model: {model.model_name}")
    # setup retriever
    retriever = vectorstore.as_retriever()

    return retriever, model


def generate_quiz_with_rag(req, retriever, model):
    """Using the function defined above, this function creates a quiz."""
    # Retrieving the context to be used in the prompt for RAG, but first converting the whole request to JSON object so
    # that it can be passed as a whole to the retriever object
    query = req.model_dump_json()
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Augmenting the context in the prompt
    prompt = f"""
    Use ONLY the following context to generate a quiz: {context}
    
    Topic: {req.topic}
    Number of Questions: {req.num_questions}
    Total Marks: {req.total_marks}
    
    Generate exactly {req.num_questions} questions. The total marks for the quiz should be {req.total_marks}.
    """

    start = time.perf_counter()

    # Tracking the cost and generating the quiz using context with in the prompt
    with get_openai_callback() as cb:
        response = model.invoke(prompt)

    end = time.perf_counter()

    latency = end - start

    # Calculate cost manually if LangChain callback doesn't support the model (e.g. gpt-4o-mini)
    total_cost = cb.total_cost
    if total_cost == 0 and cb.total_tokens > 0:
        pricing_key = model.model_name if model.model_name in MODEL_PRICING else "gpt-4.1-mini"
        if pricing_key in MODEL_PRICING:
            input_cost = (cb.prompt_tokens * MODEL_PRICING[pricing_key]["input"] / 1000)
            output_cost = (cb.completion_tokens * MODEL_PRICING[pricing_key]["output"] / 1000)
            total_cost = input_cost + output_cost

    cost_info = {
        "model_name": model.model_name,
        "prompt_tokens": cb.prompt_tokens,
        "completion_tokens": cb.completion_tokens,
        "total_tokens": cb.total_tokens,
        "cost_usd": f"{total_cost :.6f}",
        "Latency (time taken)": f"{latency :.2f}"
    }

    return response, cost_info


if __name__ == "__main__":
    retriever, model = setup_rag_components()

    req = QuizRequest(
            topic="logic gates",
            total_marks=10,
            num_questions=5
    )

    # Defining model with structured response
    model_with_structure = model.with_structured_output(QuizResponse)

    # Generating the quiz
    quiz, costs = generate_quiz_with_rag(req, retriever, model)

    # Pass the quiz text to the structured model
    response = model_with_structure.invoke(f"Convert the following quiz into the structured QuizResponse format:\n\n{quiz}")

    print(costs)

    json_quiz = response.model_dump_json(indent=2)  # a pretty json string which has 2 indents spacing between each level
    print(json_quiz)