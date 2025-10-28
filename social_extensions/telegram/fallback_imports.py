
"""Fallback imports para Telegram"""
import os

if os.getenv("DUMMY_MODE", "true").lower() == "true":
    try:
        from mcp_server.dummy_implementations import (
            DummyTelegramClient as TelegramClient,
            events,
            MessageMediaPhoto,
            MessageMediaDocument
        )
    except ImportError:
        # Fallback básico si MCP no está disponible
        class TelegramClient:
            def __init__(self, *args, **kwargs): pass
            async def start(self, *args, **kwargs): return True
            async def send_message(self, *args, **kwargs): return {"id": 1}
        
        class events:
            class NewMessage:
                def __init__(self, *args, **kwargs): pass
        
        class MessageMediaPhoto: pass
        class MessageMediaDocument: pass
else:
    # Intentar importación real
    try:
        from telethon import TelegramClient, events
        from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
    except ImportError:
        raise ImportError("Telethon no instalado. Activar DUMMY_MODE=true para usar implementación dummy")
