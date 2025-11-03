#!/usr/bin/env python3
"""
Gestor de Triggers y Monitorización con Gradio
Sistema completo de gestión de triggers, webhooks y estadísticas
"""

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import sqlite3
import asyncio
from dataclasses import dataclass
import subprocess
import psutil

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TriggerConfig:
    """Configuración de trigger."""
    name: str
    type: str  # webhook, schedule, manual
    url: str
    method: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    schedule: Optional[str]
    enabled: bool
    last_run: Optional[datetime]
    success_count: int
    error_count: int

class DatabaseManager:
    """Gestor de base de datos para estadísticas."""
    
    def __init__(self, db_path: str = "data/gradio_stats.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trigger_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    response_time REAL,
                    payload_size INTEGER,
                    response_size INTEGER,
                    error_message TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_usage REAL,
                    network_sent REAL,
                    network_recv REAL,
                    active_processes INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS webhook_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    webhook_name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source_ip TEXT,
                    payload TEXT,
                    status_code INTEGER,
                    processing_time REAL
                )
            """)
    
    def log_trigger_execution(self, trigger_name: str, status: str, 
                            response_time: float = None, error_message: str = None):
        """Registrar ejecución de trigger."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO trigger_stats 
                (trigger_name, status, response_time, error_message)
                VALUES (?, ?, ?, ?)
            """, (trigger_name, status, response_time, error_message))
    
    def log_system_metrics(self):
        """Registrar métricas del sistema."""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, disk_usage, network_sent, network_recv, active_processes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cpu_percent,
                memory.percent,
                disk.percent,
                network.bytes_sent,
                network.bytes_recv,
                len(psutil.pids())
            ))
    
    def get_trigger_stats(self, hours: int = 24) -> pd.DataFrame:
        """Obtener estadísticas de triggers."""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM trigger_stats 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            """.format(hours)
            return pd.read_sql_query(query, conn)
    
    def get_system_metrics(self, hours: int = 24) -> pd.DataFrame:
        """Obtener métricas del sistema."""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT * FROM system_metrics 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp ASC
            """.format(hours)
            return pd.read_sql_query(query, conn)

class TriggerManager:
    """Gestor de triggers y webhooks."""
    
    def __init__(self):
        self.triggers: Dict[str, TriggerConfig] = {}
        self.db = DatabaseManager()
        self.config_path = Path("config/triggers.json")
        self.load_triggers()
    
    def load_triggers(self):
        """Cargar configuración de triggers."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                    for trigger_data in data.get('triggers', []):
                        trigger = TriggerConfig(**trigger_data)
                        self.triggers[trigger.name] = trigger
            except Exception as e:
                logger.error(f"Error cargando triggers: {e}")
    
    def save_triggers(self):
        """Guardar configuración de triggers."""
        self.config_path.parent.mkdir(exist_ok=True)
        data = {
            'triggers': [
                {
                    'name': t.name,
                    'type': t.type,
                    'url': t.url,
                    'method': t.method,
                    'payload': t.payload,
                    'headers': t.headers,
                    'schedule': t.schedule,
                    'enabled': t.enabled,
                    'last_run': t.last_run.isoformat() if t.last_run else None,
                    'success_count': t.success_count,
                    'error_count': t.error_count
                }
                for t in self.triggers.values()
            ]
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def execute_trigger(self, trigger_name: str) -> Tuple[bool, str]:
        """Ejecutar trigger manualmente."""
        if trigger_name not in self.triggers:
            return False, f"Trigger '{trigger_name}' no encontrado"
        
        trigger = self.triggers[trigger_name]
        if not trigger.enabled:
            return False, f"Trigger '{trigger_name}' está deshabilitado"
        
        try:
            start_time = time.time()
            
            if trigger.method.upper() == 'GET':
                response = requests.get(trigger.url, headers=trigger.headers, timeout=30)
            else:
                response = requests.post(
                    trigger.url, 
                    json=trigger.payload, 
                    headers=trigger.headers, 
                    timeout=30
                )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                trigger.success_count += 1
                trigger.last_run = datetime.now()
                self.db.log_trigger_execution(trigger_name, 'success', response_time)
                self.save_triggers()
                return True, f"Trigger ejecutado exitosamente ({response_time:.1f}ms)"
            else:
                trigger.error_count += 1
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.db.log_trigger_execution(trigger_name, 'error', response_time, error_msg)
                self.save_triggers()
                return False, error_msg
                
        except Exception as e:
            trigger.error_count += 1
            error_msg = str(e)
            self.db.log_trigger_execution(trigger_name, 'error', None, error_msg)
            self.save_triggers()
            return False, error_msg
    
    def add_trigger(self, name: str, trigger_type: str, url: str, method: str = 'POST',
                   payload: str = '{}', headers: str = '{}', schedule: str = None) -> str:
        """Agregar nuevo trigger."""
        try:
            payload_dict = json.loads(payload) if payload else {}
            headers_dict = json.loads(headers) if headers else {}
            
            trigger = TriggerConfig(
                name=name,
                type=trigger_type,
                url=url,
                method=method,
                payload=payload_dict,
                headers=headers_dict,
                schedule=schedule,
                enabled=True,
                last_run=None,
                success_count=0,
                error_count=0
            )
            
            self.triggers[name] = trigger
            self.save_triggers()
            return f"✅ Trigger '{name}' agregado exitosamente"
            
        except json.JSONDecodeError as e:
            return f"❌ Error en JSON: {e}"
        except Exception as e:
            return f"❌ Error: {e}"

class SystemMonitor:
    """Monitor del sistema y servicios."""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtener estado de servicios."""
        services = {}
        
        # Verificar Streamlit
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            services['streamlit'] = {
                'status': 'running' if response.status_code == 200 else 'error',
                'url': 'http://localhost:8501',
                'response_time': response.elapsed.total_seconds() * 1000
            }
        except:
            services['streamlit'] = {'status': 'stopped', 'url': None, 'response_time': None}
        
        # Verificar ML API
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            services['ml_api'] = {
                'status': 'running' if response.status_code == 200 else 'error',
                'url': 'http://localhost:8000',
                'response_time': response.elapsed.total_seconds() * 1000
            }
        except:
            services['ml_api'] = {'status': 'stopped', 'url': None, 'response_time': None}
        
        return services
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_total': memory.total / (1024**3),  # GB
            'memory_used': memory.used / (1024**3),    # GB
            'disk_percent': disk.percent,
            'disk_total': disk.total / (1024**3),      # GB
            'disk_used': disk.used / (1024**3),        # GB
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }

# Instancias globales
trigger_manager = TriggerManager()
system_monitor = SystemMonitor()

def create_dashboard():
    """Crear dashboard principal de Gradio."""
    
    def refresh_trigger_list():
        """Refrescar lista de triggers."""
        trigger_data = []
        for name, trigger in trigger_manager.triggers.items():
            trigger_data.append([
                name,
                trigger.type,
                "✅" if trigger.enabled else "❌",
                trigger.success_count,
                trigger.error_count,
                trigger.last_run.strftime("%Y-%m-%d %H:%M:%S") if trigger.last_run else "Nunca"
            ])
        return trigger_data
    
    def execute_trigger_action(trigger_name: str):
        """Ejecutar trigger seleccionado."""
        if not trigger_name:
            return "❌ Selecciona un trigger", refresh_trigger_list()
        
        success, message = trigger_manager.execute_trigger(trigger_name)
        status = "✅" if success else "❌"
        return f"{status} {message}", refresh_trigger_list()
    
    def add_new_trigger(name, trigger_type, url, method, payload, headers, schedule):
        """Agregar nuevo trigger."""
        message = trigger_manager.add_trigger(name, trigger_type, url, method, payload, headers, schedule)
        return message, refresh_trigger_list()
    
    def get_system_status():
        """Obtener estado del sistema."""
        services = system_monitor.get_service_status()
        system_info = system_monitor.get_system_info()
        
        status_html = f"""
        <div style="font-family: monospace;">
        <h3>🖥️ Estado del Sistema</h3>
        <p><strong>CPU:</strong> {system_info['cpu_percent']:.1f}%</p>
        <p><strong>Memoria:</strong> {system_info['memory_percent']:.1f}% ({system_info['memory_used']:.1f}GB / {system_info['memory_total']:.1f}GB)</p>
        <p><strong>Disco:</strong> {system_info['disk_percent']:.1f}% ({system_info['disk_used']:.1f}GB / {system_info['disk_total']:.1f}GB)</p>
        
        <h3>🚀 Servicios</h3>
        """
        
        for service, info in services.items():
            status_icon = "🟢" if info['status'] == 'running' else "🔴" if info['status'] == 'error' else "⚫"
            response_info = f" ({info['response_time']:.0f}ms)" if info['response_time'] else ""
            url_info = f" - <a href='{info['url']}' target='_blank'>{info['url']}</a>" if info['url'] else ""
            status_html += f"<p>{status_icon} <strong>{service}:</strong> {info['status']}{response_info}{url_info}</p>"
        
        status_html += "</div>"
        return status_html
    
    def create_metrics_chart():
        """Crear gráfico de métricas."""
        df = trigger_manager.db.get_system_metrics(hours=24)
        
        if df.empty:
            return go.Figure().add_annotation(text="No hay datos disponibles", 
                                            xref="paper", yref="paper", 
                                            x=0.5, y=0.5, showarrow=False)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage', 'Network Activity'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}],
                   [{'secondary_y': False}, {'secondary_y': True}]]
        )
        
        # CPU
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['cpu_percent'], name='CPU %'),
            row=1, col=1
        )
        
        # Memory
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['memory_percent'], name='Memory %'),
            row=1, col=2
        )
        
        # Disk
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['disk_usage'], name='Disk %'),
            row=2, col=1
        )
        
        # Network
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['network_sent'], name='Sent'),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['network_recv'], name='Received'),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=True, title_text="Métricas del Sistema (24h)")
        return fig
    
    def create_trigger_stats_chart():
        """Crear gráfico de estadísticas de triggers."""
        df = trigger_manager.db.get_trigger_stats(hours=24)
        
        if df.empty:
            return go.Figure().add_annotation(text="No hay ejecuciones de triggers", 
                                            xref="paper", yref="paper", 
                                            x=0.5, y=0.5, showarrow=False)
        
        # Gráfico de éxitos vs errores
        status_counts = df['status'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(name='Éxitos', x=['Success'], y=[status_counts.get('success', 0)], marker_color='green'),
            go.Bar(name='Errores', x=['Error'], y=[status_counts.get('error', 0)], marker_color='red')
        ])
        
        fig.update_layout(
            title='Ejecución de Triggers (24h)',
            xaxis_title='Estado',
            yaxis_title='Cantidad',
            barmode='group'
        )
        
        return fig
    
    # Interface de Gradio
    with gr.Blocks(title="🎯 TikTok Viral ML - Gestor de Triggers", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎯 TikTok Viral ML System - Gestor de Triggers y Monitorización")
        
        with gr.Tabs():
            # Tab 1: Gestión de Triggers
            with gr.TabItem("🚀 Gestión de Triggers"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("## 📋 Lista de Triggers")
                        trigger_table = gr.Dataframe(
                            headers=["Nombre", "Tipo", "Habilitado", "Éxitos", "Errores", "Última Ejecución"],
                            value=refresh_trigger_list(),
                            interactive=False
                        )
                        
                        with gr.Row():
                            trigger_selector = gr.Dropdown(
                                choices=list(trigger_manager.triggers.keys()),
                                label="Seleccionar Trigger",
                                value=list(trigger_manager.triggers.keys())[0] if trigger_manager.triggers else None
                            )
                            execute_btn = gr.Button("▶️ Ejecutar", variant="primary")
                            refresh_btn = gr.Button("🔄 Refrescar")
                        
                        execution_result = gr.Textbox(label="Resultado de Ejecución", interactive=False)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("## ➕ Agregar Nuevo Trigger")
                        new_name = gr.Textbox(label="Nombre", placeholder="mi_trigger")
                        new_type = gr.Dropdown(["webhook", "schedule", "manual"], label="Tipo", value="webhook")
                        new_url = gr.Textbox(label="URL", placeholder="http://localhost:8000/webhook")
                        new_method = gr.Dropdown(["GET", "POST"], label="Método", value="POST")
                        new_payload = gr.Textbox(
                            label="Payload (JSON)", 
                            value='{"message": "test"}',
                            lines=3
                        )
                        new_headers = gr.Textbox(
                            label="Headers (JSON)", 
                            value='{"Content-Type": "application/json"}',
                            lines=2
                        )
                        new_schedule = gr.Textbox(label="Schedule (cron)", placeholder="0 */6 * * *")
                        add_btn = gr.Button("➕ Agregar Trigger", variant="secondary")
                        add_result = gr.Textbox(label="Resultado", interactive=False)
            
            # Tab 2: Monitorización del Sistema
            with gr.TabItem("📊 Monitorización"):
                with gr.Row():
                    system_status = gr.HTML(get_system_status())
                    refresh_status_btn = gr.Button("🔄 Actualizar Estado")
                
                with gr.Row():
                    metrics_chart = gr.Plot(create_metrics_chart())
                    trigger_stats_chart = gr.Plot(create_trigger_stats_chart())
                
                refresh_charts_btn = gr.Button("📈 Actualizar Gráficos")
            
            # Tab 3: Logs y Análisis
            with gr.TabItem("📝 Logs y Análisis"):
                with gr.Row():
                    log_hours = gr.Slider(1, 168, value=24, label="Horas hacia atrás", step=1)
                    refresh_logs_btn = gr.Button("🔄 Cargar Logs")
                
                trigger_logs = gr.Dataframe(
                    headers=["ID", "Trigger", "Timestamp", "Estado", "Tiempo Respuesta", "Error"],
                    interactive=False
                )
                
                def load_logs(hours):
                    df = trigger_manager.db.get_trigger_stats(hours)
                    return df[['id', 'trigger_name', 'timestamp', 'status', 'response_time', 'error_message']]
            
            # Tab 4: Configuración
            with gr.TabItem("⚙️ Configuración"):
                gr.Markdown("## 🔧 Configuración del Sistema")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📊 Base de Datos")
                        db_info = gr.HTML(f"<p>Ubicación: {trigger_manager.db.db_path}</p>")
                        
                        gr.Markdown("### 🔄 Auto-actualización")
                        auto_refresh = gr.Checkbox(label="Actualización automática cada 30s", value=False)
                    
                    with gr.Column():
                        gr.Markdown("### 📤 Exportar/Importar")
                        export_btn = gr.Button("📤 Exportar Configuración")
                        import_file = gr.File(label="📥 Importar Configuración")
                        import_btn = gr.Button("📥 Importar")
        
        # Event handlers
        execute_btn.click(
            execute_trigger_action,
            inputs=[trigger_selector],
            outputs=[execution_result, trigger_table]
        )
        
        refresh_btn.click(
            lambda: refresh_trigger_list(),
            outputs=[trigger_table]
        )
        
        add_btn.click(
            add_new_trigger,
            inputs=[new_name, new_type, new_url, new_method, new_payload, new_headers, new_schedule],
            outputs=[add_result, trigger_table]
        )
        
        refresh_status_btn.click(
            get_system_status,
            outputs=[system_status]
        )
        
        refresh_charts_btn.click(
            lambda: [create_metrics_chart(), create_trigger_stats_chart()],
            outputs=[metrics_chart, trigger_stats_chart]
        )
        
        refresh_logs_btn.click(
            load_logs,
            inputs=[log_hours],
            outputs=[trigger_logs]
        )
    
    return app

def main():
    """Función principal."""
    # Registrar métricas del sistema cada minuto
    import threading
    
    def log_metrics():
        while True:
            trigger_manager.db.log_system_metrics()
            time.sleep(60)
    
    metrics_thread = threading.Thread(target=log_metrics, daemon=True)
    metrics_thread.start()
    
    # Crear y lanzar la aplicación
    app = create_dashboard()
    
    # Lanzar en puerto 7860 (default de Gradio)
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True
    )

if __name__ == "__main__":
    main()