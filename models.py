from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    availability = db.Column(db.JSON)  # Example: {"9:00-10:00": True, "10:00-11:00": False}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

# Model for Class 1 Timetable
class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(50), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    teacher = db.relationship('Teacher', backref='timetables')

# Model for Class 2 Timetable
class Timetable2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.String(50), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    teacher = db.relationship('Teacher', backref='timetables2')