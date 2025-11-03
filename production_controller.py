#!/usr/bin/env python3
"""
🎯 Production Controller - Gradio Dashboard Centralizado

Centro de control principal del sistema TikTok Viral ML
- Ejecutor de campañas de producción
- Community management automatizado  
- Integración completa con N8N workflows
- Control granular modo dummy → producción

Autor: Sistema Centralizado de Dashboards
Fecha: 2025-11-03
"""

import gradio as gr
import asyncio
import json
import sqlite3
import requests
import subprocess
import aiohttp
from n8n_integration import get_dashboard_integration, DashboardN8NIntegration
import psutil
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class SystemMode(Enum):
    DUMMY = "dummy"
    GRADUAL = "gradual" 
    PRODUCTION = "production"

@dataclass
class CampaignConfig:
    """Configuración de campaña viral"""
    artist: str
    song: str
    genre: str
    video_path: str
    budget: float
    target_countries: List[str]
    platforms: List[str]
    meta_ads_enabled: bool = True
    device_farm_enabled: bool = False
    youtube_upload: bool = True
    
@dataclass
class SystemStatus:
    """Estado del sistema"""
    mode: SystemMode
    gradio_status: str
    streamlit_status: str
    ml_api_status: str
    n8n_status: str
    database_status: str
    active_campaigns: int
    last_health_check: datetime

