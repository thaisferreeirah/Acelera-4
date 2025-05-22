from flask import Flask, request, render_template
import requests
import base64

app = Flask(__name__)

#ESP32_WROOM_URL = "http://192.168.0.5/activate"  # URL do ESP32-WROOM Casa
ESP32_WROOM_URL = "http://192.168.83.136/activate" # Celular

@app.route('/recognition', methods=['POST'])
def face_recognition():
    data = request.json  # Recebe dados JSON do ESP32-CAM
    if data and data.get("recognized") == True:
        person_name = data.get("name")
        print(f"Rosto reconhecido: {person_name}")

        # Enviar comando para ESP32-WROOM ativar o motor
        requests.get(ESP32_WROOM_URL)

        return {"status": "motor activated"}, 200

    return {"status": "no recognition"}, 400

@app.route('/takephoto')
def home():
    return render_template('takephoto.html')

@app.route('/salvar_imagem', methods=['POST'])
def salvar_imagem():
    data = request.json['imagem']
    
    # Remover cabeçalho do base64 e converter para binário
    img_data = base64.b64decode(data.split(',')[1])

    # Salvar na pasta do projeto
    with open("static/captura.png", "wb") as f:
        f.write(img_data)

    return {"mensagem": "Imagem salva com sucesso!"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)