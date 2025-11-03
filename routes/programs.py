from flask import request
from ProfessorProficient.data_models import Program
from ProfessorProficient.app import app


# Getting a list of all programs
@app.route("/", methods=["GET"])
def get_programs():
    """This function returns a list of dictionaries of all programs showing their ID, Name and small description"""
    programs = Program.query.all()

    if not programs:
        return  {"error": "Sorry no programs have been added to the database"}
    else:
        return [{"id": prog.id, "Name": prog.name ,"Description": prog.description}
            for prog in programs], 200