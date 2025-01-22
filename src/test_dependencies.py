import sounddevice as sd
import numpy as np
import cv2
from picamera2 import Picamera2
from datetime import datetime

# Função para capturar áudio e testar o microfone
def testar_microfone():
    sample_rate = 44100  # Taxa de amostragem
    duration = 2  # Duração do teste em segundos
    print("Capturando áudio...")
    
    # Captura áudio do microfone
    audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Espera até o áudio ser capturado

    # Calcular a média dos valores absolutos (simples detecção de volume)
    audio_volume = np.mean(np.abs(audio_data))
    print(f"Volume médio do áudio: {audio_volume}")

    return audio_volume

# Função para capturar imagem e testar a câmera
def testar_camera():
    # Inicializar câmera com Picamera2
    camera = Picamera2()
    camera.configure(camera.create_still_configuration())
    camera.start()

    # Capturar uma imagem
    print("Capturando imagem...")
    imagem = camera.capture_array()  # Captura a imagem como um array NumPy
    print("Imagem capturada com sucesso!")

    # Mostrar a imagem (opcional)
    cv2.imshow("Imagem capturada", imagem)
    cv2.waitKey(0)  # Aguarda até pressionar uma tecla para fechar a janela
    cv2.destroyAllWindows()

# Função principal
def main():
    # Teste do microfone
    volume = testar_microfone()
    print(f"Microfone está funcionando! Volume médio: {volume}")

    # Teste da câmera
    testar_camera()

if __name__ == "__main__":
    main()
