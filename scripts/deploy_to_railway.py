#!/usr/bin/env python3
"""
🚀 Railway Deployment Script - Stakas MVP Viral System
Build and deploy complete viral analysis dashboard to Railway
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

class RailwayDeployer:
    """Deploy Stakas MVP system to Railway"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.channel_id = "UCgohgqLVu1QPdfa64Vkrgeg"
        self.app_name = "stakas-mvp-viral"
        
    def check_railway_cli(self) -> bool:
        """Verifica si Railway CLI está instalado"""
        try:
            result = subprocess.run(['railway', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Railway CLI detectado: {result.stdout.strip()}")
                return True
            else:
                return False
        except FileNotFoundError:
            return False
    
    def install_railway_cli(self) -> bool:
        """Instala Railway CLI"""
        print("📦 Instalando Railway CLI...")
        
        try:
            # Para Windows
            if os.name == 'nt':
                subprocess.run([
                    'powershell', '-Command',
                    'iex (iwr https://install.railway.app -useb)'
                ], check=True)
            else:
                # Para Unix/Linux/Mac
                subprocess.run([
                    'bash', '-c',
                    'curl -fsSL https://install.railway.app | bash'
                ], check=True)
            
            print("✅ Railway CLI instalado correctamente")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando Railway CLI: {e}")
            return False
    
    def setup_environment_variables(self):
        """Configura variables de entorno para Railway"""
        
        env_vars = {
            # App configuration
            'APP_ENV': 'production',
            'CHANNEL_ID': 'UCgohgqLVu1QPdfa64Vkrgeg',
            'CHANNEL_NAME': 'Stakas MVP',
            'GENRE': 'drill_rap_espanol',
            'TARGET_SUBSCRIBERS': '10000',
            'META_ADS_BUDGET': '500',
            
            # Streamlit configuration
            'STREAMLIT_SERVER_HEADLESS': 'true',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
            'STREAMLIT_SERVER_ENABLE_CORS': 'false',
            'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'false',
            
            # Performance
            'PYTHONUNBUFFERED': '1',
            'PYTHONDONTWRITEBYTECODE': '1'
        }
        
        print("🔧 Configurando variables de entorno en Railway...")
        
        for key, value in env_vars.items():
            try:
                result = subprocess.run([
                    'railway', 'variables', 'set', f'{key}={value}'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {key} = {value}")
                else:
                    print(f"⚠️  Error configurando {key}: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Error con variable {key}: {e}")
    
    def create_railway_project(self) -> bool:
        """Crea proyecto en Railway"""
        print("🚂 Creando proyecto Railway...")
        
        try:
            # Inicializar proyecto Railway
            result = subprocess.run([
                'railway', 'init', self.app_name
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Proyecto Railway creado")
                return True
            else:
                print(f"⚠️  Proyecto puede existir ya: {result.stderr}")
                # Intentar link a proyecto existente
                result = subprocess.run([
                    'railway', 'link'
                ], capture_output=True, text=True, cwd=self.project_root)
                return result.returncode == 0
                
        except Exception as e:
            print(f"❌ Error creando proyecto: {e}")
            return False
    
    def deploy_to_railway(self) -> bool:
        """Deploy a Railway"""
        print("🚀 Deploying a Railway...")
        
        try:
            # Deploy usando Railway
            result = subprocess.run([
                'railway', 'up', '--detach'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Deploy exitoso!")
                print(result.stdout)
                return True
            else:
                print(f"❌ Error en deploy: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error en deploy: {e}")
            return False
    
    def get_deployment_info(self):
        """Obtiene información del deployment"""
        print("📋 Obteniendo información del deployment...")
        
        try:
            # Status del deployment
            result = subprocess.run([
                'railway', 'status'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("📊 Status del deployment:")
                print(result.stdout)
            
            # URL del deployment
            result = subprocess.run([
                'railway', 'domain'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("🌐 URL del deployment:")
                print(result.stdout)
            
        except Exception as e:
            print(f"❌ Error obteniendo info: {e}")
    
    def optimize_dockerfile_for_railway(self):
        """Optimiza Dockerfile para Railway"""
        print("🔧 Optimizando Dockerfile para Railway...")
        
        dockerfile_content = """# 🚀 Stakas MVP Viral Dashboard - Railway Optimized
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \\
    pip install --no-cache-dir streamlit matplotlib seaborn plotly

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs uploads cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:$PORT/health || exit 1

# Start command (will be overridden by Railway)
CMD ["streamlit", "run", "scripts/viral_study_analysis.py", "--server.port", "$PORT", "--server.address", "0.0.0.0", "--server.headless", "true"]
"""
        
        with open(self.project_root / "Dockerfile", 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        print("✅ Dockerfile optimizado para Railway")
    
    def create_railway_ignore(self):
        """Crea .railwayignore para optimizar build"""
        
        ignore_content = """# Railway ignore file for Stakas MVP
.git/
.github/
*.pyc
__pycache__/
.pytest_cache/
.coverage
.venv/
venv/
.env*
.DS_Store
Thumbs.db
*.log
.idea/
.vscode/
node_modules/
docker-compose*.yml
.dockerignore
README*.md
docs/
examples/
tests/
.gitignore
"""
        
        with open(self.project_root / ".railwayignore", 'w', encoding='utf-8') as f:
            f.write(ignore_content)
        
        print("✅ .railwayignore creado")
    
    def run_deployment(self):
        """Ejecuta el deployment completo"""
        
        print("🎵" + "="*50 + "🎵")
        print("🚀 STAKAS MVP - RAILWAY DEPLOYMENT")
        print(f"📺 Canal: {self.channel_id}")
        print(f"🎬 App: {self.app_name}")
        print("🎯 Dashboard de Viralidad + ML Analytics")
        print("🎵" + "="*50 + "🎵\n")
        
        # 1. Verificar/instalar Railway CLI
        if not self.check_railway_cli():
            print("⚠️  Railway CLI no encontrado. Instalando...")
            if not self.install_railway_cli():
                print("❌ No se pudo instalar Railway CLI")
                print("📋 Instala manualmente desde: https://railway.app/cli")
                return False
        
        # 2. Optimizar archivos para Railway
        self.optimize_dockerfile_for_railway()
        self.create_railway_ignore()
        
        # 3. Login a Railway (interactivo)
        print("🔐 Necesitas hacer login a Railway...")
        print("Ejecuta manualmente: railway login")
        
        login_done = input("¿Ya hiciste login a Railway? (y/n): ").lower().strip()
        if login_done != 'y':
            print("Por favor ejecuta 'railway login' primero y vuelve a correr este script")
            return False
        
        # 4. Crear/linkear proyecto
        if not self.create_railway_project():
            return False
        
        # 5. Configurar variables de entorno
        self.setup_environment_variables()
        
        # 6. Deploy
        if not self.deploy_to_railway():
            return False
        
        # 7. Obtener información del deployment
        time.sleep(5)  # Esperar un poco para que el deploy se complete
        self.get_deployment_info()
        
        print("\n🎉 ¡DEPLOYMENT COMPLETADO!")
        print("📊 Dashboard de Viralidad Stakas MVP desplegado en Railway")
        print("🎯 Accede a la URL mostrada arriba para ver el análisis completo")
        print("🚀 Sistema listo para analizar UCgohgqLVu1QPdfa64Vkrgeg")
        
        return True

def main():
    """Función principal"""
    
    deployer = RailwayDeployer()
    
    try:
        success = deployer.run_deployment()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Deployment cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()