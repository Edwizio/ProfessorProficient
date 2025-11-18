from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.data_models import StudentAnswer, db

student_answers_bp = Blueprint("student_answers", __name__)


# Getting all answers using GET
@student_answers_bp.route("/", methods=["GET"])
def get_all_answers():
    """This function gets all the answers in the database submitted by the students"""

    answers = StudentAnswer.query.all()
    if not answers:
        return {"message": "No student answers found"}, 404

    return [
        {
            "id": ans.id,
            "question_id": ans.question_id,
            "student_id": ans.student_id,
            "selected_option_id": ans.selected_option_id,
            "answer_text": ans.answer_text,
            "marks_awarded": ans.marks_awarded,
            "evaluated_by_ai": ans.evaluated_by_ai,
            "evaluated_by_teacher": ans.evaluated_by_teacher,
            "attempt_number": ans.attempt_number,
            "submitted_at": ans.submitted_at.isoformat() if ans.submitted_at else None
        }
        for ans in answers
    ], 200


# Creating an answer using POST
@student_answers_bp.route("/", methods=["POST"])
def create_answer():
    """This function creates a new question in the database submitted by a student"""
    data = request.get_json()

    if not data.get("question_id") or not data.get("student_id"):
        return {"error": "question_id and student_id are required"}, 400

    new_answer = StudentAnswer(
        question_id=data["question_id"],
        student_id=data["student_id"],
        selected_option_id=data.get("selected_option_id"),
        answer_text=data.get("answer_text"),
        quiz_id=data.get("quiz_id"),
        assignment_id=data.get("assignment_id"),
        attempt_number=data.get("attempt_number", 1)
    )

    db.session.add(new_answer)
    try:
        db.session.commit()
        return {"message": "Student answer submitted successfully", "id": new_answer.id}, 201
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while submitting the answer."}, 409


# Getting a specific answer using GET
@student_answers_bp.route("/<int:answer_id>", methods=["GET"])
def get_answer(answer_id):
    """This function gets a specific answer based on its ID"""
    answer = StudentAnswer.query.get(answer_id)
    if not answer:
        return {"error": "Answer not found"}, 404

    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "student_id": answer.student_id,
        "selected_option_id": answer.selected_option_id,
        "answer_text": answer.answer_text,
        "marks_awarded": answer.marks_awarded,
        "evaluated_by_ai": answer.evaluated_by_ai,
        "evaluated_by_teacher": answer.evaluated_by_teacher
    }, 200


# Updating the answer using PUT
@student_answers_bp.route("/<int:answer_id>", methods=["PUT"])
def update_answer(answer_id):
    """This function updates answer, mainly the teacher evaluation after the teacher checks it using its ID"""

    answer = StudentAnswer.query.get(answer_id)
    if not answer:
        return {"error": "Answer not found"}, 404

    data = request.get_json()

    answer.marks_awarded = data.get("marks_awarded", answer.marks_awarded)
    answer.evaluated_by_teacher = data.get("evaluated_by_teacher", answer.evaluated_by_teacher)
    answer.feedback = data.get("feedback", answer.feedback)

    try:
        db.session.commit()
        return {"message": "Answer updated successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while updating the answer."}, 409


# Deleting an answer using DELETE
@student_answers_bp.route("/<int:answer_id>", methods=["DELETE"])
def delete_answer(answer_id):
    """This function deletes an answer in case a student wants to delete it for reattempt later using its ID"""

    answer = StudentAnswer.query.get(answer_id)
    if not answer:
        return {"error": "Answer not found"}, 404

    db.session.delete(answer)
    try:
        db.session.commit()
        return {"message": "Answer deleted successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while deleting the answer."}, 409


# Getting all answers for a student using GET
@student_answers_bp.route("/student/<int:student_id>", methods=["GET"])
def get_answers_by_student(student_id):
    """This function returns a list of all students using the student_id"""

    answers = StudentAnswer.query.filter_by(student_id=student_id).all()
    if not answers:
        return {"message": f"No answers found for student {student_id}"}, 404

    return [
        {"id": ans.id, "question_id": ans.question_id, "marks_awarded": ans.marks_awarded}
        for ans in answers
    ], 200


# Getting all answers for a question using GET
@student_answers_bp.route("/question/<int:question_id>", methods=["GET"])
def get_answers_by_question(question_id):
    """This function returns a list of all answers submitted for a specific question using its ID"""
    answers = StudentAnswer.query.filter_by(question_id=question_id).all()
    if not answers:
        return {"message": f"No answers found for question {question_id}"}, 404

    return [
        {"id": ans.id, "student_id": ans.student_id, "answer_text": ans.answer_text}
        for ans in answers
    ], 200
