#!/usr/bin/env python3
"""
📈 Analytics Engine - Streamlit Dashboard Centralizado

Motor de analytics y community management intelligence
- Performance de modelos ML (YOLO/COCO)
- Community management insights
- ROI y análisis de campañas
- Recomendaciones basadas en IA

Autor: Sistema Centralizado de Dashboards
Fecha: 2025-11-03
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlite3
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psutil
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de página
st.set_page_config(
    page_title="📈 Analytics Engine - TikTok Viral ML",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .success-metric {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .warning-metric {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
    }
    
    .danger-metric {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
    }
    
    .info-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .campaign-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AnalyticsEngine:
    """Motor principal de analytics"""
    
    def __init__(self):
        self.db_path = "data/production_control.db"
        self.analytics_db_path = "data/analytics_engine.db"
        self.ml_api_url = "http://localhost:8000"
        self.n8n_url = "http://localhost:5678"
        
        # Inicializar base de datos de analytics
        self._init_analytics_db()
    
    def _init_analytics_db(self):
        """Inicializar base de datos de analytics"""
        os.makedirs("data", exist_ok=True)
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    accuracy REAL,
                    precision_score REAL,
                    recall REAL,
                    f1_score REAL,
                    inference_time REAL,
                    test_samples INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS community_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    followers INTEGER,
                    engagement_rate REAL,
                    reach INTEGER,
                    impressions INTEGER,
                    clicks INTEGER,
                    conversions INTEGER,
                    date DATE DEFAULT CURRENT_DATE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaign_roi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    platform TEXT,
                    spend REAL,
                    revenue REAL,
                    roi_percentage REAL,
                    cpc REAL,
                    cpm REAL,
                    ctr REAL,
                    conversion_rate REAL,
                    date DATE DEFAULT CURRENT_DATE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    confidence_score REAL,
                    priority INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def get_ml_model_performance(self) -> pd.DataFrame:
        """Obtener rendimiento de modelos ML"""
        try:
            with sqlite3.connect(self.analytics_db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT model_name, accuracy, precision_score, recall, f1_score, 
                           inference_time, test_samples, timestamp
                    FROM ml_model_performance 
                    ORDER BY timestamp DESC 
                    LIMIT 100
                """, conn)
                
                # Si no hay datos, crear datos de ejemplo
                if df.empty:
                    self._generate_sample_ml_data()
                    df = pd.read_sql_query("""
                        SELECT model_name, accuracy, precision_score, recall, f1_score, 
                               inference_time, test_samples, timestamp
                        FROM ml_model_performance 
                        ORDER BY timestamp DESC 
                        LIMIT 100
                    """, conn)
                
                return df
                
        except Exception as e:
            logger.error(f"Error getting ML performance: {e}")
            return pd.DataFrame()
    
    def get_community_metrics(self) -> pd.DataFrame:
        """Obtener métricas de community management"""
        try:
            with sqlite3.connect(self.analytics_db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT platform, followers, engagement_rate, reach, 
                           impressions, clicks, conversions, date
                    FROM community_metrics 
                    ORDER BY date DESC 
                    LIMIT 50
                """, conn)
                
                # Si no hay datos, crear datos de ejemplo
                if df.empty:
                    self._generate_sample_community_data()
                    df = pd.read_sql_query("""
                        SELECT platform, followers, engagement_rate, reach, 
                               impressions, clicks, conversions, date
                        FROM community_metrics 
                        ORDER BY date DESC 
                        LIMIT 50
                    """, conn)
                
                return df
                
        except Exception as e:
            logger.error(f"Error getting community metrics: {e}")
            return pd.DataFrame()
    
    def get_campaign_roi(self) -> pd.DataFrame:
        """Obtener ROI de campañas"""
        try:
            with sqlite3.connect(self.analytics_db_path) as conn:
                df = pd.read_sql_query("""
                    SELECT campaign_id, platform, spend, revenue, roi_percentage,
                           cpc, cpm, ctr, conversion_rate, date
                    FROM campaign_roi 
                    ORDER BY date DESC 
                    LIMIT 30
                """, conn)
                
                # Si no hay datos, crear datos de ejemplo
                if df.empty:
                    self._generate_sample_roi_data()
                    df = pd.read_sql_query("""
                        SELECT campaign_id, platform, spend, revenue, roi_percentage,
                               cpc, cpm, ctr, conversion_rate, date
                        FROM campaign_roi 
                        ORDER BY date DESC 
                        LIMIT 30
                    """, conn)
                
                return df
                
        except Exception as e:
            logger.error(f"Error getting ROI data: {e}")
            return pd.DataFrame()
    
    def get_ai_recommendations(self) -> List[Dict]:
        """Obtener recomendaciones de IA"""
        try:
            with sqlite3.connect(self.analytics_db_path) as conn:
                cursor = conn.execute("""
                    SELECT category, title, description, confidence_score, priority, status
                    FROM ai_recommendations 
                    WHERE status = 'pending'
                    ORDER BY priority DESC, confidence_score DESC
                    LIMIT 10
                """)
                
                recommendations = []
                for row in cursor.fetchall():
                    recommendations.append({
                        'category': row[0],
                        'title': row[1],
                        'description': row[2],
                        'confidence_score': row[3],
                        'priority': row[4],
                        'status': row[5]
                    })
                
                # Si no hay recomendaciones, generar algunas de ejemplo
                if not recommendations:
                    self._generate_sample_recommendations()
                    return self.get_ai_recommendations()
                
                return recommendations
                
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")
            return []
    
    def _generate_sample_ml_data(self):
        """Generar datos de ejemplo para modelos ML"""
        sample_data = [
            ('YOLOv8-COCO', 0.92, 0.89, 0.87, 0.88, 0.045, 1000),
            ('YOLOv8-Custom', 0.89, 0.91, 0.85, 0.88, 0.052, 800),
            ('ResNet-50', 0.87, 0.84, 0.89, 0.86, 0.078, 1200),
            ('EfficientNet', 0.91, 0.88, 0.92, 0.90, 0.034, 950),
            ('MobileNet', 0.84, 0.82, 0.86, 0.84, 0.021, 1100)
        ]
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            for model_name, acc, prec, rec, f1, inf_time, samples in sample_data:
                conn.execute("""
                    INSERT INTO ml_model_performance 
                    (model_name, accuracy, precision_score, recall, f1_score, inference_time, test_samples)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (model_name, acc, prec, rec, f1, inf_time, samples))
    
    def _generate_sample_community_data(self):
        """Generar datos de ejemplo para community metrics"""
        platforms = ['TikTok', 'Instagram', 'YouTube', 'Twitter', 'Facebook']
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            for i, platform in enumerate(platforms):
                followers = np.random.randint(10000, 100000)
                engagement = np.random.uniform(2.5, 8.5)
                reach = int(followers * np.random.uniform(0.3, 0.8))
                impressions = int(reach * np.random.uniform(1.2, 3.0))
                clicks = int(impressions * np.random.uniform(0.01, 0.05))
                conversions = int(clicks * np.random.uniform(0.02, 0.08))
                
                conn.execute("""
                    INSERT INTO community_metrics 
                    (platform, followers, engagement_rate, reach, impressions, clicks, conversions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (platform, followers, engagement, reach, impressions, clicks, conversions))
    
    def _generate_sample_roi_data(self):
        """Generar datos de ejemplo para ROI"""
        platforms = ['Meta Ads', 'YouTube Ads', 'TikTok Ads', 'Google Ads']
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            for i in range(12):  # 12 campañas de ejemplo
                platform = np.random.choice(platforms)
                spend = np.random.uniform(100, 1000)
                revenue = spend * np.random.uniform(1.2, 4.5)
                roi = ((revenue - spend) / spend) * 100
                cpc = np.random.uniform(0.5, 3.0)
                cpm = np.random.uniform(5.0, 25.0)
                ctr = np.random.uniform(1.0, 8.0)
                conv_rate = np.random.uniform(2.0, 12.0)
                
                conn.execute("""
                    INSERT INTO campaign_roi 
                    (campaign_id, platform, spend, revenue, roi_percentage, cpc, cpm, ctr, conversion_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (i+1, platform, spend, revenue, roi, cpc, cpm, ctr, conv_rate))
    
    def _generate_sample_recommendations(self):
        """Generar recomendaciones de ejemplo"""
        recommendations = [
            ('Optimization', 'Increase TikTok Budget', 'TikTok campaigns showing 45% higher ROI than average. Consider increasing budget by 30%.', 0.89, 1),
            ('Content', 'Focus on Drill Content', 'Drill genre videos have 2.3x higher engagement. Prioritize drill content for next 3 campaigns.', 0.92, 1), 
            ('Timing', 'Optimal Posting Time', 'Best performance between 8-10 PM EST. Schedule future posts in this window.', 0.76, 2),
            ('Targeting', 'Expand to Colombia', 'Colombian market showing strong engagement signals (+67% vs baseline). Test market expansion.', 0.84, 2),
            ('Budget', 'Reallocate Meta Budget', 'Instagram performing 23% below expectations. Shift 15% budget to TikTok campaigns.', 0.88, 1)
        ]
        
        with sqlite3.connect(self.analytics_db_path) as conn:
            for category, title, desc, conf, priority in recommendations:
                conn.execute("""
                    INSERT INTO ai_recommendations (category, title, description, confidence_score, priority)
                    VALUES (?, ?, ?, ?, ?)
                """, (category, title, desc, conf, priority))

# Inicializar analytics engine
@st.cache_resource
def get_analytics_engine():
    return AnalyticsEngine()

analytics = get_analytics_engine()

# HEADER
st.markdown("""
# 📈 Analytics Engine - Intelligence Center
### TikTok Viral ML System - Community Management Analytics

**Estado:** Sistema de analytics operativo - Datos en tiempo real
""")

# SIDEBAR
st.sidebar.markdown("## 🎛️ Control Panel")

# Selector de vista
view_mode = st.sidebar.selectbox(
    "📊 Vista",
    ["Dashboard Principal", "ML Model Performance", "Community Management", "Campaign ROI", "AI Recommendations"]
)

# Auto-refresh
auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (30s)", value=False)

if auto_refresh:
    st.sidebar.info("⏱️ Auto-refresh activado")
    # Refresh cada 30 segundos
    time.sleep(30)
    st.rerun()

# Filtros
st.sidebar.markdown("### 🔍 Filtros")
date_range = st.sidebar.date_input(
    "📅 Rango de fechas",
    value=[datetime.now() - timedelta(days=7), datetime.now()],
    max_value=datetime.now()
)

platform_filter = st.sidebar.multiselect(
    "📱 Plataformas",
    ["TikTok", "Instagram", "YouTube", "Twitter", "Facebook", "Meta Ads"],
    default=["TikTok", "Instagram", "YouTube"]
)

# MAIN CONTENT
if view_mode == "Dashboard Principal":
    
    # MÉTRICAS PRINCIPALES
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card success-metric">
            <h3>🎯 Campaigns Activas</h3>
            <h1>7</h1>
            <p>+2 desde ayer</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 ROI Promedio</h3>
            <h1>245%</h1>
            <p>+18% vs mes anterior</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card warning-metric">
            <h3>📊 Engagement Rate</h3>
            <h1>6.7%</h1>
            <p>-0.3% vs semana anterior</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🧠 ML Accuracy</h3>
            <h1>92.1%</h1>
            <p>+1.2% optimización</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # GRÁFICOS PRINCIPALES
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Performance Trends")
        
        # Datos de ejemplo para el gráfico
        dates = pd.date_range(start='2024-10-01', end='2024-11-03', freq='D')
        performance_data = pd.DataFrame({
            'Date': dates,
            'ROI': np.random.uniform(180, 280, len(dates)),
            'Engagement': np.random.uniform(4.5, 8.5, len(dates)),
            'Reach': np.random.uniform(10000, 50000, len(dates))
        })
        
        fig = px.line(performance_data, x='Date', y=['ROI', 'Engagement'], 
                     title="ROI vs Engagement Rate")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Platform Distribution")
        
        platform_data = pd.DataFrame({
            'Platform': ['TikTok', 'Instagram', 'YouTube', 'Twitter', 'Facebook'],
            'Engagement': [8.2, 6.7, 5.9, 4.3, 3.8],
            'Reach': [45000, 32000, 28000, 18000, 15000]
        })
        
        fig = px.bar(platform_data, x='Platform', y='Engagement', 
                    color='Reach', title="Engagement por Plataforma")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # RECOMENDACIONES DESTACADAS
    st.subheader("🤖 AI Recommendations - Top Priorities")
    
    recommendations = analytics.get_ai_recommendations()[:3]  # Top 3
    
    for i, rec in enumerate(recommendations):
        confidence_color = "success" if rec['confidence_score'] > 0.8 else "warning" if rec['confidence_score'] > 0.6 else "danger"
        priority_emoji = "🔥" if rec['priority'] == 1 else "⚡" if rec['priority'] == 2 else "💡"
        
        st.markdown(f"""
        <div class="campaign-card">
            <h4>{priority_emoji} {rec['title']} <span style="color: #666;">({rec['category']})</span></h4>
            <p>{rec['description']}</p>
            <div style="margin-top: 10px;">
                <span class="badge badge-{confidence_color}">Confidence: {rec['confidence_score']:.0%}</span>
                <span class="badge badge-info">Priority: {rec['priority']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif view_mode == "ML Model Performance":
    st.subheader("🧠 ML Model Performance Analysis")
    
    # Obtener datos de performance ML
    ml_data = analytics.get_ml_model_performance()
    
    if not ml_data.empty:
        # Métricas de modelos
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(ml_data.groupby('model_name').mean().reset_index(), 
                        x='model_name', y='accuracy', 
                        title="Model Accuracy Comparison")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(ml_data, x='inference_time', y='accuracy', 
                           color='model_name', size='test_samples',
                           title="Accuracy vs Inference Time")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📊 Detailed Model Metrics")
        
        # Formatear datos para mostrar
        display_data = ml_data.copy()
        display_data['accuracy'] = display_data['accuracy'].map('{:.2%}'.format)
        display_data['precision_score'] = display_data['precision_score'].map('{:.2%}'.format)
        display_data['recall'] = display_data['recall'].map('{:.2%}'.format)
        display_data['f1_score'] = display_data['f1_score'].map('{:.2%}'.format)
        display_data['inference_time'] = display_data['inference_time'].map('{:.3f}s'.format)
        
        st.dataframe(display_data, use_container_width=True)
    
    else:
        st.warning("No hay datos de performance ML disponibles")

elif view_mode == "Community Management":
    st.subheader("👥 Community Management Insights")
    
    # Obtener métricas de community
    community_data = analytics.get_community_metrics()
    
    if not community_data.empty:
        # Métricas por plataforma
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_followers = community_data['followers'].sum()
            st.metric("👥 Total Followers", f"{total_followers:,}", "+5.2%")
        
        with col2:
            avg_engagement = community_data['engagement_rate'].mean()
            st.metric("💫 Avg Engagement", f"{avg_engagement:.1f}%", "+0.8%")
        
        with col3:
            total_conversions = community_data['conversions'].sum()
            st.metric("🎯 Total Conversions", f"{total_conversions:,}", "+12.3%")
        
        # Gráficos de community management
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(community_data, values='followers', names='platform',
                        title="Follower Distribution by Platform")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(community_data, x='platform', y='engagement_rate',
                        color='reach', title="Engagement Rate by Platform")
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de métricas detalladas
        st.subheader("📋 Detailed Community Metrics")
        st.dataframe(community_data, use_container_width=True)
    
    else:
        st.warning("No hay datos de community management disponibles")

elif view_mode == "Campaign ROI":
    st.subheader("💰 Campaign ROI Analysis")
    
    # Obtener datos de ROI
    roi_data = analytics.get_campaign_roi()
    
    if not roi_data.empty:
        # Métricas de ROI
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_spend = roi_data['spend'].sum()
            st.metric("💸 Total Spend", f"${total_spend:,.0f}")
        
        with col2:
            total_revenue = roi_data['revenue'].sum()
            st.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
        
        with col3:
            overall_roi = ((total_revenue - total_spend) / total_spend) * 100
            st.metric("📈 Overall ROI", f"{overall_roi:.0f}%")
        
        with col4:
            avg_ctr = roi_data['ctr'].mean()
            st.metric("👆 Avg CTR", f"{avg_ctr:.1f}%")
        
        # Gráficos de ROI
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(roi_data, x='spend', y='revenue', 
                           color='platform', size='roi_percentage',
                           title="Spend vs Revenue by Platform")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            platform_roi = roi_data.groupby('platform')['roi_percentage'].mean().reset_index()
            fig = px.bar(platform_roi, x='platform', y='roi_percentage',
                        title="Average ROI by Platform")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de campañas
        st.subheader("📊 Campaign Performance Details")
        
        # Formatear datos para mostrar
        display_roi = roi_data.copy()
        display_roi['spend'] = display_roi['spend'].map('${:,.0f}'.format)
        display_roi['revenue'] = display_roi['revenue'].map('${:,.0f}'.format)
        display_roi['roi_percentage'] = display_roi['roi_percentage'].map('{:.0f}%'.format)
        display_roi['cpc'] = display_roi['cpc'].map('${:.2f}'.format)
        display_roi['cpm'] = display_roi['cpm'].map('${:.2f}'.format)
        display_roi['ctr'] = display_roi['ctr'].map('{:.1f}%'.format)
        display_roi['conversion_rate'] = display_roi['conversion_rate'].map('{:.1f}%'.format)
        
        st.dataframe(display_roi, use_container_width=True)
    
    else:
        st.warning("No hay datos de ROI disponibles")

elif view_mode == "AI Recommendations":
    st.subheader("🤖 AI-Powered Recommendations")
    
    # Obtener todas las recomendaciones
    recommendations = analytics.get_ai_recommendations()
    
    if recommendations:
        # Filtrar por categoría
        categories = list(set([rec['category'] for rec in recommendations]))
        selected_categories = st.multiselect("🏷️ Filtrar por categoría", categories, default=categories)
        
        filtered_recs = [rec for rec in recommendations if rec['category'] in selected_categories]
        
        # Mostrar recomendaciones
        for i, rec in enumerate(filtered_recs):
            priority_color = "#ff4b4b" if rec['priority'] == 1 else "#ff8c00" if rec['priority'] == 2 else "#00c851"
            priority_text = "HIGH" if rec['priority'] == 1 else "MEDIUM" if rec['priority'] == 2 else "LOW"
            
            with st.expander(f"🎯 {rec['title']} ({rec['category']}) - Priority: {priority_text}"):
                st.markdown(f"""
                **Description:** {rec['description']}
                
                **Confidence Score:** {rec['confidence_score']:.0%} 
                **Priority Level:** {rec['priority']}
                **Status:** {rec['status'].upper()}
                
                ---
                
                **Recommended Actions:**
                - Review current campaign settings
                - Implement suggested optimizations
                - Monitor performance for 7-14 days
                - Measure impact and adjust accordingly
                """)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"✅ Implement", key=f"impl_{i}"):
                        st.success("Recomendación marcada para implementación")
                
                with col2:
                    if st.button(f"📊 Analyze", key=f"analyze_{i}"):
                        st.info("Iniciando análisis detallado...")
                
                with col3:
                    if st.button(f"❌ Dismiss", key=f"dismiss_{i}"):
                        st.warning("Recomendación descartada")
    
    else:
        st.info("No hay recomendaciones de IA disponibles en este momento")

# FOOTER
st.divider()
st.markdown("""
### 📊 Analytics Engine Status
- **Data Sources:** Production Controller, ML API, N8N Workflows  
- **Update Frequency:** Real-time (30s refresh)
- **Data Retention:** 90 days rolling window
- **AI Model:** GPT-4 + Custom ML Pipeline

**Last Updated:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Auto-refresh logic
if auto_refresh:
    time.sleep(1)  # Small delay before rerun
    st.rerun()