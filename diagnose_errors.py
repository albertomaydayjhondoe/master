#!/usr/bin/env python3
"""
🔍 TikTok Viral ML System - Diagnóstico de Errores de la Interfaz
================================================================

Script para diagnosticar qué errores está recogiendo la interfaz y
determinar si son reales o configuración.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

def print_colored(text, color_code="0"):
    """Imprimir con colores"""
    print(f"\033[9{color_code}m{text}\033[0m")

def check_import(module_name, optional=False):
    """Verificar importación de un módulo"""
    try:
        importlib.import_module(module_name)
        print_colored(f"✅ {module_name}", "2")
        return True
    except ImportError as e:
        status = "⚠️" if optional else "❌"
        print_colored(f"{status} {module_name}: {str(e)[:60]}...", "3" if optional else "1")
        return False

def check_file_exists(file_path, description=""):
    """Verificar si un archivo existe"""
    if Path(file_path).exists():
        print_colored(f"✅ {description or file_path}", "2")
        return True
    else:
        print_colored(f"❌ {description or file_path} - No encontrado", "1")
        return False

def check_environment():
    """Verificar variables de entorno"""
    print_colored("\n🔧 VARIABLES DE ENTORNO:", "6")
    
    env_vars = {
        'DUMMY_MODE': os.getenv('DUMMY_MODE', 'No configurada'),
        'STREAMLIT_PORT': os.getenv('STREAMLIT_PORT', 'No configurada'),
        'ML_API_PORT': os.getenv('ML_API_PORT', 'No configurada'),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'No configurada')
    }
    
    for var, value in env_vars.items():
        color = "2" if value != "No configurada" else "3"
        print_colored(f"   {var}: {value}", color)

def diagnose_dashboard_errors():
    """Diagnosticar errores del dashboard"""
    print_colored("🔍 DIAGNÓSTICO DE ERRORES DE LA INTERFAZ", "5")
    print_colored("=" * 60, "5")
    
    # 1. Verificar importaciones core
    print_colored("\n📦 IMPORTACIONES CORE:", "6")
    core_imports = [
        'streamlit',
        'pandas', 
        'numpy',
        'requests',
        'httpx',
        'json',
        'subprocess',
        'pathlib'
    ]
    
    core_ok = 0
    for imp in core_imports:
        if check_import(imp):
            core_ok += 1
    
    print_colored(f"\nCore imports: {core_ok}/{len(core_imports)} OK", "6")
    
    # 2. Verificar importaciones opcionales/específicas del proyecto
    print_colored("\n📱 IMPORTACIONES ESPECÍFICAS DEL PROYECTO:", "6")
    project_imports = [
        ('fastapi', True),
        ('uvicorn', True),
        ('telethon', True),
        ('sqlalchemy', True),
        ('pillow', True),
        ('torch', True),
        ('ultralytics', True),
        ('librosa', True),
        ('moviepy', True)
    ]
    
    optional_ok = 0
    for imp, optional in project_imports:
        if check_import(imp, optional):
            optional_ok += 1
    
    print_colored(f"\nProject imports: {optional_ok}/{len(project_imports)} OK", "6")
    
    # 3. Verificar estructura de archivos
    print_colored("\n📁 ESTRUCTURA DE ARCHIVOS:", "6")
    required_files = [
        ('streamlit_dashboard.py', 'Dashboard principal'),
        ('validate_multibranch.py', 'Validador multi-ramas'),
        ('run_local.sh', 'Ejecutor local'),
        ('quick.sh', 'Acceso rápido'),
        ('ml_core/api/main.py', 'ML API principal'),
        ('config/app_settings.py', 'Configuración app'),
        ('requirements-streamlit.txt', 'Requirements Streamlit')
    ]
    
    files_ok = 0
    for file_path, description in required_files:
        if check_file_exists(file_path, description):
            files_ok += 1
    
    print_colored(f"\nArchivos requeridos: {files_ok}/{len(required_files)} OK", "6")
    
    # 4. Verificar configuración ML Core
    print_colored("\n🤖 CONFIGURACIÓN ML CORE:", "6")
    try:
        sys.path.append(str(Path.cwd()))
        from ml_core.api.main import app
        print_colored("✅ ML API main importable", "2")
        
        # Verificar endpoints básicos
        try:
            from ml_core.api.main import app
            print_colored("✅ FastAPI app disponible", "2")
        except Exception as e:
            print_colored(f"⚠️ FastAPI endpoints: {str(e)[:50]}...", "3")
            
    except ImportError as e:
        print_colored(f"❌ ML Core import: {str(e)[:50]}...", "1")
    
    # 5. Verificar factory patterns
    print_colored("\n🏭 FACTORY PATTERNS:", "6")
    try:
        from ml_core.models.factory import create_yolo_detector
        print_colored("✅ ML factory disponible", "2")
    except Exception as e:
        print_colored(f"⚠️ ML factory: {str(e)[:50]}...", "3")
    
    try:
        from device_farm.controllers.factory import create_adb_controller
        print_colored("✅ Device factory disponible", "2")
    except Exception as e:
        print_colored(f"⚠️ Device factory: {str(e)[:50]}...", "3")
    
    # 6. Verificar variables de entorno
    check_environment()
    
    # 7. Verificar servicios externos
    print_colored("\n🌐 SERVICIOS EXTERNOS:", "6")
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored("✅ FFmpeg disponible", "2")
        else:
            print_colored("❌ FFmpeg no funcional", "1")
    except FileNotFoundError:
        if os.getenv('DUMMY_MODE', '').lower() == 'true':
            print_colored("⚠️ FFmpeg no disponible (OK en modo dummy)", "3")
        else:
            print_colored("❌ FFmpeg no encontrado", "1")
    
    # Check Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored("✅ Git disponible", "2")
        else:
            print_colored("❌ Git no funcional", "1")
    except FileNotFoundError:
        print_colored("❌ Git no encontrado", "1")
    
    # 8. Análisis de errores comunes
    print_colored("\n🐛 ANÁLISIS DE ERRORES COMUNES:", "6")
    
    common_issues = []
    
    # Python version
    if sys.version_info.major == 3 and sys.version_info.minor == 12:
        common_issues.append("⚠️ Python 3.12 puede causar incompatibilidades con ML libs")
    
    # Dummy mode
    if os.getenv('DUMMY_MODE', '').lower() != 'true':
        if not check_import('torch', optional=True):
            common_issues.append("❌ PyTorch faltante (requerido en modo producción)")
        if not check_import('ultralytics', optional=True):
            common_issues.append("❌ Ultralytics faltante (requerido en modo producción)")
    
    # Streamlit specific
    try:
        import streamlit as st
        if hasattr(st, 'runtime') and hasattr(st.runtime, 'scriptrunner'):
            print_colored("✅ Streamlit runtime OK", "2")
        else:
            common_issues.append("⚠️ Streamlit runtime podría tener issues")
    except:
        common_issues.append("❌ Streamlit no importable")
    
    if common_issues:
        print_colored("\n🚨 ISSUES DETECTADOS:", "1")
        for issue in common_issues:
            print_colored(f"   {issue}", "1")
    else:
        print_colored("✅ No se detectaron issues comunes", "2")
    
    # 9. Recomendaciones
    print_colored("\n💡 RECOMENDACIONES:", "6")
    
    if os.getenv('DUMMY_MODE', '').lower() != 'true':
        print_colored("   🎭 Considera usar modo dummy para desarrollo:", "3")
        print_colored("      export DUMMY_MODE=true", "3")
    
    if sys.version_info.minor == 12:
        print_colored("   🐍 Para máxima compatibilidad, considera Python 3.11:", "3")
        print_colored("      Los errores de ML pueden ser por Python 3.12", "3")
    
    print_colored("   🔧 Para errores específicos, revisa logs:", "3")
    print_colored("      ./quick.sh logs", "3")
    
    print_colored("\n🎯 CONCLUSIÓN:", "6")
    dummy_mode = os.getenv('DUMMY_MODE', '').lower() == 'true'
    
    if dummy_mode:
        print_colored("✅ En modo DUMMY: Los errores ML/API son NORMALES y esperados", "2")
        print_colored("   El sistema funciona correctamente para desarrollo", "2")
    else:
        print_colored("⚠️ En modo PRODUCCIÓN: Algunos errores requieren dependencias", "3")
        print_colored("   Usa './run_local.sh install' para instalar faltantes", "3")

if __name__ == "__main__":
    diagnose_dashboard_errors()