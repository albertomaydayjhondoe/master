#!/usr/bin/env python3
"""
🚀 Quick Railway Test - Minimal Viral Dashboard
Test build de Railway con dependencias mínimas
"""

import subprocess
import os
from pathlib import Path

def test_streamlit_local():
    """Test local del dashboard para verificar que funciona"""
    
    print("🧪 Testeando dashboard local antes de Railway...")
    
    try:
        # Install requirements mínimos
        subprocess.run([
            'pip', 'install', 
            'streamlit==1.50.0',
            'pandas==2.3.2', 
            'numpy==2.3.2',
            'matplotlib==3.10.7',
            'seaborn==0.13.2',
            'plotly==6.3.1',
            'requests==2.32.5'
        ], check=True)
        
        print("✅ Dependencias instaladas")
        
        # Test import del script
        test_script = """
import sys
sys.path.append('scripts')

try:
    # Test imports críticos
    import streamlit as st
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import requests
    from pathlib import Path
    import json
    import datetime
    
    print("OK - Todos los imports funcionan correctamente")
    
    # Test basic functionality
    data = pd.DataFrame({'x': [1,2,3], 'y': [4,5,6]})
    fig = px.line(data, x='x', y='y')
    
    print("OK - Funcionalidad basica OK")
    print("OK - Listo para Railway deployment")
    
except ImportError as e:
    print(f"ERROR - Error de import: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR - Error general: {e}")
    sys.exit(1)
"""
        
        with open('test_railway.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        result = subprocess.run(['python', 'test_railway.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test pasado exitosamente!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Test falló: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists('test_railway.py'):
            os.remove('test_railway.py')

def create_minimal_dockerfile():
    """Crear Dockerfile ultra-mínimo para Railway"""
    
    dockerfile_content = """# 🚀 Minimal Streamlit Dashboard - Railway
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-streamlit.txt ./

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements-streamlit.txt

# Copy only necessary files
COPY scripts/viral_study_analysis.py ./scripts/
COPY data/ ./data/

# Create directories
RUN mkdir -p data logs

# Environment
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \\
    CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

# Start command
CMD streamlit run scripts/viral_study_analysis.py \\
    --server.port $PORT \\
    --server.address 0.0.0.0 \\
    --server.headless true \\
    --browser.gatherUsageStats false
"""
    
    with open('Dockerfile.minimal', 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile minimal creado")

def main():
    """Test y deployment Railway"""
    
    print("🎵" + "="*50 + "🎵")
    print("🚀 RAILWAY TEST - STAKAS MVP DASHBOARD")
    print("📺 UCgohgqLVu1QPdfa64Vkrgeg")
    print("🎵" + "="*50 + "🎵\n")
    
    # 1. Test local
    if not test_streamlit_local():
        print("❌ Test local falló. Fix antes de Railway.")
        return False
    
    # 2. Crear Dockerfile minimal
    create_minimal_dockerfile()
    
    # 3. Update railway.json para usar Dockerfile minimal
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "DOCKERFILE",
            "dockerfilePath": "Dockerfile.minimal"
        },
        "deploy": {
            "numReplicas": 1,
            "restartPolicyType": "ON_FAILURE", 
            "restartPolicyMaxRetries": 3,
            "healthcheckPath": "/_stcore/health",
            "healthcheckTimeout": 60,
            "sleepApplication": False,
            "startCommand": "streamlit run scripts/viral_study_analysis.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"
        }
    }
    
    with open('railway.json', 'w', encoding='utf-8') as f:
        json.dump(railway_config, f, indent=2, ensure_ascii=False)
    
    print("✅ railway.json actualizado para Dockerfile minimal")
    
    print("\n🚀 LISTO PARA RAILWAY:")
    print("1. git add .")
    print("2. git commit -m '🔧 Fix Railway build - minimal deps'")
    print("3. git push origin main")
    print("4. Railway auto-deploy via GitHub Actions")
    
    return True

if __name__ == "__main__":
    import json
    success = main()
    if not success:
        exit(1)