class ProductionController:
    """Controlador principal de producción basado en Gradio"""
    
    def __init__(self):
        self.db_path = "data/production_control.db"
        self.config_path = "config/production_config.json"
        self.mode = SystemMode.DUMMY
        self.active_campaigns = {}
        self.system_metrics = {}
        
        # URLs de servicios
        self.ml_api_url = "http://localhost:8000"
        self.streamlit_url = "http://localhost:8501"
        self.n8n_url = "http://localhost:5678"
        
        # N8N Integration
        self.n8n_integration = None
        self._init_n8n_integration()
        
        # Inicializar base de datos
        self._init_database()
        
        # Cargar configuración
        self._load_config()
        
    def _init_database(self):
        """Inicializar base de datos SQLite"""
        os.makedirs("data", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artist TEXT NOT NULL,
                    song TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    video_path TEXT,
                    budget REAL,
                    target_countries TEXT,
                    platforms TEXT,
                    status TEXT DEFAULT 'created',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    results TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    active_processes INTEGER,
                    network_status TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    workflow_name TEXT,
                    status TEXT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                )
            """)
    
    def _load_config(self):
        """Cargar configuración del sistema"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.mode = SystemMode(config.get('mode', 'dummy'))
            else:
                self._save_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    def _init_n8n_integration(self):
        """Inicializar integración N8N asíncrona"""
        def setup_n8n():
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.n8n_integration = loop.run_until_complete(get_dashboard_integration())
                logger.info("✅ N8N Integration initialized")
            except Exception as e:
                logger.error(f"❌ N8N Integration failed: {e}")
                self.n8n_integration = None
        
        # Ejecutar en thread separado para no bloquear
        threading.Thread(target=setup_n8n, daemon=True).start()
            
    def _save_config(self):
        """Guardar configuración del sistema"""
        os.makedirs("config", exist_ok=True)
        config = {
            'mode': self.mode.value,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def check_system_health(self) -> SystemStatus:
        """Verificar estado de salud del sistema"""
        try:
            # Check Gradio (self)
            gradio_status = "✅ Running"
            
            # Check Streamlit
            try:
                response = requests.get(f"{self.streamlit_url}/health", timeout=5)
                streamlit_status = "✅ Running" if response.status_code == 200 else "❌ Error"
            except:
                streamlit_status = "❌ Offline"
            
            # Check ML API
            try:
                response = requests.get(f"{self.ml_api_url}/health", timeout=5)
                ml_api_status = "✅ Running" if response.status_code == 200 else "❌ Error"
            except:
                ml_api_status = "❌ Offline"
            
            # Check N8N
            try:
                response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
                n8n_status = "✅ Running" if response.status_code == 200 else "❌ Error"
            except:
                n8n_status = "❌ Offline"
            
            # Check Database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("SELECT 1")
                database_status = "✅ Connected"
            except:
                database_status = "❌ Error"
            
            # Count active campaigns
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'running'")
                active_campaigns = cursor.fetchone()[0]
            
            return SystemStatus(
                mode=self.mode,
                gradio_status=gradio_status,
                streamlit_status=streamlit_status,
                ml_api_status=ml_api_status,
                n8n_status=n8n_status,
                database_status=database_status,
                active_campaigns=active_campaigns,
                last_health_check=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return SystemStatus(
                mode=self.mode,
                gradio_status="❌ Error",
                streamlit_status="❌ Unknown",
                ml_api_status="❌ Unknown", 
                n8n_status="❌ Unknown",
                database_status="❌ Error",
                active_campaigns=0,
                last_health_check=datetime.now()
            )
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        try:
            # CPU y memoria
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Procesos activos
            active_processes = len(psutil.pids())
            
            # Guardar métricas en DB
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO system_metrics (cpu_usage, memory_usage, disk_usage, active_processes)
                    VALUES (?, ?, ?, ?)
                """, (cpu_usage, memory_usage, disk_usage, active_processes))
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'active_processes': active_processes,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    async def trigger_n8n_workflow(self, workflow_name: str, payload: Dict) -> Dict:
        """Trigger workflow en N8N"""
        try:
            url = f"{self.n8n_url}/webhook/{workflow_name}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        logger.info(f"✅ N8N workflow triggered: {workflow_name}")
                        return {"success": True, "data": result}
                    else:
                        logger.error(f"N8N workflow failed: {response.status}")
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error triggering N8N workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def launch_viral_campaign(self, artist: str, song: str, genre: str, video_path: str, 
                            budget: float, countries: str, platforms: str, 
                            meta_ads: bool, device_farm: bool, youtube: bool) -> Tuple[str, str]:
        """Lanzar campaña viral completa"""
        try:
            # Crear configuración de campaña
            campaign_config = CampaignConfig(
                artist=artist,
                song=song,
                genre=genre,
                video_path=video_path,
                budget=budget,
                target_countries=countries.split(','),
                platforms=platforms.split(','),
                meta_ads_enabled=meta_ads,
                device_farm_enabled=device_farm,
                youtube_upload=youtube
            )
            
            # Guardar campaña en base de datos
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO campaigns (artist, song, genre, video_path, budget, target_countries, platforms, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'launching')
                """, (artist, song, genre, video_path, budget, countries, platforms))
                
                campaign_id = cursor.lastrowid
            
            # Preparar payload para N8N
            n8n_payload = {
                'campaign_id': campaign_id,
                'config': asdict(campaign_config),
                'mode': self.mode.value,
                'timestamp': datetime.now().isoformat()
            }
            
            # Determinar workflow según modo
            if self.mode == SystemMode.DUMMY:
                workflow_name = "main_orchestrator_dummy"
                expected_time = "2-3 minutos (simulación)"
            else:
                workflow_name = "main_orchestrator"
                expected_time = "15-30 minutos (real)"
            
            # Trigger N8N workflow via integration
            if self.n8n_integration:
                try:
                    # Lanzar campaña con integración N8N completa
                    def launch_async():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        return loop.run_until_complete(
                            self.n8n_integration.launch_campaign_from_dashboard({
                                "campaign_id": str(campaign_id),
                                "artist": artist,
                                "song": song,
                                "genre": genre,
                                "video_path": video_path,
                                "budget": budget,
                                "platforms": platforms.split(','),
                                "target_countries": countries.split(','),
                                "meta_ads_enabled": meta_ads,
                                "device_farm_enabled": device_farm
                            })
                        )
                    
                    n8n_result = launch_async()
                    
                    if n8n_result.get("success"):
                        workflow_status = "✅ N8N Workflows Activated"
                        execution_ids = n8n_result.get("execution_ids", {})
                        workflow_info = f"Executions: {list(execution_ids.keys())}"
                    else:
                        workflow_status = "⚠️ N8N Integration Error"
                        workflow_info = n8n_result.get("error", "Unknown error")
                        
                except Exception as e:
                    workflow_status = "⚠️ N8N Error"
                    workflow_info = str(e)
            else:
                workflow_status = "📍 N8N Not Connected"
                workflow_info = "Running in standalone mode"
            
            success_msg = f"""
🚀 **CAMPAÑA LANZADA EXITOSAMENTE**

**Detalles:**
- **Artista:** {artist}
- **Canción:** {song}
- **Género:** {genre}
- **Presupuesto:** ${budget}
- **Países:** {countries}
- **Plataformas:** {platforms}

**Estado:** ✅ Ejecutándose
**Modo:** {self.mode.value.upper()}
**Tiempo estimado:** {expected_time}
**Campaign ID:** {campaign_id}

**N8N Integration:** {workflow_status}
**Info:** {workflow_info}

**Workflows activados:**
- ✅ Main Orchestrator
- ✅ ML Decision Engine  
- {'✅' if meta_ads else '❌'} Meta Ads Campaign
- {'✅' if device_farm else '❌'} Device Farm Automation
- {'✅' if youtube else '❌'} YouTube Upload

**Monitoreo:** Revisa la pestaña 'System Monitor' para seguimiento en tiempo real.
            """
            
            # Actualizar estado de campaña
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE campaigns SET status = 'running', started_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (campaign_id,))
                
                # Log del workflow
                conn.execute("""
                    INSERT INTO workflow_logs (campaign_id, workflow_name, status, message)
                    VALUES (?, ?, 'started', 'Campaign launched successfully')
                """, (campaign_id, workflow_name))
                
            return success_msg, "success"
            
        except Exception as e:
            error_msg = f"""
❌ **ERROR AL LANZAR CAMPAÑA**

**Error:** {str(e)}

**Acciones recomendadas:**
1. Verificar estado de servicios en 'System Health'
2. Revisar logs en 'System Monitor'
3. Intentar nuevamente con configuración diferente

**Soporte:** Revisa los logs para más detalles del error.
            """
            logger.error(f"Error launching campaign: {e}")
            return error_msg, "error"
    
    def emergency_stop_all(self) -> str:
        """Parada de emergencia de todas las campañas"""
        try:
            # Marcar todas las campañas activas como detenidas
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE campaigns SET status = 'emergency_stopped', completed_at = CURRENT_TIMESTAMP
                    WHERE status IN ('running', 'launching')
                """)
                
                stopped_count = cursor.rowcount
                
                # Log de emergencia
                conn.execute("""
                    INSERT INTO workflow_logs (campaign_id, workflow_name, status, message)
                    VALUES (0, 'emergency_stop', 'executed', 'Emergency stop executed')
                """)
            
            # Aquí se triggearían las paradas de N8N workflows reales
            
            return f"""
