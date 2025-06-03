from flask import Blueprint, request, render_template, Response
from flask import Blueprint, request, render_template, Response
import cv2
import requests
import base64
import threading
from routes.websocket import websocketio


esp = Blueprint("esp", __name__)

ESP32_WROOM_URL = "http://esp32wroom.local/activate" # URL do ESP32-WROOM
ESP32_CAM_URL = "http://esp32cam.local:81/stream" # URL do ESP32-CAM
FLASK_SERVER_URL = "http://192.168.197.89:5000/recognition"


def generate_frames():
    cap = cv2.VideoCapture(ESP32_CAM_URL)
    print("generate_frames sendo chamado!")
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = base64.b64encode(buffer).decode('utf-8')
        print("Enviando frame...")  # Log de depuração
        websocketio.emit('stream', frame_data)

@websocketio.on('start_stream')
def handle_start_stream():
    print("Transmissão iniciada pelo cliente!")
    threading.Thread(target=generate_frames, daemon=True).start()

@websocketio.on('connect')
def handle_connect():
    print("Cliente conectado!")  # Isso deve aparecer no terminal do Flask

@esp.route('/recognition', methods=['POST'])
def face_recognition():
    data = request.json  # Recebe dados JSON do ESP32-CAM
    if data and data.get("recognized") == True:
        person_name = data.get("name")
        print(f"Rosto reconhecido: {person_name}")

        # Enviar comando para ESP32-WROOM ativar o motor
        requests.get(ESP32_WROOM_URL)

        return {"status": "motor activated"}, 200

    return {"status": "no recognition"}, 400

@esp.route('/takephoto')
def takephoto():
    return render_template('takephoto.html')

@esp.route('/recognition_page')
def recognition_page():
    return render_template('recognition.html')  # Novo nome do HTML

@esp.route('/save_photo', methods=['POST'])
def save_photo():
    data = request.json
    nome = data['nome'].strip().replace(" ", "_")  # Remover espaços e evitar problemas
    
    # Remover cabeçalho do base64 e converter para binário
    img_data = base64.b64decode(data['imagem'].split(',')[1])

    # Salvar com o nome fornecido
    with open(f"static/{nome}.png", "wb") as f:
        f.write(img_data)

    return {"mensagem": f"Imagem '{nome}.png' salva com sucesso!"}

################################################
import face_recognition
import time
import os

# Caminho da pasta onde estão as imagens
STATIC_FOLDER = "./static"

# Dicionário para armazenar as codificações faciais
known_faces = {}

# Listar todos os arquivos da pasta static
for filename in os.listdir(STATIC_FOLDER):
    if filename.endswith((".jpg", ".jpeg", ".png")):  # Filtrar apenas imagens
        person_name = os.path.splitext(filename)[0]  # Nome sem extensão
        image_path = os.path.join(STATIC_FOLDER, filename)

        try:
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)
            if encoding:  # Verifica se houve codificação
                known_faces[person_name] = encoding[0]
                print(f"Carregado: {person_name}")
            else:
                print(f"Falha ao carregar {filename}, rosto não encontrado.")

        except Exception as e:
            print(f"Erro ao processar {filename}: {e}")

pause_recognition = False  # Variável para controlar a pausa
pause_start_time = 0  # Tempo de início da pausa

def recognition_generate_frames():
    global pause_recognition, pause_start_time
    cap = cv2.VideoCapture(ESP32_CAM_URL)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Se estiver pausado, espera 3 segundos antes de voltar a reconhecer
        if pause_recognition and time.time() - pause_start_time < 3:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            continue  # Não faz reconhecimento facial neste frame

        # Convertendo frame para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detectando e codificando rostos
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            name = "Desconhecido"
            for person_name, known_encoding in known_faces.items():
                matches = face_recognition.compare_faces([known_encoding], face_encoding)
                if True in matches:
                    name = person_name
                    break

            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if name != "Desconhecido":
                data = {"recognized": True, "name": name}
                requests.post(FLASK_SERVER_URL, json=data)

                # Ativar pausa de reconhecimento
                pause_recognition = True
                pause_start_time = time.time()

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        # Após 3 segundos, desativa a pausa
        if pause_recognition and time.time() - pause_start_time >= 3:
            pause_recognition = False

@esp.route('/video_feed')
def video_feed():
    return Response(recognition_generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')