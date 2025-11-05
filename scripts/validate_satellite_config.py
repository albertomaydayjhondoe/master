#!/usr/bin/env python3
"""
🔍 Neural Forge - Configuration Validator
=========================================
Validates satellite configuration and ensures main accounts cannot upload
"""

import os
import sys
import json
import asyncio
from typing import Dict, List
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from social_extensions.satellite_distribution import satellite_manager
from social_extensions.youtube_integration import youtube_manager

def load_secrets():
    """Load secrets from environment file"""
    secrets_file = "config/secrets/secrets.env"
    
    if not os.path.exists(secrets_file):
        print("❌ Secrets file not found: config/secrets/secrets.env")
        print("   Please copy config/secrets/secrets.env.template to config/secrets/secrets.env")
        print("   and configure with your real API keys")
        return False
    
    try:
        with open(secrets_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        
        print("✅ Secrets loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        return False

def validate_main_account_restrictions():
    """Validate that main accounts cannot upload"""
    print("\n🔍 Validating main account restrictions...")
    
    issues = []
    
    # Check YouTube main account
    if youtube_manager.main_account:
        if youtube_manager.main_account.upload_enabled:
            issues.append("❌ CRITICAL: YouTube main account has upload enabled!")
        else:
            print("✅ YouTube main account correctly configured (metrics only)")
        
        # Test upload restriction
        try:
            # This should raise an exception
            asyncio.run(youtube_manager.main_account.upload_video("test", "test", "test"))
            issues.append("❌ CRITICAL: YouTube main account upload not blocked!")
        except PermissionError:
            print("✅ YouTube main account upload correctly blocked")
        except Exception as e:
            print(f"⚠️  Unexpected error testing upload block: {e}")
    else:
        issues.append("⚠️  YouTube main account not configured")
    
    return issues

def validate_satellite_accounts():
    """Validate satellite account configuration"""
    print("\n🛰️  Validating satellite accounts...")
    
    issues = []
    
    # Check satellite manager
    validation_result = satellite_manager.validate_configuration()
    
    if not validation_result['valid']:
        issues.extend(validation_result['issues'])
    
    print(f"📊 Configuration Summary:")
    summary = validation_result['summary']
    print(f"   • Main accounts: {summary['main_accounts']}")
    print(f"   • Satellite accounts: {summary['satellite_accounts']}")
    print(f"   • Upload-enabled: {summary['upload_enabled_accounts']}")
    print(f"   • Metrics-enabled: {summary['metrics_enabled_accounts']}")
    
    # Check YouTube satellites
    youtube_satellites = len(youtube_manager.satellite_accounts)
    print(f"   • YouTube satellites: {youtube_satellites}")
    
    if youtube_satellites < 5:
        issues.append(f"⚠️  Only {youtube_satellites}/5 YouTube satellites configured")
    
    # Validate individual satellites
    for i, satellite in enumerate(youtube_manager.satellite_accounts, 1):
        if not satellite.upload_enabled:
            issues.append(f"❌ Satellite {i} has upload disabled")
        else:
            print(f"✅ Satellite {i} ({satellite.satellite_id}) configured correctly")
    
    return issues

def validate_secrets_configuration():
    """Validate secrets are properly configured"""
    print("\n🔐 Validating secrets configuration...")
    
    issues = []
    
    # Critical YouTube secrets (main account)
    main_youtube_secrets = [
        'YOUTUBE_API_KEY',
        'YOUTUBE_CLIENT_ID', 
        'YOUTUBE_CLIENT_SECRET',
        'YOUTUBE_REFRESH_TOKEN',
        'YOUTUBE_CHANNEL_ID'
    ]
    
    for secret in main_youtube_secrets:
        value = os.getenv(secret)
        if not value or value.startswith('your_'):
            issues.append(f"❌ Main YouTube secret not configured: {secret}")
        else:
            print(f"✅ Main YouTube secret configured: {secret}")
    
    # YouTube satellite secrets
    for i in range(1, 6):
        satellite_secrets = [
            f'YOUTUBE_SATELLITE_{i}_API_KEY',
            f'YOUTUBE_SATELLITE_{i}_CLIENT_ID',
            f'YOUTUBE_SATELLITE_{i}_CLIENT_SECRET',
            f'YOUTUBE_SATELLITE_{i}_REFRESH_TOKEN',
            f'YOUTUBE_SATELLITE_{i}_CHANNEL_ID'
        ]
        
        satellite_configured = True
        for secret in satellite_secrets:
            value = os.getenv(secret)
            if not value or value.startswith('satellite_') or value.startswith('your_'):
                satellite_configured = False
                break
        
        if satellite_configured:
            print(f"✅ Satellite {i} secrets configured")
        else:
            issues.append(f"⚠️  Satellite {i} secrets not fully configured")
    
    # Meta Ads secrets
    meta_secrets = [
        'META_ACCESS_TOKEN',
        'META_APP_ID',
        'META_APP_SECRET',
        'META_AD_ACCOUNT_ID'
    ]
    
    for secret in meta_secrets:
        value = os.getenv(secret)
        if not value or value.startswith('your_'):
            issues.append(f"⚠️  Meta Ads secret not configured: {secret}")
        else:
            print(f"✅ Meta Ads secret configured: {secret}")
    
    return issues

def validate_environment_configuration():
    """Validate environment variables"""
    print("\n🌍 Validating environment configuration...")
    
    issues = []
    
    # Critical environment settings
    critical_settings = {
        'MAIN_ACCOUNT_METRICS_ONLY': 'true',
        'USE_SATELLITE_ACCOUNTS': 'true',
        'SATELLITE_UPLOAD_ENABLED': 'true'
    }
    
    for setting, expected_value in critical_settings.items():
        actual_value = os.getenv(setting, '').lower()
        if actual_value != expected_value:
            issues.append(f"❌ Critical setting incorrect: {setting}={actual_value} (should be {expected_value})")
        else:
            print(f"✅ Critical setting correct: {setting}={expected_value}")
    
    # Check satellite count
    satellite_count = os.getenv('SATELLITE_COUNT', '0')
    if satellite_count != '5':
        issues.append(f"⚠️  SATELLITE_COUNT={satellite_count} (recommended: 5)")
    else:
        print(f"✅ Satellite count correct: {satellite_count}")
    
    return issues

async def test_functionality():
    """Test basic functionality"""
    print("\n🧪 Testing functionality...")
    
    issues = []
    
    try:
        # Test metrics collection (should work)
        print("📊 Testing metrics collection...")
        metrics = await youtube_manager.collect_all_metrics()
        
        if metrics.get('main_account'):
            print("✅ Main account metrics collection works")
        else:
            issues.append("⚠️  Main account metrics collection failed")
        
        satellite_metrics = metrics.get('satellite_accounts', [])
        print(f"✅ Collected metrics from {len(satellite_metrics)} satellites")
        
    except Exception as e:
        issues.append(f"❌ Metrics collection error: {e}")
    
    return issues

def generate_report(all_issues: List[str]):
    """Generate validation report"""
    print("\n" + "="*60)
    print("🎯 NEURAL FORGE CONFIGURATION VALIDATION REPORT")
    print("="*60)
    
    if not all_issues:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Configuration is ready for production")
        print("\n📋 Summary:")
        print("   • Main accounts configured for metrics only")
        print("   • Satellite accounts configured for content upload") 
        print("   • All security restrictions in place")
        print("   • Secrets properly separated")
        return True
    
    else:
        critical_issues = [i for i in all_issues if i.startswith("❌ CRITICAL")]
        error_issues = [i for i in all_issues if i.startswith("❌") and not i.startswith("❌ CRITICAL")]
        warning_issues = [i for i in all_issues if i.startswith("⚠️")]
        
        print(f"❌ VALIDATION FAILED: {len(all_issues)} issues found")
        print(f"   • Critical issues: {len(critical_issues)}")
        print(f"   • Error issues: {len(error_issues)}")
        print(f"   • Warnings: {len(warning_issues)}")
        
        if critical_issues:
            print("\n🚨 CRITICAL ISSUES (MUST FIX):")
            for issue in critical_issues:
                print(f"   {issue}")
        
        if error_issues:
            print("\n❌ ERROR ISSUES:")
            for issue in error_issues:
                print(f"   {issue}")
        
        if warning_issues:
            print("\n⚠️  WARNINGS:")
            for issue in warning_issues:
                print(f"   {issue}")
        
        return False

def main():
    """Main validation process"""
    print("🔍 Neural Forge Configuration Validator")
    print("========================================")
    
    # Step 1: Load secrets
    if not load_secrets():
        print("\n❌ Cannot proceed without secrets configuration")
        sys.exit(1)
    
    all_issues = []
    
    # Step 2: Validate main account restrictions
    all_issues.extend(validate_main_account_restrictions())
    
    # Step 3: Validate satellite accounts
    all_issues.extend(validate_satellite_accounts())
    
    # Step 4: Validate secrets
    all_issues.extend(validate_secrets_configuration())
    
    # Step 5: Validate environment
    all_issues.extend(validate_environment_configuration())
    
    # Step 6: Test functionality
    functionality_issues = asyncio.run(test_functionality())
    all_issues.extend(functionality_issues)
    
    # Step 7: Generate report
    success = generate_report(all_issues)
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Deploy to production server")
        print("2. Run health checks after deployment")
        print("3. Monitor satellite account usage")
        sys.exit(0)
    else:
        print("\n🔧 Fix the issues above before deploying to production")
        sys.exit(1)

if __name__ == "__main__":
    main()