#!/usr/bin/env python3
"""
🔐 GitHub Secrets Configuration Guide para Stakas MVP
Guía interactiva para configurar secrets necesarios para deployment
"""

import webbrowser
import pyperclip
from datetime import datetime

def print_banner():
    print("=" * 70)
    print("🔐 GITHUB SECRETS SETUP - STAKAS MVP")
    print("📺 Repository: albertomaydayjhondoe/master")
    print("🎵 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    print("=" * 70)

def open_github_secrets():
    """Abrir página de secrets en GitHub"""
    url = "https://github.com/albertomaydayjhondoe/master/settings/secrets/actions"
    print(f"\n🌐 Abriendo GitHub Secrets: {url}")
    try:
        webbrowser.open(url)
        return True
    except:
        print("❌ No se pudo abrir automáticamente")
        print(f"📋 Copia esta URL manualmente: {url}")
        return False

def dockerhub_setup():
    """Configurar Docker Hub secrets"""
    print("\n🐳 DOCKER HUB SETUP")
    print("-" * 40)
    
    print("\n1️⃣ Crear cuenta Docker Hub (si no tienes):")
    print("   🌐 https://hub.docker.com/signup")
    
    print("\n2️⃣ Generar Access Token:")
    print("   • Login a Docker Hub")
    print("   • Ve a Account Settings > Security")
    print("   • Click 'New Access Token'")
    print("   • Name: 'GitHub Actions Stakas MVP'")
    print("   • Permissions: Read, Write, Delete")
    print("   • Copy el token generado")
    
    # Sugerir username
    suggested_username = input("\n📝 ¿Cuál es tu username de Docker Hub? (ej: stakasmvp): ").strip()
    if not suggested_username:
        suggested_username = "stakasmvp"
    
    print(f"\n📋 SECRETS A CONFIGURAR EN GITHUB:")
    print(f"   DOCKERHUB_USERNAME = {suggested_username}")
    print(f"   DOCKERHUB_TOKEN = [el token que generaste]")
    
    # Copiar al clipboard
    try:
        pyperclip.copy(suggested_username)
        print(f"\n✅ '{suggested_username}' copiado al clipboard")
    except:
        pass
    
    return suggested_username

def railway_setup():
    """Configurar Railway secrets"""
    print("\n🚂 RAILWAY SETUP") 
    print("-" * 40)
    
    print("\n1️⃣ Crear cuenta Railway (si no tienes):")
    print("   🌐 https://railway.app")
    print("   📝 Usar GitHub para login (recomendado)")
    
    print("\n2️⃣ Obtener Railway Token:")
    print("   • Login a Railway")
    print("   • Ve a Account Settings")
    print("   • Scroll down a 'Tokens'") 
    print("   • Click 'Create Token'")
    print("   • Name: 'GitHub Actions Deploy'")
    print("   • Copy el token")
    
    print("\n3️⃣ Crear proyecto Railway:")
    print("   • Dashboard Railway > 'New Project'")
    print("   • 'Deploy from GitHub repo'")
    print("   • Seleccionar 'albertomaydayjhondoe/master'")
    print("   • Railway detectará automáticamente Dockerfile")
    
    print(f"\n📋 SECRET A CONFIGURAR EN GITHUB:")
    print(f"   RAILWAY_TOKEN = [el token que generaste]")
    
    return True

def discord_setup():
    """Configurar Discord webhook (opcional)"""
    print("\n🤖 DISCORD NOTIFICATIONS (Opcional)")
    print("-" * 40)
    
    print("\n1️⃣ Crear Discord Webhook:")
    print("   • Ve a tu servidor Discord")
    print("   • Server Settings > Integrations > Webhooks")
    print("   • 'New Webhook'")
    print("   • Name: 'Stakas MVP Deployments'")
    print("   • Channel: #general o #deployments")
    print("   • Copy Webhook URL")
    
    print(f"\n📋 SECRET OPCIONAL EN GITHUB:")
    print(f"   DISCORD_WEBHOOK_URL = [la URL del webhook]")
    
    return True

def github_secrets_instructions():
    """Instrucciones paso a paso para GitHub"""
    print("\n⚙️  CÓMO CONFIGURAR SECRETS EN GITHUB")
    print("-" * 50)
    
    steps = [
        "1. Ve a: https://github.com/albertomaydayjhondoe/master",
        "2. Click en 'Settings' (tab superior)",
        "3. En sidebar izquierdo: 'Secrets and variables' > 'Actions'",
        "4. Click 'New repository secret'",
        "5. Para cada secret:",
        "   • Name: DOCKERHUB_USERNAME",
        "   • Value: tu_username_dockerhub", 
        "   • Click 'Add secret'",
        "6. Repetir para:",
        "   • DOCKERHUB_TOKEN",
        "   • RAILWAY_TOKEN", 
        "   • DISCORD_WEBHOOK_URL (opcional)"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    return True

def verify_setup():
    """Verificar que todo esté configurado"""
    print("\n✅ VERIFICACIÓN FINAL")
    print("-" * 30)
    
    checklist = [
        "🐳 Docker Hub account creada",
        "🔑 Docker Hub access token generado",
        "🚂 Railway account creada",
        "🎫 Railway token generado",
        "📦 Railway project creado desde GitHub",
        "🔐 GitHub secrets configurados",
        "🤖 Discord webhook (opcional)"
    ]
    
    print("Verifica que hayas completado:")
    for item in checklist:
        completed = input(f"   {item} - ¿Completado? (y/N): ").lower().strip()
        if completed != 'y':
            print(f"   ⚠️  Pendiente: {item}")
    
    return True

def trigger_deployment():
    """Instrucciones para triggear deployment"""
    print("\n🚀 TRIGGER DEPLOYMENT")
    print("-" * 30)
    
    print("Una vez configurados todos los secrets:")
    print("\n🔄 Opción 1 - Auto trigger (ya se activó con el push):")
    print("   • Ve a: https://github.com/albertomaydayjhondoe/master/actions")
    print("   • Verifica workflow 'Build & Deploy Stakas MVP to Railway'")
    
    print("\n🎯 Opción 2 - Manual trigger:")
    print("   • GitHub Actions tab")
    print("   • 'Build & Deploy Stakas MVP to Railway'") 
    print("   • 'Run workflow' > Run workflow")
    
    print("\n📊 Monitoreo:")
    print("   • GitHub Actions mostrará progreso en tiempo real")
    print("   • Build tardará ~5-10 minutos")
    print("   • Railway creará URL automáticamente")
    
    return True

def main():
    """Menú principal interactivo"""
    print_banner()
    
    while True:
        print("\n🎛️  CONFIGURACIÓN SECRETS:")
        print("1. 🌐 Abrir GitHub Secrets page")
        print("2. 🐳 Docker Hub setup")
        print("3. 🚂 Railway setup") 
        print("4. 🤖 Discord setup (opcional)")
        print("5. 📋 Instrucciones GitHub paso a paso")
        print("6. ✅ Verificar setup completo")
        print("7. 🚀 Trigger deployment")
        print("8. 📖 Ver todos los pasos juntos")
        print("9. ❌ Salir")
        
        choice = input("\n👉 Selecciona opción (1-9): ").strip()
        
        if choice == "1":
            open_github_secrets()
            
        elif choice == "2":
            dockerhub_setup()
            
        elif choice == "3":
            railway_setup()
            
        elif choice == "4":
            discord_setup()
            
        elif choice == "5":
            github_secrets_instructions()
            
        elif choice == "6":
            verify_setup()
            
        elif choice == "7":
            trigger_deployment()
            
        elif choice == "8":
            print("\n🎯 SETUP COMPLETO - TODOS LOS PASOS:")
            dockerhub_setup()
            railway_setup() 
            discord_setup()
            github_secrets_instructions()
            verify_setup()
            trigger_deployment()
            
        elif choice == "9":
            print("\n🎉 ¡Setup completado!")
            print("🚀 Una vez configurados los secrets, el deployment será automático")
            print("🎵 Stakas MVP listo para viral 24/7!")
            break
            
        else:
            print("❌ Opción inválida. Usa 1-9")

if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        print("📋 Instalando pyperclip para clipboard...")
        import subprocess
        subprocess.run(["pip", "install", "pyperclip"], capture_output=True)
        import pyperclip
    
    main()