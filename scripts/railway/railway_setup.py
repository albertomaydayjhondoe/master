"""
🚀 Railway Deployment Configuration - Meta Ads-Centric
Configuración optimizada para Railway con arquitectura Meta Ads-centric
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

def generate_railway_config() -> Dict[str, Any]:
    """Generar configuración completa para Railway deployment"""
    
    return {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "DOCKER",
            "dockerfilePath": "docker/Dockerfile.railway"
        },
        "deploy": {
            "numReplicas": 1,
            "restartPolicyType": "ON_FAILURE",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 30,
            "sleepApplication": False
        },
        "environments": {
            "production": {
                "variables": {
                    # Core Configuration
                    "ENVIRONMENT": "production",
                    "DEBUG": "false",
                    "DUMMY_MODE": "false",
                    
                    # Database
                    "DATABASE_URL": "${{DATABASE_URL}}",
                    
                    # Meta Ads API  
                    "META_ACCESS_TOKEN": "${{META_ACCESS_TOKEN}}",
                    "META_APP_ID": "${{META_APP_ID}}",
                    "META_APP_SECRET": "${{META_APP_SECRET}}",
                    "META_ACCOUNT_ID": "${{META_ACCOUNT_ID}}",
                    "META_PIXEL_ID": "${{META_PIXEL_ID}}",
                    
                    # YouTube API
                    "YOUTUBE_API_KEY": "${{YOUTUBE_API_KEY}}",
                    "YOUTUBE_CLIENT_ID": "${{YOUTUBE_CLIENT_ID}}",
                    "YOUTUBE_CLIENT_SECRET": "${{YOUTUBE_CLIENT_SECRET}}",
                    
                    # TikTok API  
                    "TIKTOK_CLIENT_KEY": "${{TIKTOK_CLIENT_KEY}}",
                    "TIKTOK_CLIENT_SECRET": "${{TIKTOK_CLIENT_SECRET}}",
                    "TIKTOK_ACCESS_TOKEN": "${{TIKTOK_ACCESS_TOKEN}}",
                    
                    # Instagram API
                    "INSTAGRAM_ACCESS_TOKEN": "${{INSTAGRAM_ACCESS_TOKEN}}",
                    "INSTAGRAM_BUSINESS_ACCOUNT_ID": "${{INSTAGRAM_BUSINESS_ACCOUNT_ID}}",
                    
                    # Twitter API
                    "TWITTER_API_KEY": "${{TWITTER_API_KEY}}",
                    "TWITTER_API_SECRET": "${{TWITTER_API_SECRET}}",
                    "TWITTER_ACCESS_TOKEN": "${{TWITTER_ACCESS_TOKEN}}",
                    "TWITTER_ACCESS_TOKEN_SECRET": "${{TWITTER_ACCESS_TOKEN_SECRET}}",
                    
                    # OpenAI for ML
                    "OPENAI_API_KEY": "${{OPENAI_API_KEY}}",
                    
                    # Service URLs (Railway internal)
                    "ML_CORE_URL": "http://ml-core:8000",
                    "META_ADS_URL": "http://meta-ads-manager:9000", 
                    "YOUTUBE_UPLOADER_URL": "http://youtube-uploader:8001",
                    "UNIFIED_ORCHESTRATOR_URL": "http://unified-orchestrator:10000",
                    
                    # Webhook Configuration
                    "META_WEBHOOK_VERIFY_TOKEN": "${{META_WEBHOOK_VERIFY_TOKEN}}",
                    "WEBHOOK_BASE_URL": "${{RAILWAY_STATIC_URL}}",
                    
                    # Redis for caching
                    "REDIS_URL": "${{REDIS_URL}}",
                    
                    # Security
                    "JWT_SECRET_KEY": "${{JWT_SECRET_KEY}}",
                    "API_SECRET_KEY": "${{API_SECRET_KEY}}"
                }
            },
            "development": {
                "variables": {
                    # Core Configuration
                    "ENVIRONMENT": "development",
                    "DEBUG": "true", 
                    "DUMMY_MODE": "true",
                    
                    # Local URLs for development
                    "ML_CORE_URL": "http://localhost:8000",
                    "META_ADS_URL": "http://localhost:9000",
                    "YOUTUBE_UPLOADER_URL": "http://localhost:8001",
                    "UNIFIED_ORCHESTRATOR_URL": "http://localhost:10000",
                    
                    # Development database
                    "DATABASE_URL": "sqlite:///./dev_database.db"
                }
            }
        }
    }

def generate_procfile() -> str:
    """Generar Procfile para Railway"""
    
    return """# Meta Ads-Centric Railway Procfile
