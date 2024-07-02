import cv2
import threading
from queue import Queue
import speech_recognition as sr
import sys
from facial_recognition import ReconocimientoFacial
from music_recommendation import music_recommendation, recognize_emotion
from music_player import play_track, stop_track, get_favourite_song
from fearless_makeup import apply_fearless_makeup
from speaknow_makeup import apply_speaknow_makeup
from voice_recognition import recognize_speech, search_for_song
from red_makeup import apply_red_makeup
from lover_makeup import apply_lover_makeup
from evermore_makeup import apply_evermore_makeup
from users import add_to_favorites, add_to_no_favorites, find_in_non_favorites

# Variables globales para controlar los hilos
recognizing = True
application_running = True
current_user = None  # Variable para almacenar el usuario actual
enter = True

# Función para manejar el registro
def handle_registration():
    global current_user
    ruta_directorio = '/home/maig/PycharmProjects/CUIA'
    reconocimiento = ReconocimientoFacial(ruta_directorio)
    current_user = reconocimiento.reconocer_caras()
    if not current_user:
        print("Registrando nuevo usuario...")
        current_user = reconocimiento.registrar_usuario()

def handle_user_input(current_makeup):
    global recognizing, application_running
    while recognizing and application_running:
        command = recognize_speech()
        if command in ["speak now", "fearless", "red makeup", "lover", "evermore", "stop"]:
            current_makeup.put(command)
        elif command in ["cerrar sesion maquillaje", "cerrar sesión maquillaje", "cerrar reproductor", "cerrar sesión", "cerrar sesion", "añadir a favoritos", "añadir a no favoritos", "reproducir de favoritos", "nueva canción"]:
            current_makeup.put(command)
            if command == "cerrar sesión":
                recognizing = False
                application_running = False
                sys.exit()  # Cerrar la aplicación completamente
        elif command in ["reproducir música", "aplicar maquillaje", "cerrar sesión"]:
            print("Comando reconocido:", command)
        else:
            print("Comando no reconocido: ", command)  # Manejar comandos no reconocidos

def no_makeup(frame):
    return frame

# Aplicación principal
handle_registration()

# Crear el hilo de entrada una vez
current_makeup = Queue()
current_makeup.put(None)
input_thread = threading.Thread(target=handle_user_input, args=(current_makeup,))
input_thread.start()

