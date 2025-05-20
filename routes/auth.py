from flask import Blueprint, request, session
from models.user import db, User

auth = Blueprint("auth", __name__)

 #Rotas para autenticação
@auth.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Nome de usuário e senha são obrigatórios!", 400
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["user_id"] = user.id
        return "Logado com sucesso", 200
    else:
        return "Credenciais incorretas", 401


@auth.route("/cadastro", methods=["POST"])
def signup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not password:
        return "Nome de usuário e senha são obrigatórios!", 400
    
    if not email:
        return "Email é obrigatório!", 400
    
    if User.query.filter_by(username=username).first():
        return "Nome de usuário já existe!", 409
    
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return "Registrado com sucesso", 201

@auth.route("/logout")
def logout():
    session.clear()
    return "Sessão Limpa.", 204