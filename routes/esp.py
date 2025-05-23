from flask import Flask, request, render_template
import cv2
import requests
import base64

app = Flask(__name__)

#ESP32_WROOM_URL = "http://192.168.0.5/activate"  # URL do ESP32-WROOM em Casa
ESP32_WROOM_URL = "http://192.168.83.136/activate" # Celular

ESP32_CAM_URL = "http://192.168.83.122:81/stream"  # URL da ESP32-CAM

def generate_frames():
    cap = cv2.VideoCapture(ESP32_CAM_URL)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream')
def video_stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
    data = request.json
    nome = data['nome'].strip().replace(" ", "_")  # Remover espaços e evitar problemas
    
    # Remover cabeçalho do base64 e converter para binário
    img_data = base64.b64decode(data['imagem'].split(',')[1])

    # Salvar com o nome fornecido
    with open(f"static/{nome}.png", "wb") as f:
        f.write(img_data)

    return {"mensagem": f"Imagem '{nome}.png' salva com sucesso!"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)