from flask import Blueprint, render_template, request
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

@main.route('/acesso')
@login_required
def liberar_acesso():
    return render_template('liberarAcesso.html')

@main.route("/usuarios")
@login_required
def get_users():
    name_filter = request.args.get("name")
    access_level_filter = request.args.get("access_level")

    filters = []
    if name_filter:
        filters.append(User.username.ilike(f"%{name_filter}%"))
    if access_level_filter:
        filters.append(User.access_level.ilike(f"%{access_level_filter}%"))

    # O * envia os filtros da lista filters como argumentos separados, para a pesquisa funcionar de forma dinamica
    users = User.query.filter(*filters).all()

    if not users:
        return "Nenhum usuário encontrado!", 404

    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "access_level": user.access_level,
        })            
    
    return user_list








