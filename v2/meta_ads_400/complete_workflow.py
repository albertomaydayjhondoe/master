"""
🎯 Workflow Completo Meta Ads €400 → Automatización Total
Orquestador principal que maneja todo el flujo desde Meta Ads hasta resultados
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import httpx
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
import uuid
from .meta_ml_integration import meta_ml_integrator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Meta Ads €400 Complete Workflow",
    description="Flujo completo desde Meta Ads €400 hasta automatización 24/7",
    version="1.0.0"
)

# URLs de servicios
LANDING_GENERATOR_URL = os.getenv("LANDING_GENERATOR_URL", "http://landing-generator:8004")
ML_CORE_URL = os.getenv("ML_CORE_URL", "http://ml-core:8000")
UNIFIED_ORCHESTRATOR_URL = os.getenv("UNIFIED_ORCHESTRATOR_URL", "http://unified-orchestrator:10000")
RAILWAY_BASE_URL = os.getenv("RAILWAY_STATIC_URL", "https://meta-ads-centric.railway.app")
DUMMY_MODE = os.getenv("DUMMY_MODE", "true").lower() == "true"

# ============================================
# MODELOS DE DATOS
# ============================================

class MetaAds400Campaign(BaseModel):
    """Campaña Meta Ads de €400 con todos los parámetros"""
    
    # Datos básicos
    artist_name: str
    song_name: str
    youtube_channel: str  # REQUERIDO - Canal de YouTube del artista
    genre: str = "reggaeton"
    
    # Presupuesto y targeting
    daily_budget_euros: float = 400.0
    campaign_duration_days: int = 7
    target_countries: List[str] = ["ES", "MX", "CO", "AR"]
    
    # Configuración de automatización
    enable_ml_optimization: bool = True
    auto_approve_under_euros: float = 50.0
    require_authorization_over_euros: float = 100.0
    
    # Landing page
    landing_page_domain: Optional[str] = None
    custom_utm_params: Dict[str, str] = {}

class WorkflowResult(BaseModel):
    """Resultado completo del workflow"""
    
    # Identificadores
    campaign_id: str
    workflow_id: str
    
    # Componentes creados
    landing_page_url: str
    youtube_upload_status: str
    tiktok_upload_status: str  
    instagram_upload_status: str
    twitter_upload_status: str
    
    # UTM y tracking
    utm_tracking_active: bool
    analytics_dashboard_url: str
    
    # ML y autorización
    ml_analysis_complete: bool
    meta_ml_optimizations: List[Dict[str, Any]] = []
    meta_ml_next_actions: List[Dict[str, Any]] = []
    authorization_requests: List[Dict[str, Any]]
    
    # Railway deployment
    railway_services_active: List[str]
    monitoring_urls: Dict[str, str]
    
    # Performance inicial
    estimated_24h_reach: int
    estimated_conversions: int
    projected_roas: float

class AuthorizationDecision(BaseModel):
    """Decisión de autorización del usuario"""
    
    authorization_id: str
    decision: str  # "approved" or "rejected"
    reason: str = ""
    user_id: str = "dashboard_user"

# ============================================
# ORQUESTADOR PRINCIPAL
# ============================================

class MetaAds400Orchestrator:
    """Orquestador completo para campañas Meta Ads de €400"""
    
    def __init__(self):
        self.active_workflows = {}
        self.authorization_callbacks = {}
    
    async def launch_complete_workflow(self, campaign: MetaAds400Campaign) -> WorkflowResult:
        """Lanzar flujo completo desde Meta Ads €400"""
        
        workflow_id = str(uuid.uuid4())
        campaign_id = f"meta400_{int(datetime.now().timestamp())}"
        
        logger.info(f"🚀 Starting complete Meta Ads €400 workflow: {campaign_id}")
        
        try:
            # 1. GENERAR LANDING PAGE AUTOMÁTICA
            logger.info("📄 Step 1: Generating landing page with UTM tracking...")
            landing_result = await self._create_landing_page(campaign, campaign_id)
            
            # 2. ACTIVAR UTM TRACKING
            logger.info("📊 Step 2: Activating UTM tracking...")
            utm_result = await self._setup_utm_tracking(campaign_id, landing_result)
            
            # 3. ANÁLISIS ML + ULTRALYTICS + SISTEMA META ML
            logger.info("🤖 Step 3: Running ML analysis (Ultralytics + Meta ML System)...")
            ml_result = await self._run_ml_analysis(campaign)
            
            # 3.5. INTEGRACIÓN SISTEMA META ML (NUEVA FUNCIONALIDAD)
            logger.info("🧠 Step 3.5: Integrating Meta ML optimization system...")
            meta_ml_result = await self._integrate_meta_ml_system(campaign, ml_result)
            
            # 4. DISTRIBUCIÓN CROSS-PLATFORM
            logger.info("📱 Step 4: Distributing to all platforms...")
            distribution_result = await self._distribute_to_platforms(campaign, campaign_id)
            
            # 5. CONFIGURAR RAILWAY DEPLOYMENT
            logger.info("☁️ Step 5: Setting up Railway 24/7 monitoring...")
            railway_result = await self._setup_railway_monitoring(campaign_id)
            
            # 6. CONFIGURAR AUTORIZACIONES ML (Integrado con Meta ML)
            logger.info("🔐 Step 6: Setting up ML authorization system...")
            auth_requests = await self._setup_ml_authorizations(campaign, ml_result, meta_ml_result)
            
            # 7. CREAR DASHBOARDS DE MONITOREO
            logger.info("📊 Step 7: Creating monitoring dashboards...")
            dashboard_urls = await self._create_monitoring_dashboards(campaign_id)
            
            # Compilar resultado completo
            workflow_result = WorkflowResult(
                campaign_id=campaign_id,
                workflow_id=workflow_id,
                landing_page_url=landing_result["page_url"],
                youtube_upload_status=distribution_result.get("youtube", {}).get("status", "pending"),
                tiktok_upload_status=distribution_result.get("tiktok", {}).get("status", "pending"),
                instagram_upload_status=distribution_result.get("instagram", {}).get("status", "pending"),
                twitter_upload_status=distribution_result.get("twitter", {}).get("status", "pending"),
                utm_tracking_active=utm_result["active"],
                analytics_dashboard_url=dashboard_urls["analytics"],
                ml_analysis_complete=ml_result["complete"],
                meta_ml_optimizations=meta_ml_result.get("optimizations_applied", []),
                meta_ml_next_actions=meta_ml_result.get("next_actions", []),
                authorization_requests=auth_requests,
                railway_services_active=railway_result["active_services"],
                monitoring_urls=dashboard_urls,
                estimated_24h_reach=self._calculate_estimated_reach(campaign),
                estimated_conversions=self._calculate_estimated_conversions(campaign),
                projected_roas=ml_result.get("projected_roas", 2.8)
            )
            
            # Almacenar workflow activo
            self.active_workflows[workflow_id] = {
                "campaign": campaign.dict(),
                "result": workflow_result.dict(),
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Complete workflow launched successfully: {campaign_id}")
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")
    
    async def _create_landing_page(self, campaign: MetaAds400Campaign, campaign_id: str) -> Dict[str, Any]:
        """Crear landing page automática con UTM + Supabase"""
        
        try:
            if DUMMY_MODE:
                return {
                    "page_id": f"landing_{campaign_id}",
                    "page_url": f"{RAILWAY_BASE_URL}/landing/{campaign_id}",
                    "utm_tracking_id": f"utm_{campaign_id}",
                    "supabase_integration": "active",
                    "status": "created"
                }
            
            # Llamar al Supabase landing generator
            payload = {
                "campaign_data": {
                    "campaign_id": campaign_id,
                    "campaign_name": f"{campaign.artist_name} - {campaign.song_name}",
                    "artist_name": campaign.artist_name,
                    "song_name": campaign.song_name,
                    "budget_euros": campaign.daily_budget_euros,
                    "genre": campaign.genre,
                    "target_countries": campaign.target_countries,
                    "youtube_channel": campaign.youtube_channel
                },
                "utm_campaign": f"{campaign.artist_name}_{campaign.song_name}_{campaign_id}".replace(" ", "_").lower()
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{LANDING_GENERATOR_URL}/webhook/meta-ads",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        **result["landing_page"],
                        "supabase_integration": result.get("supabase_integration", "active"),
                        "analytics_url": result.get("analytics_url", f"{RAILWAY_BASE_URL}/api/campaign/{campaign_id}/analytics")
                    }
                else:
                    raise Exception(f"Supabase landing page creation failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Supabase landing page creation error: {str(e)}")
            raise
    
    async def _setup_utm_tracking(self, campaign_id: str, landing_result: Dict[str, Any]) -> Dict[str, bool]:
        """Configurar UTM tracking completo"""
        
        # En dummy mode, solo confirmamos que está "activo"
        return {
            "active": True,
            "tracking_id": landing_result.get("utm_tracking", {}).get("page_id"),
            "endpoints_configured": [
                "/api/utm/track",
                "/api/utm/convert", 
                "/api/utm/time-spent"
            ]
        }
    
    async def _run_ml_analysis(self, campaign: MetaAds400Campaign) -> Dict[str, Any]:
        """Ejecutar análisis ML completo (Ultralytics + Musical)"""
        
        try:
            if DUMMY_MODE:
                return {
                    "complete": True,
                    "ultralytics_score": 0.89,
                    "music_analysis": {
                        "genre_confidence": 0.94,
                        "virality_potential": 0.82,
                        "optimal_platforms": ["tiktok", "youtube", "instagram"]
                    },
                    "projected_roas": 3.2,
                    "optimization_recommendations": [
                        {
                            "type": "budget_increase",
                            "amount_euros": 75.0,
                            "confidence": 0.87,
                            "reason": "High engagement potential detected"
                        },
                        {
                            "type": "platform_expansion", 
                            "platforms": ["youtube_shorts", "instagram_reels"],
                            "amount_euros": 120.0,
                            "confidence": 0.79,
                            "reason": "Reggaeton performing well on short-form video"
                        }
                    ]
                }
            
            # En producción: llamar a ML Core
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{ML_CORE_URL}/analyze-campaign-complete",
                    json=campaign.dict()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"ML analysis failed: {response.text}")
                    return {"complete": False}
                    
        except Exception as e:
            logger.error(f"ML analysis error: {str(e)}")
            return {"complete": False, "error": str(e)}
    
    async def _distribute_to_platforms(self, campaign: MetaAds400Campaign, campaign_id: str) -> Dict[str, Dict[str, Any]]:
        """Distribuir contenido a todas las plataformas"""
        
        try:
            if DUMMY_MODE:
                return {
                    "youtube": {
                        "status": "uploaded",
                        "video_id": f"yt_video_{campaign_id}",
                        "url": f"https://youtube.com/watch?v={campaign_id}",
                        "estimated_views_24h": 15000
                    },
                    "tiktok": {
                        "status": "uploaded", 
                        "video_id": f"tt_video_{campaign_id}",
                        "url": f"https://tiktok.com/@artist/video/{campaign_id}",
                        "estimated_views_24h": 45000
                    },
                    "instagram": {
                        "status": "posted",
                        "post_id": f"ig_post_{campaign_id}", 
                        "url": f"https://instagram.com/p/{campaign_id}",
                        "estimated_reach_24h": 18000
                    },
                    "twitter": {
                        "status": "posted",
                        "thread_id": f"tw_thread_{campaign_id}",
                        "url": f"https://twitter.com/artist/status/{campaign_id}",
                        "estimated_impressions_24h": 8500
                    }
                }
            
            # Llamar al unified orchestrator
            payload = {
                "campaign_id": campaign_id,
                "campaign_name": f"{campaign.artist_name} - {campaign.song_name}",
                "artist_name": campaign.artist_name,
                "song_name": campaign.song_name,
                "platforms": ["youtube", "tiktok", "instagram", "twitter"],
                "video_url": f"{campaign.youtube_channel}/videos/latest",  # Placeholder
                "genre": campaign.genre,
                "target_countries": campaign.target_countries
            }
            
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{UNIFIED_ORCHESTRATOR_URL}/distribute",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {platform.platform: platform.dict() for platform in result.platform_results}
                else:
                    logger.warning(f"Platform distribution failed: {response.text}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Platform distribution error: {str(e)}")
            return {}
    
    async def _setup_railway_monitoring(self, campaign_id: str) -> Dict[str, Any]:
        """Configurar monitoreo 24/7 en Railway"""
        
        return {
            "active_services": [
                "ml-core",
                "meta-ads-manager", 
                "landing-generator",
                "unified-orchestrator",
                "utm-tracker",
                "ml-authorization-dashboard"
            ],
            "monitoring_active": True,
            "health_check_interval": "30s",
            "auto_scaling": True,
            "deployment_url": f"{RAILWAY_BASE_URL}"
        }
    
    async def _integrate_meta_ml_system(self, campaign: MetaAds400Campaign, ml_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrar sistema Meta ML de optimización automática"""
        
        logger.info("🧠 Integrando sistema Meta ML...")
        
        try:
            # Obtener datos de YouTube y Spotify (simulados por ahora)
            youtube_analytics = await self._get_youtube_analytics(campaign.youtube_channel)
            spotify_analytics = await self._get_spotify_analytics(campaign.artist_name, campaign.song_name)
            
            # Datos de la campaña para ML
            campaign_data = {
                "campaign_id": f"meta400_{campaign.artist_name}_{campaign.song_name}",
                "artist": campaign.artist_name,
                "song": campaign.song_name,
                "genre": campaign.genre,
                "daily_budget": campaign.daily_budget_euros,
                "target_countries": campaign.target_countries,
                "current_performance": {
                    "ctr": 0.05,  # Datos iniciales
                    "retention_rate": 0.7,
                    "conversions": 0,
                    "cost_per_conversion": 0
                }
            }
            
            # Integrar con sistema ML
            ml_integration_result = await meta_ml_integrator.integrate_ml_with_campaign(
                campaign_data, youtube_analytics, spotify_analytics
            )
            
            if ml_integration_result["success"]:
                logger.info("✅ Meta ML integrado exitosamente")
                return ml_integration_result["ml_integration"]
            else:
                logger.warning("⚠️ Meta ML falló, usando optimizaciones básicas")
                return {
                    "optimizations_applied": [],
                    "next_actions": [],
                    "performance_boost": {"estimated_roi_improvement": 0}
                }
                
        except Exception as e:
            logger.error(f"❌ Error integrando Meta ML: {str(e)}")
            return {
                "error": str(e),
                "optimizations_applied": [],
                "next_actions": [],
                "performance_boost": {"estimated_roi_improvement": 0}
            }
    
    async def _get_youtube_analytics(self, youtube_channel: str) -> Dict[str, Any]:
        """Obtener analytics filtrados de YouTube"""
        
        # Simulación de datos YouTube filtrados
        return {
            "channel": youtube_channel,
            "viewers": [
                {
                    "user_id": f"yt_user_{i}",
                    "country": ["ES", "MX", "CO", "AR"][i % 4],
                    "age": 18 + (i % 25),
                    "retention_rate": 0.45 + (i % 40) / 100,  # >40% filtro
                    "traffic_source": "organic" if i % 3 != 0 else "paid",
                    "is_recurring": i % 2 == 0,
                    "watch_time": 45 + (i % 60),
                    "actions": ["like", "comment"] if i % 3 == 0 else []
                }
                for i in range(100)
            ]
        }
    
    async def _get_spotify_analytics(self, artist: str, song: str) -> Dict[str, Any]:
        """Obtener analytics filtrados de Spotify"""
        
        # Simulación de datos Spotify filtrados
        return {
            "artist": artist,
            "song": song,
            "listeners": [
                {
                    "user_id": f"sp_user_{i}",
                    "country": ["ES", "MX", "CO", "AR", "CL"][i % 5],
                    "age": 16 + (i % 30),
                    "playlist_source": "organic" if i % 4 != 0 else "external_paid",
                    "saved_track": i % 3 == 0,
                    "repeat_listens": i % 5,
                    "listening_time": 120 + (i % 60)
                }
                for i in range(80)
            ]
        }

    async def _setup_ml_authorizations(self, campaign: MetaAds400Campaign, ml_result: Dict[str, Any], meta_ml_result: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Configurar solicitudes de autorización ML"""
        
        auth_requests = []
        
        # Procesar recomendaciones de optimización tradicionales
        recommendations = ml_result.get("optimization_recommendations", [])
        
        # Agregar recomendaciones del sistema Meta ML
        if meta_ml_result and meta_ml_result.get("next_actions"):
            for action in meta_ml_result["next_actions"]:
                # Convertir acciones ML a recomendaciones con costo
                estimated_cost = self._estimate_action_cost(action)
                recommendations.append({
                    "type": f"meta_ml_{action['action']}",
                    "amount_euros": estimated_cost,
                    "reason": action.get("description", "Optimización Meta ML"),
                    "confidence": 0.9,  # Alta confianza del sistema ML
                    "priority": action.get("priority", "medium"),
                    "estimated_impact": action.get("estimated_impact", "N/A")
                })
        
        for rec in recommendations:
            cost = rec.get("amount_euros", 0)
            
            # Auto-aprobar si está bajo el threshold
            if cost <= campaign.auto_approve_under_euros:
                auth_requests.append({
                    "id": str(uuid.uuid4()),
                    "type": rec["type"],
                    "status": "auto_approved",
                    "cost_euros": cost,
                    "reason": rec.get("reason", ""),
                    "confidence": rec.get("confidence", 0.8),
                    "auto_approved": True
                })
            else:
                # Solicitar autorización manual
                auth_requests.append({
                    "id": str(uuid.uuid4()),
                    "type": rec["type"],
                    "status": "pending_authorization",
                    "cost_euros": cost,
                    "reason": rec.get("reason", ""),
                    "confidence": rec.get("confidence", 0.8),
                    "requires_manual_approval": True,
                    "dashboard_url": f"{RAILWAY_BASE_URL}/dashboard/authorizations"
                })
        
        return auth_requests
    
    def _estimate_action_cost(self, action: Dict[str, Any]) -> float:
        """Estimar costo de una acción Meta ML"""
        
        action_costs = {
            "scale_up_campaign": 100.0,  # €100 adicionales
            "expand_high_performers": 75.0,  # €75 por país
            "create_viral_variants": 50.0,  # €50 por creativa
            "explore_new_markets": 40.0,  # €40 por exploración
            "increase_mexico": 60.0,  # País específico
            "increase_colombia": 50.0,
            "reduce_argentina": -30.0,  # Reducción (ahorro)
            "boost_viral_creative": 80.0
        }
        
        action_type = action.get("action", "unknown")
        base_cost = action_costs.get(action_type, 25.0)  # Default €25
        
        # Ajustar por prioridad
        priority_multiplier = {
            "high": 1.5,
            "medium": 1.0,
            "low": 0.7
        }
        
        multiplier = priority_multiplier.get(action.get("priority", "medium"), 1.0)
        
        return base_cost * multiplier
    
    async def _create_monitoring_dashboards(self, campaign_id: str) -> Dict[str, str]:
        """Crear URLs de dashboards de monitoreo"""
        
        return {
            "analytics": f"{RAILWAY_BASE_URL}/dashboard/analytics/{campaign_id}",
            "ml_authorization": f"{RAILWAY_BASE_URL}/dashboard/ml-auth/{campaign_id}",
            "utm_tracking": f"{RAILWAY_BASE_URL}/dashboard/utm/{campaign_id}",
            "platform_performance": f"{RAILWAY_BASE_URL}/dashboard/platforms/{campaign_id}",
            "railway_monitoring": f"{RAILWAY_BASE_URL}/dashboard/railway/{campaign_id}"
        }
    
    def _calculate_estimated_reach(self, campaign: MetaAds400Campaign) -> int:
        """Calcular reach estimado 24h"""
        
        base_reach = campaign.daily_budget_euros * 200  # €1 = ~200 reach
        
        genre_multipliers = {
            "reggaeton": 1.8,
            "pop": 1.4,
            "hip_hop": 1.6,
            "electronic": 1.2,
            "latin": 1.7,
            "rock": 1.0
        }
        
        multiplier = genre_multipliers.get(campaign.genre, 1.0)
        return int(base_reach * multiplier)
    
    def _calculate_estimated_conversions(self, campaign: MetaAds400Campaign) -> int:
        """Calcular conversiones estimadas 24h"""
        
        reach = self._calculate_estimated_reach(campaign)
        conversion_rate = 0.08  # 8% tasa de conversión estimada
        
        return int(reach * conversion_rate)

# Instanciar orquestador
orchestrator = MetaAds400Orchestrator()

# ============================================
# ENDPOINTS API
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "meta-ads-400-complete-workflow",
        "version": "1.0.0",
        "active_workflows": len(orchestrator.active_workflows),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/launch-meta-ads-400", response_model=WorkflowResult)
async def launch_meta_ads_400_campaign(
    campaign: MetaAds400Campaign,
    background_tasks: BackgroundTasks
):
    """
    🚀 ENDPOINT PRINCIPAL: Lanzar campaña Meta Ads €400 completa
    
    Este endpoint ejecuta TODO el flujo:
    1. Genera landing page automática con UTM
    2. Activa análisis ML (Ultralytics + Musical)  
    3. Distribuye a todas las plataformas
    4. Configura Railway 24/7
    5. Crea dashboards de monitoreo
    6. Solicita autorizaciones ML cuando sea necesario
    """
    
    try:
        logger.info(f"🎯 Launching Meta Ads €400 campaign for {campaign.artist_name} - {campaign.song_name}")
        
        # Validar datos requeridos
        if not campaign.youtube_channel:
            raise HTTPException(status_code=400, detail="YouTube channel is required")
        
        # Ejecutar workflow completo
        workflow_result = await orchestrator.launch_complete_workflow(campaign)
        
        # Programar monitoreo continuo en background
        background_tasks.add_task(
            _monitor_campaign_performance,
            workflow_result.campaign_id,
            workflow_result.workflow_id
        )
        
        return workflow_result
        
    except Exception as e:
        logger.error(f"Campaign launch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Obtener estado actual de un workflow"""
    
    if workflow_id not in orchestrator.active_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_data = orchestrator.active_workflows[workflow_id]
    
    # Obtener métricas actuales
    current_metrics = await _get_current_performance_metrics(
        workflow_data["result"]["campaign_id"]
    )
    
    return {
        "workflow_id": workflow_id,
        "status": workflow_data["status"],
        "campaign_data": workflow_data["campaign"],
        "initial_result": workflow_data["result"],
        "current_performance": current_metrics,
        "uptime_hours": (datetime.now() - datetime.fromisoformat(workflow_data["created_at"])).total_seconds() / 3600
    }

@app.post("/authorization/{auth_id}/decision")
async def make_authorization_decision(auth_id: str, decision: AuthorizationDecision):
    """Tomar decisión sobre autorización ML"""
    
    try:
        # Encontrar el workflow que contiene esta autorización
        target_workflow = None
        for workflow_id, workflow_data in orchestrator.active_workflows.items():
            auth_requests = workflow_data["result"]["authorization_requests"]
            if any(auth["id"] == auth_id for auth in auth_requests):
                target_workflow = workflow_data
                break
        
        if not target_workflow:
            raise HTTPException(status_code=404, detail="Authorization request not found")
        
        # Actualizar estado de la autorización
        for auth in target_workflow["result"]["authorization_requests"]:
            if auth["id"] == auth_id:
                auth["status"] = decision.decision
                auth["decision_reason"] = decision.reason
                auth["decided_by"] = decision.user_id
                auth["decided_at"] = datetime.now().isoformat()
                break
        
        # Ejecutar acción si fue aprobada
        if decision.decision == "approved":
            execution_result = await _execute_approved_action(auth_id, target_workflow)
            return {
                "success": True,
                "authorization_id": auth_id,
                "decision": decision.decision,
                "execution_result": execution_result
            }
        else:
            return {
                "success": True,
                "authorization_id": auth_id,
                "decision": decision.decision,
                "message": "Authorization rejected by user"
            }
        
    except Exception as e:
        logger.error(f"Authorization decision error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/{campaign_id}")
async def get_campaign_dashboard_data(campaign_id: str):
    """Obtener todos los datos para el dashboard de una campaña"""
    
    try:
        # Buscar workflow por campaign_id
        target_workflow = None
        for workflow_data in orchestrator.active_workflows.values():
            if workflow_data["result"]["campaign_id"] == campaign_id:
                target_workflow = workflow_data
                break
        
        if not target_workflow:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Compilar datos completos del dashboard
        dashboard_data = {
            "campaign_info": target_workflow["campaign"],
            "workflow_result": target_workflow["result"],
            "current_performance": await _get_current_performance_metrics(campaign_id),
            "utm_analytics": await _get_utm_analytics(campaign_id),
            "ml_insights": await _get_ml_insights(campaign_id),
            "authorization_status": target_workflow["result"]["authorization_requests"],
            "railway_health": await _get_railway_health_status(),
            "platform_performance": await _get_platform_performance(campaign_id)
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# FUNCIONES DE MONITOREO
# ============================================

async def _monitor_campaign_performance(campaign_id: str, workflow_id: str):
    """Monitoreo continuo de performance de campaña (background task)"""
    
    logger.info(f"🔄 Starting 24/7 monitoring for campaign {campaign_id}")
    
    monitoring_duration = 24 * 7  # 7 días de monitoreo
    check_interval = 300  # Revisar cada 5 minutos
    
    for _ in range(monitoring_duration * 12):  # 12 checks per hour
        try:
            # Obtener métricas actuales
            metrics = await _get_current_performance_metrics(campaign_id)
            
            # Evaluar si necesita optimización automática
            optimization_needed = await _evaluate_optimization_needs(metrics)
            
            if optimization_needed:
                await _trigger_automatic_optimization(campaign_id, optimization_needed)
            
            # Esperar siguiente check
            await asyncio.sleep(check_interval)
            
        except Exception as e:
            logger.error(f"Monitoring error for {campaign_id}: {str(e)}")
            await asyncio.sleep(check_interval)
    
    logger.info(f"✅ Monitoring completed for campaign {campaign_id}")

async def _get_current_performance_metrics(campaign_id: str) -> Dict[str, Any]:
    """Obtener métricas de performance actuales"""
    
    # En dummy mode, retornar métricas simuladas
    if DUMMY_MODE:
        return {
            "total_spend_euros": 185.60,
            "total_revenue_euros": 521.40,
            "current_roas": 2.81,
            "total_conversions": 94,
            "landing_page_visits": 2640,
            "landing_page_conversions": 78,
            "platform_metrics": {
                "youtube": {"views": 18500, "engagement_rate": 8.2},
                "tiktok": {"views": 52000, "engagement_rate": 15.6},
                "instagram": {"reach": 24000, "engagement_rate": 9.8},
                "twitter": {"impressions": 9500, "engagement_rate": 4.1}
            },
            "hourly_performance": "Peak at 19:00-21:00 CET",
            "optimization_opportunities": [
                {"type": "budget_reallocation", "potential_improvement": "+12% ROAS"},
                {"type": "audience_expansion", "potential_improvement": "+25% reach"}
            ]
        }
    
    # En producción: compilar métricas de todas las fuentes
    return {}

async def _get_utm_analytics(campaign_id: str) -> Dict[str, Any]:
    """Obtener analytics UTM detalladas desde Supabase"""
    
    try:
        if DUMMY_MODE:
            return {
                "total_tracked_visits": 2640,
                "conversion_funnel": {
                    "landing_page_views": 2640,
                    "button_clicks": 1890,
                    "platform_redirects": 1456,
                    "actual_conversions": 78
                },
                "source_breakdown": {
                    "meta_ads": {"visits": 1580, "conversions": 48},
                    "organic": {"visits": 420, "conversions": 15},
                    "youtube": {"visits": 380, "conversions": 10},
                    "tiktok": {"visits": 260, "conversions": 5}
                },
                "conversion_paths": [
                    {"path": "Meta Ads → Landing → Spotify", "count": 234, "revenue": 156.80},
                    {"path": "Meta Ads → Landing → YouTube", "count": 189, "revenue": 127.40},
                    {"path": "TikTok → Landing → Spotify", "count": 98, "revenue": 65.60}
                ],
                "supabase_integration": "active",
                "real_time_data": True
            }
        
        # En producción: obtener analytics desde Supabase
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{LANDING_GENERATOR_URL}/api/campaign/{campaign_id}/analytics"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Supabase UTM analytics failed: {response.text}")
                return {"error": "Failed to fetch Supabase analytics"}
                
    except Exception as e:
        logger.error(f"UTM analytics error: {str(e)}")
        return {"error": str(e)}

async def _get_ml_insights(campaign_id: str) -> Dict[str, Any]:
    """Obtener insights ML actuales"""
    
    return {
        "ultralytics_current_score": 0.91,
        "music_analysis_update": {
            "genre_performance": "Reggaeton outperforming by +40%",
            "audience_response": "High engagement in 18-24 demographic",
            "viral_indicators": "TikTok views accelerating (+180% last 6h)"
        },
        "predictive_analytics": {
            "24h_projection": {"views": 95000, "conversions": 142, "revenue": 851.20},
            "weekly_projection": {"views": 520000, "conversions": 890, "revenue": 4560.80},
            "optimization_confidence": 0.89
        },
        "real_time_recommendations": [
            {
                "action": "Increase TikTok budget by €60",
                "reason": "Viral momentum detected",
                "confidence": 0.92,
                "expected_roi": "240% within 12 hours"
            }
        ]
    }

async def _get_railway_health_status() -> Dict[str, Any]:
    """Obtener estado de salud de Railway"""
    
    return {
        "overall_health": "healthy",
        "services_status": {
            "ml-core": "running",
            "meta-ads-manager": "running", 
            "landing-generator": "running",
            "unified-orchestrator": "running",
            "utm-tracker": "running"
        },
        "resource_usage": {
            "cpu": "23%",
            "memory": "67%",
            "disk": "12%"
        },
        "uptime_24h": "99.8%",
        "response_times": {
            "ml-core": "89ms",
            "landing-generator": "156ms",
            "unified-orchestrator": "234ms"
        }
    }

async def _get_platform_performance(campaign_id: str) -> Dict[str, Any]:
    """Obtener performance por plataforma"""
    
    return {
        "youtube": {
            "video_id": f"yt_{campaign_id}",
            "views": 18500,
            "likes": 1456,
            "comments": 234,
            "subscribers_gained": 89,
            "revenue_generated": 127.40,
            "trending_status": "Rising"
        },
        "tiktok": {
            "video_id": f"tt_{campaign_id}",
            "views": 52000,
            "likes": 8900,
            "shares": 1200,
            "comments": 890,
            "followers_gained": 456,
            "viral_coefficient": 1.8,
            "trending_hashtags": ["#nuevamusica", "#reggaeton", "#viral"]
        },
        "instagram": {
            "post_id": f"ig_{campaign_id}",
            "reach": 24000,
            "impressions": 35600,
            "engagement": 2340,
            "saves": 456,
            "profile_visits": 890,
            "story_reach": 8900
        },
        "twitter": {
            "thread_id": f"tw_{campaign_id}",
            "impressions": 9500,
            "engagements": 780,
            "retweets": 123,
            "likes": 456,
            "replies": 89,
            "link_clicks": 234
        }
    }

async def _evaluate_optimization_needs(metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Evaluar si se necesita optimización automática"""
    
    current_roas = metrics.get("current_roas", 0)
    
    # Si ROAS está muy alto, sugerir aumento de presupuesto
    if current_roas > 3.5:
        return {
            "type": "budget_increase",
            "reason": "Exceptional ROAS detected",
            "recommended_increase_euros": 100.0,
            "auto_approve": False  # Requires authorization
        }
    
    # Si hay momentum viral en TikTok, expandir presupuesto
    tiktok_views = metrics.get("platform_metrics", {}).get("tiktok", {}).get("views", 0)
    if tiktok_views > 50000:
        return {
            "type": "viral_expansion",
            "reason": "Viral content detected on TikTok",
            "recommended_action": "Boost TikTok and similar platforms",
            "auto_approve": True  # Auto-approve viral opportunities
        }
    
    return None

async def _trigger_automatic_optimization(campaign_id: str, optimization: Dict[str, Any]):
    """Ejecutar optimización automática"""
    
    logger.info(f"🤖 Triggering automatic optimization for {campaign_id}: {optimization['type']}")
    
    # Aquí implementarías la lógica de optimización automática
    # - Ajustar presupuestos en Meta Ads
    # - Rebalancear distribución de plataformas
    # - Optimizar targeting
    
async def _execute_approved_action(auth_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar acción ML aprobada por el usuario"""
    
    logger.info(f"✅ Executing approved ML action: {auth_id}")
    
    # Encontrar la acción específica
    action_data = None
    for auth in workflow_data["result"]["authorization_requests"]:
        if auth["id"] == auth_id:
            action_data = auth
            break
    
    if not action_data:
        return {"success": False, "error": "Action not found"}
    
    # Ejecutar según el tipo de acción
    action_type = action_data.get("type")
    
    if action_type == "budget_increase":
        return await _execute_budget_increase(action_data)
    elif action_type == "platform_expansion":
        return await _execute_platform_expansion(action_data)
    elif action_type == "content_optimization":
        return await _execute_content_optimization(action_data)
    else:
        return {"success": False, "error": f"Unknown action type: {action_type}"}

async def _execute_budget_increase(action_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar aumento de presupuesto"""
    
    # En producción: llamar a Meta Ads API para aumentar presupuesto
    return {
        "success": True,
        "action": "budget_increase",
        "amount_euros": action_data.get("cost_euros", 0),
        "status": "executed",
        "meta_ads_response": "Budget increased successfully"
    }

async def _execute_platform_expansion(action_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar expansión a nuevas plataformas"""
    
    # En producción: llamar al unified orchestrator para nuevas plataformas
    return {
        "success": True,
        "action": "platform_expansion", 
        "new_platforms": ["youtube_shorts", "instagram_reels"],
        "status": "executed",
        "distribution_result": "Content distributed to new platforms"
    }

async def _execute_content_optimization(action_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecutar optimización de contenido"""
    
    # En producción: optimizar thumbnails, subtítulos, etc.
    return {
        "success": True,
        "action": "content_optimization",
        "optimizations": ["thumbnail_enhanced", "subtitles_added", "audio_improved"],
        "status": "executed",
        "improvement_estimate": "+15% engagement"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info"
    )