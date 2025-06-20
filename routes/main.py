from flask import Blueprint, render_template
from helpers import login_required
from models.user import User


main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
    return render_template("index.html")

@main.route("/historico")
@login_required
def historico():
    return render_template("historico.html")

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