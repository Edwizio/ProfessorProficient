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


# Getting a specific assignment by ID uding GET
@app.route("/<int:assignment_id>", methods=["GET"])
def get_assignment(assignment_id):
    """This function returns a specific assignment by its ID"""
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return {"error": "Assignment not found"}, 404

    return {
        "id": assignment.id,
        "title": assignment.title,
        "total_marks": assignment.total_marks,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
        "course_id": assignment.course_id,
        "created_by": assignment.created_by
    }, 200


# Updating an assignment using its ID with PUT
@app.route("/<int:assignment_id>", methods=["PUT"])
def update_assignment(assignment_id):
    """This function updates the attributes of an assignment using its ID"""
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return {"error": "Assignment not found"}, 404

    data = request.get_json()

    # Updating the attributes only if provided
    assignment.title = data.get("title", assignment.title)
    assignment.total_marks = data.get("total_marks", assignment.total_marks)
    assignment.due_date = data.get("due_date", assignment.due_date)

    try:
        db.session.commit()
        return {"message": f"Assignment '{assignment.title}' updated successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Deleting an assignment using its ID with DELETE
@app.route("/<int:assignment_id>", methods=["DELETE"])
def delete_assignment(assignment_id):
    """This function deletes an assignment using its ID."""
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return {"error": "Assignment not found"}, 404

    # Deleting the assignment
    db.session.delete(assignment)
    try:
        db.session.commit()
        return {"message": f"Assignment '{assignment.title}' deleted successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409

