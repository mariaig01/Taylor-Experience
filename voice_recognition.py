import json
import speech_recognition as sr
from music_player import play_track
from unidecode import unidecode

def save_tracks_to_file(tracks, filename="taylor_swift_tracks.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, ensure_ascii=False, indent=4)

def load_tracks_from_file(filename="all_taylor_songs.json"):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Escuchando comando...")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)  # Aumenta el tiempo de espera y límite de frase
            command = recognizer.recognize_google(audio, language='es-ES')
            return command.lower()
        except sr.WaitTimeoutError:
            print("Tiempo de espera terminado.")
            return None
        except sr.UnknownValueError:
            print("No se puede entender el audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return SystemExit



#Funcion que busca en all_taylor_songs la cancion que se ha solicitado por reconocimiento de voz
def load_tracks_from_file():
    # Asegúrate de que el archivo 'songs.json' está en el directorio correcto o ajusta la ruta del archivo según sea necesario
    with open('all_taylor_songs.json', 'r') as file:
        return json.load(file)

def search_for_song(song_name):
    all_songs = load_tracks_from_file()
    for song in all_songs:
        if song_name.lower() in song['track_name'].lower():
            return song['track_url']  # Usa la clave correcta según tu estructura de JSON
    return None


