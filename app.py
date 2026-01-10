from flask import Flask, render_template, Blueprint
import os
from ProfessorProficient.data_models import db, Course, User, Program, Assignment, Quiz

# Importing the Blueprints
from ProfessorProficient.routes.assignments import assignments_bp
from ProfessorProficient.routes.courses import courses_bp
from ProfessorProficient.routes.users import users_bp
from ProfessorProficient.routes.quizzes import quizzes_bp
from ProfessorProficient.routes.programs import programs_bp
from ProfessorProficient.routes.questions import questions_bp
from ProfessorProficient.routes.question_options import question_options_bp
from ProfessorProficient.routes.student_answers import student_answers_bp

# UI Blueprint
ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/")
def index():
    return render_template("index.html")

@ui_bp.route("/ui/courses")
def courses_page():
    courses = Course.query.all()
    return render_template("courses.html", courses=courses)

@ui_bp.route("/ui/users")
def users_page():
    users = User.query.all()
    return render_template("users.html", users=users)

@ui_bp.route("/ui/programs")
def programs_page():
    programs = Program.query.all()
    return render_template("programs.html", programs=programs)

@ui_bp.route("/ui/assignments")
def assignments_page():
    assignments = Assignment.query.all()
    return render_template("assignments.html", assignments=assignments)

@ui_bp.route("/ui/quizzes")
def quizzes_page():
    quizzes = Quiz.query.all()
    return render_template("quizzes.html", quizzes=quizzes)

@ui_bp.route("/ui/generate-quiz")
def generate_quiz_page():
    return render_template("generate_quiz.html")

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
    app.register_blueprint(ui_bp)
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