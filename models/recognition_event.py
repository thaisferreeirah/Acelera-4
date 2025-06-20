from db import db

class Recognition(db.Model):
    __tablename__ = 'recognition'
    recognition_id = db.Column(db.Integer, primary_key=True)
    authorized_id = db.Column(db.Integer, db.ForeignKey('authorized.authorized_id'), nullable=True)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    method = db.Column(db.String(30))
    description = db.Column(db.String(255))

