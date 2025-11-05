from flask import Flask
import os
from data_models import db


#Creating the flask app object
app = Flask(__name__)

# Finds the absolute path to our project folder
basedir = os.path.abspath(os.path.dirname(__file__))
# The database connection set up which tells that we are using SQLite and base folder has been joined with the subfolder lms.db
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/lms.db')}"
# Disabling SQLAlchemy’s event system that tracks object changes.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Link the database and the app. This is the reason we need to import db from models

if __name__ == "__main__":
    """with app.app_context():
            db.create_all()""" # Creating all the database tables defined by our models.
    app.run(debug=True)