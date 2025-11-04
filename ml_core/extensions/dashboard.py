"""
🎛️ DASHBOARD GRADIO PARA EXTENSIONES AVANZADAS

Interface visual para las tres extensiones:
- Feedback Sentiment Engine
- Cultural Trend Miner
- Network Growth Simulator
"""

import gradio as gr
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from ml_core.extensions import (
    create_sentiment_engine,
    create_trend_miner,
    create_growth_simulator
)
from ml_core.extensions.growth_simulator import (
    SimulationScenario,
    Platform,
    CampaignObjective
)
from ml_core.extensions.trend_miner import TrendPhase

logger = logging.getLogger(__name__)

class ExtensionsDashboard:
    """Dashboard principal para extensiones avanzadas"""
    
    def __init__(self):
        self.sentiment_engine = None
        self.trend_miner = None 
        self.growth_simulator = None
        self.initialized = False
        
    async def initialize(self):
        """Inicializa las extensiones"""
        try:
            logger.info("🚀 Inicializando dashboard de extensiones...")
            
            self.sentiment_engine = create_sentiment_engine()
            await self.sentiment_engine.initialize()
            
            self.trend_miner = create_trend_miner()
            await self.trend_miner.initialize()
            
            self.growth_simulator = create_growth_simulator()
            await self.growth_simulator.initialize()
            
            self.initialized = True
            logger.info("✅ Dashboard inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando dashboard: {e}")
            self.initialized = False

    # === SENTIMENT ANALYSIS INTERFACE ===
    
    async def analyze_video_sentiment_ui(self, video_id: str, platform: str, max_comments: int):
        """UI para análisis de sentimientos"""
        if not self.initialized:
            return "❌ Extensiones no inicializadas", None, None
        
        try:
            # Validar inputs
            if not video_id.strip():
                return "❌ Ingresa un ID de video válido", None, None
            
            if max_comments < 50 or max_comments > 2000:
                return "❌ Número de comentarios debe estar entre 50 y 2000", None, None
            
            # Ejecutar análisis
            summary = await self.sentiment_engine.analyze_video_feedback(
                video_id=video_id.strip(),
                platform=platform.lower(),
                max_comments=max_comments
            )
            
            if not summary:
                return "❌ No se pudo analizar el video (posiblemente sin comentarios)", None, None
            
            # Crear visualizaciones
            sentiment_chart = self._create_sentiment_chart(summary)
            emotion_chart = self._create_emotion_chart(summary)
            
            # Generar reporte de texto
            report = f"""
            📊 **ANÁLISIS COMPLETADO**
            
            **Video:** {video_id} ({platform})
            **Comentarios totales:** {summary.total_comments}
            **Comentarios orgánicos:** {summary.organic_comments}
            
            **📈 Distribución de Sentimientos:**
            • Positivo: {summary.sentiment_distribution.get('positive', 0):.1%}
            • Negativo: {summary.sentiment_distribution.get('negative', 0):.1%}
            • Neutral: {summary.sentiment_distribution.get('neutral', 0):.1%}
            
            **💭 Temas Principales:**
            {self._format_topics(summary.dominant_topics)}
            
            **🔑 Keywords Relevantes:**
            {self._format_keywords(summary.top_keywords)}
            
            **🎯 RECOMENDACIÓN:**
            {summary.recommendation}
            
            **📊 Correlación Engagement-Sentimiento:** {summary.engagement_sentiment_correlation:.2f}
            """
            
            return report, sentiment_chart, emotion_chart
            
        except Exception as e:
            logger.error(f"Error en análisis de sentimientos UI: {e}")
            return f"❌ Error: {str(e)}", None, None

    def _create_sentiment_chart(self, summary):
        """Crea gráfico de distribución de sentimientos"""
        sentiments = list(summary.sentiment_distribution.keys())
        values = list(summary.sentiment_distribution.values())
        
        colors = {'positive': '#4CAF50', 'negative': '#F44336', 'neutral': '#FFC107'}
        chart_colors = [colors.get(s, '#9E9E9E') for s in sentiments]
        
        fig = px.pie(
            values=values,
            names=sentiments,
            title="Distribución de Sentimientos",
            color_discrete_sequence=chart_colors
        )
        
        fig.update_layout(
            height=400,
            font=dict(size=14),
            showlegend=True
        )
        
        return fig

    def _create_emotion_chart(self, summary):
        """Crea gráfico de distribución emocional"""
        emotions = list(summary.emotion_distribution.keys())
        values = list(summary.emotion_distribution.values())
        
        fig = px.bar(
            x=emotions,
            y=values,
            title="Distribución Emocional",
            labels={'x': 'Emociones', 'y': 'Proporción'},
            color=values,
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Emociones",
            yaxis_title="Proporción",
            showlegend=False
        )
        
        return fig

    def _format_topics(self, topics: List[Tuple[str, float]]) -> str:
        """Formatea temas dominantes"""
        if not topics:
            return "• No se detectaron temas específicos"
        
        formatted = []
        for i, (topic, score) in enumerate(topics[:5]):
            formatted.append(f"• {topic} ({score} menciones)")
        
        return "\n".join(formatted)

    def _format_keywords(self, keywords: List[Tuple[str, int]]) -> str:
        """Formatea keywords relevantes"""
        if not keywords:
            return "• No se detectaron keywords específicas"
        
        formatted = []
        for keyword, count in keywords[:10]:
            formatted.append(f"• {keyword} ({count}x)")
        
        return "\n".join(formatted)

    # === TREND MINING INTERFACE ===
    
    async def mine_trends_ui(self, platforms_str: str, artist_genres: str, artist_keywords: str):
        """UI para minería de tendencias"""
        if not self.initialized:
            return "❌ Extensiones no inicializadas", None
        
        try:
            # Parsear inputs
            platforms = [p.strip().lower() for p in platforms_str.split(",") if p.strip()]
            if not platforms:
                platforms = ["tiktok", "youtube", "spotify"]
            
            # Crear perfil del artista
            artist_profile = {}
            if artist_genres.strip():
                artist_profile['genres'] = [g.strip() for g in artist_genres.split(",")]
            if artist_keywords.strip():
                artist_profile['keywords'] = [k.strip() for k in artist_keywords.split(",")]
            
            # Ejecutar minería
            mining_result = await self.trend_miner.mine_daily_trends()
            
            # Obtener tendencias relevantes para el artista
            relevant_trends = []
            if artist_profile:
                relevant_trends = await self.trend_miner.get_artist_relevant_trends(
                    artist_profile=artist_profile,
                    max_trends=15
                )
            
            # Crear visualización
            trends_chart = self._create_trends_chart(mining_result, relevant_trends)
            
            # Generar reporte
            report = f"""
            🔥 **TENDENCIAS DETECTADAS**
            
            **Timestamp:** {mining_result['timestamp'].strftime('%Y-%m-%d %H:%M')}
            **Tendencias totales:** {mining_result['merged_trends_count']}
            
            **📈 Por Plataforma:**
            {self._format_platform_stats(mining_result['trends_by_platform'])}
            
            **🚀 Top Tendencias Emergentes:**
            {self._format_emerging_trends(mining_result.get('top_emerging', []))}
            
            **🎯 Relevantes para tu Artista:**
            {self._format_relevant_trends(relevant_trends)}
            
            **📊 Estadísticas de Minería:**
            • Emergentes: {mining_result['stats'].get('emerging_count', 0)}
            • En crecimiento: {mining_result['stats'].get('growing_count', 0)}
            • En pico: {mining_result['stats'].get('peak_count', 0)}
            • Confianza promedio: {mining_result['stats'].get('avg_confidence', 0):.2f}
            """
            
            return report, trends_chart
            
        except Exception as e:
            logger.error(f"Error en minería de tendencias UI: {e}")
            return f"❌ Error: {str(e)}", None

    def _create_trends_chart(self, mining_result, relevant_trends):
        """Crea gráfico de tendencias"""
        # Datos para el gráfico
        platform_data = mining_result['trends_by_platform']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Tendencias por Plataforma", "Fases de Tendencias", 
                          "Top Keywords", "Relevantes para Artista"),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico 1: Tendencias por plataforma
        platforms = list(platform_data.keys())
        counts = list(platform_data.values())
        
        fig.add_trace(
            go.Bar(x=platforms, y=counts, name="Tendencias", marker_color='lightblue'),
            row=1, col=1
        )
        
        # Gráfico 2: Distribución de fases
        stats = mining_result['stats']
        phases = ['Emergente', 'Creciendo', 'Pico']
        phase_counts = [
            stats.get('emerging_count', 0),
            stats.get('growing_count', 0), 
            stats.get('peak_count', 0)
        ]
        
        fig.add_trace(
            go.Pie(labels=phases, values=phase_counts, name="Fases"),
            row=1, col=2
        )
        
        # Gráfico 3: Top keywords
        top_keywords = stats.get('top_keywords', [])[:8]
        if top_keywords:
            fig.add_trace(
                go.Bar(x=top_keywords, y=[1]*len(top_keywords), name="Keywords", 
                      marker_color='lightgreen'),
                row=2, col=1
            )
        
        # Gráfico 4: Tendencias relevantes para artista
        if relevant_trends:
            rel_keywords = [t.keyword for t in relevant_trends[:8]]
            rel_scores = [t.confidence_score for t in relevant_trends[:8]]
            
            fig.add_trace(
                go.Bar(x=rel_keywords, y=rel_scores, name="Relevancia", 
                      marker_color='orange'),
                row=2, col=2
            )
        
        fig.update_layout(height=800, showlegend=False, title_text="Dashboard de Tendencias")
        return fig

    def _format_platform_stats(self, platform_stats: Dict) -> str:
        """Formatea estadísticas por plataforma"""
        formatted = []
        for platform, count in platform_stats.items():
            formatted.append(f"• {platform.upper()}: {count} tendencias")
        return "\n".join(formatted)

    def _format_emerging_trends(self, emerging_trends: List) -> str:
        """Formatea tendencias emergentes"""
        if not emerging_trends:
            return "• No hay tendencias emergentes detectadas"
        
        formatted = []
        for trend in emerging_trends[:8]:
            keyword = trend.keyword if hasattr(trend, 'keyword') else 'N/A'
            platform = trend.platform if hasattr(trend, 'platform') else 'N/A'
            growth = trend.growth_rate if hasattr(trend, 'growth_rate') else 0
            formatted.append(f"• {keyword} ({platform}) - {growth:.0f}% crecimiento")
        
        return "\n".join(formatted)

    def _format_relevant_trends(self, relevant_trends: List) -> str:
        """Formatea tendencias relevantes para el artista"""
        if not relevant_trends:
            return "• No se encontraron tendencias específicamente relevantes"
        
        formatted = []
        for trend in relevant_trends[:6]:
            formatted.append(f"• {trend.keyword} ({trend.platform}) - Relevancia: {trend.confidence_score:.2f}")
        
        return "\n".join(formatted)

    # === GROWTH SIMULATION INTERFACE ===
    
    async def simulate_growth_ui(self, budget: float, platform: str, duration: int, 
                               content_type: str, optimization: bool):
        """UI para simulación de crecimiento"""
        if not self.initialized:
            return "❌ Extensiones no inicializadas", None, None
        
        try:
            # Validar inputs
            if budget <= 0 or budget > 10000:
                return "❌ Presupuesto debe estar entre €1 y €10,000", None, None
            
            if duration < 1 or duration > 60:
                return "❌ Duración debe estar entre 1 y 60 días", None, None
            
            # Crear escenario
            scenario = SimulationScenario(
                scenario_id=f"ui_scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                budget_eur=budget,
                platform=Platform(platform.lower()),
                objective=CampaignObjective.VIEWS,
                duration_days=duration,
                content_type=content_type.lower(),
                timing={"day_of_week": 5, "hour": 20}  # Default: Friday 8PM
            )
            
            # Ejecutar simulación
            results = await self.growth_simulator.simulate_campaign_scenarios([scenario])
            
            if not results:
                return "❌ No se pudo completar la simulación", None, None
            
            result = results[0]
            
            # Optimización opcional
            optimization_result = None
            if optimization:
                try:
                    optimization_result = await self.growth_simulator.optimize_campaign_strategy(scenario)
                except Exception as e:
                    logger.warning(f"Error en optimización: {e}")
            
            # Comparación de plataformas
            platform_comparison = await self.growth_simulator.compare_platform_strategies(scenario)
            
            # Crear visualizaciones
            roi_chart = self._create_roi_simulation_chart(result)
            platform_chart = self._create_platform_comparison_chart(platform_comparison)
            
            # Generar reporte
            report = f"""
            📈 **SIMULACIÓN DE CRECIMIENTO**
            
            **Escenario:** €{budget} en {platform} por {duration} días
            
            **🎯 Predicciones:**
            • ROI: {result.predicted_roi_percentage:.1f}%
            • Views: {result.predicted_views:,.0f}
            • Followers: {result.predicted_followers:.0f}
            • Costo por view: €{result.predicted_cost_per_view:.4f}
            
            **📊 Intervalos de Confianza (90%):**
            • ROI: {result.roi_ci_lower:.1f}% - {result.roi_ci_upper:.1f}%
            • Views: {result.views_ci_lower:,.0f} - {result.views_ci_upper:,.0f}
            
            **⚡ Análisis de Riesgo:**
            • Probabilidad ROI positivo: {result.probability_positive_roi:.1%}
            • Probabilidad superar target: {result.probability_exceeds_target:.1%}
            • Confianza simulación: {result.simulation_confidence:.1%}
            • Break-even estimado: {result.break_even_point_days:.1f} días
            
            **🎯 Optimización:**
            {self._format_optimization_result(optimization_result)}
            
            **🏆 Mejor Plataforma Alternativa:**
            {self._format_platform_recommendation(platform_comparison, platform)}
            """
            
            return report, roi_chart, platform_chart
            
        except Exception as e:
            logger.error(f"Error en simulación de crecimiento UI: {e}")
            return f"❌ Error: {str(e)}", None, None

    def _create_roi_simulation_chart(self, result):
        """Crea gráfico de simulación ROI"""
        # Simular distribución de ROI para visualización
        import numpy as np
        
        # Generar distribución normal basada en intervalos de confianza
        mean_roi = result.predicted_roi_percentage
        std_roi = (result.roi_ci_upper - result.roi_ci_lower) / 4  # Aproximación
        
        roi_distribution = np.random.normal(mean_roi, std_roi, 1000)
        
        fig = go.Figure()
        
        # Histograma de distribución ROI
        fig.add_trace(go.Histogram(
            x=roi_distribution,
            name="Distribución ROI",
            nbinsx=50,
            opacity=0.7,
            marker_color='lightblue'
        ))
        
        # Líneas de referencia
        fig.add_vline(x=mean_roi, line_dash="dash", line_color="red", 
                     annotation_text=f"ROI Predicho: {mean_roi:.1f}%")
        fig.add_vline(x=0, line_dash="dot", line_color="black", 
                     annotation_text="Break-even")
        
        fig.update_layout(
            title="Distribución de ROI - Simulación Monte Carlo",
            xaxis_title="ROI (%)",
            yaxis_title="Frecuencia",
            height=400
        )
        
        return fig

    def _create_platform_comparison_chart(self, platform_comparison):
        """Crea gráfico de comparación entre plataformas"""
        if not platform_comparison:
            return go.Figure().add_annotation(text="No hay datos de comparación", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        platforms = []
        roi_values = []
        views_values = []
        confidence_values = []
        
        for platform, result in platform_comparison.items():
            platforms.append(platform.value.upper())
            roi_values.append(result.predicted_roi_percentage)
            views_values.append(result.predicted_views)
            confidence_values.append(result.simulation_confidence)
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=("ROI por Plataforma", "Views Predichos", "Confianza"),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
        )
        
        # ROI por plataforma
        fig.add_trace(
            go.Bar(x=platforms, y=roi_values, name="ROI", marker_color='lightgreen'),
            row=1, col=1
        )
        
        # Views predichos
        fig.add_trace(
            go.Bar(x=platforms, y=views_values, name="Views", marker_color='lightblue'),
            row=1, col=2
        )
        
        # Confianza
        fig.add_trace(
            go.Bar(x=platforms, y=confidence_values, name="Confianza", marker_color='orange'),
            row=1, col=3
        )
        
        fig.update_layout(height=400, showlegend=False, title_text="Comparación entre Plataformas")
        return fig

    def _format_optimization_result(self, optimization_result) -> str:
        """Formatea resultado de optimización"""
        if not optimization_result:
            return "• No se ejecutó optimización"
        
        return f"""• Acción recomendada: {optimization_result.action_type}
        • Mejora esperada: {optimization_result.expected_improvement:.1f}%
        • Confianza: {optimization_result.confidence_score:.1%}
        • Reasoning: {optimization_result.reasoning}"""

    def _format_platform_recommendation(self, platform_comparison, current_platform) -> str:
        """Formatea recomendación de plataforma"""
        if not platform_comparison:
            return "• No hay datos de comparación disponibles"
        
        # Encontrar mejor plataforma alternativa
        best_alternative = None
        best_roi = -float('inf')
        
        for platform, result in platform_comparison.items():
            if platform.value != current_platform and result.predicted_roi_percentage > best_roi:
                best_roi = result.predicted_roi_percentage
                best_alternative = platform.value
        
        if best_alternative:
            current_roi = platform_comparison[Platform(current_platform)].predicted_roi_percentage
            improvement = best_roi - current_roi
            if improvement > 5:  # Solo recomendar si mejora >5%
                return f"• {best_alternative.upper()} podría generar {improvement:+.1f}% más ROI"
        
        return f"• {current_platform.upper()} parece ser la mejor opción actual"


