#!/usr/bin/env python3
"""
Production Control Dashboard - Red Button System

Dashboard de control para activar/desactivar funcionalidades específicas
del modo dummy a producción de manera granular y segura.

🔴 RED BUTTON SYSTEM 🔴
- Control individual por módulo
- Activación progresiva y segura
- Monitoreo en tiempo real
- Rollback inmediato
- Logs de todas las activaciones

Autor: Sistema de Control de Producción
Fecha: 2024
"""

import streamlit as st
import json
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import psutil

# Importaciones del sistema
from config.dependency_manager import (
    DependencyManager, check_dependencies, get_dependency_status
)

class ModuleStatus(Enum):
    DUMMY = "dummy"
    TESTING = "testing"
    PRODUCTION = "production"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class ModuleConfig:
    name: str
    description: str
    status: ModuleStatus
    dependencies: List[str]
    critical_level: str  # low/medium/high/critical
    last_activated: Optional[datetime]
    activation_count: int
    error_count: int
    uptime_seconds: float
    health_score: float

class ProductionControlDashboard:
    """Dashboard principal de control de producción"""
    
    def __init__(self):
        self.config_file = Path("/workspaces/master/config/production_control.json")
        self.logs_dir = Path("/workspaces/master/logs/production_control")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar página
        st.set_page_config(
            page_title="🔴 Production Control Dashboard",
            page_icon="🔴",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Estado del sistema
        self.modules = self._load_module_configs()
        self.dependency_manager = DependencyManager()
        
        # Configuración de seguridad
        self.safety_checks = True
        self.confirmation_required = True
    
    def _load_module_configs(self) -> Dict[str, ModuleConfig]:
        """Cargar configuraciones de módulos"""
        
        default_modules = {
            "telegram_bot": ModuleConfig(
                name="Telegram Bot System",
                description="Sistema de bots de Telegram para Like4Like",
                status=ModuleStatus.DUMMY,
                dependencies=["telethon", "ultralytics"],
                critical_level="high",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            ),
            "ml_ultralytics": ModuleConfig(
                name="ML Ultralytics Integration", 
                description="Integración con Ultralytics para análisis viral",
                status=ModuleStatus.DUMMY,
                dependencies=["ultralytics", "torch", "opencv-python"],
                critical_level="critical",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            ),
            "device_farm": ModuleConfig(
                name="Android Device Farm",
                description="Farm de dispositivos Android automatizados", 
                status=ModuleStatus.DUMMY,
                dependencies=["selenium", "appium"],
                critical_level="medium",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            ),
            "meta_ads": ModuleConfig(
                name="Meta Ads Integration",
                description="Integración con Facebook/Instagram Ads API",
                status=ModuleStatus.DUMMY,
                dependencies=["facebook-business"],
                critical_level="high",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            ),
            "gologin_proxy": ModuleConfig(
                name="GoLogin Proxy System",
                description="Sistema de proxies y perfiles GoLogin",
                status=ModuleStatus.DUMMY,
                dependencies=["gologin", "selenium"],
                critical_level="medium",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            ),
            "youtube_automation": ModuleConfig(
                name="YouTube Automation",
                description="Automatización de interacciones en YouTube",
                status=ModuleStatus.DUMMY,
                dependencies=["selenium", "google-api-python-client"],
                critical_level="high",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            ),
            "analytics_dashboard": ModuleConfig(
                name="Analytics Dashboard",
                description="Dashboard de analytics en tiempo real",
                status=ModuleStatus.DUMMY,
                dependencies=["streamlit", "plotly", "pandas"],
                critical_level="low",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            ),
            "cloud_processing": ModuleConfig(
                name="Cloud ML Processing",
                description="Procesamiento ML en la nube",
                status=ModuleStatus.DUMMY,
                dependencies=["boto3", "google-cloud-storage"],
                critical_level="medium",
                last_activated=None,
                activation_count=0,
                error_count=0,
                uptime_seconds=0.0,
                health_score=100.0
            )
        }
        
        # Cargar desde archivo si existe
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_data = json.load(f)
                
                for module_id, data in saved_data.items():
                    if module_id in default_modules:
                        # Actualizar datos guardados
                        module = default_modules[module_id]
                        module.status = ModuleStatus(data.get('status', 'dummy'))
                        module.activation_count = data.get('activation_count', 0)
                        module.error_count = data.get('error_count', 0)
                        module.uptime_seconds = data.get('uptime_seconds', 0.0)
                        module.health_score = data.get('health_score', 100.0)
                        
                        last_activated = data.get('last_activated')
                        if last_activated:
                            module.last_activated = datetime.fromisoformat(last_activated)
                            
            except Exception as e:
                st.error(f"Error loading module configs: {e}")
        
        return default_modules
    
    def _save_module_configs(self):
        """Guardar configuraciones de módulos"""
        
        save_data = {}
        for module_id, module in self.modules.items():
            save_data[module_id] = {
                'status': module.status.value,
                'activation_count': module.activation_count,
                'error_count': module.error_count,
                'uptime_seconds': module.uptime_seconds,
                'health_score': module.health_score,
                'last_activated': module.last_activated.isoformat() if module.last_activated else None
            }
        
        with open(self.config_file, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def run_dashboard(self):
        """Ejecutar dashboard principal"""
        
        # Header con estilo de misión crítica
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ff0000, #cc0000); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; text-align: center; margin: 0;">
                🔴 PRODUCTION CONTROL DASHBOARD 🔴
            </h1>
            <p style="color: white; text-align: center; margin: 5px 0 0 0;">
                ⚠️ CRITICAL SYSTEM CONTROLS - AUTHORIZED PERSONNEL ONLY ⚠️
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar de navegación
        self._render_sidebar()
        
        # Main content basado en selección
        page = st.session_state.get('control_page', 'System Overview')
        
        if page == 'System Overview':
            self._render_system_overview()
        elif page == 'Module Control':
            self._render_module_control()
        elif page == 'Dependency Status':
            self._render_dependency_status()
        elif page == 'System Logs':
            self._render_system_logs()
        elif page == 'Emergency Controls':
            self._render_emergency_controls()
    
    def _render_sidebar(self):
        """Renderizar sidebar de control"""
        
        st.sidebar.markdown("## 🎛️ Control Panel")
        
        # System status indicator
        system_health = self._calculate_system_health()
        
        if system_health >= 90:
            status_color = "🟢"
            status_text = "OPTIMAL"
        elif system_health >= 70:
            status_color = "🟡"
            status_text = "WARNING"
        else:
            status_color = "🔴"
            status_text = "CRITICAL"
        
        st.sidebar.markdown(f"""
        **System Status:** {status_color} {status_text}  
        **Health Score:** {system_health:.1f}%  
        **Active Modules:** {self._count_active_modules()}/{len(self.modules)}
        """)
        
        st.sidebar.markdown("---")
        
        # Navigation
        pages = [
            "System Overview",
            "Module Control", 
            "Dependency Status",
            "System Logs",
            "Emergency Controls"
        ]
        
        selected = st.sidebar.radio("Navigate to:", pages)
        st.session_state['control_page'] = selected
        
        st.sidebar.markdown("---")
        
        # Quick actions
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        if st.sidebar.button("🔄 Refresh All Status"):
            st.experimental_rerun()
        
        if st.sidebar.button("💾 Save Configuration"):
            self._save_module_configs()
            st.sidebar.success("✅ Configuration saved")
        
        if st.sidebar.button("📊 Generate Report"):
            self._generate_status_report()
        
        # Emergency button
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🚨 EMERGENCY")
        
        if st.sidebar.button("🛑 EMERGENCY STOP ALL", type="primary"):
            if st.sidebar.button("⚠️ CONFIRM EMERGENCY STOP"):
                self._emergency_stop_all()
    
    def _render_system_overview(self):
        """Renderizar vista general del sistema"""
        
        st.markdown("## 📊 System Overview")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            active_count = self._count_active_modules()
            st.metric(
                "Active Modules",
                active_count,
                delta=f"{active_count}/{len(self.modules)}"
            )
        
        with col2:
            system_health = self._calculate_system_health()
            st.metric(
                "System Health",
                f"{system_health:.1f}%",
                delta="Good" if system_health >= 80 else "Critical"
            )
        
        with col3:
            total_uptime = sum(m.uptime_seconds for m in self.modules.values())
            st.metric(
                "Total Uptime",
                f"{total_uptime/3600:.1f}h",
                delta="Cumulative"
            )
        
        with col4:
            total_errors = sum(m.error_count for m in self.modules.values())
            st.metric(
                "Total Errors",
                total_errors,
                delta="All Modules"
            )
        
        # Estado de módulos en tiempo real
        st.markdown("### 🎛️ Module Status Matrix")
        
        # Crear tabla de estado
        status_data = []
        for module_id, module in self.modules.items():
            
            # Status indicator
            if module.status == ModuleStatus.PRODUCTION:
                status_icon = "🟢 LIVE"
            elif module.status == ModuleStatus.TESTING:
                status_icon = "🟡 TEST"
            elif module.status == ModuleStatus.DUMMY:
                status_icon = "⚪ DUMMY"
            elif module.status == ModuleStatus.ERROR:
                status_icon = "🔴 ERROR"
            else:
                status_icon = "🟠 MAINT"
            
            # Critical level color
            if module.critical_level == "critical":
                critical_color = "🔴"
            elif module.critical_level == "high":
                critical_color = "🟠"
            elif module.critical_level == "medium":
                critical_color = "🟡"
            else:
                critical_color = "🟢"
            
            status_data.append({
                "Module": module.name,
                "Status": status_icon,
                "Critical": f"{critical_color} {module.critical_level.upper()}",
                "Health": f"{module.health_score:.1f}%",
                "Errors": module.error_count,
                "Uptime": f"{module.uptime_seconds/3600:.1f}h"
            })
        
        # Mostrar tabla
        import pandas as pd
        df = pd.DataFrame(status_data)
        st.dataframe(df, use_container_width=True)
        
        # Gráfico de salud del sistema
        st.markdown("### 📈 System Health Timeline")
        self._render_health_chart()
    
    def _render_module_control(self):
        """Renderizar panel de control de módulos"""
        
        st.markdown("## 🎛️ Individual Module Control")
        st.markdown("⚠️ **WARNING**: Changes to production modules affect live system")
        
        # Selector de módulo
        module_names = {mid: mod.name for mid, mod in self.modules.items()}
        selected_module_id = st.selectbox(
            "Select Module to Control:",
            options=list(module_names.keys()),
            format_func=lambda x: module_names[x]
        )
        
        if selected_module_id:
            module = self.modules[selected_module_id]
            
            # Module details
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### 🔧 {module.name}")
                st.markdown(f"**Description:** {module.description}")
                st.markdown(f"**Critical Level:** {module.critical_level.upper()}")
                st.markdown(f"**Dependencies:** {', '.join(module.dependencies)}")
                
                # Status history
                if module.last_activated:
                    st.markdown(f"**Last Activated:** {module.last_activated.strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Activations:** {module.activation_count}")
                st.markdown(f"**Errors:** {module.error_count}")
            
            with col2:
                # Current status
                self._render_module_status_card(module)
            
            st.markdown("---")
            
            # Control buttons
            st.markdown("### 🚨 DANGER ZONE - PRODUCTION CONTROLS")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(f"🟡 TESTING MODE", key=f"test_{selected_module_id}"):
                    if self._verify_dependencies(module):
                        self._activate_module(selected_module_id, ModuleStatus.TESTING)
                    else:
                        st.error("❌ Dependencies not met")
            
            with col2:
                if st.button(f"🟢 PRODUCTION", key=f"prod_{selected_module_id}", type="primary"):
                    self._show_production_confirmation(selected_module_id)
            
            with col3:
                if st.button(f"⚪ DUMMY MODE", key=f"dummy_{selected_module_id}"):
                    self._deactivate_module(selected_module_id)
            
            with col4:
                if st.button(f"🔧 MAINTENANCE", key=f"maint_{selected_module_id}"):
                    self._set_maintenance_mode(selected_module_id)
            
            # Dependency check results
            st.markdown("### 🔍 Dependency Check")
            self._render_dependency_check(module)
    
    def _render_dependency_status(self):
        """Renderizar estado de dependencias"""
        
        st.markdown("## 📦 System Dependencies Status")
        
        # Ejecutar check de dependencias
        with st.spinner("Checking dependencies..."):
            deps_status = check_dependencies()
        
        # Mostrar resultados
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚨 Critical Dependencies")
            
            for dep_name, status in deps_status.items():
                if status.critical:
                    if status.available:
                        st.success(f"✅ {dep_name} v{status.version}")
                    elif status.fallback_available:
                        st.warning(f"🟡 {dep_name} (fallback mode)")
                    else:
                        st.error(f"❌ {dep_name} - {status.error_message}")
        
        with col2:
            st.markdown("### 🔧 Optional Dependencies")
            
            for dep_name, status in deps_status.items():
                if not status.critical:
                    if status.available:
                        st.success(f"✅ {dep_name} v{status.version}")
                    elif status.fallback_available:
                        st.info(f"🟡 {dep_name} (fallback available)")
                    else:
                        st.warning(f"⚪ {dep_name} - not installed")
        
        # Install missing dependencies
        st.markdown("---")
        st.markdown("### 📥 Install Missing Dependencies")
        
        missing_critical = [
            name for name, status in deps_status.items() 
            if status.critical and not status.available
        ]
        
        if missing_critical:
            st.error(f"⚠️ Missing critical dependencies: {', '.join(missing_critical)}")
            
            if st.button("🚀 Install Critical Dependencies"):
                self._install_dependencies(missing_critical)
        else:
            st.success("✅ All critical dependencies available")
    
    def _render_system_logs(self):
        """Renderizar logs del sistema"""
        
        st.markdown("## 📋 System Operation Logs")
        
        # Log filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            log_level = st.selectbox("Log Level:", ["All", "INFO", "WARNING", "ERROR", "CRITICAL"])
        
        with col2:
            hours_back = st.number_input("Hours back:", min_value=1, max_value=168, value=24)
        
        with col3:
            if st.button("🔄 Refresh Logs"):
                st.experimental_rerun()
        
        # Display logs
        logs = self._get_system_logs(hours_back, log_level)
        
        if logs:
            for log_entry in logs[-50:]:  # Last 50 entries
                timestamp = log_entry['timestamp']
                level = log_entry['level']
                message = log_entry['message']
                
                if level == "ERROR" or level == "CRITICAL":
                    st.error(f"[{timestamp}] {level}: {message}")
                elif level == "WARNING":
                    st.warning(f"[{timestamp}] {level}: {message}")
                else:
                    st.info(f"[{timestamp}] {level}: {message}")
        else:
            st.info("No logs found for the specified criteria")
    
    def _render_emergency_controls(self):
        """Renderizar controles de emergencia"""
        
        st.markdown("## 🚨 EMERGENCY CONTROLS")
        
        st.error("""
        ⚠️ **DANGER ZONE** ⚠️  
        These controls can immediately stop all production systems.  
        Use only in case of emergency or critical system failure.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🛑 Emergency Stop")
            
            if st.button("🚨 STOP ALL PRODUCTION MODULES", type="primary"):
                st.session_state['confirm_emergency'] = True
            
            if st.session_state.get('confirm_emergency', False):
                st.error("⚠️ This will stop ALL production modules immediately!")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ CONFIRM STOP"):
                        self._emergency_stop_all()
                        st.session_state['confirm_emergency'] = False
                
                with col_b:
                    if st.button("❌ Cancel"):
                        st.session_state['confirm_emergency'] = False
        
        with col2:
            st.markdown("### 🔄 System Recovery")
            
            if st.button("🔧 Safe Mode - All Dummy"):
                self._activate_safe_mode()
            
            if st.button("🔄 Restart All Services"):
                self._restart_all_services()
            
            if st.button("🧹 Clear All Errors"):
                self._clear_all_errors()
        
        # System status during emergency
        st.markdown("---")
        st.markdown("### 📊 Current System State")
        
        emergency_status = {
            "Production Modules": len([m for m in self.modules.values() if m.status == ModuleStatus.PRODUCTION]),
            "Testing Modules": len([m for m in self.modules.values() if m.status == ModuleStatus.TESTING]),
            "Dummy Modules": len([m for m in self.modules.values() if m.status == ModuleStatus.DUMMY]),
            "Error Modules": len([m for m in self.modules.values() if m.status == ModuleStatus.ERROR]),
            "Maintenance Modules": len([m for m in self.modules.values() if m.status == ModuleStatus.MAINTENANCE])
        }
        
        for status_type, count in emergency_status.items():
            st.metric(status_type, count)
    
    def _render_module_status_card(self, module: ModuleConfig):
        """Renderizar tarjeta de estado del módulo"""
        
        # Color based on status
        if module.status == ModuleStatus.PRODUCTION:
            bg_color = "#d4edda"
            text_color = "#155724"
            status_emoji = "🟢"
        elif module.status == ModuleStatus.TESTING:
            bg_color = "#fff3cd"
            text_color = "#856404"
            status_emoji = "🟡"
        elif module.status == ModuleStatus.ERROR:
            bg_color = "#f8d7da"
            text_color = "#721c24"
            status_emoji = "🔴"
        else:
            bg_color = "#f8f9fa"
            text_color = "#495057"
            status_emoji = "⚪"
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; border-left: 4px solid {text_color};">
            <h4 style="color: {text_color}; margin: 0;">{status_emoji} {module.status.value.upper()}</h4>
            <p style="color: {text_color}; margin: 5px 0;"><strong>Health:</strong> {module.health_score:.1f}%</p>
            <p style="color: {text_color}; margin: 5px 0;"><strong>Uptime:</strong> {module.uptime_seconds/3600:.1f}h</p>
            <p style="color: {text_color}; margin: 5px 0;"><strong>Errors:</strong> {module.error_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_production_confirmation(self, module_id: str):
        """Mostrar confirmación para activar producción"""
        
        module = self.modules[module_id]
        
        st.error(f"""
        ⚠️ **PRODUCTION ACTIVATION WARNING** ⚠️  
        
        You are about to activate **{module.name}** in PRODUCTION mode.  
        
        This will:
        - Switch from dummy/simulation to REAL operations
        - Use LIVE APIs and real resources  
        - Potentially charge real money for services
        - Affect real user accounts and data
        
        **Critical Level:** {module.critical_level.upper()}
        """)
        
        # Safety checks
        if not self._verify_dependencies(module):
            st.error("❌ Cannot activate: Dependencies not met")
            return
        
        if module.error_count > 5:
            st.error("❌ Cannot activate: Module has too many errors")
            return
        
        # Confirmation checkboxes
        confirm_1 = st.checkbox("✅ I understand this affects LIVE systems")
        confirm_2 = st.checkbox("✅ I have verified all dependencies are working") 
        confirm_3 = st.checkbox("✅ I have authorization to activate production mode")
        
        if confirm_1 and confirm_2 and confirm_3:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚀 ACTIVATE PRODUCTION", type="primary", key=f"confirm_prod_{module_id}"):
                    self._activate_module(module_id, ModuleStatus.PRODUCTION)
            
            with col2:
                if st.button("❌ Cancel", key=f"cancel_prod_{module_id}"):
                    st.info("Production activation cancelled")
    
    def _verify_dependencies(self, module: ModuleConfig) -> bool:
        """Verificar que las dependencias del módulo estén disponibles"""
        
        deps_status = check_dependencies()
        
        for dep in module.dependencies:
            status = deps_status.get(dep)
            if not status or not status.available:
                return False
        
        return True
    
    def _render_dependency_check(self, module: ModuleConfig):
        """Renderizar verificación de dependencias para un módulo"""
        
        deps_status = check_dependencies()
        
        for dep in module.dependencies:
            status = deps_status.get(dep)
            
            if status:
                if status.available:
                    st.success(f"✅ {dep} v{status.version}")
                elif status.fallback_available:
                    st.warning(f"🟡 {dep} (fallback mode available)")
                else:
                    st.error(f"❌ {dep} - {status.error_message}")
            else:
                st.error(f"❌ {dep} - Status unknown")
    
    def _activate_module(self, module_id: str, target_status: ModuleStatus):
        """Activar módulo en el estado especificado"""
        
        module = self.modules[module_id]
        old_status = module.status
        
        # Log activation
        self._log_action(f"ACTIVATE", module_id, f"{old_status.value} -> {target_status.value}")
        
        # Update module
        module.status = target_status
        module.last_activated = datetime.now()
        module.activation_count += 1
        
        # Update environment variable for the module
        self._update_module_environment(module_id, target_status)
        
        # Save configuration
        self._save_module_configs()
        
        if target_status == ModuleStatus.PRODUCTION:
            st.success(f"🚀 {module.name} activated in PRODUCTION mode")
        elif target_status == ModuleStatus.TESTING:
            st.info(f"🟡 {module.name} activated in TESTING mode")
        
        st.experimental_rerun()
    
    def _deactivate_module(self, module_id: str):
        """Desactivar módulo (volver a dummy)"""
        
        module = self.modules[module_id]
        old_status = module.status
        
        self._log_action("DEACTIVATE", module_id, f"{old_status.value} -> dummy")
        
        module.status = ModuleStatus.DUMMY
        self._update_module_environment(module_id, ModuleStatus.DUMMY)
        self._save_module_configs()
        
        st.info(f"⚪ {module.name} deactivated - returned to dummy mode")
        st.experimental_rerun()
    
    def _set_maintenance_mode(self, module_id: str):
        """Poner módulo en modo mantenimiento"""
        
        module = self.modules[module_id]
        old_status = module.status
        
        self._log_action("MAINTENANCE", module_id, f"{old_status.value} -> maintenance")
        
        module.status = ModuleStatus.MAINTENANCE
        self._update_module_environment(module_id, ModuleStatus.MAINTENANCE)
        self._save_module_configs()
        
        st.warning(f"🔧 {module.name} set to maintenance mode")
        st.experimental_rerun()
    
    def _update_module_environment(self, module_id: str, status: ModuleStatus):
        """Actualizar variables de entorno para el módulo"""
        
        # Mapeo de variables de entorno por módulo
        env_vars = {
            "telegram_bot": "TELEGRAM_BOT_MODE",
            "ml_ultralytics": "ULTRALYTICS_MODE",
            "device_farm": "DEVICE_FARM_MODE", 
            "meta_ads": "META_ADS_MODE",
            "gologin_proxy": "GOLOGIN_MODE",
            "youtube_automation": "YOUTUBE_MODE",
            "analytics_dashboard": "ANALYTICS_MODE",
            "cloud_processing": "CLOUD_PROCESSING_MODE"
        }
        
        env_var = env_vars.get(module_id)
        if env_var:
            os.environ[env_var] = status.value
            
            # También escribir a archivo .env
            env_file = Path("/workspaces/master/.env")
            self._update_env_file(env_file, env_var, status.value)
    
    def _update_env_file(self, env_file: Path, var_name: str, value: str):
        """Actualizar archivo .env"""
        
        lines = []
        var_updated = False
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Actualizar variable existente o añadir nueva
        for i, line in enumerate(lines):
            if line.startswith(f"{var_name}="):
                lines[i] = f"{var_name}={value}\n"
                var_updated = True
                break
        
        if not var_updated:
            lines.append(f"{var_name}={value}\n")
        
        # Escribir archivo actualizado
        with open(env_file, 'w') as f:
            f.writelines(lines)
    
    def _emergency_stop_all(self):
        """Parada de emergencia - todos los módulos a dummy"""
        
        self._log_action("EMERGENCY_STOP", "ALL", "Production -> Dummy")
        
        for module_id, module in self.modules.items():
            if module.status == ModuleStatus.PRODUCTION:
                module.status = ModuleStatus.DUMMY
                self._update_module_environment(module_id, ModuleStatus.DUMMY)
        
        self._save_module_configs()
        
        st.error("🚨 EMERGENCY STOP EXECUTED - All modules returned to dummy mode")
        st.experimental_rerun()
    
    def _activate_safe_mode(self):
        """Activar modo seguro - todo a dummy"""
        
        for module_id, module in self.modules.items():
            module.status = ModuleStatus.DUMMY
            module.error_count = 0
            self._update_module_environment(module_id, ModuleStatus.DUMMY)
        
        # Set global dummy mode
        os.environ['DUMMY_MODE'] = 'true'
        self._update_env_file(Path("/workspaces/master/.env"), "DUMMY_MODE", "true")
        
        self._save_module_configs()
        
        st.success("✅ Safe mode activated - All modules in dummy mode")
        st.experimental_rerun()
    
    def _restart_all_services(self):
        """Reiniciar todos los servicios"""
        
        self._log_action("RESTART", "ALL", "Service restart")
        
        # Aquí implementarías el reinicio real de servicios
        st.info("🔄 Services restart initiated (simulation)")
    
    def _clear_all_errors(self):
        """Limpiar todos los errores"""
        
        for module in self.modules.values():
            module.error_count = 0
            if module.status == ModuleStatus.ERROR:
                module.status = ModuleStatus.DUMMY
        
        self._save_module_configs()
        st.success("✅ All errors cleared")
        st.experimental_rerun()
    
    def _install_dependencies(self, dependencies: List[str]):
        """Instalar dependencias faltantes"""
        
        with st.spinner("Installing dependencies..."):
            try:
                for dep in dependencies:
                    subprocess.run(['pip', 'install', dep], check=True, capture_output=True)
                
                st.success(f"✅ Successfully installed: {', '.join(dependencies)}")
                
            except subprocess.CalledProcessError as e:
                st.error(f"❌ Installation failed: {e}")
    
    def _calculate_system_health(self) -> float:
        """Calcular salud general del sistema"""
        
        if not self.modules:
            return 100.0
        
        total_health = sum(m.health_score for m in self.modules.values())
        return total_health / len(self.modules)
    
    def _count_active_modules(self) -> int:
        """Contar módulos activos (no dummy)"""
        
        return len([
            m for m in self.modules.values() 
            if m.status in [ModuleStatus.PRODUCTION, ModuleStatus.TESTING]
        ])
    
    def _render_health_chart(self):
        """Renderizar gráfico de salud del sistema"""
        
        # Simulado por ahora
        import pandas as pd
        import plotly.express as px
        
        # Generar datos simulados de las últimas 24 horas
        hours = []
        health_scores = []
        
        for i in range(24):
            hour = datetime.now() - timedelta(hours=23-i)
            hours.append(hour)
            
            # Simular variación de salud
            base_health = self._calculate_system_health()
            variation = (i % 3) * 2 - 2  # Pequeña variación
            health_scores.append(max(0, min(100, base_health + variation)))
        
        df = pd.DataFrame({
            'Time': hours,
            'Health Score': health_scores
        })
        
        fig = px.line(df, x='Time', y='Health Score', 
                     title="System Health (Last 24 hours)")
        fig.update_layout(height=300)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _log_action(self, action: str, module: str, details: str):
        """Registrar acción en logs"""
        
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'action': action,
            'module': module,
            'details': details,
            'user': 'dashboard_user'  # En producción sería el usuario real
        }
        
        # Escribir a archivo de log
        log_file = self.logs_dir / f"control_actions_{datetime.now().strftime('%Y%m%d')}.json"
        
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _get_system_logs(self, hours_back: int, level_filter: str) -> List[Dict]:
        """Obtener logs del sistema"""
        
        # Simulado - en producción leería archivos reales
        logs = []
        
        for i in range(hours_back):
            timestamp = datetime.now() - timedelta(hours=i)
            
            # Simular algunos logs
            if i % 3 == 0:
                logs.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'level': 'INFO',
                    'message': f'System health check completed - Score: {self._calculate_system_health():.1f}%'
                })
            
            if i % 7 == 0:
                logs.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'level': 'WARNING',
                    'message': 'Dependency check found missing optional package'
                })
        
        # Filtrar por level si no es "All"
        if level_filter != "All":
            logs = [log for log in logs if log['level'] == level_filter]
        
        return sorted(logs, key=lambda x: x['timestamp'])
    
    def _generate_status_report(self):
        """Generar reporte de estado"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_health': self._calculate_system_health(),
            'active_modules': self._count_active_modules(),
            'modules': {
                mid: {
                    'name': mod.name,
                    'status': mod.status.value,
                    'health': mod.health_score,
                    'errors': mod.error_count,
                    'uptime_hours': mod.uptime_seconds / 3600
                }
                for mid, mod in self.modules.items()
            }
        }
        
        report_file = self.logs_dir / f"status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        st.sidebar.success(f"✅ Report saved: {report_file.name}")

# Función principal
def main():
    """Ejecutar Production Control Dashboard"""
    
    dashboard = ProductionControlDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()