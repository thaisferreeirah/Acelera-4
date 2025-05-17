import cv2
import face_recognition
import time
import requests

FLASK_SERVER_URL = "http://192.168.0.3:5000/recognition"

# Carregar imagens de referência
known_faces = {
    "Johnny": face_recognition.face_encodings(face_recognition.load_image_file("./static/johnny.jpg"))[0],
    "Tom Hanks": face_recognition.face_encodings(face_recognition.load_image_file("./static/tom_hanks.jpeg"))[0],
}

print("Codificações carregadas:", known_faces)

# Capturar vídeo da ESP32-CAM
esp32_url = "http://192.168.0.4:81/stream"
cap = cv2.VideoCapture(esp32_url)

welcome_message = None  # Variável para armazenar o nome reconhecido
message_start_time = 0  # Tempo em que a mensagem começou a ser exibida
pause_recognition = False  # Flag para pausar reconhecimento facial

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Se não estiver pausado, realizar reconhecimento facial
    if not pause_recognition:
        # Converter o frame para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detectar e codificar rostos no frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        print("Rostos detectados:", len(face_encodings))

        for face_encoding, face_location in zip(face_encodings, face_locations):
            name = "Desconhecido"

            # Comparar com cada rosto conhecido
            for person_name, known_encoding in known_faces.items():
                matches = face_recognition.compare_faces([known_encoding], face_encoding)
                if True in matches:
                    name = person_name
                    break

            # Desenhar retângulo e exibir nome
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Se reconhecido, definir mensagem e ativar pausa
            if name != "Desconhecido":
                data = {"recognized": True, "name": name}
                requests.post(FLASK_SERVER_URL, json=data)
                welcome_message = f"{name}"
                message_start_time = time.time()  # Salvar tempo inicial
                pause_recognition = True  # Pausar reconhecimento

    # Exibir mensagem de boas-vindas em local fixo por 5 segundos
    if pause_recognition and time.time() - message_start_time < 5:
        cv2.putText(frame, welcome_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        pause_recognition = False  # Liberar reconhecimento após 5 segundos
        welcome_message = None  # Remover mensagem

    cv2.imshow("Reconhecimento Facial", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
