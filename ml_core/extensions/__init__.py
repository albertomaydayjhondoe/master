"""
🧠 EXTENSIONES AVANZADAS DEL SISTEMA ML - MODO DURMIENTE

Este módulo contiene las tres extensiones inteligentes que convierten el sistema
en un "cerebro que piensa, siente y predice":

1. 💭 Feedback Sentiment Engine - Analiza sentimientos de comentarios
2. 🔥 Cultural Trend Miner - Detecta microtendencias emergentes  
3. 📈 Network Growth Simulator - Predice crecimiento y optimiza ROI

🛌 MODO DURMIENTE ACTIVADO:
- Extensiones inactivas hasta instalación de dependencias
- Solo funcionalidades base disponibles
- Para despertar: instalar requirements-extensions.txt
"""

# Importar implementaciones dormantes por defecto
from .dormant_mode import (
    create_sentiment_engine,
    create_trend_miner, 
    create_growth_simulator,
    wake_extensions,
    check_extension_requirements,
    EXTENSIONS_DORMANT_MODE
)

# Clases dormantes como fallback
from .dormant_mode import (
    DormantSentimentEngine as FeedbackSentimentEngine,
    DormantTrendMiner as CulturalTrendMiner,
    DormantGrowthSimulator as NetworkGrowthSimulator
)

__version__ = "1.0.0-dormant"
__all__ = [
    "FeedbackSentimentEngine",
    "CulturalTrendMiner", 
    "NetworkGrowthSimulator",
    "create_sentiment_engine",
    "create_trend_miner",
    "create_growth_simulator",
    "wake_extensions",
    "check_extension_requirements"
]