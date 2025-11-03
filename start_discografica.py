#!/usr/bin/env python3
"""
🎵 Discográfica ML - Ultra-Efficient Launcher

Launcher ultra-eficiente para iniciar el sistema completo de discográfica ML
- Production Controller (Gradio) - Puerto 7860
- Analytics Engine (Streamlit) - Puerto 8501  
- Verificación de servicios automatizada

Autor: Discográfica ML Ultra-Eficiente
Fecha: 2025-11-03
"""

import subprocess
import time
import requests
import sys
import os

def start_service(name, command, port, log_file):
    """Iniciar servicio en background"""
    print(f"🚀 Starting {name}...")
    
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Iniciar servicio
    with open(f"logs/{log_file}", "w") as f:
        process = subprocess.Popen(command, stdout=f, stderr=f, shell=True)
    
    # Esperar a que inicie
    for i in range(15):
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                print(f"✅ {name} started successfully on port {port}")
                return True
        except:
            pass
        time.sleep(2)
    
    print(f"⚠️ {name} may not have started properly")
    return False

def main():
    """Launcher principal"""
    print("🎵 DISCOGRÁFICA ML - ULTRA-EFFICIENT LAUNCHER")
    print("=" * 50)
    
    # Crear directorios necesarios
    for directory in ["data", "logs", "config"]:
        os.makedirs(directory, exist_ok=True)
    
    # Servicios a iniciar
    services = [
        {
            "name": "Production Controller (Gradio)",
            "command": "python3 production_controller.py",
            "port": 7860,
            "log": "gradio.log"
        },
        {
            "name": "Analytics Engine (Streamlit)", 
            "command": "streamlit run analytics_engine.py --server.port=8501 --server.address=0.0.0.0",
            "port": 8501,
            "log": "streamlit.log"
        }
    ]
    
    # Iniciar servicios
    started_services = 0
    for service in services:
        if start_service(service["name"], service["command"], service["port"], service["log"]):
            started_services += 1
    
    # Reporte final
    print("\n" + "=" * 50)
    print(f"🎯 SERVICIOS INICIADOS: {started_services}/{len(services)}")
    print("\n📊 ACCESOS DIRECTOS:")
    print("🔴 Production Controller: http://localhost:7860")
    print("📈 Analytics Engine:      http://localhost:8501")
    print("\n🎵 DISCOGRÁFICA ML LISTA PARA USAR!")
    
    if started_services == len(services):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())