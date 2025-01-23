import pyaudio
import wave
import time
import os
from audio_classifier import classify_audio
from photo_capture import capture_photo
from datetime import datetime

from mediapipe.tasks import python
from mediapipe.tasks.python.components import containers
from mediapipe.tasks.python import audio

from bot import Bot  # Importando a classe Bot do arquivo bot.py

# Configurações de gravação de áudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
OUTPUT_FOLDER = "recordings"
OUTPUT_FILENAME_TEMPLATE = "recording_{timestamp}.wav"

bot_token = '7687834705:AAGuPsA62nbdCJnz4TfT5KAoEhyofcNm0z8'
chat_id = '1016810984'
bot = Bot(token=bot_token, chat_id=chat_id)

# Cria a pasta de gravações se não existir
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Inicializa o PyAudio
p = pyaudio.PyAudio()

# Abre o stream de áudio
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Configuração do classificador
base_options = python.BaseOptions(model_asset_path='yamnet.tflite')
options = audio.AudioClassifierOptions(base_options=base_options, max_results=4)

def send_alert(bot, message, image_path):
    bot.send_message(message)
    bot.send_photo(image_path)

#test_message = "Mensagem de teste do bot para verificar se está funcionando."
#bot.send_message(test_message)

print("Inicio")

def main():
    print("Recording in progress... Press Ctrl+C to stop.")
    try:
        with audio.AudioClassifier.create_from_options(options) as classifier:
            while True:
                frames = []
                print(f"Recording for {RECORD_SECONDS} seconds...")
                
                # Capture o áudio
                for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)

                # Gerar o nome do arquivo usando o timestamp
                timestamp = int(time.time())
                output_filename = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME_TEMPLATE.format(timestamp=timestamp))

                # Salvar o áudio gravado em um arquivo WAV
                with wave.open(output_filename, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))

                print(f"Audio recorded and saved as {output_filename}")

                # Classificar o áudio gravado
                audio_file, detected_sound = classify_audio(output_filename, classifier)

                if audio_file and detected_sound:
                    print(f"Audio Path: {audio_file}")
                    print(f"Detected Sound: {detected_sound}")

                    # Captura a foto
                    #image_path = capture_photo()
                    image_path = 'image.jpg' 
                    print(f"Image Path: {image_path}")

                    agora = datetime.now()
                    mensagem = f"""🚨 ALERTA DE SEGURANÇA 🚨
                                Data/Hora: {agora.strftime('%d/%m/%Y %H:%M:%S')}
                                Som Detectado: {detected_sound}
                                """
                
                    bot.send_alert(mensagem, image_path)

                # Pausar 1 segundo antes de iniciar uma nova gravação
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nRecording interrupted by the user.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