# Tablero de usuario
def user_dashboard():
    global recognizing, application_running, enter
    music_thread = None
    makeup_functions = [no_makeup, apply_speaknow_makeup, apply_fearless_makeup, apply_red_makeup, apply_lover_makeup, apply_evermore_makeup]
    current_makeup_index = 0
    current_makeup_func = makeup_functions[current_makeup_index]

    while recognizing and application_running:
        print("Usuario actual:", current_user)
        print("Escoge una opción:")
        print("1. Reproducir música")
        print("2. Aplicar maquillaje")
        print("3. Cerrar sesión")
        choice = recognize_speech()
        while choice not in ["1", "reproducir música", "2", "aplicar maquillaje", "3", "cerrar sesión"]:
            print("Opción no válida. Intenta de nuevo.")
            choice = recognize_speech()

        if not application_running:
            break

        if "1" in choice or "reproducir música" in choice:
            recognizing = False  # Detener el reconocimiento de voz
            while application_running:
                print("Reconociendo emoción...")
                emotion = recognize_emotion()
                recognizing = False
                track_url, track_name = music_recommendation(emotion)
                while find_in_non_favorites(current_user, track_name):
                    print("Cancion encontrada en no favoritos.")
                    print("Recomendando otra cancion.")
                    emotion = recognize_emotion()
                    track_url, track_name = music_recommendation(emotion)

                while not play_track(track_url, track_name):
                    print("Dispositivos no vinculados...")
                    emotion = recognize_emotion()
                    track_url, track_name = music_recommendation(emotion)

                if music_thread is None or not music_thread.is_alive():  # Solo crear un nuevo hilo si el anterior ha terminado
                    playing = True
                    music_thread = threading.Thread(target=play_track, args=(track_url, track_name))
                    music_thread.start()
                    music_thread.join()  # Esperar a que la música termine
                    enter = True
                    playing = False

                if not track_url:
                    print("Canción no encontrada, pruebe de nuevo.")
                    continue  # Volver a detectar la emoción y reproducir una nueva canción

                while application_running:
                    if enter:
                        print("Presiona enter para parar la música.")
                        input()  # Espera hasta que el usuario presione Enter
                        stop_track()

                    print("Canción parada. Que quiere hacer ahora?")
                    command = None
                    while not command:
                        command = recognize_speech()

                    if not application_running:
                        break
                    if command in ["nueva canción", "new song"]:
                        break  # Salir al bucle principal para detectar una nueva emoción
                    elif command in ["añadir a favoritos"]:
                        add_to_favorites(current_user, track_name, track_url)
                        print("Cancion añadida a favoritos.")
                        print(f"{track_name} añadida a favoritos.")
                        enter = False
                    elif command in ["añadir a no favoritos"]:

                        add_to_no_favorites(current_user, track_name, track_url)
                        print("Canción añadida a no favoritos.")
                        print(f"{track_name} añadida a no favoritos.")
                        enter = False
                    elif command in ["reproducir de favoritos"]:
                        track_url,track_name=get_favourite_song(current_user)
                        playing = True
                        music_thread = threading.Thread(target=play_track, args=(track_url, command))
                        music_thread.start()
                        music_thread.join()
                        playing = False
                        enter = True

                    elif "cerrar reproductor" in command:
                        break  # Volver al menú principal
                    elif "cerrar sesión" in command:
                        recognizing = False
                        application_running = False
                        sys.exit()  # Cerrar la aplicación completamente
                    else:  # Buscar canción por nombre
                        track_url = search_for_song(command)
                        if track_url:
                            track_name = command
                            if find_in_non_favorites(current_user, command):
                                print("Canción encontrada en no favoritos.")
                                print("No se puede reproducir esta canción.")
                                enter = False
                                continue
                            else:
                                playing = True
                                music_thread = threading.Thread(target=play_track, args=(track_url, command))
                                music_thread.start()
                                music_thread.join()
                                playing = False
                                enter = True
                        else:
                            print("Canción no encontrada, please try another command or song.")
                            enter = False
                        continue
                if not application_running or "cerrar reproductor" in command:
                    break
            recognizing = True  # Reiniciar el reconocimiento de voz
            if application_running:
                input_thread = threading.Thread(target=handle_user_input, args=(current_makeup,))
                input_thread.start()

        elif "aplicar maquillaje" in choice or "dos" in choice:
            print("Comenzado la aplicación de maquillaje...")
            cap = cv2.VideoCapture(0)
            while application_running:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("Fallo al capturar imagen")
                    continue

                # Verificar si se ha dicho "stop"
                if not current_makeup.empty():
                    makeup = current_makeup.get()
                    if makeup in ["cerrar sesion maquillaje", "cerrar sesión maquillaje", "cerrar sesión"]:
                        recognizing = False
                        application_running = False
                        cap.release()
                        cv2.destroyAllWindows()
                        if makeup == "cerrar sesion maquillaje" or makeup == "cerrar sesión maquillaje":
                            recognizing = True  # Reiniciar el reconocimiento de voz
                            application_running = True  # Reiniciar la aplicación
                            break  # Volver al menú principal
                        sys.exit()  # Cerrar la aplicación completamente

                    if makeup == "speak now":
                        current_makeup_func = apply_speaknow_makeup
                    elif makeup == "fearless":
                        current_makeup_func = apply_fearless_makeup
                    elif makeup == "red makeup":
                        current_makeup_func = apply_red_makeup
                    elif makeup == "lover":
                        current_makeup_func = apply_lover_makeup
                    elif makeup == "evermore":
                        current_makeup_func = apply_evermore_makeup
                    elif makeup == "cerrar sesion maquillaje" or makeup == "cerrar sesión maquillaje":
                        print("Sesión de maquillaje terminada.")
                        current_makeup_func = no_makeup

                        cap.release()
                        cv2.destroyAllWindows()

                        break  # Volver al menú principal

                frame = current_makeup_func(frame)  # Usar función asignada para procesar el frame
                cv2.imshow("Makeup Application", frame)

                # Presionar 'c' para cambiar de maquillaje
                if cv2.waitKey(1) & 0xFF == ord('c'):
                    current_makeup_index = (current_makeup_index + 1) % len(makeup_functions)
                    current_makeup_func = makeup_functions[current_makeup_index]

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            print("Sesión de maquillaje terminada.")

        elif "cerrar sesión" in choice or "tres" in choice:
            print("Cerrando sesión...")
            recognizing = False
            application_running = False
            sys.exit()  # Cerrar la aplicación completamente
        else:
            print("Opción no válida.Pruebe de nuevo.")

user_dashboard()

