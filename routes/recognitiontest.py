from datetime import datetime
import os

from flask import Blueprint, jsonify, request, url_for, render_template, session

from models.authorized_member import Authorized
from models.recognition_event import Recognition
from models.user import db

rectest = Blueprint("recognitiontest", __name__)

# Verifica se o reconhecimento facial consegue buscar as informações do autorizado
@rectest.route("/membrosrectest/<int:id>", methods=["GET"])
def get_memberrectest(id):
    member = Authorized.query.filter_by(authorized_id=id).first()  # Busca pelo authorized_id

    if member:
        return [{
            "name": member.authorized_name
        }]
    
    return "Membro não encontrado!", 404

# Registra o reconhecimento facial no banco
@rectest.route("/reclogtest", methods=["POST"])
def reclogtest():
    auth_id = request.form.get("id")
    date = datetime.today().date()
    time = datetime.today().time().strftime("%H:%M:%S")  # Formata sem os decimais
    method = "Reconhecimento Facial"

    user_id = session["user_id"]

    member = Recognition(authorized_id=auth_id, date=date, time=time, method=method, user_id=user_id)
    db.session.add(member)
    db.session.commit()

    return "Cadastrado com sucesso!", 201

# Busca o histórico de reconhecimento facial no banco de dados
def get_data_histrectest():
    recognitions = db.session.query(
            Authorized.authorized_name,
            Recognition.date,
            Recognition.time,
            Recognition.method,
            Recognition.description
        ).outerjoin(Authorized, Recognition.authorized_id == Authorized.authorized_id)\
        .order_by(Recognition.recognition_id.desc())\
        .all() 

    recognition_history = []
    for recognition in recognitions:
        recognition_history.append({
            "authorized_name": recognition.authorized_name,
            "date": recognition.date.strftime("%d/%m/%Y"), 
            "time": recognition.time.strftime("%H:%M:%S"), 
            "method": recognition.method,
            "description": recognition.description
        })
        
    return recognition_history

@rectest.route('/histrectest')
def histrectest():
    return jsonify(get_data_histrectest())

# Salva o acesso manual
@rectest.route("/manuallogtest", methods=["POST"])
def manuallogtest():
    date = datetime.today().date()
    time = datetime.today().time().strftime("%H:%M:%S")  # Formata sem os decimais
    method = "Manual"
    authorized_id = request.json.get("id")
    description = request.json.get("descricao")

    user_id = session["user_id"]

    member = Recognition(authorized_id=authorized_id, date=date, time=time, method=method, description=description, user_id=user_id)
    db.session.add(member)
    db.session.commit()

    return "Cadastrado com sucesso!", 201

# Busca os nomes e IDs dos autorizados
@rectest.route('/get_authorized_name_id')
def get_authorized_name_id():
    # Filtra os registros onde 'position' é NULL
    members = Authorized.query.filter(Authorized.position == None).all()

    result = [{"id": member.authorized_id, "name": member.authorized_name} for member in members]
    return jsonify(result)

# Busca a foto do autorizado pelo ID
@rectest.route('/get_photo/<int:id>')
def get_photo(id):
    """Verifica qual extensão da imagem está disponível"""
    formatos = ["jpg", "jpeg", "png"]
    for ext in formatos:
        caminho_arquivo = f"static/images/{id}.{ext}"
        if os.path.exists(caminho_arquivo):
            return jsonify({"foto": url_for('static', filename=f'images/{id}.{ext}')})

    return jsonify({"foto": url_for('static', filename='images/1.png')})  # Foto padrão se não encontrar


###############################################
# Cadastrar um usuário
#from models.user import db, User
#
#def cadastrarsemlogin():
#    name = "Johnny Bravo"
#    email = "jojo@email.com"
#    password = "123123"
#    access_level = "Administrador"
#    
#    match access_level:
#        case 'Administrador':
#            access_level='a'
#        case 'Porteiro':
#            access_level='p'
#        case _:
#            return "Inválido!", 400
#    
#    user = User(name=name, email=email, access_level=access_level)
#    user.hash_password(password)
#    db.session.add(user)
#    db.session.commit()
#
#    return 'a'