from flask import db, request
from ProfessorProficient.app import app
from ProfessorProficient.data_models import Quiz, Course

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