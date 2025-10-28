#!/usr/bin/env python3
"""
🔧 PATH FIXER - CROSS PLATFORM COMPATIBILITY
Corrige paths y comandos específicos de sistemas en todo el proyecto
"""

import os
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PathFixer:
    """Corrige paths y comandos para compatibilidad multiplataforma"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = []
        
    def fix_shebang_lines(self):
        """Corrige las líneas shebang problemáticas"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                # Reemplazar shebangs problemáticos
                shebang_fixes = [
                    (r'^#!/usr/bin/env python3.*$', '#!/usr/bin/env python3'),
                    (r'^#!/usr/bin/python3.*$', '#!/usr/bin/env python3'),
                    (r'^#!/usr/bin/python.*$', '#!/usr/bin/env python3'),
                ]
                
                for pattern, replacement in shebang_fixes:
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    self.fixes_applied.append(f"Fixed shebang in {file_path.relative_to(self.project_root)}")
                    
            except Exception as e:
                logger.warning(f"Could not fix shebang in {file_path}: {e}")
    
    def fix_subprocess_calls(self):
        """Corrige llamadas subprocess problemáticas"""
        python_files = list(self.project_root.rglob("*.py"))
        
        problematic_patterns = [
            # Comandos específicos de shell
            (r'subprocess\.run\(\[\'bash\'', 'subprocess.run(['),
            (r'subprocess\.run\(\[\'sh\'', 'subprocess.run(['),
            (r'subprocess\.call\(\[\'bash\'', 'subprocess.call(['),
            (r'os\.system\(f?["\']bash ', 'os.system(f"'),
            
            # Paths con barras específicas
            (r'executable=[\'"][\'"]', 'shell=True'),
        ]
        
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content
                
                for pattern, replacement in problematic_patterns:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    self.fixes_applied.append(f"Fixed subprocess calls in {file_path.relative_to(self.project_root)}")
                    
            except Exception as e:
                logger.warning(f"Could not fix subprocess calls in {file_path}: {e}")
    
    def fix_hardcoded_paths(self):
        """Corrige paths hardcodeados problemáticos"""
        files_to_check = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.md"))
        
        path_fixes = [
            # Scripts bash/powershell
            (r'\.\/[\w\-]+\.sh', 'python scripts/cross_platform_runner.py'),
            (r'\.\\[\w\-]+\.ps1', 'python scripts/cross_platform_runner.py'),
            (r'bash [\w\-]+\.sh', 'python scripts/cross_platform_runner.py'),
            (r'powershell [\w\-]+\.ps1', 'python scripts/cross_platform_runner.py'),
            
            # Paths específicos de Unix
            (r'/usr/bin/env python3', '/usr/bin/env python3'),  # Mantener pero normalizar
            (r'', ''),  # Remover referencias específicas
        ]
        
        for file_path in files_to_check:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                original_content = content
                
                for pattern, replacement in path_fixes:
                    if replacement == '':
                        # Para patrones que queremos remover completamente
                        content = re.sub(pattern, '', content)
                    else:
                        content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    self.fixes_applied.append(f"Fixed paths in {file_path.relative_to(self.project_root)}")
                    
            except Exception as e:
                logger.warning(f"Could not fix paths in {file_path}: {e}")
    
    def create_cross_platform_runner(self):
        """Crea un runner universal para scripts"""
        runner_content = '''#!/usr/bin/env python3
"""
🔧 Cross Platform Script Runner
Ejecuta scripts de forma compatible con cualquier sistema
"""

import sys
import os
from pathlib import Path
from cross_platform_launcher import CrossPlatformLauncher

def main():
    """Ejecuta scripts de forma multiplataforma"""
    if len(sys.argv) < 2:
        print("Uso: python cross_platform_runner.py <action>")
        print("Acciones disponibles:")
        print("  setup - Configurar sistema")
        print("  start - Iniciar sistema")
        print("  install - Instalar dependencias")
        print("  deploy - Preparar deployment")
        return
    
    action = sys.argv[1]
    launcher = CrossPlatformLauncher()
    
    if action == "setup":
        print("🔧 Configurando sistema...")
        launcher.install_requirements()
        
    elif action == "start":
        print("🚀 Iniciando sistema...")
        os.system(f"{launcher.get_python_command()} universal_startup.py")
        
    elif action == "install":
        print("📦 Instalando dependencias...")
        launcher.install_requirements()
        if Path("requirements-ml.txt").exists():
            launcher.install_requirements("requirements-ml.txt")
            
    elif action == "deploy":
        print("🚀 Preparando deployment...")
        os.system(f"{launcher.get_python_command()} railway_launcher.py")
        
    else:
        print(f"❌ Acción no reconocida: {action}")

if __name__ == "__main__":
    main()
'''
        
        runner_path = self.project_root / "scripts" / "cross_platform_runner.py"
        runner_path.parent.mkdir(exist_ok=True)
        runner_path.write_text(runner_content, encoding='utf-8')
        
        self.fixes_applied.append("Created cross_platform_runner.py")
    
    def fix_all(self):
        """Aplica todas las correcciones"""
        logger.info("🔧 Iniciando corrección de compatibilidad multiplataforma...")
        
        # Aplicar todas las correcciones
        self.fix_shebang_lines()
        self.fix_subprocess_calls()
        self.fix_hardcoded_paths()
        self.create_cross_platform_runner()
        
        # Mostrar resumen
        logger.info(f"✅ Correcciones aplicadas: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            logger.info("📝 Detalles de las correcciones:")
            for fix in self.fixes_applied[:10]:  # Mostrar las primeras 10
                logger.info(f"  - {fix}")
            
            if len(self.fixes_applied) > 10:
                logger.info(f"  ... y {len(self.fixes_applied) - 10} más")
        
        logger.info("🚀 Sistema listo para usar en cualquier plataforma")

def main():
    """Punto de entrada principal"""
    fixer = PathFixer()
    fixer.fix_all()

if __name__ == "__main__":
    main()