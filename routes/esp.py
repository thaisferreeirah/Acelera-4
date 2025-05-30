from flask import Blueprint, request, render_template, Response
import cv2
import requests
import base64

cam = Blueprint('recognition', __name__)

ESP32_WROOM_URL = "http://esp32wroom.local/activate" # URL do ESP32-WROOM

ESP32_CAM_URL = "http://esp32cam.local:81/stream" # URL do ESP32-CAM

def generate_frames():
    cap = cv2.VideoCapture(ESP32_CAM_URL)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@cam.route('/stream')
def stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@cam.route('/recognition', methods=['POST'])
def face_recognition():
    data = request.json  # Recebe dados JSON do ESP32-CAM
    if data and data.get("recognized") == True:
        person_name = data.get("name")
        print(f"Rosto reconhecido: {person_name}")

        # Enviar comando para ESP32-WROOM ativar o motor
        requests.get(ESP32_WROOM_URL)

        return {"status": "motor activated"}, 200

    return {"status": "no recognition"}, 400

@cam.route('/takephoto')
def home():
    return render_template('takephoto.html')

@cam.route('/save_photo', methods=['POST'])
def save_photo():
    data = request.json
    nome = data['nome'].strip().replace(" ", "_")  # Remover espaços e evitar problemas
    
    # Remover cabeçalho do base64 e converter para binário
    img_data = base64.b64decode(data['imagem'].split(',')[1])

    # Salvar com o nome fornecido
    with open(f"static/{nome}.png", "wb") as f:
        f.write(img_data)

    return {"mensagem": f"Imagem '{nome}.png' salva com sucesso!"}
