# Para realizar testes sem precisar logar

from flask import Blueprint, request
from models.user import db
from models.authorized_member import Authorized
from models.recognition_event import Recognition

from datetime import datetime

rectest = Blueprint("recognitiontest", __name__)

# Ver se o reconhecimento facial consegue buscar as informações do autorizado
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
    auth_id =  request.form.get("id")
    date = datetime.today().date()
    time = datetime.today().time()

    member = Recognition(authorized_id=auth_id, date=date, time=time)
    db.session.add(member)
    db.session.commit()

    return "Cadastrado com sucesso!", 201