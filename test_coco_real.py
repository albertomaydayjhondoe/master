#!/usr/bin/env python3
"""
Test del sistema YOLO COCO con Ultralytics real
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Configurar modo real
os.environ["DUMMY_MODE"] = "false"

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

def test_real_yolo() -> None:
    """Test con YOLO real."""
    print("🧪 Test: YOLO real con Ultralytics")
    print("=" * 50)
    
    try:
        from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector
        from PIL import Image
        import io
        import time
        
        print("🔄 Creando detector real...")
        detector = YoloCOCOPretrainedDetector(model_name="yolov8n.pt")
        
        # Info del modelo
        info = detector.get_model_info()
        print(f"✅ Modelo: {info['model_name']}")
        print(f"✅ Dispositivo: {info['device']}")
        print(f"✅ Disponible: {info['available']}")
        print(f"✅ Ultralytics: {info['ultralytics_available']}")
        
        # Crear imagen de prueba más compleja
        print("\n🔄 Creando imagen de prueba...")
        image = Image.new('RGB', (640, 480))
        # Agregar algunos "objetos" como rectángulos de colores
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        draw.rectangle([100, 100, 200, 200], fill='red')  # Simular objeto
        draw.rectangle([300, 200, 400, 350], fill='blue')  # Otro objeto
        draw.ellipse([450, 50, 550, 150], fill='green')   # Objeto redondo
        
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        # Detección
        print("🔄 Ejecutando detección...")
        start_time = time.time()
        detections = detector.detect(img_bytes)
        inference_time = (time.time() - start_time) * 1000
        
        print(f"✅ Detecciones encontradas: {len(detections)}")
        print(f"✅ Tiempo de inferencia: {inference_time:.1f}ms")
        
        # Mostrar detecciones
        if detections:
            print("\n📋 Top detecciones:")
            for i, det in enumerate(detections[:5]):
                social_icon = "🎯" if det['social_relevant'] else "🔹"
                print(f"  {social_icon} {det['class_name']}: {det['confidence']:.3f}")
        
        # Test objetos sociales
        print("\n🔄 Probando detección de objetos sociales...")
        social_detections = detector.detect_social_objects(img_bytes)
        print(f"✅ Objetos sociales: {len(social_detections)}")
        
        # Resumen
        print("\n🔄 Generando resumen...")
        summary = detector.get_detection_summary(img_bytes)
        print(f"✅ Resumen generado:")
        print(f"  - Total: {summary['total_objects']}")
        print(f"  - Sociales: {summary['social_relevant']}")
        print(f"  - Confianza promedio: {summary['avg_confidence']:.3f}")
        print(f"  - Top clases: {summary['top_classes'][:3]}")
        
        print("\n🎉 ¡Test con YOLO real completado exitosamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        print("💡 Asegúrate de que ultralytics esté instalado: pip install ultralytics")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_different_models() -> None:
    """Test con diferentes modelos si están disponibles."""
    print("\n🧪 Test: Diferentes modelos YOLO")
    print("=" * 30)
    
    models = ["yolov8n.pt", "yolov8s.pt"]
    
    for model in models:
        try:
            print(f"\n🔄 Probando {model}...")
            from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector
            
            detector = YoloCOCOPretrainedDetector(model_name=model)
            info = detector.get_model_info()
            
            if info['available']:
                print(f"✅ {model} cargado en {info['device']}")
            else:
                print(f"⚠️ {model} en modo dummy")
                
        except Exception as e:
            print(f"❌ {model}: {e}")

if __name__ == "__main__":
    print("🚀 Test YOLO COCO con Ultralytics")
    print("=" * 60)
    
    success = test_real_yolo()
    test_different_models()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡Sistema YOLO COCO completamente funcional!")
    else:
        print("⚠️ Algunos tests fallaron - revisar configuración")