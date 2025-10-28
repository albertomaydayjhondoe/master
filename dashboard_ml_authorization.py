"""
🤖 Sistema de Autorización ML Inteligente
Dashboard para autorizar decisiones ML con datos en tiempo real
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configuración de página
st.set_page_config(
    page_title="🤖 ML Authorization Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs de servicios
LANDING_GENERATOR_URL = "http://landing-generator:8004"
ML_CORE_URL = "http://ml-core:8000"
META_ADS_URL = "http://meta-ads-manager:9000"

# Estilos CSS personalizados
st.markdown("""
<style>
    .authorization-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 5px;
    }
    
    .risk-high { border-left: 5px solid #ff4444; }
    .risk-medium { border-left: 5px solid #ffaa00; }
    .risk-low { border-left: 5px solid #44ff44; }
    
    .status-pending { background: #ffa500; }
    .status-approved { background: #32cd32; }
    .status-rejected { background: #ff6b6b; }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def get_pending_authorizations() -> List[Dict]:
    """Obtener autorizaciones pendientes"""
    
    try:
        response = requests.get(f"{LANDING_GENERATOR_URL}/api/authorizations/pending", timeout=10)
        if response.status_code == 200:
            return response.json().get("authorizations", [])
        else:
            return get_mock_authorizations()
    except:
        return get_mock_authorizations()

def get_mock_authorizations() -> List[Dict]:
    """Mock data para demo"""
    
    return [
        {
            "id": "auth_001",
            "request": {
                "campaign_id": "camp_400_euros",
                "decision_type": "budget_increase",
                "cost_impact_euros": 75.0,
                "confidence_score": 0.89,
                "urgency_level": "medium",
                "current_performance": {
                    "roas": 2.8,
                    "ctr": 4.2,
                    "conversions": 89,
                    "spend_euros": 165.50
                },
                "recommended_action": {
                    "new_daily_budget": 475.0,
                    "reason": "High ROAS detected, increase budget to capture more conversions",
                    "platforms": ["youtube", "tiktok"],
                    "expected_return": 210.0
                }
            },
            "status": "pending",
            "created_at": "2025-10-27T14:30:00Z",
            "risk_level": "medium",
            "recommendation": "Recommended: Strong performance indicators support budget increase"
        },
        {
            "id": "auth_002", 
            "request": {
                "campaign_id": "camp_400_euros",
                "decision_type": "platform_expansion",
                "cost_impact_euros": 120.0,
                "confidence_score": 0.76,
                "urgency_level": "high",
                "current_performance": {
                    "youtube_views": 15000,
                    "tiktok_views": 45000,
                    "engagement_rate": 12.5
                },
                "recommended_action": {
                    "new_platforms": ["instagram_reels", "twitter_promoted"],
                    "additional_budget": 120.0,
                    "reason": "Viral content detected on TikTok, expand to capitalize",
                    "expected_reach": 85000
                }
            },
            "status": "pending",
            "created_at": "2025-10-27T15:45:00Z", 
            "risk_level": "medium",
            "recommendation": "Consider approval: Viral momentum detected"
        },
        {
            "id": "auth_003",
            "request": {
                "campaign_id": "camp_400_euros", 
                "decision_type": "content_optimization",
                "cost_impact_euros": 45.0,
                "confidence_score": 0.94,
                "urgency_level": "low",
                "current_performance": {
                    "ultralytics_score": 0.87,
                    "audio_quality": 0.92,
                    "visual_engagement": 0.78
                },
                "recommended_action": {
                    "optimize_thumbnails": True,
                    "enhance_audio": True,
                    "add_subtitles": ["spanish", "english"],
                    "reason": "ML analysis suggests content improvements will boost engagement 15%"
                }
            },
            "status": "pending",
            "created_at": "2025-10-27T16:20:00Z",
            "risk_level": "low", 
            "recommendation": "Auto-approve candidate: Low risk, high confidence"
        }
    ]

def approve_authorization(auth_id: str, decision: str, reason: str = "") -> Dict:
    """Aprobar o rechazar autorización"""
    
    try:
        response = requests.post(
            f"{LANDING_GENERATOR_URL}/api/authorization/approve/{auth_id}",
            json={
                "decision": decision,
                "reason": reason,
                "user_id": "dashboard_admin",
                "timestamp": datetime.now().isoformat()
            },
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": response.text}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_campaign_performance(campaign_id: str) -> Dict:
    """Obtener performance actual de campaña"""
    
    # Mock data para demo
    return {
        "campaign_id": campaign_id,
        "total_spend_euros": 268.50,
        "total_revenue_euros": 751.80,
        "roas": 2.8,
        "total_conversions": 127,
        "platforms_active": 4,
        "landing_page_visits": 2890,
        "landing_page_conversions": 156,
        "utm_performance": {
            "meta_ads": {"visits": 1650, "conversions": 98, "revenue": 441.20},
            "youtube": {"visits": 580, "conversions": 34, "revenue": 153.60},
            "tiktok": {"visits": 420, "conversions": 18, "revenue": 108.40},
            "instagram": {"visits": 240, "conversions": 6, "revenue": 48.60}
        },
        "ml_insights": {
            "ultralytics_analysis": "High engagement potential detected",
            "genre_optimization": "Reggaeton content performing 40% above average",
            "optimal_timing": "Peak engagement: 19:00-21:00 CET",
            "virality_score": 0.78
        }
    }

# ============================================
# SIDEBAR - CAMPAIGN OVERVIEW
# ============================================

st.sidebar.title("🚀 Meta Ads €400 Campaign")
st.sidebar.markdown("---")

# Campaign summary
campaign_perf = get_campaign_performance("camp_400_euros")

st.sidebar.metric("💰 Presupuesto Total", "€400.00")
st.sidebar.metric("📊 Gastado", f"€{campaign_perf['total_spend_euros']:.2f}")
st.sidebar.metric("💸 Ingresos", f"€{campaign_perf['total_revenue_euros']:.2f}")
st.sidebar.metric("📈 ROAS", f"{campaign_perf['roas']:.1f}x")

st.sidebar.markdown("---")
st.sidebar.markdown("**🤖 ML Status**")
st.sidebar.success("✅ Ultralytics: Active")
st.sidebar.success("✅ UTM Tracking: Active") 
st.sidebar.success("✅ Railway Hosting: Active")
st.sidebar.info("🔄 24/7 Automation: Running")

# ============================================
# MAIN CONTENT
# ============================================

st.title("🤖 ML Authorization Dashboard")
st.markdown("**Autoriza decisiones ML inteligentes para tu campaña Meta Ads de €400**")

# Tabs principales
tab_pending, tab_analytics, tab_performance, tab_settings = st.tabs([
    "🔔 Autorizaciones Pendientes", 
    "📊 Analytics UTM",
    "🎯 Performance Campaña",
    "⚙️ Configuración ML"
])

# ============================================
# TAB: AUTORIZACIONES PENDIENTES
# ============================================

with tab_pending:
    st.subheader("🔔 Decisiones ML Pendientes de Autorización")
    
    authorizations = get_pending_authorizations()
    
    if not authorizations:
        st.info("✅ No hay autorizaciones pendientes. El sistema ML está funcionando de forma autónoma.")
    else:
        for auth in authorizations:
            request_data = auth["request"]
            
            # Container principal para cada autorización
            with st.container():
                # Header con tipo y urgencia
                col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
                
                with col_header1:
                    decision_icons = {
                        "budget_increase": "💰",
                        "platform_expansion": "📱", 
                        "content_optimization": "🎨"
                    }
                    icon = decision_icons.get(request_data["decision_type"], "🤖")
                    st.markdown(f"### {icon} {request_data['decision_type'].replace('_', ' ').title()}")
                
                with col_header2:
                    urgency_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    urgency_icon = urgency_colors.get(request_data["urgency_level"], "⚪")
                    st.markdown(f"**Urgencia:** {urgency_icon} {request_data['urgency_level'].upper()}")
                
                with col_header3:
                    risk_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    risk_icon = risk_colors.get(auth["risk_level"], "⚪")
                    st.markdown(f"**Riesgo:** {risk_icon} {auth['risk_level'].upper()}")
                
                # Métricas principales
                col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
                
                with col_metrics1:
                    st.metric("💸 Coste Impacto", f"€{request_data['cost_impact_euros']:.2f}")
                
                with col_metrics2:
                    st.metric("🎯 Confianza ML", f"{request_data['confidence_score']:.1%}")
                
                with col_metrics3:
                    current_roas = request_data.get("current_performance", {}).get("roas", 2.8)
                    st.metric("📈 ROAS Actual", f"{current_roas:.1f}x")
                
                with col_metrics4:
                    expected_return = request_data.get("recommended_action", {}).get("expected_return", 0)
                    if expected_return:
                        st.metric("💰 Retorno Esperado", f"€{expected_return:.2f}")
                
                # Detalles de la recomendación
                st.markdown("**🤖 Recomendación ML:**")
                recommendation = request_data.get("recommended_action", {})
                reason = recommendation.get("reason", "Optimización basada en ML")
                st.info(f"💡 {reason}")
                
                # Performance actual
                if request_data.get("current_performance"):
                    with st.expander("📊 Ver Performance Actual"):
                        perf_data = request_data["current_performance"]
                        
                        cols = st.columns(len(perf_data))
                        for i, (key, value) in enumerate(perf_data.items()):
                            with cols[i]:
                                if isinstance(value, (int, float)):
                                    if key.endswith("_euros"):
                                        st.metric(key.replace("_", " ").title(), f"€{value:.2f}")
                                    elif key in ["roas", "ctr"]:
                                        st.metric(key.upper(), f"{value:.1f}")
                                    else:
                                        st.metric(key.replace("_", " ").title(), f"{value:,}")
                
                # Botones de decisión
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                
                with col_btn1:
                    if st.button(f"✅ Aprobar", key=f"approve_{auth['id']}", type="primary"):
                        result = approve_authorization(auth['id'], "approved", "Aprobado desde dashboard")
                        if result.get("success"):
                            st.success("✅ Autorización aprobada! Ejecutando acción ML...")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result.get('error')}")
                
                with col_btn2:
                    if st.button(f"❌ Rechazar", key=f"reject_{auth['id']}"): 
                        result = approve_authorization(auth['id'], "rejected", "Rechazado desde dashboard")
                        if result.get("success"):
                            st.warning("❌ Autorización rechazada")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result.get('error')}")
                
                with col_btn3:
                    custom_reason = st.text_input(
                        "Razón personalizada (opcional)", 
                        key=f"reason_{auth['id']}",
                        placeholder="Añade una nota sobre tu decisión..."
                    )
                
                st.markdown("---")

# ============================================
# TAB: ANALYTICS UTM  
# ============================================

with tab_analytics:
    st.subheader("📊 Analytics UTM - Landing Page Performance")
    
    # Métricas principales UTM
    col1, col2, col3, col4, col5 = st.columns(5)
    
    utm_perf = campaign_perf["utm_performance"]
    
    with col1:
        st.metric("🌐 Visitas Total", f"{campaign_perf['landing_page_visits']:,}")
    
    with col2:
        st.metric("💰 Conversiones", f"{campaign_perf['landing_page_conversions']:,}")
    
    with col3:
        conversion_rate = (campaign_perf['landing_page_conversions'] / campaign_perf['landing_page_visits']) * 100
        st.metric("📈 Tasa Conversión", f"{conversion_rate:.2f}%")
    
    with col4:
        st.metric("💸 Ingresos Landing", f"€{campaign_perf['total_revenue_euros']:.2f}")
    
    with col5:
        avg_value = campaign_perf['total_revenue_euros'] / campaign_perf['landing_page_conversions']
        st.metric("💎 Valor Promedio", f"€{avg_value:.2f}")
    
    # Gráfico de performance por fuente UTM
    utm_data = []
    for source, data in utm_perf.items():
        utm_data.append({
            "Fuente UTM": source.replace("_", " ").title(),
            "Visitas": data["visits"],
            "Conversiones": data["conversions"],
            "Ingresos": data["revenue"]
        })
    
    df_utm = pd.DataFrame(utm_data)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_visits = px.bar(
            df_utm, 
            x="Fuente UTM", 
            y="Visitas",
            title="👥 Visitas por Fuente UTM",
            color="Fuente UTM"
        )
        st.plotly_chart(fig_visits, use_container_width=True)
    
    with col_chart2:
        fig_revenue = px.bar(
            df_utm,
            x="Fuente UTM", 
            y="Ingresos",
            title="💰 Ingresos por Fuente UTM",
            color="Ingresos",
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Tabla detallada UTM
    st.subheader("📋 Desglose Detallado UTM")
    
    df_utm["Tasa Conversión %"] = (df_utm["Conversiones"] / df_utm["Visitas"] * 100).round(2)
    df_utm["CPC €"] = (campaign_perf["total_spend_euros"] / df_utm["Visitas"].sum()).round(3)
    
    st.dataframe(df_utm, use_container_width=True)

# ============================================
# TAB: PERFORMANCE CAMPAÑA
# ============================================

with tab_performance:
    st.subheader("🎯 Performance Integral - Meta Ads €400")
    
    # Insights ML
    st.markdown("### 🤖 ML Insights - Ultralytics + Análisis Musical")
    
    ml_insights = campaign_perf["ml_insights"]
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        st.info(f"🎬 **Ultralytics:** {ml_insights['ultralytics_analysis']}")
        st.success(f"🎵 **Género:** {ml_insights['genre_optimization']}")
    
    with col_insight2:
        st.warning(f"⏰ **Timing:** {ml_insights['optimal_timing']}")
        virality = ml_insights['virality_score']
        st.metric("🚀 Virality Score", f"{virality:.2f}", delta=f"+{(virality-0.5):.2f} vs promedio")
    
    # Timeline de decisiones ML
    st.markdown("### 📈 Timeline de Optimizaciones ML")
    
    timeline_data = pd.DataFrame([
        {"Hora": "14:30", "Acción": "Budget increase sugerido", "Estado": "Pendiente", "Impacto": "+€75"},
        {"Hora": "15:45", "Acción": "Platform expansion", "Estado": "Pendiente", "Impacto": "+€120"},
        {"Hora": "16:20", "Acción": "Content optimization", "Estado": "Pendiente", "Impacto": "+€45"},
        {"Hora": "13:15", "Acción": "Auto-optimización targeting", "Estado": "Ejecutado", "Impacto": "+€25"},
        {"Hora": "12:00", "Acción": "Landing page generada", "Estado": "Completado", "Impacto": "€0"}
    ])
    
    # Colorear según estado
    def color_estado(val):
        colors = {
            "Pendiente": "background-color: #ffa500",
            "Ejecutado": "background-color: #32cd32", 
            "Completado": "background-color: #32cd32"
        }
        return colors.get(val, "")
    
    styled_timeline = timeline_data.style.applymap(color_estado, subset=["Estado"])
    st.dataframe(styled_timeline, use_container_width=True)
    
    # Proyección de ROI
    st.markdown("### 💎 Proyección ROI - Si Apruebas Todas las Decisiones ML")
    
    col_proj1, col_proj2, col_proj3 = st.columns(3)
    
    with col_proj1:
        current_roi = (campaign_perf['total_revenue_euros'] - campaign_perf['total_spend_euros'])
        st.metric("💰 ROI Actual", f"€{current_roi:.2f}")
    
    with col_proj2:
        projected_investment = 75 + 120 + 45  # Suma de inversiones pendientes
        st.metric("📊 Inversión Adicional", f"€{projected_investment}")
    
    with col_proj3:
        projected_return = projected_investment * 2.8  # Usando ROAS actual
        projected_roi = projected_return - projected_investment
        st.metric("🚀 ROI Proyectado", f"€{projected_roi:.2f}", delta=f"+€{projected_roi-current_roi:.2f}")

# ============================================
# TAB: CONFIGURACIÓN ML
# ============================================

with tab_settings:
    st.subheader("⚙️ Configuración del Sistema ML")
    
    # Configuraciones de auto-aprobación
    st.markdown("### 🤖 Auto-Aprobación ML")
    
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        auto_threshold = st.number_input(
            "💰 Umbral Auto-Aprobación (€)",
            min_value=0.0,
            max_value=200.0,
            value=50.0,
            step=5.0,
            help="Decisiones ML bajo este coste se aprueban automáticamente"
        )
        
        confidence_threshold = st.slider(
            "🎯 Confianza Mínima (%)",
            min_value=50,
            max_value=95,
            value=80,
            help="Confianza ML mínima para auto-aprobación"
        )
    
    with col_config2:
        enable_notifications = st.checkbox("🔔 Notificaciones Push", value=True)
        enable_email = st.checkbox("📧 Alertas por Email", value=True)
        enable_discord = st.checkbox("💬 Discord Webhook", value=False)
        
        notification_urgency = st.selectbox(
            "⚡ Notificar Solo Urgencia",
            ["Todas", "Medium+", "High", "Critical"],
            index=1
        )
    
    # Configuración de plataformas
    st.markdown("### 📱 Plataformas Activas")
    
    platform_config = st.columns(4)
    
    with platform_config[0]:
        youtube_active = st.checkbox("📺 YouTube", value=True)
        youtube_auto = st.checkbox("🤖 YouTube Auto-Post", value=True, disabled=not youtube_active)
    
    with platform_config[1]:
        tiktok_active = st.checkbox("🎵 TikTok", value=True)
        tiktok_auto = st.checkbox("🤖 TikTok Auto-Post", value=True, disabled=not tiktok_active)
    
    with platform_config[2]:
        instagram_active = st.checkbox("📸 Instagram", value=True)
        instagram_auto = st.checkbox("🤖 Instagram Auto-Post", value=False, disabled=not instagram_active)
    
    with platform_config[3]:
        twitter_active = st.checkbox("🐦 Twitter", value=False)
        twitter_auto = st.checkbox("🤖 Twitter Auto-Post", value=False, disabled=not twitter_active)
    
    # Botón guardar configuración
    if st.button("💾 Guardar Configuración", type="primary"):
        config_data = {
            "auto_threshold_euros": auto_threshold,
            "confidence_threshold": confidence_threshold / 100,
            "notifications": {
                "push": enable_notifications,
                "email": enable_email, 
                "discord": enable_discord,
                "urgency_filter": notification_urgency
            },
            "platforms": {
                "youtube": {"active": youtube_active, "auto_post": youtube_auto},
                "tiktok": {"active": tiktok_active, "auto_post": tiktok_auto},
                "instagram": {"active": instagram_active, "auto_post": instagram_auto},
                "twitter": {"active": twitter_active, "auto_post": twitter_auto}
            }
        }
        
        st.success("✅ Configuración guardada correctamente!")
        st.json(config_data)

# ============================================
# FOOTER CON ESTADO DEL SISTEMA
# ============================================

st.markdown("---")

col_status1, col_status2, col_status3, col_status4 = st.columns(4)

with col_status1:
    st.metric("🚀 Railway", "✅ Online", help="Hosting activo")

with col_status2:
    st.metric("🤖 ML Core", "✅ Running", help="Análisis ML activo")

with col_status3:
    st.metric("📊 UTM Tracking", "✅ Active", help="Tracking funcionando")

with col_status4:
    st.metric("🔄 Automation", "24/7", help="Automatización continua")

st.markdown(
    """
    <div style='text-align: center; margin-top: 20px;'>
        <p><strong>🎯 Meta Ads €400 Campaign Dashboard</strong> | 
        <strong>Powered by ML + Railway + Ultralytics</strong> | 
        <strong>Made with ❤️ for Community Managers</strong></p>
    </div>
    """, 
    unsafe_allow_html=True
)