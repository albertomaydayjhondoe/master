"""
Utilidad para importar módulos por path dinámico
"""
import importlib
import sys
from pathlib import Path

def import_by_path(module_path: str):
    """
    Importa un módulo usando un path de puntos
    
    Args:
        module_path: Path del módulo tipo 'ml_core.models.yolo_screenshot'
    
    Returns:
        Módulo importado
    """
    try:
        return importlib.import_module(module_path)
    except ImportError as e:
        # En caso de error, retornar None para que factory use dummy
        print(f"⚠️ No se pudo importar {module_path}: {e}")
        return None