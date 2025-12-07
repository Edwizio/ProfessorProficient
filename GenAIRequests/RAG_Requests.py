# rag_history.txt
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
from quiz_ai_requests import generate_quiz, QuizRequest

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


def setup_rag_components():
    # Offline Phase

    # 1. Load
    loader = TextLoader("AND_Logic.txt")
    docs = loader.load()
    print(f"Loaded {len(docs)} documents!")

    # 2. Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    print(f"Document split into {len(chunks)} chunks!")

    # 3. Embed & 4. Store
    print("Creating vector store")
    vectorstore = FAISS.from_documents(documents=chunks, embedding=OpenAIEmbeddings(model= "text-embedding-3-small",api_key=API_KEY))
    print("Vector store created successfully")

    model = ChatOpenAI(model="gpt-4o-mini", api_key=API_KEY)

    # setup retriever
    retriever = vectorstore.as_retriever()

    return retriever, model


if __name__ == "__main__":
    # Offline
    retriever, model = setup_rag_components()

    # Online
    while True:
        user_question = input("\nYour question: ")

        print("Thinking...")

        # 1. Retrieve
        retrieved_docs = retriever.invoke(user_question)

        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # 2. Augment
        prompt_template = f"""Answer the following question by taking your knowledge AND using the context:
        {context}
        Question: {user_question}
        """

        # 3. Generate
        response = model.invoke(prompt_template)


        print("\nAnswer", response.content)

        req = QuizRequest(
            topic="logic gates",
            total_marks=10,
            num_questions=5
        )

        quiz = generate_quiz(req)
        print(quiz)