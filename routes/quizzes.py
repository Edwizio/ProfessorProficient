from flask import request, Blueprint, jsonify
from sqlalchemy.exc import SQLAlchemyError
import os

from ProfessorProficient.data_models import db, Quiz, Course, User
from GenAIRequests.RAG_Requests import generate_quiz_with_rag, setup_rag_components
from GenAIRequests.quiz_ai_requests import QuizRequest, QuizResponse

# Defining blueprint to be used in the app later
quizzes_bp = Blueprint("quizzes",__name__)

# Cache for RAG components to avoid reloading every time
rag_retriever = None
rag_model = None

@quizzes_bp.route("/generate-rag", methods=["POST"])
def generate_rag_quiz():
    """This function uses RAG to generate a quiz based on document context"""
    global rag_retriever, rag_model
    
    data = request.get_json()
    if not data.get("topic"):
        return {"error": "Topic is required"}, 400

    # Initialize RAG components if not already done
    if rag_retriever is None or rag_model is None:
        try:
            # Change directory to where the text file is expected if necessary, 
            # or ensure the path in setup_rag_components is correct.
            # RAG_Requests.py uses TextLoader("AND_Logic.txt")
            rag_retriever, rag_model = setup_rag_components()
        except Exception as e:
            return {"error": f"Failed to initialize RAG: {str(e)}"}, 500

    try:
        req = QuizRequest(
            topic=data["topic"],
            num_questions=int(data.get("num_questions", 5)),
            total_marks=int(data.get("total_marks", 10))
        )
        
        model_with_structure = rag_model.with_structured_output(QuizResponse)
        quiz_raw, costs = generate_quiz_with_rag(req, rag_retriever, rag_model)
        
        # Convert to structured output
        response = model_with_structure.invoke(f"Convert the following quiz into the structured QuizResponse format:\n\n{quiz_raw}")
        
        result = response.model_dump()
        result["costs"] = costs
        
        return jsonify(result), 200
    except Exception as e:
        return {"error": str(e)}, 500

# Getting all quizzes using GET
@quizzes_bp.route("/", methods=["GET"])
def get_quizzes():
    """This function returns a list of all quizzes"""
    quizzes = Quiz.query.all()
    if not quizzes:
        return {"message": "No quizzes found"}, 404

    return [
        {
            "id": q.id,
            "title": q.title,
            "total_marks": q.total_marks,
            "course_id": q.course_id,
            "created_by": q.created_by,
            "created_at": q.created_at.isoformat() if q.created_at else None # returning a standardized ISO Format of date and time
        }
        for q in quizzes
    ], 200


# Getting a specific quiz using its IT and GET
@quizzes_bp.route("/<int:quiz_id>", methods=["GET"])
def get_quiz(quiz_id):
    """This function returns a specific quiz by its ID"""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"error": "Quiz not found"}, 404

    return {
        "id": quiz.id,
        "title": quiz.title,
        "total_marks": quiz.total_marks,
        "course_id": quiz.course_id,
        "created_by": quiz.created_by,
        "created_at": quiz.created_at.isoformat() if quiz.created_at else None
    }, 200


# Creating a new quiz using POST
@quizzes_bp.route("/", methods=["POST"])
def create_quiz():
    """This function creates a new quiz in the database"""
    data = request.get_json()

    if not data.get("title") or not data.get("course_id") or not data.get("created_by"):
        return {"error": "Title, course_id and created_by are required fields"}, 400

    # Validating that Course and User exist that are associated with the quiz
    if not Course.query.get(data["course_id"]):
        return {"error": "Invalid course_id"}, 404
    if not User.query.get(data["created_by"]):
        return {"error": "User (creator) does not exist"}, 404 # Resource not found

    # Creating a new Quiz object
    quiz = Quiz(
        title=data["title"],
        total_marks=data.get("total_marks", 100),  # default marks 100
        due_date = data.get("due_date"),
        course_id=data["course_id"],
        created_by=data["created_by"]
    )
    # Adding the Quiz object to the database
    db.session.add(quiz)
    try:
        db.session.commit()
        return {"message": f"Quiz {quiz.title} created successfully", "id": quiz.id}, 201
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Updating the attributes of a quiz using PUT
@quizzes_bp.route("/<int:quiz_id>", methods=["PUT"])
def update_quiz(quiz_id):
    """This function updates the attributes of a quiz using its ID"""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"error": "Quiz not found"}, 404

    # Assigning the new values from the JSON to the program object other if the param exists, otherwise keeping the original value
    data = request.get_json()
    quiz.title = data.get("title", quiz.title)
    quiz.total_marks = data.get("total_marks", quiz.total_marks)
    quiz.due_date = data.get("due_date", quiz.due_date)
    quiz.course_id = data.get("course_id", quiz.course_id)

    try:
        db.session.commit()
        return {"message": "Quiz updated successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Deleting a quiz using DELETE
@quizzes_bp.route("/<int:quiz_id>", methods=["DELETE"])
def delete_quiz(quiz_id):
    """This function deletes a quiz using its ID."""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"error": "Quiz not found"}, 404

    db.session.delete(quiz)
    try:
        db.session.commit()
        return {"message": f"Quiz '{quiz.title}' deleted successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


@quizzes_bp.route("/search", methods=["GET"])
def search_quizzes():
    """This function searches the database for a particular quiz using its title."""

    # Assigning default value of empty string("") to avoid crashing in case keyword isn't provided
    keyword = request.args.get("keyword", "")

    # Searching through the database using the case-insensitive .ilike()
    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{keyword}%")).all()

    if not quizzes:
        return {"message": "No quizzes found for the given keyword"}, 404

    return [
        {"id": q.id, "title": q.title, "total_marks": q.total_marks}
        for q in quizzes
    ], 200


# Getting all quizzes for a specific course using GET
@quizzes_bp.route("/course/<int:course_id>", methods=["GET"])
def get_quizzes_by_course(course_id):
    """This function returns a list of all the quizzes of a specific course using its ID."""

    # Filtering through the quiz database using the condition where course.id is course_id
    quizzes = Quiz.query.filter(Quiz.course_id == course_id).all()

    if not quizzes:
        return {"message": "No quizzes found for this course"}, 404

    return [
        {"id": q.id, "title": q.title, "total_marks": q.total_marks}
        for q in quizzes
    ], 200
