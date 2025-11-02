#!/usr/bin/env python3
"""
Test de endpoints COCO de la API
"""

import requests
import time
from PIL import Image, ImageDraw
import io
import json
from typing import Dict, List, Optional, Any, Union

API_BASE = "http://localhost:8000/api/v1"
API_KEY = "dummy_development_key"
HEADERS = {"X-API-Key": API_KEY}

def create_test_image() -> bytes:
    """Crear imagen de prueba con formas."""
    image = Image.new('RGB', (640, 480), color='lightblue')
    draw = ImageDraw.Draw(image)
    
    # Agregar formas que podrían detectarse
    draw.rectangle([100, 100, 200, 200], fill='red')
    draw.rectangle([300, 200, 400, 350], fill='blue') 
    draw.ellipse([450, 50, 550, 150], fill='green')
    draw.rectangle([50, 300, 150, 400], fill='yellow')
    
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()

def test_health() -> None:
    """Test endpoint de salud."""
    print("🧪 Test: Health endpoint")
    
    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API está corriendo")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando API: {e}")
        return False

def test_coco_models() -> None:
    """Test endpoint de modelos."""
    print("\n🧪 Test: COCO Models endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/coco_models", headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Modelos disponibles: {data['total_models']}")
            print(f"  - Modelo por defecto: {data['default_model']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_coco_classes() -> None:
    """Test endpoint de clases."""
    print("\n🧪 Test: COCO Classes endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/coco_classes", headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Clases COCO: {data['total_classes']}")
            print(f"  - Socialmente relevantes: {data['social_relevant_count']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_coco_test() -> None:
    """Test endpoint de test."""
    print("\n🧪 Test: COCO Test endpoint")
    
    try:
        response = requests.get(f"{API_BASE}/coco_test", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['test_passed']:
                print("✅ Test interno pasó")
                print(f"  - Modelo: {data['model_info']['model_name']}")
                print(f"  - Dispositivo: {data['model_info']['device']}")
                return True
            else:
                print(f"❌ Test interno falló: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_coco_detection() -> None:
    """Test endpoint de detección."""
    print("\n🧪 Test: COCO Detection endpoint")
    
    try:
        image_bytes = create_test_image()
        
        files = {'file': ('test.jpg', image_bytes, 'image/jpeg')}
        params = {
            'model_name': 'yolov8n.pt',
            'conf_threshold': 0.25,
            'social_only': False
        }
        
        print("🔄 Subiendo imagen y ejecutando detección...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/coco_detect",
            headers=HEADERS,
            files=files,
            params=params,
            timeout=30
        )
        
        request_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detección exitosa en {request_time:.1f}ms")
            print(f"  - Total detecciones: {data['total_detections']}")
            print(f"  - Objetos sociales: {data['social_relevant_count']}")
            print(f"  - Tiempo inferencia: {data.get('processing_time_ms', 'N/A')}ms")
            
            # Mostrar primeras detecciones
            for i, det in enumerate(data['detections'][:3]):
                social_icon = "🎯" if det['social_relevant'] else "🔹"
                print(f"    {social_icon} {det['class_name']}: {det['confidence']:.3f}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"    Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_coco_summary() -> None:
    """Test endpoint de resumen."""
    print("\n🧪 Test: COCO Summary endpoint")
    
    try:
        image_bytes = create_test_image()
        
        files = {'file': ('test.jpg', image_bytes, 'image/jpeg')}
        params = {
            'model_name': 'yolov8n.pt',
            'conf_threshold': 0.25
        }
        
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
            print("✅ Resumen generado")
            print(f"  - Total objetos: {summary['total_objects']}")
            print(f"  - Socialmente relevantes: {summary['social_relevant']}")
            print(f"  - Confianza promedio: {summary['avg_confidence']:.3f}")
            print(f"  - Top clases: {summary['top_classes'][:3]}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_social_only() -> None:
    """Test detección solo objetos sociales."""
    print("\n🧪 Test: Solo objetos sociales")
    
    try:
        image_bytes = create_test_image()
        
        files = {'file': ('test.jpg', image_bytes, 'image/jpeg')}
        params = {
            'model_name': 'yolov8n.pt',
            'conf_threshold': 0.25,
            'social_only': True
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
            print(f"✅ Solo sociales: {data['total_detections']} objetos")
            
            # Verificar que todos son sociales
            all_social = all(det['social_relevant'] for det in data['detections'])
            if all_social:
                print("✅ Todos los objetos son socialmente relevantes")
            else:
                print("⚠️ Algunos objetos no son socialmente relevantes")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main() -> None:
    """Ejecutar todos los tests."""
    print("🚀 Tests de endpoints COCO API")
    print("=" * 60)
    
    tests = [
        test_health,
        test_coco_models,
        test_coco_classes,
        test_coco_test,
        test_coco_detection,
        test_coco_summary,
        test_social_only
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test falló con excepción: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los endpoints COCO funcionan perfectamente!")
    else:
        print(f"⚠️ {total - passed} tests fallaron")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)