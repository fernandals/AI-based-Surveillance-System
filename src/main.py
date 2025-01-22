import sounddevice as sd
import numpy as np
import cv2
from datetime import datetime
import tensorflow as tf
import tensorflow_hub as hub
import json
import requests
from PIL import Image
import io
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
import threading

from picamera2 import Picamera2
from picamera2.utils import Preview

class SistemaVigilancia:
    def __init__(self, token_telegram, chat_id):
        # Configurações do Telegram
        self.token = token_telegram
        self.chat_id = chat_id
        self.bot = Bot(token=token_telegram)
        
        # Configurações de áudio
        self.sample_rate = 44100
        self.block_duration = 3
        self.block_size = int(self.sample_rate * self.block_duration)
        self.sensibilidade_mic = 0.1  # Novo: configurável
        
        '''
        # Inicializar câmera
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise RuntimeError("Erro ao acessar a câmera!")
        '''

        # Inicializar a câmera com Picamera2
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_still_configuration())
        self.camera.start()

        # Carregar modelos
        self.audio_model = hub.load('https://tfhub.dev/google/yamnet/1')
        self.detector = hub.load('https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1')
        
        # Lista de sons suspeitos - agora configurável
        self.sons_suspeitos = set(['quebra', 'grito', 'explosao', 'vidro'])
        
        # Flag para controle do monitoramento
        self.monitoramento_ativo = True
        
        
    def classificar_som(audio_path):
      # Carregar e processar áudio
      audio, sr = librosa.load(audio_path, sr=16000)
      scores, embeddings, spectrogram = yamnet(audio)

      # Identificar som mais provável
      classe_som = np.argmax(scores, axis=1)
      return classe_som

    def classificar_audio(self, audio_data):
        audio_features = np.mean(np.abs(audio_data))
        if audio_features > self.sensibilidade_mic:
            return 'som_suspeito'
        return 'som_normal'
    
    def capturar_imagem(self):
      '''
      ret, frame = self.camera.read()
      if ret:
          return frame
      return None
      '''
      
      frame = self.camera.capture_array()  # Captura como um array numpy
      return frame
    
    def detectar_objetos(self, imagem):
      img = cv2.resize(imagem, (512, 512))
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      img = tf.convert_to_tensor(img, dtype=tf.uint8)
      img = tf.expand_dims(img, axis=0)

      detections = self.detector(img)  # O modelo retorna um dicionário

      boxes = detections['detection_boxes']
      scores = detections['detection_scores']
      classes = detections['detection_classes']
      num_detections = int(detections['num_detections'])

      objetos_detectados = []
      for i in range(num_detections):
          if scores[i] > 0.5:
              objetos_detectados.append({
                  'classe': int(classes[i]),
                  'confianca': float(scores[i])
              })

      return objetos_detectados


    async def enviar_alerta(self, tipo_som, objetos, imagem):
        agora = datetime.now()
        
        # Converter imagem para bytes
        _, img_encoded = cv2.imencode('.jpg', imagem)
        img_bytes = io.BytesIO(img_encoded.tobytes())
        
        # Criar mensagem
        mensagem = f"""🚨 ALERTA DE SEGURANÇA 🚨
          Data/Hora: {agora.strftime('%d/%m/%Y %H:%M:%S')}
          Som Detectado: {tipo_som}
          Objetos Detectados: {', '.join([f"Objeto {obj['classe']} ({obj['confianca']:.2f})" for obj in objetos])}
          """
        
        # Enviar mensagem e foto pelo Telegram
        await self.bot.send_message(chat_id=self.chat_id, text=mensagem)
        img_bytes.seek(0)
        await self.bot.send_photo(chat_id=self.chat_id, photo=img_bytes)
    
    def monitorar(self):
      """Função principal de monitoramento"""
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)

      async def processar_alerta(tipo_som, imagem):
          if imagem is not None:
              objetos = self.detectar_objetos(imagem)
              await self.enviar_alerta(tipo_som, objetos, imagem)

      async def main_monitoramento():
          try:
              def callback(indata, frames, time, status):
                  if status:
                      print('Erro:', status)
                      return

                  if not self.monitoramento_ativo:
                      return

                  tipo_som = self.classificar_audio(indata)

                  if tipo_som in self.sons_suspeitos:
                      imagem = self.capturar_imagem()
                      loop.call_soon_threadsafe(asyncio.create_task, processar_alerta(tipo_som, imagem))

              with sd.InputStream(callback=callback, channels=1, samplerate=self.sample_rate, blocksize=self.block_size):
                  print("Monitoramento iniciado. Pressione Ctrl+C para parar.")
                  while True:
                      sd.sleep(1000)

          except KeyboardInterrupt:
              print("\nMonitoramento interrompido pelo usuário")
          finally:
              self.camera.release()

      loop.run_until_complete(main_monitoramento())


