from db import db

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(255), unique=True)
    school_class = db.Column(db.String(5), unique=True)
