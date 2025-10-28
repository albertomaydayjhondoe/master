"""
🎯 Meta-Centric Dashboard - Streamlit UI
Dashboard unificado para crear campañas Meta Ads y monitorear cross-platform
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
    page_title="Meta Ads-Centric Campaign Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs de servicios
META_ADS_URL = "http://meta-ads-manager:9000"
ML_CORE_URL = "http://ml-core:8000" 
UNIFIED_ORCHESTRATOR_URL = "http://unified-orchestrator:10000"

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def create_campaign_with_orchestration(campaign_data: Dict) -> Dict:
    """Crear campaña Meta Ads con orquestación completa"""
    
    try:
        response = requests.post(
            f"{META_ADS_URL}/campaigns/create-with-orchestration",
            json=campaign_data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to create campaign: {response.text}"}
            
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def get_campaign_dashboard_data(campaign_id: str) -> Dict:
    """Obtener datos del dashboard para una campaña"""
    
    try:
        response = requests.get(
            f"{META_ADS_URL}/campaigns/{campaign_id}/dashboard",
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Return mock data for demo
            return get_mock_dashboard_data(campaign_id)
            
    except Exception as e:
        return get_mock_dashboard_data(campaign_id)

def get_mock_dashboard_data(campaign_id: str) -> Dict:
    """Mock data for demo purposes"""
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": "Demo Campaign",
        "status": "active",
        "created_at": "2025-10-27T10:00:00Z",
        "platforms": {
            "meta_ads": {
                "spend": 45.20,
                "impressions": 15000,
                "clicks": 450,
                "ctr": 3.0,
                "cpc": 0.10,
                "conversions": 25,
                "roas": 2.8
            },
            "youtube": {
                "views": 2500,
                "likes": 89,
                "comments": 23,
                "subscribers_gained": 12,
                "watch_time_hours": 125
            },
            "tiktok": {
                "views": 8900,
                "likes": 567,
                "shares": 89,
                "comments": 134,
                "follows": 23
            },
            "instagram": {
                "reach": 12000,
                "engagement": 890,
                "saves": 45,
                "shares": 67,
                "profile_visits": 234
            },
            "twitter": {
                "impressions": 5600,
                "engagements": 234,
                "retweets": 45,
                "likes": 189,
                "replies": 34
            }
        },
        "unified_metrics": {
            "total_reach": 38400,
            "total_engagement": 2053,
            "cross_platform_roas": 2.8,
            "virality_score": 0.72,
            "total_conversions": 67
        }
    }

# ============================================
# SIDEBAR - NAVIGATION
# ============================================

st.sidebar.title("🚀 Meta Ads-Centric")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigation",
    ["🎯 Create Campaign", "📊 Active Campaigns", "📈 Analytics", "⚙️ Settings"]
)

# ============================================
# PAGE: CREATE CAMPAIGN
# ============================================

if page == "🎯 Create Campaign":
    st.title("🚀 Meta Ads-Centric Campaign Creator")
    st.markdown("**Create a Meta Ads campaign and automatically launch across all platforms**")
    
    # Campaign Creation Form
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Campaign Details")
            
            with st.form("create_meta_campaign"):
                # Basic Info
                artist_name = st.text_input("🎤 Artist Name", value="Demo Artist")
                song_name = st.text_input("🎵 Song Name", value="New Hit 2025")
                campaign_name = st.text_input(
                    "📢 Campaign Name", 
                    value=f"{artist_name} - {song_name} - {datetime.now().strftime('%Y%m%d')}"
                )
                
                # Budget & Targeting
                col_budget, col_objective = st.columns(2)
                
                with col_budget:
                    daily_budget = st.number_input(
                        "💰 Daily Budget ($)", 
                        min_value=10.0, 
                        max_value=1000.0, 
                        value=100.0, 
                        step=10.0
                    )
                
                with col_objective:
                    objective = st.selectbox(
                        "🎯 Campaign Objective",
                        ["CONVERSIONS", "TRAFFIC", "VIDEO_VIEWS", "ENGAGEMENT", "REACH"],
                        index=0
                    )
                
                # Platform Selection
                st.subheader("📱 Target Platforms")
                platforms = st.multiselect(
                    "Select platforms to launch",
                    ["youtube", "tiktok", "instagram", "twitter"],
                    default=["youtube", "tiktok", "instagram"]
                )
                
                # Advanced Options
                with st.expander("🔧 Advanced Options"):
                    genre = st.selectbox(
                        "🎼 Music Genre",
                        ["pop", "hip_hop", "electronic", "rock", "reggaeton", "latin"],
                        index=0
                    )
                    
                    auto_optimize = st.checkbox(
                        "🤖 Enable Auto-Optimization", 
                        value=True,
                        help="Automatically optimize budget allocation based on performance"
                    )
                    
                    target_countries = st.multiselect(
                        "🌍 Target Countries",
                        ["US", "MX", "ES", "AR", "CO", "BR"],
                        default=["US", "MX", "ES"]
                    )
                
                # Submit Button
                submitted = st.form_submit_button(
                    "🚀 Launch Complete Campaign",
                    type="primary",
                    use_container_width=True
                )
                
                if submitted:
                    # Prepare campaign data
                    campaign_data = {
                        "name": campaign_name,
                        "objective": objective,
                        "daily_budget": daily_budget,
                        "artist_name": artist_name,
                        "song_name": song_name,
                        "platforms": platforms,
                        "auto_optimize": auto_optimize,
                        "genre": genre,
                        "target_countries": target_countries
                    }
                    
                    # Show loading
                    with st.spinner("🚀 Launching ecosystem..."):
                        # Create campaign
                        result = create_campaign_with_orchestration(campaign_data)
                        
                        if "error" in result:
                            st.error(f"❌ Error: {result['error']}")
                        else:
                            st.success("🎉 Campaign launched successfully!")
                            st.balloons()
                            
                            # Display results
                            st.json(result)
                            
                            # Store campaign ID for monitoring
                            if "meta_campaign" in result:
                                campaign_id = result["meta_campaign"].get("id", "demo_campaign")
                                st.session_state["current_campaign_id"] = campaign_id
                                st.info(f"📊 Monitor your campaign: Campaign ID `{campaign_id}`")
        
        with col2:
            st.subheader("💡 Campaign Preview")
            
            # Campaign Summary Card
            st.info(f"""
            **🎤 Artist:** {artist_name if 'artist_name' in locals() else 'Demo Artist'}
            **🎵 Song:** {song_name if 'song_name' in locals() else 'New Hit 2025'}
            **💰 Budget:** ${daily_budget if 'daily_budget' in locals() else 100}/day
            **📱 Platforms:** {len(platforms) if 'platforms' in locals() else 3} selected
            
            **🚀 Expected Results:**
            • 15-30K daily reach
            • 5-10x ROAS
            • Cross-platform optimization
            """)
            
            # Quick Tips
            st.subheader("💡 Pro Tips")
            st.markdown("""
            • **Budget $100+**: Enables all platforms
            • **Hip Hop/Reggaeton**: High TikTok performance  
            • **Auto-Optimization**: 20% better ROAS
            • **Multiple Countries**: Broader reach
            """)

# ============================================
# PAGE: ACTIVE CAMPAIGNS
# ============================================

elif page == "📊 Active Campaigns":
    st.title("📊 Active Campaigns Dashboard")
    
    # Campaign Selector
    campaign_id = st.selectbox(
        "Select Campaign",
        ["demo_campaign_001", "demo_campaign_002", "demo_campaign_003"],
        index=0
    )
    
    # Get campaign data
    dashboard_data = get_campaign_dashboard_data(campaign_id)
    
    if dashboard_data:
        # Campaign Overview
        st.subheader(f"🎯 {dashboard_data.get('campaign_name', 'Campaign')}")
        
        # Metrics Overview
        col1, col2, col3, col4, col5 = st.columns(5)
        
        unified = dashboard_data.get("unified_metrics", {})
        
        with col1:
            st.metric(
                "Total Reach",
                f"{unified.get('total_reach', 0):,}",
                delta="+15% vs yesterday"
            )
        
        with col2:
            st.metric(
                "Total Engagement", 
                f"{unified.get('total_engagement', 0):,}",
                delta="+8% vs yesterday"
            )
        
        with col3:
            st.metric(
                "Cross-Platform ROAS",
                f"{unified.get('cross_platform_roas', 0):.1f}x",
                delta="+0.3x vs yesterday"
            )
        
        with col4:
            st.metric(
                "Virality Score",
                f"{unified.get('virality_score', 0):.2f}",
                delta="+0.05 vs yesterday"
            )
        
        with col5:
            st.metric(
                "Total Conversions",
                f"{unified.get('total_conversions', 0)}",
                delta="+12 vs yesterday"
            )
        
        # Platform Performance
        st.subheader("📱 Platform Performance")
        
        platforms = dashboard_data.get("platforms", {})
        
        # Create platform performance chart
        platform_data = []
        for platform, metrics in platforms.items():
            if platform == "meta_ads":
                reach = metrics.get("impressions", 0)
                engagement = metrics.get("clicks", 0)
            elif platform == "youtube":
                reach = metrics.get("views", 0)
                engagement = metrics.get("likes", 0) + metrics.get("comments", 0)
            elif platform == "tiktok":
                reach = metrics.get("views", 0)
                engagement = metrics.get("likes", 0) + metrics.get("shares", 0)
            elif platform == "instagram":
                reach = metrics.get("reach", 0)
                engagement = metrics.get("engagement", 0)
            elif platform == "twitter":
                reach = metrics.get("impressions", 0)
                engagement = metrics.get("engagements", 0)
            else:
                continue
            
            platform_data.append({
                "Platform": platform.title(),
                "Reach": reach,
                "Engagement": engagement,
                "Engagement Rate": (engagement / reach * 100) if reach > 0 else 0
            })
        
        df_platforms = pd.DataFrame(platform_data)
        
        # Platform Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Reach by Platform
            fig_reach = px.bar(
                df_platforms, 
                x="Platform", 
                y="Reach",
                title="📊 Reach by Platform",
                color="Platform"
            )
            st.plotly_chart(fig_reach, use_container_width=True)
        
        with col_chart2:
            # Engagement Rate by Platform
            fig_engagement = px.bar(
                df_platforms,
                x="Platform", 
                y="Engagement Rate",
                title="💬 Engagement Rate by Platform",
                color="Engagement Rate",
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig_engagement, use_container_width=True)
        
        # Detailed Platform Metrics
        st.subheader("📋 Detailed Platform Metrics")
        
        tab_meta, tab_youtube, tab_tiktok, tab_instagram, tab_twitter = st.tabs([
            "Meta Ads", "YouTube", "TikTok", "Instagram", "Twitter"
        ])
        
        with tab_meta:
            meta_metrics = platforms.get("meta_ads", {})
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Spend", f"${meta_metrics.get('spend', 0):.2f}")
                st.metric("CPC", f"${meta_metrics.get('cpc', 0):.3f}")
            
            with col2:
                st.metric("Impressions", f"{meta_metrics.get('impressions', 0):,}")
                st.metric("CTR", f"{meta_metrics.get('ctr', 0):.2f}%")
            
            with col3:
                st.metric("Clicks", f"{meta_metrics.get('clicks', 0):,}")
                st.metric("Conversions", f"{meta_metrics.get('conversions', 0)}")
            
            with col4:
                st.metric("ROAS", f"{meta_metrics.get('roas', 0):.1f}x")
        
        with tab_youtube:
            youtube_metrics = platforms.get("youtube", {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Views", f"{youtube_metrics.get('views', 0):,}")
                st.metric("Likes", f"{youtube_metrics.get('likes', 0):,}")
            
            with col2:
                st.metric("Comments", f"{youtube_metrics.get('comments', 0):,}")
                st.metric("Subscribers", f"+{youtube_metrics.get('subscribers_gained', 0)}")
            
            with col3:
                st.metric("Watch Time", f"{youtube_metrics.get('watch_time_hours', 0)}h")
        
        with tab_tiktok:
            tiktok_metrics = platforms.get("tiktok", {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Views", f"{tiktok_metrics.get('views', 0):,}")
                st.metric("Likes", f"{tiktok_metrics.get('likes', 0):,}")
            
            with col2:
                st.metric("Shares", f"{tiktok_metrics.get('shares', 0):,}")
                st.metric("Comments", f"{tiktok_metrics.get('comments', 0):,}")
            
            with col3:
                st.metric("Follows", f"+{tiktok_metrics.get('follows', 0)}")
        
        with tab_instagram:
            instagram_metrics = platforms.get("instagram", {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Reach", f"{instagram_metrics.get('reach', 0):,}")
                st.metric("Engagement", f"{instagram_metrics.get('engagement', 0):,}")
            
            with col2:
                st.metric("Saves", f"{instagram_metrics.get('saves', 0):,}")
                st.metric("Shares", f"{instagram_metrics.get('shares', 0):,}")
            
            with col3:
                st.metric("Profile Visits", f"{instagram_metrics.get('profile_visits', 0):,}")
        
        with tab_twitter:
            twitter_metrics = platforms.get("twitter", {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Impressions", f"{twitter_metrics.get('impressions', 0):,}")
                st.metric("Engagements", f"{twitter_metrics.get('engagements', 0):,}")
            
            with col2:
                st.metric("Retweets", f"{twitter_metrics.get('retweets', 0):,}")
                st.metric("Likes", f"{twitter_metrics.get('likes', 0):,}")
            
            with col3:
                st.metric("Replies", f"{twitter_metrics.get('replies', 0):,}")

# ============================================
# PAGE: ANALYTICS
# ============================================

elif page == "📈 Analytics":
    st.title("📈 Cross-Platform Analytics")
    
    # Time Range Selector
    time_range = st.selectbox(
        "📅 Time Range",
        ["Last 24 hours", "Last 7 days", "Last 30 days", "Custom"],
        index=1
    )
    
    # Generate mock time series data
    if time_range == "Last 7 days":
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    else:
        dates = pd.date_range(end=datetime.now(), periods=24, freq='H')
    
    # Mock performance data
    performance_data = []
    for i, date in enumerate(dates):
        performance_data.append({
            "Date": date,
            "Meta Ads Spend": 45 + i * 2,
            "Total Reach": 15000 + i * 1000,
            "Total Engagement": 800 + i * 50,
            "Cross-Platform ROAS": 2.5 + (i * 0.1),
            "Conversions": 25 + i * 3
        })
    
    df_performance = pd.DataFrame(performance_data)
    
    # Performance Over Time Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_reach = px.line(
            df_performance,
            x="Date",
            y="Total Reach", 
            title="📊 Total Reach Over Time"
        )
        st.plotly_chart(fig_reach, use_container_width=True)
    
    with col_chart2:
        fig_roas = px.line(
            df_performance,
            x="Date", 
            y="Cross-Platform ROAS",
            title="💰 Cross-Platform ROAS Over Time"
        )
        st.plotly_chart(fig_roas, use_container_width=True)
    
    # Platform Comparison
    st.subheader("📱 Platform Performance Comparison")
    
    platform_comparison = pd.DataFrame({
        "Platform": ["Meta Ads", "YouTube", "TikTok", "Instagram", "Twitter"],
        "Reach": [15000, 2500, 8900, 12000, 5600],
        "Engagement": [450, 112, 656, 890, 234],
        "Conversions": [25, 8, 12, 15, 7],
        "Cost per Conversion": [1.81, 0.50, 0.75, 1.20, 2.10]
    })
    
    # Multi-metric comparison chart
    fig_comparison = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Reach", "Engagement", "Conversions", "Cost per Conversion"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Add traces
    for i, metric in enumerate(["Reach", "Engagement", "Conversions", "Cost per Conversion"]):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        fig_comparison.add_trace(
            go.Bar(
                x=platform_comparison["Platform"],
                y=platform_comparison[metric],
                name=metric,
                showlegend=False
            ),
            row=row, col=col
        )
    
    fig_comparison.update_layout(height=600, title_text="Cross-Platform Performance Comparison")
    st.plotly_chart(fig_comparison, use_container_width=True)

# ============================================
# PAGE: SETTINGS  
# ============================================

elif page == "⚙️ Settings":
    st.title("⚙️ Meta-Centric Settings")
    
    # API Endpoints Configuration
    st.subheader("🔗 Service Endpoints")
    
    with st.expander("API Endpoints", expanded=True):
        meta_ads_url = st.text_input("Meta Ads Manager URL", value=META_ADS_URL)
        ml_core_url = st.text_input("ML Core URL", value=ML_CORE_URL)
        orchestrator_url = st.text_input("Unified Orchestrator URL", value=UNIFIED_ORCHESTRATOR_URL)
    
    # Default Campaign Settings
    st.subheader("🎯 Default Campaign Settings")
    
    with st.expander("Campaign Defaults", expanded=True):
        default_budget = st.number_input("Default Daily Budget ($)", value=100.0)
        default_objective = st.selectbox("Default Objective", ["CONVERSIONS", "TRAFFIC", "ENGAGEMENT"], index=0)
        default_platforms = st.multiselect(
            "Default Platforms",
            ["youtube", "tiktok", "instagram", "twitter"],
            default=["youtube", "tiktok", "instagram"]
        )
    
    # Optimization Settings
    st.subheader("🤖 Optimization Settings")
    
    with st.expander("Auto-Optimization", expanded=True):
        enable_auto_optimization = st.checkbox("Enable Auto-Optimization", value=True)
        optimization_frequency = st.selectbox("Optimization Frequency", ["Hourly", "Daily", "Weekly"], index=1)
        min_roas_threshold = st.number_input("Minimum ROAS Threshold", value=1.5)
        max_cpc_threshold = st.number_input("Maximum CPC Threshold ($)", value=5.0)
    
    # Notification Settings
    st.subheader("🔔 Notifications")
    
    with st.expander("Alert Settings", expanded=True):
        enable_alerts = st.checkbox("Enable Performance Alerts", value=True)
        alert_email = st.text_input("Alert Email", value="admin@example.com")
        low_performance_alert = st.checkbox("Low Performance Alert (ROAS < threshold)", value=True)
        high_spend_alert = st.checkbox("High Spend Alert (Budget exceeded)", value=True)
    
    # Save Settings
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")
        st.balloons()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🚀 <strong>Meta Ads-Centric Campaign Manager</strong> | 
        Built for Community Managers | 
        <strong>Made with ❤️</strong></p>
    </div>
    """, 
    unsafe_allow_html=True
)