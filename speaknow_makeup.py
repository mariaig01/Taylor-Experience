import cv2
import mediapipe as mp
import numpy as np
from makeup import rgb_to_bgr, draw_lines, apply_shading, apply_lipstick, overlay_image_alpha, get_cheek_points, get_lip_points, get_upper_eyeliner_points, get_upper_eyeliner_triangles_points, get_ear_points, draw_earrings

mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=1)

malla_color_labios = rgb_to_bgr((252, 5, 178))  # Color rojo
malla_color_parpados = rgb_to_bgr((0, 0, 0))
malla_color_eyeliner = rgb_to_bgr((0, 0, 0))

earring_image = cv2.imread('imagenesmakeup/speaknowpendientes3.png', cv2.IMREAD_UNCHANGED)

def apply_speaknow_makeup(frame):
    if frame is None or frame.size == 0:
        return frame

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = faceMesh.process(imgRGB)

    if results.multi_face_landmarks:
        for faceLms in results.multi_face_landmarks:
            lip_points = get_lip_points(faceLms, frame.shape)
            frame = apply_shading(frame, lip_points, malla_color_labios, shade_factor=0.7)

            left_upper_eyeliner_points = get_upper_eyeliner_points(faceLms, frame.shape, eye='left')
            right_upper_eyeliner_points = get_upper_eyeliner_points(faceLms, frame.shape, eye='right')
            left_upper_eyeliner_triangles_points = get_upper_eyeliner_triangles_points(faceLms, frame.shape, eye='left')
            right_upper_eyeliner_triangles_points = get_upper_eyeliner_triangles_points(faceLms, frame.shape, eye='right')

            right_cheek = get_cheek_points(faceLms, frame.shape, side='right')
            left_ear, right_ear = get_ear_points(faceLms, frame.shape)

            draw_lines(frame, left_upper_eyeliner_points, malla_color_eyeliner, thickness=1)
            draw_lines(frame, right_upper_eyeliner_points, malla_color_eyeliner, thickness=1)
            frame = apply_shading(frame, left_upper_eyeliner_triangles_points, malla_color_eyeliner, shade_factor=0.7)
            frame = apply_shading(frame, right_upper_eyeliner_triangles_points, malla_color_eyeliner, shade_factor=0.7)
            frame = apply_shading(frame, lip_points, malla_color_labios, shade_factor=0.7)


            if left_ear and right_ear:
                draw_earrings(frame, left_ear, earring_image)
                draw_earrings(frame, right_ear, earring_image)

    return frame


