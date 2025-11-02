from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from data_models import db, User


class DataManager():
    # Define Crud operations as methods for User Class
    def create_user(self, name, password):
        """This method creates a new user"""

        # Hashing the password
        password_hw = generate_password_hash(password)

        new_user = User(name=name, password=password_hw)

        db.session.add(new_user)
        # Using db.session.rollback() with try-except to avoid crashing if database error occurs
        try:
            db.session.commit()
            return new_user
        except SQLAlchemyError:
            db.session.rollback()
            return None


    def get_users(self):
        """This function returns a list of the existing users"""
        if self.role == "admin":
            users = User.query.all()
            return [user.role for user in users]
        else:
            return f"The role {self.role} is not allowed to get a user list"


    def delete_user(self, user_id):
        """This function deletes a user based on it's ID"""

        # Fetching the correct User Object
        user = User.query.get(user_id)

        # Deleting the user from the database
        db.session.delete(user)
        # Using db.session.rollback() with try-except to avoid crashing if database error occurs
        try:
            db.session.commit()
            return user
        except SQLAlchemyError:
            db.session.rollback()
            return None

    def update_user(self, user_id):
        """This function updates a given user's attribute that are provided"""