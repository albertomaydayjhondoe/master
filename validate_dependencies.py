#!/usr/bin/env python3
"""
Validador de Dependencias - TikTok Viral ML System
==================================================
Script que verifica que todas las dependencias estén correctamente instaladas
según la rama y configuración actual.
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path
from datetime import datetime

def log_info(msg):
    print(f"[INFO] {msg}")

def log_success(msg):
    print(f"✅ {msg}")

def log_warning(msg):
    print(f"⚠️  {msg}")

def log_error(msg):
    print(f"❌ {msg}")

def log_header(msg):
    print(f"\n🔍 {msg}")
    print("=" * (len(msg) + 4))

def check_import(module_name, optional=False):
    """Verifica si un módulo puede importarse"""
    try:
        importlib.import_module(module_name)
        log_success(f"{module_name}")
        return True
    except ImportError as e:
        if optional:
            log_warning(f"{module_name} (opcional) - {str(e)}")
        else:
            log_error(f"{module_name} - {str(e)}")
        return False

def get_current_branch():
    """Obtiene la rama Git actual"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        return "unknown"

def check_system_dependencies():
    """Verifica dependencias del sistema"""
    log_header("DEPENDENCIAS DEL SISTEMA")
    
    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    log_info(f"Python version: {python_version}")
    
    if python_version < "3.9" or python_version > "3.11":
        log_warning(f"Python {python_version} puede causar incompatibilidades. Recomendado: 3.9-3.11")
    else:
        log_success(f"Python {python_version} es compatible")
    
    # Git
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        log_success("Git instalado")
    except:
        log_error("Git no encontrado")
    
    # FFmpeg (para procesamiento de video)
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        log_success("FFmpeg instalado")
    except:
        log_warning("FFmpeg no encontrado (requerido para procesamiento de video)")
    
    return True

def check_core_dependencies():
    """Verifica dependencias core compartidas"""
    log_header("DEPENDENCIAS CORE (COMPARTIDAS)")
    
    core_deps = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "sqlalchemy",
        "httpx",
        "aiohttp",
        "requests",
        "numpy",
        "pandas",
        "pillow"
    ]
    
    success_count = 0
    for dep in core_deps:
        if check_import(dep):
            success_count += 1
    
    log_info(f"Dependencias core: {success_count}/{len(core_deps)} ✅")
    return success_count == len(core_deps)

