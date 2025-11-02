"""
YOLO COCO Pretrained Model - Implementación con modelos preentrenados COCO

Este módulo implementa detección de objetos usando modelos YOLO preentrenados 
en el dataset COCO. Perfecto para detección general de objetos en screenshots.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image
import io

try:
    from ultralytics import YOLO
    import torch
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

import os
def is_dummy_mode() -> bool:
    return os.getenv("DUMMY_MODE", "true").lower() == "true"

logger = logging.getLogger(__name__)

__all__ = ['YoloCOCOPretrainedDetector']


class YoloCOCOPretrainedDetector:
    """
    Detector YOLO con modelos preentrenados en COCO dataset.
    
    Características:
    - Detección de 80 clases COCO standard
    - Modelos preentrenados listos para usar
    - Optimizado para screenshots y análisis de UI
    - Soporte para CPU y GPU automático
    """
    
    # Clases COCO más relevantes para análisis de redes sociales
    SOCIAL_RELEVANT_CLASSES = {
        0: 'person',
        1: 'bicycle', 
        2: 'car',
        3: 'motorcycle',
        4: 'airplane',
        5: 'bus',
        6: 'train',
        7: 'truck',
        8: 'boat',
        15: 'cat',
        16: 'dog',
        17: 'horse',
        18: 'sheep',
        19: 'cow',
        20: 'elephant',
        21: 'bear',
        22: 'zebra',
        23: 'giraffe',
        24: 'backpack',
        26: 'handbag',
        27: 'tie',
        28: 'suitcase',
        32: 'sports ball',
        37: 'skateboard',
        38: 'surfboard',
        39: 'tennis racket',
        41: 'cup',
        42: 'fork',
        43: 'knife',
        44: 'spoon',
        45: 'bowl',
        46: 'banana',
        47: 'apple',
        48: 'sandwich',
        49: 'orange',
        50: 'broccoli',
        51: 'carrot',
        52: 'hot dog',
        53: 'pizza',
        54: 'donut',
        55: 'cake',
        56: 'chair',
        57: 'couch',
        58: 'potted plant',
        59: 'bed',
        61: 'toilet',
        62: 'tv',
        63: 'laptop',
        64: 'mouse',
        65: 'remote',
        66: 'keyboard',
        67: 'cell phone',
        73: 'book',
        74: 'clock',
        75: 'vase',
        76: 'scissors',
        77: 'teddy bear',
        78: 'hair drier',
        79: 'toothbrush'
    }
    
    def __init__(self, 
                 model_name: str = "yolov8n.pt",
                 device: str = "auto",
                 conf_threshold: float = 0.25,
                 iou_threshold: float = 0.45,
                 max_detections: int = 1000):
        """
        Inicializar detector YOLO COCO.
        
        Args:
            model_name: Nombre del modelo YOLO ('yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt')
            device: Dispositivo ('auto', 'cpu', 'cuda', 'cuda:0', etc.)
            conf_threshold: Umbral de confianza mínima
            iou_threshold: Umbral IoU para NMS
            max_detections: Número máximo de detecciones por imagen
        """
        self.model_name = model_name
        self.device = self._setup_device(device)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.max_detections = max_detections
        self.model = None
        
        # Verificar disponibilidad
        if not ULTRALYTICS_AVAILABLE:
            if is_dummy_mode():
                logger.warning("Ultralytics no disponible, usando modo dummy")
                self._init_dummy_mode()
                return
            else:
                raise ImportError("Ultralytics no está instalado. Instala con: pip install ultralytics")
        
        # Inicializar modelo real
        self._init_model()
        
    def _setup_device(self, device: str) -> str:
        """Configurar dispositivo automáticamente."""
        if device == "auto":
            if ULTRALYTICS_AVAILABLE and torch.cuda.is_available():
                device = "cuda"
                logger.info(f"GPU detectada, usando CUDA")
            else:
                device = "cpu"
                logger.info(f"Usando CPU para inferencia")
        return device
        
    def _init_model(self) -> None:
        """Inicializar modelo YOLO real."""
        try:
            logger.info(f"Cargando modelo YOLO: {self.model_name}")
            
            # Cargar modelo preentrenado
            self.model = YOLO(self.model_name)
            
            # Mover a dispositivo especificado
            if self.device != "cpu":
                self.model.to(self.device)
                
            logger.info(f"Modelo YOLO cargado exitosamente en {self.device}")
            
            # Calentar modelo con una imagen dummy
            self._warmup_model()
            
        except Exception as e:
            logger.error(f"Error al cargar modelo YOLO: {e}")
            if is_dummy_mode():
                logger.warning("Fallback a modo dummy")
                self._init_dummy_mode()
            else:
                raise
                
    def _init_dummy_mode(self) -> None:
        """Inicializar modo dummy si no hay modelo real."""
        self.model = None
        logger.info("Detector YOLO inicializado en modo dummy")
        
    def _warmup_model(self) -> None:
        """Calentar modelo con inferencia dummy."""
        if self.model is None:
            return
            
        try:
            # Crear imagen dummy 640x640
            dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            
            # Ejecutar inferencia dummy
            _ = self.model(dummy_image, 
                          conf=self.conf_threshold,
                          iou=self.iou_threshold,
                          verbose=False)
            
            logger.info("Modelo YOLO calentado exitosamente")
            
        except Exception as e:
            logger.warning(f"Error al calentar modelo: {e}")
    
    def detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Detectar objetos en imagen.
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            Lista de detecciones con formato:
            [
                {
                    "class_id": int,
                    "class_name": str,
                    "confidence": float,
                    "bbox": {"x1": int, "y1": int, "x2": int, "y2": int},
                    "center": {"x": int, "y": int},
                    "area": int,
                    "social_relevant": bool
                }
            ]
        """
        if self.model is None:
            return self._dummy_detect(image_bytes)
            
        try:
            # Convertir bytes a PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Asegurar RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Ejecutar inferencia
            results = self.model(image,
                               conf=self.conf_threshold,
                               iou=self.iou_threshold,
                               max_det=self.max_detections,
                               verbose=False)
            
            # Procesar resultados
            detections = []
            
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes
                    
                    for i in range(len(boxes)):
                        # Extraer datos
                        bbox = boxes.xyxy[i].cpu().numpy()  # x1, y1, x2, y2
                        conf = float(boxes.conf[i].cpu().numpy())
                        class_id = int(boxes.cls[i].cpu().numpy())
                        
                        # Calcular centro y área
                        x1, y1, x2, y2 = bbox
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        area = int((x2 - x1) * (y2 - y1))
                        
                        # Nombre de clase
                        class_name = self.model.names.get(class_id, f"class_{class_id}")
                        
                        # Determinar si es relevante para redes sociales
                        social_relevant = class_id in self.SOCIAL_RELEVANT_CLASSES
                        
                        detection = {
                            "class_id": class_id,
                            "class_name": class_name,
                            "confidence": round(conf, 3),
                            "bbox": {
                                "x1": int(x1),
                                "y1": int(y1), 
                                "x2": int(x2),
                                "y2": int(y2)
                            },
                            "center": {
                                "x": center_x,
                                "y": center_y
                            },
                            "area": area,
                            "social_relevant": social_relevant
                        }
                        
                        detections.append(detection)
            
            # Ordenar por confianza descendente
            detections.sort(key=lambda x: x["confidence"], reverse=True)
            
            logger.info(f"Detectados {len(detections)} objetos")
            return detections
            
        except Exception as e:
            logger.error(f"Error en detección YOLO: {e}")
            return self._dummy_detect(image_bytes)
    
    def _dummy_detect(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Detección dummy para testing."""
        import random
        
        dummy_classes = [
            {"id": 0, "name": "person", "social": True},
            {"id": 67, "name": "cell phone", "social": True}, 
            {"id": 62, "name": "tv", "social": True},
            {"id": 63, "name": "laptop", "social": True},
            {"id": 56, "name": "chair", "social": False},
            {"id": 75, "name": "vase", "social": False}
        ]
        
        detections = []
        num_detections = random.randint(2, 8)
        
        for _ in range(num_detections):
            cls = random.choice(dummy_classes)
            
            # Coordenadas aleatorias
            x1 = random.randint(50, 500)
            y1 = random.randint(50, 500)
            x2 = x1 + random.randint(50, 200)
            y2 = y1 + random.randint(50, 200)
            
            detection = {
                "class_id": cls["id"],
                "class_name": cls["name"],
                "confidence": round(random.uniform(0.3, 0.95), 3),
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "center": {"x": int((x1+x2)/2), "y": int((y1+y2)/2)},
                "area": (x2-x1) * (y2-y1),
                "social_relevant": cls["social"]
            }
            
            detections.append(detection)
        
        return sorted(detections, key=lambda x: x["confidence"], reverse=True)
    
    def detect_social_objects(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Detectar solo objetos relevantes para redes sociales.
        
        Returns:
            Lista filtrada solo con objetos socialmente relevantes
        """
        all_detections = self.detect(image_bytes)
        
        # Filtrar solo objetos relevantes
        social_detections = [d for d in all_detections if d["social_relevant"]]
        
        logger.info(f"Detectados {len(social_detections)} objetos socialmente relevantes de {len(all_detections)} total")
        
        return social_detections
    
    def get_detection_summary(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Obtener resumen completo de detecciones.
        
        Returns:
            Diccionario con estadísticas de detección
        """
        detections = self.detect(image_bytes)
        
        if not detections:
            return {
                "total_objects": 0,
                "social_relevant": 0,
                "top_classes": [],
                "avg_confidence": 0.0,
                "detection_areas": []
            }
        
        # Estadísticas
        total_objects = len(detections)
        social_relevant = len([d for d in detections if d["social_relevant"]])
        avg_confidence = sum(d["confidence"] for d in detections) / total_objects
        
        # Top classes
        class_counts: Dict[str, int] = {}
        for d in detections:
            class_name = d["class_name"]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        top_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Áreas de detección
        detection_areas = [
            {
                "class": d["class_name"],
                "confidence": d["confidence"], 
                "center": d["center"],
                "area": d["area"]
            }
            for d in detections[:10]  # Top 10 por confianza
        ]
        
        return {
            "total_objects": total_objects,
            "social_relevant": social_relevant,
            "top_classes": top_classes,
            "avg_confidence": round(avg_confidence, 3),
            "detection_areas": detection_areas,
            "model_info": {
                "model_name": self.model_name,
                "device": self.device,
                "conf_threshold": self.conf_threshold
            }
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "conf_threshold": self.conf_threshold,
            "iou_threshold": self.iou_threshold,
            "max_detections": self.max_detections,
            "available": self.model is not None,
            "ultralytics_available": ULTRALYTICS_AVAILABLE,
            "num_classes": 80,  # COCO tiene 80 clases
            "social_relevant_classes": len(self.SOCIAL_RELEVANT_CLASSES)
        }


# Función de conveniencia para uso directo
def detect_objects_coco(image_bytes: bytes, 
                       model_name: str = "yolov8n.pt",
                       conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
    """
    Función de conveniencia para detección rápida con COCO.
    
    Args:
        image_bytes: Bytes de la imagen
        model_name: Modelo YOLO a usar
        conf_threshold: Umbral de confianza
        
    Returns:
        Lista de detecciones
    """
    detector = YoloCOCOPretrainedDetector(
        model_name=model_name,
        conf_threshold=conf_threshold
    )
    
    return detector.detect(image_bytes)


if __name__ == "__main__":
    # Test del detector
    logging.basicConfig(level=logging.INFO)
    
    # Crear detector
    detector = YoloCOCOPretrainedDetector(model_name="yolov8n.pt")
    
    # Mostrar info del modelo
    info = detector.get_model_info()
    print("Información del modelo:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test con imagen dummy
    dummy_image = Image.new('RGB', (640, 480), color='blue')
    img_bytes = io.BytesIO()
    dummy_image.save(img_bytes, format='JPEG')
    img_bytes_data = img_bytes.getvalue()
    
    # Detectar objetos
    detections = detector.detect(img_bytes_data)
    print(f"\nDetecciones encontradas: {len(detections)}")
    
    for detection in detections[:3]:  # Mostrar top 3
        print(f"  - {detection['class_name']}: {detection['confidence']:.3f}")