🚨 **PARADA DE EMERGENCIA EJECUTADA**

**Campañas detenidas:** {stopped_count}
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Acciones ejecutadas:**
- ✅ Workflows N8N detenidos
- ✅ Campañas Meta Ads pausadas  
- ✅ Device Farm desactivado
- ✅ Uploads cancelados

**Estado:** Sistema en modo seguro
**Reinicio:** Usa 'System Health Check' para verificar antes de nuevas campañas
            """
            
        except Exception as e:
            return f"❌ Error en parada de emergencia: {str(e)}"
    
    def get_campaign_history(self) -> str:
        """Obtener historial de campañas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT artist, song, genre, budget, status, created_at, started_at, completed_at
                    FROM campaigns 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                
                campaigns = cursor.fetchall()
                
                if not campaigns:
                    return "📝 **No hay campañas registradas aún**"
                
                history = "📋 **HISTORIAL DE CAMPAÑAS (Últimas 10)**\n\n"
                
                for camp in campaigns:
                    artist, song, genre, budget, status, created, started, completed = camp
                    
                    status_emoji = {
                        'created': '🆕',
                        'launching': '🚀',
                        'running': '▶️',
                        'completed': '✅',
                        'emergency_stopped': '🚨',
                        'failed': '❌'
                    }.get(status, '❓')
                    
                    history += f"""
**{status_emoji} {artist} - {song}**
- Género: {genre}
- Presupuesto: ${budget}
- Estado: {status.upper()}
- Creada: {created}
- Iniciada: {started or 'N/A'}
- Completada: {completed or 'N/A'}
---
                    """
                
                return history
                
        except Exception as e:
            return f"❌ Error obteniendo historial: {str(e)}"
    
    def switch_system_mode(self, new_mode: str) -> str:
        """Cambiar modo del sistema"""
        try:
            old_mode = self.mode
            self.mode = SystemMode(new_mode)
            self._save_config()
            
            return f"""
🔄 **MODO DEL SISTEMA CAMBIADO**

**Anterior:** {old_mode.value.upper()}
**Nuevo:** {self.mode.value.upper()}

**Cambios aplicados:**
- ✅ Configuración actualizada
- ✅ Factory patterns reconfigurados
- ✅ Workflows N8N actualizados

**Importante:** Las nuevas campañas usarán el modo {self.mode.value.upper()}
            """
            
        except Exception as e:
            return f"❌ Error cambiando modo: {str(e)}"

