from flask import request, Blueprint
from sqlalchemy.exc import SQLAlchemyError

from data_models import db, Program, User

# Defining blueprint to be used in the app later
programs_bp = Blueprint("programs",__name__)

# Getting a list of all programs using GET
@programs_bp.route("/", methods=["GET"])
def get_programs():
    """This function returns a list of dictionaries of all programs showing their ID, Name and small description"""
    programs = Program.query.all()

    if not programs:
        return  {"error": "Sorry no programs have been added to the database"}
    else:
        return [
            {
                "id": prog.id, 
                "name": prog.name, 
                "description": prog.description,
                "teachers": [{"id": t.id, "name": t.name, "email": t.email} for t in prog.teachers],
                "students": [{"id": s.id, "name": s.name, "email": s.email} for s in prog.students]
            }
            for prog in programs
        ], 200

# Getting a program by its ID using GET
@programs_bp.route("/<int:program_id>")
def get_program(program_id):
    """This function gets a program by its ID"""
    program = Program.query.get_or_404(program_id) # Using got_or_404() for automatic error handling

    return {
        "id": program.id,
        "name": program.name,
        "description": program.description,
        "teachers": [{"id": t.id, "name": t.name, "email": t.email} for t in program.teachers],
        "students": [{"id": s.id, "name": s.name, "email": s.email} for s in program.students]
    }, 200

# Assigning a teacher to a program
@programs_bp.route("/<int:program_id>/assign-teacher/<int:teacher_id>", methods=["POST"])
def assign_teacher(program_id, teacher_id):
    program = Program.query.get(program_id)
    teacher = User.query.get(teacher_id)
    if not program or not teacher:
        return {"error": "Program or Teacher not found"}, 404
    if teacher in program.teachers:
        return {"message": "Teacher already assigned"}, 409
    program.teachers.append(teacher)
    try:
        db.session.commit()
        return {"message": f"Teacher '{teacher.name}' assigned to '{program.name}'"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Conflict occurred"}, 409

# Removing a teacher from a program
@programs_bp.route("/<int:program_id>/remove-teacher/<int:teacher_id>", methods=["DELETE"])
def remove_teacher(program_id, teacher_id):
    program = Program.query.get(program_id)
    teacher = User.query.get(teacher_id)
    if not program or not teacher:
        return {"error": "Program or Teacher not found"}, 404
    if teacher not in program.teachers:
        return {"message": "Teacher not assigned"}, 400
    program.teachers.remove(teacher)
    try:
        db.session.commit()
        return {"message": "Teacher removed"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Conflict occurred"}, 409

# Enrolling a student in a program
@programs_bp.route("/<int:program_id>/enroll-student/<int:student_id>", methods=["POST"])
def enroll_student(program_id, student_id):
    program = Program.query.get(program_id)
    student = User.query.get(student_id)
    if not program or not student:
        return {"error": "Program or Student not found"}, 404
    if student in program.students:
        return {"message": "Student already enrolled"}, 409
    program.students.append(student)
    try:
        db.session.commit()
        return {"message": f"Student '{student.name}' enrolled in '{program.name}'"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Conflict occurred"}, 409

# Removing a student from a program
@programs_bp.route("/<int:program_id>/remove-student/<int:student_id>", methods=["DELETE"])
def remove_student(program_id, student_id):
    program = Program.query.get(program_id)
    student = User.query.get(student_id)
    if not program or not student:
        return {"error": "Program or Student not found"}, 404
    if student not in program.students:
        return {"message": "Student not enrolled"}, 400
    program.students.remove(student)
    try:
        db.session.commit()
        return {"message": "Student removed"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Conflict occurred"}, 409


# Creating a new program using POST
@programs_bp.route("/", methods=["POST"])
def create_program():
    data = request.get_json()

    # Checking for the required parameters
    if not data.get("name") or not data.get("created_by"):
        return {"error": "Name and created_by are required fields"}, 400

    if not User.query.get(data["created_by"]):
        return {"error": "User (creator) does not exist"}, 404  # Resource not found

    # Creating new Program object
    program = Program(
        name=data["name"],
        description=data.get("description"),
        created_by=data["created_by"]
    )

    # Adding to the database
    db.session.add(program)
    # Error handling while adding the new program to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": "Program created successfully", "id": program.id}, 201
    except SQLAlchemyError:
        return {"error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Updating a program's different attributes using PUT
@programs_bp.route("/<int:program_id>", methods=["PUT"])
def update_program(program_id):
    """This function updates a program using its ID."""
    program = Program.query.get_or_404(program_id) # Using got_or_404() for automatic error handling
    data = request.get_json()

    # Assigning the new values from the JSON to the program object other if the param exists, otherwise keeping the original value
    program.name = data.get("name", program.name)
    program.description = data.get("description", program.description)

    # Error handling while updating to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": f"User {program.name} updated successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Deleting a specific program using DELETE
@programs_bp.route("/<int:program_id>", methods=["DELETE"])
def delete_program(program_id):
    """This function deletes a specific program based on its ID."""

    program = Program.query.get_or_404(program_id) # Using got_or_404() for automatic error handling

    # Preventing deletion if courses exist
    if program.courses:
        return {"error": "Cannot delete program with courses assigned"}, 409

    # Deleting the program from the database
    db.session.delete(program)
    # Error handling while updating to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": f"The program {program.id} deleted successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {
            "error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Searching for a specific program by name using GET
@programs_bp.route("/search", methods=["GET"])
def search_program():
    """This function searches for a program by its name"""

    # Assigning default value of empty string("") to avoid crashing in case keyword isn't provided
    keyword = request.args.get("keyword", "")

    # Searching through the database using the case-insensitive .ilike()
    programs = Program.query.filter(Program.name.ilike(f"%{keyword}%")).all()
    return [
        {"id": p.id, "name": p.name, "description": p.description}
        for p in programs
    ], 200


# Course count in each program fetched using GET
@programs_bp.route("/program-course-counts", methods=["GET"])
def programs_with_course_counts():
    programs = Program.query.all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "course_count": len(p.courses)
        }
        for p in programs
    ], 200