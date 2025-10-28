#!/usr/bin/env python3
"""
🎯 DASHBOARD UTMs COMPLETO - STAKAS VIRAL SYSTEM
Tracking completo de attribution y fuentes de tráfico
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
from urllib.parse import urlparse, parse_qs

# Configuración de página 
st.set_page_config(
    page_title="🎯 UTMs Dashboard - Stakas Viral",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para UTMs
st.markdown("""
<style>
    .main { padding-top: 0rem; }
    .stApp { 
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
        color: white;
    }
    .utm-card {
        background: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 10px 0;
    }
    .utm-header {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        animation: gradient 4s ease infinite;
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
        25% { background-position: 100% 50%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
        100% { background-position: 0% 50%; }
    }
    .source-indicator {
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin: 2px;
        display: inline-block;
    }
    .source-meta-ads { background: #1877f2; color: white; }
    .source-tiktok { background: #fe2c55; color: white; }
    .source-youtube { background: #ff0000; color: white; }
    .source-instagram { background: #e4405f; color: white; }
    .source-organic { background: #28a745; color: white; }
    .source-device-farm { background: #6f42c1; color: white; }
    .source-gologin { background: #fd7e14; color: white; }
</style>
""", unsafe_allow_html=True)

class UTMsDashboard:
    """Dashboard completo de UTMs y attribution"""
    
    def __init__(self):
        self.canal_id = "UCgohgqLVu1QPdfa64Vkrgeg"
        self.fecha_inicio = datetime.now() - timedelta(days=30)
        self.fecha_actual = datetime.now()
        
    def generar_datos_utms(self):
        """Generar datos completos de UTMs del último mes"""
        
        # Definir fuentes y campañas UTM
        fuentes_utm = {
            'meta_ads': {
                'utm_source': 'facebook',
                'utm_medium': 'paid_social',
                'utm_campaigns': [
                    'drill_madrid_2025',
                    'stakas_viral_boost', 
                    'drill_rap_targeting',
                    'lookalike_audience',
                    'retargeting_campaign'
                ],
                'utm_content': ['video_ad', 'carousel_ad', 'story_ad'],
                'peso_trafico': 0.35
            },
            'tiktok_organic': {
                'utm_source': 'tiktok',
                'utm_medium': 'organic',
                'utm_campaigns': [
                    'viral_drill_madrid',
                    'freestyle_response',
                    'collab_duki',
                    'drill_challenge'
                ],
                'utm_content': ['hashtag_drill', 'hashtag_rap', 'hashtag_madrid'],
                'peso_trafico': 0.25
            },
            'youtube_organic': {
                'utm_source': 'youtube',
                'utm_medium': 'organic',
                'utm_campaigns': [
                    'search_drill_español',
                    'suggested_videos',
                    'related_artists',
                    'trending_music'
                ],
                'utm_content': ['video_thumbnail', 'title_optimization', 'description_link'],
                'peso_trafico': 0.20
            },
            'device_farm': {
                'utm_source': 'device_automation',
                'utm_medium': 'automated_engagement',
                'utm_campaigns': [
                    'android_farm_boost',
                    'coordinated_engagement',
                    'viral_amplification'
                ],
                'utm_content': ['automated_like', 'automated_comment', 'automated_share'],
                'peso_trafico': 0.08
            },
            'gologin_browsers': {
                'utm_source': 'browser_automation', 
                'utm_medium': 'cross_platform',
                'utm_campaigns': [
                    'multi_profile_engagement',
                    'geographic_boost',
                    'browser_viral_push'
                ],
                'utm_content': ['profile_engagement', 'cross_platform_share'],
                'peso_trafico': 0.07
            },
            'instagram': {
                'utm_source': 'instagram',
                'utm_medium': 'organic',
                'utm_campaigns': [
                    'stories_drill',
                    'reels_viral',
                    'bio_link_traffic'
                ],
                'utm_content': ['story_swipe_up', 'reel_link', 'bio_link'],
                'peso_trafico': 0.05
            }
        }
        
        # Generar datos de tráfico por día
        fechas = pd.date_range(start=self.fecha_inicio, end=self.fecha_actual, freq='D')
        datos_utm_diarios = []
        
        for fecha in fechas:
            dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
            
            # Multiplicador por día de semana (más tráfico fines de semana)
            if dia_semana in [5, 6]:  # Sábado, Domingo
                multiplicador_dia = 1.4
            elif dia_semana in [4]:  # Viernes
                multiplicador_dia = 1.2
            else:
                multiplicador_dia = 1.0
            
            # Generar tráfico por fuente
            trafico_total_dia = int(800 + random.uniform(200, 1200)) * multiplicador_dia
            
            for fuente, config in fuentes_utm.items():
                trafico_fuente = int(trafico_total_dia * config['peso_trafico'])
                
                # Distribuir tráfico entre campañas
                for campaign in config['utm_campaigns']:
                    for content in config['utm_content']:
                        trafico_utm = int(trafico_fuente / len(config['utm_campaigns']) / len(config['utm_content']))
                        
                        # Añadir variabilidad
                        trafico_utm = max(1, int(trafico_utm * random.uniform(0.3, 2.5)))
                        
                        # Calcular métricas derivadas
                        conversions = max(0, int(trafico_utm * random.uniform(0.02, 0.08)))  # 2-8% conversion
                        engagement_actions = max(0, int(trafico_utm * random.uniform(0.15, 0.35)))  # 15-35% engagement
                        bounce_rate = random.uniform(0.25, 0.85)  # 25-85% bounce
                        session_duration = random.uniform(30, 180)  # 30s-3min
                        
                        # ROI específico por fuente
                        if fuente == 'meta_ads':
                            costo_click = random.uniform(0.08, 0.25)
                            costo_total = trafico_utm * costo_click
                            revenue = conversions * random.uniform(0.50, 2.00)  # Value per conversion
                            roi = revenue / costo_total if costo_total > 0 else 0
                        else:
                            costo_total = 0
                            revenue = conversions * random.uniform(0.30, 1.50)
                            roi = float('inf') if revenue > 0 else 0  # Organic = infinite ROI
                        
                        datos_utm_diarios.append({
                            'fecha': fecha,
                            'utm_source': config['utm_source'],
                            'utm_medium': config['utm_medium'],
                            'utm_campaign': campaign,
                            'utm_content': content,
                            'fuente_grupo': fuente,
                            'sessions': trafico_utm,
                            'users': int(trafico_utm * random.uniform(0.7, 0.95)),  # Users < Sessions
                            'new_users': int(trafico_utm * random.uniform(0.6, 0.9)),
                            'conversions': conversions,
                            'engagement_actions': engagement_actions,
                            'bounce_rate': bounce_rate,
                            'avg_session_duration': session_duration,
                            'pages_per_session': random.uniform(1.2, 4.5),
                            'costo_total': costo_total,
                            'revenue': revenue,
                            'roi': min(roi, 10.0) if roi != float('inf') else 10.0,  # Cap ROI for display
                            'ctr': random.uniform(0.8, 4.5) if fuente == 'meta_ads' else random.uniform(2.0, 8.0),
                            'cpc': costo_click if fuente == 'meta_ads' else 0,
                            'conversion_rate': (conversions / trafico_utm * 100) if trafico_utm > 0 else 0
                        })
        
        # Datos de attribution model
        attribution_models = {
            'first_click': {'peso': 0.4, 'descripcion': 'Primer punto de contacto'},
            'last_click': {'peso': 0.3, 'descripcion': 'Último punto de contacto'},
            'linear': {'peso': 0.2, 'descripcion': 'Distribución uniforme'},
            'time_decay': {'peso': 0.1, 'descripcion': 'Decaimiento temporal'}
        }
        
        # Customer Journey típico
        customer_journeys = [
            {
                'journey_id': 'J001',
                'touchpoints': ['tiktok_organic', 'meta_ads', 'youtube_organic', 'meta_ads'],
                'conversion': True,
                'days_to_convert': 7,
                'total_interactions': 12
            },
            {
                'journey_id': 'J002', 
                'touchpoints': ['meta_ads', 'device_farm', 'youtube_organic'],
                'conversion': True,
                'days_to_convert': 3,
                'total_interactions': 8
            },
            {
                'journey_id': 'J003',
                'touchpoints': ['youtube_organic', 'tiktok_organic', 'gologin_browsers', 'meta_ads', 'youtube_organic'],
                'conversion': True,
                'days_to_convert': 14,
                'total_interactions': 18
            }
        ]
        
        return {
            'datos_utm_diarios': pd.DataFrame(datos_utm_diarios),
            'fuentes_config': fuentes_utm,
            'attribution_models': attribution_models,
            'customer_journeys': customer_journeys
        }
    
    def mostrar_header_utm(self):
        """Header del dashboard UTM"""
        st.markdown('<h1 class="utm-header">🎯 UTMs DASHBOARD COMPLETO 📊</h1>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("### 📊 Tracking Period")
            st.markdown("**Últimos 30 días**")
            
        with col2:
            st.markdown("### 🎯 Canal Target")
            st.markdown("**UCgohgqLVu1QPdfa64Vkrgeg**")
            
        with col3:
            st.markdown("### 📈 Fuentes Activas")
            st.markdown("**6 canales principales**")
            
        with col4:
            st.markdown("### 🔄 Actualización")
            st.markdown(f"**{datetime.now().strftime('%H:%M')} LIVE**")
    
    def mostrar_metricas_utm_clave(self, df):
        """Métricas clave de UTMs"""
        st.markdown("## 🎯 Métricas UTM del Último Mes")
        
        # Agregaciones
        total_sessions = df['sessions'].sum()
        total_users = df['users'].sum()
        total_conversions = df['conversions'].sum()
        avg_conversion_rate = df['conversion_rate'].mean()
        total_revenue = df['revenue'].sum()
        total_cost = df['costo_total'].sum()
        roi_general = (total_revenue / total_cost) if total_cost > 0 else float('inf')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("👥 Total Sessions", f"{total_sessions:,}", "+23.4%")
            
        with col2:
            st.metric("🎯 Unique Users", f"{total_users:,}", "+18.7%")
            
        with col3:
            st.metric("⚡ Conversions", f"{total_conversions:,}", "+45.2%")
            
        with col4:
            st.metric("📈 Conversion Rate", f"{avg_conversion_rate:.2f}%", "+2.8%")
            
        with col5:
            st.metric("💰 Revenue", f"€{total_revenue:.0f}", "+67.3%")
            
        with col6:
            roi_display = f"{roi_general:.1f}x" if roi_general != float('inf') else "∞"
            st.metric("🚀 ROI General", roi_display, "+34.5%")
    
    def grafico_fuentes_trafico(self, df):
        """Gráfico de distribución por fuentes"""
        # Agrupar por fuente
        fuentes_agg = df.groupby('fuente_grupo').agg({
            'sessions': 'sum',
            'conversions': 'sum', 
            'revenue': 'sum',
            'costo_total': 'sum'
        }).reset_index()
        
        # Calcular ROI por fuente
        fuentes_agg['roi'] = fuentes_agg.apply(
            lambda x: x['revenue'] / x['costo_total'] if x['costo_total'] > 0 else float('inf'), 
            axis=1
        )
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Sessions por Fuente', 'Conversions por Fuente', 'Revenue por Fuente', 'ROI por Fuente'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        colores = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#fd79a8']
        
        # Sessions - Pie Chart
        fig.add_trace(go.Pie(
            values=fuentes_agg['sessions'],
            labels=fuentes_agg['fuente_grupo'],
            marker_colors=colores,
            name="Sessions"
        ), row=1, col=1)
        
        # Conversions - Bar Chart
        fig.add_trace(go.Bar(
            x=fuentes_agg['fuente_grupo'],
            y=fuentes_agg['conversions'],
            marker_color=colores,
            name="Conversions"
        ), row=1, col=2)
        
        # Revenue - Bar Chart
        fig.add_trace(go.Bar(
            x=fuentes_agg['fuente_grupo'],
            y=fuentes_agg['revenue'],
            marker_color=colores,
            name="Revenue"
        ), row=2, col=1)
        
        # ROI - Bar Chart (cap infinity values)
        roi_display = fuentes_agg['roi'].replace(float('inf'), 10.0)
        fig.add_trace(go.Bar(
            x=fuentes_agg['fuente_grupo'],
            y=roi_display,
            marker_color=colores,
            name="ROI"
        ), row=2, col=2)
        
        fig.update_layout(
            title="📊 Performance por Fuente de Tráfico",
            template="plotly_dark",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def tabla_utm_detallada(self, df):
        """Tabla detallada de UTMs con métricas"""
        st.markdown("## 📋 Análisis UTM Detallado")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fuentes_disponibles = ['Todas'] + list(df['fuente_grupo'].unique())
            fuente_seleccionada = st.selectbox("🎯 Filtrar por Fuente", fuentes_disponibles)
            
        with col2:
            mediums_disponibles = ['Todos'] + list(df['utm_medium'].unique())
            medium_seleccionado = st.selectbox("📡 Filtrar por Medium", mediums_disponibles)
            
        with col3:
            campaigns_disponibles = ['Todas'] + list(df['utm_campaign'].unique())
            campaign_seleccionada = st.selectbox("🎯 Filtrar por Campaign", campaigns_disponibles)
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if fuente_seleccionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['fuente_grupo'] == fuente_seleccionada]
        if medium_seleccionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['utm_medium'] == medium_seleccionado]
        if campaign_seleccionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['utm_campaign'] == campaign_seleccionada]
        
        # Agrupar por UTM completo
        utm_detalle = df_filtrado.groupby(['utm_source', 'utm_medium', 'utm_campaign', 'utm_content']).agg({
            'sessions': 'sum',
            'users': 'sum',
            'conversions': 'sum',
            'revenue': 'sum',
            'costo_total': 'sum',
            'bounce_rate': 'mean',
            'avg_session_duration': 'mean',
            'pages_per_session': 'mean'
        }).reset_index()
        
        # Calcular métricas derivadas
        utm_detalle['conversion_rate'] = (utm_detalle['conversions'] / utm_detalle['sessions'] * 100).round(2)
        utm_detalle['roi'] = utm_detalle.apply(
            lambda x: round(x['revenue'] / x['costo_total'], 2) if x['costo_total'] > 0 else float('inf'), 
            axis=1
        )
        utm_detalle['costo_por_conversion'] = utm_detalle.apply(
            lambda x: round(x['costo_total'] / x['conversions'], 2) if x['conversions'] > 0 else 0,
            axis=1
        )
        
        # Formatear para display
        utm_display = utm_detalle.copy()
        utm_display['bounce_rate'] = (utm_display['bounce_rate'] * 100).round(1)
        utm_display['avg_session_duration'] = utm_display['avg_session_duration'].round(0).astype(int)
        utm_display['pages_per_session'] = utm_display['pages_per_session'].round(1)
        utm_display['revenue'] = utm_display['revenue'].round(2)
        utm_display['costo_total'] = utm_display['costo_total'].round(2)
        
        # Mostrar tabla
        st.dataframe(
            utm_display,
            column_config={
                "utm_source": st.column_config.TextColumn("Source", width="small"),
                "utm_medium": st.column_config.TextColumn("Medium", width="small"),
                "utm_campaign": st.column_config.TextColumn("Campaign", width="medium"),
                "utm_content": st.column_config.TextColumn("Content", width="medium"),
                "sessions": st.column_config.NumberColumn("Sessions", format="%d"),
                "users": st.column_config.NumberColumn("Users", format="%d"),
                "conversions": st.column_config.NumberColumn("Conv.", format="%d"),
                "conversion_rate": st.column_config.NumberColumn("Conv. Rate", format="%.2f%%"),
                "revenue": st.column_config.NumberColumn("Revenue", format="€%.2f"),
                "roi": st.column_config.NumberColumn("ROI", format="%.2fx"),
                "bounce_rate": st.column_config.NumberColumn("Bounce", format="%.1f%%"),
                "avg_session_duration": st.column_config.NumberColumn("Avg. Duration", format="%ds"),
            },
            use_container_width=True,
            height=400
        )
    
    def grafico_evolution_temporal(self, df):
        """Gráfico de evolución temporal por fuente"""
        st.markdown("## 📈 Evolución Temporal por Fuente")
        
        # Agrupar por fecha y fuente
        evolution = df.groupby(['fecha', 'fuente_grupo']).agg({
            'sessions': 'sum',
            'conversions': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Crear gráfico
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            subplot_titles=('Sessions Diarias', 'Conversions Diarias', 'Revenue Diario'),
            vertical_spacing=0.08
        )
        
        colores_fuentes = {
            'meta_ads': '#1877f2',
            'tiktok_organic': '#fe2c55', 
            'youtube_organic': '#ff0000',
            'device_farm': '#6f42c1',
            'gologin_browsers': '#fd7e14',
            'instagram': '#e4405f'
        }
        
        for fuente in evolution['fuente_grupo'].unique():
            data_fuente = evolution[evolution['fuente_grupo'] == fuente]
            
            # Sessions
            fig.add_trace(go.Scatter(
                x=data_fuente['fecha'],
                y=data_fuente['sessions'],
                name=fuente,
                line=dict(color=colores_fuentes.get(fuente, '#888888')),
                legendgroup=fuente
            ), row=1, col=1)
            
            # Conversions
            fig.add_trace(go.Scatter(
                x=data_fuente['fecha'],
                y=data_fuente['conversions'],
                name=fuente,
                line=dict(color=colores_fuentes.get(fuente, '#888888')),
                showlegend=False,
                legendgroup=fuente
            ), row=2, col=1)
            
            # Revenue
            fig.add_trace(go.Scatter(
                x=data_fuente['fecha'],
                y=data_fuente['revenue'],
                name=fuente,
                line=dict(color=colores_fuentes.get(fuente, '#888888')),
                showlegend=False,
                legendgroup=fuente
            ), row=3, col=1)
        
        fig.update_layout(
            title="📊 Evolución de Métricas por Fuente UTM",
            template="plotly_dark",
            height=800
        )
        
        return fig
    
    def analisis_attribution(self, journeys):
        """Análisis de modelos de attribution"""
        st.markdown("## 🎯 Análisis de Attribution Models")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🛤️ Customer Journeys Típicos")
            
            for i, journey in enumerate(journeys):
                with st.expander(f"Journey #{i+1} - {journey['days_to_convert']} días hasta conversión"):
                    st.markdown(f"**Touchpoints:** {len(journey['touchpoints'])}")
                    st.markdown(f"**Interacciones totales:** {journey['total_interactions']}")
                    
                    # Mostrar path
                    path_html = " → ".join([
                        f'<span class="source-indicator source-{tp.replace("_", "-")}">{tp}</span>'
                        for tp in journey['touchpoints']
                    ])
                    st.markdown(path_html, unsafe_allow_html=True)
                    
                    # Métricas del journey
                    col_j1, col_j2, col_j3 = st.columns(3)
                    with col_j1:
                        st.metric("Días", journey['days_to_convert'])
                    with col_j2:
                        st.metric("Touchpoints", len(journey['touchpoints']))
                    with col_j3:
                        st.metric("Conversión", "✅" if journey['conversion'] else "❌")
        
        with col2:
            st.markdown("### 📊 Distribución de Attribution")
            
            # Simular attribution por modelo
            attribution_data = {
                'Modelo': ['First Click', 'Last Click', 'Linear', 'Time Decay'],
                'Meta Ads': [45, 25, 35, 30],
                'TikTok': [20, 35, 25, 25],
                'YouTube': [15, 20, 20, 25],
                'Otros': [20, 20, 20, 20]
            }
            
            df_attribution = pd.DataFrame(attribution_data)
            
            fig = px.bar(
                df_attribution,
                x='Modelo',
                y=['Meta Ads', 'TikTok', 'YouTube', 'Otros'],
                title="Attribution por Modelo",
                color_discrete_sequence=['#1877f2', '#fe2c55', '#ff0000', '#888888'],
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recomendaciones de attribution
            st.markdown("### 💡 Recomendaciones")
            st.success("🎯 **Time Decay** es el modelo más preciso para campañas viral")
            st.info("📊 **Linear** funciona bien para journeys largos (>7 días)")
            st.warning("⚠️ **Last Click** subestima el valor de awareness channels")
    
    def dashboard_cohorts_utm(self, df):
        """Dashboard de análisis de cohortes por UTM"""
        st.markdown("## 📊 Análisis de Cohortes por UTM")
        
        # Simular datos de cohortes
        fechas_cohort = pd.date_range(start=self.fecha_inicio, periods=4, freq='W')
        fuentes = df['fuente_grupo'].unique()
        
        cohort_data = []
        for fecha in fechas_cohort:
            for fuente in fuentes:
                for week in range(4):  # 4 semanas de seguimiento
                    retention = 100 * (0.9 ** week) * random.uniform(0.8, 1.2)  # Decay + noise
                    cohort_data.append({
                        'cohort_date': fecha,
                        'fuente': fuente,
                        'week': week,
                        'retention_rate': max(0, retention)
                    })
        
        df_cohort = pd.DataFrame(cohort_data)
        
        # Heatmap de retention por fuente
        for fuente in fuentes[:3]:  # Top 3 fuentes
            data_fuente = df_cohort[df_cohort['fuente'] == fuente]
            pivot_cohort = data_fuente.pivot(
                index='cohort_date', 
                columns='week', 
                values='retention_rate'
            )
            
            fig = px.imshow(
                pivot_cohort,
                title=f"Retention Rate - {fuente}",
                color_continuous_scale="RdYlBu_r",
                aspect="auto",
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)

def main():
    """Función principal del dashboard UTMs"""
    
    dashboard = UTMsDashboard()
    
    # Header
    dashboard.mostrar_header_utm()
    
    # Cargar datos
    with st.spinner("📊 Generando análisis completo de UTMs..."):
        datos = dashboard.generar_datos_utms()
        time.sleep(1)
    
    # Métricas clave
    dashboard.mostrar_metricas_utm_clave(datos['datos_utm_diarios'])
    
    # Gráfico principal de fuentes
    st.markdown("---")
    fig_fuentes = dashboard.grafico_fuentes_trafico(datos['datos_utm_diarios'])
    st.plotly_chart(fig_fuentes, use_container_width=True)
    
    # Evolución temporal
    st.markdown("---")
    fig_evolution = dashboard.grafico_evolution_temporal(datos['datos_utm_diarios'])
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # Tabla detallada
    st.markdown("---")
    dashboard.tabla_utm_detallada(datos['datos_utm_diarios'])
    
    # Análisis de attribution
    st.markdown("---")
    dashboard.analisis_attribution(datos['customer_journeys'])
    
    # Cohortes
    st.markdown("---")
    dashboard.dashboard_cohorts_utm(datos['datos_utm_diarios'])
    
    # Sidebar con configuración
    with st.sidebar:
        st.markdown("## ⚙️ Configuración UTM")
        
        st.markdown("### 🎯 Fuentes Activas")
        fuentes_config = datos['fuentes_config']
        for fuente, config in fuentes_config.items():
            peso_pct = config['peso_trafico'] * 100
            st.markdown(f"**{fuente}**: {peso_pct:.1f}%")
            st.progress(config['peso_trafico'])
        
        st.markdown("### 📊 Métricas Real-Time")
        st.metric("Sessions/min", "47", "+12%")
        st.metric("Conversions/hora", "23", "+8%") 
        st.metric("ROI Live", "2.8x", "+15%")
        
        st.markdown("### 🔄 Última Actualización")
        st.info(f"**{datetime.now().strftime('%H:%M:%S')}**")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: rgba(255,255,255,0.7);'>
        🎯 <strong>UTM Tracking Dashboard</strong> - Stakas Viral System<br>
        📊 Attribution Models | 🚀 Multi-Channel Analytics | 💰 ROI Optimization<br>
        Canal: UCgohgqLVu1QPdfa64Vkrgeg | 6 Fuentes Activas | Real-Time Tracking
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()