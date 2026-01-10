import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

# Class Model UserRole defined to set the roles allowed for users using the enum class
class UserRole(enum.Enum):
    """This class defines the user roles allowed using the enum method from Enum class to ensure database integrity,avoid
    magic strings and typos and to prevent invalid user values"""
    admin = "admin"
    teacher = "teacher"
    student = "student"

# Integrating the Student, Teacher and Admin model as a single class User
class User(db.Model):
    """This class defines a general user who can either be a teacher, student or admin"""
    __tablename__ = 'users'
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
    questions_created = db.relationship("Question", back_populates="created_by_user") # Adding new link to questions
    answers = db.relationship("StudentAnswer", back_populates="student") # Adding new link to answers

    # Many-to-many relationships defined, the below variables will serve as the relationship properties,
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
    __tablename__ = 'programs'
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

    def __repr__(self):
        return f"Program (id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the Program {self.name} with represents {self.description}"

# Defining the Course model as a class
class Course(db.Model):
    """This class defines a course which can be taken up by a student and taught and maintained by a teacher, also they
    can have courses and assignments"""
    __tablename__ = 'courses'
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
    # enrolled as well as multiple quizzes and assignments which will be instrumented lists
    teachers = db.relationship("User", secondary="teacher_course", back_populates="teaching_courses")
    students = db.relationship("User", secondary="student_course", back_populates="enrolled_courses")

    quizzes = db.relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    assignments = db.relationship("Assignment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Course (id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the Course {self.name} with code {self.code}"


# Association Table teacher_course created to handle the many-to_many relationships between teachers, and the courses they teach
teacher_course = db.Table(
    'teacher_course',
    db.Column('teacher_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
)

# Association Table student_course created to handle the many-to_many relationships between students, and the courses they take
student_course = db.Table(
    'student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
)

# Class model Quiz created and defined
class Quiz(db.Model):
    """This class defines the basic functions of a quiz table like its title, marks, due date, the teacher who created it,
    and the course it is linked to"""
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    total_marks = db.Column(db.Integer)
    due_date = db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships defined based on courses and teachers
    course = db.relationship("Course", back_populates="quizzes")
    created_by_user = db.relationship("User", back_populates="quizzes_created")

    # Relationships added for the questions and answers
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    student_answers = db.relationship("StudentAnswer", backref="quiz")

    def __repr__(self):
        return f"Quiz (id = {self.id}, title = {self.title})"

    def __str__(self):
        return f"The id {self.id} represents the Quiz titled {self.title}"


# Class model Quiz created and defined
class Assignment(db.Model):
    """This class defines the basic functions of an assignment table like its title, marks, due date, the teacher who
    created it, and the course it is linked to"""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    total_marks = db.Column(db.Integer)
    due_date = db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships defined based on courses and teachers
    course = db.relationship("Course", back_populates="assignments")
    created_by_user = db.relationship("User", back_populates="assignments_created")

    # Relationships added for the questions and answers
    questions = db.relationship("Question", back_populates="assignment", cascade="all, delete-orphan")
    student_answers = db.relationship("StudentAnswer", backref="assignment")

    def __repr__(self):
        return f"Assignment (id = {self.id}, title = {self.title})"

    def __str__(self):
        return f"The id {self.id} represents the Assignment titled {self.title}"


# Adding the Question Table to expand the database and accommodate Gen AI requests for later
class Question(db.Model):
    __tablename__ = 'questions'

    id =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # The newer columns pertaining to the questions, their types and marks
    question_text = db.Column(db.Text, nullable=False) # db.Text used as it can be a large descriptive value
    question_type = db.Column(db.String(10))
    marks = db.Column(db.Integer)

    # Defining the relationships between users, quizzes, assignments with questions, answers and the options that can be answered
    created_by_user = db.relationship("User", back_populates="questions_created")
    assignment = db.relationship("Assignment", back_populates="questions")
    quiz = db.relationship("Quiz", back_populates="questions")

    options = db.relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    student_answers = db.relationship("StudentAnswer", back_populates="question")

    def __repr__(self):
        return f"Question (id = {self.id}, title = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the Question titled {self.title}"


# QuestionOption Class defined to introduce a way to facilitate the different options for MCQs
class QuestionOption(db.Model):
    __tablename__ = 'question_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)

    option_text = db.Column(db.Text, nullable=False) # the text for the option
    is_correct = db.Column(db.Boolean, default=False) # whether correct option or not
    order_index = db.Column(db.Integer, default=0) # number of the option

    question = db.relationship("Question", back_populates="options") # relationship defined for the Question Class
    student_answers = db.relationship("StudentAnswer", back_populates="selected_option")


# StudentAnswer Class defined for storing the answers submitted by the students
class StudentAnswer(db.Model):
    __tablename__ = 'student_answers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # nullable can be true if the question doesn't belong to a quiz and belongs to an assignment
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=True)

    selected_option_id = db.Column(db.Integer, db.ForeignKey('question_options.id')) # in case of MCS
    answer_text = db.Column(db.Text) # In case of descriptive questions

    marks_awarded = db.Column(db.Integer)
    evaluated_by_ai = db.Column(db.Boolean, default=False)
    evaluated_by_teacher = db.Column(db.Boolean, default=False)

    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
    attempt_number = db.Column(db.Integer, default=1)

    # Relationships defined
    question = db.relationship("Question", back_populates="student_answers")
    student = db.relationship("User", back_populates="answers") # answers is an attribute on the User model
    selected_option = db.relationship("QuestionOption", back_populates="student_answers")

