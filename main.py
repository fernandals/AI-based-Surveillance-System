from src.config.settings import load_config
from src.camera.camera_manager import CameraManager
from src.audio.audio_manager import AudioManager
from src.detection.object_detector import ObjectDetector
from src.telegram.bot import TelegramBot
import asyncio
import threading

def main():
    # Carregar configurações
    config = load_config()
    
    # Inicializar componentes
    camera = CameraManager()
    audio = AudioManager()
    detector = ObjectDetector()
    bot = TelegramBot(config['TELEGRAM_TOKEN'], config['CHAT_ID'])
    
    # Iniciar sistema
    try:
        # Iniciar threads
        monitoring_thread = threading.Thread(target=audio.start_monitoring)
        monitoring_thread.start()
        
        # Iniciar bot do Telegram
        bot.run()
        
    except KeyboardInterrupt:
        print("Encerrando sistema...")
        
if __name__ == "__main__":
    main()