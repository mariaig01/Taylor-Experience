import cv2
from deepface import DeepFace
from collections import Counter
import time
import threading
import json
import random
from music_player import play_track

# Crear un lock
emotion_analysis_lock = threading.Lock()

def analyze_emotion(frame, emociones):
    try:
        # Adquirir el lock antes de llamar a DeepFace.analyze
        with emotion_analysis_lock:
            face_analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        for analysis in face_analysis:
            if 'dominant_emotion' in analysis:
                emotion = analysis['dominant_emotion']
                emociones.append(emotion)
    except ValueError as e:
        print("Error in analyze_emotion:", e)

def recognize_emotion():
    print("Reconociendo tu emoción...")
    video_capture = cv2.VideoCapture(0)
    emociones = []
    threads = []
    inicio_tiempo = time.time()

    # Inicializar la cámara antes de empezar el bucle
    if not video_capture.isOpened():
        print("Error: Cannot open webcam")
        return None

    # Esperar unos segundos para que la cámara se estabilice
    time.sleep(2)

    # Esperar a que un frame esté listo antes de mostrarlo
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to capture the first frame")
        video_capture.release()
        cv2.destroyAllWindows()
        return None

    # Reducir la frecuencia de análisis para una visualización más fluida
    analysis_interval = 2  # Analizar cada 2 frames
    frame_count = 0

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to capture frame")
                continue

            # Analizar emociones solo en frames específicos
            frame_count += 1
            if frame_count % analysis_interval == 0:
                thread = threading.Thread(target=analyze_emotion, args=(frame, emociones))
                thread.start()
                threads.append(thread)

            # Mostrar el frame
            cv2.imshow('Video', frame)

            # Condiciones de salida
            if time.time() - inicio_tiempo >= 5:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        video_capture.release()
        cv2.destroyAllWindows()

    # Asegurarse de que todos los hilos de análisis han terminado
    for thread in threads:
        thread.join()

    if emociones:
        emocion_mas_frecuente = Counter(emociones).most_common(1)[0][0]
        print("Tu emoción más frecuente es:", emocion_mas_frecuente)
        return emocion_mas_frecuente
    else:
        print("No se detectaron emociones")
        return None

def get_random_track_from_json(json_files):
    all_tracks = []

    # Cargar las canciones de todos los archivos JSON
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            tracks = json.load(f)
        all_tracks.extend(tracks)  # Agregar las listas de canciones a all_tracks

    # Seleccionar una canción aleatoria
    random_track = random.choice(all_tracks)
    track_url = random_track[2]  # La URL de la canción es el tercer elemento de la lista
    track_name = random_track[0]  # El nombre de la canción es el primer elemento de la lista

    return track_url, track_name

def music_recommendation(emotion):
    # Definir los nombres de los archivos JSON que contienen las listas de canciones
    json_files = [
        "taylor_disgusted_tracks.json",
        "taylor_happy_tracks.json",
        "taylor_angry_tracks.json",
        "taylor_scared_tracks.json",
        "taylor_neutral_tracks.json",
        "taylor_sad_tracks.json",
        "taylor_surprised_tracks.json"
    ]

    # Obtener una canción aleatoria de los archivos JSON
    track_url, track_name = get_random_track_from_json(json_files)  # Ahora track_url y track_name son una URL de canción y el nombre de la canción respectivamente

    return track_url, track_name

