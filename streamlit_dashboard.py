#!/usr/bin/env python3
"""
🎯 TikTok Viral ML System - Interfaz Web Universal Streamlit
===========================================================

Interfaz web completa que gestiona todas las ramas y funcionalidades:
- 🌿 Control multi-rama (MAIN, META, TELE)
- 🎭 Toggle modo dummy/producción
- 📊 Dashboard de estado en tiempo real
- 🔧 Instalación automática de dependencias
- 📈 Monitoreo y métricas
- ⚡ Control de servicios y APIs

Uso:
    streamlit run streamlit_dashboard.py
    streamlit run streamlit_dashboard.py --server.port 8501
"""

import streamlit as st
import os
import sys
import json
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from typing import Dict, List, Any, Optional
import asyncio
import importlib.util

# Configuración de la página
st.set_page_config(
    page_title="🎯 TikTok Viral ML System - Dashboard Universal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid;
    }
    
    .status-ready {
        background-color: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    
    .status-partial {
        background-color: #fff3cd;
        border-color: #ffc107;
        color: #856404;
    }
    
    .status-incomplete {
        background-color: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .branch-selector {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        padding: 0.5rem;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitDashboard:
    """Dashboard principal de Streamlit"""
    
    def __init__(self):
        self.setup_session_state()
        self.current_branch = self.get_git_branch()
        self.dummy_mode = self.get_dummy_mode()
        
    def setup_session_state(self):
        """Inicializa el estado de la sesión"""
        if 'validation_data' not in st.session_state:
            st.session_state.validation_data = {}
        if 'installation_status' not in st.session_state:
            st.session_state.installation_status = {}
        if 'service_status' not in st.session_state:
            st.session_state.service_status = {}
        if 'dummy_mode' not in st.session_state:
            st.session_state.dummy_mode = self.get_dummy_mode()
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = False
        if 'selected_branch' not in st.session_state:
            st.session_state.selected_branch = self.get_git_branch()
            
    def get_git_branch(self) -> str:
        """Obtiene la rama actual de Git"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=Path.cwd())
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"
    
    def get_dummy_mode(self) -> bool:
        """Verifica si el modo dummy está activo"""
        return os.getenv('DUMMY_MODE', 'false').lower() == 'true'
    
    def toggle_dummy_mode(self, enable: bool):
        """Cambia el modo dummy"""
        if enable:
            os.environ['DUMMY_MODE'] = 'true'
        else:
            os.environ.pop('DUMMY_MODE', None)
        st.session_state.dummy_mode = enable
        
    def run_command(self, command: List[str], timeout: int = 300) -> Dict[str, Any]:
        """Ejecuta un comando de shell y devuelve el resultado"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=Path.cwd()
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def validate_branch(self, branch: str, dummy_mode: bool = None) -> Dict[str, Any]:
        """Valida una rama específica"""
        if dummy_mode is None:
            dummy_mode = self.dummy_mode
            
        command = ['python', 'validate_multibranch.py', '--branch', branch, '--quiet']
        if dummy_mode:
            command.append('--dummy-mode')
            
        result = self.run_command(command)
        
        if result['success']:
            # Parse the exit code to determine status
            if result['returncode'] == 0:
                status = 'READY'
                score = 95
            elif result['returncode'] == 1:
                status = 'PARTIAL'
                score = 75
            else:
                status = 'INCOMPLETE'
                score = 40
        else:
            status = 'ERROR'
            score = 0
            
        return {
            'branch': branch,
            'status': status,
            'score': score,
            'dummy_mode': dummy_mode,
            'timestamp': datetime.now().isoformat(),
            'details': result
        }
    
    def validate_all_branches(self, dummy_mode: bool = None) -> Dict[str, Any]:
        """Valida todas las ramas"""
        if dummy_mode is None:
            dummy_mode = self.dummy_mode
            
        branches = ['main', 'meta', 'tele']
        results = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, branch in enumerate(branches):
            status_text.text(f"Validando rama {branch}...")
            results[branch] = self.validate_branch(branch, dummy_mode)
            progress_bar.progress((i + 1) / len(branches))
            
        progress_bar.empty()
        status_text.empty()
        
        return results
    
    def install_dependencies(self, branch: str, dummy_mode: bool = None) -> Dict[str, Any]:
        """Instala dependencias para una rama"""
        if dummy_mode is None:
            dummy_mode = self.dummy_mode
            
        command = ['./install_dependencies.sh']
        if dummy_mode:
            command.append('--dummy')
        else:
            command.append(f'--{branch}')
            
        with st.spinner(f'Instalando dependencias para rama {branch}...'):
            result = self.run_command(command, timeout=600)  # 10 minutos timeout
            
        return result
    
    def check_service_status(self, service: str) -> Dict[str, Any]:
        """Verifica el estado de un servicio"""
        # Implementación básica - puedes expandir según tus servicios
        services_info = {
            'ml_api': {
                'port': 8000,
                'health_endpoint': '/health',
                'name': 'ML API Service'
            },
            'telegram_bot': {
                'process': 'telegram_like4like_bot.py',
                'name': 'Telegram Bot'
            },
            'n8n': {
                'port': 5678,
                'name': 'n8n Workflows'
            }
        }
        
        if service not in services_info:
            return {'status': 'unknown', 'message': 'Service not configured'}
            
        # Implementar verificación real según el tipo de servicio
        return {'status': 'stopped', 'message': 'Service check not implemented'}

def render_header():
    """Renderiza el header principal"""
    st.markdown("""
    <div class="main-header">
        🎯 TikTok Viral ML System - Dashboard Universal
    </div>
    """, unsafe_allow_html=True)

def render_sidebar(dashboard: StreamlitDashboard):
    """Renderiza la barra lateral con controles"""
    st.sidebar.title("🎛️ Panel de Control")
    
    # Control de modo dummy
    st.sidebar.subheader("🎭 Modo de Operación")
    dummy_mode = st.sidebar.toggle(
        "Modo Dummy (Testing rápido)",
        value=dashboard.dummy_mode,
        key="dummy_mode_toggle"
    )
    
    if dummy_mode != dashboard.dummy_mode:
        dashboard.toggle_dummy_mode(dummy_mode)
        st.sidebar.success(f"Modo {'Dummy' if dummy_mode else 'Producción'} activado")
    
    # Selector de rama
    st.sidebar.subheader("🌿 Rama Activa")
    current_branch = dashboard.current_branch
    st.sidebar.info(f"Rama Git actual: **{current_branch}**")
    
    selected_branch = st.sidebar.selectbox(
        "Rama para operaciones:",
        options=['main', 'meta', 'tele'],
        index=0 if current_branch not in ['main', 'meta', 'tele'] else ['main', 'meta', 'tele'].index(current_branch),
        key="branch_selector"
    )
    st.session_state.selected_branch = selected_branch
    
    # Auto-refresh
    st.sidebar.subheader("🔄 Actualización")
    auto_refresh = st.sidebar.toggle(
        "Auto-refresh (30s)",
        value=st.session_state.auto_refresh,
        key="auto_refresh_toggle"
    )
    st.session_state.auto_refresh = auto_refresh
    
    # Información del sistema
    st.sidebar.subheader("ℹ️ Sistema")
    st.sidebar.text(f"Python: {sys.version.split()[0]}")
    st.sidebar.text(f"Modo: {'🎭 Dummy' if dummy_mode else '🔧 Producción'}")
    st.sidebar.text(f"Timestamp: {datetime.now().strftime('%H:%M:%S')}")
    
    return selected_branch, dummy_mode

def render_status_cards(validation_data: Dict[str, Any]):
    """Renderiza las tarjetas de estado de las ramas"""
    if not validation_data:
        st.warning("🔄 No hay datos de validación. Ejecuta una validación primero.")
        return
    
    st.subheader("📊 Estado de las Ramas")
    
    cols = st.columns(len(validation_data))
    
    for i, (branch, data) in enumerate(validation_data.items()):
        with cols[i]:
            status = data.get('status', 'UNKNOWN')
            score = data.get('score', 0)
            
            # Determinar color y estilo
            if status == 'READY':
                card_class = 'status-ready'
                icon = '✅'
                color = 'green'
            elif status == 'PARTIAL':
                card_class = 'status-partial'
                icon = '⚠️'
                color = 'orange'
            else:
                card_class = 'status-incomplete'
                icon = '❌'
                color = 'red'
            
            # Tarjeta de estado
            st.markdown(f"""
            <div class="status-card {card_class}">
                <h3>{icon} RAMA {branch.upper()}</h3>
                <p><strong>Estado:</strong> {status}</p>
                <p><strong>Score:</strong> {score}%</p>
                <p><strong>Modo:</strong> {'🎭 Dummy' if data.get('dummy_mode') else '🔧 Producción'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Métricas
            st.metric(
                label=f"Score {branch.upper()}",
                value=f"{score}%",
                delta=f"{status}"
            )

def render_validation_section(dashboard: StreamlitDashboard):
    """Renderiza la sección de validación"""
    st.header("🔍 Validación del Sistema")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🔍 Validar Rama Actual", type="primary"):
            selected_branch = st.session_state.selected_branch
            with st.spinner(f"Validando rama {selected_branch}..."):
                result = dashboard.validate_branch(selected_branch, dashboard.dummy_mode)
                st.session_state.validation_data[selected_branch] = result
                st.success(f"✅ Validación completada: {result['status']} ({result['score']}%)")
    
    with col2:
        if st.button("🔄 Validar Todas las Ramas"):
            results = dashboard.validate_all_branches(dashboard.dummy_mode)
            st.session_state.validation_data.update(results)
            
            # Mostrar resumen
            ready_count = sum(1 for r in results.values() if r['status'] == 'READY')
            total_count = len(results)
            st.success(f"✅ Validación completada: {ready_count}/{total_count} ramas listas")
    
    with col3:
        if st.button("🗑️ Limpiar"):
            st.session_state.validation_data = {}
            st.success("🧹 Datos limpiados")
    
    # Mostrar resultados
    if st.session_state.validation_data:
        render_status_cards(st.session_state.validation_data)

def render_installation_section(dashboard: StreamlitDashboard):
    """Renderiza la sección de instalación de dependencias"""
    st.header("📦 Gestión de Dependencias")
    
    selected_branch = st.session_state.selected_branch
    dummy_mode = dashboard.dummy_mode
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button(f"📦 Instalar Deps {selected_branch.upper()}", type="primary"):
            result = dashboard.install_dependencies(selected_branch, dummy_mode)
            st.session_state.installation_status[selected_branch] = result
            
            if result['success']:
                st.success(f"✅ Dependencias instaladas para {selected_branch}")
                # Auto-validar después de instalación
                validation_result = dashboard.validate_branch(selected_branch, dummy_mode)
                st.session_state.validation_data[selected_branch] = validation_result
                st.info(f"🔍 Nueva validación: {validation_result['status']} ({validation_result['score']}%)")
            else:
                st.error(f"❌ Error instalando dependencias: {result['stderr']}")
    
    with col2:
        if st.button("🔧 Auto-reparar"):
            with st.spinner("Ejecutando auto-reparación..."):
                command = ['python', 'validate_multibranch.py', '--fix']
                if dummy_mode:
                    command.append('--dummy-mode')
                
                result = dashboard.run_command(command, timeout=900)  # 15 minutos
                
                if result['success']:
                    st.success("✅ Auto-reparación completada")
                    # Re-validar todas las ramas
                    results = dashboard.validate_all_branches(dummy_mode)
                    st.session_state.validation_data.update(results)
                else:
                    st.error(f"❌ Error en auto-reparación: {result['stderr']}")
    
    with col3:
        space_mode = "~500MB" if dummy_mode else "2-10GB"
        st.info(f"💾 Espacio: {space_mode}")
    
    # Mostrar estado de instalación
    if st.session_state.installation_status:
        st.subheader("📋 Historial de Instalaciones")
        for branch, result in st.session_state.installation_status.items():
            with st.expander(f"📦 {branch.upper()} - {'✅ Éxito' if result['success'] else '❌ Error'}"):
                st.text("STDOUT:")
                st.code(result['stdout'])
                if result['stderr']:
                    st.text("STDERR:")
                    st.code(result['stderr'])

def render_services_section(dashboard: StreamlitDashboard):
    """Renderiza la sección de control de servicios"""
    st.header("⚡ Control de Servicios")
    
    services = {
        'ml_api': 'ML API Service (FastAPI)',
        'telegram_bot': 'Telegram Bot',
        'n8n_workflows': 'n8n Workflows',
        'device_farm': 'Device Farm Controller',
        'gologin_automation': 'GoLogin Browser Automation'
    }
    
    cols = st.columns(3)
    
    for i, (service_key, service_name) in enumerate(services.items()):
        with cols[i % 3]:
            st.markdown(f"**{service_name}**")
            
            status = st.session_state.service_status.get(service_key, {'status': 'stopped'})
            
            if status['status'] == 'running':
                st.success("🟢 Ejecutándose")
                if st.button(f"⏹️ Detener {service_key}", key=f"stop_{service_key}"):
                    st.info(f"🔄 Deteniendo {service_name}...")
                    # Implementar lógica de detención
            else:
                st.error("🔴 Detenido")
                if st.button(f"▶️ Iniciar {service_key}", key=f"start_{service_key}"):
                    st.info(f"🔄 Iniciando {service_name}...")
                    # Implementar lógica de inicio

def render_monitoring_section(dashboard: StreamlitDashboard):
    """Renderiza la sección de monitoreo"""
    st.header("📈 Monitoreo y Métricas")
    
    # Métricas del sistema
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌿 Rama Activa",
            value=dashboard.current_branch.upper(),
            delta="Git branch"
        )
    
    with col2:
        st.metric(
            label="🎭 Modo Operación",
            value="Dummy" if dashboard.dummy_mode else "Producción",
            delta="Toggle en sidebar"
        )
    
    with col3:
        ready_branches = sum(1 for data in st.session_state.validation_data.values() 
                           if data.get('status') == 'READY')
        total_branches = len(st.session_state.validation_data) if st.session_state.validation_data else 3
        st.metric(
            label="✅ Ramas Listas",
            value=f"{ready_branches}/{total_branches}",
            delta=f"{(ready_branches/total_branches*100):.0f}%" if total_branches > 0 else "0%"
        )
    
    with col4:
        avg_score = sum(data.get('score', 0) for data in st.session_state.validation_data.values()) / max(len(st.session_state.validation_data), 1)
        st.metric(
            label="📊 Score Promedio",
            value=f"{avg_score:.1f}%",
            delta="Todas las ramas"
        )
    
    # Gráfico de scores por rama
    if st.session_state.validation_data:
        st.subheader("📊 Scores por Rama")
        
        df = pd.DataFrame([
            {
                'Rama': branch.upper(),
                'Score': data.get('score', 0),
                'Status': data.get('status', 'UNKNOWN'),
                'Modo': 'Dummy' if data.get('dummy_mode') else 'Producción'
            }
            for branch, data in st.session_state.validation_data.items()
        ])
        
        st.bar_chart(df.set_index('Rama')['Score'])
        st.dataframe(df, use_container_width=True)

def render_logs_section():
    """Renderiza la sección de logs"""
    st.header("📝 Logs del Sistema")
    
    log_files = {
        'system_validation': 'logs/system_validation_*.json',
        'apply_report': 'logs/apply_report_*.json',
        'telegram_bot': 'logs/telegram_bot.log',
        'ml_api': 'logs/ml_api.log'
    }
    
    selected_log = st.selectbox(
        "Seleccionar log:",
        options=list(log_files.keys()),
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # Implementar lectura de logs
    st.info("🔄 Funcionalidad de logs en desarrollo")

def main():
    """Función principal de la aplicación Streamlit"""
    dashboard = StreamlitDashboard()
    
    # Header
    render_header()
    
    # Sidebar
    selected_branch, dummy_mode = render_sidebar(dashboard)
    
    # Auto-refresh
    if st.session_state.auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Validación", 
        "📦 Dependencias", 
        "⚡ Servicios", 
        "📈 Monitoreo", 
        "📝 Logs"
    ])
    
    with tab1:
        render_validation_section(dashboard)
    
    with tab2:
        render_installation_section(dashboard)
    
    with tab3:
        render_services_section(dashboard)
    
    with tab4:
        render_monitoring_section(dashboard)
    
    with tab5:
        render_logs_section()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🎯 TikTok Viral ML System - Dashboard Universal v1.0<br>
        <small>Gestión completa de todas las ramas desde una interfaz unificada</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()