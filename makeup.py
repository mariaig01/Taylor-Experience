import cv2
import mediapipe as mp
import numpy as np
from math import e, sqrt, pi
import random

def rgb_to_bgr(color):
    return color[::-1]

def draw_lines(image, points, color, thickness=2):
    for i in range(len(points) - 1):
        cv2.line(image, tuple(points[i]), tuple(points[i + 1]), color, thickness)

def apply_shading(image, points, base_color, shade_factor=0.5):
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], (1, 1, 1))

    shaded = np.zeros_like(image)
    cv2.fillPoly(shaded, [np.array(points, dtype=np.int32)], base_color)

    shaded = cv2.GaussianBlur(shaded, (21, 21), 0)
    result = cv2.addWeighted(image, 1, shaded, shade_factor, 0)
    result = np.where(mask == 0, image, result)

    return result

def apply_lipstick(image, points, base_color, shade_factor=0.5):
    # Crear una máscara para los labios
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], (1, 1, 1))

    # Crear una imagen con el color base
    colored = np.zeros_like(image)
    cv2.fillPoly(colored, [np.array(points, dtype=np.int32)], base_color)

    # Crear una máscara de sombreado
    shaded = np.zeros_like(image)
    cv2.fillPoly(shaded, [np.array(points, dtype=np.int32)], base_color)

    # Aplicar sombreado
    shaded = cv2.GaussianBlur(shaded, (21, 21), 0)
    result = cv2.addWeighted(image, 1, shaded, shade_factor, 0)
    result = np.where(mask == 0, image, result)

    # Aplicar brillo
    brightness_mask = np.zeros_like(image)
    cv2.fillPoly(brightness_mask, [np.array(points, dtype=np.int32)], (255, 255, 255))
    brightness_mask = cv2.GaussianBlur(brightness_mask, (21, 21), 0)
    result = cv2.addWeighted(result, 1, brightness_mask, 0.3, 0)

    # Mejorar el contorno de los labios
    contours = np.zeros_like(image)
    cv2.polylines(contours, [np.array(points, dtype=np.int32)], True, (0, 0, 0), 1, cv2.LINE_AA)
    contours = cv2.GaussianBlur(contours, (3, 3), 0)
    result = cv2.addWeighted(result, 1, contours, 0.5, 0)

    # Ajustar la saturación y brillo para un efecto más realista
    hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 50)  # Incrementar la saturación
    v = cv2.add(v, -30)  # Reducir el brillo
    final_hsv = cv2.merge((h, s, v))
    result = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    return result



def draw_glasses(frame, faceLms, glasses_image_path):
    glasses_image = cv2.imread(glasses_image_path, cv2.IMREAD_UNCHANGED)

    glasses_points = get_glasses_points(faceLms, frame.shape)

    # Calcular el centro de los puntos de las gafas
    glasses_center = np.mean(glasses_points, axis=0).astype(int)

    # Calcular la posición superior izquierda de las gafas
    glasses_top_left = (glasses_center[0] - glasses_image.shape[1] // 2, glasses_center[1] - glasses_image.shape[0] // 2)

    # Superponer las gafas en el marco del video
    overlay_image_alpha(frame, glasses_image[:, :, :3], glasses_top_left, glasses_image[:, :, 3])

    return frame



def get_lip_points(face_landmarks, image_shape):
    indices = [
        61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95,
        78, 61, 78, 61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 308, 415, 310, 311, 312, 13, 82, 81,
        80, 191, 78, 61
    ]
    return [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in indices
    ]

def get_eye_points(face_landmarks, image_shape, eye='left'):
    if eye == 'left':
        indices = [
            159, 158, 157, 173, 133, 190, 56, 28, 29, 30, 247, 226, 130, 33, 246, 161, 160
        ]
    else:
        indices = [
            386, 387, 388, 466, 263, 359, 446, 467, 260, 259, 257, 286, 414, 463, 398, 384, 385
        ]
    return [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in indices
    ]

def get_eyeliner_points(face_landmarks, image_shape, eye='left'):
    if eye == 'left':
        indices = [
            33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7, 33
        ]
    else:
        indices = [
            463, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382, 463
        ]
    return [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in indices
    ]

def get_upper_eyeliner_points(face_landmarks, image_shape, eye='left'):
    if eye == 'left':
        indices = [
            133,173,157,158,159,160,161,246,
        ]
    else:
        indices = [
            463, 398, 384, 385, 386, 387, 388, 466, 263,
        ]
    return [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in indices
    ]

def get_upper_eyeliner_triangles_points(face_landmarks, image_shape, eye='left'):
    if eye == 'left':
        indices = [
            33, 246,247,33
        ]
    else:
        indices = [
            263,467,466,263
        ]
    return [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in indices
    ]

def get_ear_points(face_landmarks, image_shape):
    left_ear_indices = [ 132]
    right_ear_indices = [ 433]
    left_ear = [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in left_ear_indices
    ]
    right_ear = [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in right_ear_indices
    ]
    return left_ear, right_ear

def draw_earrings(image, ear_points, earring_image):
    for i, point in enumerate(ear_points):
        if point[0] < 0 or point[1] < 0 or point[0] >= image.shape[1] or point[1] >= image.shape[0]:
            continue  # Saltar puntos fuera del marco

        # Ajustar el pendiente izquierdo con un desplazamiento
        if i == 0:  # Índice 0 corresponde al pendiente izquierdo
            adjusted_point = (point[0] - 10, point[1] + 10)  # Ajustar según sea necesario
        else:
            adjusted_point = point

        overlay_image_alpha(image, earring_image[:, :, :3], tuple(adjusted_point), earring_image[:, :, 3])



def get_cheek_points(face_landmarks, image_shape, side='left'):
    if side == 'left':
        indices = [234, 93, 132]
    else:
        indices = [280, 346, 352]
    return [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in indices
    ]

def get_glasses_points(face_landmarks, image_shape):
    indices = [35,265]
    return [
        [int(face_landmarks.landmark[i].x * image_shape[1]), int(face_landmarks.landmark[i].y * image_shape[0])]
        for i in indices
    ]


def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    x, y = pos

    # Rango de la imagen
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Rango de la imagen superpuesta
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Verificar si el rango es válido
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return img

    # Aplicar la máscara de transparencia
    img_crop = img[y1:y2, x1:x2]
    img_overlay_crop = img_overlay[y1o:y2o, x1o:x2o]
    alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis] / 255.0

    img_crop[:] = (1.0 - alpha) * img_crop + alpha * img_overlay_crop

    return img

