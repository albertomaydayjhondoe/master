#!/usr/bin/env python3
"""
Railway Environment Variables Setup
Script para configurar todas las variables de entorno necesarias
"""

import os
import subprocess
import json
from typing import Dict, List

def set_railway_variable(key: str, value: str, service: str = None):
    """Set a Railway environment variable"""
    
    cmd = ["railway", "variables", "set", f"{key}={value}"]
    if service:
        cmd.extend(["--service", service])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Set {key}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set {key}: {e.stderr}")

def setup_core_variables():
    """Setup core system variables"""
    
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
    """Setup internal service URLs"""
    
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
    """Setup security-related variables"""
    
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
    """Prompt user for API keys"""
    
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
        print(f"\n{service}")
        print("-" * 30)
        
        for key in keys:
            value = input(f"Enter {key} (leave empty to skip): ").strip()
            if value:
                set_railway_variable(key, value)
                print(f"Set {key}")
            else:
                print(f"Skipped {key}")

def verify_setup():
    """Verify Railway setup"""
    
    print("\nVerifying setup...")
    
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
    """Main setup function"""
    
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
    print("\n" + "=" * 50)
    setup_apis = input("Do you want to configure API keys now? (y/n): ").lower() == 'y'
    
    if setup_apis:
        prompt_api_keys()
    else:
        print("Skipping API keys setup")
        print("You can set them later in Railway dashboard")
    
    # Verify
    verify_setup()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. railway up (to deploy)")
    print("2. Configure Meta Ads webhooks") 
    print("3. Test with sample campaign")

if __name__ == "__main__":
    main()
