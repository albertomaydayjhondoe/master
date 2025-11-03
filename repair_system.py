#!/usr/bin/env python3
"""
Reparador automático del sistema - Sin Ultralytics
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def fix_imports():
    """Reparar imports problemáticos."""
    logger = logging.getLogger(__name__)
    
    fixes = [
        # Archivo: config/app_settings.py
        {
            'file': 'config/app_settings.py',
            'old': 'from typing import Dict, Any, Optional',
            'new': 'from typing import Dict, Any, Optional, List'
        },
        
        # Archivo: ml_core/api/main.py
        {
            'file': 'ml_core/api/main.py',
            'old': 'from typing import Optional, Dict, Any',
            'new': 'from typing import Optional, Dict, Any, Union, List'
        },
        
        # Archivo: device_farm/controllers/device_manager.py
        {
            'file': 'device_farm/controllers/device_manager.py',
            'old': 'from typing import List, Dict, Optional',
            'new': 'from typing import List, Dict, Optional, Any, Union'
        },
        
        # Archivo: social_extensions/meta/meta_automator.py
        {
            'file': 'social_extensions/meta/meta_automator.py',
            'old': 'from typing import Dict, List, Optional',
            'new': 'from typing import Dict, List, Optional, Any, Union'
        }
    ]
    
    for fix in fixes:
        try:
            file_path = Path(fix['file'])
            if file_path.exists():
                content = file_path.read_text()
                if fix['old'] in content:
                    content = content.replace(fix['old'], fix['new'])
                    file_path.write_text(content)
                    logger.info(f"✅ Fixed imports in {fix['file']}")
        except Exception as e:
            logger.error(f"❌ Error fixing {fix['file']}: {e}")

def install_missing_packages():
    """Instalar paquetes que faltan sin Ultralytics."""
    logger = logging.getLogger(__name__)
    
    packages = [
        'pillow',
        'opencv-python',
        'numpy',
        'requests',
        'fastapi',
        'uvicorn',
        'streamlit',
        'sqlalchemy',
        'psycopg2-binary',
        'pymongo',
        'redis',
        'celery',
        'python-telegram-bot',
        'tweepy',
        'instagrapi',
        'pyrogram',
        'facebook-sdk',
        'playwright',
        'selenium',
        'appium-python-client',
        'adbutils',
        'pydantic',
        'python-dotenv',
        'schedule',
        'watchdog',
        'psutil',
        'matplotlib',
        'pandas',
        'scikit-learn',
        'transformers',
        'sentence-transformers',
        'librosa',
        'moviepy'
    ]
    
    for package in packages:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
            logger.info(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Failed to install {package}: {e}")

def fix_factory_functions():
    """Reparar funciones factory que faltan."""
    logger = logging.getLogger(__name__)
    
    # Fix ml_core factory
    ml_factory_path = Path('ml_core/models/factory.py')
    if ml_factory_path.exists():
        content = ml_factory_path.read_text()
        
        if 'def create_yolo_detector' not in content:
            factory_addition = '''

def create_yolo_detector(model_path: str = None):
    """Crear detector YOLO - alias para compatibilidad."""
    return get_yolo_screenshot_detector(model_path)

def create_anomaly_detector():
    """Crear detector de anomalías."""
    from .dummy_implementations import DummyAnomalyDetector
    return DummyAnomalyDetector()
'''
            content += factory_addition
            ml_factory_path.write_text(content)
            logger.info("✅ Fixed ML factory functions")
    
    # Fix device_farm factory
    device_factory_path = Path('device_farm/controllers/factory.py')
    if device_factory_path.exists():
        content = device_factory_path.read_text()
        
        if 'def create_adb_controller' not in content:
            factory_addition = '''

def create_adb_controller():
    """Crear controlador ADB - alias para compatibilidad."""
    return get_adb_controller()
'''
            content += factory_addition
            device_factory_path.write_text(content)
            logger.info("✅ Fixed device factory functions")

def create_missing_dummy_classes():
    """Crear clases dummy que faltan."""
    logger = logging.getLogger(__name__)
    
    # Crear dummy implementations para ML
    ml_dummy_path = Path('ml_core/models/dummy_implementations.py')
    if not ml_dummy_path.exists():
        dummy_content = '''"""
