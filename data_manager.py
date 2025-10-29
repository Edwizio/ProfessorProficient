from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from data_models import db, Student, Course, Teacher


class DataManager():
    # Define Crud operations as methods
    def create_student(self, name, password):
        """This method creates a new student"""

        # Hashing the password
        password_hw = generate_password_hash(password)

        new_student = Student(name=name, password=password_hw)

        db.session.add(new_student)
        # Using db.session.rollback() with try-except to avoid crashing if database error occurs
        try:
            db.session.commit()
            return new_student
        except SQLAlchemyError:
            db.session.rollback()
            return None


    def get_students(self):
        """This function returns a list of the existing students"""
        students = Student.query.all()
        return students

    def delete_student(self, student_id):
        """This function deletes a student based on it's ID"""

        # Fetching the correct Student Object
        student = Student.query.get(student_id)

        # Deleting the student from the database
        db.session.delete(student)
        # Using db.session.rollback() with try-except to avoid crashing if database error occurs
        try:
            db.session.commit()
            return student
        except SQLAlchemyError:
            db.session.rollback()
            return None