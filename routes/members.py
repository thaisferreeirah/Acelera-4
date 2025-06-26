from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from models.user import db
from models.authorized_member import Authorized
from helpers import login_required
from base64 import b64decode

from werkzeug.utils import secure_filename
import os

from routes.esp import adicionar_nova_face, atualizar_face

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
    photo_file = request.files.get("photo")
    photo_base64 = request.form.get("photoData")

    if not auth_name or not cpf:
        return jsonify({"message": "Preencha todos os campos!"}), 400

    if len(cpf) != 11:
        return jsonify({"message": "CPF inválido!"}), 400

    if Authorized.query.filter_by(cpf=cpf).first():
        return jsonify({"message": "CPF já cadastrado!"}), 409

    # Verifique a existência da imagem antes de criar o registro
    if not ((photo_base64 and photo_base64.startswith("data:image")) or (photo_file and photo_file.filename != "")):
        return jsonify({"message": "Adicione uma foto!"}), 400

    # Cria o registro
    member = Authorized(authorized_name=auth_name, cpf=cpf)
    db.session.add(member)
    db.session.commit()

    # Agora salva a imagem
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

    adicionar_nova_face(f"{member.authorized_id}.png")

    return jsonify({"message": "Autorizado cadastrado com sucesso!"}), 200

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

    atualizar_face(f"{member.authorized_id}.png")

    return jsonify({"message": "Alterações salvas com sucesso!"}), 200

@members.route("/membros/delete/<int:id>", methods=["POST"])
def delete_member(id):
    import os
    import glob

    member = Authorized.query.get(id)

    if not member:
        return "Membro não encontrado", 404

    # Caminhos possíveis para a imagem (jpg, jpeg, png)
    padrao_imagem = f"static/images/{member.authorized_id}.*"
    arquivos = glob.glob(padrao_imagem)

    # Remove todos os arquivos encontrados com esse ID
    for caminho in arquivos:
        try:
            os.remove(caminho)
        except Exception as e:
            return f"Erro ao excluir imagem: {str(e)}", 500

    db.session.delete(member)
    db.session.commit()

    return "Apagado com sucesso!", 204