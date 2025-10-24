"""
🎨 DASHBOARD V3 - Streamlit UI
Sistema de gestión de campañas virales
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Config
st.set_page_config(
    page_title="Community Manager Dashboard V3",
    page_icon="🚀",
    layout="wide"
)

# API URL
UNIFIED_API = "http://unified-orchestrator:10000"

# ═════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════

st.sidebar.title("🚀 Dashboard V3")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegación",
    ["🏠 Home", "🎬 Lanzar Campaña", "🔄 Monitorear Canal", "📊 Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Estado del Sistema")

# Check health
try:
    response = requests.get(f"{UNIFIED_API}/health", timeout=2)
    if response.status_code == 200:
        st.sidebar.success("✅ Sistema Online")
    else:
        st.sidebar.error("❌ Sistema Offline")
except:
    st.sidebar.error("❌ Sistema Offline")

# ═════════════════════════════════════════════════════════════
# HOME PAGE
# ═════════════════════════════════════════════════════════════

if page == "🏠 Home":
    st.title("🚀 Community Manager Dashboard V3")
    st.markdown("---")
    
    st.markdown("""
    ## Sistema de Auto-Viralización
    
    Este dashboard te permite:
    
    ### 🎬 Lanzar Campañas Virales
    - Sube un video o provee URL de YouTube
    - Configura presupuesto y targeting
    - El sistema lo viraliza automáticamente en todas las redes
    
    ### 🔄 Monitorear Canales
    - Monitoreo 24/7 de tu canal de YouTube
    - Auto-detección de videos nuevos
    - Análisis ML y auto-lanzamiento de campañas
    - **Control de carga:** Max 2 campañas/día
    
    ### 📊 Analytics en Tiempo Real
    - Views, engagement, ROI
    - Tracking multi-plataforma
    - Optimización continua
    """)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Campañas Activas", "0", "0")
    
    with col2:
        st.metric("Views Total", "0", "0")
    
    with col3:
        st.metric("Budget Gastado", "$0", "$0")
    
    with col4:
        st.metric("ROI Promedio", "0x", "0x")

# ═════════════════════════════════════════════════════════════
# LAUNCH CAMPAIGN PAGE
# ═════════════════════════════════════════════════════════════

elif page == "🎬 Lanzar Campaña":
    st.title("🎬 Lanzar Campaña Viral")
    st.markdown("---")
    
    with st.form("launch_form"):
        st.subheader("Información del Video")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_path = st.text_input(
                "Path o URL del Video",
                placeholder="/data/videos/mi_video.mp4"
            )
            
            artist_name = st.text_input(
                "Nombre del Artista",
                placeholder="Stakas"
            )
        
        with col2:
            song_name = st.text_input(
                "Nombre de la Canción",
                placeholder="Nueva Vida"
            )
            
            genre = st.selectbox(
                "Género",
                ["Trap", "Reggaeton", "Hip Hop", "Pop", "Rock", "Electronic"]
            )
        
        st.markdown("---")
        st.subheader("Configuración de Campaña")
        
        col1, col2 = st.columns(2)
        
        with col1:
            daily_budget = st.number_input(
                "Presupuesto Diario Meta Ads ($)",
                min_value=10.0,
                max_value=10000.0,
                value=50.0,
                step=10.0
            )
        
        with col2:
            target_countries = st.multiselect(
                "Países Objetivo",
                ["US", "MX", "ES", "AR", "CL", "CO", "BR", "PE"],
                default=["US", "MX", "ES"]
            )
        
        submitted = st.form_submit_button("🚀 Lanzar Campaña")
        
        if submitted:
            if not video_path or not artist_name or not song_name:
                st.error("❌ Por favor completa todos los campos obligatorios")
            else:
                with st.spinner("Lanzando campaña..."):
                    try:
                        response = requests.post(
                            f"{UNIFIED_API}/launch",
                            json={
                                "video_path": video_path,
                                "artist_name": artist_name,
                                "song_name": song_name,
                                "genre": genre,
                                "daily_ad_budget": daily_budget,
                                "target_countries": target_countries
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Campaña lanzada: {result['campaign_id']}")
                            st.json(result)
                        else:
                            st.error(f"❌ Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ═════════════════════════════════════════════════════════════
# MONITOR CHANNEL PAGE
# ═════════════════════════════════════════════════════════════

elif page == "🔄 Monitorear Canal":
    st.title("🔄 Monitorear Canal de YouTube")
    st.markdown("---")
    
    st.info("""
    **Modo Auto-Viralización 24/7**
    
    El sistema monitoreará tu canal continuamente y automáticamente lanzará campañas 
    para videos nuevos que tengan alto potencial viral (ML score > threshold).
    
    **Control de Carga:** Máximo 2 campañas/día para no sobrecargar UTM.
    """)
    
    with st.form("monitor_form"):
        youtube_channel = st.text_input(
            "ID del Canal de YouTube",
            placeholder="UC_ABC123XYZ",
            help="Encuentra el ID en la URL de tu canal: youtube.com/channel/UC_ABC123XYZ"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_launch = st.checkbox(
                "Auto-lanzar campañas",
                value=True,
                help="Si está desactivado, solo recibirás notificaciones"
            )
            
            virality_threshold = st.slider(
                "Threshold de Virality (ML Score)",
                min_value=0.0,
                max_value=1.0,
                value=0.70,
                step=0.05,
                help="Solo lanzará campañas para videos con score ML superior a este valor"
            )
        
        with col2:
            max_campaigns = st.number_input(
                "Máximo Campañas por Día",
                min_value=1,
                max_value=10,
                value=2,
                help="Límite diario para proteger recursos (UTM, APIs)"
            )
            
            daily_budget = st.number_input(
                "Presupuesto por Video ($)",
                min_value=10.0,
                max_value=1000.0,
                value=50.0,
                step=10.0
            )
        
        check_interval = st.selectbox(
            "Intervalo de Revisión",
            [2, 4, 6, 12, 24],
            index=2,
            format_func=lambda x: f"Cada {x} horas"
        )
        
        submitted = st.form_submit_button("🔄 Iniciar Monitoreo 24/7")
        
        if submitted:
            if not youtube_channel:
                st.error("❌ Por favor ingresa el ID del canal")
            else:
                with st.spinner("Iniciando monitor..."):
                    try:
                        response = requests.post(
                            f"{UNIFIED_API}/monitor-channel",
                            json={
                                "youtube_channel_id": youtube_channel,
                                "auto_launch": auto_launch,
                                "virality_threshold": virality_threshold,
                                "max_campaigns_per_day": max_campaigns,
                                "daily_ad_budget_per_video": daily_budget,
                                "check_interval_hours": check_interval
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Monitor iniciado correctamente")
                            st.json(result)
                        else:
                            st.error(f"❌ Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ═════════════════════════════════════════════════════════════
# ANALYTICS PAGE
# ═════════════════════════════════════════════════════════════

elif page == "📊 Analytics":
    st.title("📊 Analytics de Campañas")
    st.markdown("---")
    
    st.info("Analytics en tiempo real - En construcción")
    
    # Placeholder metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Views Totales", "0", "0")
    
    with col2:
        st.metric("Engagement Rate", "0%", "0%")
    
    with col3:
        st.metric("ROI", "0x", "0x")
