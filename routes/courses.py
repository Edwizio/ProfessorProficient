from flask import db, request
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.data_models import Course, Program, User
from ProfessorProficient.app import app

# Getting a list of courses using GET
@app.route("/", methods=["GET"])
def get_courses():
    """This function returns a list of all the available courses"""
    courses = Course.query.all()

    # Error handling in case of no courses in the database
    if not courses:
        return {"message": "No courses found"}, 200 # Used for GET(Successful fetch)

    return [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "credit_hours": c.credit_hours,
            "program_id": c.program_id,
            "created_by": c.created_by,
        }
        for c in courses
    ], 200


# Creating a new course using POST
@app.route("/", method=["POST"])
def create_course():
    """This function creates a new courses in the database"""

    data = request.get_json()
    # Checking for input validation
    if not data.get("name") or not data.get("code") or not data.get("program_id") or not data.get("created_by"):
        return {"error": "name, code, program_id, and created_by are required"}, 400 # Client-side input error

    # Making sure that the Program and User exist before adding and connecting the foreign keys
    if not Program.query.get(data["program_id"]):
        return {"error": "Program does not exist"}, 404
    if not User.query.get(data["created_by"]):
        return {"error": "User (creator) does not exist"}, 404 # Resource not found

    # Creating a new Course object
    course = Course(
        name=data["name"],
        code=data["code"],
        credit_hours=data.get("credit_hours", 3), # Setting the default value to 3 hours
        program_id=data["program_id"],
        created_by=data["created_by"],
    )

    # Adding to the database
    db.session.add(course)
    # Error handling while adding the new course to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": "Course created successfully", "id": course.id}, 201 # used for POST(successful created)
    except SQLAlchemyError:
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Getting a course by its ID using GET
@app.route("/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """This function returns a specific course based on its ID"""
    course = Course.query.get_or_404(course_id) # Using got_or_404() for automatic error handling

    return {
        "id": course.id,
        "name": course.name,
        "code": course.code,
        "credit_hours": course.credit_hours,
        "program_id": course.program_id,
        "created_by": course.created_by,
    }, 200 # Successful fetch


# Updating the course attributes using PUT
@app.route("/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """This function updates a course using its ID."""
    course = Course.query.get_or_404(course_id) # Using got_or_404() for automatic error handling

    data = request.get_json()

    # Assigning the new values from the JSON to the program object other if the param exists, otherwise keeping the original value
    course.name = data.get("name", course.name)
    course.code = data.get("code", course.code)
    course.credit_hours = data.get("credit_hours", course.credit_hours)
    course.program_id = data.get("program_id", course.program_id)

    # Error handling while adding the new course to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": f"Course '{course.name}' updated successfully"}, 200
    except SQLAlchemyError:
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Deleting a course using DELETE
@app.route("/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """This function deletes a specific course based on its ID."""
    course = Course.query.get(course_id)
    if not course:
        return {"error": "Course not found"}, 404

    # Deleting a course from the database
    db.session.delete(course)
    # Error handling while adding the new course to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": f"Course '{course.name}' deleted successfully"}, 200
    except SQLAlchemyError:
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Assigning a teacher to a course using POST
@app.route("/<int:course_id>/assign-teacher/<int:teacher_id>", methods=["POST"])
def assign_teacher(course_id, teacher_id):
    """This function assigns a teacher to a course"""
    course = Course.query.get(course_id)
    teacher = User.query.get(teacher_id)

    if not course or not teacher:
        return {"error": "Course or Teacher not found"}, 404

    if teacher in course.teachers:
        return {"message": "Teacher already assigned"}, 409

    # First accessing the instrumented list course.teacher and then appending the new teacher to it
    course.teachers.append(teacher)
    try:
        db.session.commit()
        return {"message": f"Teacher '{teacher.name}' assigned to '{course.name}'"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Removing a teacher from a course using DELETE
@app.route("/<int:course_id>/remove-teacher/<int:teacher_id>", methods=["DELETE"])
def remove_teacher(course_id, teacher_id):
    """This function deletes a teacher from a course"""
    course = Course.query.get(course_id)
    teacher = User.query.get(teacher_id)

    if not course or not teacher:
        return {"error": "Course or Teacher not found"}, 404

    # Checking if the teacher is not assigned
    if teacher not in course.teachers:
        return {"message": "Teacher not assigned to this course"}, 400

    # Removing from the database using instrumented list course.teachers and remove method
    course.teachers.remove(teacher)
    try:
        db.session.commit()
        return {"message": f"Teacher '{teacher.name}' removed from '{course.name}'"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409
