import json
import os


def add_to_favorites(user, track_name, track_url):
    usuarios_json = 'usuarios.json'
    if os.path.exists(usuarios_json):
        with open(usuarios_json, 'r') as file:
            usuarios = json.load(file)
    else:
        usuarios = {}

    if user not in usuarios:
        usuarios[user] = {"favoritos": []}

    favoritos = usuarios[user].get("favoritos", [])
    favoritos.append({"track_name": track_name, "track_url": track_url})
    usuarios[user]["favoritos"] = favoritos

    with open(usuarios_json, 'w') as file:
        json.dump(usuarios, file, indent=4)

    print(f"Canción '{track_name}' añadida a favoritos de {user}.")

def add_to_no_favorites(user, track_name, track_url):
    usuarios_json = 'usuarios.json'
    if os.path.exists(usuarios_json):
        with open(usuarios_json, 'r') as file:
            usuarios = json.load(file)
    else:
        usuarios = {}

    if user not in usuarios:
        usuarios[user] = {"no_favoritos": []}

    no_favoritos = usuarios[user].get("no_favoritos", [])
    no_favoritos.append({"track_name": track_name, "track_url": track_url})
    usuarios[user]["no_favoritos"] = no_favoritos

    with open(usuarios_json, 'w') as file:
        json.dump(usuarios, file, indent=4)

    print(f"Canción '{track_name}' añadida a no favoritos de {user}.")

def remove_from_favorites(user, track_name):
    usuarios_json = 'usuarios.json'
    if os.path.exists(usuarios_json):
        with open(usuarios_json, 'r') as file:
            usuarios = json.load(file)
    else:
        usuarios = {}

    if user not in usuarios:
        print(f"No se encontraron favoritos para el usuario {user}.")
        return

    favoritos = usuarios[user].get("favoritos", [])
    for i, cancion in enumerate(favoritos):
        if cancion["track_name"] == track_name:
            favoritos.pop(i)
            break

    usuarios[user]["favoritos"] = favoritos

    with open(usuarios_json, 'w') as file:
        json.dump(usuarios, file, indent=4)

    print(f"Canción '{track_name}' eliminada de favoritos de {user}.")


def find_in_non_favorites(user, track_name):
    usuarios_json = 'usuarios.json'
    if os.path.exists(usuarios_json):
        with open(usuarios_json, 'r') as file:
            usuarios = json.load(file)
    else:
        usuarios = {}

    if user not in usuarios:
        print(f"No se encontraron no favoritos para el usuario {user}.")
        return

    no_favoritos = usuarios[user].get("no_favoritos", [])
    for cancion in no_favoritos:
        if cancion["track_name"] == track_name:
            return True

