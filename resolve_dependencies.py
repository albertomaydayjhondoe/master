#!/usr/bin/env python3
"""
Universal Import Resolver and Dependency Manager
Resolves import issues across the entire project by installing missing packages
or providing dummy implementations when in development mode.
"""

import os
import sys
import subprocess
import importlib
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DependencyResolver:
    """Resolves missing dependencies across the project"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.dummy_mode = os.getenv('DUMMY_MODE', 'true').lower() == 'true'
        
        # Define package mappings
        self.package_mappings = {
            'selenium': 'selenium==4.15.2',
            'telethon': 'telethon==1.33.1', 
            'asyncpg': 'asyncpg==0.29.0',
            'aiohttp': 'aiohttp==3.9.1',
            'psycopg2': 'psycopg2-binary==2.9.7',
            'webdriver_manager': 'webdriver-manager==4.0.1',
            'colorlog': 'colorlog==6.8.0',
        }
    
    def check_missing_imports(self) -> dict:
        """Check for missing imports across Python files"""
        missing_imports = {}
        
        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.name.startswith('.') or 'dummy_implementations' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract import statements
                imports = self.extract_imports(content)
                
                # Check each import
                for imp in imports:
                    if not self.can_import(imp):
                        if py_file not in missing_imports:
                            missing_imports[py_file] = []
                        missing_imports[py_file].append(imp)
                        
            except Exception as e:
                logger.debug(f"Error checking {py_file}: {e}")
        
        return missing_imports
    
    def extract_imports(self, content: str) -> list:
        """Extract import statements from Python code"""
        imports = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Handle 'import module' statements
            if line.startswith('import ') and not line.startswith('import os') and not line.startswith('import sys'):
                module = line.replace('import ', '').split()[0].split('.')[0]
                imports.append(module)
            
            # Handle 'from module import' statements  
            elif line.startswith('from ') and ' import ' in line:
                module = line.split(' import ')[0].replace('from ', '').split('.')[0]
                if module not in ['os', 'sys', 'typing', 'datetime', 'pathlib', 'json', 'asyncio', 'logging', 'random', 'time']:
                    imports.append(module)
        
        return list(set(imports))
    
    def can_import(self, module_name: str) -> bool:
        """Check if a module can be imported"""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
    
    def install_missing_packages(self, missing_imports: dict) -> bool:
        """Install missing packages"""
        if self.dummy_mode:
            logger.info("🎭 DUMMY MODE: Skipping package installation")
            return True
        
        # Collect unique missing packages
        missing_packages = set()
        for file_imports in missing_imports.values():
            for imp in file_imports:
                if imp in self.package_mappings:
                    missing_packages.add(self.package_mappings[imp])
                else:
                    missing_packages.add(imp)
        
        if not missing_packages:
            logger.info("✅ No missing packages to install")
            return True
        
        logger.info(f"📦 Installing missing packages: {list(missing_packages)}")
        
        try:
            # Install packages
            for package in missing_packages:
                logger.info(f"Installing {package}...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], check=True, capture_output=True)
            
            logger.info("✅ All packages installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install packages: {e}")
            return False
    
    def create_dummy_imports_file(self, missing_imports: dict):
        """Create or update dummy imports configuration"""
        if not self.dummy_mode:
            return
        
        # Collect all missing modules
        all_missing = set()
        for file_imports in missing_imports.values():
            all_missing.update(file_imports)
        
        if not all_missing:
            return
        
        # Create __init__.py file with dummy imports
        init_file = self.project_root / '__init__.py'
        
        dummy_code = '''"""
Auto-generated dummy imports for development mode
This file provides dummy implementations for missing packages
"""
import sys
import os

DUMMY_MODE = os.getenv('DUMMY_MODE', 'true').lower() == 'true'

if DUMMY_MODE:
    # Create dummy modules for missing imports
    dummy_modules = {}
    
'''
        
        for module in sorted(all_missing):
            dummy_code += f"    # Dummy {module}\n"
            dummy_code += f"    class Dummy{module.capitalize()}:\n"
            dummy_code += f"        def __getattr__(self, name): return lambda *args, **kwargs: None\n"
            dummy_code += f"    dummy_modules['{module}'] = Dummy{module.capitalize()}()\n\n"
        
        dummy_code += '''
    # Add dummy modules to sys.modules
    for name, module in dummy_modules.items():
        if name not in sys.modules:
            sys.modules[name] = module
            print(f"🎭 Dummy module loaded: {name}")
'''
        
        with open(init_file, 'w') as f:
            f.write(dummy_code)
        
        logger.info(f"✅ Created dummy imports file: {init_file}")
    
    def resolve_all(self):
        """Main resolution method"""
        logger.info("🔍 Checking for missing imports...")
        
        missing_imports = self.check_missing_imports()
        
        if not missing_imports:
            logger.info("✅ No missing imports found")
            return True
        
        logger.info(f"📋 Found missing imports in {len(missing_imports)} files")
        
        for file_path, imports in missing_imports.items():
            logger.info(f"  {file_path.name}: {imports}")
        
        if self.dummy_mode:
            logger.info("🎭 Creating dummy implementations...")
            self.create_dummy_imports_file(missing_imports)
        else:
            logger.info("🚀 Installing missing packages...")
            success = self.install_missing_packages(missing_imports)
            if not success:
                logger.error("❌ Failed to install some packages")
                return False
        
        logger.info("✅ Dependency resolution complete")
        return True

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    resolver = DependencyResolver(project_root)
    success = resolver.resolve_all()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()