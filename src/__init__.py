"""
Viral Marketing AI System - Source Code Root
Arquitectura basada en Clean Architecture y Domain-Driven Design
"""

__version__ = "2.0.0"
__author__ = "Viral Marketing AI Team"
__description__ = "Advanced Multi-Platform Viral Marketing System with AI Intelligence"

# Configuración global del sistema
SYSTEM_CONFIG = {
    "version": __version__,
    "architecture": "Clean Architecture + DDD",
    "platforms_supported": ["meta", "tiktok", "youtube", "twitter", "telegram"],
    "domains": ["campaigns", "analytics", "intelligence", "platforms", "automation", "shared"],
    "environment": "production-ready",
    "dummy_mode": True  # Se cambia a False en producción real
}

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "SYSTEM_CONFIG"
]