from flask import request, Blueprint, session, jsonify
from sqlalchemy.exc import SQLAlchemyError
from ProfessorProficient.data_models import db, User, UserRole
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Defining blueprint to be used in the app later
users_bp = Blueprint("users",__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        user = db.session.get(User, user_id)
        if not user or user.role != UserRole.admin:
            return jsonify({"error": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["user_role"] = user.role.value
        return jsonify({"message": f"Logged in as {user.name}", "role": user.role.value}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@users_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

# Creating a route for getting a list for the users from the database
@users_bp.route("/", methods=["GET"])
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
@users_bp.route("/", methods=["POST"])
@admin_required
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

    # Hashing the password
    password_hw = generate_password_hash(data["password"])
    # Creating the new User Object to be added in the database
    new_user = User(
        name=data["name"],
        email=data["email"],
        password=password_hw,
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

# Updating a user's different attributes using PUT method instead of POST to avoid creating a new route unnecessarily
@users_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    """This function updates to provided user details."""
    user = User.query.get_or_404(user_id) # Using got_or_404() for automatic error handling
    data = request.get_json()

    # Assigning the new values from the JSON to the user object other if the param exists, otherwise keeping the original value
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    
    # Hashing the password if provided
    if "password" in data and data["password"]:
        user.password = generate_password_hash(data["password"])

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


# Deleting an existing user from the database
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """This function deletes a user by ID."""
    user = User.query.get_or_404(user_id) # Using got_or_404() for automatic error handling

    # Deleting the user from the database
    db.session.delete(user)

    # Error handling while updating to the database to avoid crashing in case of any database error
    try:
        db.session.commit()
        return {"message": f"User {user.name} deleted successfully"}, 200
    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "The request could not be completed as it conflicts with the current state of the resource."}, 409


# Searching the database based on the provided name or email
@users_bp.route("/search", methods=["GET"])
def search_users():
    """This function searches users by name or email."""
    keyword = request.args.get("q")
    if not keyword:
        return {"error": "Missing search query 'q'"}, 400

    # Searching through the database using the case-insensitive .ilike() and | operator
    users = User.query.filter(
        (User.name.ilike(f"%{keyword}%")) | (User.email.ilike(f"%{keyword}%"))
    ).all()

    # Considering the case if the no users match the input query
    if not users:
        return {"message": "No users found"}, 404

    # Returning a list of users who match the search criterion
    return [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role.value
    } for u in users], 200


# Finding a user based on it's ID
@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    """This function fetches a specific user by it's ID."""
    user = User.query.get_or_404(user_id) # Using got_or_404() for automatic error handling

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }, 200


# Counting the total number of users in the database by role
@users_bp.route("/count", methods=["GET"])
def count_users():
    """This function returns the total count of users by role using the func utility that lets us call SQL functions in
    Python like sum(), count, max() etc """

    # A list of tuples which first extracts the role of user, then counts the users after grouping by roles
    result = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
    # role.value extracts the role enum and the result is a dictionary which displays the count of each role as key value pairs
    counts = {role.value: count for role, count in result}
    return counts, 200