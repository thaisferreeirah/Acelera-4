from flask import Blueprint, render_template
from helpers import login_required

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
    return render_template("index.html")

@main.route("/historico")
@login_required
def historico():
    return render_template("historico.html")