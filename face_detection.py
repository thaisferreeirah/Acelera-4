import cv2
import face_recognition

# Carregar uma imagem de referência (banco de dados)
known_image = face_recognition.load_image_file("johnny_foto.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]  # Extraindo características faciais

# Capturar vídeo da ESP32-CAM
esp32_url = "http://192.168.83.122:81/stream"
cap = cv2.VideoCapture(esp32_url)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Converter o frame para RGB (necessário para face_recognition)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detectar e codificar rostos no frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        # Comparar com o rosto conhecido
        matches = face_recognition.compare_faces([known_encoding], face_encoding)
        name = "Desconhecido"

        if True in matches:
            name = "Pessoa Conhecida"

        # Desenhar um retângulo ao redor do rosto e mostrar o nome
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Reconhecimento Facial", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()