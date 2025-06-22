import base64
import os
import threading
import time

import cv2
import face_recognition
import requests

import config
from flask import Blueprint, request, render_template
from routes.websocket import websocketio

esp = Blueprint("esp", __name__)

ESP32_WROOM_URL = "http://esp32wroom.local/activate"
ESP32_CAM_URL = "http://esp32cam.local:81/stream"
FLASK_SERVER_URL = config.FLASK_URL

@esp.route('/takephoto')
def takephoto():
    return render_template('takephoto.html')

@esp.route('/reconhecimentoDisplay')
def reconhecimentoDisplay():
    return render_template('reconhecimentoDisplay.html')  # Novo nome do HTML

ultimo_reconhecimento = 0  # Tempo da última ativação
COOLDOWN_TIME = 3  # Tempo mínimo entre ativações (segundos)

# Função para permitir exibir a captura do ESP32Cam em mais de uma página e para fazer o reconhecimento facial
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
        if reconhecimento_ativo and frame_count % 12 != 0:
            continue

        # Se reconhecimento estiver ativo, processar rostos
        if reconhecimento_ativo:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding in face_encodings:
                id = "Desconhecido"
                for person_id, known_encoding in known_faces.items():
                    matches = face_recognition.compare_faces([known_encoding], face_encoding)
                    if True in matches:
                        id = person_id
                        break

                # Verifica se já passou o tempo mínimo desde a última ativação
                tempo_atual = time.time()
                if (tempo_atual - ultimo_reconhecimento) < COOLDOWN_TIME:
                    continue  # Pula a ativação do motor e reconhecimento repetido

                # Atualiza o tempo da última ativação
                ultimo_reconhecimento = tempo_atual

                if id != "Desconhecido":
                    response = requests.get(f"{FLASK_SERVER_URL}/membrosrectest/{id}")

                    if response.status_code == 200:
                        try:
                            data = response.json()  # Converte a resposta para um dicionário
                            name = data[0]["name"]  # Extrai o campo "name" corretamente
                            websocketio.emit('recognized_name', {"name": name})  # Enviar nome via WebSocket

                            dataLog = {"id": id}
                            responseLog = requests.post(f"{FLASK_SERVER_URL}/reclogtest", data=dataLog)
                            print(responseLog)
                            #requests.get(ESP32_WROOM_URL)  # Ativar o motor
                        except requests.exceptions.JSONDecodeError:
                            print("Erro ao decodificar JSON. Resposta recebida:")
                            print(response.text)
                    else:
                        print("Erro ao buscar o membro:", response.text)

# Inicia a transmissão
@websocketio.on('start_stream')
def handle_start_stream():
    print("Transmissão iniciada pelo cliente!")
    threading.Thread(target=generate_frames, daemon=True).start()

# Habilita o reconhecimento facial
@websocketio.on('enable_recognition')
def enable_recognition():
    global reconhecimento_ativo
    reconhecimento_ativo = True

# Desabilita o queconhecimento facial
@websocketio.on('disable_recognition')
def disable_recognition():
    global reconhecimento_ativo
    reconhecimento_ativo = False

# Conecta
@websocketio.on('connect')
def handle_connect():
    print("Cliente conectado!")  # Isso deve aparecer no terminal do Flask

# Salva a foto
@esp.route('/save_photo', methods=['POST'])
def save_photo():
    data = request.json
    nome = data['nome'].strip().replace(" ", "_")  # Remover espaços e evitar problemas
    
    # Remover cabeçalho do base64 e converter para binário
    img_data = base64.b64decode(data['imagem'].split(',')[1])

    # Salvar com o nome fornecido
    with open(f"static/images/{nome}.png", "wb") as f:
        f.write(img_data)

    return {"mensagem": f"Imagem '{nome}.png' salva com sucesso!"}


STATIC_FOLDER = "./static/images" # Caminho da pasta onde estão as imagens
known_faces = {} # Dicionário para armazenar as codificações faciais

# Carrega todas as fotos da pasta static
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


# Abrir portão manualmente
@esp.route('/open_gate')
def open_gate():
    requests.get(ESP32_WROOM_URL)