"""
MCP Server para Manejo de Dependencias y Errores
Solución completa de Model Context Protocol para el sistema
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import importlib
import sys
import os
from pathlib import Path

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPErrorType(Enum):
    """Tipos de errores MCP"""
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    TYPE_ERROR = "type_error"
    DEPENDENCY_ERROR = "dependency_error"
    CONFIGURATION_ERROR = "configuration_error"

@dataclass
class MCPError:
    """Estructura de error MCP"""
    error_type: MCPErrorType
    file_path: str
    line_number: int
    error_message: str
    suggested_fix: str
    severity: str = "medium"  # low, medium, high, critical
    auto_fixable: bool = False

@dataclass
class MCPDependency:
    """Dependencia MCP"""
    name: str
    version: Optional[str] = None
    install_command: str = ""
    dummy_implementation: Optional[str] = None
    required: bool = True
    category: str = "general"

class MCPDependencyManager:
    """Manejador de dependencias MCP"""
    
    def __init__(self):
        self.dependencies = self._initialize_dependencies()
        self.dummy_mode = os.getenv("DUMMY_MODE", "true").lower() == "true"
        
    def _initialize_dependencies(self) -> Dict[str, MCPDependency]:
        """Inicializa catálogo de dependencias"""
        return {
            # Social Media APIs
            "telethon": MCPDependency(
                name="telethon",
                version="1.32.1",
                install_command="pip install telethon",
                dummy_implementation="social_extensions.telegram.dummy.DummyTelegramClient",
                category="telegram"
            ),
            "instagrapi": MCPDependency(
                name="instagrapi", 
                version="2.0.0",
                install_command="pip install instagrapi",
                dummy_implementation="social_extensions.instagram.dummy.DummyInstagramAPI",
                category="instagram"
            ),
            "tweepy": MCPDependency(
                name="tweepy",
                version="4.14.0", 
                install_command="pip install tweepy",
                dummy_implementation="social_extensions.twitter.dummy.DummyTwitterAPI",
                category="twitter"
            ),
            "linkedin_api": MCPDependency(
                name="linkedin-api",
                version="2.0.0",
                install_command="pip install linkedin-api",
                dummy_implementation="social_extensions.linkedin.dummy.DummyLinkedInAPI",
                category="linkedin"
            ),
            "facebook_business": MCPDependency(
                name="facebook-business",
                version="19.0.0",
                install_command="pip install facebook-business",
                dummy_implementation="social_extensions.meta.dummy.DummyMetaAPI",
                category="meta"
            ),
            
            # ML/AI Libraries
            "ultralytics": MCPDependency(
                name="ultralytics",
                version="8.0.200",
                install_command="pip install ultralytics",
                dummy_implementation="ml_core.models.dummy.DummyYOLO",
                category="ml"
            ),
            "cv2": MCPDependency(
                name="opencv-python",
                version="4.8.1.78",
                install_command="pip install opencv-python",
                dummy_implementation="ml_core.vision.dummy.DummyCV2",
                category="vision"
            ),
            
            # Cloud Services
            "boto3": MCPDependency(
                name="boto3",
                version="1.34.0",
                install_command="pip install boto3",
                dummy_implementation="ml_core.cloud.dummy.DummyBoto3",
                category="cloud"
            ),
            
            # Utilities
            "numpy": MCPDependency(
                name="numpy",
                version="1.24.0",
                install_command="pip install numpy",
                required=True,
                category="core"
            )
        }
    
    def get_dummy_implementation(self, module_name: str) -> Optional[str]:
        """Obtiene implementación dummy para un módulo"""
        if not self.dummy_mode:
            return None
            
        dependency = self.dependencies.get(module_name)
        return dependency.dummy_implementation if dependency else None
    
    def is_module_available(self, module_name: str) -> bool:
        """Verifica si un módulo está disponible"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def get_install_command(self, module_name: str) -> str:
        """Obtiene comando de instalación para un módulo"""
        dependency = self.dependencies.get(module_name)
        return dependency.install_command if dependency else f"pip install {module_name}"

