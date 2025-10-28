"""
🎨 COMMUNITY MANAGER DASHBOARD - Sistema Unificado V3
Dashboard Streamlit para lanzar campañas virales con un click

Features:
- Lanzar campañas multi-plataforma
- Monitorear analytics en tiempo real
- Optimizar campañas activas
- Ver recomendaciones ML
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from unified_system_v3 import UnifiedCommunityManagerSystem
import sys
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Community Manager Dashboard v3",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.big-font {
    font-size:50px !important;
    font-weight:bold;
    text-align:center;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'system' not in st.session_state:
    st.session_state.system = UnifiedCommunityManagerSystem(dummy_mode=True)
    st.session_state.campaign_launched = False
    st.session_state.campaign_results = None
    st.session_state.analytics = None

# ============================================
# HEADER
# ============================================

st.markdown('<p class="big-font">🚀 Community Manager Dashboard</p>', unsafe_allow_html=True)
st.markdown("### Sistema Unificado de Lanzamiento Viral v3.0")

st.divider()

# ============================================
# SIDEBAR - CAMPAIGN CONFIG
# ============================================

with st.sidebar:
    st.header("⚙️ Configuración de Campaña")
    
    st.subheader("📹 Video")
    video_file = st.file_uploader("Upload video", type=['mp4', 'mov', 'avi'])
    if not video_file:
        video_path = st.text_input("O ingresa path:", value="/data/videos/nueva_vida_official.mp4")
    else:
        video_path = f"/tmp/{video_file.name}"
    
    st.subheader("🎤 Artista")
    artist_name = st.text_input("Nombre del artista:", value="Stakas")
    song_name = st.text_input("Nombre de la canción:", value="Nueva Vida")
    genre = st.selectbox("Género:", ["Trap", "Reggaeton", "Hip Hop", "Pop", "Rock", "Electrónica"])
    
    st.subheader("💰 Meta Ads")
    daily_budget = st.slider("Budget diario ($):", 20, 200, 50, 10)
    
    st.subheader("🌎 Targeting")
    countries = st.multiselect(
        "Países target:",
        ["US", "MX", "ES", "AR", "CL", "CO", "PE", "BR"],
        default=["US", "MX", "ES"]
    )
    
    st.divider()
    
    # System status
    st.subheader("📊 System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Mode", "DUMMY" if st.session_state.system.dummy_mode else "PROD")
    with col2:
        status = "🟢 Active" if st.session_state.campaign_launched else "⚫ Idle"
        st.markdown(f"**Status:** {status}")

# ============================================
# MAIN AREA
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["🚀 Launch", "📊 Analytics", "🎯 Optimize", "📝 History"])

# --------------------------------------------
# TAB 1: LAUNCH CAMPAIGN
# --------------------------------------------

with tab1:
    st.header("🎬 Lanzar Campaña Viral")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Workflow Automático:
        
        1. **📋 Preparación**: Thumbnails, captions, hashtags
        2. **📱 Publicación**: YouTube, TikTok (10 cuentas), IG (5 cuentas), Twitter, Facebook
        3. **💰 Meta Ads**: Campaign con targeting inteligente
        4. **🤖 Engagement**: Automation con Device Farm + GoLogin
        5. **📊 Tracking**: Facebook Pixel + Conversion API
        
        **Todo en un click! 🚀**
        """)
    
    with col2:
        st.markdown("### Preview:")
        st.info(f"""
        **Artista:** {artist_name}
        **Canción:** {song_name}
        **Género:** {genre}
        
        **Plataformas:** 5
        **Cuentas:** 18 total
        **Budget:** ${daily_budget}/día
        **Países:** {len(countries)}
        """)
    
    st.divider()
    
    # Launch button
    if not st.session_state.campaign_launched:
        if st.button("🚀 LANZAR CAMPAÑA", type="primary", use_container_width=True):
            with st.spinner("🚀 Lanzando campaña en todas las plataformas..."):
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                async def launch():
                    status_text.text("📋 Preparando assets...")
                    progress_bar.progress(20)
                    await asyncio.sleep(0.5)
                    
                    status_text.text("📱 Publicando en plataformas...")
                    progress_bar.progress(40)
                    
                    results = await st.session_state.system.launch_viral_video_campaign(
                        video_path=video_path,
                        artist_name=artist_name,
                        song_name=song_name,
                        genre=genre,
                        daily_ad_budget=daily_budget,
                        target_countries=countries
                    )
                    
                    status_text.text("💰 Creando Meta Ads campaign...")
                    progress_bar.progress(60)
                    await asyncio.sleep(0.5)
                    
                    status_text.text("🤖 Activando engagement automation...")
                    progress_bar.progress(80)
                    await asyncio.sleep(0.5)
                    
                    status_text.text("📊 Configurando tracking...")
                    progress_bar.progress(100)
                    
                    return results
                
                # Run async
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(launch())
                loop.close()
                
                st.session_state.campaign_results = results
                st.session_state.campaign_launched = True
                
                st.success("✅ ¡Campaña lanzada exitosamente!")
                st.balloons()
    
    # Show results if campaign launched
    if st.session_state.campaign_launched and st.session_state.campaign_results:
        st.markdown("---")
        st.subheader("✅ Campaña Lanzada")
        
        results = st.session_state.campaign_results
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Plataformas", len(results.get("platforms", {})))
        
        with col2:
            total_accounts = len(results.get("platforms", {}).get("tiktok", {}).get("accounts", [])) + \
                           len(results.get("platforms", {}).get("instagram", {}).get("accounts", []))
            st.metric("Cuentas Activas", total_accounts)
        
        with col3:
            st.metric("Meta Ads", f"${daily_budget}/día")
        
        with col4:
            reach = st.session_state.system._estimate_reach(results)
            st.metric("Alcance Est.", reach)
        
        # Platform details
        st.markdown("#### 📱 URLs Publicadas:")
        
        platforms = results.get("platforms", {})
        
        if "youtube" in platforms:
            st.markdown(f"🎥 **YouTube:** [{platforms['youtube']['url']}]({platforms['youtube']['url']})")
        
        if "tiktok" in platforms:
            with st.expander(f"📱 TikTok ({len(platforms['tiktok']['accounts'])} cuentas)"):
                for acc in platforms['tiktok']['accounts'][:5]:  # Show first 5
                    st.markdown(f"- [{acc['username']}]({acc['url']})")
        
        if "instagram" in platforms:
            with st.expander(f"📸 Instagram ({len(platforms['instagram']['accounts'])} cuentas)"):
                for acc in platforms['instagram']['accounts']:
                    st.markdown(f"- [{acc['username']}]({acc['url']})")
        
        if "twitter" in platforms:
            st.markdown(f"🐦 **Twitter:** [{platforms['twitter']['url']}]({platforms['twitter']['url']})")

