"""
Import resolver for dummy mode
Automatically provides dummy implementations when real packages are not available
"""
import sys
import os
import importlib
from typing import Any, Dict, Optional

# Get dummy mode setting
DUMMY_MODE = os.getenv('DUMMY_MODE', 'true').lower() == 'true'

def setup_dummy_imports():
    """Setup dummy imports when in dummy mode"""
    if not DUMMY_MODE:
        return
    
    try:
        from .dummy_implementations import get_dummy_implementations
        dummy_modules = get_dummy_implementations()
        
        # Add dummy modules to sys.modules
        for module_name, dummy_module in dummy_modules.items():
            if module_name not in sys.modules:
                sys.modules[module_name] = dummy_module
                print(f"🎭 Dummy module loaded: {module_name}")
    
    except ImportError as e:
        print(f"⚠️ Could not load dummy implementations: {e}")

def safe_import(module_name: str, fallback_name: Optional[str] = None) -> Any:
    """
    Safely import a module with fallback to dummy implementation
    
    Args:
        module_name: Name of the module to import
        fallback_name: Optional fallback module name
    
    Returns:
        Imported module or dummy implementation
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        if DUMMY_MODE:
            print(f"🎭 Using dummy implementation for: {module_name}")
            
            # Try to get from dummy implementations
            try:
                from .dummy_implementations import get_dummy_implementations
                dummy_modules = get_dummy_implementations()
                
                if module_name in dummy_modules:
                    return dummy_modules[module_name]
                elif fallback_name and fallback_name in dummy_modules:
                    return dummy_modules[fallback_name]
            except ImportError:
                pass
        
        # Re-raise the original import error if no dummy available
        raise

def conditional_import(module_name: str, dummy_class=None):
    """
    Conditionally import a module or return dummy class
    
    Args:
        module_name: Name of the module to import
        dummy_class: Dummy class to return if import fails
    
    Returns:
        Real module or dummy class
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        if DUMMY_MODE and dummy_class:
            print(f"🎭 Using dummy class for: {module_name}")
            return dummy_class
        raise

# Initialize dummy imports on module load
if DUMMY_MODE:
    setup_dummy_imports()