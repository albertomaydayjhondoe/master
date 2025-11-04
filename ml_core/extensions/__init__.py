"""
🧠 EXTENSIONES AVANZADAS DEL SISTEMA ML

Este módulo contiene las tres extensiones inteligentes que convierten el sistema
en un "cerebro que piensa, siente y predice":

1. 💭 Feedback Sentiment Engine - Analiza sentimientos de comentarios
2. 🔥 Cultural Trend Miner - Detecta microtendencias emergentes  
3. 📈 Network Growth Simulator - Predice crecimiento y optimiza ROI

Cada extensión es modular y puede funcionar independientemente.
"""

from .sentiment_engine import FeedbackSentimentEngine
from .trend_miner import CulturalTrendMiner
from .growth_simulator import NetworkGrowthSimulator

__version__ = "1.0.0"
__all__ = [
    "FeedbackSentimentEngine",
    "CulturalTrendMiner", 
    "NetworkGrowthSimulator"
]