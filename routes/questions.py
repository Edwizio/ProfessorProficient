from flask import request
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.app import app
from ProfessorProficient.data_models import Question, db, QuestionOption

# Getting a list of all questions using GET
@app.route('/questions', methods=['GET'])
def get_questions():
    """This function gets a list of all the questions with optional filters based on quiz_id, assignment_id, created_by,
    question_type, min or max marks and keywords"""

    quiz_id = request.args.get("quiz_id")
    assignment_id = request.args.get("assignment_id")
    created_by = request.args.get("created_by")
    question_type = request.args.get("type")
    contains = request.args.get("contains")
    min_marks = request.args.get("min_marks", type=int)
    max_marks = request.args.get("max_marks", type=int)


    query = Question.query

    if quiz_id:
        query = query.filter(Question.quiz_id == quiz_id)

    if assignment_id:
        query = query.filter(Question.assignment_id == assignment_id)

    if created_by:
        query = query.filter(Question.created_by == created_by)

    if question_type:
        query = query.filter(Question.question_type.ilike(question_type))

    if contains:
        query = query.filter(Question.question_text.ilike(f"%{contains}%"))

    if min_marks is not None:
        query = query.filter(Question.marks >= min_marks)

    if max_marks is not None:
        query = query.filter(Question.marks <= max_marks)

    questions = query.all()

    return [{
        "id": q.id,
        "question_text": q.question_text,
        "question_type": q.question_type,
        "marks": q.marks,
        "quiz_id": q.quiz_id,
        "assignment_id": q.assignment_id,
        "created_by": q.created_by,
        "created_at": q.created_at.isoformat() if q.created_at else None,
        "options_count": len(q.options),
        "student_answers_count": len(q.student_answers)
    } for q in questions], 200


# Creating a new question using POST
@app.route("/questions", methods=["POST"])
def create_question():
    """This function creates a new question in the database based on the parameters provided"""

    data = request.get_json()

    if not data or "question_text" not in data:
        return {"error": "Missing required field 'question_text'."}, 400

    new_question = Question(
        question_text=data["question_text"],
        question_type=data.get("question_type", "text"),
        marks=data.get("marks"),
        quiz_id=data.get("quiz_id"),
        assignment_id=data.get("assignment_id"),
        created_by=data.get("created_by")
    )

    try:
        db.session.add(new_question)
        db.session.flush() # creates the new_question ID but not commiting yet as we have to check if it has the MCQ options

    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while creating the question."}, 409


    # If the question is an MCQ type
    options = data.get("options", [])
    for idx, opt in enumerate(options):
        option = QuestionOption(
            question_id=new_question.id,
            option_text=opt.get("option_text"),
            is_correct=opt.get("is_correct", False),
            order_index=idx
        )
        db.session.add(option)

    try:
        db.session.commit()
        return {"message": "Question created successfully", "id": new_question.id}, 201
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while creating the question."}, 409


# Updating a question using PUT
@app.route("/questions/<int:question_id>", methods=["PUT"])
def update_question(question_id):
    """This function updates a question's parameters using its ID"""

    question = Question.query.get_or_404(question_id)
    data = request.get_json()

    question.question_text = data.get("question_text", question.question_text)
    question.question_type = data.get("question_type", question.question_type)
    question.marks = data.get("marks", question.marks)
    question.quiz_id = data.get("quiz_id", question.quiz_id)
    question.assignment_id = data.get("assignment_id", question.assignment_id)

    try:
        db.session.commit()
        return {"message": f"Question {question.id} updated successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while updating the question."}, 409


# Deleting a question using DELETE
@app.route("/questions/<int:question_id>", methods=["DELETE"])
def delete_question(question_id):
    """This function deletes question by ID"""

    question = Question.query.get_or_404(question_id)

    db.session.delete(question)

    try:
        db.session.commit()
        return {"message": f"Question {question.id} deleted successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while deleting the question."}, 409


# Getting a question using GET
@app.route("/questions/<int:question_id>", methods=["GET"])
def get_question_by_id(question_id):
    """This function returns a question based on its ID along with its question fields, list of options and count of answers"""

    q = Question.query.get_or_404(question_id)

    return {
        "id": q.id,
        "question_text": q.question_text,
        "question_type": q.question_type,
        "marks": q.marks,
        "quiz_id": q.quiz_id,
        "assignment_id": q.assignment_id,
        "created_by": q.created_by,
        "created_at": q.created_at.isoformat() if q.created_at else None,
        "options": [
            {
                "id": opt.id,
                "option_text": opt.option_text,
                "is_correct": opt.is_correct,
                "order_index": opt.order_index
            }
            for opt in q.options
        ],
        "student_answers_count": len(q.student_answers)
    }, 200


# Searching for a questions using GET
@app.route("/questions/search", methods=["GET"])
def search_questions():
    """This function searches inside the question_text parameter, optional filters can be question_type, min_marks or
    max_marks"""

    keyword = request.args.get("q")
    q_type = request.args.get("type")
    min_marks = request.args.get("min_marks", type=int)
    max_marks = request.args.get("max_marks", type=int)

    if not keyword:
        return {"error": "Missing search query 'q'."}, 400

    query = Question.query.filter(
        Question.question_text.ilike(f"%{keyword}%")
    )

    if q_type:
        query = query.filter(Question.question_type.ilike(q_type))

    if min_marks is not None:
        query = query.filter(Question.marks >= min_marks)

    if max_marks is not None:
        query = query.filter(Question.marks <= max_marks)

    results = query.all()

    if not results:
        return {"message": "No questions found"}, 404

    return [{
        "id": q.id,
        "question_text": q.question_text,
        "question_type": q.question_type,
        "marks": q.marks
    } for q in results], 200


# Counting the questions using GET
@app.route("/questions/count", methods=["GET"])
def count_questions():
    """This function returns count of questions grouped by question_type"""

    result = db.session.query(
        Question.question_type,
        func.count(Question.id)
    ).group_by(Question.question_type).all()

    return {
        q_type if q_type else "unspecified": count
        for q_type, count in result
    }, 200
