# Para realizar testes sem precisar logar

from flask import Blueprint, request, render_template, jsonify
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
    auth_id = request.form.get("id")
    date = datetime.today().date()
    time = datetime.today().time().strftime("%H:%M:%S")  # Formata sem os decimais

    member = Recognition(authorized_id=auth_id, date=date, time=time)
    db.session.add(member)
    db.session.commit()

    return "Cadastrado com sucesso!", 201

# Página do histórico de reconhecimento facial
@rectest.route('/historicotest')
def historicotest():
    return render_template('historico.html')


import psycopg2
# Busca o histórico de reconhecimento facial no banco de dados
def get_data_histrectest():
    conn = psycopg2.connect(database="meubanco", user="postgres", password="123", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("""
        SELECT a.authorized_name, r.date, r.time
        FROM authorized a
        JOIN recognition r ON a.authorized_id = r.authorized_id
        ORDER BY r.recognition_id DESC""")
    
    rows = cur.fetchall()
    conn.close()

    # Converte 'time' para string formatada
    return [{"authorized_name": row[0], "date": row[1].strftime("%d/%m/%Y"), "time": row[2].strftime("%H:%M:%S")} for row in rows]

@rectest.route('/histrectest')
def histrectest():
    return jsonify(get_data_histrectest())