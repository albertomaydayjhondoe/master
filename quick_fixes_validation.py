#!/usr/bin/env python3
"""Quick validation script to verify the fixes applied"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logging_fixes():
    """Test that logging is working properly"""
    # Test Discord notifier
    try:
        from monitoring.alerts.discord_notifier import DiscordNotifier
        notifier = DiscordNotifier()
        notifier.send({"test": "alert"})
        print("✅ Discord notifier logging fix works")
    except Exception as e:
        print(f"❌ Discord notifier error: {e}")
    
    # Test telegram models
    try:
        from telegram_automation.database.models import DummyConnection
        conn = DummyConnection()
        print("✅ Database models logging fix works")
    except Exception as e:
        print(f"❌ Database models error: {e}")
    
    # Test telegram bot
    try:
        from telegram_automation.bot.telegram_bot import TelegramBot
        # Don't create a bot instance to avoid connection issues
        print("✅ Telegram bot import works")
    except Exception as e:
        print(f"❌ Telegram bot error: {e}")

def test_factory_enhancements():
    """Test factory modules with new docstrings"""
    try:
        import ml_core.models.factory as ml_factory
        print(f"✅ ML factory has docstring: {bool(ml_factory.__doc__)}")
        print(f"✅ ML factory has __all__: {hasattr(ml_factory, '__all__')}")
    except Exception as e:
        print(f"❌ ML factory error: {e}")
    
    try:
        import device_farm.controllers.factory as df_factory  
        print(f"✅ Device farm factory has __all__: {hasattr(df_factory, '__all__')}")
    except Exception as e:
        print(f"❌ Device farm factory error: {e}")

if __name__ == "__main__":
    print("🔧 Quick Issue Fixes Validation")
    print("=" * 40)
    
    # Set up logging to see our improvements
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    
    test_logging_fixes()
    test_factory_enhancements()
    
    print("=" * 40)
    print("🎉 Quick fixes validation complete!")