#!/usr/bin/env python3
"""
🎬 Validador de Integración LongCat Video
Valida que la sustitución de Runway por LongCat está completa y funcional
"""

import os
import sys
import asyncio
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def validate_runway_cleanup():
    """Validar que no queden rastros de Runway"""
    print("🧹 Validando limpieza de Runway...")
    
    # Archivos a verificar
    files_to_check = [
        "requirements.txt",
        "requirements-meta-py312.txt", 
        "requirements-ml.txt",
        "pyproject.toml"
    ]
    
    runway_found = False
    
    for filename in files_to_check:
        filepath = root_dir / filename
        if filepath.exists():
            content = filepath.read_text()
            if "runway" in content.lower():
                print(f"❌ Runway encontrado en {filename}")
                runway_found = True
    
    if not runway_found:
        print("✅ Limpieza de Runway completada")
    
    return not runway_found

def validate_longcat_module():
    """Validar que el módulo LongCat está correctamente implementado"""
    print("🎬 Validando módulo LongCat Video...")
    
    try:
        # Verificar estructura de archivos
        module_dir = root_dir / "ml_core" / "video_generation"
        required_files = [
            "__init__.py",
            "longcat_generator.py", 
            "longcat_api.py"
        ]
        
        for filename in required_files:
            filepath = module_dir / filename
            if not filepath.exists():
                print(f"❌ Archivo faltante: {filepath}")
                return False
            else:
                print(f"✅ {filename} presente")
        
        # Verificar imports
        from ml_core.video_generation import create_video_generator, LongCatVideoGenerator
        print("✅ Imports correctos")
        
        # Verificar creación de generador
        config = {
            "output_dir": "data/generated_videos",
            "models_dir": "data/models/longcat"
        }
        generator = create_video_generator(config)
        print("✅ Generador creado correctamente")
        
        # Verificar métodos principales
        assert hasattr(generator, 'generate_text_to_video')
        assert hasattr(generator, 'generate_image_to_video')
        assert hasattr(generator, 'get_capabilities')
        print("✅ Métodos principales disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validando módulo LongCat: {e}")
        return False

def validate_api_integration():
    """Validar integración con FastAPI"""
    print("🚀 Validando integración FastAPI...")
    
    try:
        from ml_core.video_generation.longcat_api import longcat_router
        print("✅ Router FastAPI importado correctamente")
        
        # Verificar endpoints (considerando el prefijo del router)
        routes = [route.path for route in longcat_router.routes]
        expected_routes = [
            "/generate/text-to-video",
            "/generate/image-to-video", 
            "/health",
            "/capabilities"
        ]
        
        for expected_route in expected_routes:
            # Buscar la ruta con o sin prefijo
            route_found = any(route.endswith(expected_route) for route in routes)
            if route_found:
                print(f"✅ Endpoint {expected_route} disponible")
            else:
                print(f"❌ Endpoint {expected_route} faltante")
                print(f"   Rutas disponibles: {routes}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validando API: {e}")
        return False

def validate_dashboard_integration():
    """Validar integración con dashboard de producción"""
    print("📊 Validando integración con dashboard...")
    
    try:
        # Verificar imports en production_controller
        controller_file = root_dir / "production_controller.py"
        if not controller_file.exists():
            print("❌ production_controller.py no encontrado")
            return False
        
        content = controller_file.read_text()
        
        # Verificar imports
        if "from ml_core.video_generation import create_video_generator" in content:
            print("✅ Import de video_generation presente")
        else:
            print("❌ Import de video_generation faltante")
            return False
        
        # Verificar inicialización
        if "self.video_generator" in content:
            print("✅ Inicialización del generador presente")
        else:
            print("❌ Inicialización del generador faltante")
            return False
        
        # Verificar UI elements
        if "🎬 LongCat Video Generation" in content:
            print("✅ Elementos UI de video generación presentes")
        else:
            print("❌ Elementos UI de video generación faltantes")
            return False
        
        # Verificar parámetros en método launch
        if "video_generation: bool = False" in content and "video_prompt: str = \"\"" in content:
            print("✅ Parámetros de video generación en método launch")
        else:
            print("❌ Parámetros de video generación faltantes en método launch")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validando dashboard: {e}")
        return False

async def validate_dummy_functionality():
    """Validar funcionalidad en modo dummy"""
    print("🎭 Validando funcionalidad dummy...")
    
    try:
        from ml_core.video_generation import create_video_generator
        
        config = {
            "output_dir": "data/generated_videos",
            "models_dir": "data/models/longcat"
        }
        
        generator = create_video_generator(config)
        await generator.initialize()
        print("✅ Inicialización async correcta")
        
        # Probar generación text-to-video
        result = await generator.generate_text_to_video(
            prompt="test video generation",
            duration=5,
            output_name="validation_test"
        )
        
        if result.success:
            print("✅ Generación text-to-video funcional")
        else:
            print(f"❌ Error en text-to-video: {result.error}")
            return False
        
        # Probar capabilities
        capabilities = await generator.get_capabilities()
        if capabilities:
            print("✅ Capabilities disponibles")
            print(f"   - Formatos: {capabilities.get('supported_formats', [])}")
            print(f"   - Resoluciones: {capabilities.get('max_resolution', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validando funcionalidad dummy: {e}")
        return False

def main():
    """Ejecutar validación completa"""
    print("🎬 VALIDADOR DE INTEGRACIÓN LONGCAT VIDEO")
    print("=" * 50)
    
    validations = [
        ("Limpieza Runway", validate_runway_cleanup()),
        ("Módulo LongCat", validate_longcat_module()),
        ("Integración API", validate_api_integration()),
        ("Integración Dashboard", validate_dashboard_integration())
    ]
    
    # Validación async
    async_result = asyncio.run(validate_dummy_functionality())
    validations.append(("Funcionalidad Dummy", async_result))
    
    print("\n📋 RESUMEN DE VALIDACIÓN")
    print("=" * 50)
    
    all_passed = True
    for name, passed in validations:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 VALIDACIÓN COMPLETA: INTEGRACIÓN LONGCAT EXITOSA")
        print("🚀 Sistema listo para producción con LongCat Video")
    else:
        print("❌ VALIDACIÓN FALLIDA: Corregir errores antes de continuar")
        sys.exit(1)

if __name__ == "__main__":
    main()