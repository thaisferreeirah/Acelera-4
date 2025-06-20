# Para realizar testes sem precisar logar

from flask import Blueprint, request, render_template, jsonify, url_for
from models.user import db
from models.authorized_member import Authorized
from models.recognition_event import Recognition
import os
import psycopg2

from datetime import datetime

rectest = Blueprint("recognitiontest", __name__)

# Rota para a página liberarAcesso.html
@rectest.route('/libacestest')
def libacestest():
    return render_template('liberarAcesso.html')

# Rota para a página historico.html
@rectest.route('/historicotest')
def historicotest():
    return render_template('historico.html')

@rectest.route("/cadastrosemlogin")
def cadastrosemlogin():
    return render_template("cadastroUsuario.html")

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
    method = "Reconhecimento Facial"

    member = Recognition(authorized_id=auth_id, date=date, time=time, method=method)
    db.session.add(member)
    db.session.commit()

    return "Cadastrado com sucesso!", 201

# Busca o histórico de reconhecimento facial no banco de dados
def get_data_histrectest():
    conn = psycopg2.connect(database="meubanco", user="postgres", password="123", host="localhost", port="5432")
    cur = conn.cursor()
    cur.execute("""
        SELECT a.authorized_name, r.date, r.time, r.method, r.description
        FROM recognition r
        LEFT JOIN authorized a ON a.authorized_id = r.authorized_id
        ORDER BY r.recognition_id DESC""")
    
    rows = cur.fetchall()
    conn.close()

    # Converte 'time' para string formatada
    return [{"authorized_name": row[0], "date": row[1].strftime("%d/%m/%Y"), "time": row[2].strftime("%H:%M:%S"), "method": row[3], "description": row[4]} for row in rows]

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

    member = Recognition(authorized_id=authorized_id, date=date, time=time, method=method, description=description)
    db.session.add(member)
    db.session.commit()

    return "Cadastrado com sucesso!", 201

# Busca os nomes e IDs dos autorizados
@rectest.route('/get_authorized_name_id')
def get_authorized_name_id():
    members = Authorized.query.all()  # Obtém todos os registros da tabela
    result = [{"id": member.authorized_id, "name": member.authorized_name} for member in members]
    return jsonify(result)  # Retorna os dados em formato JSON

# Busca a foto do autorizado pelo ID
@rectest.route('/get_photo/<int:id>')
def get_photo(id):
    """Verifica qual extensão da imagem está disponível"""
    formatos = ["jpg", "jpeg", "png"]
    for ext in formatos:
        caminho_arquivo = f"static/images/{id}.{ext}"
        if os.path.exists(caminho_arquivo):
            return jsonify({"foto": url_for('static', filename=f'images/{id}.{ext}')})

    return jsonify({"foto": url_for('static', filename='images/default.jpg')})  # Foto padrão se não encontrar



from models.user import db, User

def cadastrarsemlogin():
    username = "ad"
    email = "ad@email.com"
    password = "123"
    access_level = "Administrador"
    
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

    return 'a'