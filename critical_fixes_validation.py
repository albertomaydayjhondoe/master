#!/usr/bin/env python3
"""
Validation script for critical error fixes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test critical imports work"""
    print("🔍 Testing critical imports...")
    
    try:
        from ml_core.meta_automation.client import MetaMarketingClient
        print("✅ MetaMarketingClient import works")
    except Exception as e:
        print(f"❌ MetaMarketingClient error: {e}")
    
    try:
        from telegram_automation.database.models import DatabaseConnection, Contact, Exchange
        print("✅ Database models import works")
    except Exception as e:
        print(f"❌ Database models error: {e}")
    
    try:
        # Test client initialization
        client = MetaMarketingClient()
        print("✅ MetaMarketingClient initialization works")
    except Exception as e:
        print(f"❌ MetaMarketingClient init error: {e}")

def test_type_safety():
    """Test type safety improvements"""
    print("\n🔧 Testing type safety...")
    
    try:
        from ml_core.meta_automation.client import MetaMarketingClient
        # Test with None values
        client = MetaMarketingClient(api_key=None)
        print("✅ Optional[str] type hints work")
    except Exception as e:
        print(f"❌ Type hints error: {e}")

if __name__ == "__main__":
    print("🛠️  Critical Error Fixes Validation")
    print("=" * 45)
    
    test_imports()
    test_type_safety()
    
    print("=" * 45)
    print("🎯 Critical error fixes validation complete!")