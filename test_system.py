#!/usr/bin/env python3
"""
Comprehensive System Test Script
Tests all components of the universal dummy system
"""
import os
import sys
import asyncio
import importlib

def test_imports():
    """Test that all critical imports work"""
    print("🔍 Testing Critical Imports...")
    
    results = {}
    
    # Test core libraries
    test_modules = [
        'aiohttp',
        'asyncpg', 
        'telethon',
        'selenium',
        'webdriver_manager',
        'colorlog',
        'schedule',
        'requests'
    ]
    
    for module in test_modules:
        try:
            importlib.import_module(module)
            results[module] = "✅ PASS"
        except ImportError as e:
            results[module] = f"❌ FAIL: {e}"
    
    # Test our custom modules
    custom_modules = [
        'telegram_automation.youtube_executor.youtube_executor',
        'telegram_automation.bot.telegram_bot',
        'telegram_automation.database.models'
    ]
    
    for module in custom_modules:
        try:
            importlib.import_module(module)
            results[module] = "✅ PASS"
        except ImportError as e:
            results[module] = f"❌ FAIL: {e}"
    
    print("\n📊 Import Test Results:")
    for module, result in results.items():
        print(f"  {module}: {result}")
    
    passed = len([r for r in results.values() if "✅" in r])
    total = len(results)
    
    print(f"\n📈 Summary: {passed}/{total} imports successful ({passed/total*100:.1f}%)")
    return passed == total

async def test_youtube_executor():
    """Test YouTube executor in both modes"""
    print("\n🎬 Testing YouTube Executor...")
    
    try:
        # Test dummy mode
        os.environ['DUMMY_MODE'] = 'true'
        from telegram_automation.youtube_executor.youtube_executor import YouTubeExecutor, GoLoginAPI
        
        api = GoLoginAPI('test-token')
        profiles = api.get_available_profiles()
        print(f"✅ Dummy mode: {len(profiles)} profiles available")
        
        # Test production mode (imports only)
        os.environ['DUMMY_MODE'] = 'false'
        # Reload module to test production imports
        import telegram_automation.youtube_executor.youtube_executor as yt_module
        importlib.reload(yt_module)
        
        api_prod = yt_module.GoLoginAPI('prod-token')
        profiles_prod = api_prod.get_available_profiles()
        print(f"✅ Production mode: {len(profiles_prod)} profiles available")
        
        return True
        
    except Exception as e:
        print(f"❌ YouTube executor test failed: {e}")
        return False

async def test_telegram_bot():
    """Test Telegram bot components"""
    print("\n💬 Testing Telegram Bot...")
    
    try:
        os.environ['DUMMY_MODE'] = 'true'
        from telegram_automation.bot.telegram_bot import TelegramBot
        
        # Create bot instance (dummy mode)
        bot = TelegramBot(api_id=123, api_hash="dummy", bot_token="dummy")
        print("✅ Telegram bot created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram bot test failed: {e}")
        return False

async def test_database_models():
    """Test database models"""
    print("\n🗄️ Testing Database Models...")
    
    try:
        from telegram_automation.database.models import DatabaseConnection, Exchange
        from telegram_automation.bot.telegram_bot import Contact
        
        # Test dummy database
        db = DatabaseConnection("sqlite:///test.db")
        exchange = Exchange()
        contact = Contact()
        
        print("✅ Database models created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("🚀 Universal System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("YouTube Executor", test_youtube_executor),
        ("Telegram Bot", test_telegram_bot),
        ("Database Models", test_database_models)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for use.")
    else:
        print("⚠️ Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())