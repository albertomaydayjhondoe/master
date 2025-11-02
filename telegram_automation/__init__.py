"""
Telegram Automation System - Sistema de Intercambio Multiplataforma

Sistema completo de bot de Telegram para gestionar intercambios masivos de engagement
real en YouTube, Instagram y cuentas satélite mediante grupos de apoyo mutuo.

Arquitectura Modular:
1. Listener Module - Escucha y detecta contenido
2. Executor Module - Ejecuta acciones de engagement  
3. Priority Engine - Priorización inteligente ML
4. Metrics Collector - Registro y análisis
5. Message Generator - Engagement emocional humanizado
6. Multi-Account Manager - Coordinación de cuentas satélite

Integración con:
- ML Core: Decisiones de priorización y contenido
- GoLogin Automation: Cuentas anónimas y navegadores
- Database: Registro completo de interacciones
- Orchestration: Coordinación con workflows n8n
"""

from .bot.telegram_bot import TelegramBot
from .core.priority_engine import PriorityEngine
from .core.metrics_collector import MetricsCollector
from .core.multi_account_manager import MultiAccountManager
from .integrations.ml_integration import MLIntegration
from .integrations.gologin_integration import GoLoginIntegration
from .config.telegram_config import TelegramConfig

__version__ = "1.0.0"
__author__ = "Telegram Automation Team"

# Exports principales
__all__ = [
    'TelegramBot',
    'PriorityEngine', 
    'MetricsCollector',
    'MultiAccountManager',
    'MLIntegration',
    'GoLoginIntegration',
    'TelegramConfig'
]