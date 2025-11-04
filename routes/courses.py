from flask import db
from ProfessorProficient.data_models import Course
from ProfessorProficient.app import app

# Getting a list of courses using GET
@app.route("/", methods=["GET"])
def get_courses():
    """This function returns a list of all the available courses"""
    courses = Course.query.all()

    # Error handling in case of no courses in the database
    if not courses:
        return {"message": "No courses found"}, 200

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