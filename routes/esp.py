from flask import Blueprint, request, render_template, Response
import cv2
import requests
import base64
import threading
import face_recognition
import os
import time
from routes.websocket import websocketio

esp = Blueprint("esp", __name__)

ESP32_WROOM_URL = "http://esp32wroom.local/activate" # URL do ESP32-WROOM
ESP32_CAM_URL = "http://esp32cam.local:81/stream" # URL do ESP32-CAM
FLASK_SERVER_URL = "http://192.168.197.89:5000/recognition"

import time

ultimo_reconhecimento = 0  # Tempo da última ativação
COOLDOWN_TIME = 7  # Tempo mínimo entre ativações (segundos)

def generate_frames():
    cap = cv2.VideoCapture(ESP32_CAM_URL)
    global reconhecimento_ativo, ultimo_reconhecimento
    reconhecimento_ativo = False

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = base64.b64encode(buffer).decode('utf-8')

        # Enviar o vídeo sem reconhecimento para todas as páginas
        websocketio.emit('stream_raw', frame_data)

        # Pula o processamento facial em alguns frames para melhorar a performance
        frame_count += 1
        if reconhecimento_ativo and frame_count % 6 != 0:
            continue  # Não faz o reconhecimento facial neste frame

        # Se reconhecimento estiver ativo, processar rostos
        if reconhecimento_ativo:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding in face_encodings:
                name = "Desconhecido"
                for person_name, known_encoding in known_faces.items():
                    matches = face_recognition.compare_faces([known_encoding], face_encoding)
                    if True in matches:
                        name = person_name
                        break

                # Verifica se já passou o tempo mínimo desde a última ativação
                tempo_atual = time.time()
                if (tempo_atual - ultimo_reconhecimento) < COOLDOWN_TIME:
                    continue  # Pula a ativação do motor e reconhecimento repetido

                # Atualiza o tempo da última ativação
                ultimo_reconhecimento = tempo_atual

                if name != "Desconhecido":
                    websocketio.emit('recognized_name', {"name": name})  # Enviar nome via WebSocket
                    requests.get(ESP32_WROOM_URL)  # Ativar o motor

@websocketio.on('start_stream')
def handle_start_stream():
    print("Transmissão iniciada pelo cliente!")
    threading.Thread(target=generate_frames, daemon=True).start()

@websocketio.on('enable_recognition')
def enable_recognition():
    global reconhecimento_ativo
    reconhecimento_ativo = True

@websocketio.on('disable_recognition')
def disable_recognition():
    global reconhecimento_ativo
    reconhecimento_ativo = False

@websocketio.on('connect')
def handle_connect():
    print("Cliente conectado!")  # Isso deve aparecer no terminal do Flask

@esp.route('/recognition', methods=['POST'])
def recognition():
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