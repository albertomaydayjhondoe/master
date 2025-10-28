#!/usr/bin/env python3
"""
🚀 Railway Production Setup - Complete System Deployment
Configures Railway secrets, environment variables, and deployment
"""

import json
import os
import subprocess
import sys
from pathlib import Path

class RailwayProductionSetup:
    """Complete Railway production setup"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config = {
            'app_name': 'stakas-mvp-viral-system',
            'channel_id': 'UCgohgqLVu1QPdfa64Vkrgeg',
            'channel_name': 'Stakas MVP',
            'budget': 500,
            'target_subs': 10000
        }
    
    def check_railway_cli(self):
        """Check if Railway CLI is installed"""
        try:
            result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
            print(f"✅ Railway CLI: {result.stdout.strip()}")
            return True
        except FileNotFoundError:
            print("❌ Railway CLI not found. Installing...")
            return False
    
    def install_railway_cli(self):
        """Install Railway CLI"""
        try:
            # Windows installation
            if os.name == 'nt':
                subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
            else:
                subprocess.run(['curl', '-fsSL', 'https://railway.app/install.sh'], shell=True)
            print("✅ Railway CLI installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Railway CLI: {e}")
            return False
    
    def railway_login(self):
        """Login to Railway"""
        print("🔐 Please login to Railway...")
        print("👉 Run: railway login")
        print("👉 Then run this script again")
        
        # Check if already logged in
        try:
            result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Already logged in: {result.stdout.strip()}")
                return True
            else:
                return False
        except:
            return False
    
    def create_railway_project(self):
        """Create or link Railway project"""
        try:
            # Try to create new project
            result = subprocess.run([
                'railway', 'project', 'create', 
                '--name', self.config['app_name']
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Railway project created: {self.config['app_name']}")
                
                # Get project ID
                project_info = subprocess.run(['railway', 'status'], capture_output=True, text=True)
                print(f"📋 Project info: {project_info.stdout}")
                return True
            else:
                print(f"ℹ️ Project might already exist: {result.stderr}")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create project: {e}")
            return False
    
    def set_environment_variables(self):
        """Set all production environment variables"""
        env_vars = {
            'APP_ENV': 'production',
            'CHANNEL_ID': self.config['channel_id'],
            'CHANNEL_NAME': self.config['channel_name'],
            'GENRE': 'drill_rap_espanol',
            'TARGET_SUBSCRIBERS': str(self.config['target_subs']),
            'META_ADS_BUDGET': str(self.config['budget']),
            'STREAMLIT_SERVER_HEADLESS': 'true',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
            'STREAMLIT_SERVER_MAX_UPLOAD_SIZE': '5',
            'STREAMLIT_SERVER_FILE_WATCHER_TYPE': 'none',
            'DUMMY_MODE': 'false',  # Production mode
            'ML_ENABLED': 'true',
            'N8N_ENABLED': 'true',
            'META_ADS_ENABLED': 'true',
            'DEVICE_FARM_ENABLED': 'true',
            'GOLOGIN_ENABLED': 'true'
        }
        
        print("🔧 Setting production environment variables...")
        for key, value in env_vars.items():
            try:
                subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
                print(f"  ✅ {key}={value}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to set {key}: {e}")
    
    def deploy_to_railway(self):
        """Deploy complete system to Railway"""
        print("🚀 Deploying to Railway...")
        
        try:
            # Use the optimized Dockerfile
            result = subprocess.run([
                'railway', 'up', '--detach'
            ], capture_output=True, text=True)
            
            print(f"📋 Deployment result: {result.stdout}")
            if result.stderr:
                print(f"⚠️ Warnings: {result.stderr}")
                
            return result.returncode == 0
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            return False
    
    def get_deployment_info(self):
        """Get deployment URLs and status"""
        try:
            # Get deployment status
            status = subprocess.run(['railway', 'status'], capture_output=True, text=True)
            print(f"📊 Status:\n{status.stdout}")
            
            # Get domain
            domain = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
            print(f"🌐 Domain:\n{domain.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get info: {e}")
            return False
    
    def create_github_secrets_instructions(self):
        """Create instructions for GitHub secrets"""
        print("\n" + "="*60)
        print("🔑 GITHUB SECRETS CONFIGURATION")
        print("="*60)
        
        # Get Railway token instructions
        print("""
📋 STEP 1: Get Railway Token
1. Go to: https://railway.app/account/tokens
2. Create new token: "GitHub Actions Deploy"
3. Copy the token

📋 STEP 2: Get Railway Project ID  
1. Run: railway status
2. Copy the Project ID from output

📋 STEP 3: Add to GitHub Secrets
1. Go to: https://github.com/albertomaydayjhondoe/master/settings/secrets/actions
2. Add these secrets:
   
   RAILWAY_TOKEN = <your_railway_token>
   RAILWAY_PROJECT_ID = <your_project_id>

📋 STEP 4: Trigger Deployment
1. Push any change to main branch
2. GitHub Actions will auto-deploy to Railway
        """)
    
    def run_complete_setup(self):
        """Run complete production setup"""
        print("🚀 STAKAS MVP - COMPLETE PRODUCTION SETUP")
        print("="*50)
        
        # Step 1: Check/Install Railway CLI
        if not self.check_railway_cli():
            if not self.install_railway_cli():
                return False
        
        # Step 2: Login check
        if not self.railway_login():
            return False
        
        # Step 3: Create/Link project
        if not self.create_railway_project():
            return False
        
        # Step 4: Set environment variables
        self.set_environment_variables()
        
        # Step 5: Deploy
        if self.deploy_to_railway():
            print("✅ Deployment successful!")
            self.get_deployment_info()
        else:
            print("❌ Deployment failed")
        
        # Step 6: GitHub secrets instructions
        self.create_github_secrets_instructions()
        
        print("\n🎯 SYSTEM READY FOR PRODUCTION!")
        print(f"📺 Channel: {self.config['channel_id']}")
        print(f"💰 Budget: €{self.config['budget']}/month")
        print(f"🎯 Target: {self.config['target_subs']:,} subscribers")

def main():
    """Main entry point"""
    setup = RailwayProductionSetup()
    setup.run_complete_setup()

if __name__ == "__main__":
    main()