Implementaciones dummy para desarrollo sin GPU
"""
from typing import Dict, Any, List, Optional, Union
import random
import time

class DummyYoloDetector:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "dummy_yolo.pt"
        
    def detect(self, image_data: bytes) -> Dict[str, Any]:
        time.sleep(0.1)  # Simular procesamiento
        return {
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.85,
                    "bbox": [100, 100, 200, 300],
                    "social_relevant": True
                }
            ],
            "total_detections": 1,
            "processing_time_ms": 100
        }

class DummyAnomalyDetector:
    def detect_anomaly(self, data: Any) -> Dict[str, Any]:
        return {
            "is_anomaly": False,
            "confidence": 0.1,
            "anomaly_type": None
        }

class DummyScreenshotAnalyzer:
    def analyze(self, screenshot: bytes) -> Dict[str, Any]:
        return {
            "content_type": "video",
            "engagement_score": 0.75,
            "is_shadowbanned": False
        }
'''
        ml_dummy_path.write_text(dummy_content)
        logger.info("✅ Created ML dummy implementations")
    
    # Crear dummy implementations para device farm
    device_dummy_path = Path('device_farm/controllers/dummy_implementations.py')
    if not device_dummy_path.exists():
        dummy_content = '''"""
Implementaciones dummy para controladores de dispositivos
"""
from typing import Dict, Any, List, Optional

class DummyADBController:
    def __init__(self):
        self.connected = True
        
    def connect(self, device_id: str) -> bool:
        return True
        
    def disconnect(self) -> bool:
        return True
        
    def tap(self, x: int, y: int) -> bool:
        return True
        
    def swipe(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        return True
        
    def screenshot(self) -> bytes:
        # Crear imagen dummy de 1x1 pixel
        from PIL import Image
        import io
        img = Image.new('RGB', (1, 1), color='black')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
        
    def get_device_info(self) -> Dict[str, Any]:
        return {
            "device_id": "dummy_device",
            "model": "Dummy Phone",
            "android_version": "13.0"
        }

class DummyAppiumDriver:
    def __init__(self):
        self.connected = True
        
    def find_element(self, locator: str) -> Any:
        return DummyElement()
        
    def quit(self):
        pass

class DummyElement:
    def click(self):
        pass
        
    def send_keys(self, text: str):
        pass
        
    def get_attribute(self, name: str) -> str:
        return "dummy_value"
'''
        device_dummy_path.write_text(dummy_content)
        logger.info("✅ Created device dummy implementations")

def fix_config_files():
    """Reparar archivos de configuración."""
    logger = logging.getLogger(__name__)
    
    # Verificar y crear config básico
    config_path = Path('config/app_settings.py')
    if config_path.exists():
        content = config_path.read_text()
        
        # Asegurar que DUMMY_MODE esté configurado
        if 'DUMMY_MODE' not in content:
            dummy_config = '''

# Modo dummy para desarrollo
DUMMY_MODE = os.getenv("DUMMY_MODE", "true").lower() == "true"
'''
            content += dummy_config
            config_path.write_text(content)
            logger.info("✅ Fixed app settings config")

def create_requirements_file():
    """Crear archivo requirements limpio sin Ultralytics."""
    logger = logging.getLogger(__name__)
    
    requirements = '''# Core dependencies
fastapi>=0.104.1
uvicorn>=0.24.0
pydantic>=2.5.0
python-dotenv>=1.0.0
requests>=2.31.0

# Web interface
streamlit>=1.28.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pymongo>=4.6.0
redis>=5.0.0

# Task queue
celery>=5.3.0

# Image processing
pillow>=10.1.0
opencv-python>=4.8.0
numpy>=1.24.0

# Social media APIs
python-telegram-bot>=20.0
tweepy>=4.14.0
instagrapi>=2.0.0
pyrogram>=2.0.0
facebook-sdk>=3.1.0

# Browser automation
selenium>=4.15.0
playwright>=1.40.0

# Mobile automation
appium-python-client>=3.1.0
adbutils>=0.16.0

# ML/AI (without Ultralytics)
transformers>=4.35.0
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
torch>=2.1.0
torchaudio>=2.1.0

# Media processing
librosa>=0.10.0
moviepy>=1.0.3

# Utilities
schedule>=1.2.0
watchdog>=3.0.0
psutil>=5.9.0
matplotlib>=3.8.0
pandas>=2.1.0
'''
    
    req_path = Path('requirements-core.txt')
    req_path.write_text(requirements)
    logger.info("✅ Created core requirements file")

def main():
    """Ejecutar todas las reparaciones."""
    logger = setup_logging()
    logger.info("🔧 Iniciando reparación automática del sistema")
    
    try:
        logger.info("📝 Reparando imports...")
        fix_imports()
        
        logger.info("📦 Instalando paquetes faltantes...")
        install_missing_packages()
        
        logger.info("🏭 Reparando funciones factory...")
        fix_factory_functions()
        
        logger.info("🎭 Creando clases dummy...")
        create_missing_dummy_classes()
        
        logger.info("⚙️ Reparando configuración...")
        fix_config_files()
        
        logger.info("📋 Creando requirements...")
        create_requirements_file()
        
        logger.info("✅ Reparación completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la reparación: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)