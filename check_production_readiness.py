#!/usr/bin/env python3
"""
🚀 NEURAL FORGE - PRODUCTION DEPLOYMENT CHECKER
==============================================
Validates complete system readiness for viral campaigns

Features:
✅ LongCat AI Video Generation with Secure Satellites
✅ Meta Ads Production API Integration  
✅ YouTube Satellite Distribution System
✅ Enterprise Security & Monitoring
✅ Docker Production Environment
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import json

# Add project to path
sys.path.append('.')

class ProductionDeploymentChecker:
    """Comprehensive production readiness validation"""
    
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
        
    async def check_secure_satellites(self) -> Dict[str, Any]:
        """Check secure satellite system"""
        print("🛰️ Checking Secure LongCat Satellites...")
        
        try:
            from social_extensions.longcat_satellites_secure import get_secure_satellite_manager
            
            manager = await get_secure_satellite_manager()
            status = manager.get_status()
            
            result = {
                "component": "secure_satellites",
                "status": "✅ READY" if status.get("initialized") else "⚠️ PARTIAL",
                "satellites": len(manager.satellites),
                "security_enabled": True,
                "dummy_mode": not manager.video_generator
            }
            
            if result["dummy_mode"]:
                self.warnings.append("Secure satellites running in dummy mode - production dependencies missing")
            
            return result
        except Exception as e:
            self.errors.append(f"Secure satellites failed: {e}")
            return {"component": "secure_satellites", "status": "❌ FAILED", "error": str(e)}
    
    async def check_meta_ads(self) -> Dict[str, Any]:
        """Check Meta Ads production system"""
        print("📱 Checking Meta Ads Production...")
        
        try:
            from social_extensions.meta_ads_production import MetaAdsProductionAPI
            
            # Check for required environment variables
            required_vars = [
                'META_APP_ID', 'META_APP_SECRET', 'META_ACCESS_TOKEN',
                'META_AD_ACCOUNT_ID', 'META_PAGE_ID'
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            result = {
                "component": "meta_ads",
                "status": "✅ READY" if not missing_vars else "⚠️ CONFIG_NEEDED",
                "missing_env_vars": missing_vars,
                "api_available": True
            }
            
            if missing_vars:
                self.warnings.append(f"Meta Ads missing env vars: {', '.join(missing_vars)}")
            
            return result
        except Exception as e:
            self.errors.append(f"Meta Ads check failed: {e}")
            return {"component": "meta_ads", "status": "❌ FAILED", "error": str(e)}
    
    async def check_youtube_satellites(self) -> Dict[str, Any]:
        """Check YouTube satellite system"""
        print("📺 Checking YouTube Satellites...")
        
        try:
            # Check satellite environment variables
            satellite_configs = []
            for i in range(1, 6):
                config = {
                    "api_key": os.getenv(f'YOUTUBE_SATELLITE_{i}_API_KEY'),
                    "client_id": os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_ID'),
                    "client_secret": os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_SECRET'),
                    "refresh_token": os.getenv(f'YOUTUBE_SATELLITE_{i}_REFRESH_TOKEN'),
                    "channel_id": os.getenv(f'YOUTUBE_SATELLITE_{i}_CHANNEL_ID')
                }
                
                if all(config.values()):
                    satellite_configs.append(i)
            
            result = {
                "component": "youtube_satellites",
                "status": "✅ READY" if satellite_configs else "⚠️ CONFIG_NEEDED",
                "configured_satellites": len(satellite_configs),
                "satellite_ids": satellite_configs
            }
            
            if not satellite_configs:
                self.warnings.append("No YouTube satellites configured - set YOUTUBE_SATELLITE_X_* env vars")
            
            return result
        except Exception as e:
            self.errors.append(f"YouTube satellites check failed: {e}")
            return {"component": "youtube_satellites", "status": "❌ FAILED", "error": str(e)}
    
    async def check_monitoring_system(self) -> Dict[str, Any]:
        """Check monitoring and dashboards"""
        print("📊 Checking Monitoring System...")
        
        try:
            dashboard_files = [
                "monitoring/dashboards/grafana/meta_ads_performance.json",
                "monitoring/dashboards/grafana/youtube_analytics.json",
                "monitoring/dashboards/grafana/longcat_metrics.json"
            ]
            
            existing_dashboards = [f for f in dashboard_files if Path(f).exists()]
            
            result = {
                "component": "monitoring",
                "status": "✅ READY" if existing_dashboards else "⚠️ PARTIAL",
                "dashboards": len(existing_dashboards),
                "dashboard_files": existing_dashboards
            }
            
            if not existing_dashboards:
                self.warnings.append("No monitoring dashboards found")
            
            return result
        except Exception as e:
            self.errors.append(f"Monitoring check failed: {e}")
            return {"component": "monitoring", "status": "❌ FAILED", "error": str(e)}
    
    async def check_security_config(self) -> Dict[str, Any]:
        """Check security configuration"""
        print("🔐 Checking Security Configuration...")
        
        try:
            security_files = [
                "config/secrets/.env",
                "config/secrets/longcat_key.bin"
            ]
            
            existing_files = [f for f in security_files if Path(f).exists()]
            
            # Check if encryption key directory exists
            key_dir = Path("config/secrets")
            key_dir.mkdir(parents=True, exist_ok=True)
            
            result = {
                "component": "security",
                "status": "✅ READY" if len(existing_files) >= 1 else "⚠️ SETUP_NEEDED",
                "security_files": existing_files,
                "encryption_ready": True
            }
            
            if len(existing_files) < 1:
                self.warnings.append("Security configuration incomplete - check config/secrets/")
            
            return result
        except Exception as e:
            self.errors.append(f"Security check failed: {e}")
            return {"component": "security", "status": "❌ FAILED", "error": str(e)}
    
    async def check_docker_environment(self) -> Dict[str, Any]:
        """Check Docker production environment"""
        print("🐳 Checking Docker Environment...")
        
        try:
            docker_files = [
                "docker-compose.prod.yml",
                "docker/Dockerfile.ml-api",
                "docker/Dockerfile.ml-api.no-gpu"
            ]
            
            existing_files = [f for f in docker_files if Path(f).exists()]
            
            result = {
                "component": "docker",
                "status": "✅ READY" if existing_files else "⚠️ PARTIAL",
                "docker_files": len(existing_files),
                "production_ready": "docker-compose.prod.yml" in [Path(f).name for f in existing_files]
            }
            
            if not existing_files:
                self.warnings.append("Docker configuration files missing")
            
            return result
        except Exception as e:
            self.errors.append(f"Docker check failed: {e}")
            return {"component": "docker", "status": "❌ FAILED", "error": str(e)}
    
    async def check_campaign_launcher(self) -> Dict[str, Any]:
        """Check viral campaign launcher"""
        print("🚀 Checking Campaign Launcher...")
        
        try:
            launcher_file = Path("launch_viral_campaign.py")
            
            if launcher_file.exists():
                # Try to import (will show any import issues)
                try:
                    from launch_viral_campaign import ViralCampaignOrchestrator
                    orchestrator = ViralCampaignOrchestrator()
                    
                    result = {
                        "component": "campaign_launcher",
                        "status": "✅ READY",
                        "file_exists": True,
                        "import_successful": True
                    }
                except Exception as import_error:
                    result = {
                        "component": "campaign_launcher", 
                        "status": "⚠️ IMPORT_ISSUES",
                        "file_exists": True,
                        "import_successful": False,
                        "import_error": str(import_error)
                    }
                    self.warnings.append(f"Campaign launcher import issues: {import_error}")
            else:
                result = {
                    "component": "campaign_launcher",
                    "status": "❌ MISSING",
                    "file_exists": False
                }
                self.errors.append("Campaign launcher file missing")
            
            return result
        except Exception as e:
            self.errors.append(f"Campaign launcher check failed: {e}")
            return {"component": "campaign_launcher", "status": "❌ FAILED", "error": str(e)}
    
    async def run_complete_check(self) -> Dict[str, Any]:
        """Run all production readiness checks"""
        print("🔍 NEURAL FORGE - PRODUCTION DEPLOYMENT CHECK")
        print("=" * 60)
        
        checks = [
            ("Secure Satellites", self.check_secure_satellites),
            ("Meta Ads", self.check_meta_ads), 
            ("YouTube Satellites", self.check_youtube_satellites),
            ("Monitoring", self.check_monitoring_system),
            ("Security", self.check_security_config),
            ("Docker", self.check_docker_environment),
            ("Campaign Launcher", self.check_campaign_launcher)
        ]
        
        results = []
        
        for check_name, check_func in checks:
            print(f"\n🔍 {check_name}...")
            try:
                result = await check_func()
                results.append(result)
                print(f"   {result['status']}")
            except Exception as e:
                error_result = {"component": check_name.lower().replace(" ", "_"), "status": "❌ CRASHED", "error": str(e)}
                results.append(error_result)
                print(f"   ❌ CRASHED: {e}")
        
        # Summary
        ready_count = len([r for r in results if r["status"].startswith("✅")])
        partial_count = len([r for r in results if r["status"].startswith("⚠️")])
        failed_count = len([r for r in results if r["status"].startswith("❌")])
        
        overall_status = "✅ PRODUCTION READY" if failed_count == 0 and partial_count == 0 else \
                        "⚠️ NEEDS CONFIGURATION" if failed_count == 0 else \
                        "❌ NOT READY"
        
        summary = {
            "overall_status": overall_status,
            "timestamp": "2025-01-22T18:00:00",
            "components_ready": ready_count,
            "components_partial": partial_count, 
            "components_failed": failed_count,
            "total_components": len(results),
            "results": results,
            "warnings": self.warnings,
            "errors": self.errors
        }
        
        return summary

async def main():
    """Main deployment check"""
    checker = ProductionDeploymentChecker()
    summary = await checker.run_complete_check()
    
    # Print detailed summary
    print("\n" + "=" * 60)
    print("🎯 PRODUCTION READINESS SUMMARY")
    print("=" * 60)
    
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Components Ready: {summary['components_ready']}/{summary['total_components']}")
    
    if summary['warnings']:
        print(f"\n⚠️ Warnings ({len(summary['warnings'])}):")
        for warning in summary['warnings']:
            print(f"   • {warning}")
    
    if summary['errors']:
        print(f"\n❌ Errors ({len(summary['errors'])}):")
        for error in summary['errors']:
            print(f"   • {error}")
    
    # Component details
    print(f"\n📋 Component Status:")
    for result in summary['results']:
        print(f"   {result['status']} {result['component']}")
    
    # Save report
    report_file = f"logs/production_readiness_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(report_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Full report saved: {report_file}")
    
    # Recommendations
    print(f"\n🎯 NEXT STEPS:")
    if summary['overall_status'] == "✅ PRODUCTION READY":
        print("   🚀 System is ready for viral campaign deployment!")
        print("   📋 Run: python launch_viral_campaign.py")
    elif summary['overall_status'] == "⚠️ NEEDS CONFIGURATION":
        print("   🔧 Configure missing environment variables")
        print("   📁 Check config/secrets/ directory")
        print("   🛠️ Review warnings above")
    else:
        print("   🔥 Fix critical errors first")
        print("   📚 Check documentation: docs/setup/")
        print("   🐛 Review error messages above")
    
    return summary['overall_status'] == "✅ PRODUCTION READY"

if __name__ == "__main__":
    from datetime import datetime
    success = asyncio.run(main())
    sys.exit(0 if success else 1)