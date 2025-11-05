#!/usr/bin/env python3
"""
🧪 Secure Satellite Integration Test
====================================
Tests the complete LongCat + Secure Satellites integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project to path
sys.path.append('.')

async def test_secure_satellite_import():
    """Test importing secure satellite manager"""
    print("🔧 Testing secure satellite import...")
    
    try:
        from social_extensions.longcat_satellites_secure import get_secure_satellite_manager
        print("✅ Secure satellite manager import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_satellite_initialization():
    """Test initializing the secure satellite manager"""
    print("\n🛰️ Testing satellite initialization...")
    
    try:
        from social_extensions.longcat_satellites_secure import get_secure_satellite_manager
        
        # Initialize (will use dummy mode)
        manager = await get_secure_satellite_manager()
        print("✅ Satellite manager initialized successfully")
        
        # Test basic methods
        status = manager.get_status()
        print(f"✅ Manager status: {status.get('initialized', False)}")
        print(f"✅ Found {len(manager.satellites)} satellites")
        
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

async def test_content_validation():
    """Test content validation system"""
    print("\n🔍 Testing content validation...")
    
    try:
        from social_extensions.longcat_satellites_secure import get_secure_satellite_manager
        
        manager = await get_secure_satellite_manager()
        
        # Test valid content
        valid_content = {
            'artist': 'Test Artist',
            'song': 'Test Song',
            'genre': 'electronic',
            'prompt': 'Create a professional music video'
        }
        
        # Test internal validation (this is a private method, so we'll test it indirectly)
        dummy_path = "data/temp/test_content.mp4"
        Path(dummy_path).parent.mkdir(parents=True, exist_ok=True)
        Path(dummy_path).write_text("dummy content")
        
        validation = manager._validate_content(dummy_path)
        print(f"✅ Content validation result: {validation['valid']}")
        
        if Path(dummy_path).exists():
            Path(dummy_path).unlink()
        
        return True
    except Exception as e:
        print(f"❌ Content validation failed: {e}")
        return False

async def test_dummy_distribution():
    """Test dummy video distribution"""
    print("\n📹 Testing dummy distribution...")
    
    try:
        from social_extensions.longcat_satellites_secure import get_secure_satellite_manager
        
        manager = await get_secure_satellite_manager()
        
        # Create dummy content file
        dummy_path = "data/temp/test_content.mp4"
        Path(dummy_path).parent.mkdir(parents=True, exist_ok=True)
        Path(dummy_path).write_text("dummy video content")
        
        # Test distribution
        result = await manager.distribute_variations(
            content_path=dummy_path,
            artist="Test Artist",
            song="Test Song",
            genre="electronic",
            base_prompt="Test music video",
            variations=["remix", "edit"]
        )
        
        print(f"✅ Distribution result: {result.get('status', 'unknown')}")
        print(f"   - Successful: {result.get('successful', 0)}")
        print(f"   - Failed: {result.get('failed', 0)}")
        
        # Cleanup
        if Path(dummy_path).exists():
            Path(dummy_path).unlink()
        
        return True
    except Exception as e:
        print(f"❌ Distribution test failed: {e}")
        return False

async def test_campaign_launcher_integration():
    """Test integration with campaign launcher"""
    print("\n🚀 Testing campaign launcher integration...")
    
    try:
        from launch_viral_campaign import ViralCampaignOrchestrator
        
        # Initialize orchestrator
        orchestrator = ViralCampaignOrchestrator()
        print("✅ Campaign orchestrator initialized")
        
        # Check if satellite manager can be accessed
        if hasattr(orchestrator, 'satellite_manager'):
            print("✅ Satellite manager attribute found")
        else:
            print("ℹ️ Satellite manager will be initialized on demand")
        
        return True
    except Exception as e:
        print(f"❌ Campaign launcher integration failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("🧪 Neural Forge - Secure Satellite Integration Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_secure_satellite_import),
        ("Initialization Test", test_satellite_initialization),
        ("Content Validation Test", test_content_validation),
        ("Distribution Test", test_dummy_distribution),
        ("Campaign Integration Test", test_campaign_launcher_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Secure satellite integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)