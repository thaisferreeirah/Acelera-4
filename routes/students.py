from flask import Blueprint, request
from models.user import db
from models.student import Student

students = Blueprint("student", __name__)

# Rotas de aluno
@students.route("/aluno/cadastro", methods=["POST"])
def student_signup():
    id = request.form.get("id")
    name = request.form.get("name")
    school_class = request.form.get("class")

    if not id:
        return "Insira o id do aluno!"
    
    # Verificar se é número
    
    if not name or not school_class:
        return "Nome e classe são obrigatórios!"
    
    student = Student(student_id=id, student_name=name, school_class=school_class)
    db.session.add(student)
    db.session.commit()

    return "Aluno cadastrado com sucesso!", 201