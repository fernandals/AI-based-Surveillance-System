import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
import cv2
from pathlib import Path
import json

class ObjectDetector:
    """
    Detector de objetos usando modelo EfficientDet do TensorFlow Hub.
    """
    
    # Mapeamento de labels COCO em português
    LABELS_PT = {
        1: "pessoa", 2: "bicicleta", 3: "carro", 4: "moto", 5: "avião",
        6: "ônibus", 7: "trem", 8: "caminhão", 9: "barco", 10: "semáforo",
        11: "hidrante", 13: "placa pare", 14: "parquímetro", 15: "banco",
        16: "pássaro", 17: "gato", 18: "cachorro", 19: "cavalo", 20: "ovelha",
        21: "vaca", 22: "elefante", 23: "urso", 24: "zebra", 25: "girafa",
        27: "mochila", 28: "guarda-chuva", 31: "bolsa", 32: "gravata",
        33: "mala", 34: "frisbee", 35: "esquis", 36: "snowboard",
        37: "bola esportiva", 38: "pipa", 39: "taco baseball",
        40: "luva baseball", 41: "skateboard", 42: "prancha surf",
        43: "raquete tênis", 44: "garrafa", 46: "taça vinho", 47: "xícara",
        48: "garfo", 49: "faca", 50: "colher", 51: "tigela", 52: "banana",
        53: "maçã", 54: "sanduíche", 55: "laranja", 56: "brócolis",
        57: "cenoura", 58: "cachorro-quente", 59: "pizza", 60: "donut",
        61: "bolo", 62: "cadeira", 63: "sofá", 64: "vaso planta",
        65: "cama", 67: "mesa jantar", 70: "privada", 72: "tv",
        73: "laptop", 74: "mouse", 75: "controle remoto", 76: "teclado",
        77: "celular", 78: "micro-ondas", 79: "forno", 80: "torradeira",
        81: "pia", 82: "geladeira", 84: "livro", 85: "relógio",
        86: "vaso", 87: "tesoura", 88: "ursinho pelúcia", 89: "secador",
        90: "escova dentes"
    }
    
    def __init__(self,
                 model_url: str = "https://tfhub.dev/tensorflow/efficientdet/lite2/detection/2",
                 confidence_threshold: float = 0.5,
                 cache_dir: Optional[str] = None):
        """
        Inicializa o detector de objetos.

        Args:
            model_url: URL do modelo no TensorFlow Hub
            confidence_threshold: Limite mínimo de confiança para detecções
            cache_dir: Diretório para cache do modelo
        """
        self.model_url = model_url
        self.confidence_threshold = confidence_threshold
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Inicializar modelo
        self.model = None
        self.is_loaded = False
        
        # Métricas
        self.total_detections = 0
        self.cache_hits = 0
        
    def load_model(self) -> bool:
        """
        Carrega o modelo de detecção.
        
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        try:
            self.logger.info("Carregando modelo de detecção...")
            
            # Configurar cache se especificado
            if self.cache_dir:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                os.environ['TFHUB_CACHE_DIR'] = str(self.cache_dir)
            
            # Carregar modelo
            self.model = hub.load(self.model_url)
            self.is_loaded = True
            
            self.logger.info("Modelo carregado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo: {str(e)}")
            return False
    
    def preprocess_image(self, image: np.ndarray) -> tf.Tensor:
        """
        Pré-processa a imagem para o formato esperado pelo modelo.
        
        Args:
            image: Imagem no formato numpy array (RGB)
            
        Returns:
            tf.Tensor: Imagem processada
        """
        # Redimensionar para o tamanho esperado pelo modelo
        image = cv2.resize(image, (512, 512))
        
        # Converter para float e expandir dimensões
        image = tf.convert_to_tensor(image)
        image = tf.cast(image, tf.uint8)
        image = tf.expand_dims(image, axis=0)
        
        return image
    
    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        Detecta objetos em uma imagem.
        
        Args:
            image: Imagem no formato numpy array (RGB)
            
        Returns:
            List[Dict]: Lista de detecções com classe, confiança e coordenadas
        """
        if not self.is_loaded:
            if not self.load_model():
                return []
        
        try:
            # Pré-processar imagem
            processed_image = self.preprocess_image(image)
            
            # Realizar detecção
            results = self.model(processed_image)
            
            # Extrair resultados
            boxes = results['detection_boxes'][0].numpy()
            classes = results['detection_classes'][0].numpy().astype(np.int32)
            scores = results['detection_scores'][0].numpy()
            
            # Filtrar detecções pela confiança
            detections = []
            for box, class_id, score in zip(boxes, classes, scores):
                if score >= self.confidence_threshold and class_id in self.LABELS_PT:
                    detection = {
                        'classe': self.LABELS_PT[class_id],
                        'confianca': float(score),
                        'bbox': {
                            'y_min': float(box[0]),
                            'x_min': float(box[1]),
                            'y_max': float(box[2]),
                            'x_max': float(box[3])
                        }
                    }
                    detections.append(detection)
            
            # Atualizar métricas
            self.total_detections += len(detections)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar objetos: {str(e)}")
            return []
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Desenha as detecções na imagem.
        
        Args:
            image: Imagem original
            detections: Lista de detecções
            
        Returns:
            np.ndarray: Imagem com detecções desenhadas
        """
        image_with_boxes = image.copy()
        height, width = image.shape[:2]
        
        for detection in detections:
            # Extrair coordenadas
            bbox = detection['bbox']
            y_min, x_min = int(bbox['y_min'] * height), int(bbox['x_min'] * width)
            y_max, x_max = int(bbox['y_max'] * height), int(bbox['x_max'] * width)
            
            # Desenhar retângulo
            cv2.rectangle(image_with_boxes, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            
            # Adicionar label
            label = f"{detection['classe']} {detection['confianca']:.2f}"
            cv2.putText(image_with_boxes, label, (x_min, y_min - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return image_with_boxes
    
    def get_metrics(self) -> dict:
        """
        Retorna métricas do detector.
        
        Returns:
            dict: Dicionário com métricas
        """
        return {
            "total_detections": self.total_detections,
            "modelo_carregado": self.is_loaded,
            "confianca_minima": self.confidence_threshold,
            "cache_hits": self.cache_hits
        }

# Exemplo de uso
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar detector
    detector = ObjectDetector(confidence_threshold=0.5)
    
    # Carregar uma imagem de teste (substitua pelo seu caminho)
    imagem = cv2.imread("capturas/capture_20250119-164635.jpg")
    if imagem is not None:
        # Converter BGR para RGB
        imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        
        # Detectar objetos
        deteccoes = detector.detect_objects(imagem)
        
        # Desenhar detecções
        imagem_com_boxes = detector.draw_detections(imagem, deteccoes)
        
        print(f"Objetos detectados: {len(deteccoes)}")
        for d in deteccoes:
            print(f"- {d['classe']}: {d['confianca']:.2f}")