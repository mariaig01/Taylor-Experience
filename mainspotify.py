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


def load_tracks_from_file(filename="taylor_swift_tracks.json"):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_tracks_to_file(tracks, filename="taylor_swift_tracks.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, ensure_ascii=False, indent=4)

def main():
    token = get_token()
    artist_name = "Taylor Swift"
    artist_id = search_for_artist(token, artist_name)
    if not artist_id:
        print(f"No se encontró el artista: {artist_name}")
        return

    albums = get_albums(token, artist_id)
    all_tracks = load_tracks_from_file()  # Cargar las canciones existentes
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
            # Verificar si la canción ya existe
            if track_info['track_name'] not in all_tracks:
                all_tracks[track_info['track_name']] = track_info  # Agregar la canción si no existe

    save_tracks_to_file(all_tracks)
    print(f"Se han guardado {len(all_tracks)} canciones únicas de {artist_name}.")

    # Imprimir todas las canciones únicas
    for track_name, track_info in all_tracks.items():
        print(f"Álbum: {track_info['album']}, Canción: {track_name}, URL: {track_info['track_url']}")

if __name__ == "__main__":
    main()