import enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class UserRole(enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"

# Integrating the Student, Teacher and Admin model as a single class
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    # Adding the relationship to User class, all tables will be created by the User instance
    programs_created = db.relationship("Program", back_populates="created_by_user") #back populates ensures the two tables are in sync
    courses_created = db.relationship("Course", back_populates="created_by_user")
    quizzes_created = db.relationship("Quiz", back_populates="created_by_user")
    assignments_created = db.relationship("Assignment", back_populates="created_by_user")

    # Many-to-many relationships defined, the below tables will serve as the joining table
    # Secondary tells SQLAlchemy that there’s a linking table that connects these two tables in a many-to-many relationship
    teaching_courses = db.relationship("Course", secondary="teacher_course", back_populates="teachers")
    enrolled_courses = db.relationship("Course", secondary="student_course", back_populates="students")

    def __repr__(self):
        return f"User(id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the user {self.name}"

# Defining the Course model as a class
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    grade = db.Column(db.Float, nullable=False)
    quiz = db.Column(db.Float, nullable=False)
    assignment = db.Column(db.Float, nullable=False)
    paper = db.Column(db.Float, nullable=False)

    # Adding the relationship to Teacher class
    teacher = db.relationship("Teacher", backref="course", lazy=True)

    # Link Class to Student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def __repr__(self):
        return f"Course (id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the Course {self.name}"


# Defining the Teacher model as a class
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    project = db.Column(db.String(20), nullable=False)

    # Link Class to Student
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f"Teacher(id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the teacher {self.name}"


# Defining the Semester model as a class
class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    # Link to Program class
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)

    # Relationships
    program = db.relationship('Program', backref="Semester", lazy=True)
    courses = db.relationship('Course', back_populates='semester', cascade="all, delete-orphan")

    # Link Class to Student
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f"Teacher(id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the teacher {self.name}"