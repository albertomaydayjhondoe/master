#!/usr/bin/env python3
"""
🚀 Railway Deployment Script para Stakas MVP
Sistema automatizado de build, test y deploy a Railway
Canal: UCgohgqLVu1QPdfa64Vkrgeg | Budget: €500/month Meta Ads
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

class StakasRailwayDeployer:
    def __init__(self):
        self.project_name = "stakas-mvp-viral"
        self.channel_id = "UCgohgqLVu1QPdfa64Vkrgeg"
        self.docker_image = "stakasmvp/viral-system"
        self.project_root = Path(__file__).parent
        
    def print_banner(self):
        """Banner de inicio"""
        print("=" * 70)
        print("🎵 STAKAS MVP - VIRAL SYSTEM DEPLOYMENT")
        print("🎯 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
        print("💰 Budget: €500/month Meta Ads")
        print("🚀 Target: Railway Production Deployment")
        print("=" * 70)
        
    def check_prerequisites(self):
        """Verificar herramientas necesarias"""
        print("\n🔍 Verificando prerequisitos...")
        
        tools = [
            ("docker", "Docker para builds"),
            ("git", "Git para versioning"),
        ]
        
        missing_tools = []
        for tool, description in tools:
            try:
                subprocess.run([tool, "--version"], 
                             capture_output=True, check=True)
                print(f"✅ {description}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ {description}")
                missing_tools.append(tool)
        
        # Railway CLI es opcional
        try:
            subprocess.run(["railway", "--version"], 
                         capture_output=True, check=True)
            print("✅ Railway CLI (opcional)")
            self.has_railway_cli = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Railway CLI no instalado (usando deployment manual)")
            self.has_railway_cli = False
            
        if missing_tools:
            print(f"\n❌ Faltan herramientas: {', '.join(missing_tools)}")
            return False
            
        return True
        
    def build_docker_image(self, tag="latest"):
        """Build optimizado de Docker image"""
        print(f"\n🏗️  Building Docker image: {self.docker_image}:{tag}")
        
        build_args = [
            "docker", "build",
            "-t", f"{self.docker_image}:{tag}",
            "--build-arg", f"CHANNEL_ID={self.channel_id}",
            "--build-arg", "META_ADS_BUDGET=500",
            "--build-arg", "ENVIRONMENT=production",
            "--platform", "linux/amd64",  # Railway compatibility
            "."
        ]
        
        print("📦 Build command:", " ".join(build_args))
        
        try:
            result = subprocess.run(build_args, 
                                  cwd=self.project_root,
                                  capture_output=False, 
                                  text=True)
            
            if result.returncode == 0:
                print(f"✅ Build exitoso: {self.docker_image}:{tag}")
                return True
            else:
                print(f"❌ Build falló con código: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Error durante build: {e}")
            return False
            
    def test_image_locally(self, tag="latest", port=8080):
        """Test local de la imagen"""
        print(f"\n🧪 Testing imagen localmente en puerto {port}...")
        
        # Detener contenedor anterior si existe
        subprocess.run(["docker", "stop", "stakas-test"], 
                      capture_output=True)
        subprocess.run(["docker", "rm", "stakas-test"], 
                      capture_output=True)
        
        test_cmd = [
            "docker", "run", "--rm", "-d",
            "--name", "stakas-test",
            "-p", f"{port}:8080",
            "-e", "DUMMY_MODE=true",
            "-e", f"CHANNEL_ID={self.channel_id}",
            "-e", "META_ADS_BUDGET=500",
            "-e", "ENVIRONMENT=testing",
            f"{self.docker_image}:{tag}"
        ]
        
        try:
            # Iniciar contenedor
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Error iniciando contenedor: {result.stderr}")
                return False
                
            print("⏳ Esperando que la aplicación inicie...")
            time.sleep(15)  # Dar tiempo a Streamlit para iniciar
            
            # Test health check
            health_cmd = [
                "docker", "exec", "stakas-test",
                "curl", "-f", f"http://localhost:8080/health"
            ]
            
            health_result = subprocess.run(health_cmd, 
                                         capture_output=True, 
                                         text=True)
            
            if health_result.returncode == 0:
                print(f"✅ Health check OK - App corriendo en http://localhost:{port}")
                
                # Mostrar logs brevemente
                logs_cmd = ["docker", "logs", "--tail", "10", "stakas-test"]
                logs_result = subprocess.run(logs_cmd, 
                                           capture_output=True, 
                                           text=True)
                if logs_result.stdout:
                    print("📋 Últimos logs:")
                    print(logs_result.stdout)
                    
                return True
            else:
                print("❌ Health check falló")
                # Mostrar logs en caso de error
                logs_cmd = ["docker", "logs", "stakas-test"]
                logs_result = subprocess.run(logs_cmd, 
                                           capture_output=True, 
                                           text=True)
                if logs_result.stdout:
                    print("📋 Logs del contenedor:")
                    print(logs_result.stdout)
                return False
                
        except Exception as e:
            print(f"❌ Error durante test: {e}")
            return False
            
        finally:
            # Limpiar contenedor de test
            subprocess.run(["docker", "stop", "stakas-test"], 
                          capture_output=True)
            
    def create_railway_config(self):
        """Generar configuración Railway optimizada"""
        print("\n⚙️  Generando configuración Railway...")
        
        railway_config = {
            "$schema": "https://railway.app/railway.schema.json",
            "build": {
                "builder": "DOCKERFILE",
                "dockerfilePath": "Dockerfile"
            },
            "deploy": {
                "numReplicas": 1,
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 3,
                "healthcheckPath": "/health",
                "healthcheckTimeout": 30,
                "sleepApplication": False
            }
        }
        
        config_file = self.project_root / "railway.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(railway_config, f, indent=2)
                
            print(f"✅ Configuración guardada: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando config: {e}")
            return False
            
    def deploy_to_railway(self):
        """Deploy a Railway usando CLI o instrucciones manuales"""
        print("\n🚀 Iniciando deployment a Railway...")
        
        if self.has_railway_cli:
            return self._deploy_with_cli()
        else:
            return self._deploy_manual_instructions()
            
    def _deploy_with_cli(self):
        """Deploy usando Railway CLI"""
        print("📡 Usando Railway CLI para deployment...")
        
        try:
            # Login check
            login_result = subprocess.run(["railway", "whoami"], 
                                        capture_output=True, text=True)
            
            if login_result.returncode != 0:
                print("🔐 Necesitas hacer login a Railway:")
                subprocess.run(["railway", "login"])
                
            # Deploy
            print("🚀 Iniciando deployment...")
            deploy_result = subprocess.run(["railway", "up", "--detach"], 
                                         capture_output=False, text=True)
            
            if deploy_result.returncode == 0:
                print("✅ Deployment exitoso!")
                
                # Get deployment URL
                url_result = subprocess.run(["railway", "domain"], 
                                          capture_output=True, text=True)
                if url_result.stdout:
                    print(f"🌍 URL: {url_result.stdout.strip()}")
                    
                return True
            else:
                print("❌ Deployment falló")
                return False
                
        except Exception as e:
            print(f"❌ Error en deployment CLI: {e}")
            return False
            
    def _deploy_manual_instructions(self):
        """Instrucciones para deployment manual"""
        print("\n📋 INSTRUCCIONES PARA DEPLOYMENT MANUAL:")
        print("-" * 50)
        
        instructions = [
            "1. 🌐 Ve a https://railway.app y haz login",
            "2. 📦 Click 'New Project' → 'Deploy from GitHub repo'",
            "3. 🔗 Conecta este repositorio",
            "4. ⚙️  Railway detectará automáticamente el Dockerfile",
            "5. 🔧 Configura variables de entorno:",
            f"   - CHANNEL_ID={self.channel_id}",
            "   - META_ADS_BUDGET=500",
            "   - ENVIRONMENT=production", 
            "   - DUMMY_MODE=false",
            "   - PORT=8080",
            "6. 🚀 Click 'Deploy' y espera el build",
            "7. 🌍 Railway te dará una URL automáticamente",
            "",
            "💡 TIP: Railway auto-deploya en cada git push a main!"
        ]
        
        for instruction in instructions:
            print(instruction)
            
        return True
        
    def generate_env_template(self):
        """Generar template de variables de entorno"""
        print("\n📝 Generando template de variables de entorno...")
        
        env_template = f"""# Railway Environment Variables for Stakas MVP
