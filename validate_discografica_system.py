#!/usr/bin/env python3
"""
🎵 VALIDADOR RÁPIDO - DISCOGRÁFICA ML CON LONGCAT-VIDEO
=====================================================
Script de verificación rápida del sistema completo
"""

import os
import sys
import subprocess
from pathlib import Path
import importlib.util

def print_status(message, status, details=None):
    """Imprimir estado con colores"""
    colors = {
        'ok': '\033[92m✅',      # Verde
        'error': '\033[91m❌',    # Rojo  
        'warning': '\033[93m⚠️', # Amarillo
        'info': '\033[94mℹ️',     # Azul
        'reset': '\033[0m'       # Reset
    }
    
    color = colors.get(status, colors['info'])
    reset = colors['reset']
    print(f"{color} {message}{reset}")
    
    if details:
        print(f"   {details}")

def check_module(module_name, description):
    """Verificar si un módulo está disponible"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            print_status(f"{description}", "ok")
            return True
        else:
            print_status(f"{description}", "error", f"Módulo '{module_name}' no encontrado")
            return False
    except Exception as e:
        print_status(f"{description}", "error", str(e))
        return False

def check_longcat_integration():
    """Verificar integración completa de LongCat"""
    try:
        from ml_core.video_generation import create_video_generator, LongCatVideoGenerator
        from ml_core.video_generation.longcat_api import longcat_router
        
        # Crear generador de prueba
        generator = create_video_generator({})
        
        # Verificar métodos principales
        assert hasattr(generator, 'generate_text_to_video')
        assert hasattr(generator, 'generate_image_to_video')
        assert hasattr(generator, 'get_capabilities')
        
        print_status("LongCat-Video completamente integrado", "ok")
        return True
        
    except Exception as e:
        print_status("LongCat-Video integration", "error", str(e))
        return False

def check_dashboard_integration():
    """Verificar integración con dashboard"""
    try:
        controller_file = Path("production_controller.py")
        if not controller_file.exists():
            print_status("Dashboard integration", "error", "production_controller.py no encontrado")
            return False
        
        content = controller_file.read_text()
        
        checks = [
            ("video_generation import", "from ml_core.video_generation import create_video_generator"),
            ("video generator initialization", "self.video_generator"),  
            ("video UI controls", "🎬 LongCat Video Generation"),
            ("video parameters", "video_generation: bool = False")
        ]
        
        for check_name, search_text in checks:
            if search_text in content:
                print_status(f"Dashboard: {check_name}", "ok")
            else:
                print_status(f"Dashboard: {check_name}", "error")
                return False
        
        return True
        
    except Exception as e:
        print_status("Dashboard integration", "error", str(e))
        return False

def check_file_structure():
    """Verificar estructura de archivos"""
    required_files = [
        ("ml_core/video_generation/__init__.py", "Módulo video generation"),
        ("ml_core/video_generation/longcat_generator.py", "LongCat generator"),
        ("ml_core/video_generation/longcat_api.py", "LongCat API"),
        ("production_controller.py", "Dashboard principal"),
        ("requirements.txt", "Dependencias principales")
    ]
    
    all_ok = True
    for filepath, description in required_files:
        if Path(filepath).exists():
            print_status(description, "ok")
        else:
            print_status(description, "error", f"Archivo {filepath} no encontrado")
            all_ok = False
    
    return all_ok

def main():
    """Ejecutar validación completa"""
    print("🎵 VALIDADOR RÁPIDO - DISCOGRÁFICA ML CON LONGCAT-VIDEO")
    print("=" * 55)
    print()
    
    checks = []
    
    # 1. Estructura de archivos
    print("📁 ESTRUCTURA DE ARCHIVOS")
    checks.append(("Estructura archivos", check_file_structure()))
    print()
    
    # 2. Dependencias Python  
    print("🐍 DEPENDENCIAS PYTHON")
    python_modules = [
        ("torch", "PyTorch (ML backend)"),
        ("transformers", "HuggingFace Transformers"), 
        ("diffusers", "Diffusion models"),
        ("gradio", "Dashboard Gradio"),
        ("fastapi", "API backend"),
        ("ultralytics", "YOLO models")
    ]
    
    for module, desc in python_modules:
        checks.append((desc, check_module(module, desc)))
    print()
    
    # 3. Integración LongCat
    print("🎬 INTEGRACIÓN LONGCAT-VIDEO")
    checks.append(("LongCat integration", check_longcat_integration()))
    print()
    
    # 4. Dashboard
    print("📊 DASHBOARD INTEGRATION")  
    checks.append(("Dashboard integration", check_dashboard_integration()))
    print()
    
    # 5. GPU Check (opcional)
    print("🚀 ACELERACIÓN GPU")
    try:
        import torch
        if torch.cuda.is_available():
            print_status(f"GPU disponible: {torch.cuda.get_device_name()}", "ok")
            gpu_ok = True
        else:
            print_status("GPU no disponible (usando CPU)", "warning", "Generación será más lenta")
            gpu_ok = True  # No crítico
    except:
        print_status("PyTorch no disponible", "error")
        gpu_ok = False
    
    checks.append(("GPU/PyTorch", gpu_ok))
    print()
    
    # Resumen final
    print("📋 RESUMEN FINAL")
    print("=" * 20)
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    for check_name, status in checks:
        status_text = "✅ PASS" if status else "❌ FAIL"
        print(f"{check_name}: {status_text}")
    
    print()
    percentage = (passed / total) * 100
    
    if percentage == 100:
        print_status(f"🎉 SISTEMA COMPLETAMENTE OPERATIVO ({passed}/{total})", "ok")
        print_status("🚀 Listo para lanzar campañas con LongCat-Video!", "info")
        return 0
    elif percentage >= 80:
        print_status(f"⚡ Sistema mayormente funcional ({passed}/{total})", "warning")
        print_status("🔧 Corrige errores menores para 100% funcionalidad", "info")
        return 1
    else:
        print_status(f"❌ Sistema requiere reparación ({passed}/{total})", "error")
        print_status("🛠️ Ejecuta setup y corrige errores antes de continuar", "info")
        return 2

if __name__ == "__main__":
    sys.exit(main())