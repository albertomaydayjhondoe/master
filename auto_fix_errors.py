#!/usr/bin/env python3
"""
Auto Fix All System Errors
Repara automáticamente todos los errores de tipo y código del sistema.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

def fix_function_return_types(file_path: str) -> None:
    """Arregla funciones que necesitan tipos de retorno."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Patrones de funciones test que retornan bool
        patterns = [
            (r'def (test_\w+)\(\):', r'def \1() -> bool:'),
            (r'def (test_\w+)\(.*?\):', r'def \1() -> bool:'),
            (r'def main\(\):', r'def main() -> int:'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print(f"✅ Fixed return types in {file_path}")
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")

def fix_byteio_errors(file_path: str) -> None:
    """Arregla errores de BytesIO vs bytes."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Patrones para arreglar BytesIO
        if "img_bytes = img_bytes.getvalue()" in content:
            content = content.replace(
                "img_bytes = img_bytes.getvalue()",
                "img_data = img_bytes.getvalue()"
            )
            
            # Reemplazar usos posteriores
            content = content.replace(
                "detector.detect(img_bytes)",
                "detector.detect(img_data)"
            )
            content = content.replace(
                "detector.detect_social_objects(img_bytes)",
                "detector.detect_social_objects(img_data)"
            )
            content = content.replace(
                "detector.get_detection_summary(img_bytes)",
                "detector.get_detection_summary(img_data)"
            )
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print(f"✅ Fixed BytesIO errors in {file_path}")
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")

def fix_model_none_errors(file_path: str) -> None:
    """Arregla errores de self.model = None."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Agregar imports si es necesario
        if "from typing import" in content and "Optional" not in content:
            content = content.replace(
                "from typing import",
                "from typing import Optional,"
            )
        
        # Cambiar self.model = None por self.model: Optional[Any] = None
        content = re.sub(
            r'self\.model = None',
            'self.model: Optional[Any] = None',
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print(f"✅ Fixed model None errors in {file_path}")
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")

def install_missing_stubs() -> None:
    """Instala stubs de tipos que faltan."""
    packages = [
        "types-requests",
        "types-pillow",
        "types-pyyaml"
    ]
    
    for package in packages:
        try:
            subprocess.run(["pip", "install", package], check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Could not install {package}")

def main() -> int:
    """Función principal de reparación automática."""
    print("🔧 AUTO FIX ALL SYSTEM ERRORS")
    print("=" * 50)
    
    # Instalar stubs faltantes
    print("\n1. Installing missing type stubs...")
    install_missing_stubs()
    
    # Archivos con errores específicos
    files_to_fix = [
        "/workspaces/master/test_coco_system.py",
        "/workspaces/master/test_coco_simple.py", 
        "/workspaces/master/test_coco_real.py",
        "/workspaces/master/test_coco_api.py",
        "/workspaces/master/ml_core/models/yolo_coco_pretrained.py",
        "/workspaces/master/social_extensions/meta/musical_ml_models.py",
        "/workspaces/master/telegram_like4like_bot.py"
    ]
    
    print("\n2. Fixing function return types...")
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_function_return_types(file_path)
    
    print("\n3. Fixing BytesIO errors...")
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_byteio_errors(file_path)
    
    print("\n4. Fixing model None errors...")
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            fix_model_none_errors(file_path)
    
    print("\n🎉 Auto fix completed!")
    return 0

if __name__ == "__main__":
    exit(main())