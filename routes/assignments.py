from flask import request
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.app import app
from ProfessorProficient.data_models import db, Assignment, Course, User


# Getting a list of all assignments using GET
@app.route("/", methods=["GET"])
def get_assignemnts():
    """This function gets a list of all the assignments in the database"""
    assignments = Assignment.query.all()
    if not assignments:
        return {"message": "No assignments found"}, 404

    return [
        {
            "id": a.id,
            "title": a.title,
            "total_marks": a.total_marks,
            "course_id": a.course_id,
            "created_by": a.created_by,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in assignments
    ], 200


# Creating a new assignment using POST
@app.route("/", methods=["POST"])
def create_assignment():
    """This function creates a new assignment in the database"""
    data = request.get_json()

    if not data.get("title") or not data.get("course_id") or not data.get("created_by"):
        return {"error": "title, course_id, and created_by are required fields"}, 400

    # Validating that Course and User exist that are associated with the quiz
    if not Course.query.get(data["course_id"]):
        return {"error": "Invalid course_id"}, 404
    if not User.query.get(data["created_by"]):
        return {"error": "User (creator) does not exist"}, 404  # Resource not found

    # Creating a new Assignment object
    new_assignment = Assignment(
        title=data["title"],
        total_marks=data.get("total_marks", 100),
        due_date=data.get("due_date"),
        course_id=data["course_id"],
        created_by=data["created_by"]
    )

    # Adding the Assignment object to the database
    db.session.add(new_assignment)
    try:
        db.session.commit()
        return { "message": f"Assignment {new_assignment.title} created successfully", "id": new_assignment.id }, 201
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409
