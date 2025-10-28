#!/usr/bin/env python3
"""
🚀 Deployment Manual a Railway - Stakas MVP
Como Railway CLI falla, usaremos GitHub Actions para deploy automático
"""

import json
import subprocess
from pathlib import Path

def create_github_workflow_railway():
    """Crear GitHub Action para deploy automático a Railway"""
    
    workflow_content = """name: 🚀 Railway Deploy - Stakas MVP Viral Dashboard

on:
  push:
    branches: [ main ]
    paths:
      - 'scripts/viral_study_analysis.py'
      - 'railway.json'
      - 'Dockerfile'
      - 'requirements*.txt'
  workflow_dispatch:
    inputs:
      deploy_type:
        description: 'Tipo de deploy'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

env:
  RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

jobs:
  deploy-viral-dashboard:
    name: 🎬 Deploy Viral Dashboard
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout Repository
      uses: actions/checkout@v4
      
    - name: 🐍 Setup Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: 📦 Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install matplotlib seaborn plotly streamlit
        
    - name: 🧪 Test Viral Analysis
      run: |
        python scripts/viral_study_analysis.py
        echo "✅ Viral analysis test passed"
        
    - name: 🚂 Install Railway CLI
      run: |
        curl -fsSL https://railway.app/install.sh | sh
        echo "$HOME/.railway/bin" >> $GITHUB_PATH
        
    - name: 🔐 Railway Login
      run: |
        railway login --token ${{ secrets.RAILWAY_TOKEN }}
        
    - name: 🎯 Set Railway Project Context
      run: |
        railway link -p ${{ secrets.RAILWAY_PROJECT_ID }}
        
    - name: 🔧 Set Environment Variables
      run: |
        railway variables set APP_ENV=production
        railway variables set CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
        railway variables set CHANNEL_NAME="Stakas MVP"
        railway variables set GENRE=drill_rap_espanol
        railway variables set TARGET_SUBSCRIBERS=10000
        railway variables set META_ADS_BUDGET=500
        railway variables set STREAMLIT_SERVER_HEADLESS=true
        railway variables set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
        
    - name: 🚀 Deploy to Railway
      run: |
        railway up --detach
        
    - name: 📋 Get Deployment Info
      run: |
        railway status
        railway domain
        
    - name: 💬 Discord Notification
      if: success()
      uses: Ilshidur/action-discord@master
      env:
        DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK_URL }}
      with:
        args: |
          🚀 **Stakas MVP Viral Dashboard Deployed!**
          📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg
          🎬 Dashboard: Análisis de viralidad completo
          💰 Meta Ads: €500/mes optimization
          🎯 Objetivo: 0→10K subscribers
          ✅ Deploy exitoso en Railway
"""
    
    # Crear directorio .github/workflows si no existe
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    # Escribir workflow
    workflow_path = workflow_dir / "deploy-railway-viral.yml"
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(workflow_content)
    
    print(f"✅ GitHub Workflow creado: {workflow_path}")

