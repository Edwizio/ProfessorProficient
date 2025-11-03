from flask import request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from ProfessorProficient.data_models import User, UserRole, db
from ProfessorProficient.app import app

# Creating a route for getting a list for the users from the database
@app.route("/", methods=["GET"])
def get_users():
    """This function fetches all users with optional filters by role or name."""

    role = request.args.get("role")
    name = request.args.get("name")

    query = User.query
    if role:
        try:
            query = query.filter(User.role == User(role))
        except ValueError:
            return {"error": "Invalid role filter"}, 400
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    users = query.all()
    return [{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "created_at": user.created_at.isoformat() if user.created_at else None # returning a standardized ISO Format of date and time
    } for user in users], 200


# Adding a new User to the database
@app.route("/", methods=["POST"])
def create_user():
    """This function creates a new user (admin, teacher, or student)."""
    data = request.get_json()

    # Checking if a required parameter is missing in the data
    if not all(param in data for param in ("name", "email", "password", "role")):
        return {"error": "Missing required fields"}, 400

    # Checking for the validation of the role
    try:
        role_enum = UserRole[data["role"]]
    except KeyError:
        return {"error": f"Invalid role '{data['role']}'. Must be one of {[r.value for r in UserRole]}"}, 400

    # Creating the new User Object to be added in the database
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role=role_enum
    )

    # Error handling while adding the new user to the database to avoid crashing in case of any database error
    try:
        db.session.add(new_user)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "The request could not be completed as it conflicts with the current state of the resource."}, 409

    return {"message": f"{new_user.role.value.title()} '{new_user.name}' created successfully"}, 201

# Updating a user's different attributing using PUT method instead of POST to avoid creating a new route unnecessarily
@app.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """This function updates to provided user details."""
    user = User.query.get_or_404(user_id) # Using got_or_404() for automatic error handling
    data = request.get_json()

    # Assigning the new values from the JSON to the user object other if the param exists, otherwise keeping the original value
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.password = data.get("password", user.password)

    # Checking for validity if role is to be updated as well
    if "role" in data:
        try:
            user.role = UserRole[data["role"]]
        except KeyError:
            return {"error": "Invalid role"}, 400

    # Error handling while updating to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": f"User {user.name} updated successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "The request could not be completed as it conflicts with the current state of the resource."}, 409