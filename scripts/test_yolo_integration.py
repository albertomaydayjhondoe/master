#!/usr/bin/env python3
"""
Test script para verificar la integración de YOLOv8 en producción.
Prueba los modelos descargados y la API del ML Core.
"""
import sys
import os
import io
from pathlib import Path
from PIL import Image
import json
import asyncio

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.app_settings import is_dummy_mode
from ml_core.models.factory import get_yolo_screenshot_detector

async def test_yolo_integration():
    """Test completo de la integración YOLOv8."""
    print("🚀 Iniciando tests de integración YOLOv8...")
    
    # 1. Verificar modo de operación
    print(f"\n📊 Modo actual: {'DUMMY' if is_dummy_mode() else 'PRODUCTION'}")
    
    if is_dummy_mode():
        print("⚠️ Sistema en modo DUMMY. Para probar YOLOv8 real, configura DUMMY_MODE=false")
        return False
    
    # 2. Verificar modelos disponibles
    models_path = project_root / "data" / "models" / "production"
    print(f"\n📁 Verificando modelos en: {models_path}")
    
    required_models = [
        "tiktok_ui_detector.pt",
        "tiktok_video_analyzer.pt", 
        "anomaly_detector.pt"
    ]
    
    for model in required_models:
        model_path = models_path / model
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ {model} ({size_mb:.1f} MB)")
        else:
            print(f"  ❌ {model} - NO ENCONTRADO")
            return False
    
    # 3. Test de carga de modelo
    print("\n🔄 Probando carga de detector...")
    try:
        detector = get_yolo_screenshot_detector(
            model_path=str(models_path / "tiktok_ui_detector.pt"),
            device="cpu"  # Usar CPU para test
        )
        print("  ✅ Detector cargado correctamente")
    except Exception as e:
        print(f"  ❌ Error cargando detector: {e}")
        return False
    
    # 4. Test de inferencia con imagen sintética
    print("\n🖼️ Probando detección con imagen de prueba...")
    try:
        # Crear imagen de prueba que simule una interfaz TikTok
        test_img = Image.new('RGB', (1080, 1920), color='black')
        
        # Simular elementos de UI típicos de TikTok
        from PIL import ImageDraw
        draw = ImageDraw.Draw(test_img)
        
        # Fondo degradado
        for y in range(1920):
            color = int(128 + 127 * (y / 1920))
            draw.line([(0, y), (1080, y)], fill=(color//3, color//2, color))
        
        # "Botones" simulados
        # Like button (corazón)
        draw.ellipse([950, 800, 1020, 870], fill=(255, 100, 100))
        
        # Comment button
        draw.ellipse([950, 900, 1020, 970], fill=(255, 255, 255))
        
        # Share button  
        draw.ellipse([950, 1000, 1020, 1070], fill=(255, 255, 100))
        
        # Profile area
        draw.ellipse([950, 600, 1020, 670], fill=(150, 150, 255))
        
        # Video player area (centro)
        draw.rectangle([100, 300, 900, 1600], fill=(50, 50, 50))
        
        # Convertir a bytes
        img_buffer = io.BytesIO()
        test_img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Ejecutar detección
        detections = detector.detect(img_bytes)
        
        print(f"  ✅ Inferencia completada: {len(detections)} detecciones")
        
        # Mostrar resultados
        if detections:
            print("  📍 Detecciones encontradas:")
            for i, detection in enumerate(detections[:5]):  # Solo primeras 5
                print(f"    {i+1}. {detection['type']} - Confianza: {detection['confidence']:.3f}")
        else:
            print("  ℹ️ No se encontraron detecciones (normal con imagen sintética)")
            
    except Exception as e:
        print(f"  ❌ Error en inferencia: {e}")
        return False
    
    # 5. Test de configuración ML
    print("\n⚙️ Verificando configuración ML...")
    try:
        from ml_core.api.main import app
        print("  ✅ API ML Core importada correctamente")
        
        # Verificar endpoints
        from ml_core.api.endpoints.screenshot_analysis import router
        print("  ✅ Endpoint de screenshot_analysis disponible")
        
    except Exception as e:
        print(f"  ❌ Error verificando API: {e}")
        return False
    
    # 6. Test de performance básico
    print("\n⚡ Test de performance...")
    try:
        import time
        
        # Crear imagen más pequeña para test de velocidad
        small_img = Image.new('RGB', (640, 640), color='red')
        img_buffer = io.BytesIO()
        small_img.save(img_buffer, format='JPEG', quality=85)
        img_bytes = img_buffer.getvalue()
        
        # Medir tiempo de inferencia
        start_time = time.time()
        for _ in range(3):
            results = detector.detect(img_bytes)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 3
        print(f"  ✅ Tiempo promedio de inferencia: {avg_time:.3f}s")
        
        if avg_time < 2.0:
            print("  🚀 Performance: EXCELENTE")
        elif avg_time < 5.0:
            print("  ⚡ Performance: BUENA")
        else:
            print("  🐌 Performance: LENTA (considerar GPU)")
            
    except Exception as e:
        print(f"  ❌ Error en test de performance: {e}")
        return False
    
    print("\n🎉 ¡Todos los tests de YOLOv8 completados exitosamente!")
    return True

def test_ml_api_startup():
    """Test de arranque de la API ML."""
    print("\n🌐 Testing ML API startup...")
    
    try:
        # Import ML API
        from ml_core.api.main import app
        print("  ✅ FastAPI app importada")
        
        # Test configuración
        from ml_core.api.endpoints import screenshot_analysis, anomaly_detection
        print("  ✅ Endpoints importados correctamente")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en startup de API: {e}")
        return False

async def main():
    """Función principal de tests."""
    print("=" * 60)
    print("🧪 SUITE DE TESTS - INTEGRACIÓN YOLOV8 PRODUCTION")
    print("=" * 60)
    
    success = True
    
    # Test 1: Integración YOLOv8
    if not await test_yolo_integration():
        success = False
    
    # Test 2: API ML Startup
    if not test_ml_api_startup():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 RESULTADO: ¡TODOS LOS TESTS PASARON!")
        print("✅ Sistema YOLOv8 listo para producción")
        print("\n🚀 Próximos pasos:")
        print("   1. Inicia ML Core API: python ml_core/api/main.py")
        print("   2. Prueba endpoints en http://localhost:8000/docs")
        print("   3. Integra con dispositivos y GoLogin")
    else:
        print("❌ RESULTADO: ALGUNOS TESTS FALLARON")
        print("🔧 Revisa la configuración antes de continuar")
    
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)