class TelegramBot:
    def __init__(self, token, sistema_vigilancia):
        self.application = Application.builder().token(token).build()
        self.sistema = sistema_vigilancia
        
        # Registrar handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.status))
        self.application.add_handler(CommandHandler("sensibilidade", self.set_sensibilidade))
        self.application.add_handler(CommandHandler("sons", self.listar_sons))
        self.application.add_handler(CommandHandler("adicionar_som", self.adicionar_som))
        self.application.add_handler(CommandHandler("remover_som", self.remover_som))
        self.application.add_handler(CommandHandler("pausar", self.pausar))
        self.application.add_handler(CommandHandler("continuar", self.continuar))
        self.application.add_handler(CommandHandler("ajuda", self.ajuda))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🎥 Sistema de Vigilância iniciado!\n\n"
            "Comandos disponíveis:\n"
            "/status - Ver configurações atuais\n"
            "/sensibilidade [valor] - Ajustar sensibilidade do microfone\n"
            "/sons - Listar sons monitorados\n"
            "/adicionar_som [som] - Adicionar som à lista\n"
            "/remover_som [som] - Remover som da lista\n"
            "/pausar - Pausar monitoramento\n"
            "/continuar - Retomar monitoramento\n"
            "/ajuda - Ver esta mensagem"
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        status = f"""📊 Status do Sistema:
        
Monitoramento: {'Ativo' if self.sistema.monitoramento_ativo else 'Pausado'}
Sensibilidade: {self.sistema.sensibilidade_mic}
Sons monitorados: {', '.join(self.sistema.sons_suspeitos)}"""
        await update.message.reply_text(status)
    
    async def set_sensibilidade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            valor = float(context.args[0])
            if 0 < valor <= 1:
                self.sistema.sensibilidade_mic = valor
                await update.message.reply_text(f"✅ Sensibilidade ajustada para {valor}")
            else:
                await update.message.reply_text("❌ Valor deve estar entre 0 e 1")
        except (IndexError, ValueError):
            await update.message.reply_text("❌ Use: /sensibilidade [valor entre 0 e 1]")
    
    async def listar_sons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sons = ', '.join(self.sistema.sons_suspeitos)
        await update.message.reply_text(f"🔊 Sons monitorados:\n{sons}")
    
    async def adicionar_som(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            som = context.args[0].lower()
            self.sistema.sons_suspeitos.add(som)
            await update.message.reply_text(f"✅ Som '{som}' adicionado à lista")
        except IndexError:
            await update.message.reply_text("❌ Use: /adicionar_som [nome do som]")
    
    async def remover_som(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            som = context.args[0].lower()
            if som in self.sistema.sons_suspeitos:
                self.sistema.sons_suspeitos.remove(som)
                await update.message.reply_text(f"✅ Som '{som}' removido da lista")
            else:
                await update.message.reply_text("❌ Som não encontrado na lista")
        except IndexError:
            await update.message.reply_text("❌ Use: /remover_som [nome do som]")
    
    async def pausar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.sistema.monitoramento_ativo = False
        await update.message.reply_text("⏸ Monitoramento pausado")
    
    async def continuar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.sistema.monitoramento_ativo = True
        await update.message.reply_text("▶️ Monitoramento retomado")
    
    async def ajuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start(update, context)
    
    def iniciar(self):
        self.application.run_polling()

def main():
    # Configurações do Telegram (substitua com seus valores)
    TOKEN = "7687834705:AAGuPsA62nbdCJnz4TfT5KAoEhyofcNm0z8"
    CHAT_ID = "1016810984"
    
    # Inicializar sistema de vigilância
    sistema = SistemaVigilancia(TOKEN, CHAT_ID)
    
    # Inicializar bot do Telegram
    bot = TelegramBot(TOKEN, sistema)
    
    # Iniciar monitoramento em uma thread separada
    thread_monitoramento = threading.Thread(target=sistema.monitorar)
    thread_monitoramento.start()
    
    # Iniciar bot do Telegram
    bot.iniciar()

if __name__ == "__main__":
    main()