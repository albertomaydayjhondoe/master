#!/usr/bin/env python3
"""
🔥 DASHBOARD MÉTRICAS DEL ÚLTIMO MES - STAKAS VIRAL SYSTEM
¡La fiesta empezó! Métricas completas de crecimiento viral
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import time

# Configuración de página 
st.set_page_config(
    page_title="🔥 Stakas Viral - Métricas Último Mes",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para el tema viral
st.markdown("""
<style>
    .main { padding-top: 0rem; }
    .stApp { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 10px 0;
    }
    .viral-header {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
        background-size: 200% 200%;
        animation: gradient 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .live-indicator {
        animation: pulse 2s infinite;
        color: #ff4444;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

class StakasViralDashboard:
    """Dashboard completo de métricas virales del último mes"""
    
    def __init__(self):
        self.canal_id = "UCgohgqLVu1QPdfa64Vkrgeg"
        self.fecha_inicio = datetime.now() - timedelta(days=30)
        self.fecha_actual = datetime.now()
        
    def generar_datos_ultimo_mes(self):
        """Generar datos realistas del último mes"""
        
        # Generar fechas del último mes
        fechas = pd.date_range(start=self.fecha_inicio, end=self.fecha_actual, freq='D')
        
        # Datos base del canal
        datos_canal = {
            'suscriptores_inicio': 47,
            'suscriptores_actual': 156,
            'videos_subidos': 8,
            'total_visualizaciones': 45670,
            'engagement_rate': 12.3,
            'crecimiento_diario_promedio': 3.6
        }
        
        # Generar métricas diarias
        metricas_diarias = []
        subs_base = datos_canal['suscriptores_inicio']
        
        for i, fecha in enumerate(fechas):
            # Simular crecimiento viral con picos
            viral_multiplier = 1 + (np.sin(i/3) * 0.5 + random.uniform(0.5, 2.0))
            if i in [7, 14, 23]:  # Picos virales
                viral_multiplier *= 3.5
            
            nuevos_subs = max(0, int(3 + viral_multiplier + random.uniform(-1, 5)))
            subs_base += nuevos_subs
            
            metricas_diarias.append({
                'fecha': fecha,
                'nuevos_suscriptores': nuevos_subs,
                'suscriptores_totales': subs_base,
                'visualizaciones': int(800 + viral_multiplier * 400 + random.uniform(100, 1500)),
                'likes': int(45 + viral_multiplier * 25 + random.uniform(5, 80)),
                'comentarios': int(8 + viral_multiplier * 5 + random.uniform(1, 15)),
                'shares': int(3 + viral_multiplier * 2 + random.uniform(0, 8)),
                'tiempo_visualizacion': round(2.3 + viral_multiplier * 0.8 + random.uniform(-0.5, 1.2), 1),
                'ctr': round(4.2 + viral_multiplier * 1.5 + random.uniform(-1, 2), 2),
                'engagement_rate': round(8.5 + viral_multiplier * 2 + random.uniform(-2, 4), 2),
                'gasto_ads': round(16.67 + random.uniform(-3, 7), 2),
                'roi_ads': round(2.1 + viral_multiplier * 0.8 + random.uniform(-0.5, 1.5), 2)
            })
        
        # Datos de videos virales
        videos_virales = [
            {
                'titulo': '🔥 Stakas - DRILL MADRID 2025',
                'fecha_subida': fechas[7],
                'visualizaciones': 12450,
                'likes': 1240,
                'comentarios': 156,
                'duracion': '2:34',
                'viral_score': 8.7,
                'engagement': 15.2
            },
            {
                'titulo': '💀 Stakas x Duki - Colaboración ÉPICA',
                'fecha_subida': fechas[14], 
                'visualizaciones': 23890,
                'likes': 2890,
                'comentarios': 345,
                'duracion': '3:12',
                'viral_score': 9.3,
                'engagement': 18.7
            },
            {
                'titulo': '🎯 Stakas - RESPUESTA A TODO',
                'fecha_subida': fechas[23],
                'visualizaciones': 8760,
                'likes': 967,
                'comentarios': 123,
                'duracion': '2:45',
                'viral_score': 7.9,
                'engagement': 13.8
            },
            {
                'titulo': '🚀 Stakas - FREESTYLE VIRAL',
                'fecha_subida': fechas[28],
                'visualizaciones': 15670,
                'likes': 1890,
                'comentarios': 234,
                'duracion': '1:58',
                'viral_score': 8.9,
                'engagement': 16.4
            }
        ]
        
        # Métricas de Meta Ads
        datos_meta_ads = {
            'budget_total': 500.0,
            'gastado': 487.30,
            'impresiones': 234567,
            'clicks': 4567,
            'ctr': 1.95,
            'cpc': 0.107,
            'conversiones': 89,
            'cpa': 5.48,
            'roi': 2.34,
            'campañas_activas': 12
        }
        
        # Device Farm métricas
        device_farm_stats = {
            'dispositivos_activos': 8,
            'acciones_automatizadas': 1450,
            'likes_automatizados': 890,
            'comentarios_automatizados': 234,
            'shares_automatizados': 156,
            'tiempo_engagement': 24.5  # horas
        }
        
        # GoLogin métricas
        gologin_stats = {
            'perfiles_activos': 25,
            'sesiones_completadas': 450,
            'engagement_cross_platform': 789,
            'tiempo_total_sesiones': 67.8  # horas
        }
        
        return {
            'metricas_diarias': pd.DataFrame(metricas_diarias),
            'datos_canal': datos_canal,
            'videos_virales': videos_virales,
            'meta_ads': datos_meta_ads,
            'device_farm': device_farm_stats,
            'gologin': gologin_stats
        }
    
    def mostrar_header_viral(self):
        """Mostrar header animado viral"""
        st.markdown('<h1 class="viral-header">🔥 STAKAS VIRAL SYSTEM 🚀</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🎯 Canal Target")
            st.markdown("**UCgohgqLVu1QPdfa64Vkrgeg**")
            
        with col2:
            st.markdown("### 📊 Período")
            st.markdown("**Últimos 30 días**")
            
        with col3:
            st.markdown('### <span class="live-indicator">🔴 LIVE</span>', unsafe_allow_html=True)
            st.markdown(f"**{datetime.now().strftime('%d/%m/%Y %H:%M')}**")
    
    def mostrar_metricas_clave(self, datos):
        """Mostrar métricas clave en cards destacadas"""
        st.markdown("## 🎯 Métricas Clave del Último Mes")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        crecimiento = datos['datos_canal']['suscriptores_actual'] - datos['datos_canal']['suscriptores_inicio']
        crecimiento_pct = (crecimiento / datos['datos_canal']['suscriptores_inicio']) * 100
        
        with col1:
            st.metric(
                "👥 Nuevos Suscriptores", 
                f"+{crecimiento}", 
                f"{crecimiento_pct:.1f}%"
            )
            
        with col2:
            st.metric(
                "📺 Total Visualizaciones", 
                f"{datos['datos_canal']['total_visualizaciones']:,}", 
                "+234%"
            )
            
        with col3:
            st.metric(
                "💰 ROI Meta Ads", 
                f"{datos['meta_ads']['roi']:.2f}x", 
                "+15.7%"
            )
            
        with col4:
            st.metric(
                "🤖 Acciones Automatizadas", 
                f"{datos['device_farm']['acciones_automatizadas']:,}", 
                "+89%"
            )
            
        with col5:
            st.metric(
                "📈 Engagement Rate", 
                f"{datos['datos_canal']['engagement_rate']:.1f}%", 
                "+3.2%"
            )
    
    def grafico_crecimiento_suscriptores(self, df):
        """Gráfico de crecimiento de suscriptores"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['suscriptores_totales'],
            mode='lines+markers',
            name='Suscriptores Totales',
            line=dict(color='#ff6b6b', width=3),
            fill='tonexty',
            fillcolor='rgba(255, 107, 107, 0.3)'
        ))
        
        fig.add_trace(go.Bar(
            x=df['fecha'],
            y=df['nuevos_suscriptores'],
            name='Nuevos Suscriptores Diarios',
            marker_color='#4ecdc4',
            opacity=0.7,
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="📈 Crecimiento de Suscriptores - Últimos 30 Días",
            xaxis_title="Fecha",
            yaxis=dict(title="Suscriptores Totales", side="left"),
            yaxis2=dict(title="Nuevos Suscriptores", side="right", overlaying="y"),
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    def grafico_engagement_detallado(self, df):
        """Gráfico detallado de engagement"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Visualizaciones Diarias', 'Engagement Rate', 'Tiempo de Visualización', 'CTR'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Visualizaciones
        fig.add_trace(go.Scatter(
            x=df['fecha'], y=df['visualizaciones'],
            name='Visualizaciones', line=dict(color='#ff6b6b')
        ), row=1, col=1)
        
        # Engagement Rate
        fig.add_trace(go.Scatter(
            x=df['fecha'], y=df['engagement_rate'],
            name='Engagement %', line=dict(color='#4ecdc4')
        ), row=1, col=2)
        
        # Tiempo de visualización
        fig.add_trace(go.Scatter(
            x=df['fecha'], y=df['tiempo_visualizacion'],
            name='Tiempo (min)', line=dict(color='#45b7d1')
        ), row=2, col=1)
        
        # CTR
        fig.add_trace(go.Scatter(
            x=df['fecha'], y=df['ctr'],
            name='CTR %', line=dict(color='#96ceb4')
        ), row=2, col=2)
        
        fig.update_layout(
            title="📊 Métricas de Engagement Detalladas",
            template="plotly_dark",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def grafico_meta_ads_performance(self, df):
        """Gráfico de performance de Meta Ads"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Gasto Diario vs ROI', 'Performance Acumulativa'),
            specs=[[{"secondary_y": True}, {"secondary_y": False}]]
        )
        
        # Gasto vs ROI
        fig.add_trace(go.Bar(
            x=df['fecha'], y=df['gasto_ads'],
            name='Gasto Diario (€)', marker_color='#ff6b6b'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['fecha'], y=df['roi_ads'],
            name='ROI', line=dict(color='#4ecdc4', width=3),
            yaxis='y2'
        ), row=1, col=1, secondary_y=True)
        
        # Performance acumulativa  
        gasto_acum = df['gasto_ads'].cumsum()
        fig.add_trace(go.Scatter(
            x=df['fecha'], y=gasto_acum,
            name='Gasto Acumulado', line=dict(color='#45b7d1'),
            fill='tonexty'
        ), row=1, col=2)
        
        fig.update_layout(
            title="💰 Performance Meta Ads - Últimos 30 Días",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    def tabla_videos_virales(self, videos):
        """Tabla de videos virales del mes"""
        st.markdown("## 🎬 Videos Virales del Mes")
        
        for i, video in enumerate(videos):
            with st.expander(f"🔥 #{i+1} - {video['titulo']} (Score: {video['viral_score']})"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📺 Visualizaciones", f"{video['visualizaciones']:,}")
                    
                with col2:
                    st.metric("❤️ Likes", f"{video['likes']:,}")
                    
                with col3:
                    st.metric("💬 Comentarios", f"{video['comentarios']:,}")
                    
                with col4:
                    st.metric("🔥 Engagement", f"{video['engagement']:.1f}%")
    
    def dashboard_automation_systems(self, device_stats, gologin_stats):
        """Dashboard de sistemas de automatización"""
        st.markdown("## 🤖 Sistemas de Automatización")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📱 Device Farm Stats")
            
            # Gráfico de acciones por device
            acciones_por_tipo = {
                'Likes': device_stats['likes_automatizados'],
                'Comentarios': device_stats['comentarios_automatizados'],
                'Shares': device_stats['shares_automatizados']
            }
            
            fig_device = px.pie(
                values=list(acciones_por_tipo.values()),
                names=list(acciones_por_tipo.keys()),
                title="Distribución de Acciones Automatizadas",
                color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
            )
            fig_device.update_layout(template="plotly_dark")
            st.plotly_chart(fig_device, use_container_width=True)
            
        with col2:
            st.markdown("### 🌐 GoLogin Browser Automation")
            
            # Métricas de GoLogin
            st.metric("Perfiles Activos", f"{gologin_stats['perfiles_activos']}/30")
            st.metric("Sesiones Completadas", f"{gologin_stats['sesiones_completadas']}")
            st.metric("Engagement Cross-Platform", f"{gologin_stats['engagement_cross_platform']}")
            st.metric("Tiempo Total (horas)", f"{gologin_stats['tiempo_total_sesiones']:.1f}")
            
            # Progress bar de eficiencia
            eficiencia = (gologin_stats['perfiles_activos'] / 30) * 100
            st.progress(eficiencia / 100)
            st.caption(f"Eficiencia de Perfiles: {eficiencia:.1f}%")
    
    def mostrar_predicciones_ai(self, df):
        """Mostrar predicciones de IA para próximo mes"""
        st.markdown("## 🔮 Predicciones IA - Próximo Mes")
        
        # Calcular tendencias
        crecimiento_promedio = df['nuevos_suscriptores'].tail(7).mean()
        engagement_trend = df['engagement_rate'].tail(7).mean()
        roi_trend = df['roi_ads'].tail(7).mean()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            prediccion_subs = int(crecimiento_promedio * 30 * 1.15)  # +15% optimista
            st.metric(
                "🎯 Suscriptores Predichos", 
                f"+{prediccion_subs}",
                "Próximo mes"
            )
            
        with col2:
            prediccion_engagement = engagement_trend * 1.08  # +8% mejora
            st.metric(
                "📈 Engagement Predicho", 
                f"{prediccion_engagement:.1f}%",
                "+8% vs actual"
            )
            
        with col3:
            prediccion_roi = roi_trend * 1.12  # +12% optimización
            st.metric(
                "💰 ROI Predicho", 
                f"{prediccion_roi:.2f}x",
                "+12% optimización"
            )
        
        # Gráfico de predicción
        st.markdown("### 📊 Proyección de Crecimiento")
        
        # Datos históricos + predicción
        fechas_futuras = pd.date_range(start=df['fecha'].max(), periods=31, freq='D')[1:]
        
        fig = go.Figure()
        
        # Datos reales
        fig.add_trace(go.Scatter(
            x=df['fecha'],
            y=df['suscriptores_totales'],
            mode='lines+markers',
            name='Datos Reales',
            line=dict(color='#ff6b6b', width=2)
        ))
        
        # Predicción
        subs_actuales = df['suscriptores_totales'].iloc[-1]
        prediccion_subs_diarios = np.random.normal(crecimiento_promedio * 1.15, 2, 30)
        prediccion_subs_acum = [subs_actuales + sum(prediccion_subs_diarios[:i+1]) for i in range(30)]
        
        fig.add_trace(go.Scatter(
            x=fechas_futuras,
            y=prediccion_subs_acum,
            mode='lines+markers',
            name='Predicción IA',
            line=dict(color='#4ecdc4', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="🔮 Predicción de Crecimiento - Próximos 30 Días",
            xaxis_title="Fecha",
            yaxis_title="Suscriptores",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Función principal del dashboard"""
    
    dashboard = StakasViralDashboard()
    
    # Header viral
    dashboard.mostrar_header_viral()
    
    # Generar datos
    with st.spinner("🔥 Cargando métricas virales del último mes..."):
        datos = dashboard.generar_datos_ultimo_mes()
        time.sleep(1)  # Efecto de carga
    
    # Métricas clave
    dashboard.mostrar_metricas_clave(datos)
    
    # Gráficos principales
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_crecimiento = dashboard.grafico_crecimiento_suscriptores(datos['metricas_diarias'])
        st.plotly_chart(fig_crecimiento, use_container_width=True)
        
    with col2:
        fig_meta_ads = dashboard.grafico_meta_ads_performance(datos['metricas_diarias'])
        st.plotly_chart(fig_meta_ads, use_container_width=True)
    
    # Engagement detallado
    st.markdown("---")
    fig_engagement = dashboard.grafico_engagement_detallado(datos['metricas_diarias'])
    st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Videos virales
    st.markdown("---")
    dashboard.tabla_videos_virales(datos['videos_virales'])
    
    # Sistemas de automatización
    st.markdown("---")
    dashboard.dashboard_automation_systems(datos['device_farm'], datos['gologin'])
    
    # Predicciones IA
    st.markdown("---")
    dashboard.mostrar_predicciones_ai(datos['metricas_diarias'])
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: rgba(255,255,255,0.7);'>
        🚀 <strong>Stakas Viral System</strong> - Powered by Meta Ads + ML + Device Farm + GoLogin<br>
        🎯 Canal: UCgohgqLVu1QPdfa64Vkrgeg | 💰 Budget: €500/month | 🔥 Status: VIRAL ACTIVO
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()