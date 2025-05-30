from flask import Flask
from db import db
from routes.websocket import websocketio

from routes.main import main
from routes.auth import auth
from routes.members import members
from routes.students import students
from routes.esp import esp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/meubanco'

app.secret_key = "segredo"

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(members)
app.register_blueprint(students)
app.register_blueprint(esp)

websocketio.init_app(app)

if __name__ == "__main__":
    #app.run(host="192.168.83.89", port=5000, debug=True)
    #app.run(host="0.0.0.0", port=5000, debug=True)
    websocketio.run(app, host="192.168.197.89", port=5000, debug=True)