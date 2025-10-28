#!/usr/bin/env python3
"""
Railway Docker Deployment Manager
Gestiona el deployment completo del sistema Stakas ML via Docker
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class RailwayDockerManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docker_image = "stakasml/stakas-ml"
        self.railway_config = {
            "build": {
                "builder": "DOCKERFILE",
                "dockerfilePath": "Dockerfile"
            },
            "deploy": {
                "startCommand": "streamlit run ml_core/api/main.py --server.port $PORT --server.address 0.0.0.0",
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 3
            }
        }
        
    def check_prerequisites(self):
        """Verificar requisitos previos"""
        print("🔍 Verificando prerequisitos...")
        
        # Docker
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            print("✅ Docker instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker no encontrado. Instala Docker Desktop")
            return False
            
        # Git
        try:
            subprocess.run(["git", "--version"], 
                         capture_output=True, check=True)
            print("✅ Git disponible")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git no encontrado")
            return False
            
        return True
        
    def build_docker_image(self, tag="latest"):
        """Build de la imagen Docker"""
        print(f"🏗️  Building Docker image: {self.docker_image}:{tag}")
        
        cmd = [
            "docker", "build",
            "--target", "production",
            "-t", f"{self.docker_image}:{tag}",
            "."
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=False, text=True)
            if result.returncode == 0:
                print(f"✅ Build exitoso: {self.docker_image}:{tag}")
                return True
            else:
                print(f"❌ Build falló con código: {result.returncode}")
                return False
        except Exception as e:
            print(f"❌ Error en build: {e}")
            return False
            
    def test_image_locally(self, tag="latest"):
        """Test local de la imagen"""
        print(f"🧪 Testing imagen: {self.docker_image}:{tag}")
        
        # Test basic run
        cmd = [
            "docker", "run", "--rm",
            "-p", "8080:8080",
            "-e", "DUMMY_MODE=true",
            "-e", "CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg",
            "--name", "stakas-test",
            f"{self.docker_image}:{tag}"
        ]
        
        print("Iniciando contenedor de test...")
        print("⚠️  Presiona Ctrl+C para detener el test")
        
        try:
            subprocess.run(cmd, cwd=self.project_root)
            return True
        except KeyboardInterrupt:
            print("\n🛑 Test detenido por usuario")
            # Cleanup container
            subprocess.run(["docker", "stop", "stakas-test"], 
                         capture_output=True)
            return True
        except Exception as e:
            print(f"❌ Error en test: {e}")
            return False
            
    def push_to_dockerhub(self, tag="latest"):
        """Push imagen a Docker Hub"""
        print(f"📦 Pushing a Docker Hub: {self.docker_image}:{tag}")
        
        # Login check
        dockerhub_username = os.getenv('DOCKERHUB_USERNAME')
        dockerhub_token = os.getenv('DOCKERHUB_TOKEN')
        
        if not dockerhub_username or not dockerhub_token:
            print("⚠️  Variables DOCKERHUB_USERNAME y DOCKERHUB_TOKEN requeridas")
            print("   Configúralas en el entorno o en GitHub Secrets")
            
            # Interactive login
            try:
                subprocess.run(["docker", "login"], check=True)
            except subprocess.CalledProcessError:
                print("❌ Login a Docker Hub falló")
                return False
        
        # Push
        try:
            cmd = ["docker", "push", f"{self.docker_image}:{tag}"]
            result = subprocess.run(cmd, capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"✅ Push exitoso: {self.docker_image}:{tag}")
                return True
            else:
                print(f"❌ Push falló con código: {result.returncode}")
                return False
        except Exception as e:
            print(f"❌ Error en push: {e}")
            return False
            
    def generate_railway_config(self):
        """Generar configuración para Railway"""
        print("⚙️  Generando configuración Railway...")
        
        config_file = self.project_root / "railway.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(self.railway_config, f, indent=2)
            
            print(f"✅ Configuración guardada: {config_file}")
            print("\n📋 Variables de entorno requeridas en Railway:")
            
            env_vars = [
                "ENVIRONMENT=production",
                "DUMMY_MODE=false", 
                "CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg",
                "META_ADS_BUDGET=500",
                "PORT=8080",
                "TZ=Europe/Madrid",
                "PYTHONPATH=/app"
            ]
            
            for var in env_vars:
                print(f"   {var}")
                
            return True
        except Exception as e:
            print(f"❌ Error generando config: {e}")
            return False
            
    def deploy_to_railway_via_github(self):
        """Preparar deployment via GitHub Actions"""
        print("🚀 Preparando deployment via GitHub Actions...")
        
        # Verificar que existe workflow
        workflow_file = self.project_root / ".github/workflows/docker-deploy.yml"
        if not workflow_file.exists():
            print(f"❌ Workflow no encontrado: {workflow_file}")
            return False
            
        print("✅ Workflow GitHub Actions encontrado")
        print("\n📋 Pasos para deployment automático:")
        print("1. Configurar secrets en GitHub:")
        print("   - DOCKERHUB_USERNAME")
        print("   - DOCKERHUB_TOKEN") 
        print("   - RAILWAY_TOKEN")
        print("2. Push código a GitHub:")
        print("   git add .")
        print("   git commit -m 'feat: docker deployment ready'")
        print("   git push origin main")
        print("3. Monitorear GitHub Actions tab")
        print("4. Verificar deployment en Railway dashboard")
        
        return True
        
    def full_deployment_pipeline(self):
        """Pipeline completo de deployment"""
        print("🎯 Iniciando pipeline completo de deployment\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tag = f"v{timestamp}"
        
        # 1. Prerequisites
        if not self.check_prerequisites():
            return False
            
        # 2. Build
        if not self.build_docker_image(tag):
            return False
            
        # 3. Test local (opcional)
        test_local = input("\n🧪 ¿Quieres hacer test local? (y/N): ").lower()
        if test_local == 'y':
            if not self.test_image_locally(tag):
                print("⚠️  Test falló, pero continuando...")
                
        # 4. Tag como latest
        try:
            subprocess.run([
                "docker", "tag", 
                f"{self.docker_image}:{tag}",
                f"{self.docker_image}:latest"
            ], check=True)
            print(f"✅ Tagged como latest")
        except Exception as e:
            print(f"❌ Error tagging: {e}")
            return False
            
        # 5. Push to Docker Hub
        push_hub = input("\n📦 ¿Push a Docker Hub? (y/N): ").lower()
        if push_hub == 'y':
            if not self.push_to_dockerhub("latest"):
                return False
            if not self.push_to_dockerhub(tag):
                return False
                
        # 6. Railway config
        if not self.generate_railway_config():
            return False
            
        # 7. GitHub deployment prep
        if not self.deploy_to_railway_via_github():
            return False
            
        print("\n🎉 Pipeline completado exitosamente!")
        print(f"📦 Imagen: {self.docker_image}:latest")
        print("🚀 Listo para deployment automático via GitHub Actions")
        
        return True

def main():
    """Menú principal interactivo"""
    manager = RailwayDockerManager()
    
    print("=" * 60)
    print("🚀 Railway Docker Deployment Manager")
    print("📺 Canal: Stakas MVP (UCgohgqLVu1QPdfa64Vkrgeg)")
    print("💰 Budget: €500/month Meta Ads")
    print("=" * 60)
    
    while True:
        print("\n🎛️  Opciones disponibles:")
        print("1. ✅ Verificar prerequisitos")
        print("2. 🏗️  Build Docker image")
        print("3. 🧪 Test imagen local")
        print("4. 📦 Push a Docker Hub")
        print("5. ⚙️  Generar config Railway")
        print("6. 🚀 Preparar GitHub deployment")
        print("7. 🎯 Pipeline completo")
        print("8. ❌ Salir")
        
        choice = input("\n👉 Selecciona opción (1-8): ").strip()
        
        if choice == "1":
            manager.check_prerequisites()
            
        elif choice == "2":
            tag = input("Tag (default: latest): ").strip() or "latest"
            manager.build_docker_image(tag)
            
        elif choice == "3":
            tag = input("Tag a testear (default: latest): ").strip() or "latest"
            manager.test_image_locally(tag)
            
        elif choice == "4":
            tag = input("Tag a pushear (default: latest): ").strip() or "latest"
            manager.push_to_dockerhub(tag)
            
        elif choice == "5":
            manager.generate_railway_config()
            
        elif choice == "6":
            manager.deploy_to_railway_via_github()
            
        elif choice == "7":
            manager.full_deployment_pipeline()
            
        elif choice == "8":
            print("👋 ¡Hasta luego! Deploy exitoso 🚀")
            break
            
        else:
            print("❌ Opción inválida. Intenta 1-8")

if __name__ == "__main__":
    main()