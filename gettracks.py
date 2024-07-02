from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

# Cargar las variables de entorno
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.text)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    artists = json_result.get('artists', {}).get('items', [])
    if artists:
        return artists[0]['id']
    return None

def get_albums(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&limit=50"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result.get('items', [])

def get_tracks(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit=50"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result.get('items', [])



def get_all_tracks(token, artist_name):
    artist_id = search_for_artist(token, artist_name)
    if not artist_id:
        print(f"No se encontró el artista: {artist_name}")
        return []

    albums = get_albums(token, artist_id)
    all_tracks = []
    for album in albums:
        album_id = album['id']
        album_name = album['name']
        tracks = get_tracks(token, album_id)
        for track in tracks:
            track_info = {
                'album': album_name,
                'track_name': track['name'],
                'track_url': track['external_urls']['spotify']
            }
            all_tracks.append(track_info)

    return all_tracks



def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    all_tracks = []

    while url:
        result = get(url, headers=headers)
        try:
            result.raise_for_status()  # Verificar si la solicitud fue exitosa
            json_result = result.json()  # Intentar cargar el resultado como JSON
            tracks = json_result.get('items', [])
            all_tracks.extend(tracks)
            url = json_result.get('next')  # Obtener la URL de la siguiente página
        except Exception as e:
            print(f"Error al obtener las canciones de la playlist: {e}")
            return []

    return all_tracks

def load_tracks_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return [] # Devuelve una lista vacía si el archivo no existe

def save_tracks_to_file(tracks, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, ensure_ascii=False, indent=4)

def main():
    # Definir las URLs de las playlists y los nombres de los archivos JSON
    playlists = {
        "taylor_disgusted_tracks.json": "2njVZyl2nmISKI055XrKHA",
        "taylor_happy_tracks.json": "5so3kOc4qYxi7Ux1Dcxqxw",
        "taylor_angry_tracks.json": "1OOARVaoO5OxdNXG8AWaS8",
        "taylor_scared_tracks.json": "2PQLgLAzhmDMmuhVLjneEV",
        "taylor_neutral_tracks.json": "7o5ke3FT9XkWU9MVMofjpr",
        "taylor_sad_tracks.json": "0KLcDVnpjKVTyxpk3LqcVO",
        "taylor_surprised_tracks.json": "5ro21fK4kJv4AlVdFjeNvn"
    }

    token = get_token()
    artist_name = "Taylor Swift"
    for filename, playlist_id in playlists.items():  # Modificar para usar el ID de la playlist
        tracks_playlist = get_playlist_tracks(token, playlist_id)
        all_tracks_playlist = load_tracks_from_file(filename)  # Cargar las canciones existentes
        for track in tracks_playlist:
            track_info_playlist = {
                'track_name': track['track']['name'],
                'artist_name': track['track']['artists'][0]['name'],
                'track_url': track['track']['external_urls']['spotify']
            }
            # Convertir el diccionario track_info en una tupla
            track_tuple = (track_info_playlist['track_name'], track_info_playlist['artist_name'], track_info_playlist['track_url'])
            # Verificar si la canción ya existe
            if track_tuple not in all_tracks_playlist:
                all_tracks_playlist.append(track_tuple)  # Agregar la canción si no existe

        save_tracks_to_file(all_tracks_playlist, filename)
        print(f"Se han guardado {len(all_tracks_playlist)} canciones de la playlist {filename}.")

    all_tracks = get_all_tracks(token, artist_name)
    save_tracks_to_file(all_tracks, "all_taylor_songs.json")
    print(f"Se han guardado {len(all_tracks)} canciones únicas de {artist_name}.")


if __name__ == "__main__":
    main()
