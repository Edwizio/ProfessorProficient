from flask import request
from ProfessorProficient.app import app
from ProfessorProficient.data_models import db, Assignment


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
