from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Defining the Student model as a class
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    program = db.Column(db.String(20), nullable=False)

    # Adding the relationship to Course class
    courses = db.relationship("Course", backref="student", lazy=True)

    def __repr__(self):
        return f"Student(id = {self.id}, name = {self.name})"

    def __str__(self):
        return f"The id {self.id} represents the student {self.name}"

# Defining the Course model as a class
class Course(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False)

  grade = db.Column(db.Float, nullable=False)
  quiz = db.Column(db.Float, nullable=False)
  assignment = db.Column(db.Float, nullable=False)
  paper = db.Column(db.Float, nullable=False)

  # Link Class to Student
  student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

  def __repr__(self):
      return f"Course (id = {self.id}, name = {self.name})"

  def __str__(self):
      return f"The id {self.id} represents the Course {self.name}"