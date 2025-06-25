from flask import Blueprint, request, session, render_template, redirect, url_for
from models.user import db, User
from helpers import login_required

auth = Blueprint("auth", __name__)

 #Rotas para autenticação
@auth.route("/login")
def loging():
    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Nome de usuário e senha são obrigatórios!", 400
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["user_id"] = user.id
        return redirect(url_for("main.index"))
    else:
        return "Credenciais incorretas", 401

@auth.route("/usuario")
@login_required
def signupg():
    return render_template("usuario.html")

@auth.route("/cadastro", methods=["POST"])
@login_required
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    access_level = request.form.get("access")

    if not username or not password:
        return "Nome de usuário e senha são obrigatórios!", 400
    
    if not email:
        return "Email é obrigatório!", 400
    
    if not access_level:
        return "Selecione um nível de acesso!", 400
    
    if User.query.filter_by(username=username).first():
        return "Nome de usuário já existe!", 409
    
    match access_level:
        case 'Administrador':
            access_level='a'
        case 'Porteiro':
            access_level='p'
        case _:
            return "Inválido!", 400
    
    user = User(username=username, email=email, access_level=access_level)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("auth.signupg"))

@auth.route("/logout")
@login_required
def logout():
    session.clear()
    return "Sessão Limpa.", 204