web: python -m uvicorn v2.meta_ads.meta_centric_orchestrator:app --host 0.0.0.0 --port $PORT
ml-core: python -m uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000
meta-ads: python -m uvicorn v2.meta_ads.meta_ads_manager:app --host 0.0.0.0 --port 9000  
youtube: python -m uvicorn v2.youtube.youtube_uploader:app --host 0.0.0.0 --port 8001
orchestrator: python -m uvicorn v2.unified_orchestrator.main:app --host 0.0.0.0 --port 10000
dashboard: streamlit run dashboard_meta_centric.py --server.port 8501
worker: python -m v2.workers.campaign_worker
"""

def generate_dockerfile_railway() -> str:
    """Generar Dockerfile optimizado para Railway"""
    
    return """# Meta Ads-Centric Railway Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    software-properties-common \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dummy.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/models/production
RUN mkdir -p /app/logs
RUN mkdir -p /app/temp

# Set environment variables
ENV PYTHONPATH=/app
ENV DUMMY_MODE=true
ENV ENVIRONMENT=production

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port
EXPOSE $PORT

# Default command (can be overridden by Procfile)
CMD python -m uvicorn v2.meta_ads.meta_centric_orchestrator:app --host 0.0.0.0 --port $PORT
"""

def generate_railway_deployment_script() -> str:
    """Generar script de deployment para Railway"""
    
    return """#!
# Railway Meta Ads-Centric Deployment Script

set -e

echo "Starting Meta Ads-Centric Railway deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "Checking Railway authentication..."
railway login

# Create new project if it doesn't exist
echo "Setting up Railway project..."
railway project new meta-ads-centric --template blank

# Link to project
railway link

# Set environment variables
echo "Setting environment variables..."

# Core variables (you need to provide these)
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set DUMMY_MODE=false

# Database
echo "Setting up database..."
railway add --database postgresql
railway variables set DATABASE_URL='${{DATABASE_URL}}'

# Redis for caching  
echo "Setting up Redis..."
railway add --database redis
railway variables set REDIS_URL='${{REDIS_URL}}'

# Meta Ads (REQUIRED - you need to set these)
echo "Meta Ads configuration (REQUIRED)..."
echo "Please set these manually in Railway dashboard:"
echo "- META_ACCESS_TOKEN"
echo "- META_APP_ID" 
echo "- META_APP_SECRET"
echo "- META_ACCOUNT_ID"
echo "- META_PIXEL_ID"

# YouTube (REQUIRED)
echo "YouTube configuration (REQUIRED)..."
echo "Please set these manually in Railway dashboard:"
echo "- YOUTUBE_API_KEY"
echo "- YOUTUBE_CLIENT_ID"
echo "- YOUTUBE_CLIENT_SECRET"

# TikTok (OPTIONAL)
echo "TikTok configuration (OPTIONAL)..."
echo "Set these if you have TikTok API access:"
echo "- TIKTOK_CLIENT_KEY"
echo "- TIKTOK_CLIENT_SECRET" 
echo "- TIKTOK_ACCESS_TOKEN"

# Instagram (OPTIONAL)
echo "Instagram configuration (OPTIONAL)..."
echo "Set these if you have Instagram API access:"
echo "- INSTAGRAM_ACCESS_TOKEN"
echo "- INSTAGRAM_BUSINESS_ACCOUNT_ID"

# Twitter (OPTIONAL) 
echo "Twitter configuration (OPTIONAL)..."
echo "Set these if you have Twitter API access:"
echo "- TWITTER_API_KEY"
echo "- TWITTER_API_SECRET"
echo "- TWITTER_ACCESS_TOKEN" 
echo "- TWITTER_ACCESS_TOKEN_SECRET"

