import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os,json,random
from dotenv import load_dotenv


# Cargar las variables de entorno
load_dotenv()

# Configurar las credenciales de la API de Spotify
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

# Alcance necesario para controlar la reproducción
SCOPE = 'user-read-playback-state,user-modify-playback-state,user-read-currently-playing'

# Autenticar al usuario sin abrir el navegador
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=SCOPE,
                                               open_browser=False))

def get_device_id():
    devices = sp.devices()
    for device in devices['devices']:
        if device['is_active']:
            return device['id']
    return None

def get_url_from_track_name(track_name):
    results = sp.search(q=track_name, limit=1)
    if results['tracks']['items']:
        track_url = results['tracks']['items'][0]['uri']
        return track_url
    return None

def get_current_track_info():
    try:
        current_playback = sp.current_playback()
        if current_playback and current_playback['is_playing']:
            track_info = {
                'name': current_playback['item']['name'],
                'artist': current_playback['item']['artists'][0]['name'],
                'album': current_playback['item']['album']['name'],
                'uri': current_playback['item']['uri']
            }
            return track_info
    except spotipy.exceptions.SpotifyException as e:
        print("Error fetching current track info:", e)
    return None


def get_favourite_song(usuario):
    # Cargar el archivo JSON
    with open('usuarios.json', 'r', encoding='utf-8') as f:
        usuarios = json.load(f)

    # Verificar si el usuario existe en el archivo JSON
    if usuario in usuarios:
        # Obtener la lista de canciones favoritas del usuario
        favoritos = usuarios[usuario].get('favoritos', [])

        if favoritos:
            # Seleccionar una canción aleatoria de la lista de favoritos
            cancion_favorita = random.choice(favoritos)
            track_name = cancion_favorita['track_name']
            track_url = cancion_favorita['track_url']
            return track_url, track_name
        else:
            print(f"El usuario {usuario} no tiene canciones favoritas.")
            return None, None
    else:
        print(f"El usuario {usuario} no existe.")
        return None, None

playing = False

def play_track(track_url, track_name):
    global playing
    playing = True
    device_id = get_device_id()
    if device_id:
        sp.start_playback(device_id=device_id, uris=[track_url])
        print(f"Reproduciendo la canción {track_name}..." )
        return True
    else:
        print("No hay dispositivos activos disponibles. Por favor apre spotify, reproduce una cancion y párala")
        playing = False
        return False

def stop_track():
    global playing
    playing = False
    device_id = get_device_id()
    if device_id:
        sp.pause_playback(device_id=device_id)
        print("Reproducción de música pausada.")
    else:
        print("No hay dispositivos activos disponibles.")

