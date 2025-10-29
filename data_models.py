import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


class UserRole(enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"

# Integrating the Student, Teacher and Admin model as a single class User
class User(db.Model):
    """This class defines a general user who can either be a teacher, student or admin"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))


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


# Creating the model class Program which stores information about the programs offered for students to enroll
class Program(db.Model):
    """ This class defines a program in which students get enrolled"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # # Adding the relationship to Program class, all tables will be created by the User instance
    created_by_user = db.relationship("User", back_populates="programs_created")
    # As one program can have many courses, this is a one-to-many relationship, and it ensures when a parent is changed or
    # deleted, the child also gets changed or deleted
    courses = db.relationship("Course", back_populates="program", cascade="all, delete-orphan")


# Defining the Course model as a class
class Course(db.Model):
    """This class defines a course which can be taken up by a student and taught and maintained by a teacher, also they
    can have courses and assignments"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    credit_hours = db.Column(db.Integer)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # Defining relationships to the program and user classes
    program = db.relationship("Program", back_populates="courses")
    created_by_user = db.relationship("User", back_populates="courses_created")

    # Defining Many-to-Many Relationships as students and teachers can have many courses and courses can have many students
    # enrolled as well as multiple quizzes and assignments
    teachers = db.relationship("User", secondary="teacher_course", back_populates="teaching_courses")
    students = db.relationship("User", secondary="student_course", back_populates="enrolled_courses")

    quizzes = db.relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    assignments = db.relationship("Assignment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Course (id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the Course {self.name} with code {self.code}"



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