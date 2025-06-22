import config
from flask import Flask
from db import db
from routes.websocket import websocketio
from routes.main import main
from routes.auth import auth
from routes.members import members
from routes.students import students
from routes.esp import esp
from routes.recognitiontest import rectest

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/meubanco'

app.secret_key = "segredo"

db.init_app(app)

# Registro de Blueprints
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(members)
app.register_blueprint(students)
app.register_blueprint(esp)
app.register_blueprint(rectest)

websocketio.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria tabelas se não existirem
    websocketio.run(app, allow_unsafe_werkzeug=True, host=config.HOST, port=config.PORT, debug=True)