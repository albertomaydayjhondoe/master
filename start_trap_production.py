#!/usr/bin/env python3
"""
🎵 LAUNCHER PRODUCCIÓN - ARTISTA TRAP
====================================
Inicia sistema completo en modo producción para campañas trap
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def setup_production_env():
    """Configurar entorno de producción"""
    os.environ['DUMMY_MODE'] = 'false'
    os.environ['ML_PRODUCTION_MODE'] = 'true'
    os.environ['TRAP_ARTIST_MODE'] = 'true'
    print("✅ Entorno producción configurado")

def verify_ml_models():
    """Verificar que modelos ML están disponibles"""
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✅ Modelos YOLO verificados")
        return True
    except Exception as e:
        print(f"❌ Error modelos ML: {e}")
        return False

def start_services():
    """Iniciar servicios del sistema"""
    print("🚀 Iniciando servicios producción...")
    
    # ML API
    subprocess.Popen([sys.executable, "-m", "ml_core.api.main"], 
                     cwd=Path.cwd())
    time.sleep(3)
    
    # Production Controller (Gradio)
    subprocess.Popen([sys.executable, "production_controller.py"], 
                     cwd=Path.cwd())
    time.sleep(2)
    
    # Analytics Engine (Streamlit)  
    subprocess.Popen(["streamlit", "run", "analytics_engine.py", 
                      "--server.port=8501"], cwd=Path.cwd())
    time.sleep(2)
    
    print("✅ Servicios iniciados")

def verify_services():
    """Verificar que servicios están corriendo"""
    services = [
        ("ML API", "http://localhost:8000/health"),
        ("Gradio Dashboard", "http://localhost:7860"),
        ("Streamlit Analytics", "http://localhost:8501")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OPERATIVO")
            else:
                print(f"⚠️  {name}: Respuesta {response.status_code}")
        except:
            print(f"❌ {name}: NO DISPONIBLE")

if __name__ == "__main__":
    print("🎵 INICIANDO SISTEMA TRAP EN PRODUCCIÓN")
    print("=====================================")
    
    setup_production_env()
    
    if not verify_ml_models():
        print("❌ Modelos ML no disponibles. Ejecuta el script de activación primero.")
        sys.exit(1)
    
    start_services()
    time.sleep(5)
    verify_services()
    
    print("")
    print("🎯 SISTEMA TRAP PRODUCTIVO INICIADO")
    print("===================================")
    print("📊 Gradio Dashboard: http://localhost:7860")
    print("📈 Streamlit Analytics: http://localhost:8501") 
    print("🤖 ML API: http://localhost:8000")
    print("")
    print("🔥 ¡LISTO PARA CAMPAÑAS VIRALES TRAP! 🎵")
