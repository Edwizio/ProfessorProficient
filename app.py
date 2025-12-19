from flask import Flask
import os
from data_models import db

# Importing the Blueprints
from routes.assignments import assignments_bp
from routes.courses import courses_bp
from routes.users import users_bp
from routes.quizzes import quizzes_bp
from routes.programs import programs_bp
from routes.questions import questions_bp
from routes.question_options import question_options_bp
from routes.student_answers import student_answers_bp

#Creating the flask app object
def create_app():
    """This function creates a Flask app which registers the Blueprints from the routes as well as configuring the
    database paths"""
    app = Flask(__name__)

    # Finds the absolute path to our project folder
    basedir = os.path.abspath(os.path.dirname(__file__))
    # The database connection set up which tells that we are using SQLite and base folder has been joined with the subfolder lms.db
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/lms.db')}"
    # Disabling SQLAlchemy’s event system that tracks object changes.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # Link the database and the app. This is the reason we need to import db from models

    # Registering the Blueprints
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(programs_bp, url_prefix="/programs")
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(quizzes_bp, url_prefix="/quizzes")
    app.register_blueprint(assignments_bp, url_prefix="/assignments")
    app.register_blueprint(questions_bp, url_prefix="/questions")
    app.register_blueprint(question_options_bp, url_prefix="/question_options")
    app.register_blueprint(student_answers_bp, url_prefix="/student_answers")

    return app


if __name__ == "__main__":
    app = create_app()
    """with app.app_context():
            db.create_all()""" # Creating all the database tables defined by our models.
    app.run(debug=True)