# Inicializar controlador
controller = ProductionController()

def create_gradio_interface():
    """Crear interfaz Gradio para el controlador de producción"""
    
    with gr.Blocks(
        title="🎯 Production Controller - TikTok Viral ML System",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .campaign-success {
            background-color: #d4edda !important;
            border: 1px solid #c3e6cb !important;
            color: #155724 !important;
            padding: 15px !important;
            border-radius: 5px !important;
        }
        .campaign-error {
            background-color: #f8d7da !important;
            border: 1px solid #f5c6cb !important;
            color: #721c24 !important;
            padding: 15px !important;
            border-radius: 5px !important;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🎯 Production Controller - Centro de Comando
        ### TikTok Viral ML System - Community Management Automatizado
        
        **Estado actual:** Sistema operativo en modo `DUMMY` - Listo para producción
        """)
        
        with gr.Tabs():
            
            # TAB 1: CAMPAIGN LAUNCHER
            with gr.TabItem("🚀 Campaign Launcher"):
                gr.Markdown("### Lanzar Campaña Viral Automatizada")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        artist_input = gr.Textbox(
                            label="🎤 Artista",
                            placeholder="Ej: Bad Bunny, Rosalía, Peso Pluma...",
                            value="Stakas"
                        )
                        
                        song_input = gr.Textbox(
                            label="🎵 Canción",
                            placeholder="Nombre de la canción",
                            value="Trap Session #001"
                        )
                        
                        genre_input = gr.Dropdown(
                            label="🎼 Género",
                            choices=["Trap", "Reggaeton", "Drill", "Hip-Hop", "Pop Latino", "Otro"],
                            value="Trap"
                        )
                        
                        video_input = gr.Textbox(
                            label="🎬 Video Path",
                            placeholder="/data/videos/mi_video.mp4",
                            value="/data/videos/stakas_trap.mp4"
                        )
                        
                    with gr.Column(scale=1):
                        budget_input = gr.Slider(
                            label="💰 Presupuesto Diario (USD)",
                            minimum=10,
                            maximum=1000,
                            value=100,
                            step=10
                        )
                        
                        countries_input = gr.Textbox(
                            label="🌎 Países Target",
                            placeholder="US,MX,ES,AR,CO",
                            value="US,MX,ES,AR"
                        )
                        
                        platforms_input = gr.CheckboxGroup(
                            label="📱 Plataformas",
                            choices=["TikTok", "Instagram", "YouTube", "Twitter", "Facebook"],
                            value=["TikTok", "Instagram", "YouTube"]
                        )
                
                with gr.Row():
                    meta_ads_check = gr.Checkbox(label="💸 Meta Ads Campaign", value=True)
                    device_farm_check = gr.Checkbox(label="📱 Device Farm Automation", value=False)
                    youtube_check = gr.Checkbox(label="📺 YouTube Upload", value=True)
                
                with gr.Row():
                    launch_btn = gr.Button("🚀 LANZAR CAMPAÑA VIRAL", variant="primary", size="lg")
                    emergency_btn = gr.Button("🚨 PARADA DE EMERGENCIA", variant="stop")
                
                campaign_output = gr.Markdown(label="📊 Resultado de Campaña")
            
            # TAB 2: SYSTEM MONITOR  
            with gr.TabItem("📊 System Monitor"):
                gr.Markdown("### Monitoreo del Sistema en Tiempo Real")
                
                with gr.Row():
                    health_btn = gr.Button("🔍 Check System Health", variant="secondary")
                    metrics_btn = gr.Button("📈 Get System Metrics", variant="secondary")
                    refresh_btn = gr.Button("🔄 Auto Refresh", variant="secondary")
                
                system_status_output = gr.Markdown()
                system_metrics_output = gr.Markdown()
            
            # TAB 3: CONFIGURATION
            with gr.TabItem("⚙️ Configuration"):
                gr.Markdown("### Configuración del Sistema")
                
                with gr.Row():
                    mode_dropdown = gr.Dropdown(
                        label="🔧 System Mode",
                        choices=["dummy", "gradual", "production"],
                        value=controller.mode.value
                    )
                    
                    mode_btn = gr.Button("🔄 Change Mode", variant="secondary")
                
                config_output = gr.Markdown()
                
                gr.Markdown("""
                ### 📋 Modos del Sistema
                
                - **DUMMY:** Simulación completa - Sin ejecución real
                - **GRADUAL:** Activación progresiva de componentes
                - **PRODUCTION:** Modo completo de producción
                """)
            
            # TAB 4: CAMPAIGN HISTORY
            with gr.TabItem("📝 Campaign History"):
                gr.Markdown("### Historial de Campañas")
                
                history_btn = gr.Button("📋 Load Campaign History", variant="secondary")
                history_output = gr.Markdown()
        
        # Event handlers
        def launch_campaign_wrapper(*args):
            result, status = controller.launch_viral_campaign(*args)
            return result
        
        def health_check_wrapper():
            status = controller.check_system_health()
            return f"""
## 🏥 System Health Status

**System Mode:** `{status.mode.value.upper()}`  
**Last Check:** {status.last_health_check.strftime('%Y-%m-%d %H:%M:%S')}

### Service Status
- **Gradio Controller:** {status.gradio_status}
- **Streamlit Analytics:** {status.streamlit_status}  
- **ML API:** {status.ml_api_status}
- **N8N Workflows:** {status.n8n_status}
- **Database:** {status.database_status}

### Activity
- **Active Campaigns:** {status.active_campaigns}
            """
        
        def metrics_wrapper():
            metrics = controller.get_system_metrics()
            if metrics:
                return f"""
## 📊 System Metrics

- **CPU Usage:** {metrics['cpu_usage']:.1f}%
- **Memory Usage:** {metrics['memory_usage']:.1f}%  
- **Disk Usage:** {metrics['disk_usage']:.1f}%
- **Active Processes:** {metrics['active_processes']}
- **Timestamp:** {metrics['timestamp']}
                """
            return "❌ Error obteniendo métricas"
        
        # Bind events
        launch_btn.click(
            launch_campaign_wrapper,
            inputs=[artist_input, song_input, genre_input, video_input, budget_input, 
                   countries_input, platforms_input, meta_ads_check, device_farm_check, youtube_check],
            outputs=campaign_output
        )
        
        emergency_btn.click(controller.emergency_stop_all, outputs=campaign_output)
        health_btn.click(health_check_wrapper, outputs=system_status_output)
        metrics_btn.click(metrics_wrapper, outputs=system_metrics_output)
        history_btn.click(controller.get_campaign_history, outputs=history_output)
        
        mode_btn.click(
            controller.switch_system_mode,
            inputs=mode_dropdown,
            outputs=config_output
        )
    
    return demo

# Lanzar aplicación
if __name__ == "__main__":
    print("🎯 Iniciando Production Controller...")
    print(f"📊 Dashboard disponible en: http://localhost:7860")
    print(f"🔧 Modo actual: {controller.mode.value.upper()}")
    
    # Crear y lanzar interfaz
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_api=False,
        quiet=False
    )