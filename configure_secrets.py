#!/usr/bin/env python3
"""
🔐 Configurador Automático de GitHub Secrets
Script para configurar secrets de Stakas MVP deployment
"""

import subprocess
import sys
import json
import base64
import requests
from getpass import getpass

class GitHubSecretsManager:
    def __init__(self):
        self.repo_owner = "albertomaydayjhondoe"
        self.repo_name = "master"
        self.secrets = {
            "DOCKERHUB_USERNAME": "agora90",
            "DOCKERHUB_TOKEN": "",
            "RAILWAY_TOKEN": "", 
            "DISCORD_WEBHOOK_URL": ""
        }
    
    def check_gh_cli(self):
        """Verificar si GitHub CLI está instalado"""
        try:
            result = subprocess.run(["gh", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub CLI detectado")
                return True
        except FileNotFoundError:
            print("❌ GitHub CLI no encontrado")
            return False
    
    def install_gh_cli(self):
        """Instalar GitHub CLI en Windows"""
        print("\n📦 Instalando GitHub CLI...")
        print("🔄 Ejecutando: winget install GitHub.cli")
        
        try:
            result = subprocess.run([
                "winget", "install", "GitHub.cli"
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print("✅ GitHub CLI instalado")
                print("⚠️  Reinicia PowerShell y ejecuta de nuevo este script")
                return True
            else:
                print("❌ Error instalando GitHub CLI")
                return False
        except FileNotFoundError:
            print("❌ winget no encontrado")
            print("📋 Instala manualmente desde: https://cli.github.com/")
            return False
    
    def gh_login_check(self):
        """Verificar login en GitHub CLI"""
        try:
            result = subprocess.run(["gh", "auth", "status"], 
                                  capture_output=True, text=True)
            if "Logged in to github.com" in result.stderr:
                print("✅ GitHub CLI autenticado")
                return True
            else:
                print("❌ GitHub CLI no autenticado")
                return False
        except:
            return False
    
    def gh_login(self):
        """Login en GitHub CLI"""
        print("\n🔐 Iniciando login en GitHub...")
        try:
            subprocess.run(["gh", "auth", "login"], check=True)
            return True
        except:
            print("❌ Error en login")
            return False
    
    def collect_secrets(self):
        """Recopilar valores de secrets"""
        print("\n🔑 CONFIGURACIÓN DE SECRETS")
        print("=" * 50)
        
        # Docker Hub Username (ya lo tenemos)
        print(f"✅ DOCKERHUB_USERNAME: {self.secrets['DOCKERHUB_USERNAME']}")
        
        # Docker Hub Token
        print("\n🐳 DOCKERHUB_TOKEN:")
        print("   1. Ve a https://hub.docker.com/")
        print("   2. Login como 'agora90'")
        print("   3. Account Settings > Security > New Access Token")
        print("   4. Name: 'GitHub Actions Stakas MVP'")
        print("   5. Permissions: Read, Write, Delete")
        
        dockerhub_token = getpass("   Pega tu Docker Hub token: ").strip()
        if dockerhub_token:
            self.secrets["DOCKERHUB_TOKEN"] = dockerhub_token
            print("   ✅ Token configurado")
        
        # Railway Token
        print("\n🚂 RAILWAY_TOKEN:")
        print("   1. Ve a https://railway.app")
        print("   2. Login con GitHub")
        print("   3. Account Settings > Tokens > Create Token")
        print("   4. Name: 'GitHub Actions Deploy'")
        
        railway_token = getpass("   Pega tu Railway token: ").strip()
        if railway_token:
            self.secrets["RAILWAY_TOKEN"] = railway_token
            print("   ✅ Token configurado")
        
        # Discord Webhook (opcional)
        print("\n🤖 DISCORD_WEBHOOK_URL (opcional):")
        discord_webhook = input("   Pega Discord webhook URL (Enter para saltar): ").strip()
        if discord_webhook:
            self.secrets["DISCORD_WEBHOOK_URL"] = discord_webhook
            print("   ✅ Webhook configurado")
        else:
            print("   ⏩ Saltado (opcional)")
    
    def set_secrets_gh_cli(self):
        """Configurar secrets usando GitHub CLI"""
        print("\n🚀 Configurando secrets en GitHub...")
        
        success_count = 0
        total_secrets = len([v for v in self.secrets.values() if v])
        
        for secret_name, secret_value in self.secrets.items():
            if not secret_value:
                continue
                
            print(f"\n📝 Configurando {secret_name}...")
            
            cmd = [
                "gh", "secret", "set", secret_name,
                "--repo", f"{self.repo_owner}/{self.repo_name}",
                "--body", secret_value
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"   ✅ {secret_name} configurado")
                    success_count += 1
                else:
                    print(f"   ❌ Error configurando {secret_name}: {result.stderr}")
                    
            except Exception as e:
                print(f"   ❌ Exception configurando {secret_name}: {e}")
        
        print(f"\n📊 Resultado: {success_count}/{total_secrets} secrets configurados")
        return success_count == total_secrets
    
    def verify_secrets(self):
        """Verificar que los secrets están configurados"""
        print("\n🔍 Verificando secrets configurados...")
        
        cmd = [
            "gh", "secret", "list",
            "--repo", f"{self.repo_owner}/{self.repo_name}"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Secrets configurados en el repositorio:")
                print(result.stdout)
                return True
            else:
                print(f"❌ Error verificando secrets: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Exception verificando secrets: {e}")
            return False
    
    def trigger_workflow(self):
        """Trigger manual del workflow"""
        print("\n🚀 Triggering GitHub Actions workflow...")
        
        cmd = [
            "gh", "workflow", "run", "deploy-railway.yml",
            "--repo", f"{self.repo_owner}/{self.repo_name}",
            "--field", "deploy_to_railway=true"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Workflow triggered!")
                print("📊 Monitorea el progreso en:")
                print(f"   https://github.com/{self.repo_owner}/{self.repo_name}/actions")
                return True
            else:
                print(f"❌ Error triggering workflow: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Exception triggering workflow: {e}")
            return False
    
    def manual_instructions(self):
        """Instrucciones manuales si GitHub CLI falla"""
        print("\n📋 INSTRUCCIONES MANUALES:")
        print("=" * 50)
        
        print("Ve a esta URL:")
        print(f"https://github.com/{self.repo_owner}/{self.repo_name}/settings/secrets/actions")
        
        print("\nConfigura estos secrets:")
        for secret_name, secret_value in self.secrets.items():
            if secret_value:
                print(f"\n🔑 {secret_name}:")
                print(f"   Value: {secret_value[:10]}{'...' if len(secret_value) > 10 else ''}")
        
        print(f"\n🚀 Luego trigger el workflow:")
        print(f"https://github.com/{self.repo_owner}/{self.repo_name}/actions")

def main():
    """Función principal"""
    manager = GitHubSecretsManager()
    
    print("🔐 GITHUB SECRETS AUTO-CONFIGURATOR")
    print("📺 Repo: albertomaydayjhondoe/master")
    print("🎵 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    print("=" * 60)
    
    # Verificar GitHub CLI
    if not manager.check_gh_cli():
        install_choice = input("\n📦 ¿Instalar GitHub CLI automáticamente? (y/N): ")
        if install_choice.lower() == 'y':
            if manager.install_gh_cli():
                print("⚠️  Reinicia PowerShell y ejecuta de nuevo este script")
                return
        else:
            print("📋 Usa las instrucciones manuales al final")
    
    # Verificar login
    if manager.check_gh_cli() and not manager.gh_login_check():
        login_choice = input("\n🔐 ¿Hacer login en GitHub CLI? (y/N): ")
        if login_choice.lower() == 'y':
            if not manager.gh_login():
                print("❌ Login falló, usando método manual")
    
    # Recopilar secrets
    manager.collect_secrets()
    
    # Configurar secrets
    if manager.check_gh_cli() and manager.gh_login_check():
        print("\n🎯 Usando GitHub CLI para configurar secrets...")
        
        if manager.set_secrets_gh_cli():
            manager.verify_secrets()
            
            # Trigger workflow
            trigger_choice = input("\n🚀 ¿Trigger deployment ahora? (y/N): ")
            if trigger_choice.lower() == 'y':
                manager.trigger_workflow()
        else:
            print("❌ Error configurando secrets via CLI")
            manager.manual_instructions()
    else:
        print("⚠️  GitHub CLI no disponible, usando método manual")
        manager.manual_instructions()
    
    print("\n🎉 ¡Configuración completada!")
    print("🎵 Stakas MVP listo para deployment automático")
    print("📊 Monitorea el progreso en GitHub Actions")

if __name__ == "__main__":
    main()