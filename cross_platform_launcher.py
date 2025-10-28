#!/usr/bin/env python3
"""
🚀 CROSS-PLATFORM SYSTEM LAUNCHER
Launcher universal compatible con Linux, Windows y macOS
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CrossPlatformLauncher:
    """Launcher que detecta el sistema y ejecuta comandos compatibles"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_linux = self.system == 'linux'
        self.is_mac = self.system == 'darwin'
        self.shell = self.detect_shell()
        
    def detect_shell(self):
        """Detecta el shell disponible"""
        if self.is_windows:
            if shutil.which('powershell'):
                return 'powershell'
            elif shutil.which('pwsh'):
                return 'pwsh'
            else:
                return 'cmd'
        else:
            return os.environ.get('SHELL', '')
    
    def run_command(self, command: str, shell: bool = True, check: bool = True):
        """Ejecuta comando de forma cross-platform"""
        try:
            if self.is_windows and shell:
                # En Windows, usar subprocess con shell=True
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    check=check
                )
            else:
                # En Linux/Mac, usar bash
                result = subprocess.run(
                    command,
                    shell=shell,
                    capture_output=True,
                    text=True,
                    check=check,
                    shell=True if not self.is_windows else None
                )
            
            return result.stdout.strip() if result.stdout else ""
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {command}")
            logger.error(f"Error: {e.stderr}")
            if check:
                raise
            return None
    
    def get_python_command(self):
        """Obtiene el comando Python correcto para el sistema"""
        python_commands = ['python3', 'python', 'py']
        
        for cmd in python_commands:
            if shutil.which(cmd):
                return cmd
        
        raise RuntimeError("No se encontró Python en el sistema")
    
    def get_pip_command(self):
        """Obtiene el comando pip correcto"""
        pip_commands = ['pip3', 'pip', f'{self.get_python_command()} -m pip']
        
        for cmd in pip_commands:
            try:
                if ' -m pip' in cmd:
                    # Test using python -m pip
                    self.run_command(f'{cmd} --version')
                    return cmd
                elif shutil.which(cmd.split()[0]):
                    return cmd
            except:
                continue
        
        return f'{self.get_python_command()} -m pip'
    
    def install_requirements(self, requirements_file: str = 'requirements.txt'):
        """Instala requirements de forma cross-platform"""
        pip_cmd = self.get_pip_command()
        
        if Path(requirements_file).exists():
            logger.info(f"Instalando {requirements_file}...")
            self.run_command(f'{pip_cmd} install -r {requirements_file}')
        else:
            logger.warning(f"No se encontró {requirements_file}")
    
    def start_streamlit(self, script: str, port: int = 8501):
        """Inicia Streamlit de forma cross-platform"""
        python_cmd = self.get_python_command()
        
        command = f'{python_cmd} -m streamlit run {script} --server.port {port} --server.address 0.0.0.0'
        
        if self.is_windows:
            # En Windows, agregar --server.headless para evitar problemas
            command += ' --server.headless true'
        
        logger.info(f"Iniciando Streamlit: {command}")
        
        # Para Streamlit, no usar capture_output para ver logs en tiempo real
        subprocess.Popen(
            command,
            shell=True,
            shell=True if not self.is_windows else None
        )
    
    def start_fastapi(self, app_module: str, port: int = 8000):
        """Inicia FastAPI de forma cross-platform"""
        python_cmd = self.get_python_command()
        
        command = f'{python_cmd} -m uvicorn {app_module} --host 0.0.0.0 --port {port}'
        
        logger.info(f"Iniciando FastAPI: {command}")
        
        subprocess.Popen(
            command,
            shell=True,
            shell=True if not self.is_windows else None
        )
    
    def check_dependencies(self):
        """Verifica dependencias del sistema"""
        dependencies = {
            'python': self.get_python_command(),
            'pip': self.get_pip_command(),
            'git': 'git'
        }
        
        missing = []
        
        for name, cmd in dependencies.items():
            try:
                if ' -m ' in cmd:
                    # Para comandos como "python -m pip"
                    self.run_command(f'{cmd} --version')
                else:
                    if not shutil.which(cmd):
                        missing.append(name)
            except:
                missing.append(name)
        
        if missing:
            logger.error(f"Dependencias faltantes: {', '.join(missing)}")
            return False
        
        logger.info("✅ Todas las dependencias están disponibles")
        return True
    
    def get_startup_info(self):
        """Información del sistema para debugging"""
        return {
            'system': self.system,
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'python_command': self.get_python_command(),
            'pip_command': self.get_pip_command(),
            'shell': self.shell,
            'cwd': os.getcwd()
        }

def main():
    """Función principal para testing del launcher"""
    launcher = CrossPlatformLauncher()
    
    print("🚀 Cross-Platform Launcher Test")
    print("=" * 50)
    
    info = launcher.get_startup_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n🔍 Verificando dependencias...")
    launcher.check_dependencies()

if __name__ == "__main__":
    main()