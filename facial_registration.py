import os
import cv2
import json

class RegistroFacial:
    def __init__(self, nombre_usuario, contraseña, ruta_directorio):
        self.nombre_usuario = nombre_usuario
        self.contraseña = contraseña
        self.ruta_directorio = ruta_directorio
        self.tomar_foto()

    def tomar_foto(self):
        captura = cv2.VideoCapture(0)
        print("Presiona 'F' para tomar la foto.")
        imagen_limpia = None

        while True:
            ret, imagen = captura.read()
            if not ret:
                print("Error al capturar la imagen")
                break
            imagen_mostrar = imagen.copy()
            cv2.putText(imagen_mostrar, "Presiona 'F' para tomar la foto", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
            cv2.imshow('Camara', imagen_mostrar)
            if cv2.waitKey(1) & 0xFF == ord('f'):
                imagen_limpia = imagen.copy()
                nombre_imagen = os.path.join(self.ruta_directorio, "caras", self.nombre_usuario + ".jpg")
                cv2.imwrite(nombre_imagen, imagen_limpia)
                print("¡Foto guardada correctamente!")
                usuarios = {}
                if os.path.exists(os.path.join(self.ruta_directorio, "usuarios.json")):
                    with open(os.path.join(self.ruta_directorio, "usuarios.json"), 'r') as file:
                        usuarios = json.load(file)

                usuarios[self.nombre_usuario] = {"contraseña": self.contraseña}
                with open(os.path.join(self.ruta_directorio, "usuarios.json"), 'w') as file:
                    json.dump(usuarios, file)
                break

        captura.release()
        cv2.destroyAllWindows()