def create_railway_dockerfile():
    """Crear Dockerfile optimizado para Railway"""
    
    dockerfile_content = """# 🚀 Stakas MVP Viral Dashboard - Railway Production
FROM python:3.11-slim

# Metadata
LABEL app="stakas-mvp-viral-dashboard"
LABEL channel="UCgohgqLVu1QPdfa64Vkrgeg" 
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt && \\
    pip install --no-cache-dir \\
        streamlit==1.50.0 \\
        matplotlib==3.10.7 \\
        seaborn==0.13.2 \\
        plotly==6.3.1 \\
        pandas==2.3.2 \\
        numpy==2.3.2

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data logs cache uploads

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Expose port (Railway will set PORT env var)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \\
    CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

# Start Streamlit dashboard
CMD streamlit run scripts/viral_study_analysis.py \\
    --server.port $PORT \\
    --server.address 0.0.0.0 \\
    --server.headless true \\
    --server.enableCORS false \\
    --server.enableXsrfProtection false \\
    --browser.gatherUsageStats false
"""
    
    with open("Dockerfile", 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile optimizado para Railway creado")

def create_railway_readme():
    """Crear README específico para Railway deployment"""
    
    readme_content = """# 🚀 Stakas MVP - Railway Deployment

## 🎯 Canal Target: UCgohgqLVu1QPdfa64Vkrgeg

Dashboard interactivo de análisis de viralidad para el canal **Stakas MVP** especializado en **Drill/Rap Español**.

### 📊 Features del Dashboard

- **🎵 Análisis de Viralidad**: Predicciones ML para contenido drill español
- **💰 Optimización Meta Ads**: Estrategia €500/mes ES+LATAM
- **📈 Proyecciones Crecimiento**: 0→10K subscribers en 12 meses
- **🎬 Calendario Contenido**: Planning viral automatizado
- **🏆 Análisis Competitivo**: Benchmarks sector drill español

### 🚀 Deploy a Railway

#### Método 1: GitHub Actions (Recomendado)

1. **Setup Secrets en GitHub**:
   ```
   RAILWAY_TOKEN=your_railway_token
   RAILWAY_PROJECT_ID=your_project_id
   DISCORD_WEBHOOK_URL=your_discord_webhook
   ```

2. **Push a main branch**:
   ```bash
   git add .
   git commit -m "🚀 Deploy viral dashboard"
   git push origin main
   ```

3. **Auto-deploy**: GitHub Actions se ejecuta automáticamente

#### Método 2: Manual Railway CLI

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Create/link project  
railway init stakas-mvp-viral

# Set environment variables
railway variables set APP_ENV=production
railway variables set CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
railway variables set STREAMLIT_SERVER_HEADLESS=true

# Deploy
railway up
```

### 🔧 Environment Variables

```env
# Core App
APP_ENV=production
CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
CHANNEL_NAME=Stakas MVP
GENRE=drill_rap_espanol
TARGET_SUBSCRIBERS=10000
META_ADS_BUDGET=500

# Streamlit Config
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 📱 Dashboard Sections

1. **📈 Growth Projections**: Comparativa orgánico vs Meta Ads vs ML optimizado
2. **💰 Meta Ads Strategy**: Distribución €500 España/LATAM/Lookalike  
3. **🎬 Viral Content Analysis**: Tipos de contenido con mayor potencial
4. **📅 Content Calendar**: Planning próximos 7 días optimizado
5. **🎯 Recommendations**: Acciones inmediatas y goals mensuales

### 🎵 Especialización Drill Español

- **Keywords Viral**: drill español, barrio life, trap madrid, freestyle real
- **Horarios Peak**: 19:00-22:00 weekdays, 15:00-21:30 weekends
- **Targeting**: España + LATAM 16-28 años + intereses Hip Hop/Urban
- **Collaborations**: 96% viral score (máximo impacto)

### 📊 KPIs Objetivo

- **Subscriber Growth**: >8% mensual
- **Video Views**: >15K promedio por video
- **Engagement Rate**: >6%
- **Meta Ads ROAS**: >3:1
- **Cost per Subscriber**: <€1.50

---

**🎯 Objetivo Final**: Crecimiento de 0 a 10.000 subscribers en 12 meses con €500/mes Meta Ads optimizados por ML para contenido drill/rap español auténtico.**
"""
    
    with open("RAILWAY_README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Railway README creado")

def update_requirements():
    """Actualizar requirements.txt para Railway"""
    
    requirements_content = """# 🚀 Stakas MVP Viral Dashboard - Railway Requirements

# Core framework
streamlit==1.50.0
pandas==2.3.2
numpy==2.3.2

# Visualization
matplotlib==3.10.7
seaborn==0.13.2
plotly==6.3.1

# Web requests
requests==2.32.5

# Data handling
python-dateutil==2.9.0.post0

# Optional performance
cachetools==6.2.0
"""
    
    with open("requirements-railway.txt", 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✅ requirements-railway.txt creado")

def main():
    """Setup completo para Railway deployment"""
    
    print("🎵" + "="*60 + "🎵")
    print("🚀 SETUP RAILWAY DEPLOYMENT - STAKAS MVP")
    print("📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
    print("🎬 Dashboard de Viralidad + ML Analytics")
    print("🎵" + "="*60 + "🎵\n")
    
    # Crear todos los archivos necesarios
    print("📝 Creando archivos para Railway deployment...")
    
    create_github_workflow_railway()
    create_railway_dockerfile()  
    create_railway_readme()
    update_requirements()
    
    print("\n✅ Setup Railway completado!")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. 🔑 Configura secrets en GitHub:")
    print("   - RAILWAY_TOKEN (from railway.app)")
    print("   - RAILWAY_PROJECT_ID (from Railway project)")
    print("   - DISCORD_WEBHOOK_URL (optional)")
    
    print("\n2. 🚀 Deploy options:")
    print("   a) Push to main → Auto-deploy via GitHub Actions")
    print("   b) Manual: railway login && railway up")
    
    print("\n3. 📊 Accede al dashboard en la URL que Railway te proporcione")
    
    print("\n🎯 El dashboard mostrará:")
    print("   - Proyecciones 0→10K subscribers")
    print("   - Optimización Meta Ads €500/mes")
    print("   - Análisis contenido viral drill español")
    print("   - Calendar de posting optimizado")
    
    # Commit changes
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        print("\n✅ Archivos añadidos a git. ¡Listo para push y auto-deploy!")
    except:
        print("\n⚠️  Recuerda hacer git add . && git commit && git push")

if __name__ == "__main__":
    main()