#!/usr/bin/env python3
"""
Test simple del sistema YOLO COCO
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Configurar dummy mode para evitar problemas
os.environ["DUMMY_MODE"] = "true"

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def test_import() -> None:
    """Test de import del detector."""
    print("🧪 Test 1: Importando detector COCO...")
    
    try:
        from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector
        print("✅ Import exitoso")
        return True
    except Exception as e:
        print(f"❌ Error en import: {e}")
        return False

def test_detector_creation() -> None:
    """Test de creación del detector."""
    print("🧪 Test 2: Creando detector...")
    
    try:
        from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector
        
        detector = YoloCOCOPretrainedDetector(model_name="yolov8n.pt")
        print("✅ Detector creado")
        
        # Obtener info
        info = detector.get_model_info()
        print(f"  - Modelo: {info['model_name']}")
        print(f"  - Dispositivo: {info['device']}")
        print(f"  - Disponible: {info['available']}")
        print(f"  - Ultralytics: {info['ultralytics_available']}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando detector: {e}")
        return False

def test_dummy_detection() -> None:
    """Test de detección dummy."""
    print("🧪 Test 3: Detección dummy...")
    
    try:
        from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector
        from PIL import Image
        import io
        
        detector = YoloCOCOPretrainedDetector(model_name="yolov8n.pt")
        
        # Crear imagen dummy
        image = Image.new('RGB', (640, 480), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()
        
        # Detectar
        detections = detector.detect(img_data)
        print(f"✅ Detecciones: {len(detections)}")
        
        # Mostrar primeras detecciones
        for i, det in enumerate(detections[:3]):
            print(f"  {i+1}. {det['class_name']}: {det['confidence']:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Error en detección: {e}")
        return False

def test_factory() -> None:
    """Test de factory."""
    print("🧪 Test 4: Factory pattern...")
    
    try:
        from ml_core.models.factory import get_yolo_coco_detector
        
        detector = get_yolo_coco_detector(model_name="yolov8n.pt")
        print("✅ Factory funcionando")
        
        return True
    except Exception as e:
        print(f"❌ Error en factory: {e}")
        return False

def main() -> None:
    """Ejecutar tests."""
    print("🚀 Test simple sistema YOLO COCO")
    print("=" * 50)
    
    tests = [
        test_import,
        test_detector_creation,
        test_dummy_detection,
        test_factory
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"🏁 Resultado: {passed}/{len(tests)} tests pasaron")
    
    if passed == len(tests):
        print("🎉 ¡Sistema COCO funcionando!")
    else:
        print("⚠️ Algunos tests fallaron")

if __name__ == "__main__":
    main()