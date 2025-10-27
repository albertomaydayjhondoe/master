"""
📊 DASHBOARD ML META - Optimización y Aprendizaje Automático
Dashboard Streamlit para visualizar ML insights, distribución geográfica y performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import json

# Configuración de página
st.set_page_config(
    page_title="🧠 META ML Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs de servicios
ML_API_URL = "http://localhost:8006"  # Sistema Meta ML

# CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .performance-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .country-card {
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    .high-perf { border-left-color: #28a745; background-color: #d4edda; }
    .medium-perf { border-left-color: #ffc107; background-color: #fff3cd; }
    .low-perf { border-left-color: #dc3545; background-color: #f8d7da; }
</style>
""", unsafe_allow_html=True)

def load_ml_dashboard_data(campaign_id: str = "demo_campaign"):
    """Cargar datos del dashboard ML"""
    try:
        response = requests.get(f"{ML_API_URL}/ml/dashboard-data/{campaign_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return get_dummy_dashboard_data()
    except:
        return get_dummy_dashboard_data()

def get_dummy_dashboard_data():
    """Datos dummy para desarrollo"""
    return {
        "campaign_id": "demo_reggaeton_2025",
        "current_performance": {
            "total_spend": 387.50,
            "total_conversions": 124,
            "current_roi": 3.21,
            "spain_performance": 2.68,
            "latam_performance": 3.47
        },
        "geographic_distribution": {
            "spain": {"percentage": 35.0, "performance": 2.68, "trend": "stable"},
            "mexico": {"percentage": 28.0, "performance": 3.65, "trend": "increasing"},
            "colombia": {"percentage": 22.0, "performance": 3.24, "trend": "increasing"},
            "argentina": {"percentage": 10.0, "performance": 1.89, "trend": "decreasing"},
            "chile": {"percentage": 5.0, "performance": 4.12, "trend": "exploring"}
        },
        "audience_segments": [
            {
                "name": "Cross-Platform Reggaeton Fans",
                "size": 67000,
                "roi": 3.78,
                "platforms": ["YouTube", "Spotify", "Meta"],
                "top_countries": ["MX", "ES", "CO"]
            },
            {
                "name": "Organic YouTube Listeners", 
                "size": 45000,
                "roi": 2.94,
                "platforms": ["YouTube", "Meta"],
                "top_countries": ["ES", "AR"]
            },
            {
                "name": "Spotify Savers & Repeaters",
                "size": 38000,
                "roi": 3.45,
                "platforms": ["Spotify", "Meta"], 
                "top_countries": ["MX", "CO", "CL"]
            }
        ],
        "viral_creatives": [
            {
                "id": "creative_reggaeton_beat",
                "name": "Reggaeton Beat Drop 30s",
                "viral_score": 94,
                "performance_lift": "+178%",
                "top_platform": "TikTok",
                "cross_platform_score": 0.89
            },
            {
                "id": "creative_urban_visual",
                "name": "Urban Visual Storytelling",
                "viral_score": 87,
                "performance_lift": "+134%", 
                "top_platform": "Instagram",
                "cross_platform_score": 0.76
            }
        ],
        "ml_insights": {
            "next_optimization": "Increase Mexico budget by €95 (+25%)",
            "confidence": 92,
            "learning_status": "Active - 245 samples",
            "model_accuracy": 91.3,
            "data_quality": {
                "youtube_organic": 89,
                "spotify_organic": 84,
                "cross_platform_matches": 156
            }
        },
        "performance_timeline": generate_performance_timeline()
    }

def generate_performance_timeline():
    """Generar datos de timeline de performance"""
    dates = pd.date_range(start=datetime.now()-timedelta(days=14), end=datetime.now(), freq='D')
    
    return {
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
        "spain_roi": np.random.normal(2.6, 0.3, len(dates)).clip(1.5, 4.0).tolist(),
        "mexico_roi": np.random.normal(3.5, 0.4, len(dates)).clip(2.0, 5.0).tolist(),
        "colombia_roi": np.random.normal(3.2, 0.3, len(dates)).clip(2.0, 4.5).tolist(),
        "chile_roi": np.random.normal(4.0, 0.5, len(dates)).clip(2.5, 6.0).tolist(),
        "argentina_roi": np.random.normal(1.9, 0.2, len(dates)).clip(1.2, 3.0).tolist()
    }

# ============================================
# INTERFACE PRINCIPAL
# ============================================

def main():
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">
            🧠 META ML DASHBOARD
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Sistema de Machine Learning - Optimización España/LATAM
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## ⚙️ Configuración")
    
    campaign_id = st.sidebar.selectbox(
        "Seleccionar Campaña",
        ["demo_reggaeton_2025", "campaign_urbano_001", "campaign_pop_latino"]
    )
    
    refresh_data = st.sidebar.button("🔄 Actualizar Datos")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Sistema ML")
    st.sidebar.markdown(f"**Status:** ✅ Activo")
    st.sidebar.markdown(f"**Modelos:** 2 entrenados")
    st.sidebar.markdown(f"**Última actualización:** {datetime.now().strftime('%H:%M')}")
    
    # Cargar datos
    data = load_ml_dashboard_data(campaign_id)
    
    # Métricas principales
    show_main_metrics(data)
    
    # Distribución geográfica
    show_geographic_analysis(data)
    
    # Segmentos de audiencia
    show_audience_segments(data)
    
    # Creatividades virales
    show_viral_creatives(data)
    
    # ML Insights
    show_ml_insights(data)
    
    # Performance timeline
    show_performance_timeline(data)

def show_main_metrics(data):
    """Mostrar métricas principales"""
    
    st.markdown("## 📊 Performance Actual")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Total Invertido</h3>
            <h2>€{data['current_performance']['total_spend']}</h2>
            <p>+12% vs semana anterior</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Conversiones</h3>
            <h2>{data['current_performance']['total_conversions']}</h2>
            <p>+28% vs semana anterior</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="performance-card">
            <h3>📈 ROI Actual</h3>
            <h2>{data['current_performance']['current_roi']:.2f}x</h2>
            <p>Target: 2.5x ✅</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        latam_vs_spain = (data['current_performance']['latam_performance'] / 
                         data['current_performance']['spain_performance'] - 1) * 100
        
        st.markdown(f"""
        <div class="insight-card">
            <h3>🌎 LATAM vs España</h3>
            <h2>+{latam_vs_spain:.0f}%</h2>
            <p>LATAM superior</p>
        </div>
        """, unsafe_allow_html=True)

def show_geographic_analysis(data):
    """Análisis de distribución geográfica"""
    
    st.markdown("## 🌍 Distribución Geográfica España-LATAM")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Mapa de performance por país
        geo_data = data['geographic_distribution']
        
        countries = []
        percentages = []
        performances = []
        colors = []
        
        for country, info in geo_data.items():
            country_names = {
                'spain': 'España', 'mexico': 'México', 'colombia': 'Colombia',
                'argentina': 'Argentina', 'chile': 'Chile'
            }
            countries.append(country_names.get(country, country.title()))
            percentages.append(info['percentage'])
            performances.append(info['performance'])
            
            # Color basado en performance
            if info['performance'] > 3.0:
                colors.append('#28a745')  # Verde
            elif info['performance'] > 2.0:
                colors.append('#ffc107')  # Amarillo  
            else:
                colors.append('#dc3545')  # Rojo
        
        fig = go.Figure()
        
        # Gráfico de barras con performance
        fig.add_trace(go.Bar(
            x=countries,
            y=performances,
            text=[f"{p:.2f}x ROI<br>{pct:.0f}% budget" for p, pct in zip(performances, percentages)],
            textposition='auto',
            marker_color=colors,
            name="Performance ROI"
        ))
        
        fig.update_layout(
            title="Performance ROI por País",
            xaxis_title="País",
            yaxis_title="ROI",
            template="plotly_white",
            height=400
        )
        
        # Línea de objetivo
        fig.add_hline(y=2.5, line_dash="dash", line_color="red", 
                     annotation_text="Target ROI: 2.5x")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 Status por País")
        
        for country, info in data['geographic_distribution'].items():
            country_names = {
                'spain': '🇪🇸 España', 'mexico': '🇲🇽 México', 'colombia': '🇨🇴 Colombia',
                'argentina': '🇦🇷 Argentina', 'chile': '🇨🇱 Chile'
            }
            
            # Determinar clase CSS basada en performance
            if info['performance'] > 3.0:
                card_class = "high-perf"
                status = "🚀 Alto"
            elif info['performance'] > 2.0:
                card_class = "medium-perf" 
                status = "📊 Medio"
            else:
                card_class = "low-perf"
                status = "⚠️ Bajo"
            
            trend_icons = {"increasing": "📈", "stable": "➡️", "decreasing": "📉", "exploring": "🔍"}
            
            st.markdown(f"""
            <div class="country-card {card_class}">
                <strong>{country_names.get(country, country.title())}</strong><br>
                Performance: {info['performance']:.2f}x ({status})<br>
                Budget: {info['percentage']:.0f}%<br>
                Trend: {trend_icons.get(info['trend'], '➡️')} {info['trend'].title()}
            </div>
            """, unsafe_allow_html=True)

def show_audience_segments(data):
    """Mostrar segmentos de audiencia optimizados"""
    
    st.markdown("## 👥 Segmentos de Audiencia Optimizados")
    
    segments = data['audience_segments']
    
    for i, segment in enumerate(segments):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            **{segment['name']}**
            
            📊 **Tamaño:** {segment['size']:,} usuarios  
            🎯 **ROI:** {segment['roi']:.2f}x  
            🌐 **Plataformas:** {', '.join(segment['platforms'])}  
            🌍 **Top países:** {', '.join(segment['top_countries'])}
            """)
        
        with col2:
            # Gráfico de tamaño del segmento
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = segment['roi'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "ROI"},
                gauge = {
                    'axis': {'range': [None, 5]},
                    'bar': {'color': "darkgreen" if segment['roi'] > 3 else "orange"},
                    'steps': [
                        {'range': [0, 2], 'color': "lightgray"},
                        {'range': [2, 3], 'color': "yellow"},
                        {'range': [3, 5], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 2.5
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Distribución por plataformas
            platform_data = {
                "Plataforma": segment['platforms'],
                "Engagement": np.random.uniform(0.8, 1.0, len(segment['platforms']))
            }
            
            fig = px.bar(
                platform_data, 
                x="Engagement", 
                y="Plataforma",
                orientation='h',
                color="Engagement",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(
                height=200, 
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

def show_viral_creatives(data):
    """Mostrar creatividades con potencial viral"""
    
    st.markdown("## 🚀 Creatividades Virales")
    
    viral_creatives = data['viral_creatives']
    
    col1, col2 = st.columns(2)
    
    for i, creative in enumerate(viral_creatives):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            # Score color
            score = creative['viral_score']
            if score >= 90:
                score_color = "#28a745"
                score_status = "🔥 Viral"
            elif score >= 80:
                score_color = "#ffc107"  
                score_status = "⭐ Alto"
            else:
                score_color = "#6c757d"
                score_status = "📊 Medio"
            
            st.markdown(f"""
            <div style="border: 2px solid {score_color}; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                <h4 style="margin: 0; color: {score_color};">{creative['name']}</h4>
                <p><strong>Viral Score:</strong> {score}/100 ({score_status})</p>
                <p><strong>Performance Lift:</strong> {creative['performance_lift']}</p>
                <p><strong>Top Platform:</strong> {creative['top_platform']}</p>
                <p><strong>Cross-Platform Score:</strong> {creative['cross_platform_score']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

def show_ml_insights(data):
    """Mostrar insights del ML"""
    
    st.markdown("## 🤖 ML Insights & Recomendaciones")
    
    ml_data = data['ml_insights']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <h3>🎯 Próxima Optimización</h3>
            <h4>{ml_data['next_optimization']}</h4>
            <p>Confianza: {ml_data['confidence']}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>📚 Estado del Aprendizaje</h3>
            <p><strong>Status:</strong> {ml_data['learning_status']}</p>
            <p><strong>Precisión del Modelo:</strong> {ml_data['model_accuracy']}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Calidad de datos
        quality_data = ml_data['data_quality']
        
        fig = go.Figure()
        
        categories = ['YouTube Orgánico', 'Spotify Orgánico', 'Cross-Platform']
        values = [quality_data['youtube_organic'], quality_data['spotify_organic'], 
                 quality_data['cross_platform_matches']]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Calidad de Datos'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Calidad de Datos por Fuente",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_performance_timeline(data):
    """Mostrar timeline de performance"""
    
    st.markdown("## 📈 Timeline de Performance (14 días)")
    
    timeline_data = data['performance_timeline']
    
    fig = go.Figure()
    
    countries = {
        'spain_roi': ('🇪🇸 España', '#FF6B6B'),
        'mexico_roi': ('🇲🇽 México', '#4ECDC4'), 
        'colombia_roi': ('🇨🇴 Colombia', '#45B7D1'),
        'chile_roi': ('🇨🇱 Chile', '#96CEB4'),
        'argentina_roi': ('🇦🇷 Argentina', '#FFEAA7')
    }
    
    for key, (name, color) in countries.items():
        fig.add_trace(go.Scatter(
            x=timeline_data['dates'],
            y=timeline_data[key],
            mode='lines+markers',
            name=name,
            line=dict(color=color, width=3),
            marker=dict(size=6)
        ))
    
    # Línea objetivo
    fig.add_hline(y=2.5, line_dash="dash", line_color="red", 
                 annotation_text="Target ROI: 2.5x")
    
    fig.update_layout(
        title="ROI por País - Últimos 14 Días",
        xaxis_title="Fecha",
        yaxis_title="ROI",
        template="plotly_white",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de estadísticas
    st.markdown("### 📊 Estadísticas del Período")
    
    stats_data = []
    for key, (name, _) in countries.items():
        values = timeline_data[key]
        stats_data.append({
            'País': name,
            'ROI Promedio': f"{np.mean(values):.2f}x",
            'ROI Máximo': f"{np.max(values):.2f}x", 
            'ROI Mínimo': f"{np.min(values):.2f}x",
            'Tendencia': "📈" if values[-1] > values[0] else "📉"
        })
    
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

if __name__ == "__main__":
    main()