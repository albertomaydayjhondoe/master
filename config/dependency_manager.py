#!/usr/bin/env python3
"""
Dependency Management and Configuration

Sistema inteligente para manejar dependencias en modo dummy vs production.
Automaticamente detecta qué librerías están disponibles y configura fallbacks.

Autor: Sistema de Documentación Automática  
Fecha: 2024
"""

import os
import sys
import importlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DependencyStatus:
    """Estado de una dependencia"""
    name: str
    available: bool
    version: Optional[str] = None
    fallback_available: bool = False
    critical: bool = False
    error_message: Optional[str] = None

class DependencyManager:
    """Gestor inteligente de dependencias"""
    
    def __init__(self):
        self.dependencies_status: Dict[str, DependencyStatus] = {}
        self.dummy_mode = os.getenv('DUMMY_MODE', 'true').lower() == 'true'
        
        # Dependencias críticas vs opcionales
        self.critical_dependencies = {
            'ultralytics': 'ML model training and inference',
            'torch': 'Deep learning framework',
            'opencv-python': 'Computer vision processing',
            'telethon': 'Telegram bot functionality',
            'numpy': 'Numerical computations',
            'pandas': 'Data processing'
        }
        
        self.optional_dependencies = {
            'streamlit': 'Web dashboard interface',
            'plotly': 'Interactive visualizations', 
            'git': 'Version control integration',
            'selenium': 'Browser automation',
            'facebook-business': 'Meta Ads integration',
            'google-api-python-client': 'YouTube API integration',
            'playwright': 'Advanced browser automation',
            'gologin': 'Proxy management system'
        }
        
        # Mock classes para dummy mode
        self.mock_classes = {}
        
    def check_all_dependencies(self) -> Dict[str, DependencyStatus]:
        """Verificar estado de todas las dependencias"""
        
        print("🔍 Checking dependency status...")
        
        # Verificar dependencias críticas
        for dep, description in self.critical_dependencies.items():
            status = self._check_dependency(dep, description, critical=True)
            self.dependencies_status[dep] = status
        
        # Verificar dependencias opcionales
        for dep, description in self.optional_dependencies.items():
            status = self._check_dependency(dep, description, critical=False)
            self.dependencies_status[dep] = status
        
        self._print_dependency_summary()
        return self.dependencies_status
    
    def _check_dependency(self, name: str, description: str, critical: bool = False) -> DependencyStatus:
        """Verificar una dependencia específica"""
        
        try:
            # Intentar importar
            module = importlib.import_module(name)
            
            # Obtener versión si está disponible
            version = getattr(module, '__version__', 'unknown')
            
            return DependencyStatus(
                name=name,
                available=True,
                version=version,
                fallback_available=True,
                critical=critical
            )
            
        except ImportError as e:
            return DependencyStatus(
                name=name,
                available=False,
                version=None,
                fallback_available=self._has_fallback(name),
                critical=critical,
                error_message=str(e)
            )
    
    def _has_fallback(self, dependency: str) -> bool:
        """Verificar si existe fallback para una dependencia"""
        
        fallbacks = {
            'streamlit': True,  # CLI mode available
            'plotly': True,     # Simple text charts
            'git': True,        # File-based simulation
            'telethon': True,   # Mock Telegram client
            'ultralytics': True, # Dummy ML predictions
            'selenium': True,   # Mock browser automation
            'facebook-business': True, # Mock ads API
            'opencv-python': True, # Basic image processing fallback
            'playwright': True, # Alternative browser automation
            'gologin': True    # Mock proxy management
        }
        
        return fallbacks.get(dependency, False)
    
    def _print_dependency_summary(self):
        """Imprimir resumen del estado de dependencias"""
        
        print(f"\n📊 Dependency Status Summary")
        print("=" * 50)
        
        # Dependencias críticas
        print("🚨 Critical Dependencies:")
        critical_available = 0
        for name, status in self.dependencies_status.items():
            if status.critical:
                icon = "✅" if status.available else ("🟡" if status.fallback_available else "❌")
                mode = ""
                if not status.available and status.fallback_available:
                    mode = " (fallback mode)"
                elif not status.available:
                    mode = " (NOT AVAILABLE)"
                
                print(f"  {icon} {name:<20} {mode}")
                if status.available:
                    critical_available += 1
        
        # Dependencias opcionales
        print("\n🔧 Optional Dependencies:")
        optional_available = 0
        for name, status in self.dependencies_status.items():
            if not status.critical:
                icon = "✅" if status.available else ("🟡" if status.fallback_available else "❌")
                mode = ""
                if not status.available and status.fallback_available:
                    mode = " (fallback available)"
                elif not status.available:
                    mode = " (not available)"
                
                print(f"  {icon} {name:<20} {mode}")
                if status.available:
                    optional_available += 1
        
        # Estadísticas
        total_critical = len(self.critical_dependencies)
        total_optional = len(self.optional_dependencies)
        
        print(f"\n📈 Summary:")
        print(f"  Critical: {critical_available}/{total_critical} available")
        print(f"  Optional: {optional_available}/{total_optional} available")
        print(f"  Mode: {'🎭 Dummy' if self.dummy_mode else '🚀 Production'}")
        
        # Recomendaciones
        if critical_available < total_critical:
            print(f"\n💡 To enable full functionality, install missing dependencies:")
            print(f"   pip install -r requirements.txt")
    
    def get_import_wrapper(self, dependency: str):
        """Obtener wrapper de importación con fallback"""
        
        status = self.dependencies_status.get(dependency)
        
        if not status or not status.available:
            # Retornar mock/fallback
            return self._get_fallback_implementation(dependency)
        
        # Retornar importación real
        return importlib.import_module(dependency)
    
    def _get_fallback_implementation(self, dependency: str):
        """Obtener implementación fallback para una dependencia"""
        
        if dependency == 'streamlit':
            return self._get_streamlit_fallback()
        elif dependency == 'telethon':
            return self._get_telethon_fallback()
        elif dependency == 'ultralytics':
            return self._get_ultralytics_fallback()
        elif dependency == 'opencv-python':
            return self._get_opencv_fallback()
        elif dependency == 'plotly':
            return self._get_plotly_fallback()
        else:
            return self._get_generic_fallback(dependency)
    
    def _get_streamlit_fallback(self):
        """Fallback para Streamlit (modo CLI)"""
        class StreamlitMock:
            @staticmethod
            def write(*args, **kwargs):
                print(*args)
            
            @staticmethod 
            def title(text):
                print(f"\n{'='*len(text)}")
                print(text)
                print('='*len(text))
            
            @staticmethod
            def error(text):
                print(f"❌ {text}")
            
            @staticmethod
            def success(text):
                print(f"✅ {text}")
            
            @staticmethod
            def warning(text):
                print(f"⚠️ {text}")
            
            @staticmethod
            def info(text):
                print(f"ℹ️ {text}")
        
        return StreamlitMock()
    
    def _get_telethon_fallback(self):
        """Fallback para Telethon (cliente dummy)"""
        class TelegramClientMock:
            def __init__(self, *args, **kwargs):
                self.session_name = args[0] if args else "dummy_session"
            
            async def start(self, phone=None):
                print(f"🎭 Mock Telegram client started for {phone}")
            
            async def send_message(self, entity, message):
                print(f"📤 Mock sending to {entity}: {message}")
            
            async def disconnect(self):
                print("🔌 Mock client disconnected")
            
            def on(self, event_type):
                def decorator(func):
                    print(f"📝 Mock event handler registered: {func.__name__}")
                    return func
                return decorator
        
        class EventsMock:
            class NewMessage:
                def __init__(self, *args, **kwargs): pass
        
        class TypesMock:
            class MessageMediaPhoto: pass
            class MessageMediaDocument: pass
        
        return {
            'TelegramClient': TelegramClientMock,
            'events': EventsMock(),
            'types': TypesMock()
        }
    
    def _get_ultralytics_fallback(self):
        """Fallback para Ultralytics (predicciones dummy)"""
        class YOLOMock:
            def __init__(self, model_path=None):
                self.model_path = model_path
                print(f"🎭 Mock YOLO model loaded: {model_path}")
            
            def __call__(self, image):
                # Retornar resultados simulados
                return [MockDetectionResult()]
            
            def predict(self, source, *args, **kwargs):
                return [MockDetectionResult()]
        
        class MockDetectionResult:
            def __init__(self):
                self.boxes = MockBoxes()
        
        class MockBoxes:
            def __init__(self):
                # Simular detecciones
                import random
                self.cls = [random.randint(0, 5) for _ in range(3)]
                self.conf = [random.uniform(0.7, 0.95) for _ in range(3)]
        
        return {'YOLO': YOLOMock}
    
    def _get_opencv_fallback(self):
        """Fallback para OpenCV (procesamiento básico)"""
        import numpy as np
        
        class CV2Mock:
            @staticmethod
            def imdecode(buffer, flags):
                # Retornar imagen simulada
                return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            @staticmethod
            def imwrite(path, image):
                print(f"🎭 Mock image saved to: {path}")
                return True
            
            IMREAD_COLOR = 1
        
        return CV2Mock()
    
    def _get_plotly_fallback(self):
        """Fallback para Plotly (gráficos texto)"""
        class PlotlyMock:
            class express:
                @staticmethod
                def line(*args, **kwargs):
                    return MockFigure("Line Chart")
                
                @staticmethod
                def bar(*args, **kwargs):
                    return MockFigure("Bar Chart")
                
                @staticmethod
                def imshow(*args, **kwargs):
                    return MockFigure("Heatmap")
            
            class graph_objects:
                @staticmethod
                def Figure(*args, **kwargs):
                    return MockFigure("Custom Chart")
                
                @staticmethod
                def Indicator(*args, **kwargs):
                    return {"type": "indicator"}
        
        class MockFigure:
            def __init__(self, chart_type):
                self.chart_type = chart_type
            
            def update_layout(self, **kwargs):
                return self
            
            def show(self):
                print(f"📊 {self.chart_type} (mock display)")
        
        return PlotlyMock()
    
    def _get_generic_fallback(self, dependency: str):
        """Fallback genérico para cualquier dependencia"""
        
        class GenericMock:
            def __init__(self, *args, **kwargs): 
                pass
            
            def __call__(self, *args, **kwargs):
                print(f"🎭 Mock call to {dependency}")
                return self
            
            def __getattr__(self, name):
                return GenericMock()
        
        return GenericMock()

# Instancia global del manager
dependency_manager = DependencyManager()

# Funciones de conveniencia
def check_dependencies():
    """Verificar todas las dependencias"""
    return dependency_manager.check_all_dependencies()

def get_safe_import(dependency: str):
    """Importación segura con fallback"""
    return dependency_manager.get_import_wrapper(dependency)

def is_dummy_mode():
    """Verificar si estamos en modo dummy"""
    return dependency_manager.dummy_mode

def get_dependency_status(dependency: str) -> Optional[DependencyStatus]:
    """Obtener estado de una dependencia específica"""
    return dependency_manager.dependencies_status.get(dependency)

# Auto-check al importar
if __name__ == "__main__":
    check_dependencies()
else:
    # Check silencioso al importar como módulo
    dependency_manager.check_all_dependencies()