
# from flask import Blueprint, render_template, request, jsonify
# from datetime import datetime
# import psycopg2
# import os
# from helpers import login_required
# from models.user import User
# from models.authorized_member import Authorized
# from models.recognition_event import Recognition
# from db import db

# main = Blueprint("main", __name__)

# # Rotas principais
# @main.route("/")
# @login_required
# def index():
#     return render_template("index.html")

# # # Rotas de histórico (unificadas)
# # @main.route("/historico")
# # @login_required
# # def historico():
# #     return render_template("historico.html")

# # Rotas de acesso
# @main.route('/acesso')
# @login_required
# def liberar_acesso():
#     return render_template('liberarAcesso.html')

# # Rotas de cadastros
# @main.route("/lista-cadastros")
# @login_required
# def lista_cadastros():
#     nome_filtro = request.args.get('filtro_nome', '')
#     cargo_filtro = request.args.get('filtro_cargo', '')
    
#     query = Authorized.query
#     if nome_filtro:
#         query = query.filter(Authorized.authorized_name.contains(nome_filtro))
#     if cargo_filtro:
#         query = query.filter_by(position=cargo_filtro)
    
#     cadastros = query.all()
#     return render_template("lista_cadastros.html", cadastros=cadastros)

# # API de reconhecimento facial
# @main.route("/api/membros/<int:id>", methods=["GET"])
# @login_required
# def get_member(id):
#     member = Authorized.query.filter_by(authorized_id=id).first()
#     return jsonify({"name": member.authorized_name}) if member else ("Membro não encontrado!", 404)

# @main.route("/api/log-recognicao", methods=["POST"])
# @login_required
# def log_recognicao():
#     auth_id = request.form.get("id")
#     new_log = Recognition(
#         authorized_id=auth_id,
#         date=datetime.today().date(),
#         time=datetime.today().time().strftime("%H:%M:%S"),
#         method="Reconhecimento Facial"
#     )
#     db.session.add(new_log)
#     db.session.commit()
#     return "Cadastrado com sucesso!", 201

# # @main.route('/api/historico-recognicao')
# # @login_required
# # def historico_recognicao_data():
# #     # Rotas de histórico (unificadas)
# @main.route("/historico")
# @login_required
# def historico():
#     return render_template("historico.html")
#     conn = psycopg2.connect(
#         database="meubanco",
#         user="postgres",
#         password="123",
#         host="localhost",
#         port="5432"
#     )
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT a.authorized_name, r.date, r.time, r.method, r.description
#         FROM recognition r
#         LEFT JOIN authorized a ON a.authorized_id = r.authorized_id
#         ORDER BY r.recognition_id DESC""")
    
#     historico = [{
#         "authorized_name": row[0],
#         "date": row[1].strftime("%d/%m/%Y"),
#         "time": row[2].strftime("%H:%M:%S"),
#         "method": row[3],
#         "description": row[4]
#     } for row in cur.fetchall()]
    
#     conn.close()
#     return jsonify(historico)

# @main.route("/api/log-manual", methods=["POST"])
# @login_required
# def log_manual():
#     data = request.json
#     new_log = Recognition(
#         authorized_id=data.get("id"),
#         date=datetime.today().date(),
#         time=datetime.today().time().strftime("%H:%M:%S"),
#         method="Manual",
#         description=data.get("descricao")
#     )
#     db.session.add(new_log)
#     db.session.commit()
#     return "Cadastrado com sucesso!", 201

# @main.route('/api/autorizados')
# @login_required
# def get_autorizados():
#     members = Authorized.query.all()
#     return jsonify([{"id": m.authorized_id, "name": m.authorized_name} for m in members])

# @main.route('/api/foto-autorizado/<int:id>')
# @login_required
# def get_foto_autorizado(id):
#     for ext in ["jpg", "jpeg", "png"]:
#         if os.path.exists(f"static/images/{id}.{ext}"):
#             return jsonify({"foto": url_for('static', filename=f'images/{id}.{ext}')})
#     return jsonify({"foto": url_for('static', filename='images/default.jpg')})