# Canal: {self.channel_id}
# Budget: €500/month Meta Ads

# Core Configuration
ENVIRONMENT=production
DUMMY_MODE=false
CHANNEL_ID={self.channel_id}
PORT=8080
TZ=Europe/Madrid

# Meta Ads Configuration (€500/month budget)
META_ADS_BUDGET=500
META_ACCESS_TOKEN=your_meta_access_token_here
META_APP_ID=your_meta_app_id_here
META_APP_SECRET=your_meta_app_secret_here
META_ACCOUNT_ID=your_meta_account_id_here

# YouTube API (for channel analysis)
YOUTUBE_API_KEY=your_youtube_api_key_here

# Database (Railway auto-provides)
DATABASE_URL=${{DATABASE_URL}}
REDIS_URL=${{REDIS_URL}}

# Optional: Webhook URLs
DISCORD_WEBHOOK_URL=your_discord_webhook_here
SLACK_WEBHOOK_URL=your_slack_webhook_here

# Security
JWT_SECRET_KEY=your_jwt_secret_here
API_SECRET_KEY=your_api_secret_here
"""
        
        env_file = self.project_root / "railway.env.template"
        
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_template)
                
            print(f"✅ Template creado: {env_file}")
            print("💡 Configura estas variables en Railway dashboard")
            return True
            
        except Exception as e:
            print(f"❌ Error creando template: {e}")
            return False
            
    def full_deployment_pipeline(self):
        """Pipeline completo de deployment"""
        print("\n🎯 Ejecutando pipeline completo de deployment...")
        
        steps = [
            ("Verificar prerequisitos", self.check_prerequisites),
            ("Build Docker image", lambda: self.build_docker_image("latest")),
            ("Test imagen local", lambda: self.test_image_locally("latest")),
            ("Crear config Railway", self.create_railway_config),
            ("Generar env template", self.generate_env_template),
            ("Deploy a Railway", self.deploy_to_railway)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📍 {step_name}...")
            
            if not step_func():
                print(f"❌ Falló: {step_name}")
                return False
                
            print(f"✅ Completado: {step_name}")
            
        print("\n🎉 ¡DEPLOYMENT PIPELINE COMPLETADO!")
        print(f"🎵 Canal Stakas MVP ({self.channel_id}) listo para viralizar")
        print("💰 Sistema optimizado para €500/month Meta Ads budget")
        
        return True

def main():
    """Menú interactivo principal"""
    deployer = StakasRailwayDeployer()
    deployer.print_banner()
    
    while True:
        print("\n🎛️  OPCIONES DE DEPLOYMENT:")
        print("1. ✅ Verificar prerequisitos")
        print("2. 🏗️  Build Docker image")
        print("3. 🧪 Test imagen local")  
        print("4. ⚙️  Crear config Railway")
        print("5. 📝 Generar env template")
        print("6. 🚀 Deploy a Railway")
        print("7. 🎯 Pipeline completo")
        print("8. ❌ Salir")
        
        choice = input("\n👉 Selecciona opción (1-8): ").strip()
        
        if choice == "1":
            deployer.check_prerequisites()
            
        elif choice == "2":
            tag = input("Tag (default: latest): ").strip() or "latest"
            deployer.build_docker_image(tag)
            
        elif choice == "3":
            tag = input("Tag a testear (default: latest): ").strip() or "latest"
            port = input("Puerto local (default: 8080): ").strip() or "8080"
            deployer.test_image_locally(tag, int(port))
            
        elif choice == "4":
            deployer.create_railway_config()
            
        elif choice == "5":
            deployer.generate_env_template()
            
        elif choice == "6":
            deployer.deploy_to_railway()
            
        elif choice == "7":
            deployer.full_deployment_pipeline()
            
        elif choice == "8":
            print("👋 ¡Deploy completado! Stakas MVP listo para viral 🚀")
            break
            
        else:
            print("❌ Opción inválida. Usa 1-8")

if __name__ == "__main__":
    main()