# --------------------------------------------
# TAB 2: ANALYTICS
# --------------------------------------------

with tab2:
    st.header("📊 Analytics en Tiempo Real")
    
    if not st.session_state.campaign_launched:
        st.info("👉 Lanza una campaña primero para ver analytics")
    else:
        # Refresh button
        if st.button("🔄 Actualizar Analytics"):
            async def get_analytics():
                return await st.session_state.system.get_campaign_analytics()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            st.session_state.analytics = loop.run_until_complete(get_analytics())
            loop.close()
        
        if st.session_state.analytics:
            analytics = st.session_state.analytics
            
            # Top metrics
            st.subheader("🎯 Métricas Globales")
            
            col1, col2, col3, col4 = st.columns(4)
            
            totals = analytics.get("totals", {})
            
            with col1:
                st.metric("Total Views", f"{totals.get('total_views', 0):,}")
            
            with col2:
                st.metric("Total Engagement", f"{totals.get('total_engagement', 0):,}")
            
            with col3:
                st.metric("Estimated Reach", f"{totals.get('estimated_reach', 0):,}")
            
            with col4:
                viral_score = totals.get('viral_score', 0)
                st.metric("Viral Score", f"{viral_score}/10", delta=f"+{viral_score-5}")
            
            st.divider()
            
            # Platform breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📱 Por Plataforma")
                
                platforms = analytics.get("platforms", {})
                
                if "tiktok" in platforms:
                    tiktok = platforms["tiktok"]
                    st.markdown("### 📱 TikTok")
                    st.metric("Total Views", f"{tiktok['total_views']:,}")
                    st.metric("Likes", f"{tiktok['total_likes']:,}")
                    st.metric("Viral Probability", f"{tiktok['viral_probability']*100:.0f}%")
                
                if "instagram" in platforms:
                    ig = platforms["instagram"]
                    st.markdown("### 📸 Instagram")
                    st.metric("Total Views", f"{ig['total_views']:,}")
                    st.metric("Likes", f"{ig['total_likes']:,}")
                
                if "youtube" in platforms:
                    yt = platforms["youtube"]
                    st.markdown("### 🎥 YouTube")
                    st.metric("Views", f"{yt['views']:,}")
                    st.metric("Likes", f"{yt['likes']:,}")
            
            with col2:
                st.subheader("💰 Meta Ads Performance")
                
                meta = analytics.get("meta_ads", {})
                
                if meta:
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.metric("Impressions", f"{meta.get('impressions', 0):,}")
                        st.metric("Clicks", f"{meta.get('clicks', 0):,}")
                        st.metric("Spend", f"${meta.get('spend', 0):.2f}")
                    
                    with col_b:
                        st.metric("CTR", f"{meta.get('ctr', 0):.1f}%")
                        st.metric("Landing Views", f"{meta.get('landing_page_views', 0):,}")
                        st.metric("Cost/View", f"${meta.get('cost_per_view', 0):.3f}")
                
                st.divider()
                
                st.subheader("🤖 Engagement Automation")
                
                engagement = analytics.get("engagement_automation", {})
                
                if engagement:
                    st.metric("Likes Dados", f"{engagement.get('likes_given', 0):,}")
                    st.metric("Comentarios", f"{engagement.get('comments_posted', 0)}")
                    st.metric("Cuentas Bot", f"{engagement.get('accounts_used', 0)}")
            
            # Recommendations
            st.divider()
            st.subheader("💡 Recomendaciones ML")
            
            recommendations = analytics.get("recommendations", [])
            
            for i, rec in enumerate(recommendations):
                st.markdown(f"{i+1}. {rec}")

