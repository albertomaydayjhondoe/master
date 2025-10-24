#!/usr/bin/env python3
"""
Auto-Update Documentation System

Sistema automático para mantener la documentación actualizada basándose en:
- Cambios en el código fuente
- Nuevas funcionalidades añadidas
- Modificaciones en APIs
- Actualizaciones de dependencias

Autor: Sistema de Documentación Automática
Fecha: 2024
"""

import os
import re
import ast
import git
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import defaultdict

@dataclass
class CodeChange:
    """Representa un cambio en el código que puede afectar documentación"""
    file_path: str
    change_type: str  # added/modified/deleted
    function_changes: List[str]
    class_changes: List[str]
    import_changes: List[str]
    docstring_changes: List[str]
    commit_hash: str
    commit_message: str
    timestamp: datetime

@dataclass
class DocumentationUpdate:
    """Representa una actualización necesaria en la documentación"""
    target_file: str
    section: str
    update_type: str  # api_reference/example/configuration/troubleshooting
    priority: str     # low/medium/high/critical
    description: str
    suggested_content: str
    related_changes: List[CodeChange]

class DocumentationAutoUpdater:
    """Sistema principal de auto-actualización de documentación"""
    
    def __init__(self, repo_path: str = "/workspaces/master"):
        self.repo_path = Path(repo_path)
        self.docs_path = self.repo_path / "docs"
        self.functionality_guides_path = self.docs_path / "functionality_guides"
        
        # Configuración de tracking
        self.tracked_patterns = {
            "api_functions": r"^(async )?def\s+(\w+)\s*\(",
            "classes": r"^class\s+(\w+)",
            "dataclasses": r"^@dataclass\s*\nclass\s+(\w+)",
            "imports": r"^(from\s+\S+\s+)?import\s+(.+)",
            "config_vars": r"(\w+)\s*=\s*['\"]([^'\"]+)['\"]",
            "docstrings": r'"""([^"]*?)"""'
        }
        
        # Mapeo de archivos a documentación
        self.file_doc_mapping = {
            "social_extensions/telegram/monitoring.py": "monitoring_system_README.md",
            "ml_integration/": "ml_integration_README.md",
            "device_farm/": "device_farm_README.md",
            "analytics_dashboard/": "analytics_dashboard_README.md",
            "identity_management/": "identity_management_README.md",
            "platform_publishing/": "platform_publishing_README.md",
            "meta_ads_integration/": "meta_ads_integration_README.md",
            "gologin_automation/": "gologin_automation_README.md"
        }
        
        self.last_scan_file = self.docs_path / ".last_documentation_scan"
    
    async def run_auto_update_cycle(self):
        """Ejecutar ciclo completo de auto-actualización"""
        
        print("🔄 Starting documentation auto-update cycle...")
        
        # 1. Detectar cambios desde última ejecución
        last_scan_time = await self.get_last_scan_time()
        changes = await self.detect_code_changes(since=last_scan_time)
        
        print(f"📊 Detected {len(changes)} code changes since {last_scan_time}")
        
        # 2. Analizar impacto en documentación
        documentation_updates = await self.analyze_documentation_impact(changes)
        
        print(f"📝 Generated {len(documentation_updates)} documentation updates")
        
        # 3. Priorizar actualizaciones
        prioritized_updates = await self.prioritize_updates(documentation_updates)
        
        # 4. Aplicar actualizaciones automáticas (solo las de baja complejidad)
        auto_applied = await self.apply_automatic_updates(prioritized_updates)
        
        # 5. Generar reporte de actualizaciones manuales necesarias
        manual_updates = [u for u in prioritized_updates if u not in auto_applied]
        await self.generate_manual_update_report(manual_updates)
        
        # 6. Actualizar timestamp de último scan
        await self.update_last_scan_time()
        
        print(f"✅ Auto-update cycle completed:")
        print(f"   📦 Auto-applied: {len(auto_applied)} updates")
        print(f"   ✋ Manual required: {len(manual_updates)} updates")
        
        return {
            "changes_detected": len(changes),
            "updates_generated": len(documentation_updates),
            "auto_applied": len(auto_applied),
            "manual_required": len(manual_updates)
        }
    
    async def detect_code_changes(self, since: datetime) -> List[CodeChange]:
        """Detectar cambios en el código desde una fecha específica"""
        
        try:
            repo = git.Repo(self.repo_path)
            
            # Obtener commits desde la fecha especificada
            commits = list(repo.iter_commits(
                since=since.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            changes = []
            
            for commit in commits:
                # Analizar archivos modificados en cada commit
                for item in commit.stats.files:
                    file_path = item
                    
                    # Solo procesar archivos Python relevantes
                    if not file_path.endswith('.py'):
                        continue
                    
                    if self.should_track_file(file_path):
                        change = await self.analyze_file_changes(
                            file_path, commit
                        )
                        if change:
                            changes.append(change)
            
            return changes
            
        except Exception as e:
            print(f"❌ Error detecting code changes: {e}")
            return []
    
    async def analyze_file_changes(self, file_path: str, commit) -> Optional[CodeChange]:
        """Analizar cambios específicos en un archivo"""
        
        try:
            # Obtener contenido del archivo en el commit
            file_content = commit.tree[file_path].data_stream.read().decode()
            
            # Analizar funciones, clases, imports, etc.
            functions = self.extract_functions(file_content)
            classes = self.extract_classes(file_content)
            imports = self.extract_imports(file_content)
            docstrings = self.extract_docstrings(file_content)
            
            return CodeChange(
                file_path=file_path,
                change_type="modified",  # Simplificado por ahora
                function_changes=functions,
                class_changes=classes,
                import_changes=imports,
                docstring_changes=docstrings,
                commit_hash=commit.hexsha,
                commit_message=commit.message.strip(),
                timestamp=datetime.fromtimestamp(commit.committed_date)
            )
            
        except Exception as e:
            print(f"❌ Error analyzing file {file_path}: {e}")
            return None
    
    def extract_functions(self, code: str) -> List[str]:
        """Extraer nombres de funciones del código"""
        functions = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions.append(node.name)
                    
        except Exception:
            # Fallback a regex si AST falla
            pattern = re.compile(self.tracked_patterns["api_functions"], re.MULTILINE)
            matches = pattern.findall(code)
            functions = [match[1] for match in matches if match[1]]
        
        return functions
    
    def extract_classes(self, code: str) -> List[str]:
        """Extraer nombres de clases del código"""
        classes = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    
        except Exception:
            # Fallback a regex
            pattern = re.compile(self.tracked_patterns["classes"], re.MULTILINE)
            matches = pattern.findall(code)
            classes = matches
        
        return classes
    
    def extract_imports(self, code: str) -> List[str]:
        """Extraer imports del código"""
        imports = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
                        
        except Exception:
            # Fallback a regex
            pattern = re.compile(self.tracked_patterns["imports"], re.MULTILINE)
            matches = pattern.findall(code)
            imports = [match[1] for match in matches]
        
        return imports
    
    def extract_docstrings(self, code: str) -> List[str]:
        """Extraer docstrings del código"""
        docstrings = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(docstring[:100] + "..." if len(docstring) > 100 else docstring)
                        
        except Exception:
            # Fallback a regex
            pattern = re.compile(self.tracked_patterns["docstrings"], re.DOTALL)
            matches = pattern.findall(code)
            docstrings = [match[:100] + "..." if len(match) > 100 else match for match in matches]
        
        return docstrings
    
    async def analyze_documentation_impact(self, changes: List[CodeChange]) -> List[DocumentationUpdate]:
        """Analizar impacto de cambios en la documentación"""
        
        updates = []
        
        for change in changes:
            # Determinar qué archivo de documentación se ve afectado
            doc_file = self.get_target_doc_file(change.file_path)
            
            if not doc_file:
                continue
            
            # Generar actualizaciones basadas en los cambios
            
            # 1. Nuevas funciones -> Actualizar API Reference
            if change.function_changes:
                for func_name in change.function_changes:
                    update = DocumentationUpdate(
                        target_file=doc_file,
                        section="API Reference",
                        update_type="api_reference",
                        priority="medium",
                        description=f"Nueva función '{func_name}' detectada",
                        suggested_content=await self.generate_function_documentation(
                            change.file_path, func_name
                        ),
                        related_changes=[change]
                    )
                    updates.append(update)
            
            # 2. Nuevas clases -> Actualizar Core Classes
            if change.class_changes:
                for class_name in change.class_changes:
                    update = DocumentationUpdate(
                        target_file=doc_file,
                        section="Core Classes",
                        update_type="api_reference",
                        priority="high",
                        description=f"Nueva clase '{class_name}' detectada",
                        suggested_content=await self.generate_class_documentation(
                            change.file_path, class_name
                        ),
                        related_changes=[change]
                    )
                    updates.append(update)
            
            # 3. Nuevos imports -> Actualizar Dependencies
            if change.import_changes:
                new_deps = await self.detect_new_dependencies(change.import_changes)
                if new_deps:
                    update = DocumentationUpdate(
                        target_file=doc_file,
                        section="Configuración Detallada",
                        update_type="configuration",
                        priority="low",
                        description=f"Nuevas dependencias detectadas: {', '.join(new_deps)}",
                        suggested_content=await self.generate_dependency_documentation(new_deps),
                        related_changes=[change]
                    )
                    updates.append(update)
            
            # 4. Cambios en docstrings -> Verificar consistency
            if change.docstring_changes:
                update = DocumentationUpdate(
                    target_file=doc_file,
                    section="Troubleshooting",
                    update_type="troubleshooting",
                    priority="low",
                    description="Docstrings actualizados - revisar consistency",
                    suggested_content="// Revisar manualmente para consistency //",
                    related_changes=[change]
                )
                updates.append(update)
        
        return updates
    
    def get_target_doc_file(self, file_path: str) -> Optional[str]:
        """Determinar qué archivo de documentación corresponde a un archivo de código"""
        
        for pattern, doc_file in self.file_doc_mapping.items():
            if file_path.startswith(pattern):
                return doc_file
        
        return None
    
    def should_track_file(self, file_path: str) -> bool:
        """Determinar si un archivo debe ser tracked para documentación"""
        
        # Ignorar archivos de test, __pycache__, etc.
        ignore_patterns = [
            "__pycache__", 
            ".pytest_cache",
            "test_", 
            "_test.py",
            ".pyc"
        ]
        
        for pattern in ignore_patterns:
            if pattern in file_path:
                return False
        
        # Solo trackear archivos en directorios relevantes
        relevant_dirs = [
            "social_extensions/",
            "ml_integration/", 
            "device_farm/",
            "analytics_dashboard/",
            "identity_management/",
            "platform_publishing/",
            "meta_ads_integration/",
            "gologin_automation/"
        ]
        
        return any(file_path.startswith(dir_) for dir_ in relevant_dirs)
    
    async def generate_function_documentation(self, file_path: str, func_name: str) -> str:
        """Generar documentación automática para una función"""
        
        # Placeholder - en producción esto analizaría la función real
        return f"""
#### `{func_name}()` 
Nueva función detectada en `{file_path}`.

```python
# Ejemplo de uso
result = await {func_name}()
print(f"Result: {{result}}")
```

**Parámetros:**
- Por determinar (revisar código fuente)

**Retorna:**
- Por determinar (revisar código fuente)

**Ejemplo:**
```python
# Completar con ejemplo real
pass
```
"""
    
    async def generate_class_documentation(self, file_path: str, class_name: str) -> str:
        """Generar documentación automática para una clase"""
        
        return f"""
#### `{class_name}`
Nueva clase detectada en `{file_path}`.

```python
# Crear instancia
{class_name.lower()} = {class_name}()

# Verificar inicialización  
print(f"Initialized: {{{class_name.lower()}.is_initialized}}")
```

**Atributos principales:**
- Por determinar (revisar código fuente)

**Métodos principales:**
- Por determinar (revisar código fuente)

**Ejemplo de uso:**
```python
# Completar con ejemplo real
pass
```
"""
    
    async def generate_dependency_documentation(self, dependencies: List[str]) -> str:
        """Generar documentación para nuevas dependencias"""
        
        dep_installs = []
        for dep in dependencies:
            # Intentar mapear a nombres de pip packages conocidos
            pip_name = self.map_import_to_pip(dep)
            if pip_name:
                dep_installs.append(f"pip install {pip_name}")
        
        installs_text = "\n".join(dep_installs) if dep_installs else "# Revisar dependencias manualmente"
        
        return f"""
```bash
# Nuevas dependencias detectadas
{installs_text}
```

**Dependencias añadidas:**
{chr(10).join(f"- `{dep}`" for dep in dependencies)}
"""
    
    def map_import_to_pip(self, import_name: str) -> Optional[str]:
        """Mapear nombre de import a package de pip"""
        
        # Mapeo básico de imports conocidos
        import_to_pip = {
            "requests": "requests",
            "aiohttp": "aiohttp", 
            "pandas": "pandas",
            "numpy": "numpy",
            "plotly": "plotly",
            "streamlit": "streamlit",
            "selenium": "selenium",
            "PIL": "pillow",
            "cv2": "opencv-python",
            "torch": "torch"
        }
        
        # Obtener nombre base del import
        base_import = import_name.split('.')[0]
        
        return import_to_pip.get(base_import)
    
    async def detect_new_dependencies(self, imports: List[str]) -> List[str]:
        """Detectar dependencias que son nuevas y deben documentarse"""
        
        # Cargar dependencias conocidas
        known_deps = await self.load_known_dependencies()
        
        new_deps = []
        for imp in imports:
            base_import = imp.split('.')[0]
            
            # Ignorar imports locales y built-ins
            if (not self.is_external_package(base_import) or 
                base_import in known_deps):
                continue
                
            new_deps.append(base_import)
        
        return list(set(new_deps))  # Remove duplicates
    
    def is_external_package(self, package_name: str) -> bool:
        """Verificar si un package es externo (no built-in)"""
        
        builtin_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'random', 
            'asyncio', 'collections', 'functools', 'itertools',
            're', 'math', 'pathlib', 'typing', 'dataclasses'
        }
        
        return package_name not in builtin_modules
    
    async def load_known_dependencies(self) -> set:
        """Cargar lista de dependencias ya conocidas/documentadas"""
        
        # En producción esto leería de requirements.txt o similar
        known_deps = {
            'requests', 'aiohttp', 'pandas', 'numpy', 'plotly', 
            'streamlit', 'selenium', 'pillow', 'opencv-python',
            'torch', 'ultralytics', 'facebook-business'
        }
        
        return known_deps
    
    async def prioritize_updates(self, updates: List[DocumentationUpdate]) -> List[DocumentationUpdate]:
        """Priorizar actualizaciones por impacto y complejidad"""
        
        priority_weights = {
            "critical": 4,
            "high": 3,
            "medium": 2, 
            "low": 1
        }
        
        # Ordenar por prioridad y tipo
        sorted_updates = sorted(
            updates,
            key=lambda u: (
                priority_weights.get(u.priority, 0),
                u.update_type == "api_reference",  # API changes son más importantes
                u.target_file  # Agrupar por archivo
            ),
            reverse=True
        )
        
        return sorted_updates
    
    async def apply_automatic_updates(self, updates: List[DocumentationUpdate]) -> List[DocumentationUpdate]:
        """Aplicar automáticamente actualizaciones de baja complejidad"""
        
        auto_applied = []
        
        for update in updates:
            # Solo aplicar automáticamente actualizaciones simples y de baja prioridad
            if (update.priority in ["low", "medium"] and 
                update.update_type in ["configuration", "troubleshooting"] and
                "// Revisar manualmente //" not in update.suggested_content):
                
                try:
                    success = await self.apply_update_to_file(update)
                    if success:
                        auto_applied.append(update)
                        print(f"✅ Auto-applied: {update.description}")
                    
                except Exception as e:
                    print(f"❌ Failed to auto-apply update: {e}")
        
        return auto_applied
    
    async def apply_update_to_file(self, update: DocumentationUpdate) -> bool:
        """Aplicar una actualización específica a un archivo de documentación"""
        
        doc_file_path = self.functionality_guides_path / update.target_file
        
        if not doc_file_path.exists():
            print(f"❌ Documentation file not found: {doc_file_path}")
            return False
        
        try:
            # Leer archivo actual
            with open(doc_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar sección target
            section_pattern = f"## {update.section}"
            section_match = re.search(section_pattern, content)
            
            if not section_match:
                print(f"❌ Section '{update.section}' not found in {update.target_file}")
                return False
            
            # Insertar contenido nuevo al final de la sección
            # (Implementación simplificada - en producción sería más sofisticada)
            
            # Crear backup
            backup_path = doc_file_path.with_suffix('.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Aplicar actualización (placeholder - implementación real requiere parsing más sofisticado)
            updated_content = content + f"\n\n<!-- Auto-generated update -->\n{update.suggested_content}\n"
            
            # Escribir archivo actualizado
            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"📝 Updated {update.target_file} - {update.section}")
            return True
            
        except Exception as e:
            print(f"❌ Error applying update to {update.target_file}: {e}")
            return False
    
    async def generate_manual_update_report(self, manual_updates: List[DocumentationUpdate]):
        """Generar reporte de actualizaciones que requieren intervención manual"""
        
        if not manual_updates:
            return
        
        report_content = f"""
# 📋 Manual Documentation Updates Required

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total updates needed**: {len(manual_updates)}
- **High priority**: {len([u for u in manual_updates if u.priority == 'high'])}
- **Critical priority**: {len([u for u in manual_updates if u.priority == 'critical'])}

## Updates by File

"""
        
        # Agrupar por archivo
        updates_by_file = defaultdict(list)
        for update in manual_updates:
            updates_by_file[update.target_file].append(update)
        
        for doc_file, file_updates in updates_by_file.items():
            report_content += f"### 📄 {doc_file}\n\n"
            
            for update in file_updates:
                priority_emoji = {
                    "critical": "🚨",
                    "high": "⚠️", 
                    "medium": "📋",
                    "low": "💡"
                }
                
                report_content += f"""
#### {priority_emoji.get(update.priority, '📋')} {update.description}

**Priority**: {update.priority.upper()}  
**Section**: {update.section}  
**Type**: {update.update_type}

**Suggested Content:**
```
{update.suggested_content}
```

**Related Changes:**
"""
                
                for change in update.related_changes:
                    report_content += f"- `{change.file_path}` - {change.commit_message}\n"
                
                report_content += "\n---\n\n"
        
        # Guardar reporte
        report_path = self.docs_path / "manual_updates_needed.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Manual update report generated: {report_path}")
    
    async def get_last_scan_time(self) -> datetime:
        """Obtener timestamp del último scan de documentación"""
        
        if self.last_scan_file.exists():
            try:
                with open(self.last_scan_file, 'r') as f:
                    timestamp_str = f.read().strip()
                    return datetime.fromisoformat(timestamp_str)
            except Exception:
                pass
        
        # Default: hace 24 horas
        return datetime.now() - timedelta(days=1)
    
    async def update_last_scan_time(self):
        """Actualizar timestamp del último scan"""
        
        with open(self.last_scan_file, 'w') as f:
            f.write(datetime.now().isoformat())

# Sistema de scheduling para ejecución automática
class DocumentationUpdateScheduler:
    """Scheduler para ejecutar auto-updates periódicamente"""
    
    def __init__(self, updater: DocumentationAutoUpdater):
        self.updater = updater
        self.running = False
    
    async def start_scheduled_updates(self, interval_hours: int = 6):
        """Iniciar updates automáticos cada X horas"""
        
        self.running = True
        print(f"🕒 Starting scheduled documentation updates every {interval_hours} hours")
        
        while self.running:
            try:
                await self.updater.run_auto_update_cycle()
                
                # Esperar hasta próxima ejecución
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                print(f"❌ Error in scheduled update: {e}")
                await asyncio.sleep(300)  # Esperar 5 min antes de reintentar
    
    def stop_scheduled_updates(self):
        """Detener updates automáticos"""
        self.running = False
        print("🛑 Stopped scheduled documentation updates")

# CLI para ejecutar manualmente
async def main():
    """Función principal para ejecución manual"""
    
    print("🚀 Documentation Auto-Updater")
    print("=" * 40)
    
    updater = DocumentationAutoUpdater()
    
    try:
        # Ejecutar ciclo completo
        results = await updater.run_auto_update_cycle()
        
        print("\n✅ Update cycle completed successfully!")
        print(f"📊 Results: {results}")
        
    except Exception as e:
        print(f"❌ Error running auto-updater: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))