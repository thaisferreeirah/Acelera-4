from db import db

class Authorized(db.Model):
    __tablename__ = 'authorized'
    authorized_id = db.Column(db.Integer, primary_key=True)
    authorized_name = db.Column(db.String(255))
    cpf = db.Column(db.String(14), unique=True)
    position = db.Column(db.String(12))
    photo = db.Column(db.Text, unique=True)
