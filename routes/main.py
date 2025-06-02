from flask import Blueprint
from helpers import login_required

main = Blueprint("main", __name__)

@main.route("/")
@login_required
def index():
    return "Olá Flask"