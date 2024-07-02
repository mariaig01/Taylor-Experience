import os
import cv2
import face_recognition
import json
import time
from facial_registration import RegistroFacial

class ReconocimientoFacial:
    def __init__(self, ruta_directorio):
        self.ruta_directorio = ruta_directorio
        self.usuarios_json = os.path.join(ruta_directorio, "usuarios.json")
        self.cargar_datos_usuarios()

    def cargar_datos_usuarios(self):
        if os.path.exists(self.usuarios_json) and os.path.getsize(self.usuarios_json) > 0:
            with open(self.usuarios_json, 'r') as file:
                usuarios = json.load(file)
                self.encodings_referencia = [face_recognition.face_encodings(face_recognition.load_image_file(os.path.join(self.ruta_directorio, "caras", usuario + ".jpg")))[0] for usuario in usuarios]
                self.nombres_referencia = list(usuarios.keys())
        else:
            self.encodings_referencia = []
            self.nombres_referencia = []

    def reconocer_caras(self):
        camara = cv2.VideoCapture(0)
        inicio_tiempo = time.time()
        usuario_detectado = False
        tiempo_usuario_detectado = None
        usuario_actual = None

        while True:
            ret, imagen_capturada = camara.read()
            imagen_rgb = cv2.cvtColor(imagen_capturada, cv2.COLOR_BGR2RGB)
            ubicaciones_caras = face_recognition.face_locations(imagen_rgb)
            encodings_caras = face_recognition.face_encodings(imagen_rgb, ubicaciones_caras)
            nombres = []

            for encoding in encodings_caras:
                coincidencias = face_recognition.compare_faces(self.encodings_referencia, encoding)
                nombre = "Desconocido"

                if True in coincidencias:
                    indice = coincidencias.index(True)
                    nombre = self.nombres_referencia[indice]

                nombres.append(nombre)

            tiempo_transcurrido = time.time() - inicio_tiempo
            if tiempo_transcurrido > 2 and not usuario_detectado:
                print("No se detectó ningún usuario. Cerrando la cámara.")
                break

            for (top, right, bottom, left), nombre in zip(ubicaciones_caras, nombres):
                cv2.rectangle(imagen_capturada, (left, top), (right, bottom), (162, 0, 255), 2)
                cv2.putText(imagen_capturada, nombre, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (162, 0, 255), 2)

                if nombre != "Desconocido" and not usuario_detectado:
                    print(f"Usuario {nombre} detectado. Iniciando sesión como {nombre}.")
                    usuario_detectado = True
                    tiempo_usuario_detectado = time.time()
                    usuario_actual = nombre

            if usuario_detectado:
                if time.time() - tiempo_usuario_detectado > 3:
                    print("Cerrando la cámara después de detectar el usuario.")
                    break

            cv2.imshow("Reconocimiento Facial", imagen_capturada)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        camara.release()
        cv2.destroyAllWindows()

        if not usuario_detectado:
            usuario_actual = self.registrar_usuario()

        return usuario_actual

    def registrar_usuario(self):
        while True:
            nombre_usuario = input("Ingrese su nombre de usuario: ")
            if nombre_usuario in self.nombres_referencia:
                print("Nombre de usuario ya existe. Por favor, elija otro nombre de usuario.")
                continue
            contraseña = input("Ingrese su contraseña: ")
            RegistroFacial(nombre_usuario, contraseña, self.ruta_directorio)
            self.cargar_datos_usuarios()
            return nombre_usuario  # Devolver el nombre del usuario registrado
