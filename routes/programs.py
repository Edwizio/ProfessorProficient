from flask import request, db
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.data_models import Program
from ProfessorProficient.app import app


# Getting a list of all programs using GET
@app.route("/", methods=["GET"])
def get_programs():
    """This function returns a list of dictionaries of all programs showing their ID, Name and small description"""
    programs = Program.query.all()

    if not programs:
        return  {"error": "Sorry no programs have been added to the database"}
    else:
        return [{"id": prog.id, "Name": prog.name ,"Description": prog.description}
            for prog in programs], 200



# Getting a program by its ID using GET
@app.route("/<int:program_id>")
def get_program(program_id):
    """This function gets a program by its ID"""
    program = Program.query.get_or_404(program_id) # Using got_or_404() for automatic error handling

    return {
        "id": program.id,
        "name": program.name,
        "description": program.description
    }, 200


# Creating a new program using POST
@app.route("/", methods=["POST"])
def create_program():
    data = request.get_json()

    # Checking for the required parameters
    if not data.get("name") or not data.get("created_by"):
        return {"error": "Name and created_by are required fields"}, 400

    # Creating new Program object
    program = Program(
        name=data["name"],
        description=data.get("description"),
        created_by=data["created_by"]
    )

    # Adding to the database
    db.session.add(program)
    # Error handling while adding the new user to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": "Program created successfully", "id": program.id}, 201
    except SQLAlchemyError:
        return {"error": "The request could not be completed as it conflicts with the current state of the resource."}, 409

