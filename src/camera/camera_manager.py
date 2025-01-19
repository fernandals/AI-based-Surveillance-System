from picamera2 import Picamera2
import numpy as np
import logging
from typing import Optional, Tuple
from threading import Lock
import time
from pathlib import Path
import cv2

class CameraManager:
    """
    Gerenciador para Raspberry Pi Camera usando PiCamera2.
    """
    
    def __init__(self, 
                 resolution: Tuple[int, int] = (640, 480),
                 rotation: int = 0,
                 save_path: Optional[str] = None):
        """
        Inicializa o gerenciador de câmera.

        Args:
            resolution: Tupla (largura, altura) para resolução
            rotation: Rotação da imagem em graus (0, 90, 180, ou 270)
            save_path: Caminho opcional para salvar imagens capturadas
        """
        self.resolution = resolution
        self.rotation = rotation
        self.save_path = Path(save_path) if save_path else None
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Inicializar câmera
        self.camera = None
        self.lock = Lock()
        self.is_running = False
        
        # Métricas
        self.last_capture_time = None
        self.total_captures = 0
        self.failed_captures = 0
        
    def start(self) -> bool:
        """
        Inicializa e configura a PiCamera2.
        
        Returns:
            bool: True se inicialização foi bem sucedida, False caso contrário
        """
        try:
            with self.lock:
                if self.is_running:
                    self.logger.warning("Câmera já está em execução")
                    return True
                
                self.camera = Picamera2()
                
                # Configurar câmera
                config = self.camera.create_still_configuration(
                    main={"size": self.resolution},
                    lores={"size": (320, 240)},  # Preview de baixa resolução
                    display="lores"
                )
                
                self.camera.configure(config)
                self.camera.start()
                
                # Tempo para o sensor se ajustar
                time.sleep(2)
                
                self.is_running = True
                self.logger.info("PiCamera2 iniciada com sucesso")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar PiCamera2: {str(e)}")
            return False
            
    def stop(self) -> None:
        """
        Para a câmera e libera recursos.
        """
        with self.lock:
            if self.camera is not None:
                self.camera.stop()
                self.camera.close()
                self.camera = None
                self.is_running = False
                self.logger.info("PiCamera2 desligada")
    
    def capture_image(self) -> Optional[np.ndarray]:
        """
        Captura uma única imagem da câmera.
        
        Returns:
            np.ndarray: Imagem capturada ou None se falhar
        """
        if not self.is_running:
            self.logger.error("Tentativa de captura com câmera desligada")
            return None
            
        try:
            with self.lock:
                # Capturar imagem
                frame = self.camera.capture_array()
                
                # Aplicar rotação se necessário
                if self.rotation:
                    if self.rotation == 90:
                        frame = np.rot90(frame)
                    elif self.rotation == 180:
                        frame = np.rot90(frame, 2)
                    elif self.rotation == 270:
                        frame = np.rot90(frame, 3)
                
                # Atualizar métricas
                self.total_captures += 1
                self.last_capture_time = time.time()
                
                # Salvar imagem se caminho foi especificado
                if self.save_path:
                    self._save_image(frame)
                
                return frame
                
        except Exception as e:
            self.failed_captures += 1
            self.logger.error(f"Erro ao capturar imagem: {str(e)}")
            return None
    
    def _save_image(self, frame: np.ndarray) -> bool:
        """
        Salva a imagem no caminho especificado.
        
        Args:
            frame: Imagem a ser salva
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            if not self.save_path.exists():
                self.save_path.mkdir(parents=True)
            
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filepath = self.save_path / f"capture_{timestamp}.jpg"
            
            # Salvar imagem usando OpenCV
            cv2.imwrite(str(filepath), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            self.logger.info(f"Imagem salva em: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar imagem: {str(e)}")
            return False
    
    def get_metrics(self) -> dict:
        """
        Retorna métricas do uso da câmera.
        
        Returns:
            dict: Dicionário com métricas
        """
        return {
            "total_captures": self.total_captures,
            "failed_captures": self.failed_captures,
            "success_rate": (
                (self.total_captures - self.failed_captures) / self.total_captures * 100 
                if self.total_captures > 0 else 0
            ),
            "last_capture": self.last_capture_time,
            "is_running": self.is_running,
            "resolution": self.resolution,
            "rotation": self.rotation
        }
    
    def __enter__(self):
        """Suporte para uso com context manager"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante que a câmera seja desligada ao sair do context"""
        self.stop()

# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Exemplo básico
    with CameraManager(resolution=(1280, 720), save_path="capturas") as cam:
        # Capturar uma imagem
        image = cam.capture_image()
        if image is not None:
            print("Imagem capturada com sucesso!")
            print(f"Formato da imagem: {image.shape}")
        
        # Mostrar métricas
        print("\nMétricas da câmera:")
        print(cam.get_metrics())
