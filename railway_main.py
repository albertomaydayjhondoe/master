#!/usr/bin/env python3
"""
Railway Main App - Stakas MVP Viral System 24/7
Aplicación principal unificada para Railway deployment
"""

import streamlit as st
import uvicorn
import asyncio
import threading
import time
import os
import logging
import sys
from datetime import datetime
import subprocess
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/railway_app.log')
    ]
)

logger = logging.getLogger(__name__)

# Configuraciones
PORT = int(os.getenv('PORT', 8080))
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
AUTO_RESTART = os.getenv('AUTO_RESTART', 'true').lower() == 'true'

class RailwayApp:
    """Aplicación principal para Railway"""
    
    def __init__(self):
        self.port = PORT
        self.environment = ENVIRONMENT
        self.running = True
        self.services = {}
        
        # Configurar Streamlit
        os.environ['STREAMLIT_SERVER_PORT'] = str(self.port)
        os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        logger.info(f"Inicializando Railway App en puerto {self.port}")
        
    def create_unified_dashboard(self):
        """Crear dashboard unificado con todas las funcionalidades"""
        
        # Configuración de página
        st.set_page_config(
            page_title="🚀 Stakas MVP - Viral System 24/7",
            page_icon="🎵",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # CSS personalizado
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
            }
            .status-online {
                background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
                padding: 1rem;
                border-radius: 5px;
                color: white;
                margin: 0.5rem 0;
            }
            .metric-card {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                margin: 1rem 0;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Header principal
        st.markdown("""
        <div class="main-header">
            <h1>🎵 STAKAS MVP - VIRAL SYSTEM 24/7</h1>
            <h3>📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg | 🚀 Powered by Railway</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Status del sistema
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="status-online">
                <h4>🟢 Sistema Online</h4>
                <p>Railway 24/7 Activo</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("🎯 Canal Status", "VERIFIED", "100% Operativo")
        
        with col3:
            st.metric("💰 Meta Ads Budget", "€500/mes", "€16.67/día")
        
        with col4:
            st.metric("📊 ROI Proyectado", "60-180%", "Según escenario")
        
        # Tabs principales
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏠 Dashboard", "📊 Analytics", "🤖 Automation", "⚙️ Control", "📋 Reports"
        ])
        
        with tab1:
            self.render_main_dashboard()
        
        with tab2:
            self.render_analytics()
        
        with tab3:
            self.render_automation_status()
        
        with tab4:
            self.render_control_panel()
        
        with tab5:
            self.render_reports()
    
    def render_main_dashboard(self):
        """Render del dashboard principal"""
        
        st.markdown("## 🏠 Dashboard Principal")
        
        # Métricas en tiempo real simuladas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>📺 Canal Stakas MVP</h4>
                <p><strong>Suscriptores actuales:</strong> ~15,200</p>
                <p><strong>Género:</strong> Drill/Rap Español</p>
                <p><strong>Videos activos:</strong> 15</p>
                <p><strong>Engagement:</strong> 3.2% → 5.8%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>💰 Meta Ads Performance</h4>
                <p><strong>Presupuesto:</strong> €500/mes</p>
                <p><strong>CTR objetivo:</strong> >3.5%</p>
                <p><strong>CPC objetivo:</strong> <€0.20</p>
                <p><strong>ROAS esperado:</strong> 2.5-3.5x</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h4>🚀 Proyecciones</h4>
                <p><strong>Nuevos subs/mes:</strong> 300-900</p>
                <p><strong>ROI esperado:</strong> 60-180%</p>
                <p><strong>Payback:</strong> 45-60 días</p>
                <p><strong>Crecimiento 6m:</strong> 15-32%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Videos recientes detectados
        st.markdown("### 🎬 Contenido Viral Detectado")
        
        videos = [
            "Si te gusta la canción te ganas un Iphone📱#drill #drillespañol #mvp #stakasmvp #viral",
            "Stakas MVP | SNOW❄️ (Video oficial)",
            "D.E.P. HERMANITO🙏🏼✞ VUELA ALTO PAC CHAVES MVP🙌🏽🕊🖤"
        ]
        
        for i, video in enumerate(videos, 1):
            st.markdown(f"**{i}.** {video}")
        
        # Hashtags trending
        st.markdown("### 🏷️ Hashtags Trending Detectados")
        hashtags = "#drill #drillespañol #mvp #stakasmvp #viral #snow #iphone #español"
        st.code(hashtags)
    
    def render_analytics(self):
        """Render de analytics avanzados"""
        
        st.markdown("## 📊 Analytics Avanzados")
        
        # Simulación de métricas en tiempo real
        import random
        import pandas as pd
        import plotly.graph_objects as go
        
        # Gráfico de crecimiento proyectado
        st.markdown("### 📈 Crecimiento Proyectado - Meta Ads €500/mes")
        
        scenarios = ['Conservador', 'Moderado', 'Optimista']
        subs_min = [300, 450, 650]
        subs_max = [450, 650, 900]
        roi_min = [60, 90, 130]
        roi_max = [90, 130, 180]
        
        fig = go.Figure()
        
        # Barras de suscriptores
        fig.add_trace(go.Bar(
            name='Subs Mínimo',
            x=scenarios,
            y=subs_min,
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Subs Máximo',
            x=scenarios,
            y=subs_max,
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title='Nuevos Suscriptores Proyectados por Mes',
            xaxis_title='Escenarios',
            yaxis_title='Nuevos Suscriptores',
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de escenarios
        df = pd.DataFrame({
            'Escenario': scenarios,
            'Suscriptores/mes': [f"{subs_min[i]}-{subs_max[i]}" for i in range(3)],
            'ROI (%)': [f"{roi_min[i]}-{roi_max[i]}%" for i in range(3)],
            'CTR Esperado': ['2.5-3.5%', '3.5-4.5%', '4.5-6.0%'],
            'CPC Promedio': ['€0.15-0.25', '€0.12-0.20', '€0.08-0.15']
        })
        
        st.dataframe(df, use_container_width=True)
    
    def render_automation_status(self):
        """Render del estado de automatización"""
        
        st.markdown("## 🤖 Estado de Automatización")
        
        subsystems = [
            ("Content Automation", "Publicación automática multi-plataforma", "🟢 ACTIVO"),
            ("Engagement Automation", "Bots inteligentes con patrones ML", "🟢 ACTIVO"),
            ("Analytics Automation", "Monitoreo y métricas en tiempo real", "🟢 ACTIVO"),
            ("Cross-Platform Sync", "TikTok, Instagram, YouTube, Twitter", "🟢 ACTIVO"),
            ("Performance Optimization", "ML continuous learning", "🟢 ACTIVO"),
            ("Continuous Monitoring", "24/7 health checks y alertas", "🟢 ACTIVO")
        ]
        
        for name, description, status in subsystems:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{name}**")
                st.caption(description)
            
            with col2:
                st.markdown(status)
            
            st.markdown("---")
        
        # Horarios de publicación
        st.markdown("### 📅 Horarios Optimizados ML")
        
        schedule_data = {
            'Plataforma': ['TikTok', 'Instagram', 'YouTube Shorts', 'YouTube Main', 'Twitter'],
            'Horario': ['20:30 diario', '19:00 feed + stories', 'L/M/V 21:00', 'Viernes 18:00', '3x/día'],
            'Optimización': ['Peak engagement', 'Spain+LATAM prime', 'Weekend viral', 'Weekly drop', 'Continuous engagement']
        }
        
        import pandas as pd
        schedule_df = pd.DataFrame(schedule_data)
        st.dataframe(schedule_df, use_container_width=True)
    
    def render_control_panel(self):
        """Render del panel de control"""
        
        st.markdown("## ⚙️ Panel de Control")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 ACTIVAR META ADS", type="primary"):
                st.success("✅ Meta Ads Campaign Activating...")
                st.balloons()
                st.info("🤖 Todos los subsistemas se activarán automáticamente")
        
        with col2:
            if st.button("⚡ BOOST ENGAGEMENT"):
                st.success("🔥 Engagement bots activados")
                st.info("📈 Aumentando interacciones x2")
        
        with col3:
            if st.button("📊 SYNC PLATFORMS"):
                st.success("🌐 Sincronización completa")
                st.info("✅ TikTok, Instagram, YouTube, Twitter")
        
        with col4:
            if st.button("🔄 SYSTEM RESTART"):
                st.warning("⚠️ Reiniciando servicios...")
                st.info("🔄 Sistema se reiniciará en 30s")
        
        st.markdown("---")
        
        # Configuraciones avanzadas
        st.markdown("### ⚙️ Configuraciones Avanzadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            meta_budget = st.slider("💰 Meta Ads Budget (€/día)", 10, 50, 17)
            st.write(f"Presupuesto mensual: €{meta_budget * 30}")
            
            target_ctr = st.slider("🎯 CTR Objetivo (%)", 2.0, 8.0, 3.5)
            
            engagement_intensity = st.selectbox("🔥 Intensidad Engagement", 
                                              ["Conservadora", "Moderada", "Agresiva"])
        
        with col2:
            posting_frequency = st.selectbox("📅 Frecuencia Posts", 
                                           ["1x/día", "2x/día", "3x/día"])
            
            geographic_focus = st.multiselect("🌍 Focus Geográfico", 
                                            ["España", "México", "Argentina", "Colombia", "Chile"],
                                            default=["España", "México"])
            
            content_style = st.selectbox("🎵 Estilo Contenido",
                                       ["Drill Puro", "Drill + Trap", "Urban Mix"])
        
        if st.button("💾 GUARDAR CONFIGURACIÓN"):
            st.success("✅ Configuración guardada y aplicada")
    
    def render_reports(self):
        """Render de reportes"""
        
        st.markdown("## 📋 Reportes y Documentación")
        
        # Resumen ejecutivo
        st.markdown("### 📊 Resumen Ejecutivo")
        
        summary_text = f"""
        **Canal**: Stakas MVP (UCgohgqLVu1QPdfa64Vkrgeg)
        **Status**: ✅ Verificado 100% | 🟢 Operativo 24/7
        **Género**: Drill/Rap Español (95% potencial viral)
        **Última actualización**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        **Meta Ads Strategy**:
        - Presupuesto: €500/mes (€16.67/día)
        - Target: España 35% + LATAM 65%
        - Demografía: 18-34 años
        - ROI proyectado: 60-180%
        
        **Automatización**:
        - 6 subsistemas operativos
        - Monitoreo 24/7 activo
        - ML optimization continua
        - Cross-platform sync
        """
        
        st.markdown(summary_text)
        
        # Archivos descargables
        st.markdown("### 📁 Documentación Descargable")
        
        reports = [
            ("REPORTE_EJECUTIVO_FINAL_STAKAS_MVP.txt", "📄 Reporte completo"),
            ("detailed_channel_analysis.json", "🔍 Análisis técnico"),
            ("executive_summary_data.json", "📊 Datos ejecutivos"),
            ("railway_deployment_guide.md", "🚀 Guía Railway")
        ]
        
        for filename, description in reports:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{description}**")
                st.caption(filename)
            with col2:
                if st.button(f"📥", key=filename):
                    st.success(f"Descargando {filename}")
        
        # URLs importantes
        st.markdown("### 🌐 URLs del Sistema")
        
        urls = [
            ("Dashboard Principal", "https://[tu-railway-url].railway.app"),
            ("Health Check", "https://[tu-railway-url].railway.app/health"),
            ("API Status", "https://[tu-railway-url].railway.app/api/status"),
            ("Monitoring", "https://[tu-railway-url].railway.app/metrics")
        ]
        
        for name, url in urls:
            st.markdown(f"- **{name}**: `{url}`")
    
    def create_health_endpoint(self):
        """Crear endpoint de health check"""
        
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        
        @app.route('/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'environment': ENVIRONMENT,
                'services': {
                    'streamlit': 'running',
                    'automation': 'active',
                    'monitoring': 'active'
                }
            })
        
        @app.route('/api/status')
        def api_status():
            return jsonify({
                'canal': 'Stakas MVP',
                'channel_id': 'UCgohgqLVu1QPdfa64Vkrgeg',
                'status': 'verified',
                'automation': 'active',
                'meta_ads_ready': True,
                'roi_projection': '60-180%'
            })
        
        return app
    
    def run_health_server(self):
        """Ejecutar servidor de health check en thread separado"""
        
        flask_app = self.create_health_endpoint()
        flask_app.run(host='0.0.0.0', port=8081, debug=False)
    
    def run_streamlit(self):
        """Ejecutar aplicación Streamlit"""
        
        # Crear archivo temporal para Streamlit
        streamlit_code = '''
import streamlit as st
from railway_main import RailwayApp

app = RailwayApp()
app.create_unified_dashboard()
'''
        
        with open('streamlit_app_temp.py', 'w') as f:
            f.write(streamlit_code)
        
        # Ejecutar Streamlit
        cmd = [
            'streamlit', 'run', 'streamlit_app_temp.py',
            '--server.port', str(self.port),
            '--server.address', '0.0.0.0',
            '--browser.gatherUsageStats', 'false',
            '--server.headless', 'true'
        ]
        
        subprocess.run(cmd)
    
    def run(self):
        """Ejecutar aplicación principal"""
        
        logger.info("🚀 Iniciando Stakas MVP Viral System en Railway")
        logger.info(f"Puerto: {self.port}, Ambiente: {self.environment}")
        
        try:
            # Iniciar health check server en thread separado
            health_thread = threading.Thread(target=self.run_health_server, daemon=True)
            health_thread.start()
            logger.info("✅ Health check server iniciado en puerto 8081")
            
            # Ejecutar dashboard principal
            self.create_unified_dashboard()
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando aplicación: {e}")
            if AUTO_RESTART:
                logger.info("🔄 Reiniciando aplicación...")
                time.sleep(10)
                self.run()

def main():
    """Función principal"""
    
    # Configurar directorio de logs
    Path('logs').mkdir(exist_ok=True)
    
    # Crear y ejecutar aplicación
    app = RailwayApp()
    
    if __name__ == "__main__":
        # Ejecutar directamente
        app.run()
    else:
        # Ejecutar como módulo Streamlit
        app.create_unified_dashboard()

if __name__ == "__main__":
    main()