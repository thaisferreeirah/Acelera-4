from flask import Flask, request
import requests

app = Flask(__name__)

ESP32_WROOM_URL = "http://192.168.0.5/activate"  # URL do ESP32-WROOM

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
