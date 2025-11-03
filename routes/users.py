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
        return {"error": "Email already exists"}, 409

    return {"message": f"{new_user.role.value.title()} '{new_user.name}' created successfully"}, 201
