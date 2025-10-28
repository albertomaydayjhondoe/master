"""
Telegram Groups Extension for Social Media Automation
Provides automation for Telegram group management and posting
"""

from .telegram_automator import TelegramAutomator
from .telegram_action_generator import TelegramActionGenerator
from .api_endpoints import router as telegram_router
from .monitoring import TelegramMonitor
from .production_config import TelegramProductionConfig

# Try to import telegram-specific dependencies
try:
    import telethon
    from telethon import TelegramClient
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("🤖 Telegram dependencies not available - using dummy implementations")

try:
    import asyncio
    ASYNCIO_AVAILABLE = True
except ImportError:
    ASYNCIO_AVAILABLE = False

__all__ = [
    'TelegramAutomator',
    'TelegramActionGenerator', 
    'telegram_router',
    'TelegramMonitor',
    'TelegramProductionConfig',
    'TELEGRAM_AVAILABLE',
    'ASYNCIO_AVAILABLE'
]

__version__ = "1.0.0"