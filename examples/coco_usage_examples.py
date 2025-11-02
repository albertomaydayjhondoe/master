#!/usr/bin/env python3
"""
Ejemplo de uso del sistema YOLO COCO

Este ejemplo muestra cómo usar el sistema de detección de objetos COCO
tanto a través de la API como directamente con el detector.
"""

import asyncio
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import sys
from typing import Dict, List, Optional, Any, Union

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_core.models.yolo_coco_pretrained import YoloCOCOPretrainedDetector, detect_objects_coco

def create_example_image() -> bytes:
    """Crear una imagen de ejemplo con varios objetos reconocibles."""
    # Crear imagen base
    image = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(image)
    
    # Simular algunos objetos que YOLO podría reconocer
    # Rectangulos de diferentes colores y tamaños
    draw.rectangle([100, 100, 250, 200], fill='red', outline='darkred', width=3)      # Posible laptop/tv
    draw.rectangle([300, 150, 450, 300], fill='blue', outline='darkblue', width=3)   # Posible suitcase
    draw.rectangle([500, 80, 650, 180], fill='green', outline='darkgreen', width=3)  # Posible book
    
    # Círculos - podrían ser detectados como sports ball, etc.
    draw.ellipse([150, 300, 250, 400], fill='yellow', outline='orange', width=3)
    draw.ellipse([400, 350, 500, 450], fill='purple', outline='indigo', width=3)
    
    # Formas que podrían ser detectadas como objetos
    draw.rectangle([50, 450, 150, 550], fill='brown', outline='black', width=2)  # chair
    draw.rectangle([600, 400, 750, 550], fill='pink', outline='red', width=2)    # couch
    
    # Agregar texto
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), "Imagen de prueba YOLO COCO", fill='black', font=font)
    draw.text((10, 40), "Varios objetos para detección", fill='black', font=font)
    
    return image

def example_direct_usage():
    """Ejemplo de uso directo del detector."""
    print("🔬 Ejemplo 1: Uso directo del detector")
    print("=" * 50)
    
    # Crear imagen de ejemplo
    image = create_example_image()
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()
    
    print("📷 Imagen de prueba creada")
    
    # Crear detector
    print("🤖 Creando detector YOLO COCO...")
    detector = YoloCOCOPretrainedDetector(
        model_name="yolov8n.pt",    # Modelo más rápido
        conf_threshold=0.25,         # Umbral de confianza
        device="auto"                # Auto-detectar dispositivo
    )
    
    # Mostrar info del modelo
    info = detector.get_model_info()
    print(f"✅ Modelo cargado: {info['model_name']} en {info['device']}")
    
    # Ejecutar detección
    print("\n🔍 Ejecutando detección de objetos...")
    detections = detector.detect(image_bytes)
    
    print(f"📊 Resultados: {len(detections)} objetos detectados")
    
    # Mostrar detecciones
    if detections:
        print("\n📋 Detecciones encontradas:")
        for i, det in enumerate(detections[:5], 1):
            social_icon = "🎯" if det['social_relevant'] else "🔹"
            confidence = det['confidence']
            class_name = det['class_name']
            center = det['center']
            
            print(f"  {i}. {social_icon} {class_name}: {confidence:.3f} "
                  f"(centro: {center['x']}, {center['y']})")
    
    # Detección solo objetos sociales
    print("\n🎯 Detección solo objetos socialmente relevantes...")
    social_detections = detector.detect_social_objects(image_bytes)
    print(f"📊 Objetos sociales: {len(social_detections)}")
    
    for det in social_detections:
        print(f"  🎯 {det['class_name']}: {det['confidence']:.3f}")
    
    # Resumen estadístico
    print("\n📈 Generando resumen estadístico...")
    summary = detector.get_detection_summary(image_bytes)
    
    print(f"📊 Resumen:")
    print(f"  - Total objetos: {summary['total_objects']}")
    print(f"  - Socialmente relevantes: {summary['social_relevant']}")
    print(f"  - Confianza promedio: {summary['avg_confidence']:.3f}")
    print(f"  - Top 3 clases: {summary['top_classes'][:3]}")
    
    return True

def example_convenience_function():
    """Ejemplo usando la función de conveniencia."""
    print("\n🛠️ Ejemplo 2: Función de conveniencia")
    print("=" * 50)
    
    # Crear imagen
    image = create_example_image()
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()
    
    # Usar función de conveniencia
    print("🚀 Usando función de conveniencia...")
    detections = detect_objects_coco(
        image_bytes=image_bytes,
        model_name="yolov8n.pt",
        conf_threshold=0.3  # Un poco más estricto
    )
    
    print(f"📊 Función de conveniencia: {len(detections)} objetos")
    
    for det in detections[:3]:
        print(f"  🔹 {det['class_name']}: {det['confidence']:.3f}")
    
    return True

