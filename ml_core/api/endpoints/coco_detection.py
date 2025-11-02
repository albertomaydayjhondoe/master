"""
COCO Object Detection API Endpoint

Endpoint para detección de objetos usando modelos YOLO preentrenados en COCO.
Perfecto para análisis de contenido de redes sociales.
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from pathlib import Path

from ml_core.models.factory import get_yolo_coco_detector
from ml_core.api.main import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


class COCODetectionRequest(BaseModel):
    """Request para detección COCO con parámetros configurables."""
    model_name: str = Field(default="yolov8n.pt", description="Modelo YOLO a usar")
    conf_threshold: float = Field(default=0.25, ge=0.0, le=1.0, description="Umbral de confianza")
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0, description="Umbral IoU para NMS")
    max_detections: int = Field(default=1000, ge=1, le=10000, description="Máximo detecciones")
    social_only: bool = Field(default=False, description="Solo objetos relevantes para redes sociales")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "yolov8s.pt",
                "conf_threshold": 0.3,
                "iou_threshold": 0.45,
                "max_detections": 500,
                "social_only": True
            }
        }


class COCODetectionResponse(BaseModel):
    """Response de detección COCO."""
    success: bool
    total_detections: int
    social_relevant_count: int
    detections: List[Dict[str, Any]]
    model_info: Dict[str, Any]
    processing_time_ms: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_detections": 5,
                "social_relevant_count": 3,
                "detections": [
                    {
                        "class_id": 0,
                        "class_name": "person",
                        "confidence": 0.892,
                        "bbox": {"x1": 120, "y1": 80, "x2": 300, "y2": 450},
                        "center": {"x": 210, "y": 265},
                        "area": 66600,
                        "social_relevant": True
                    }
                ],
                "model_info": {
                    "model_name": "yolov8s.pt",
                    "device": "cuda",
                    "conf_threshold": 0.3
                },
                "processing_time_ms": 245.6
            }
        }


class COCOSummaryResponse(BaseModel):
    """Response de resumen de detección COCO."""
    success: bool
    summary: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "summary": {
                    "total_objects": 8,
                    "social_relevant": 5,
                    "top_classes": [["person", 3], ["cell phone", 2], ["car", 1]],
                    "avg_confidence": 0.756,
                    "detection_areas": [
                        {
                            "class": "person",
                            "confidence": 0.892,
                            "center": {"x": 210, "y": 265},
                            "area": 66600
                        }
                    ]
                }
            }
        }


@router.post("/coco_detect", 
             response_model=COCODetectionResponse,
             summary="Detectar objetos con YOLO COCO",
             description="""
             Detecta objetos en una imagen usando modelos YOLO preentrenados en COCO dataset.
             
             **Características:**
             - 80 clases de objetos COCO
             - Modelos desde nano (rápido) hasta xlarge (preciso)
             - Filtrado automático de objetos relevantes para redes sociales
             - Configuración flexible de umbrales
             
             **Modelos disponibles:**
             - yolov8n.pt (ultra rápido, 6MB)
             - yolov8s.pt (rápido, 22MB) 
             - yolov8m.pt (balance, 52MB)
             - yolov8l.pt (preciso, 87MB)
             - yolov8x.pt (máxima precisión, 136MB)
             """)
async def detect_objects_coco(
    file: UploadFile = File(..., description="Imagen para analizar"),
    model_name: str = Query(default="yolov8n.pt", description="Modelo YOLO"),
    conf_threshold: float = Query(default=0.25, ge=0.0, le=1.0, description="Umbral confianza"),
    iou_threshold: float = Query(default=0.45, ge=0.0, le=1.0, description="Umbral IoU"),
    max_detections: int = Query(default=1000, ge=1, le=10000, description="Máx detecciones"),
    social_only: bool = Query(default=False, description="Solo objetos sociales"),
    api_key: str = Depends(verify_api_key)
):
    """Endpoint principal para detección de objetos COCO."""
    
    import time
    start_time = time.time()
    
    try:
        # Validar archivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Leer imagen
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Imagen vacía")
        
        if len(image_bytes) > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="Imagen demasiado grande (máx 50MB)")
        
        # Crear detector
        detector = get_yolo_coco_detector(
            model_name=model_name,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
            max_detections=max_detections
        )
        
        # Detectar objetos
        if social_only:
            detections = detector.detect_social_objects(image_bytes)
        else:
            detections = detector.detect(image_bytes)
        
        # Contar objetos socialmente relevantes
        social_count = len([d for d in detections if d.get("social_relevant", False)])
        
        # Tiempo de procesamiento
        processing_time = (time.time() - start_time) * 1000
        
        # Información del modelo
        model_info = detector.get_model_info()
        
        logger.info(f"COCO detección completada: {len(detections)} objetos en {processing_time:.1f}ms")
        
        return COCODetectionResponse(
            success=True,
            total_detections=len(detections),
            social_relevant_count=social_count,
            detections=detections,
            model_info=model_info,
            processing_time_ms=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en detección COCO: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/coco_summary",
             response_model=COCOSummaryResponse,
             summary="Resumen de detección COCO",
             description="""
             Obtiene un resumen estadístico de las detecciones COCO en una imagen.
             
             **Incluye:**
             - Conteo total de objetos
             - Objetos relevantes para redes sociales
             - Top 5 clases más detectadas
             - Confianza promedio
             - Áreas de detección principales
             - Información del modelo usado
             """)
async def get_coco_summary(
    file: UploadFile = File(..., description="Imagen para analizar"),
    model_name: str = Query(default="yolov8n.pt", description="Modelo YOLO"),
    conf_threshold: float = Query(default=0.25, ge=0.0, le=1.0, description="Umbral confianza"),
    api_key: str = Depends(verify_api_key)
):
    """Endpoint para obtener resumen de detecciones COCO."""
    
    try:
        # Validar archivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Leer imagen
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Imagen vacía")
        
        # Crear detector
        detector = get_yolo_coco_detector(
            model_name=model_name,
            conf_threshold=conf_threshold
        )
        
        # Obtener resumen
        summary = detector.get_detection_summary(image_bytes)
        
        logger.info(f"COCO resumen generado: {summary['total_objects']} objetos")
        
        return COCOSummaryResponse(
            success=True,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en resumen COCO: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/coco_models",
            summary="Listar modelos COCO disponibles",
            description="Obtiene información sobre todos los modelos YOLO COCO disponibles.")
async def get_available_coco_models(api_key: str = Depends(verify_api_key)):
    """Endpoint para listar modelos COCO disponibles."""
    
    models = {
        "yolov8n.pt": {
            "name": "YOLOv8 Nano",
            "description": "Ultra rápido, menor precisión",
            "speed": "fastest",
            "accuracy": "lower", 
            "size_mb": 6,
            "recommended_use": "tiempo_real"
        },
        "yolov8s.pt": {
            "name": "YOLOv8 Small", 
            "description": "Rápido con buena precisión",
            "speed": "fast",
            "accuracy": "good",
            "size_mb": 22,
            "recommended_use": "produccion_ligera"
        },
        "yolov8m.pt": {
            "name": "YOLOv8 Medium",
            "description": "Balance óptimo velocidad/precisión",
            "speed": "medium", 
            "accuracy": "high",
            "size_mb": 52,
            "recommended_use": "produccion_standard"
        },
        "yolov8l.pt": {
            "name": "YOLOv8 Large",
            "description": "Alta precisión",
            "speed": "slow",
            "accuracy": "very_high",
            "size_mb": 87,
            "recommended_use": "analisis_detallado"
        },
        "yolov8x.pt": {
            "name": "YOLOv8 XLarge",
            "description": "Máxima precisión",
            "speed": "slowest",
            "accuracy": "highest", 
            "size_mb": 136,
            "recommended_use": "investigacion"
        }
    }
    
    return {
        "success": True,
        "models": models,
        "default_model": "yolov8n.pt",
        "total_models": len(models)
    }


@router.get("/coco_classes",
            summary="Listar clases COCO",
            description="Obtiene todas las clases COCO con indicadores de relevancia social.")
async def get_coco_classes(
    social_only: bool = Query(default=False, description="Solo clases socialmente relevantes"),
    api_key: str = Depends(verify_api_key)
):
    """Endpoint para listar clases COCO."""
    
    # Importar las clases desde el detector
    from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector
    
    all_classes = {
        0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus',
        6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant',
        11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat',
        16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear',
        22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag',
        27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard',
        32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove',
        36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle',
        40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon',
        45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange',
        50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut',
        55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed',
        60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse',
        65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave',
        69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book',
        74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear',
        78: 'hair drier', 79: 'toothbrush'
    }
    
    social_relevant = YoloCOCOPretrainedDetector.SOCIAL_RELEVANT_CLASSES
    
    if social_only:
        classes = {id: name for id, name in all_classes.items() if id in social_relevant}
    else:
        classes = all_classes
    
    # Agregar indicadores de relevancia social
    classes_with_social = {
        id: {
            "name": name,
            "social_relevant": id in social_relevant
        }
        for id, name in classes.items()
    }
    
    return {
        "success": True,
        "classes": classes_with_social,
        "total_classes": len(classes_with_social),
        "social_relevant_count": len([c for c in classes_with_social.values() if c["social_relevant"]])
    }


# Configuración para testing
@router.get("/coco_test",
            summary="Test del sistema COCO",
            description="Endpoint de prueba para verificar que el sistema COCO funciona correctamente.")
async def test_coco_system(api_key: str = Depends(verify_api_key)):
    """Endpoint de test para el sistema COCO."""
    
    try:
        # Crear detector de prueba
        detector = get_yolo_coco_detector(model_name="yolov8n.pt")
        
        # Obtener info del modelo
        model_info = detector.get_model_info()
        
        # Test con imagen dummy
        from PIL import Image
        import io
        
        # Crear imagen de prueba
        test_image = Image.new('RGB', (640, 480), color='blue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        # Ejecutar detección
        detections = detector.detect(img_bytes)
        
        return {
            "success": True,
            "test_passed": True,
            "model_info": model_info,
            "test_detections": len(detections),
            "sample_detection": detections[0] if detections else None,
            "message": "Sistema COCO funcionando correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error en test COCO: {e}")
        return {
            "success": False,
            "test_passed": False,
            "error": str(e),
            "message": "Error en sistema COCO"
        }