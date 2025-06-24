from flask import Blueprint, render_template, request, jsonify, url_for
from datetime import datetime
import psycopg2
import os
from helpers import login_required
from models.user import User
from models.authorized_member import Authorized
from models.recognition_event import Recognition
from db import db

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
     return render_template("index.html")
     
@main.route("/historico")
@login_required
def historico():
      return render_template("historico.html")
       
@main.route('/acesso')
@login_required
def liberar_acesso():
    return render_template('liberarAcesso.html')

@main.route("/usuarios")
@login_required
def get_users():
    users = User.query.all()

    if not users:
        return "Nenhum membro autorizado encontrado!", 404

    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "access_level": user.access_level,
        })            
    
    return user_list








