from flask import request
from ProfessorProficient.data_models import Program
from ProfessorProficient.app import app

@app.route("/", methods=["GET"])
def get_programs():
    """This function returns a list of dictionaries of all programs showing their ID, Name and small description"""
    programs = Program.query.all()

    return [{"id": prog.id, "Name": prog.name ,"Description": prog.description}
            for prog in programs], 200