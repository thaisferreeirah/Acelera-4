from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from models.user import db
from models.authorized_member import Authorized
from helpers import login_required
from base64 import b64decode

from werkzeug.utils import secure_filename
import os

members = Blueprint("members", __name__)

@members.route("/autorizado")
#@login_required
def members_page():
    return render_template("autorizado.html")

# Rotas parar membros autorizados
@members.route("/membros", methods=["GET"])
#@login_required
def get_members():
    authorized_members = Authorized.query.all()

    if not authorized_members:
        return "Nenhum membro autorizado encontrado!", 404

    members_list = []
    for member in authorized_members:
        members_list.append({
            "id": member.authorized_id,
            "name": member.authorized_name,
            "cpf": member.cpf,
            "position": member.position
        })            
    
    return members_list

@members.route("/membros", methods=["POST"])
#@login_required
def auth_member_signup():
    auth_name = request.form.get("name")
    cpf = request.form.get("cpf")
    photo_file = request.files.get("photo")  # Foto tradicional
    photo_base64 = request.form.get("photoData")  # Foto da câmera

    # Validação de CPF
    if len(cpf) != 11:
        return "CPF inválido!", 400

    if Authorized.query.filter_by(cpf=cpf).first():
        return "CPF já cadastrado!", 409

    # Salva a imagem da câmera (base64)
    if photo_base64 and photo_base64.startswith("data:image"):
        img_data = b64decode(photo_base64.split(',')[1])
        with open(f"static/images/{member.authorized_id}.png", "wb") as f:
            f.write(img_data)

    # Ou salva a imagem selecionada pelo input file
    elif photo_file and photo_file.filename != "":
        filename = secure_filename(f"{member.authorized_id}.png")
        photo_file.save(os.path.join("static/images", filename))

    else:
        return "Adicione uma foto!"

    # Cria o registro
    member = Authorized(authorized_name=auth_name, cpf=cpf)
    db.session.add(member)
    db.session.commit()  # Agora o member.authorized_id está disponível

    return redirect(url_for("members.members_page"))

@members.route("/membros/<int:id>", methods=["GET"])
#@login_required
def get_member(id):
    member = Authorized.query.get(id)

    if member:
        return [{
            "id": member.authorized_id,
            "name": member.authorized_name,
            "cpf": member.cpf,
            "photo": member.photo
        }]
    
    return "Membro não encontrado!", 404

@members.route("/membros/update/<int:id>", methods=["POST"])
#@login_required
def update_member(id):
    member = Authorized.query.get(id)

    if not member:
        return jsonify({"message": "Não encontrado!"}), 404

    new_name = request.form.get("name")
    new_cpf = request.form.get("cpf")
    photo_file = request.files.get("photo")  # imagem tradicional
    photo_base64 = request.form.get("photoData")  # imagem da câmera

    if not new_name or not new_cpf:
        return jsonify({"message": "Preencha todos os campos!"}), 400

    if len(new_cpf) != 11:
        return jsonify({"message": "CPF inválido!"}), 400

    # Verifica se o novo CPF já pertence a outro autorizado
    if Authorized.query.filter(Authorized.cpf == new_cpf, Authorized.authorized_id != id).first():
        return jsonify({"message": "CPF já cadastrado em outro membro autorizado!"}), 409

    # Atualiza os dados
    member.authorized_name = new_name
    member.cpf = new_cpf

    # Salva a nova imagem (caso enviada)
    if photo_base64 and photo_base64.startswith("data:image"):
        from base64 import b64decode
        img_data = b64decode(photo_base64.split(',')[1])
        with open(f"static/images/{member.authorized_id}.png", "wb") as f:
            f.write(img_data)

    elif photo_file and photo_file.filename != "":
        from werkzeug.utils import secure_filename
        import os
        filename = secure_filename(f"{member.authorized_id}.png")
        photo_file.save(os.path.join("static/images", filename))

    db.session.commit()

    return jsonify({"message": "Alterações salvas com sucesso!"}), 200

@members.route("/membros/delete/<int:id>", methods=["POST"])
#@login_required
def delete_member(id):
    member = Authorized.query.get(id)

    if not member:
        return "Membro não encontrado", 404
    
    db.session.delete(member)
    db.session.commit()

    return "Apagado com sucesso!", 204