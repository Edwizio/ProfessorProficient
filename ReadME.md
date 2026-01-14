📘 ProfessorProficient – AI-Powered LMS with RAG

ProfessorProficient is an AI-powered Learning Management System (LMS) that uses Retrieval-Augmented Generation (RAG) to automatically create quizzes and educational content from course materials. The platform combines traditional LMS features with modern AI pipelines for intelligent content generation.

🚀 Key Features

* AI-driven quiz generation using RAG (Retrieval-Augmented Generation)

* Document-based learning using FAISS vector search

* Secure quiz and assignment management system
 
* MCQ and descriptive question support
 
* Fully structured outputs using Pydantic validation
 
* RESTful API architecture for easy frontend integration

🧩 Tech Stack

* Python 3.10+
* Flask
* LangChain
* OpenAI GPT models
* OpenAI Embeddings
* FAISS Vector Store
* SQLite (lms.db)
* Pydantic
* dotenv

📁 Project Structure
ProfessorProficient/
│
├── data/
│   └── lms.db
│
├── GenAIRequests/
│   ├── AND_Logic.txt
│   ├── descriptive_quiz_ai_requests.py
│   ├── quiz_ai_requests.py
│   ├── RAG_Requests.py
│   └── test_requests.py
│
├── routes/
│   ├── assignments.py
│   ├── courses.py
│   ├── programs.py
│   ├── question_options.py
│   ├── questions.py
│   ├── quizzes.py
│   ├── student_answers.py
│   └── users.py
│   
├── templates/
│   ├── assignments.html
│   ├── courses.html
│   ├── generate_quiz.html
│   ├── index.html
│   ├── layout.html
│   ├── programs.html
│   ├── quizzes.html
│   └──  users.html
│
├── app.py
├── data_models.py
├── .env
├── db_schema.png
├── Updated_DB_Schema.png
├── Updated_DB_Scheme_2.png
└── ReadME.md


⚙️ Installation & Setup

1. Clone the Repository
`git clone https://github.com/your-username/ProfessorProficient.git
cd ProfessorProficient
`

2. Create Virtual Environment
`python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows`

3. Install Dependencies
`pip install -r requirements.txt`

4. Environment Variables

Create a .env file in the root:

`OPENAI_API_KEY=your_api_key_here`

▶️ Running the Application

Start the Flask server:

`python app.py`

The API will run at:

http://localhost:5000

🧠 AI / RAG Pipeline Overview

The RAG system works as follows:

1. Loads course documents from GenAIRequests/
2. Splits documents into semantic chunks
3. Converts chunks into embeddings
4. Stores embeddings in FAISS
5. Retrieves the most relevant chunks based on user query
6. Injects context into GPT prompt
7. Generates structured quiz JSON output

✅ Example: Quiz Generation

`from GenAIRequests.RAG_Requests import generate_quiz_with_rag
from GenAIRequests.quiz_ai_requests import QuizRequest

req = QuizRequest(
    topic="logic gates",
    num_questions=5,
    total_marks=10
)

quiz = generate_quiz_with_rag(req)
print(quiz)
`

📄 Example Output

{
  "topic": "logic gates",
  "total_marks": 10,
  "questions": [
    {
      "question": "What does an AND gate output when both inputs are 1?",
      "options": ["0", "1", "Depends on voltage", "Undefined"],
      "correct_answer": "1",
      "marks": 2
    }
  ]
}