def check_rama_dependencies():
    """Verifica dependencias específicas de RAMA MAIN"""
    log_header("DEPENDENCIAS RAMA MAIN - ML + Device Farm")
    
    ml_deps = [
        "torch",
        "torchvision", 
        "ultralytics",
        "opencv",  # opencv-python
        "sklearn",  # scikit-learn
    ]
    
    device_deps = [
        "appium",  # appium-python-client
        "uiautomator2",
        "selenium"
    ]
    
    audio_deps = [
        "librosa",
        "soundfile"
    ]
    
    success_count = 0
    total_deps = len(ml_deps) + len(device_deps) + len(audio_deps)
    
    log_info("Dependencias ML:")
    for dep in ml_deps:
        if check_import(dep):
            success_count += 1
    
    log_info("Dependencias Device Farm:")
    for dep in device_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    log_info("Dependencias Audio (Módulo 7):")
    for dep in audio_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    # Verificaciones especiales
    if check_import("torch"):
        try:
            import torch
            log_info(f"PyTorch version: {torch.__version__}")
            log_info(f"CUDA disponible: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                log_info(f"Dispositivos CUDA: {torch.cuda.device_count()}")
        except:
            pass
    
    if check_import("ultralytics"):
        try:
            try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
            log_success("YOLOv8 disponible")
        except:
            log_warning("YOLOv8 no puede inicializarse")
    
    log_info(f"Dependencias RAMA: {success_count}/{total_deps}")
    return success_count >= total_deps * 0.7  # 70% success rate

def check_meta_dependencies():
    """Verifica dependencias específicas de RAMA META"""
    log_header("DEPENDENCIAS RAMA META - Meta Ads + GoLogin")
    
    meta_deps = [
        "facebook_business",  # facebook-business
        "selenium",
        "playwright",
        "requests"
    ]
    
    browser_deps = [
        "undetected_chromedriver",
        "webdriver_manager"
    ]
    
    success_count = 0
    total_deps = len(meta_deps) + len(browser_deps)
    
    log_info("Dependencias Meta Ads:")
    for dep in meta_deps:
        if check_import(dep):
            success_count += 1
    
    log_info("Dependencias Browser Automation:")
    for dep in browser_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    log_info(f"Dependencias META: {success_count}/{total_deps}")
    return success_count >= total_deps * 0.7

def check_tele_dependencies():
    """Verifica dependencias específicas de RAMA TELE"""
    log_header("DEPENDENCIAS RAMA TELE - Telegram + Social")
    
    telegram_deps = [
        "telethon",
        "telegram",  # python-telegram-bot
        "pyrogram"
    ]
    
    social_deps = [
        "instagrapi",
        "tweepy"
    ]
    
    success_count = 0
    total_deps = len(telegram_deps) + len(social_deps)
    
    log_info("Dependencias Telegram:")
    for dep in telegram_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    log_info("Dependencias Social Media:")
    for dep in social_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    log_info(f"Dependencias TELE: {success_count}/{total_deps}")
    return success_count >= total_deps * 0.7

def check_modulo7_dependencies():
    """Verifica dependencias específicas del Módulo 7"""
    log_header("DEPENDENCIAS MÓDULO 7 - Sincronización Semántico Visual")
    
    audio_deps = [
        "librosa",
        "soundfile", 
        "torch_audio",  # torchaudio
    ]
    
    video_deps = [
        "moviepy",
        "imageio",
        "cv2"  # opencv-python
    ]
    
    ml_deps = [
        "transformers",
        "sentence_transformers"
    ]
    
    success_count = 0
    total_deps = len(audio_deps) + len(video_deps) + len(ml_deps)
    
    log_info("Análisis de Audio:")
    for dep in audio_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    log_info("Procesamiento de Video:")
    for dep in video_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    log_info("ML Avanzado:")
    for dep in ml_deps:
        if check_import(dep, optional=True):
            success_count += 1
    
    log_info(f"Dependencias MÓDULO 7: {success_count}/{total_deps}")
    return success_count >= total_deps * 0.5

def check_file_structure():
    """Verifica estructura de archivos necesaria"""
    log_header("ESTRUCTURA DE ARCHIVOS")
    
    required_files = [
        "requirements.txt",
        "requirements-rama.txt",
        "requirements-meta.txt", 
        "requirements-tele.txt",
        "requirements-dummy.txt",
        ".env",
        "ml_core/api/main.py"
    ]
    
    required_dirs = [
        "data",
        "logs",
        "config",
        "ml_core",
        "social_extensions"
    ]
    
    success_count = 0
    
    log_info("Archivos requeridos:")
    for file_path in required_files:
        if Path(file_path).exists():
            log_success(file_path)
            success_count += 1
        else:
            log_error(f"{file_path} no encontrado")
    
    log_info("Directorios requeridos:")
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            log_success(dir_path)
            success_count += 1
        else:
            log_warning(f"{dir_path} no encontrado")
    
    total_items = len(required_files) + len(required_dirs)
    log_info(f"Estructura: {success_count}/{total_items}")
    return success_count >= total_items * 0.8

def check_dummy_mode():
    """Verifica configuración de modo dummy"""
    log_header("CONFIGURACIÓN DUMMY MODE")
    
    dummy_mode = os.getenv("DUMMY_MODE", "false").lower() == "true"
    log_info(f"DUMMY_MODE: {dummy_mode}")
    
    if dummy_mode:
        log_success("Modo dummy activado - sin dependencias pesadas requeridas")
        return True
    else:
        log_info("Modo producción - todas las dependencias requeridas")
        return False

def main():
    """Función principal"""
    print("🔍 TikTok Viral ML System - Validador de Dependencias")
    print("=" * 55)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detectar rama
    current_branch = get_current_branch()
    log_info(f"Rama actual: {current_branch}")
    
    # Verificar modo dummy
    is_dummy = check_dummy_mode()
    
    # Verificaciones básicas
    results = []
    results.append(check_system_dependencies())
    results.append(check_core_dependencies())
    results.append(check_file_structure())
    
    # Verificaciones específicas por rama (si no está en modo dummy)
    if not is_dummy:
        if current_branch in ["main", "rama"]:
            results.append(check_rama_dependencies())
        elif current_branch == "meta":
            results.append(check_meta_dependencies())
        elif current_branch in ["tele", "telegram"]:
            results.append(check_tele_dependencies())
        
        # Módulo 7 (todas las ramas)
        results.append(check_modulo7_dependencies())
    
    # Resumen final
    log_header("RESUMEN FINAL")
    
    success_rate = sum(results) / len(results) if results else 0
    
    if success_rate >= 0.9:
        log_success(f"Sistema LISTO - {success_rate:.1%} de verificaciones exitosas")
        print("\n🚀 El sistema está correctamente configurado y listo para usar!")
        exit_code = 0
    elif success_rate >= 0.7:
        log_warning(f"Sistema PARCIAL - {success_rate:.1%} de verificaciones exitosas")
        print("\n⚠️  El sistema puede funcionar pero algunas características estarán limitadas.")
        print("💡 Ejecuta: ./install_dependencies.sh para completar la instalación")
        exit_code = 1
    else:
        log_error(f"Sistema INCOMPLETO - {success_rate:.1%} de verificaciones exitosas")
        print("\n❌ El sistema NO está listo para usar.")
        print("🔧 Ejecuta: ./install_dependencies.sh para instalar dependencias")
        exit_code = 2
    
    # Recomendaciones
    print("\n📋 Próximos pasos:")
    if not is_dummy:
        print("   1. Configura variables en .env")
        print("   2. Ejecuta: uvicorn ml_core.api.main:app --reload")
        print("   3. Accede a: http://localhost:8000")
    else:
        print("   1. Modo dummy activado - ejecuta tests")
        print("   2. pytest tests/ -v")
        print("   3. uvicorn ml_core.api.main:app --reload")
    
    print(f"\n📊 Score final: {success_rate:.1%}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()