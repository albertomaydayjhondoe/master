#!/usr/bin/env python3
"""
🚀 Quick Setup - Abrir URLs para configuración de secrets
"""

import webbrowser
import time

def open_urls():
    """Abrir todas las URLs necesarias para configurar secrets"""
    
    urls = [
        {
            "name": "🔐 GitHub Secrets (CONFIGURAR AQUÍ)",
            "url": "https://github.com/albertomaydayjhondoe/master/settings/secrets/actions",
            "action": "Configurar secrets: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, RAILWAY_TOKEN"
        },
        {
            "name": "🐳 Docker Hub (OBTENER TOKEN)",
            "url": "https://hub.docker.com/settings/security",
            "action": "Login como 'agora90' → New Access Token → Name: 'GitHub Actions Stakas MVP'"
        },
        {
            "name": "🚂 Railway (OBTENER TOKEN)", 
            "url": "https://railway.app/account",
            "action": "Login with GitHub → Tokens → Create Token → Name: 'GitHub Actions Deploy'"
        },
        {
            "name": "📊 GitHub Actions (MONITOREAR)",
            "url": "https://github.com/albertomaydayjhondoe/master/actions", 
            "action": "Ver progreso del deployment cuando esté configurado"
        }
    ]
    
    print("🚀 STAKAS MVP - QUICK SETUP")
    print("📺 Repository: albertomaydayjhondoe/master")
    print("🎵 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    print("=" * 60)
    
    for i, url_info in enumerate(urls, 1):
        print(f"\n{i}. {url_info['name']}")
        print(f"   URL: {url_info['url']}")
        print(f"   📋 {url_info['action']}")
        
        choice = input(f"   ¿Abrir ahora? (y/N): ").lower().strip()
        if choice == 'y':
            try:
                webbrowser.open(url_info['url'])
                print(f"   ✅ Abierto en navegador")
                if i < len(urls):
                    time.sleep(2)  # Pausa entre aperturas
            except:
                print(f"   ❌ Error abriendo URL")
        else:
            print(f"   ⏩ Saltado")
    
    print(f"\n📋 SECRETS A CONFIGURAR EN GITHUB:")
    print(f"   DOCKERHUB_USERNAME = agora90")
    print(f"   DOCKERHUB_TOKEN = [token de Docker Hub]")
    print(f"   RAILWAY_TOKEN = [token de Railway]")
    print(f"   DISCORD_WEBHOOK_URL = [opcional]")
    
    print(f"\n🎯 Una vez configurados los secrets:")
    print(f"   • GitHub Actions se ejecutará automáticamente")
    print(f"   • Docker image: agora90/stakas-mvp:latest")
    print(f"   • Railway desplegará automáticamente")
    print(f"   • Monitorea en GitHub Actions")
    
    print(f"\n🎉 ¡Stakas MVP listo para viral 24/7!")

if __name__ == "__main__":
    open_urls()