"""
🧠 EXTENSIONES AVANZADAS - MODO DURMIENTE

Todas las extensiones están en estado dormant hasta activación manual.
Solo funciona con constantes ya definidas en el sistema base.
"""

# Modo durmiente global para extensiones
EXTENSIONS_DORMANT_MODE = True
EXTENSIONS_AWAKE = False

# Solo activar si hay configuración completa
SENTIMENT_ENGINE_ENABLED = False  # Requiere: transformers, bertopic
TREND_MINER_ENABLED = False      # Requiere: APIs externas
GROWTH_SIMULATOR_ENABLED = False  # Requiere: modelos entrenados

def check_requirements():
    """
    Verifica si al menos las dependencias básicas están disponibles
    """
    # Solo checkeamos dependencias básicas para permitir despertar parcial
    basic_packages = ['pandas', 'numpy', 'requests']
    
    missing = []
    for package in basic_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    # Siempre retorna True para permitir despertar (modo desarrollo)
    return True, missing

# Dummy implementations para evitar errores
class DormantSentimentEngine:
    def __init__(self):
        self.mode = "dormant"
    
    async def initialize(self):
        return False
    
    async def analyze_video_feedback(self, *args, **kwargs):
        return {"status": "dormant", "message": "Sentiment engine en modo durmiente"}
    
    def analyze_comments(self, comments):
        """Análisis básico de comentarios en modo durmiente"""
        return {
            "sentiment": "neutral",
            "score": 0.5,
            "topics": ["music", "general"],
            "summary": f"Analyzed {len(comments)} comments in dormant mode",
            "dormant_mode": True
        }

class DormantTrendMiner:  
    def __init__(self):
        self.mode = "dormant"
    
    async def initialize(self):
        return False
    
    async def mine_daily_trends(self, *args, **kwargs):
        return {"status": "dormant", "message": "Trend miner en modo durmiente"}
    
    def discover_trends(self):
        """Descubrimiento básico de tendencias en modo durmiente"""
        return {
            "trends": [
                {"platform": "TikTok", "trend": "Urban Beats", "score": 0.85},
                {"platform": "YouTube", "trend": "Trap Latino", "score": 0.78}
            ],
            "summary": "Demo trends in dormant mode",
            "dormant_mode": True
        }

class DormantGrowthSimulator:
    def __init__(self):
        self.mode = "dormant"
    
    async def initialize(self):
        return False
    
    async def simulate_campaign_scenarios(self, *args, **kwargs):
        return []

# Factory functions que retornan implementaciones dormantes
def create_sentiment_engine():
    if EXTENSIONS_DORMANT_MODE or not SENTIMENT_ENGINE_ENABLED:
        return DormantSentimentEngine()
    else:
        from .sentiment_engine import FeedbackSentimentEngine
        return FeedbackSentimentEngine()

def create_trend_miner():
    if EXTENSIONS_DORMANT_MODE or not TREND_MINER_ENABLED:
        return DormantTrendMiner()
    else:
        from .trend_miner import CulturalTrendMiner
        return CulturalTrendMiner()

def create_growth_simulator():
    if EXTENSIONS_DORMANT_MODE or not GROWTH_SIMULATOR_ENABLED:
        return DormantGrowthSimulator()
    else:
        from .growth_simulator import NetworkGrowthSimulator
        return NetworkGrowthSimulator()

# Para despertar extensiones (solo si requirements están disponibles)
def wake_extensions():
    """
    Despierta las extensiones en modo desarrollo/demo
    """
    can_wake, missing = check_requirements()
    
    # En modo desarrollo, siempre permitimos despertar
    print("🧠 NEURAL FORGE DISCOGRÁFICA - Despertando extensiones...")
    print("🎯 Modo: Desarrollo/Demo (funcionalidad limitada)")
    
    if missing:
        print(f"⚠️ Algunas dependencias faltan: {missing}")
        print("💡 Extensiones funcionarán en modo simulado")
    
    # Cambiar variable global para indicar que estamos despiertos
    global EXTENSIONS_AWAKE
    EXTENSIONS_AWAKE = True
    
    return "🎉 Extensiones despertadas en modo desarrollo - Dashboard disponible"

# Factory functions para crear las extensiones
def create_sentiment_engine():
    """Factory para crear Sentiment Engine"""
    if EXTENSIONS_AWAKE:
        return DormantSentimentEngine()  # En modo demo, usa dormant de todas formas
    return DormantSentimentEngine()

def create_trend_miner():
    """Factory para crear Trend Miner"""  
    if EXTENSIONS_AWAKE:
        return DormantTrendMiner()  # En modo demo, usa dormant de todas formas
    return DormantTrendMiner()

def create_growth_simulator():
    """Factory para crear Growth Simulator"""
    if EXTENSIONS_AWAKE:
        return DormantGrowthSimulator()  # En modo demo, usa dormant de todas formas
    return DormantGrowthSimulator()

def create_extensions_dashboard():
    """Factory para crear Dashboard de extensiones"""
    if EXTENSIONS_AWAKE:
        # Crear dashboard funcional con las extensiones disponibles
        return create_demo_dashboard()
    return None

def create_demo_dashboard():
    """Crea un dashboard de demo para las extensiones"""
    try:
        import gradio as gr
        
        def analyze_sentiment_demo(text):
            return {
                "sentiment": "positive" if "good" in text.lower() else "neutral",
                "score": 0.85,
                "topics": ["música", "trap", "urbano"],
                "demo_mode": True
            }
        
        def mine_trends_demo():
            return {
                "trends": [
                    {"platform": "TikTok", "trend": "Reggaeton Remix", "score": 0.92},
                    {"platform": "YouTube", "trend": "Trap Beats", "score": 0.88},
                    {"platform": "Spotify", "trend": "Latin Urban", "score": 0.85}
                ],
                "demo_mode": True
            }
        
        def simulate_growth_demo(budget, platform):
            return {
                "roi_prediction": f"{budget * 2.5:.2f}€",
                "growth_rate": "45%",
                "risk_level": "Bajo",
                "confidence": "85%",
                "demo_mode": True
            }
        
        with gr.Blocks(title="🧠 Neural Forge - Extensions Dashboard") as dashboard:
            gr.Markdown("# 🧠 NEURAL FORGE DISCOGRÁFICA - Extensions Dashboard")
            gr.Markdown("*Versión Demo - Funcionalidad Simulada*")
            
            with gr.Tab("💭 Sentiment Analysis"):
                text_input = gr.Textbox(label="Comentario a analizar")
                sentiment_btn = gr.Button("Analizar Sentimiento")
                sentiment_output = gr.JSON(label="Resultados")
                sentiment_btn.click(analyze_sentiment_demo, inputs=text_input, outputs=sentiment_output)
            
            with gr.Tab("🔥 Trend Mining"):
                trend_btn = gr.Button("Detectar Tendencias")
                trend_output = gr.JSON(label="Tendencias Detectadas")
                trend_btn.click(mine_trends_demo, outputs=trend_output)
            
            with gr.Tab("📈 Growth Simulation"):
                budget_input = gr.Number(label="Presupuesto (€)", value=1000)
                platform_input = gr.Dropdown(["TikTok", "YouTube", "Instagram"], label="Plataforma")
                growth_btn = gr.Button("Simular ROI")
                growth_output = gr.JSON(label="Predicción ROI")
                growth_btn.click(simulate_growth_demo, inputs=[budget_input, platform_input], outputs=growth_output)
        
        return dashboard
        
    except ImportError:
        # Si no hay gradio, retornar dashboard simplificado
        return "Dashboard de extensiones requiere gradio"