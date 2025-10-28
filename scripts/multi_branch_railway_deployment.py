#!/usr/bin/env python3
"""
🚀 Multi-Branch Railway Deployment - albertomaydayjhondoe/master
Deploy completo del repositorio con todas sus ramas especializadas
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class MultiRailwayDeployer:
    """Deployer completo multi-rama para Railway"""
    
    def __init__(self):
        self.repo = "albertomaydayjhondoe/master"
        self.branches = []
        self.deployments = {}
        
    def get_all_branches(self) -> List[str]:
        """Obtener todas las ramas del repositorio"""
        
        print("📋 Analizando estructura de ramas...")
        
        try:
            # Get local branches
            result = subprocess.run(['git', 'branch'], 
                                  capture_output=True, text=True)
            local_branches = [branch.strip().replace('* ', '') 
                            for branch in result.stdout.split('\n') 
                            if branch.strip() and not branch.startswith('remotes/')]
            
            # Get remote branches
            result = subprocess.run(['git', 'branch', '-r'], 
                                  capture_output=True, text=True)
            remote_branches = [branch.strip().replace('origin/', '') 
                             for branch in result.stdout.split('\n') 
                             if branch.strip() and 'origin/' in branch 
                             and 'HEAD' not in branch]
            
            # Combine and deduplicate
            all_branches = list(set(local_branches + remote_branches))
            
            # Filter important branches
            important_branches = [
                'main',           # Principal
                'Meta',           # Meta Ads specialization  
                'completo',       # Sistema completo
                'device-farm-v5-integration',  # Device Farm
                'micro-services', # Microservicios
                'production/stable', # Producción estable
                'feature/ml-optimization', # ML optimization
                'feature/meta-cbo-campaigns', # Meta CBO
                'operational/meta-youtube'  # Operations
            ]
            
            # Select branches that exist
            selected_branches = [branch for branch in important_branches 
                               if branch in all_branches]
            
            print(f"✅ Ramas encontradas: {len(all_branches)}")
            print(f"🎯 Ramas para deploy: {len(selected_branches)}")
            
            for branch in selected_branches:
                print(f"  • {branch}")
            
            self.branches = selected_branches
            return selected_branches
            
        except Exception as e:
            print(f"❌ Error obteniendo ramas: {e}")
            return ['main']  # Fallback to main only
    
    def create_branch_specific_config(self, branch: str) -> Dict[str, Any]:
        """Crear configuración específica por rama"""
        
        base_config = {
            "$schema": "https://railway.app/railway.schema.json",
            "build": {
                "builder": "DOCKERFILE",
                "dockerfilePath": "Dockerfile.minimal"
            },
            "deploy": {
                "numReplicas": 1,
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 3,
                "healthcheckTimeout": 60,
                "sleepApplication": False
            }
        }
        
        # Configuraciones específicas por rama
        branch_configs = {
            'main': {
                "service_name": "stakas-mvp-main",
                "description": "Dashboard principal de viralidad",
                "start_command": "streamlit run scripts/viral_study_analysis.py --server.port $PORT --server.address 0.0.0.0 --server.headless true",
                "health_path": "/_stcore/health",
                "env_vars": {
                    "APP_ENV": "production",
                    "BRANCH": "main",
                    "SERVICE_TYPE": "dashboard"
                }
            },
            'Meta': {
                "service_name": "stakas-mvp-meta",
                "description": "Meta Ads optimization system", 
                "start_command": "python -m uvicorn ml_core.api.main:app --host 0.0.0.0 --port $PORT",
                "health_path": "/health",
                "env_vars": {
                    "APP_ENV": "production",
                    "BRANCH": "meta",
                    "SERVICE_TYPE": "meta_ads_api"
                }
            },
            'completo': {
                "service_name": "stakas-mvp-completo",
                "description": "Sistema completo integrado",
                "start_command": "python -m uvicorn ml_core.api.main:app --host 0.0.0.0 --port $PORT",
                "health_path": "/health", 
                "env_vars": {
                    "APP_ENV": "production",
                    "BRANCH": "completo",
                    "SERVICE_TYPE": "full_system"
                }
            },
            'device-farm-v5-integration': {
                "service_name": "stakas-mvp-devicefarm",
                "description": "Device Farm automation system",
                "start_command": "python device_farm/controllers/device_manager.py",
                "health_path": "/health",
                "env_vars": {
                    "APP_ENV": "production", 
                    "BRANCH": "device-farm",
                    "SERVICE_TYPE": "device_automation"
                }
            },
            'micro-services': {
                "service_name": "stakas-mvp-microservices",
                "description": "Microservices architecture",
                "start_command": "python -m uvicorn ml_core.api.main:app --host 0.0.0.0 --port $PORT",
                "health_path": "/health",
                "env_vars": {
                    "APP_ENV": "production",
                    "BRANCH": "microservices", 
                    "SERVICE_TYPE": "microservices"
                }
            }
        }
        
        # Get branch specific config or use default
        branch_config = branch_configs.get(branch, branch_configs['main'])
        
        # Update base config
        base_config["deploy"]["startCommand"] = branch_config["start_command"]
        base_config["deploy"]["healthcheckPath"] = branch_config["health_path"]
        
        return {
            "config": base_config,
            "metadata": branch_config
        }
    
    def create_dockerfile_for_branch(self, branch: str):
        """Crear Dockerfile específico para cada rama"""
        
        # Dockerfile base para todas las ramas
        if branch == 'main':
            # Dashboard Streamlit
            dockerfile_content = """# Stakas MVP Dashboard - Main Branch
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

