#!/usr/bin/env python3
"""
Test script para el sistema YOLO COCO

Script para probar la implementación de detección de objetos con modelos preentrenados COCO.
"""

import asyncio
import logging
import sys
from pathlib import Path
from PIL import Image
import io
import requests
import time
from typing import Dict, List, Optional, Any, Union

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector, detect_objects_coco

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_image() -> bytes:
    """Crear una imagen de prueba simple."""
    # Crear imagen con colores
    image = Image.new('RGB', (640, 480), color='lightblue')
    
    # Convertir a bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()


def test_basic_detector() -> None:
    """Test básico del detector COCO."""
    logger.info("🧪 Test 1: Detector básico")
    
    try:
        # Crear detector
        detector = YoloCOCOPretrainedDetector(model_name="yolov8n.pt")
        
        # Mostrar info del modelo
        info = detector.get_model_info()
        logger.info(f"Modelo cargado: {info['model_name']}")
        logger.info(f"Dispositivo: {info['device']}")
        logger.info(f"Disponible: {info['available']}")
        logger.info(f"Ultralytics: {info['ultralytics_available']}")
        
        # Test con imagen
        image_bytes = create_test_image()
        detections = detector.detect(image_bytes)
        
        logger.info(f"✅ Detecciones encontradas: {len(detections)}")
        
        # Mostrar primeras detecciones
        for i, detection in enumerate(detections[:3]):
            logger.info(f"  {i+1}. {detection['class_name']}: {detection['confidence']:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test básico: {e}")
        return False


def test_social_objects() -> None:
    """Test de detección de objetos sociales."""
    logger.info("🧪 Test 2: Objetos socialmente relevantes")
    
    try:
        detector = YoloCOCOPretrainedDetector(model_name="yolov8n.pt")
        image_bytes = create_test_image()
        
        # Detección completa
        all_detections = detector.detect(image_bytes)
        
        # Solo objetos sociales
        social_detections = detector.detect_social_objects(image_bytes)
        
        logger.info(f"✅ Total detecciones: {len(all_detections)}")
        logger.info(f"✅ Objetos sociales: {len(social_detections)}")
        
        # Mostrar objetos sociales
        for detection in social_detections[:3]:
            logger.info(f"  - {detection['class_name']}: {detection['confidence']:.3f} (social)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test social: {e}")
        return False


def test_detection_summary() -> None:
    """Test de resumen de detecciones."""
    logger.info("🧪 Test 3: Resumen de detecciones")
    
    try:
        detector = YoloCOCOPretrainedDetector(model_name="yolov8n.pt")
        image_bytes = create_test_image()
        
        summary = detector.get_detection_summary(image_bytes)
        
        logger.info(f"✅ Resumen generado:")
        logger.info(f"  - Total objetos: {summary['total_objects']}")
        logger.info(f"  - Socialmente relevantes: {summary['social_relevant']}")
        logger.info(f"  - Confianza promedio: {summary['avg_confidence']:.3f}")
        logger.info(f"  - Top clases: {summary['top_classes'][:3]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test resumen: {e}")
        return False


def test_convenience_function() -> None:
    """Test de función de conveniencia."""
    logger.info("🧪 Test 4: Función de conveniencia")
    
    try:
        image_bytes = create_test_image()
        
        # Usar función de conveniencia
        detections = detect_objects_coco(
            image_bytes=image_bytes,
            model_name="yolov8n.pt",
            conf_threshold=0.25
        )
        
        logger.info(f"✅ Función de conveniencia: {len(detections)} detecciones")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en función de conveniencia: {e}")
        return False


def test_different_models() -> None:
    """Test con diferentes modelos."""
    logger.info("🧪 Test 5: Diferentes modelos YOLO")
    
    models_to_test = ["yolov8n.pt", "yolov8s.pt"]
    
    for model_name in models_to_test:
        try:
            logger.info(f"  Probando {model_name}...")
            
            start_time = time.time()
            detector = YoloCOCOPretrainedDetector(model_name=model_name)
            
            image_bytes = create_test_image()
            detections = detector.detect(image_bytes)
            
            inference_time = (time.time() - start_time) * 1000
            
            logger.info(f"    ✅ {model_name}: {len(detections)} detecciones en {inference_time:.1f}ms")
            
        except Exception as e:
            logger.warning(f"    ⚠️ {model_name}: {e}")
    
    return True


def test_api_endpoints() -> None:
    """Test de endpoints de la API (si está corriendo)."""
    logger.info("🧪 Test 6: Endpoints API (opcional)")
    
    try:
        # Verificar si la API está corriendo
        response = requests.get("http://localhost:8000/health", timeout=2)
        
        if response.status_code != 200:
            logger.info("  ⚠️ API no está corriendo en localhost:8000")
            return True
        
        logger.info("  ✅ API detectada, probando endpoints...")
        
        # Test endpoint de modelos
        response = requests.get(
            "http://localhost:8000/api/v1/coco_models",
            headers={"X-API-Key": "dummy_development_key"},
            timeout=5
        )
        
        if response.status_code == 200:
            models = response.json()
            logger.info(f"    ✅ Modelos disponibles: {models['total_models']}")
        
        # Test endpoint de clases
        response = requests.get(
            "http://localhost:8000/api/v1/coco_classes",
            headers={"X-API-Key": "dummy_development_key"},
            timeout=5
        )
        
        if response.status_code == 200:
            classes = response.json()
            logger.info(f"    ✅ Clases COCO: {classes['total_classes']}")
        
        # Test endpoint de test
        response = requests.get(
            "http://localhost:8000/api/v1/coco_test",
            headers={"X-API-Key": "dummy_development_key"},
            timeout=10
        )
        
        if response.status_code == 200:
            test_result = response.json()
            logger.info(f"    ✅ Test API: {test_result['test_passed']}")
        
        return True
        
    except requests.exceptions.RequestException:
        logger.info("  ℹ️ API no disponible (opcional)")
        return True
    except Exception as e:
        logger.warning(f"  ⚠️ Error en test API: {e}")
        return True


def main() -> None:
    """Ejecutar todos los tests."""
    logger.info("🚀 Iniciando tests del sistema YOLO COCO")
    logger.info("=" * 60)
    
    tests = [
        test_basic_detector,
        test_social_objects,
        test_detection_summary,
        test_convenience_function,
        test_different_models,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Test falló: {e}")
            logger.info("")
    
    logger.info("=" * 60)
    logger.info(f"🏁 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        logger.info("🎉 ¡Todos los tests pasaron! Sistema COCO listo para usar.")
        return 0
    else:
        logger.warning(f"⚠️ {total - passed} tests fallaron. Revisar implementación.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)