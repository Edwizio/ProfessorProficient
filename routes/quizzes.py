from flask import db, request
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.app import app
from ProfessorProficient.data_models import Quiz, Course, User

# Getting all quizzes using GET
@app.route("/", methods=["GET"])
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
@app.route("/<int:quiz_id>", methods=["GET"])
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
@app.route("/", methods=["POST"])
def create_quiz():
    """This function creates a new quiz in the database"""
    data = request.get_json()

    if not data.get("title") or not data.get("course_id") or not data.get("created_by"):
        return {"error": "Title, course_id and created_by are required fields"}, 400

    # Validate that Course and User exist that are associated with the quiz
    if not Course.query.get(data["course_id"]):
        return {"error": "Invalid course_id"}, 404
    if not User.query.get(data["created_by"]):
        return {"error": "User (creator) does not exist"}, 404 # Resource not found

    # Creating a new Quiz object
    quiz = Quiz(
        title=data["title"],
        total_marks=data.get("total_marks", 100),  # default marks 100
        course_id=data["course_id"],
        created_by=data["created_by"]
    )
    # Adding the Quiz object to the database
    db.session.add(quiz)
    try:
        db.session.commit()
        return {"message": "Quiz created successfully", "id": quiz.id}, 201
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409
