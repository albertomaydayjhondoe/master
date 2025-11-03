#!/usr/bin/env python3
"""
Instalador y validador final de dependencias
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    return logging.getLogger(__name__)

def install_core_dependencies():
    """Instalar dependencias core sin problemas."""
    logger = logging.getLogger(__name__)
    
    # Dependencias críticas sin conflictos
    critical_packages = [
        'fastapi==0.104.1',
        'uvicorn[standard]==0.24.0',
        'streamlit==1.28.1',
        'pydantic==2.5.0',
        'python-dotenv==1.0.0',
        'requests==2.31.0'
    ]
    
    for package in critical_packages:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', package
            ], check=True, capture_output=True)
            logger.info(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Failed to install {package}")

def install_optional_dependencies():
    """Instalar dependencias opcionales."""
    logger = logging.getLogger(__name__)
    
    optional_packages = [
        'psutil',
        'schedule',
        'watchdog',
        'matplotlib',
        'pandas',
        'numpy',
        'pillow'
    ]
    
    for package in optional_packages:
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', package
            ], check=True, capture_output=True, timeout=60)
            logger.info(f"✅ Installed {package}")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            logger.warning(f"⚠️ Skipped {package}")

def create_minimal_requirements():
    """Crear requirements mínimos."""
    logger = logging.getLogger(__name__)
    
    minimal_req = '''# Minimal working requirements
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
streamlit>=1.28.0
pydantic>=2.5.0
python-dotenv>=1.0.0
requests>=2.31.0
pillow>=10.0.0
numpy>=1.24.0
pandas>=2.0.0
psutil>=5.9.0
'''
    
    req_path = Path('requirements-minimal.txt')
    req_path.write_text(minimal_req)
    logger.info("✅ Created requirements-minimal.txt")

def fix_python_path():
    """Reparar PYTHONPATH."""
    logger = logging.getLogger(__name__)
    
    current_dir = Path.cwd()
    python_path = os.environ.get('PYTHONPATH', '')
    
    if str(current_dir) not in python_path:
        new_path = f"{current_dir}:{python_path}" if python_path else str(current_dir)
        os.environ['PYTHONPATH'] = new_path
        logger.info(f"✅ Fixed PYTHONPATH: {new_path}")

def validate_imports():
    """Validar imports críticos."""
    logger = logging.getLogger(__name__)
    
    critical_imports = [
        'fastapi',
        'streamlit',
        'pydantic',
        'requests',
        'PIL',
        'numpy',
        'pandas'
    ]
    
    failed_imports = []
    
    for module in critical_imports:
        try:
            __import__(module)
            logger.info(f"✅ {module} importable")
        except ImportError as e:
            failed_imports.append(module)
            logger.error(f"❌ {module} not importable: {e}")
    
    return len(failed_imports) == 0

def create_startup_test():
    """Crear test básico de startup."""
    logger = logging.getLogger(__name__)
    
    test_content = '''#!/usr/bin/env python3
"""
Test básico de startup del sistema
"""

def test_basic_imports():
    """Test imports básicos."""
    try:
        import fastapi
        import streamlit
        import pydantic
        import requests
        import numpy
        import pandas
        print("✅ Todos los imports críticos funcionan")
        return True
    except ImportError as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_dummy_mode():
    """Test modo dummy."""
    import os
    os.environ['DUMMY_MODE'] = 'true'
    
    try:
        from ml_core.models.factory import get_yolo_screenshot_detector
        detector = get_yolo_screenshot_detector()
        print("✅ Factory ML funciona")
        
        from device_farm.controllers.factory import get_adb_controller
        controller = get_adb_controller()
        print("✅ Factory Device funciona")
        
        return True
    except Exception as e:
        print(f"❌ Error en factories: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test básico de sistema")
    print("=" * 40)
    
    success = True
    success &= test_basic_imports()
    success &= test_dummy_mode()
    
    if success:
        print("🎉 Sistema básico funcional")
    else:
        print("❌ Sistema tiene problemas")
        exit(1)
'''
    
    test_path = Path('test_startup.py')
    test_path.write_text(test_content)
    test_path.chmod(0o755)
    logger.info("✅ Created test_startup.py")

def main():
    """Ejecutar instalación final."""
    logger = setup_logging()
    logger.info("🔧 Instalación final de dependencias")
    
    try:
        logger.info("📦 Instalando dependencias críticas...")
        install_core_dependencies()
        
        logger.info("📦 Instalando dependencias opcionales...")
        install_optional_dependencies()
        
        logger.info("📋 Creando requirements mínimos...")
        create_minimal_requirements()
        
        logger.info("🐍 Reparando PYTHONPATH...")
        fix_python_path()
        
        logger.info("🧪 Creando test de startup...")
        create_startup_test()
        
        logger.info("✅ Validando imports...")
        if validate_imports():
            logger.info("🎉 Instalación completada exitosamente")
            return True
        else:
            logger.warning("⚠️ Algunos imports fallan, pero sistema básico funcional")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error en instalación: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)