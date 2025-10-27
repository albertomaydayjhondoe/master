#!/usr/bin/env python3
"""
🚀 Railway Environment Variables Setup Script
Configura todas las variables de entorno necesarias para Railway deployment
"""

import os
import sys
import json
from typing import Dict, List

class RailwayEnvSetup:
    """Setup de variables de entorno para Railway"""
    
    def __init__(self):
        self.required_vars = self._get_required_variables()
        self.railway_commands = []
    
    def _get_required_variables(self) -> Dict[str, Dict]:
        """Retorna todas las variables requeridas organizadas por categoría"""
        return {
            "core": {
                "DUMMY_MODE": "false",
                "RAILWAY_ENVIRONMENT": "production", 
                "PYTHONPATH": ".",
                "PORT": "$PORT"
            },
            
            "database": {
                "DATABASE_URL": "${RAILWAY_DATABASE_URL}",
                "POSTGRES_PASSWORD": "railway_postgres_2025",
                "REDIS_URL": "${RAILWAY_REDIS_URL}"
            },
            
            "meta_ads": {
                "META_ACCESS_TOKEN": "REQUIRED - Get from Meta Business Manager",
                "META_AD_ACCOUNT_ID": "REQUIRED - Your Meta Ad Account ID", 
                "META_PIXEL_ID": "REQUIRED - Your Facebook Pixel ID"
            },
            
            "youtube": {
                "YOUTUBE_CLIENT_ID": "REQUIRED - Google Cloud Console",
                "YOUTUBE_CLIENT_SECRET": "REQUIRED - Google Cloud Console",
                "YOUTUBE_CHANNEL_ID": "REQUIRED - Your YouTube Channel ID"
            },
            
            "n8n": {
                "N8N_USER": "admin",
                "N8N_PASSWORD": "viral_admin_2025",
                "N8N_ENCRYPTION_KEY": "railway_n8n_key_2025"
            },
            
            "monitoring": {
                "GRAFANA_USER": "admin",
                "GRAFANA_PASSWORD": "viral_monitor_2025"
            },
            
            "telegram": {
                "TELEGRAM_BOT_TOKEN": "OPTIONAL - For notifications",
                "TELEGRAM_CHAT_ID": "OPTIONAL - For notifications"
            },
            
            "gologin": {
                "GOLOGIN_API_KEY": "OPTIONAL - For browser automation",
                "GOLOGIN_PROFILE_IDS": "OPTIONAL - Comma separated profile IDs"
            },
            
            "service_urls": {
                "ML_CORE_URL": "https://ml-core.railway.app",
                "META_ADS_URL": "https://meta-ads.railway.app", 
                "YOUTUBE_URL": "https://youtube.railway.app",
                "N8N_URL": "https://n8n.railway.app"
            }
        }
    
    def generate_railway_commands(self) -> List[str]:
        """Genera comandos railway variables set"""
        commands = []
        
        print("🚀 RAILWAY ENVIRONMENT SETUP")
        print("="*60)
        
        for category, variables in self.required_vars.items():
            print(f"\n📂 {category.upper()} Variables:")
            print("-" * 40)
            
            for var_name, default_value in variables.items():
                if "REQUIRED" in str(default_value):
                    print(f"⚠️  {var_name}: {default_value}")
                    commands.append(f'# {var_name}="{default_value}"')
                else:
                    print(f"✅ {var_name}: {default_value}")
                    commands.append(f'railway variables set {var_name}="{default_value}"')
        
        return commands
    
    def save_setup_script(self, filename: str = "railway_setup.sh"):
        """Guarda script de setup para Railway"""
        commands = self.generate_railway_commands()
        
        script_content = f'''#!/bin/bash
# 🚀 Railway Environment Variables Setup
# Generated automatically for TikTok Viral ML System V3

echo "🚀 Setting up Railway environment variables..."

# Core system variables
{chr(10).join([cmd for cmd in commands if not cmd.startswith('#')])}

echo "✅ Basic variables configured!"
echo "⚠️  Configure these REQUIRED variables manually:"
echo "   1. Meta Ads credentials (META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, META_PIXEL_ID)"
echo "   2. YouTube API credentials (YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_CHANNEL_ID)"  
echo "   3. Optional: Telegram notifications (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)"
echo "   4. Optional: GoLogin automation (GOLOGIN_API_KEY, GOLOGIN_PROFILE_IDS)"

echo "🌐 After setting required variables, deploy with:"
echo "   railway up"
'''
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(filename, 0o755)
        print(f"\n💾 Setup script saved: {filename}")
        return filename
    
    def generate_env_template(self, filename: str = ".env.railway.template"):
        """Genera template de variables de entorno"""
        template_lines = []
        
        for category, variables in self.required_vars.items():
            template_lines.append(f"# {category.upper()} Variables")
            for var_name, default_value in variables.items():
                if "REQUIRED" in str(default_value):
                    template_lines.append(f"{var_name}=# {default_value}")
                else:
                    template_lines.append(f"{var_name}={default_value}")
            template_lines.append("")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(template_lines))
        
        print(f"📄 Environment template saved: {filename}")
        return filename
    
    def validate_current_env(self) -> Dict[str, bool]:
        """Valida variables de entorno actuales"""
        validation = {}
        
        print("\n🔍 VALIDATING CURRENT ENVIRONMENT")
        print("="*50)
        
        for category, variables in self.required_vars.items():
            print(f"\n📂 {category.upper()}:")
            
            for var_name, _ in variables.items():
                current_value = os.getenv(var_name)
                is_set = current_value is not None and current_value.strip() != ""
                
                if is_set:
                    # Mask sensitive values
                    display_value = current_value
                    if any(sensitive in var_name.lower() for sensitive in ['token', 'secret', 'key', 'password']):
                        display_value = f"{current_value[:8]}..." if len(current_value) > 8 else "***"
                    print(f"   ✅ {var_name}: {display_value}")
                else:
                    print(f"   ❌ {var_name}: Not set")
                
                validation[var_name] = is_set
        
        # Summary
        total_vars = sum(len(vars) for vars in self.required_vars.values())
        set_vars = sum(validation.values())
        
        print(f"\n📊 SUMMARY: {set_vars}/{total_vars} variables configured ({set_vars/total_vars*100:.1f}%)")
        
        if set_vars == total_vars:
            print("🎉 All variables configured! Ready for Railway deployment.")
        else:
            missing = [var for var, is_set in validation.items() if not is_set]
            print(f"⚠️  Missing variables: {', '.join(missing[:5])}")
            if len(missing) > 5:
                print(f"   ... and {len(missing) - 5} more")
        
        return validation

def main():
    """Main entry point"""
    setup = RailwayEnvSetup()
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                🚀 RAILWAY DEPLOYMENT SETUP                      ║
║                                                                  ║
║  TikTok Viral ML System V3 - Environment Configuration          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    # Generate commands and templates
    setup_script = setup.save_setup_script()
    env_template = setup.generate_env_template()
    
    # Validate current environment
    validation = setup.validate_current_env()
    
    print(f"""
🎯 NEXT STEPS:

1. 📝 Configure required variables:
   Edit {env_template} with your credentials
   
2. 🚀 Run setup script:
   ./{setup_script}
   
3. 🌐 Deploy to Railway:
   railway login
   railway link
   railway up
   
4. 📊 Monitor deployment:
   railway logs
   railway status

📚 Full documentation: RAILWAY_OPERABILITY_ANALYSIS.md
""")

if __name__ == "__main__":
    main()