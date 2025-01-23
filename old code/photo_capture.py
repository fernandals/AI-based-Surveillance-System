import time
from picamera2 import Picamera2

# Função para capturar uma foto
def capture_photo():
    picam2 = Picamera2()  # Inicializa a PiCamera2
    picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))
    picam2.start()

    # Captura a imagem
    timestamp = int(time.time())
    image_path = f"image_{timestamp}.jpg"
    picam2.capture_file(image_path)  # Salva a imagem capturada

    picam2.stop()  # Finaliza a captura
    print(f"Image captured: {image_path}")
    return image_path