# OpenAI (RECOMMENDED)
echo "OpenAI configuration (RECOMMENDED)..."
echo "Set this for enhanced ML capabilities:"
echo "- OPENAI_API_KEY"

# Security
railway variables set JWT_SECRET_KEY=$(openssl rand -base64 32)
railway variables set API_SECRET_KEY=$(openssl rand -base64 32)
railway variables set META_WEBHOOK_VERIFY_TOKEN=$(openssl rand -base64 16)

# Service URLs (automatic)
railway variables set ML_CORE_URL=http://ml-core:8000
railway variables set META_ADS_URL=http://meta-ads-manager:9000
railway variables set YOUTUBE_UPLOADER_URL=http://youtube-uploader:8001
railway variables set UNIFIED_ORCHESTRATOR_URL=http://unified-orchestrator:10000
railway variables set WEBHOOK_BASE_URL='${{RAILWAY_STATIC_URL}}'

# Deploy
echo "Deploying to Railway..."
railway up

echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Set your API keys in Railway dashboard"
echo "2. Configure Meta Ads webhooks to point to your Railway URL"
echo "3. Test with a sample campaign"
echo ""
echo "Railway URL: $(railway status --json | jq -r '.deployments[0].url')"
echo ""
echo "Your Meta Ads-Centric system is ready!"
"""

def generate_environment_setup() -> str:
    """Generar script para configurar variables de entorno"""
    
    return """#!/usr/bin/env python3
\"\"\"
Railway Environment Variables Setup
Script para configurar todas las variables de entorno necesarias
\"\"\"

import os
import subprocess
import json
from typing import Dict, List

def set_railway_variable(key: str, value: str, service: str = None):
    \"\"\"Set a Railway environment variable\"\"\"
    
    cmd = ["railway", "variables", "set", f"{key}={value}"]
    if service:
        cmd.extend(["--service", service])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Set {key}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set {key}: {e.stderr}")

def setup_core_variables():
    \"\"\"Setup core system variables\"\"\"
    
    print("Setting up core variables...")
    
    variables = {
        "ENVIRONMENT": "production",
        "DEBUG": "false", 
        "DUMMY_MODE": "false",
        "PYTHONPATH": "/app"
    }
    
    for key, value in variables.items():
        set_railway_variable(key, value)

def setup_service_urls():
    \"\"\"Setup internal service URLs\"\"\"
    
    print("Setting up service URLs...")
    
    urls = {
        "ML_CORE_URL": "http://ml-core:8000",
        "META_ADS_URL": "http://meta-ads-manager:9000",
        "YOUTUBE_UPLOADER_URL": "http://youtube-uploader:8001", 
        "UNIFIED_ORCHESTRATOR_URL": "http://unified-orchestrator:10000",
        "WEBHOOK_BASE_URL": "${RAILWAY_STATIC_URL}"
    }
    
    for key, value in urls.items():
        set_railway_variable(key, value)

def setup_security_variables():
    \"\"\"Setup security-related variables\"\"\"
    
    print("Setting up security variables...")
    
    # Generate secure random keys
    import secrets
    
    security_vars = {
        "JWT_SECRET_KEY": secrets.token_urlsafe(32),
        "API_SECRET_KEY": secrets.token_urlsafe(32),
        "META_WEBHOOK_VERIFY_TOKEN": secrets.token_urlsafe(16)
    }
    
    for key, value in security_vars.items():
        set_railway_variable(key, value)

