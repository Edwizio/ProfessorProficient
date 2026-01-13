from app import create_app
from ProfessorProficient.data_models import db, User, Course

app = create_app()

with app.app_context():
    print("--- Users ---")
    users = User.query.all()
    if not users:
        print("No users found.")
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Role: {u.role}")

    print("\n--- Courses ---")
    courses = Course.query.all()
    if not courses:
        print("No courses found.")
    for c in courses:
        print(f"ID: {c.id}, Name: {c.name}")
