from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError

from ProfessorProficient.data_models import QuestionOption, db

# Defining blueprint to be used in the app later
question_options_bp = Blueprint("question_options", __name__)

# Getting all options using GET
@question_options_bp.route("/", methods=["GET"])
def get_all_options():
    """This function returns a list of all the options available for all the questions"""
    options = QuestionOption.query.all()
    if not options:
        return {"message": "No question options found"}, 404

    return [
        {
            "id": opt.id,
            "question_id": opt.question_id,
            "option_text": opt.option_text,
            "is_correct": opt.is_correct,
            "order_index": opt.order_index
        }
        for opt in options
    ], 200


# Creating a new option in the Database
@question_options_bp.route("/", methods=["POST"])
def create_option():
    """This function creates options for a particular question in the Database"""
    data = request.get_json()

    if not data.get("question_id") or not data.get("option_text"):
        return {"error": "question_id and option_text are required"}, 400

    new_option = QuestionOption(
        question_id=data["question_id"],
        option_text=data["option_text"],
        is_correct=data.get("is_correct", False),
        order_index=data.get("order_index", 0)
    )

    db.session.add(new_option)
    try:
        db.session.commit()
        return { "message": "Option created successfully", "id": new_option.id }, 201
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while creating the options."}, 409


# Getting an option by ID using GET
@question_options_bp.route("/<int:option_id>", methods=["GET"])
def get_option(option_id):
    """This function returns a specific option using its ID"""
    opt = QuestionOption.query.get(option_id)
    if not opt:
        return {"error": "Option not found"}, 404

    return {
        "id": opt.id,
        "question_id": opt.question_id,
        "option_text": opt.option_text,
        "is_correct": opt.is_correct,
        "order_index": opt.order_index
    }, 200


# Updating an option using PUT
@question_options_bp.route("/<int:option_id>", methods=["PUT"])
def update_option(option_id):
    """This function updates the provided parameters of an option using its ID"""
    opt = QuestionOption.query.get(option_id)
    if not opt:
        return {"error": "Option not found"}, 404

    data = request.get_json()

    opt.option_text = data.get("option_text", opt.option_text)
    opt.is_correct = data.get("is_correct", opt.is_correct)
    opt.order_index = data.get("order_index", opt.order_index)

    try:
        db.session.commit()
        return {"message": f"Option {opt.id} updated successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while updating the option."}, 409


# Deleting an option using DELETE
@question_options_bp.route("/<int:option_id>", methods=["DELETE"])
def delete_option(option_id):
    """This function deletes an option using its ID"""

    opt = QuestionOption.query.get(option_id)
    if not opt:
        return {"error": "Option not found"}, 404

    db.session.delete(opt)
    try:
        db.session.commit()
        return {"message": f"Option {opt.id} deleted successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Database conflict occurred while deleting the option."}, 409


# Getting all options for a question using GET
@question_options_bp.route("/question/<int:question_id>", methods=["GET"])
def get_options_by_question(question_id):
    """This function returns all the available options for a question using the question_id as a list"""

    options = QuestionOption.query.filter_by(question_id=question_id).all()
    if not options:
        return {"message": f"No options found for question ID {question_id}"}, 404

    return [
        {
            "id": opt.id,
            "option_text": opt.option_text,
            "is_correct": opt.is_correct,
            "order_index": opt.order_index
        }
        for opt in options
    ], 200
