from flask import Blueprint, request
from models.user import db
from models.authorized_member import Authorized

members = Blueprint("members", __name__)

# Rotas parar membros autorizados
@members.route("/membros", methods=["GET"])
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
            "photo": member.photo
        })            
    
    return members_list

@members.route("/membros", methods=["POST"])
def auth_member_signup():
    auth_name = request.form.get("name")
    cpf = request.form.get("cpf")
    photo = request.form.get("photo")

    if len(cpf) != 11:
        print(len(cpf))
        return "CPF inválido!", 400
    
    if Authorized.query.filter(Authorized.cpf == cpf).first():
        return "CPF já cadastrado em outro membro autorizado!", 409

    member = Authorized(authorized_name=auth_name, cpf=cpf, photo=photo)
    db.session.add(member)
    db.session.commit()

    return "Cadastrado com sucesso!", 201

@members.route("/membros/<int:id>", methods=["GET"])
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
def update_member(id):
    member = Authorized.query.get(id)

    if not member:
        return "Não encontrado!", 404
    
    new_name = request.form.get("name")
    new_cpf = request.form.get("cpf")
    new_photo = request.form.get("photo")

    if not new_name or not new_cpf or not new_photo:
        return "Preencha todos os campos!", 400
    
    if len(new_cpf) != 11:
        print(len(new_cpf))
        return "CPF inválido!", 400
    
    # Verifica se o novo CPF pertence a alguém já cadastrado
    if Authorized.query.filter(Authorized.cpf == new_cpf, member.authorized_id != id).first():
        return "CPF já cadastrado em outro membro autorizado!", 409
    
    member.authorized_name = new_name
    member.cpf = new_cpf
    member.photo = new_photo

    db.session.commit()
    
    return [{
            "id": member.authorized_id,
            "name": member.authorized_name,
            "cpf": member.cpf,
            "photo": member.photo
        }]

@members.route("/membros/delete/<int:id>", methods=["POST"])
def delete_member(id):
    member = Authorized.query.get(id)

    if not member:
        return "Membro não encontrado", 404
    
    db.session.delete(member)
    db.session.commit()

    return "Apagado com sucesso!", 204