# # Exemplo de rota atualizada usando seu modelo Recognition
# # @main.route("/api/log-recognicao", methods=["POST"])
# # @login_required
# # def log_recognicao():
# #     auth_id = request.form.get("id")
# #     new_log = Recognition(
# #         authorized_id=auth_id,
# #         date=datetime.today().date(),
# #         time=datetime.today().time(),
# #         method="Reconhecimento Facial",
# #         description=None
# #     )
# #     db.session.add(new_log)
# #     db.session.commit()
# #     return "Cadastrado com sucesso!", 201




from flask import Blueprint, render_template, request, jsonify, url_for
from datetime import datetime
import psycopg2
import os
from helpers import login_required
from models.user import User
from models.authorized_member import Authorized
from models.recognition_event import Recognition
from db import db

main = Blueprint("main", __name__)

# Rotas principais
@main.route("/")
@login_required
def index():
    return render_template("index.html")

@main.route("/historico")
@login_required
def historico():
    """Rota unificada para o histórico"""
    return render_template("historico.html")

@main.route('/acesso')
@login_required
def liberar_acesso():
    return render_template('liberarAcesso.html')

@main.route("/lista-cadastros")
@login_required
def lista_cadastros():
    nome_filtro = request.args.get('filtro_nome', '')
    cargo_filtro = request.args.get('filtro_cargo', '')
    
    query = Authorized.query
    if nome_filtro:
        query = query.filter(Authorized.authorized_name.contains(nome_filtro))
    if cargo_filtro:
        query = query.filter_by(position=cargo_filtro)
    
    cadastros = query.all()
    return render_template("lista_cadastros.html", cadastros=cadastros)

# API de reconhecimento facial
@main.route("/api/membros/<int:id>", methods=["GET"])
@login_required
def get_member(id):
    member = Authorized.query.filter_by(authorized_id=id).first()
    return jsonify({"name": member.authorized_name}) if member else ("Membro não encontrado!", 404)

@main.route("/api/log-recognicao", methods=["POST"])
@login_required
def log_recognicao():
    auth_id = request.form.get("id")
    new_log = Recognition(
        authorized_id=auth_id,
        date=datetime.today().date(),
        time=datetime.today().time().strftime("%H:%M:%S"),
        method="Reconhecimento Facial"
    )
    db.session.add(new_log)
    db.session.commit()
    return "Cadastrado com sucesso!", 201

@main.route('/api/historico-recognicao')
@login_required
def historico_recognicao_data():
    conn = psycopg2.connect(
        database="meubanco",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT a.authorized_name, r.date, r.time, r.method, r.description
        FROM recognition r
        LEFT JOIN authorized a ON a.authorized_id = r.authorized_id
        ORDER BY r.recognition_id DESC""")
    
    historico = [{
        "authorized_name": row[0],
        "date": row[1].strftime("%d/%m/%Y"),
        "time": row[2].strftime("%H:%M:%S"),
        "method": row[3],
        "description": row[4]
    } for row in cur.fetchall()]
    
    conn.close()
    return jsonify(historico)

@main.route("/api/log-manual", methods=["POST"])
@login_required
def log_manual():
    data = request.json
    new_log = Recognition(
        authorized_id=data.get("id"),
        date=datetime.today().date(),
        time=datetime.today().time().strftime("%H:%M:%S"),
        method="Manual",
        description=data.get("descricao")
    )
    db.session.add(new_log)
    db.session.commit()
    return "Cadastrado com sucesso!", 201

@main.route('/api/autorizados')
@login_required
def get_autorizados():
    members = Authorized.query.all()
    return jsonify([{"id": m.authorized_id, "name": m.authorized_name} for m in members])

@main.route('/api/foto-autorizado/<int:id>')
@login_required
def get_foto_autorizado(id):
    for ext in ["jpg", "jpeg", "png"]:
        if os.path.exists(f"static/images/{id}.{ext}"):
            return jsonify({"foto": url_for('static', filename=f'images/{id}.{ext}')})
    return jsonify({"foto": url_for('static', filename='images/default.jpg')})