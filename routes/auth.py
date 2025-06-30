from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify
from models.user import db, User
from helpers import login_required

auth = Blueprint("auth", __name__)

# Rotas para autenticação
@auth.route("/login")
def loging():
    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "Nome de usuário e senha são obrigatórios!", 400
    
    user = User.query.filter_by(email=email).first()
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
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    access_level = request.form.get("access")

    if not email or not password:
        return jsonify({"message": "Nome de usuário e senha são obrigatórios!"}), 400
    
    if not name:
        return jsonify({"message": "Nome é obrigatório!"}), 400
    
    if not access_level:
        return jsonify({"message": "Selecione um nível de acesso!"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Nome de usuário já existe!"}), 409
    
    match access_level:
        case 'Administrador':
            access_level='a'
        case 'Porteiro':
            access_level='p'
        case _:
            return jsonify({"message": "Inválido!"}), 400
    
    user = User(name=name, email=email, access_level=access_level)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário cadastrado com sucesso!"}), 200

@auth.route("/usuarios", methods=["GET"])
#@login_required
def get_users():
    users = User.query.all()

    if not users:
        return "Nenhum membro autorizado encontrado!", 404

    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "access_level": user.access_level
        })            
    
    return users_list

@auth.route("/usuarios/update/<int:id>", methods=["POST"])
#@login_required
def usermember(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "Não encontrado!"}), 404

    new_name = request.form.get("name")
    new_email = request.form.get("email")
    new_password = request.form.get("password")

    # Verifica se o novo email já pertence a outro usuário
    if User.query.filter(User.email == new_email, User.id != id).first():
        return jsonify({"message": "Usuário já existe!"}), 409

    # Atualiza os dados
    user.name = new_name
    user.email = new_email
    user.hash_password(new_password)

    db.session.commit()

    return jsonify({"message": "Alterações salvas com sucesso!"}), 200

@auth.route("/usuarios/delete/<int:id>", methods=["POST"])
def delete_user(id):
    user = User.query.get(id)

    if not user:
        return "Usuário não encontrado", 404

    db.session.delete(user)
    db.session.commit()

    return "Apagado com sucesso!", 204

@auth.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))