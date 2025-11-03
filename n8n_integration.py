"""
🔄 N8N Integration Layer - Dashboard to Workflow Connector

Integración completa entre dashboards centralizados y workflows N8N
- Webhooks bidireccionales para comunicación
- Ejecución automática de workflows desde dashboards
- Monitoreo en tiempo real de ejecuciones N8N
- Community management completamente automatizado

Autor: Sistema de Integración N8N
Fecha: 2025-11-03
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import time
import threading
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Estados de workflows N8N"""
    INACTIVE = "inactive"
    ACTIVE = "active" 
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

class WorkflowPriority(Enum):
    """Prioridades de workflows"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class WorkflowExecution:
    """Ejecución de workflow"""
    execution_id: str
    workflow_name: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime]
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]

@dataclass
class CampaignWorkflowConfig:
    """Configuración para workflows de campaña"""
    workflow_name: str
    priority: WorkflowPriority
    timeout: int
    retry_count: int
    webhook_url: str
    input_mapping: Dict[str, str]
    output_handlers: List[str]

class N8NIntegrationClient:
    """Cliente para integración con N8N"""
    
    def __init__(self, n8n_url: str = "http://localhost:5678"):
        self.base_url = n8n_url
        self.session = None
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_callbacks: Dict[str, List[Callable]] = {}
        
        # Configuración de workflows disponibles
        self.available_workflows = {
            "main_orchestrator": CampaignWorkflowConfig(
                workflow_name="main_orchestrator",
                priority=WorkflowPriority.HIGH,
                timeout=1800,  # 30 minutos
                retry_count=2,
                webhook_url="/webhook/main-orchestrator",
                input_mapping={
                    "artist": "campaign.artist",
                    "song": "campaign.song", 
                    "budget": "campaign.budget",
                    "platforms": "campaign.platforms"
                },
                output_handlers=["campaign_completed", "metrics_updated"]
            ),
            
            "ml_decision_engine": CampaignWorkflowConfig(
                workflow_name="ml_decision_engine",
                priority=WorkflowPriority.HIGH,
                timeout=300,  # 5 minutos
                retry_count=3,
                webhook_url="/webhook/ml-decision",
                input_mapping={
                    "video_path": "content.video_path",
                    "content_type": "analysis.content_type",
                    "target_audience": "targeting.audience"
                },
                output_handlers=["ml_analysis_completed", "recommendations_generated"]
            ),
            
            "device_farm_trigger": CampaignWorkflowConfig(
                workflow_name="device_farm_trigger", 
                priority=WorkflowPriority.MEDIUM,
                timeout=600,  # 10 minutos
                retry_count=2,
                webhook_url="/webhook/device-farm",
                input_mapping={
                    "action": "device.action",
                    "target_devices": "device.targets",
                    "content": "device.content"
                },
                output_handlers=["device_actions_completed", "engagement_metrics"]
            ),
            
            "viral_content_generator": CampaignWorkflowConfig(
                workflow_name="viral_content_generator",
                priority=WorkflowPriority.MEDIUM,
                timeout=900,  # 15 minutos
                retry_count=1,
                webhook_url="/webhook/viral-content",
                input_mapping={
                    "genre": "content.genre",
                    "trending_topics": "content.trends",
                    "target_demographics": "content.demographics"
                },
                output_handlers=["content_generated", "viral_score_calculated"]
            ),
            
            "meta_ads_orchestrator": CampaignWorkflowConfig(
                workflow_name="meta_ads_orchestrator",
                priority=WorkflowPriority.HIGH,
                timeout=600,  # 10 minutos
                retry_count=2,
                webhook_url="/webhook/meta-ads",
                input_mapping={
                    "campaign_objective": "ads.objective",
                    "budget": "ads.budget",
                    "targeting": "ads.targeting",
                    "creative_assets": "ads.creative"
                },
                output_handlers=["ads_campaign_created", "performance_tracking_started"]
            ),
            
            "community_management_auto": CampaignWorkflowConfig(
                workflow_name="community_management_auto",
                priority=WorkflowPriority.CRITICAL,
                timeout=1200,  # 20 minutos
                retry_count=1,
                webhook_url="/webhook/community-management",
                input_mapping={
                    "platforms": "community.platforms",
                    "engagement_rules": "community.rules",
                    "response_templates": "community.templates"
                },
                output_handlers=["community_actions_completed", "engagement_analytics"]
            )
        }
    
    async def initialize(self):
        """Inicializar cliente N8N"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Verificar conexión con N8N
        await self._health_check()
        
        # Inicializar monitoreo de ejecuciones
        self._start_execution_monitor()
        
        logger.info("N8N Integration Client initialized successfully")
    
    async def close(self):
        """Cerrar cliente"""
        if self.session:
            await self.session.close()
    
    async def _health_check(self) -> bool:
        """Verificar estado de N8N"""
        try:
            async with self.session.get(f"{self.base_url}/healthz") as response:
                if response.status == 200:
                    logger.info("✅ N8N connection healthy")
                    return True
                else:
                    logger.warning(f"⚠️ N8N health check returned {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ N8N health check failed: {e}")
            return False
    
    async def trigger_workflow(self, workflow_name: str, payload: Dict[str, Any]) -> str:
        """Triggear workflow específico"""
        if workflow_name not in self.available_workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow_config = self.available_workflows[workflow_name]
        
        try:
            # Mapear datos de entrada según configuración
            mapped_payload = self._map_input_data(payload, workflow_config.input_mapping)
            
            # Agregar metadatos
            execution_payload = {
                "execution_id": f"exec_{int(time.time())}_{workflow_name}",
                "timestamp": datetime.now().isoformat(),
                "priority": workflow_config.priority.value,
                "data": mapped_payload
            }
            
            # Hacer request a webhook
            webhook_url = urljoin(self.base_url, workflow_config.webhook_url)
            
            async with self.session.post(webhook_url, json=execution_payload) as response:
                if response.status in [200, 201]:
                    response_data = await response.json()
                    execution_id = execution_payload["execution_id"]
                    
                    # Registrar ejecución
                    execution = WorkflowExecution(
                        execution_id=execution_id,
                        workflow_name=workflow_name,
                        status=WorkflowStatus.RUNNING,
                        started_at=datetime.now(),
                        completed_at=None,
                        input_data=payload,
                        output_data=None,
                        error_message=None
                    )
                    
                    self.active_executions[execution_id] = execution
                    
                    logger.info(f"✅ Workflow {workflow_name} triggered: {execution_id}")
                    return execution_id
                
                else:
                    error_msg = f"Webhook request failed: {response.status}"
                    logger.error(f"❌ {error_msg}")
                    raise Exception(error_msg)
        
        except Exception as e:
            logger.error(f"❌ Error triggering workflow {workflow_name}: {e}")
            raise
    
    def _map_input_data(self, payload: Dict[str, Any], input_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Mapear datos de entrada según configuración"""
        mapped_data = {}
        
        for target_key, source_path in input_mapping.items():
            try:
                # Navegar por la estructura anidada (ej: "campaign.artist")
                value = payload
                for key in source_path.split('.'):
                    value = value[key]
                mapped_data[target_key] = value
            except (KeyError, TypeError):
                logger.warning(f"Missing or invalid data for {source_path}")
                mapped_data[target_key] = None
        
        return mapped_data
    
    async def launch_viral_campaign_workflow(self, campaign_config: Dict[str, Any]) -> Dict[str, str]:
        """Lanzar workflow completo de campaña viral"""
        logger.info("🚀 Launching complete viral campaign workflow...")
        
        execution_ids = {}
        
        try:
            # 1. Trigger ML Decision Engine first
            ml_payload = {
                "content": {
                    "video_path": campaign_config.get("video_path"),
                    "content_type": "video"
                },
                "analysis": {
                    "content_type": campaign_config.get("genre", "trap")
                },
                "targeting": {
                    "audience": campaign_config.get("target_countries", ["US", "MX"])
                }
            }
            
            ml_execution_id = await self.trigger_workflow("ml_decision_engine", ml_payload)
            execution_ids["ml_decision"] = ml_execution_id
            
            # 2. Wait for ML analysis (simplified - en producción usaríamos callbacks)
            await asyncio.sleep(5)
            
            # 3. Trigger Main Orchestrator with campaign
            main_payload = {
                "campaign": {
                    "artist": campaign_config.get("artist"),
                    "song": campaign_config.get("song"),
                    "budget": campaign_config.get("budget"),
                    "platforms": campaign_config.get("platforms", ["tiktok", "instagram"])
                }
            }
            
            main_execution_id = await self.trigger_workflow("main_orchestrator", main_payload)
            execution_ids["main_orchestrator"] = main_execution_id
            
            # 4. Trigger Meta Ads if enabled
            if campaign_config.get("meta_ads_enabled", True):
                ads_payload = {
                    "ads": {
                        "objective": "REACH",
                        "budget": campaign_config.get("budget"),
                        "targeting": {
                            "countries": campaign_config.get("target_countries"),
                            "interests": ["music", "trap", "reggaeton"]
                        },
                        "creative": {
                            "video_path": campaign_config.get("video_path"),
                            "caption": f"🎵 {campaign_config.get('artist')} - {campaign_config.get('song')}"
                        }
                    }
                }
                
                ads_execution_id = await self.trigger_workflow("meta_ads_orchestrator", ads_payload)
                execution_ids["meta_ads"] = ads_execution_id
            
            # 5. Trigger Device Farm if enabled
            if campaign_config.get("device_farm_enabled", False):
                device_payload = {
                    "device": {
                        "action": "post_content",
                        "targets": ["device_01", "device_02", "device_03"],
                        "content": {
                            "video": campaign_config.get("video_path"),
                            "caption": f"{campaign_config.get('artist')} - {campaign_config.get('song')} #viral #trap"
                        }
                    }
                }
                
                device_execution_id = await self.trigger_workflow("device_farm_trigger", device_payload)
                execution_ids["device_farm"] = device_execution_id
            
            # 6. Trigger Community Management
            community_payload = {
                "community": {
                    "platforms": campaign_config.get("platforms", ["tiktok", "instagram"]),
                    "rules": {
                        "auto_like": True,
                        "auto_comment": True,
                        "engagement_threshold": 100
                    },
                    "templates": {
                        "thank_you": "¡Gracias por el apoyo! 🔥",
                        "promo": f"Nueva música de {campaign_config.get('artist')} 🎵"
                    }
                }
            }
            
            community_execution_id = await self.trigger_workflow("community_management_auto", community_payload)
            execution_ids["community_management"] = community_execution_id
            
            logger.info(f"✅ Campaign workflow launched with {len(execution_ids)} executions")
            return execution_ids
            
        except Exception as e:
            logger.error(f"❌ Error launching campaign workflow: {e}")
            raise
    
    def _start_execution_monitor(self):
        """Iniciar monitoreo de ejecuciones en background"""
        def monitor_loop():
            while True:
                try:
                    self._check_execution_status()
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.error(f"Execution monitor error: {e}")
                    time.sleep(30)  # Wait longer on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("🔍 Started execution monitoring thread")
    
    def _check_execution_status(self):
        """Verificar estado de ejecuciones activas"""
        # En una implementación real, esto consultaría la API de N8N
        # Por ahora, simulamos la actualización de estados
        
        for execution_id, execution in list(self.active_executions.items()):
            if execution.status == WorkflowStatus.RUNNING:
                # Simular progreso de ejecución
                elapsed_time = datetime.now() - execution.started_at
                
                # Simular completación después de cierto tiempo
                if elapsed_time.total_seconds() > 60:  # 1 minuto para demo
                    execution.status = WorkflowStatus.COMPLETED
                    execution.completed_at = datetime.now()
                    execution.output_data = {
                        "status": "success",
                        "duration": elapsed_time.total_seconds(),
                        "results": {"demo": "completed"}
                    }
                    
                    # Ejecutar callbacks
                    self._execute_callbacks(execution_id, execution)
                    
                    logger.info(f"✅ Execution {execution_id} completed")
    
    def _execute_callbacks(self, execution_id: str, execution: WorkflowExecution):
        """Ejecutar callbacks para ejecución completada"""
        if execution_id in self.execution_callbacks:
            for callback in self.execution_callbacks[execution_id]:
                try:
                    callback(execution)
                except Exception as e:
                    logger.error(f"Callback error for {execution_id}: {e}")
    
    def add_execution_callback(self, execution_id: str, callback: Callable[[WorkflowExecution], None]):
        """Agregar callback para ejecución específica"""
        if execution_id not in self.execution_callbacks:
            self.execution_callbacks[execution_id] = []
        
        self.execution_callbacks[execution_id].append(callback)
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Obtener estado de ejecución específica"""
        return self.active_executions.get(execution_id)
    
    def get_active_executions(self) -> List[WorkflowExecution]:
        """Obtener todas las ejecuciones activas"""
        return [exec for exec in self.active_executions.values() 
                if exec.status in [WorkflowStatus.RUNNING]]
    
    def get_workflow_history(self, limit: int = 50) -> List[WorkflowExecution]:
        """Obtener historial de ejecuciones"""
        all_executions = list(self.active_executions.values())
        all_executions.sort(key=lambda x: x.started_at, reverse=True)
        return all_executions[:limit]

# ============================================
# INTEGRATION HELPERS
# ============================================

class DashboardN8NIntegration:
    """Integración específica entre dashboards y N8N"""
    
    def __init__(self, n8n_client: N8NIntegrationClient):
        self.n8n_client = n8n_client
        self.campaign_executions: Dict[str, Dict[str, str]] = {}
    
    async def launch_campaign_from_dashboard(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Lanzar campaña desde dashboard con integración completa N8N"""
        try:
            # Lanzar workflows
            execution_ids = await self.n8n_client.launch_viral_campaign_workflow(campaign_config)
            
            # Registrar campaña
            campaign_id = campaign_config.get("campaign_id", f"camp_{int(time.time())}")
            self.campaign_executions[campaign_id] = execution_ids
            
            # Configurar callbacks para monitoreo
            self._setup_campaign_callbacks(campaign_id, execution_ids)
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "execution_ids": execution_ids,
                "message": f"Campaign launched with {len(execution_ids)} workflows",
                "estimated_completion": "15-30 minutes"
            }
            
        except Exception as e:
            logger.error(f"Error launching campaign from dashboard: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to launch campaign workflows"
            }
    
    def _setup_campaign_callbacks(self, campaign_id: str, execution_ids: Dict[str, str]):
        """Configurar callbacks para monitoreo de campaña"""
        def campaign_callback(execution: WorkflowExecution):
            logger.info(f"📊 Campaign {campaign_id} - Workflow {execution.workflow_name} completed")
            
            # Aquí se pueden agregar notificaciones, updates de dashboard, etc.
            if execution.status == WorkflowStatus.COMPLETED:
                self._handle_workflow_completion(campaign_id, execution)
            elif execution.status == WorkflowStatus.ERROR:
                self._handle_workflow_error(campaign_id, execution)
        
        # Agregar callback a cada ejecución
        for workflow_name, execution_id in execution_ids.items():
            self.n8n_client.add_execution_callback(execution_id, campaign_callback)
    
    def _handle_workflow_completion(self, campaign_id: str, execution: WorkflowExecution):
        """Manejar completación de workflow"""
        logger.info(f"✅ Campaign {campaign_id} - {execution.workflow_name} completed successfully")
        
        # Aquí se pueden agregar:
        # - Updates de métricas en dashboard
        # - Notificaciones push
        # - Logs de analytics
        # - Triggers de workflows dependientes
    
    def _handle_workflow_error(self, campaign_id: str, execution: WorkflowExecution):
        """Manejar error de workflow"""
        logger.error(f"❌ Campaign {campaign_id} - {execution.workflow_name} failed: {execution.error_message}")
        
        # Aquí se pueden agregar:
        # - Alertas de error en dashboard
        # - Reintentos automáticos
        # - Rollback de acciones
        # - Notificaciones de soporte
    
    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Obtener estado completo de campaña"""
        if campaign_id not in self.campaign_executions:
            return {"error": "Campaign not found"}
        
        execution_ids = self.campaign_executions[campaign_id]
        workflow_statuses = {}
        
        for workflow_name, execution_id in execution_ids.items():
            execution = self.n8n_client.get_execution_status(execution_id)
            if execution:
                workflow_statuses[workflow_name] = {
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "error": execution.error_message
                }
        
        # Calcular estado general
        statuses = [status["status"] for status in workflow_statuses.values()]
        if "error" in statuses:
            overall_status = "error"
        elif "running" in statuses:
            overall_status = "running"
        elif all(status == "completed" for status in statuses):
            overall_status = "completed"
        else:
            overall_status = "partial"
        
        return {
            "campaign_id": campaign_id,
            "overall_status": overall_status,
            "workflows": workflow_statuses,
            "progress": len([s for s in statuses if s == "completed"]) / len(statuses) * 100
        }

# ============================================
# SINGLETON INSTANCE
# ============================================

_n8n_client: Optional[N8NIntegrationClient] = None
_dashboard_integration: Optional[DashboardN8NIntegration] = None

async def get_n8n_client() -> N8NIntegrationClient:
    """Obtener cliente N8N singleton"""
    global _n8n_client
    
    if _n8n_client is None:
        _n8n_client = N8NIntegrationClient()
        await _n8n_client.initialize()
    
    return _n8n_client

async def get_dashboard_integration() -> DashboardN8NIntegration:
    """Obtener integración dashboard-N8N singleton"""
    global _dashboard_integration
    
    if _dashboard_integration is None:
        n8n_client = await get_n8n_client()
        _dashboard_integration = DashboardN8NIntegration(n8n_client)
    
    return _dashboard_integration

# ============================================
# EXAMPLE USAGE & TESTING
# ============================================

async def test_n8n_integration():
    """Test completo de integración N8N"""
    print("🧪 Testing N8N Integration...")
    
    try:
        # Inicializar cliente
        client = await get_n8n_client()
        integration = await get_dashboard_integration()
        
        # Configuración de campaña de prueba
        campaign_config = {
            "campaign_id": "test_001",
            "artist": "Stakas Test",
            "song": "Integration Test",
            "genre": "trap",
            "video_path": "/data/videos/test.mp4",
            "budget": 50,
            "platforms": ["tiktok", "instagram"],
            "target_countries": ["US", "MX"],
            "meta_ads_enabled": True,
            "device_farm_enabled": False
        }
        
        # Lanzar campaña
        result = await integration.launch_campaign_from_dashboard(campaign_config)
        print(f"📊 Campaign launch result: {result}")
        
        if result["success"]:
            campaign_id = result["campaign_id"]
            
            # Monitorear progreso
            for i in range(5):
                await asyncio.sleep(10)
                status = integration.get_campaign_status(campaign_id)
                print(f"📈 Campaign status (check {i+1}): {status}")
                
                if status.get("overall_status") == "completed":
                    break
        
        # Mostrar historial
        history = client.get_workflow_history(5)
        print(f"📜 Recent executions: {len(history)}")
        
        await client.close()
        print("✅ N8N Integration test completed")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    # Ejecutar test
    asyncio.run(test_n8n_integration())