def example_api_usage():
    """Ejemplo usando la API REST."""
    print("\n🌐 Ejemplo 3: Uso vía API REST")
    print("=" * 50)
    
    API_BASE = "http://localhost:8000/api/v1"
    API_KEY = "dummy_development_key"
    HEADERS = {"X-API-Key": API_KEY}
    
    try:
        # Verificar que la API está corriendo
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=3)
        if response.status_code != 200:
            print("⚠️ API no está corriendo. Inicia con: uvicorn ml_core.api.main:app --port 8000")
            return False
        
        print("✅ API está corriendo")
        
        # Obtener modelos disponibles
        print("\n📋 Consultando modelos disponibles...")
        response = requests.get(f"{API_BASE}/coco_models", headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ {models['total_models']} modelos disponibles")
        
        # Crear imagen para detección
        image = create_example_image()
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()
        
        # Ejecutar detección via API
        print("\n🔍 Ejecutando detección via API...")
        
        files = {'file': ('example.jpg', image_bytes, 'image/jpeg')}
        params = {
            'model_name': 'yolov8n.pt',
            'conf_threshold': 0.25,
            'social_only': False
        }
        
        response = requests.post(
            f"{API_BASE}/coco_detect",
            headers=HEADERS,
            files=files,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API detección exitosa:")
            print(f"  - Total detecciones: {data['total_detections']}")
            print(f"  - Objetos sociales: {data['social_relevant_count']}")
            print(f"  - Tiempo: {data.get('processing_time_ms', 'N/A')}ms")
            
            for det in data['detections'][:3]:
                social_icon = "🎯" if det['social_relevant'] else "🔹"
                print(f"    {social_icon} {det['class_name']}: {det['confidence']:.3f}")
        
        # Obtener resumen via API
        print("\n📈 Obteniendo resumen via API...")
        
        files = {'file': ('example.jpg', image_bytes, 'image/jpeg')}
        params = {'model_name': 'yolov8n.pt', 'conf_threshold': 0.25}
        
        response = requests.post(
            f"{API_BASE}/coco_summary",
            headers=HEADERS,
            files=files,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data['summary']
            print(f"✅ Resumen via API:")
            print(f"  - Total: {summary['total_objects']}")
            print(f"  - Sociales: {summary['social_relevant']}")
            print(f"  - Confianza: {summary['avg_confidence']:.3f}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error conectando a API: {e}")
        print("💡 Asegúrate de que la API esté corriendo:")
        print("   uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def example_different_models():
    """Ejemplo comparando diferentes modelos YOLO."""
    print("\n⚖️ Ejemplo 4: Comparación de modelos")
    print("=" * 50)
    
    models_to_test = [
        ("yolov8n.pt", "Nano - Ultra rápido"),
        ("yolov8s.pt", "Small - Balance velocidad/precisión")
    ]
    
    # Crear imagen
    image = create_example_image()
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()
    
    results = {}
    
    for model_name, description in models_to_test:
        print(f"\n🧪 Probando {model_name} ({description})...")
        
        try:
            import time
            
            # Crear detector
            start_time = time.time()
            detector = YoloCOCOPretrainedDetector(model_name=model_name)
            load_time = (time.time() - start_time) * 1000
            
            # Ejecutar detección
            start_time = time.time()
            detections = detector.detect(image_bytes)
            inference_time = (time.time() - start_time) * 1000
            
            results[model_name] = {
                'detections': len(detections),
                'load_time': load_time,
                'inference_time': inference_time,
                'avg_confidence': sum(d['confidence'] for d in detections) / len(detections) if detections else 0
            }
            
            print(f"  ✅ {len(detections)} detecciones en {inference_time:.1f}ms")
            
        except Exception as e:
            print(f"  ❌ Error con {model_name}: {e}")
    
    # Mostrar comparación
    if results:
        print(f"\n📊 Comparación de modelos:")
        print(f"{'Modelo':<12} {'Detecciones':<12} {'Tiempo (ms)':<12} {'Confianza':<10}")
        print("-" * 50)
        
        for model, result in results.items():
            print(f"{model:<12} {result['detections']:<12} "
                  f"{result['inference_time']:<12.1f} {result['avg_confidence']:<10.3f}")
    
    return True

def main() -> None:
    """Ejecutar todos los ejemplos."""
    print("🎯 Ejemplos de uso del sistema YOLO COCO")
    print("=" * 60)
    
    examples = [
        example_direct_usage,
        example_convenience_function,
        example_api_usage,
        example_different_models
    ]
    
    success_count = 0
    
    for example in examples:
        try:
            if example():
                success_count += 1
        except Exception as e:
            print(f"❌ Ejemplo falló: {e}")
        
        print("")  # Separador
    
    print("=" * 60)
    print(f"🏁 Completados: {success_count}/{len(examples)} ejemplos")
    
    if success_count == len(examples):
        print("🎉 ¡Todos los ejemplos ejecutados exitosamente!")
    else:
        print("⚠️ Algunos ejemplos tuvieron problemas")
    
    print("\n💡 Próximos pasos:")
    print("  1. Experimenta con diferentes modelos (yolov8s.pt, yolov8m.pt, etc.)")
    print("  2. Ajusta umbrales de confianza según tus necesidades")
    print("  3. Usa social_only=True para filtrar objetos relevantes")
    print("  4. Integra en tu pipeline de procesamiento de imágenes")
    print("  5. Explora la documentación de la API en http://localhost:8000/docs")

if __name__ == "__main__":
    main()