def prompt_api_keys():
    \"\"\"Prompt user for API keys\"\"\"
    
    print("API Keys Configuration")
    print("=" * 50)
    
    api_keys = {
        "Meta Ads": [
            "META_ACCESS_TOKEN",
            "META_APP_ID", 
            "META_APP_SECRET",
            "META_ACCOUNT_ID",
            "META_PIXEL_ID"
        ],
        "YouTube": [
            "YOUTUBE_API_KEY",
            "YOUTUBE_CLIENT_ID",
            "YOUTUBE_CLIENT_SECRET"
        ],
        "TikTok (Optional)": [
            "TIKTOK_CLIENT_KEY",
            "TIKTOK_CLIENT_SECRET",
            "TIKTOK_ACCESS_TOKEN"
        ],
        "Instagram (Optional)": [
            "INSTAGRAM_ACCESS_TOKEN", 
            "INSTAGRAM_BUSINESS_ACCOUNT_ID"
        ],
        "Twitter (Optional)": [
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET", 
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_TOKEN_SECRET"
        ],
        "OpenAI (Recommended)": [
            "OPENAI_API_KEY"
        ]
    }
    
    for service, keys in api_keys.items():
        print(f"\\n{service}")
        print("-" * 30)
        
        for key in keys:
            value = input(f"Enter {key} (leave empty to skip): ").strip()
            if value:
                set_railway_variable(key, value)
                print(f"Set {key}")
            else:
                print(f"Skipped {key}")

def verify_setup():
    \"\"\"Verify Railway setup\"\"\"
    
    print("\\nVerifying setup...")
    
    try:
        # Get current variables
        result = subprocess.run(
            ["railway", "variables"],
            capture_output=True,
            text=True,
            check=True
        )
        
        variables = result.stdout
        
        # Count set variables
        required_vars = [
            "ENVIRONMENT", "ML_CORE_URL", "META_ACCESS_TOKEN",
            "JWT_SECRET_KEY", "DATABASE_URL"
        ]
        
        set_count = sum(1 for var in required_vars if var in variables)
        
        print(f"{set_count}/{len(required_vars)} required variables set")
        
        if set_count >= 3:
            print("Minimum configuration complete!")
            return True
        else:
            print("More configuration needed")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Verification failed: {e.stderr}")
        return False

def main():
    \"\"\"Main setup function\"\"\"
    
    print("Railway Meta Ads-Centric Setup")
    print("=" * 50)
    
    # Check Railway CLI
    try:
        subprocess.run(["railway", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Railway CLI not found. Please install it first:")
        print("npm install -g @railway/cli")
        return
    
    # Setup steps
    setup_core_variables()
    setup_service_urls()
    setup_security_variables()
    
    # Interactive API key setup
    print("\\n" + "=" * 50)
    setup_apis = input("Do you want to configure API keys now? (y/n): ").lower() == 'y'
    
    if setup_apis:
        prompt_api_keys()
    else:
        print("Skipping API keys setup")
        print("You can set them later in Railway dashboard")
    
    # Verify
    verify_setup()
    
    print("\\nSetup complete!")
    print("\\nNext steps:")
    print("1. railway up (to deploy)")
    print("2. Configure Meta Ads webhooks") 
    print("3. Test with sample campaign")

if __name__ == "__main__":
    main()
"""

def create_railway_files():
    """Crear todos los archivos de Railway"""
    
    base_path = Path(".")
    
    # railway.json
    railway_config = generate_railway_config()
    with open(base_path / "railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    
    # Procfile
    with open(base_path / "Procfile", "w") as f:
        f.write(generate_procfile())
    
    # Dockerfile para Railway
    docker_path = base_path / "docker"
    docker_path.mkdir(exist_ok=True)
    
    with open(docker_path / "Dockerfile.railway", "w") as f:
        f.write(generate_dockerfile_railway())
    
    # Script de deployment
    scripts_path = base_path / "scripts" / "railway"
    scripts_path.mkdir(parents=True, exist_ok=True)
    
    with open(scripts_path / "deploy.sh", "w") as f:
        f.write(generate_railway_deployment_script())
    
    # Script de configuración de entorno
    with open(scripts_path / "setup_environment.py", "w") as f:
        f.write(generate_environment_setup())
    
    # Hacer ejecutables los scripts
    os.chmod(scripts_path / "deploy.sh", 0o755)
    os.chmod(scripts_path / "setup_environment.py", 0o755)
    
    print("Railway files created successfully!")
    print(f"Files created:")
    print(f"  - railway.json")
    print(f"  - Procfile")
    print(f"  - docker/Dockerfile.railway")
    print(f"  - scripts/railway/deploy.sh")
    print(f"  - scripts/railway/setup_environment.py")

if __name__ == "__main__":
    create_railway_files()