# --------------------------------------------
# TAB 3: OPTIMIZE
# --------------------------------------------

with tab3:
    st.header("🎯 Optimización Automática")
    
    if not st.session_state.campaign_launched:
        st.info("👉 Lanza una campaña primero para optimizar")
    else:
        st.markdown("""
        ### Sistema de Optimización ML
        
        El sistema analiza performance en tiempo real y sugiere/aplica optimizaciones:
        
        - 📈 **Budget Optimization**: Ajusta presupuesto basado en ROAS
        - 🎯 **Targeting Refinement**: Mejora audiences
        - 🤖 **Engagement Boost**: Aumenta actividad en posts high-performing
        - 📊 **Creative Testing**: A/B testing de thumbnails/captions
        """)
        
        st.divider()
        
        if st.button("🎯 Optimizar Campaña", type="primary"):
            with st.spinner("Analizando performance y aplicando optimizaciones..."):
                async def optimize():
                    return await st.session_state.system.optimize_ongoing_campaign()
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                optimizations = loop.run_until_complete(optimize())
                loop.close()
                
                if optimizations.get("optimizations_applied", 0) > 0:
                    st.success(f"✅ {optimizations['optimizations_applied']} optimizaciones aplicadas")
                    
                    st.markdown(f"**Impacto Estimado:** {optimizations.get('estimated_impact', 'N/A')}")
                    
                    st.markdown("#### Cambios Aplicados:")
                    
                    for opt in optimizations.get("optimizations", []):
                        with st.expander(f"🔧 {opt['action'].replace('_', ' ').title()} - {opt['platform']}"):
                            st.json(opt)
                else:
                    st.info("ℹ️ No se encontraron optimizaciones necesarias en este momento")

# --------------------------------------------
# TAB 4: HISTORY
# --------------------------------------------

with tab4:
    st.header("📝 Historial de Campañas")
    
    st.info("🚧 Feature en desarrollo - próximamente mostrará todas las campañas lanzadas")
    
    if st.session_state.campaign_results:
        st.markdown("### Campaña Actual")
        
        with st.expander("Ver JSON completo"):
            st.json(st.session_state.campaign_results)

# ============================================
# FOOTER
# ============================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Sistema:** v3.0 Unified")

with col2:
    st.markdown("**Status:** 🟢 Operational")

with col3:
    st.markdown(f"**Última actualización:** {datetime.now().strftime('%H:%M:%S')}")
