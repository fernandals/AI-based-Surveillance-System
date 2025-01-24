import time
import cv2
import os
import random
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
# from picamera2 import Picamera2  # Mantido para referência, se necessário

# Configurações visuais
MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # vermelho

# Caminho da pasta de imagens
IMAGE_FOLDER = "imgs/"

# Configuração do modelo de detecção
MODEL_PATH = "efficientdet.tflite"
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.ObjectDetectorOptions(base_options=base_options, score_threshold=0.5)
detector = vision.ObjectDetector.create_from_options(options)

def visualize(image, detection_result) -> np.ndarray:
    """Desenha bounding boxes e rótulos na imagem."""
    for detection in detection_result.detections:
        bbox = detection.bounding_box
        start_point = (bbox.origin_x, bbox.origin_y)
        end_point = (bbox.origin_x + bbox.width, bbox.origin_y + bbox.height)
        cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = f"{category_name} ({probability})"
        text_location = (MARGIN + bbox.origin_x, MARGIN + ROW_SIZE + bbox.origin_y)
        
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    return image

def process_random_image():
    """Escolhe aleatoriamente uma imagem da pasta imgs/, processa e salva a versão anotada."""
    if not os.path.exists(IMAGE_FOLDER):
        print(f"⚠️ Pasta '{IMAGE_FOLDER}' não encontrada.")
        return None
    
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("⚠️ Nenhuma imagem encontrada para processamento.")
        return None

    # Escolhe uma imagem aleatoriamente
    random_image = random.choice(image_files)
    image_path = os.path.join(IMAGE_FOLDER, random_image)
    print(f"📷 Imagem selecionada: {random_image}")

    # Carrega a imagem para o modelo
    image = mp.Image.create_from_file(image_path)
    detection_result = detector.detect(image)

    # Processa a imagem
    image_copy = np.copy(image.numpy_view())
    annotated_image = visualize(image_copy, detection_result)

    # Salva a imagem anotada
    annotated_image_path = os.path.join(IMAGE_FOLDER, f"annotated_{random_image}")
    cv2.imwrite(annotated_image_path, annotated_image)

    print(f"✅ Imagem processada e salva em: {annotated_image_path}")
    return annotated_image_path


