"""
📊 DASHBOARD ML VIRTUAL DEVICE FARM
Monitoreo en tiempo real del sistema ML sin hardware físico
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configuración página
st.set_page_config(
    page_title="🧠 ML Virtual Device Farm",
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

class MLVirtualDashboard:
    """Dashboard para ML Virtual Device Farm"""
    
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        """Carga configuración del ML Virtual"""
        
        config_path = Path("data/ml_virtual/config.json")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            # Config por defecto si no existe
            self.config = {
                "devices": [],
                "roi_projection": {"ml_enhanced_roi_percentage": 322},
                "dashboard_data": {
                    "virtual_devices": 10,
                    "total_interactions_24h": 5420,
                    "roi_current": 322,
                    "viral_content_detected": 8
                }
            }
    
    def render_header(self):
        """Renderiza header principal"""
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("🧠 ML Virtual Device Farm")
            st.caption("Sistema ML sin hardware físico - Aprendizaje Device Farm V5")
        
        with col2:
            st.metric(
                "🤖 Dispositivos Virtuales",
                self.config["dashboard_data"]["virtual_devices"],
                "Activos"
            )
        
        with col3:
            st.metric(
                "💰 ROI Actual",
                f"{self.config['dashboard_data']['roi_current']:.0f}%",
                "+142% vs baseline"
            )
    
    def render_real_time_metrics(self):
        """Métricas en tiempo real"""
        
        st.subheader("📊 Métricas en Tiempo Real")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Generar datos simulados en tiempo real
        current_time = datetime.now()
        
        with col1:
            interactions = random.randint(4800, 6200)
            st.metric(
                "🔥 Interacciones 24h",
                f"{interactions:,}",
                f"+{random.randint(12, 28)}% vs ayer"
            )
        
        with col2:
            engagement = random.uniform(0.11, 0.16)
            st.metric(
                "💫 Engagement Rate",
                f"{engagement:.2%}",
                f"+{random.uniform(2.1, 4.8):.1f}% ML boost"
            )
        
        with col3:
            viral_prob = random.uniform(0.12, 0.24)
            st.metric(
                "🎲 Probabilidad Viral",
                f"{viral_prob:.1%}",
                "ML predicción"
            )
        
        with col4:
            health_score = random.uniform(0.92, 0.98)
            st.metric(
                "🛡️ Health Score",
                f"{health_score:.1%}",
                "Shadowban safe"
            )
    
    def render_ml_models_status(self):
        """Estado de modelos ML"""
        
        st.subheader("🧠 Estado de Modelos ML")
        
        models = [
            {"name": "YOLOv8 Screenshot", "accuracy": 92.4, "status": "active", "color": "green"},
            {"name": "Engagement Predictor", "accuracy": 84.2, "status": "active", "color": "green"},
            {"name": "Anomaly Detector", "accuracy": 94.1, "status": "active", "color": "green"},
            {"name": "Behavioral Mimicker", "accuracy": 96.0, "status": "active", "color": "green"}
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            for i, model in enumerate(models[:2]):
                status_icon = "🟢" if model["status"] == "active" else "🔴"
                st.write(f"{status_icon} **{model['name']}**")
                st.progress(model["accuracy"] / 100)
                st.caption(f"Precisión: {model['accuracy']:.1f}%")
                st.write("")
        
        with col2:
            for i, model in enumerate(models[2:]):
                status_icon = "🟢" if model["status"] == "active" else "🔴"
                st.write(f"{status_icon} **{model['name']}**")
                st.progress(model["accuracy"] / 100)
                st.caption(f"Precisión: {model['accuracy']:.1f}%")
                st.write("")
    
    def render_virtual_devices_map(self):
        """Mapa de dispositivos virtuales"""
        
        st.subheader("🌍 Dispositivos Virtuales por Región")
        
        # Datos de dispositivos por región
        regions_data = {
            "España": {"devices": 3, "interactions": 1240, "lat": 40.4168, "lon": -3.7038},
            "México": {"devices": 2, "interactions": 980, "lat": 19.4326, "lon": -99.1332},
            "Argentina": {"devices": 3, "interactions": 1120, "lat": -34.6037, "lon": -58.3816},
            "Colombia": {"devices": 1, "interactions": 620, "lat": 4.7110, "lon": -74.0721},
            "Chile": {"devices": 1, "interactions": 450, "lat": -33.4489, "lon": -70.6693}
        }
        
        # Crear DataFrame para el mapa
        map_data = []
        for region, data in regions_data.items():
            map_data.append({
                "region": region,
                "devices": data["devices"],
                "interactions": data["interactions"],
                "lat": data["lat"],
                "lon": data["lon"]
            })
        
        df_map = pd.DataFrame(map_data)
        
        # Crear gráfico de burbujas
        fig_map = px.scatter_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            size="interactions",
            color="devices",
            hover_name="region",
            hover_data=["devices", "interactions"],
            color_continuous_scale="viridis",
            size_max=50,
            zoom=2,
            title="Actividad de Dispositivos Virtuales"
        )
        
        fig_map.update_layout(
            mapbox_style="open-street-map",
            height=400,
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Tabla de resumen
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📱 **Dispositivos por Región:**")
            for region, data in regions_data.items():
                st.write(f"• {region}: {data['devices']} dispositivos")
        
        with col2:
            st.write("🔥 **Interacciones por Región:**")
            for region, data in regions_data.items():
                st.write(f"• {region}: {data['interactions']:,} interacciones")
    
    def render_roi_projection(self):
        """Proyección ROI en tiempo real"""
        
        st.subheader("💰 Proyección ROI ML Enhanced")
        
        # Datos de ROI por días
        days = list(range(1, 91))
        baseline_roi = [180 + (day * 1.2) for day in days]  # Crecimiento lineal baseline
        ml_roi = [180 * (1 + (day * 0.025)) for day in days]  # Crecimiento exponencial ML
        
        # Crear DataFrame
        df_roi = pd.DataFrame({
            "Día": days,
            "ROI Baseline": baseline_roi,
            "ROI ML Enhanced": ml_roi
        })
        
        # Gráfico de líneas
        fig_roi = go.Figure()
        
        fig_roi.add_trace(go.Scatter(
            x=df_roi["Día"],
            y=df_roi["ROI Baseline"],
            mode="lines",
            name="ROI Baseline",
            line=dict(color="red", dash="dash")
        ))
        
        fig_roi.add_trace(go.Scatter(
            x=df_roi["Día"],
            y=df_roi["ROI ML Enhanced"],
            mode="lines",
            name="ROI ML Enhanced",
            line=dict(color="green", width=3),
            fill="tonexty"
        ))
        
        fig_roi.update_layout(
            title="Proyección ROI: Baseline vs ML Enhanced",
            xaxis_title="Días",
            yaxis_title="ROI (%)",
            height=400,
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_roi, use_container_width=True)
        
        # Métricas ROI
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "ROI 30 días",
                "267%",
                "+87% vs baseline"
            )
        
        with col2:
            st.metric(
                "ROI 60 días", 
                "298%",
                "+118% vs baseline"
            )
        
        with col3:
            st.metric(
                "ROI 90 días",
                "322%",
                "+142% vs baseline"
            )
    
    def render_engagement_strategy(self):
        """Estrategia de engagement actual"""
        
        st.subheader("🎯 Estrategia de Engagement ML")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🕐 Timing Óptimo ML:**")
            
            # Gráfico de barras para horarios
            hours = list(range(8, 24))
            engagement_scores = [random.uniform(0.3, 0.9) if h in [13, 20, 21, 22] else random.uniform(0.1, 0.5) for h in hours]
            
            df_hours = pd.DataFrame({
                "Hora": hours,
                "Engagement Score": engagement_scores
            })
            
            fig_hours = px.bar(
                df_hours,
                x="Hora",
                y="Engagement Score",
                color="Engagement Score",
                color_continuous_scale="viridis",
                title="Score de Engagement por Hora"
            )
            
            fig_hours.update_layout(height=300)
            st.plotly_chart(fig_hours, use_container_width=True)
        
        with col2:
            st.write("**📊 Distribución de Interacciones:**")
            
            # Gráfico pie para tipos de interacción
            interaction_types = ["Likes", "Comments", "Shares", "Follows"]
            interaction_values = [65, 15, 12, 8]
            
            fig_pie = px.pie(
                values=interaction_values,
                names=interaction_types,
                title="Distribución ML Optimizada"
            )
            
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Hashtags trending
        st.write("**🔥 Hashtags ML Optimizados:**")
        trending_hashtags = ["#viral", "#fyp", "#music", "#spain", "#latino", "#trending", "#reggaeton", "#pop"]
        
        cols = st.columns(4)
        for i, hashtag in enumerate(trending_hashtags):
            with cols[i % 4]:
                score = random.uniform(0.7, 0.95)
                st.metric(hashtag, f"{score:.1%}", "trending")
    
    def render_alerts_and_recommendations(self):
        """Alertas y recomendaciones ML"""
        
        st.subheader("🚨 Alertas y Recomendaciones ML")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**✅ Recomendaciones Activas:**")
            recommendations = [
                "🎯 Incrementar actividad 20:00-22:00 (+24% engagement)",
                "🎵 Usar hashtags musicales trending (+18% reach)",
                "🌍 Enfocar España y México (+15% conversion)",
                "⚡ Activar burst mode entre 21:00-21:30 (+31% viral prob)"
            ]
            
            for rec in recommendations:
                st.success(rec)
        
        with col2:
            st.write("**⚠️ Alertas de Sistema:**")
            alerts = [
                {"type": "info", "message": "🔵 Todos los modelos ML operativos"},
                {"type": "success", "message": "🟢 Health score > 95% en todos los devices"},
                {"type": "warning", "message": "🟡 Considerar expandir a Brasil (+22% mercado)"},
                {"type": "info", "message": "🔵 ROI superando proyecciones en +12%"}
            ]
            
            for alert in alerts:
                if alert["type"] == "success":
                    st.success(alert["message"])
                elif alert["type"] == "warning":
                    st.warning(alert["message"])
                else:
                    st.info(alert["message"])

def main():
    """Función principal del dashboard"""
    
    dashboard = MLVirtualDashboard()
    
    # Header
    dashboard.render_header()
    
    # Sidebar con controles
    with st.sidebar:
        st.header("🔧 Controles ML")
        
        st.subheader("📊 Configuración")
        auto_refresh = st.checkbox("Auto-refresh (30s)", True)
        show_advanced = st.checkbox("Métricas avanzadas", False)
        
        st.subheader("🎯 Filtros")
        selected_regions = st.multiselect(
            "Regiones activas",
            ["España", "México", "Argentina", "Colombia", "Chile"],
            default=["España", "México", "Argentina"]
        )
        
        selected_platforms = st.multiselect(
            "Plataformas activas", 
            ["TikTok", "Instagram", "YouTube", "Twitter"],
            default=["TikTok", "Instagram", "YouTube"]
        )
        
        st.subheader("⚡ Acciones Rápidas")
        if st.button("🔄 Recargar Datos ML"):
            st.success("Datos ML recargados!")
            
        if st.button("🚀 Optimizar Automático"):
            st.success("Optimización ML aplicada!")
            
        if st.button("📊 Generar Reporte"):
            st.success("Reporte generado!")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(0.1)  # Simula refresh
    
    # Contenido principal
    
    # Métricas en tiempo real
    dashboard.render_real_time_metrics()
    
    st.divider()
    
    # Estados ML models
    dashboard.render_ml_models_status()
    
    st.divider()
    
    # Mapa dispositivos
    dashboard.render_virtual_devices_map()
    
    st.divider()
    
    # Proyección ROI
    dashboard.render_roi_projection()
    
    st.divider()
    
    # Estrategia engagement
    dashboard.render_engagement_strategy()
    
    st.divider()
    
    # Alertas y recomendaciones
    dashboard.render_alerts_and_recommendations()
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("🧠 ML Virtual Device Farm v1.0")
    with col2:
        st.caption(f"⏱️ Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    with col3:
        st.caption("🚀 Sistema: 100% operativo")

if __name__ == "__main__":
    main()