class MCPErrorDetector:
    """Detector de errores MCP"""
    
    def __init__(self, dependency_manager: MCPDependencyManager):
        self.dependency_manager = dependency_manager
        
    async def scan_file_errors(self, file_path: str) -> List[MCPError]:
        """Escanea errores en un archivo específico"""
        errors = []
        
        if not os.path.exists(file_path):
            return errors
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Detectar errores de import
            import_errors = self._detect_import_errors(file_path, content)
            errors.extend(import_errors)
            
            # Detectar errores de sintaxis
            syntax_errors = self._detect_syntax_errors(file_path, content)
            errors.extend(syntax_errors)
            
        except Exception as e:
            logger.error(f"Error escaneando {file_path}: {e}")
            
        return errors
    
    def _detect_import_errors(self, file_path: str, content: str) -> List[MCPError]:
        """Detecta errores de import"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Detectar imports
            if line.startswith('import ') or line.startswith('from '):
                module_name = self._extract_module_name(line)
                
                if module_name and not self.dependency_manager.is_module_available(module_name):
                    dummy_impl = self.dependency_manager.get_dummy_implementation(module_name)
                    
                    if dummy_impl:
                        suggested_fix = f"Usar implementación dummy: {dummy_impl}"
                        auto_fixable = True
                    else:
                        install_cmd = self.dependency_manager.get_install_command(module_name)
                        suggested_fix = f"Instalar dependencia: {install_cmd}"
                        auto_fixable = False
                    
                    errors.append(MCPError(
                        error_type=MCPErrorType.IMPORT_ERROR,
                        file_path=file_path,
                        line_number=i,
                        error_message=f"Import '{module_name}' no puede ser resuelto",
                        suggested_fix=suggested_fix,
                        auto_fixable=auto_fixable
                    ))
        
        return errors
    
    def _extract_module_name(self, line: str) -> Optional[str]:
        """Extrae nombre del módulo de una línea de import"""
        line = line.strip()
        
        if line.startswith('import '):
            # import module_name
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].split('.')[0]
        elif line.startswith('from '):
            # from module_name import ...
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].split('.')[0]
        
        return None
    
    def _detect_syntax_errors(self, file_path: str, content: str) -> List[MCPError]:
        """Detecta errores de sintaxis"""
        errors = []
        
        try:
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            errors.append(MCPError(
                error_type=MCPErrorType.SYNTAX_ERROR,
                file_path=file_path,
                line_number=e.lineno or 0,
                error_message=str(e),
                suggested_fix="Revisar sintaxis Python en la línea indicada",
                severity="high"
            ))
        
        return errors

class MCPAutoFixer:
    """Auto-reparador de errores MCP"""
    
    def __init__(self, dependency_manager: MCPDependencyManager):
        self.dependency_manager = dependency_manager
        
    async def fix_import_errors(self, file_path: str, errors: List[MCPError]) -> bool:
        """Repara errores de import automáticamente"""
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            lines = content.split('\n')
            
            for error in errors:
                if error.error_type == MCPErrorType.IMPORT_ERROR and error.auto_fixable:
                    line_idx = error.line_number - 1
                    if 0 <= line_idx < len(lines):
                        original_line = lines[line_idx]
                        fixed_line = self._fix_import_line(original_line, error)
                        
                        if fixed_line != original_line:
                            lines[line_idx] = fixed_line
                            modified = True
                            logger.info(f"Fijo import en {file_path}:{error.line_number}")
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                return True
                
        except Exception as e:
            logger.error(f"Error reparando {file_path}: {e}")
            
        return False
    
    def _fix_import_line(self, original_line: str, error: MCPError) -> str:
        """Repara una línea de import específica"""
        if not self.dependency_manager.dummy_mode:
            return original_line
            
        # Extraer módulo de la línea
        module_name = self._extract_module_from_line(original_line)
        if not module_name:
            return original_line
            
        # Obtener implementación dummy
        dummy_impl = self.dependency_manager.get_dummy_implementation(module_name)
        if not dummy_impl:
            return original_line
            
        # Generar línea de import con implementación dummy
        if original_line.strip().startswith('import '):
            return f"    # Original: {original_line.strip()}\n    try:\n        {original_line.strip()}\n    except ImportError:\n        from {dummy_impl} import *"
        elif original_line.strip().startswith('from '):
            return f"    # Original: {original_line.strip()}\n    try:\n        {original_line.strip()}\n    except ImportError:\n        from {dummy_impl} import *"
            
        return original_line
    
    def _extract_module_from_line(self, line: str) -> Optional[str]:
        """Extrae módulo de línea de import"""
        line = line.strip()
        
        if line.startswith('import '):
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].split('.')[0]
        elif line.startswith('from '):
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].split('.')[0]
        
        return None

class MCPServer:
    """Servidor MCP principal"""
    
    def __init__(self):
        self.dependency_manager = MCPDependencyManager()
        self.error_detector = MCPErrorDetector(self.dependency_manager)
        self.auto_fixer = MCPAutoFixer(self.dependency_manager)
        self.workspace_root = "/workspaces/master"
        
    async def scan_workspace_errors(self) -> Dict[str, List[MCPError]]:
        """Escanea errores en todo el workspace"""
        all_errors = {}
        
        # Archivos Python a escanear
        python_files = []
        for root, dirs, files in os.walk(self.workspace_root):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Escanear cada archivo
        for file_path in python_files:
            try:
                errors = await self.error_detector.scan_file_errors(file_path)
                if errors:
                    relative_path = os.path.relpath(file_path, self.workspace_root)
                    all_errors[relative_path] = errors
            except Exception as e:
                logger.error(f"Error escaneando {file_path}: {e}")
        
        return all_errors
    
    async def auto_fix_errors(self, target_files: Optional[List[str]] = None) -> Dict[str, bool]:
        """Auto-repara errores en archivos especificados"""
        results = {}
        
        if target_files is None:
            # Escanear todo el workspace
            all_errors = await self.scan_workspace_errors()
            target_files = list(all_errors.keys())
        
        for file_path in target_files:
            try:
                full_path = os.path.join(self.workspace_root, file_path)
                errors = await self.error_detector.scan_file_errors(full_path)
                
                if errors:
                    success = await self.auto_fixer.fix_import_errors(full_path, errors)
                    results[file_path] = success
                else:
                    results[file_path] = True  # No hay errores
                    
            except Exception as e:
                logger.error(f"Error auto-reparando {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    async def generate_error_report(self) -> Dict[str, Any]:
        """Genera reporte completo de errores"""
        all_errors = await self.scan_workspace_errors()
        
        # Estadísticas
        total_files = len(all_errors)
        total_errors = sum(len(errors) for errors in all_errors.values())
        
        error_by_type = {}
        auto_fixable_count = 0
        
        for errors in all_errors.values():
            for error in errors:
                error_type = error.error_type.value
                error_by_type[error_type] = error_by_type.get(error_type, 0) + 1
                
                if error.auto_fixable:
                    auto_fixable_count += 1
        
        return {
            "summary": {
                "total_files_with_errors": total_files,
                "total_errors": total_errors,
                "auto_fixable_errors": auto_fixable_count,
                "manual_fix_required": total_errors - auto_fixable_count
            },
            "errors_by_type": error_by_type,
            "errors_by_file": all_errors,
            "dummy_mode": self.dependency_manager.dummy_mode,
            "recommendations": self._generate_recommendations(all_errors)
        }
    
    def _generate_recommendations(self, all_errors: Dict[str, List[MCPError]]) -> List[str]:
        """Genera recomendaciones basadas en errores"""
        recommendations = []
        
        # Contar tipos de errores
        import_errors = 0
        syntax_errors = 0
        
        for errors in all_errors.values():
            for error in errors:
                if error.error_type == MCPErrorType.IMPORT_ERROR:
                    import_errors += 1
                elif error.error_type == MCPErrorType.SYNTAX_ERROR:
                    syntax_errors += 1
        
        if import_errors > 0:
            recommendations.append(
                f"Se detectaron {import_errors} errores de import. "
                "Considerar ejecutar auto-fix o instalar dependencias faltantes."
            )
        
        if syntax_errors > 0:
            recommendations.append(
                f"Se detectaron {syntax_errors} errores de sintaxis que requieren revisión manual."
            )
        
        if self.dependency_manager.dummy_mode:
            recommendations.append(
                "DUMMY_MODE está activado. Esto permite ejecutar el sistema sin dependencias reales."
            )
        else:
            recommendations.append(
                "DUMMY_MODE está desactivado. Asegurar que todas las dependencias estén instaladas."
            )
        
        return recommendations

# Función principal para usar el MCP Server
async def run_mcp_diagnostics():
    """Ejecuta diagnósticos completos MCP"""
    mcp_server = MCPServer()
    
    print("🔍 EJECUTANDO DIAGNÓSTICO MCP...")
    print("=" * 50)
    
    # Generar reporte de errores
    report = await mcp_server.generate_error_report()
    
    # Mostrar resultados
    print("📊 RESUMEN DE ERRORES:")
    print(f"  Archivos con errores: {report['summary']['total_files_with_errors']}")
    print(f"  Total de errores: {report['summary']['total_errors']}")
    print(f"  Auto-reparables: {report['summary']['auto_fixable_errors']}")
    print(f"  Requieren revisión manual: {report['summary']['manual_fix_required']}")
    print()
    
    print("🔧 ERRORES POR TIPO:")
    for error_type, count in report['errors_by_type'].items():
        print(f"  {error_type}: {count}")
    print()
    
    print("💡 RECOMENDACIONES:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    print()
    
    # Auto-reparar errores
    if report['summary']['auto_fixable_errors'] > 0:
        print("🔧 EJECUTANDO AUTO-REPARACIÓN...")
        results = await mcp_server.auto_fix_errors()
        
        fixed_count = sum(1 for success in results.values() if success)
        print(f"  ✅ Archivos reparados: {fixed_count}/{len(results)}")
        
        for file_path, success in results.items():
            status = "✅" if success else "❌"
            print(f"    {status} {file_path}")
    
    return report

if __name__ == "__main__":
    asyncio.run(run_mcp_diagnostics())