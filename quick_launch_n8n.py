#!/usr/bin/env python3
"""
🎬 Quick Launch - n8n Stakas MVP Orchestrator
Script rápido para lanzar el sistema completo de workflows
"""

import os
import time
import webbrowser
import subprocess
from pathlib import Path

def print_banner():
    banner = """
🎵════════════════════════════════════════════════════════════🎵
║                                                            ║
║    🚀 STAKAS MVP - n8n WORKFLOW ORCHESTRATOR 🚀            ║
║                                                            ║
║    🎯 Canal: UCgohgqLVu1QPdfa64Vkrgeg                       ║
║    💰 Budget: €500/mes Meta Ads                            ║
║    🎵 Género: Drill/Rap Español                            ║
║    📈 Meta: 0→10K subscribers                              ║
║                                                            ║
🎵════════════════════════════════════════════════════════════🎵
    """
    print(banner)

def quick_launch():
    """Lanzamiento rápido del sistema completo"""
    print_banner()
    
    print("\n🔧 Iniciando n8n + PostgreSQL + Redis...")
    
    # Lanzar docker-compose
    try:
        subprocess.run([
            "docker-compose", "-f", "docker-compose.n8n.yml", "up", "-d"
        ], check=True)
        print("✅ Servicios Docker iniciados correctamente")
    except subprocess.CalledProcessError:
        print("❌ Error iniciando servicios Docker")
        return False
    except FileNotFoundError:
        print("❌ Docker Compose no encontrado. Instala Docker Desktop.")
        return False
    
    # Esperar a que n8n esté listo
    print("\n⏳ Esperando a que n8n esté disponible...")
    for i in range(15):
        try:
            import requests
            response = requests.get("http://localhost:5678/healthz", timeout=3)
            if response.status_code == 200:
                print(f"✅ n8n listo después de {i*2} segundos")
                break
        except:
            pass
        time.sleep(2)
        print(f"   Intentando... ({i+1}/15)")
    else:
        print("⚠️  n8n puede necesitar más tiempo. Continuando...")
    
    # URLs útiles
    urls = {
        "n8n Dashboard": "http://localhost:5678",
        "PostgreSQL Admin (opcional)": "http://localhost:8080",  # Si añades pgAdmin
        "Redis Commander (opcional)": "http://localhost:8081",   # Si añades Redis Commander
        "Stakas GitHub Repo": "https://github.com/albertomaydayjhondoe/master",
        "Railway Deploy": "https://railway.app"
    }
    
    print("\n🌐 URLs del Sistema:")
    for name, url in urls.items():
        print(f"   {name}: {url}")
    
    # Credenciales
    print("\n🔐 Credenciales n8n:")
    print("   Usuario: stakas_admin")
    print("   Password: StakasN8N2024!")
    
    # Información de workflows
    print("\n📋 Workflows Disponibles:")
    print("   1. 📊 Channel Monitor - Analytics cada 2h + Auto-optimización")
    print("   2. 🎬 Viral Content Generator - IA + Meta Ads €500/mes") 
    print("   3. 🚀 Launch Orchestrator - Deployment automation")
    
    # Webhooks
    print("\n🔗 Webhooks para Triggers Externos:")
    print("   Generar Contenido: http://localhost:5678/webhook/viral-content")
    print("   Launch Sistema: http://localhost:5678/webhook/stakas-launch")
    
    # Próximos pasos
    print("\n📝 Próximos Pasos:")
    print("   1. Configura credentials en n8n (YouTube, Meta, GitHub, Discord)")
    print("   2. Importa workflows desde n8n/workflows/*.json")
    print("   3. Activa workflows para automatización completa")
    print("   4. Ejecuta: python setup_n8n_stakas.py (setup automático)")
    
    # Abrir dashboard
    try:
        print("\n🌐 Abriendo n8n Dashboard...")
        webbrowser.open("http://localhost:5678")
        time.sleep(2)
        
        print("📖 Abriendo documentación...")
        webbrowser.open("https://github.com/albertomaydayjhondoe/master/blob/main/n8n/README_WORKFLOWS.md")
        
    except Exception as e:
        print(f"❌ Error abriendo browser: {e}")
        print("   Accede manualmente a: http://localhost:5678")
    
    print("\n🎉 ¡Sistema Stakas MVP lanzado exitosamente!")
    print("🎯 Listo para automatizar UCgohgqLVu1QPdfa64Vkrgeg hacia 10K subs")
    
    return True

if __name__ == "__main__":
    success = quick_launch()
    if not success:
        exit(1)