def create_extensions_dashboard():
    """Crea dashboard Gradio para extensiones"""
    
    dashboard = ExtensionsDashboard()
    
    # Inicializar en background
    async def init_dashboard():
        await dashboard.initialize()
    
    # Ejecutar inicialización
    import threading
    def run_init():
        asyncio.run(init_dashboard())
    
    init_thread = threading.Thread(target=run_init)
    init_thread.daemon = True
    init_thread.start()
    
    # === CREAR INTERFACES ===
    
    with gr.Blocks(title="🧠 Extensiones Avanzadas - Dashboard", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("# 🧠 **EXTENSIONES AVANZADAS - DASHBOARD**")
        gr.Markdown("*Feedback Sentiment Engine | Cultural Trend Miner | Network Growth Simulator*")
        
        with gr.Tabs():
            
            # TAB 1: SENTIMENT ANALYSIS
            with gr.TabItem("💭 Análisis de Sentimientos"):
                gr.Markdown("## 🧠 Feedback Sentiment Engine")
                gr.Markdown("Analiza comentarios de videos para entender la recepción del público")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        video_id_input = gr.Textbox(
                            label="ID del Video",
                            placeholder="ej: dQw4w9WgXcQ (YouTube) o @usuario/video/123 (TikTok)",
                            info="ID o URL del video a analizar"
                        )
                        platform_input = gr.Dropdown(
                            choices=["youtube", "tiktok", "instagram"],
                            value="youtube",
                            label="Plataforma"
                        )
                        max_comments_input = gr.Slider(
                            minimum=50,
                            maximum=2000,
                            value=500,
                            step=50,
                            label="Máximo Comentarios"
                        )
                        analyze_btn = gr.Button("🔍 Analizar Sentimientos", variant="primary")
                    
                    with gr.Column(scale=2):
                        sentiment_report = gr.Markdown(value="Haz clic en 'Analizar Sentimientos' para comenzar")
                
                with gr.Row():
                    sentiment_chart = gr.Plot(label="Distribución de Sentimientos")
                    emotion_chart = gr.Plot(label="Distribución Emocional")
                
                # Event handler
                async def analyze_sentiment_handler(video_id, platform, max_comments):
                    return await dashboard.analyze_video_sentiment_ui(video_id, platform, max_comments)
                
                analyze_btn.click(
                    fn=analyze_sentiment_handler,
                    inputs=[video_id_input, platform_input, max_comments_input],
                    outputs=[sentiment_report, sentiment_chart, emotion_chart]
                )
            
            # TAB 2: TREND MINING
            with gr.TabItem("🔥 Detección de Tendencias"):
                gr.Markdown("## ⛏️ Cultural Trend Miner")
                gr.Markdown("Detecta microtendencias emergentes en tiempo real")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        platforms_input = gr.Textbox(
                            label="Plataformas",
                            value="tiktok, youtube, spotify",
                            placeholder="Separadas por comas",
                            info="Plataformas a analizar"
                        )
                        artist_genres_input = gr.Textbox(
                            label="Géneros del Artista",
                            placeholder="trap, drill, reggaeton",
                            info="Para filtrar tendencias relevantes"
                        )
                        artist_keywords_input = gr.Textbox(
                            label="Keywords del Artista",
                            placeholder="beat, freestyle, cypher",
                            info="Palabras clave asociadas al artista"
                        )
                        mine_trends_btn = gr.Button("⛏️ Minar Tendencias", variant="primary")
                    
                    with gr.Column(scale=2):
                        trends_report = gr.Markdown(value="Haz clic en 'Minar Tendencias' para comenzar")
                
                trends_chart = gr.Plot(label="Dashboard de Tendencias")
                
                # Event handler
                async def mine_trends_handler(platforms_str, artist_genres, artist_keywords):
                    return await dashboard.mine_trends_ui(platforms_str, artist_genres, artist_keywords)
                
                mine_trends_btn.click(
                    fn=mine_trends_handler,
                    inputs=[platforms_input, artist_genres_input, artist_keywords_input],
                    outputs=[trends_report, trends_chart]
                )
            
            # TAB 3: GROWTH SIMULATION
            with gr.TabItem("📈 Simulación de Crecimiento"):
                gr.Markdown("## 🎲 Network Growth Simulator") 
                gr.Markdown("Simula escenarios de crecimiento y predice ROI")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        budget_input = gr.Number(
                            label="Presupuesto (€)",
                            value=500,
                            minimum=1,
                            maximum=10000,
                            info="Presupuesto total de la campaña"
                        )
                        platform_sim_input = gr.Dropdown(
                            choices=["youtube", "instagram", "tiktok", "spotify", "facebook"],
                            value="instagram",
                            label="Plataforma"
                        )
                        duration_input = gr.Slider(
                            minimum=1,
                            maximum=60,
                            value=7,
                            step=1,
                            label="Duración (días)"
                        )
                        content_type_input = gr.Dropdown(
                            choices=["video", "image", "story", "reel", "carousel"],
                            value="video",
                            label="Tipo de Contenido"
                        )
                        optimization_input = gr.Checkbox(
                            label="Aplicar Optimización Q-Learning",
                            value=True,
                            info="Usa IA para optimizar la estrategia"
                        )
                        simulate_btn = gr.Button("🎲 Simular Crecimiento", variant="primary")
                    
                    with gr.Column(scale=2):
                        simulation_report = gr.Markdown(value="Haz clic en 'Simular Crecimiento' para comenzar")
                
                with gr.Row():
                    roi_chart = gr.Plot(label="Distribución de ROI")
                    platform_comparison_chart = gr.Plot(label="Comparación de Plataformas")
                
                # Event handler
                async def simulate_growth_handler(budget, platform, duration, content_type, optimization):
                    return await dashboard.simulate_growth_ui(budget, platform, duration, content_type, optimization)
                
                simulate_btn.click(
                    fn=simulate_growth_handler,
                    inputs=[budget_input, platform_sim_input, duration_input, content_type_input, optimization_input],
                    outputs=[simulation_report, roi_chart, platform_comparison_chart]
                )
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("*🧠 Powered by Advanced ML Extensions - Discográfica System*")
    
    return demo

# Export
extensions_dashboard = create_extensions_dashboard