from flask import Flask, render_template, Blueprint
import os
from datetime import datetime, timezone
from data_models import db, Course, User, Program, Assignment, Quiz, UserRole, StudentAnswer

# Importing the Blueprints
from routes.assignments import assignments_bp
from routes.courses import courses_bp
from routes.users import users_bp
from routes.quizzes import quizzes_bp
from routes.programs import programs_bp
from routes.questions import questions_bp
from routes.question_options import question_options_bp
from routes.student_answers import student_answers_bp

# UI Blueprint
ui_bp = Blueprint("ui", __name__)

def time_ago(dt):
    if dt is None:
        return ""
    # Ensure dt is offset-aware or handle it accordingly
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    if seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    if seconds < 172800:
        return "Yesterday"
    days = int(seconds // 86400)
    return f"{days} day{'s' if days != 1 else ''} ago"

@ui_bp.route("/")
def index():
    active_courses = Course.query.count()
    total_students = User.query.filter_by(role=UserRole.student).count()
    quizzes_generated = Quiz.query.count()

    # Fetch recent activities
    activities = []
    
    # Recent Quizzes
    recent_quizzes = Quiz.query.order_by(Quiz.created_at.desc()).limit(5).all()
    for q in recent_quizzes:
        activities.append({
            'title': f"New Quiz Generated: {q.title}",
            'time': time_ago(q.created_at),
            'timestamp': q.created_at,
            'type': 'AI',
            'badge_class': 'bg-info text-dark'
        })
        
    # Recent Courses
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
    for c in recent_courses:
        activities.append({
            'title': f"Course Created: {c.name}",
            'time': time_ago(c.created_at),
            'timestamp': c.created_at,
            'type': 'System',
            'badge_class': 'bg-secondary'
        })
        
    # Recent Users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    for u in recent_users:
        activities.append({
            'title': f"New {u.role.value.capitalize()}: {u.name}",
            'time': time_ago(u.created_at),
            'timestamp': u.created_at,
            'type': 'User',
            'badge_class': 'bg-success'
        })

    # Recent Submissions
    recent_submissions = StudentAnswer.query.order_by(StudentAnswer.submitted_at.desc()).limit(5).all()
    for s in recent_submissions:
        # Avoid potential N+1 or None issues
        quiz_title = "Assignment"
        if s.question and s.question.quiz:
            quiz_title = s.question.quiz.title
        
        activities.append({
            'title': f"New Submission for {quiz_title}",
            'time': time_ago(s.submitted_at),
            'timestamp': s.submitted_at,
            'type': 'User',
            'badge_class': 'bg-success'
        })

    # Sort activities by timestamp descending
    def get_timestamp(x):
        ts = x['timestamp']
        if ts is None:
            return datetime.min.replace(tzinfo=timezone.utc)
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts

    activities.sort(key=get_timestamp, reverse=True)
    recent_activities = activities[:5]

    return render_template("index.html", 
                         active_courses=active_courses, 
                         total_students=total_students, 
                         quizzes_generated=quizzes_generated,
                         recent_activities=recent_activities)

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
    app.config['SECRET_KEY'] = 'super-secret-key-for-dev'

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