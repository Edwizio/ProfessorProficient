from flask import request, Blueprint
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.data_models import db, Assignment, Course, User
from sqlalchemy import func

# Defining blueprint to be used in the app later
assignments_bp = Blueprint("assignments",__name__)

# Getting a list of all assignments using GET
@assignments_bp.route("/", methods=["GET"])
def get_assignments():
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
@assignments_bp.route("/", methods=["POST"])
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


# Getting a specific assignment by ID using GET
@assignments_bp.route("/<int:assignment_id>", methods=["GET"])
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
@assignments_bp.route("/<int:assignment_id>", methods=["PUT"])
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
@assignments_bp.route("/<int:assignment_id>", methods=["DELETE"])
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


# Getting all assignments for a specific course using GET
@assignments_bp.route("/course/<int:course_id>", methods=["GET"])
def get_assignments_by_course(course_id):
    """This function returns a list of all the assignments of a specific course using its ID."""

    # Filtering through the assignment database using the condition where course.id is course_id
    assignments = Assignment.query.filter(Assignment.course_id == course_id).all()
    if not assignments:
        return {"message": f"No assignments found for course ID {course_id}"}, 404

    return [
        {"id": a.id, "title": a.title, "total_marks": a.total_marks}
        for a in assignments
    ], 200


# Searching assignments by keyword using GET
@assignments_bp.route("/search", methods=["GET"])
def search_assignments():
    """This function searches the database for a particular assignment using its title."""

    # Assigning default value of empty string("") to avoid crashing in case keyword isn't provided
    keyword = request.args.get("keyword", "")
    if not keyword:
        return {"error": "Please provide a search keyword"}, 400

    # Searching through the database using the case-insensitive .ilike()
    assignments = Assignment.query.filter(Assignment.title.ilike(f"%{keyword}%")).all()
    if not assignments:
        return {"message": f"No assignments found matching '{keyword}'"}, 404

    return [
        {"id": a.id, "title": a.title, "course_id": a.course_id}
        for a in assignments
    ], 200


# Getting all assignments created by a specific teacher
@assignments_bp.route("/created-by/<int:user_id>", methods=["GET"])
def get_assignments_by_creator(user_id):
    """This function gets a list of all the assignments created by a specific teacher"""
    assignments = Assignment.query.filter(Assignment.created_by == user_id).all()
    if not assignments:
        return {"message": f"No assignments created by user ID {user_id}"}, 404

    return [
        {"id": a.id, "title": a.title, "course_id": a.course_id}
        for a in assignments
    ], 200


# Getting count of assignments per course using GET
@assignments_bp.route("/stats/per-course", methods=["GET"])
def assignments_per_course():
    """This function returns count of assignments per course"""

    # A list of tuples which first extracts the Course ID, then counts the assignments after grouping by course IDs
    results = db.session.query(
        Assignment.course_id,
        func.count(Assignment.id)
    ).group_by(Assignment.course_id).all()

    return {
        "assignments_per_course": [
            {"course_id": c_id, "assignment_count": count}
            for c_id, count in results
        ]
    }, 200