COPY requirements-streamlit.txt ./
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements-streamlit.txt

COPY scripts/viral_study_analysis.py ./scripts/
COPY data/ ./data/
RUN mkdir -p data logs

ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV BRANCH=main

EXPOSE $PORT

HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \\
    CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

CMD streamlit run scripts/viral_study_analysis.py \\
    --server.port $PORT \\
    --server.address 0.0.0.0 \\
    --server.headless true
"""
        
        elif branch in ['Meta', 'completo', 'micro-services']:
            # FastAPI ML System
            dockerfile_content = f"""# Stakas MVP ML System - {branch} Branch
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir fastapi uvicorn python-dotenv pydantic

COPY ml_core/ ./ml_core/
COPY config/ ./config/
RUN mkdir -p data logs

ENV PYTHONUNBUFFERED=1
ENV DUMMY_MODE=true
ENV BRANCH={branch}

EXPOSE $PORT

HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \\
    CMD curl -f http://localhost:$PORT/health || exit 1

CMD python -m uvicorn ml_core.api.main:app --host 0.0.0.0 --port $PORT
"""
        
        else:
            # Generic service
            dockerfile_content = f"""# Stakas MVP Service - {branch} Branch  
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

COPY requirements*.txt ./
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt || \\
    pip install --no-cache-dir fastapi uvicorn python-dotenv

COPY . .
RUN mkdir -p data logs

ENV PYTHONUNBUFFERED=1
ENV BRANCH={branch}

EXPOSE $PORT

HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \\
    CMD curl -f http://localhost:$PORT/health || exit 1

CMD python -m uvicorn ml_core.api.main:app --host 0.0.0.0 --port $PORT || \\
    python -m http.server $PORT
"""
        
        dockerfile_path = f"Dockerfile.{branch.replace('/', '-')}"
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        print(f"✅ Dockerfile creado: {dockerfile_path}")
        return dockerfile_path
    
    def create_github_workflow_multi_branch(self):
        """Crear GitHub Action para multi-branch deployment"""
        
        workflow_content = """name: 🚀 Multi-Branch Railway Deploy

on:
  push:
    branches: 
      - main
      - Meta
      - completo
      - device-farm-v5-integration
      - micro-services
      - 'production/*'
      - 'feature/*'
  workflow_dispatch:
    inputs:
      branch:
        description: 'Branch to deploy'
        required: true
        default: 'main'
        type: choice
        options:
          - main
          - Meta
          - completo
          - device-farm-v5-integration
          - micro-services

env:
  RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

jobs:
  deploy-branch:
    name: 🎯 Deploy ${{ github.ref_name }}
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout Branch
      uses: actions/checkout@v4
      with:
        ref: ${{ github.ref_name }}
        
    - name: 🐍 Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: 🚂 Install Railway CLI
      run: |
        curl -fsSL https://railway.app/install.sh | sh
        echo "$HOME/.railway/bin" >> $GITHUB_PATH
        
    - name: 🔐 Railway Login
      run: railway login --token ${{ secrets.RAILWAY_TOKEN }}
      
    - name: 📋 Determine Service Config
      id: config
      run: |
        BRANCH_NAME="${{ github.ref_name }}"
        case $BRANCH_NAME in
          "main")
            echo "service_name=stakas-mvp-main" >> $GITHUB_OUTPUT
            echo "dockerfile=Dockerfile.main" >> $GITHUB_OUTPUT
            ;;
          "Meta")
            echo "service_name=stakas-mvp-meta" >> $GITHUB_OUTPUT  
            echo "dockerfile=Dockerfile.Meta" >> $GITHUB_OUTPUT
            ;;
          "completo")
            echo "service_name=stakas-mvp-completo" >> $GITHUB_OUTPUT
            echo "dockerfile=Dockerfile.completo" >> $GITHUB_OUTPUT
            ;;
          "device-farm-v5-integration")
            echo "service_name=stakas-mvp-devicefarm" >> $GITHUB_OUTPUT
            echo "dockerfile=Dockerfile.device-farm-v5-integration" >> $GITHUB_OUTPUT
            ;;
          *)
            echo "service_name=stakas-mvp-${BRANCH_NAME//[^a-zA-Z0-9]/-}" >> $GITHUB_OUTPUT
            echo "dockerfile=Dockerfile.generic" >> $GITHUB_OUTPUT
            ;;
        esac
        
    - name: 🎯 Create/Link Railway Service
      run: |
        railway link -p ${{ secrets.RAILWAY_PROJECT_ID }} || true
        railway service create ${{ steps.config.outputs.service_name }} || true
        
    - name: 🔧 Set Branch Environment Variables
      run: |
        railway variables set BRANCH="${{ github.ref_name }}"
        railway variables set CHANNEL_ID="UCgohgqLVu1QPdfa64Vkrgeg"
        railway variables set APP_ENV="production"
        railway variables set COMMIT_SHA="${{ github.sha }}"
        
    - name: 🚀 Deploy to Railway
      run: |
        if [ -f "${{ steps.config.outputs.dockerfile }}" ]; then
          railway up --dockerfile ${{ steps.config.outputs.dockerfile }} --detach
        else
          railway up --dockerfile Dockerfile.minimal --detach
        fi
        
    - name: 📋 Get Deployment Info
      run: |
        railway status
        railway domain || echo "No domain configured"
        
    - name: 💬 Success Notification
      if: success()
      run: |
        echo "🚀 Branch ${{ github.ref_name }} deployed successfully!"
        echo "📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg"
        echo "🎯 Service: ${{ steps.config.outputs.service_name }}"
