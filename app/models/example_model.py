# Example model for database (if using SQLAlchemy)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ExampleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)