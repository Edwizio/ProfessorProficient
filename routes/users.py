from flask import request
from ProfessorProficient.data_models import User, UserRole

from ProfessorProficient.app import app

# Creating a route for getting a list for the users
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
        "created_at": user.created_at.isoformat() if user.created_at else None
    } for user in users], 200