"""
        
        workflow_dir = Path(".github/workflows")
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        with open(workflow_dir / "deploy-multi-branch.yml", 'w', encoding='utf-8') as f:
            f.write(workflow_content)
        
        print("✅ Multi-branch GitHub Workflow creado")
    
    def deploy_all_branches(self):
        """Deploy todas las ramas importantes"""
        
        print("🚀" + "="*60 + "🚀")
        print("🎯 MULTI-BRANCH RAILWAY DEPLOYMENT")
        print(f"📁 Repo: {self.repo}")
        print("📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg")
        print("🚀" + "="*60 + "🚀\n")
        
        # 1. Get all branches
        branches = self.get_all_branches()
        
        # 2. Create branch-specific Dockerfiles
        print("\n🔧 Creando Dockerfiles por rama...")
        for branch in branches:
            try:
                dockerfile = self.create_dockerfile_for_branch(branch)
                print(f"  ✅ {branch} → {dockerfile}")
            except Exception as e:
                print(f"  ❌ Error con {branch}: {e}")
        
        # 3. Create GitHub workflow
        self.create_github_workflow_multi_branch()
        
        # 4. Create branch deployment summary
        self.create_deployment_summary(branches)
        
        print("\n🎯 DEPLOYMENT PLAN:")
        print("1. 📋 Dockerfiles creados para cada rama")
        print("2. 🔄 GitHub Action configurado para auto-deploy")
        print("3. 🚀 Push activará deployment automático")
        
        services = {
            'main': 'Dashboard Principal (Streamlit)',
            'Meta': 'Meta Ads API System',
            'completo': 'Sistema Completo Integrado',
            'device-farm-v5-integration': 'Device Farm Automation',
            'micro-services': 'Microservices Architecture'
        }
        
        print("\n🎬 SERVICIOS RAILWAY:")
        for branch in branches[:5]:  # Top 5
            service_desc = services.get(branch, 'Generic Service')
            print(f"  • {branch} → {service_desc}")
        
        return True
    
    def create_deployment_summary(self, branches: List[str]):
        """Crear resumen de deployment"""
        
        summary = {
            "repository": self.repo,
            "total_branches": len(branches),
            "deployed_branches": branches,
            "services": {},
            "deployment_date": "2025-10-28",
            "channel_target": "UCgohgqLVu1QPdfa64Vkrgeg"
        }
        
        for branch in branches:
            config = self.create_branch_specific_config(branch)
            summary["services"][branch] = {
                "service_name": config["metadata"].get("service_name", f"stakas-{branch}"),
                "description": config["metadata"].get("description", "Service description"),
                "dockerfile": f"Dockerfile.{branch.replace('/', '-')}",
                "health_endpoint": config["metadata"].get("health_path", "/health")
            }
        
        with open('railway-deployment-summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print("✅ Deployment summary creado: railway-deployment-summary.json")

def main():
    """Función principal"""
    
    deployer = MultiRailwayDeployer()
    
    try:
        success = deployer.deploy_all_branches()
        
        if success:
            print("\n🎉 MULTI-BRANCH DEPLOYMENT CONFIGURADO!")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. git add .")
            print("2. git commit -m '🚀 Multi-branch Railway deployment setup'")
            print("3. git push origin main")
            print("4. Configurar RAILWAY_TOKEN y RAILWAY_PROJECT_ID en GitHub Secrets")
            print("5. Push a cualquier rama activará auto-deploy")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error en deployment: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)