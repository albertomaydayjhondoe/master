"""🎯 Meta Ads Centric Production System - Core del Viral System Stakas MVP

Sistema centralizado donde Meta Ads es el motor principal que orquesta:
- ML Core para insights de contenido viral
- Device Farm para automatización de dispositivos  
- GoLogin para automation de browsers
- n8n para orquestación de workflows
- Budget €500/month optimizado con IA

Todo gira en torno a las campañas de Meta Ads para maximizar el crecimiento viral.
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import requests
from pathlib import Path

# Imports del sistema
from ml_core.api.main import app as ml_api
from ml_core.models.factory import get_yolo_screenshot_detector, get_affinity_model
from device_farm.controllers.factory import get_device_manager
from gologin_automation.api.gologin_client import GoLoginClient
from monitoring.health.account_health import AccountHealthMonitor
from config.app_settings import get_env, is_dummy_mode

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetaCentricConfig:
    """Configuración centralizada del sistema Meta Ads."""
    # Meta Ads Core
    meta_access_token: str
    meta_ads_account_id: str  
    meta_app_id: str
    meta_pixel_id: str
    daily_budget: float = 16.67  # €500/month = €16.67/day
    
    # YouTube Target
    youtube_channel_id: str = "UCgohgqLVu1QPdfa64Vkrgeg"
    target_genre: str = "drill_rap_espanol"
    
    # ML Optimization
    ml_api_url: str = "http://localhost:8000"
    viral_threshold: float = 0.7
    engagement_target: int = 10000  # likes per video target
    
    # Device Farm
    device_count: int = 10
    automation_intensity: str = "medium"  # low, medium, high
    
    # GoLogin Automation  
    gologin_profiles: int = 30
    browser_automation: bool = True
    
    # Campaign Performance
    roi_target: float = 3.0  # 3x return on ad spend
    conversion_goal: str = "youtube_subscribers"
    geo_targeting: List[str] = None
    
    def __post_init__(self):
        if self.geo_targeting is None:
            self.geo_targeting = ["ES", "MX", "AR", "CO", "PE", "CL"]


class MetaAdsCentricSystem:
    """Sistema centralizado con Meta Ads como core del viral engine."""
    
    def __init__(self, config: MetaCentricConfig):
        self.config = config
        self.is_production = not is_dummy_mode()
        
        # Inicializar componentes
        self.ml_detector = None
        self.affinity_model = None
        self.device_manager = None
        self.gologin_client = None
        self.health_monitor = None
        
        # Meta Ads API client
        self.meta_base_url = "https://graph.facebook.com/v18.0"
        self.session = requests.Session()
        
        # State tracking
        self.active_campaigns = {}
        self.performance_data = {}
        self.daily_spend = 0.0
        
        logger.info(f"🚀 Meta Ads Centric System initialized - Production: {self.is_production}")
    
    async def initialize_components(self):
        """Inicializar todos los componentes del sistema."""
        try:
            logger.info("🔧 Initializing Meta Ads Centric System components...")
            
            # 1. ML Core
            if self.is_production:
                self.ml_detector = get_yolo_screenshot_detector(
                    model_path="data/models/production/yolo_tiktok_v8.pt"
                )
                self.affinity_model = get_affinity_model()
                logger.info("✅ ML Core initialized in PRODUCTION mode")
            else:
                logger.info("⚠️ ML Core in dummy mode")
            
            # 2. Device Farm
            self.device_manager = get_device_manager()
            logger.info(f"✅ Device Manager initialized - {self.config.device_count} devices")
            
            # 3. GoLogin Client
            if self.is_production:
                self.gologin_client = GoLoginClient()
                await self.gologin_client.initialize_profiles(self.config.gologin_profiles)
                logger.info(f"✅ GoLogin initialized - {self.config.gologin_profiles} profiles")
            
            # 4. Health Monitor
            self.health_monitor = AccountHealthMonitor()
            logger.info("✅ Health Monitor initialized")
            
            # 5. Verify Meta Ads API connection
            await self._verify_meta_connection()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {str(e)}")
            return False
    
    async def _verify_meta_connection(self):
        """Verificar conexión con Meta Ads API."""
        try:
            url = f"{self.meta_base_url}/me"
            params = {"access_token": self.config.meta_access_token}
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ Meta API connected - User: {user_data.get('name', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Meta API connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Meta API verification error: {str(e)}")
            return False
    
    async def create_viral_campaign(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear campaña Meta Ads optimizada para viralidad basada en ML insights.
        
        Args:
            video_data: Datos del video con URL, metadatos, screenshots
            
        Returns:
            Dict con información de la campaña creada
        """
        try:
            logger.info(f"🎯 Creating viral campaign for video: {video_data.get('title', 'Unknown')}")
            
            # 1. Análisis ML del contenido
            ml_insights = await self._analyze_viral_potential(video_data)
            
            # 2. Calcular budget optimal basado en insights
            optimal_budget = self._calculate_optimal_budget(ml_insights)
            
            # 3. Generar targeting inteligente
            targeting = await self._generate_smart_targeting(ml_insights, video_data)
            
            # 4. Crear campaña en Meta Ads
            campaign_data = {
                "name": f"Viral_Stakas_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "objective": "LINK_CLICKS",
                "status": "ACTIVE",
                "daily_budget": int(optimal_budget * 100),  # En centavos
                "bid_strategy": "LOWEST_COST_WITH_BID_CAP"
            }
            
            campaign = await self._create_meta_campaign(campaign_data, targeting, video_data)
            
            # 5. Activar device farm para engagement orgánico
            if self.device_manager:
                await self.device_manager.start_viral_boost(video_data['url'], ml_insights)
            
            # 6. Iniciar automation GoLogin
            if self.gologin_client:
                await self.gologin_client.boost_video_engagement(video_data['url'])
            
            logger.info(f"🚀 Viral campaign created: {campaign['id']}")
            return campaign
            
        except Exception as e:
            logger.error(f"❌ Campaign creation failed: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def _analyze_viral_potential(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar potencial viral usando ML Core."""
        insights = {
            "viral_score": 0.5,  # Default
            "engagement_prediction": {"likes": 1000, "comments": 50},
            "optimal_posting_time": "20:00",
            "target_demographics": ["18-24", "25-34"],
            "content_category": "drill_rap",
            "trending_elements": []
        }
        
        try:
            if self.ml_detector and 'screenshot_path' in video_data:
                # Análisis de screenshot
                detection_result = self.ml_detector.detect(
                    open(video_data['screenshot_path'], 'rb').read()
                )
                
                # Calcular score basado en detecciones
                ui_elements = len([d for d in detection_result if d['confidence'] > 0.7])
                insights["viral_score"] = min(0.95, 0.3 + (ui_elements * 0.1))
                
                # Predicción de engagement mejorada
                base_likes = 1000
                multiplier = 1 + (insights["viral_score"] * 2)
                insights["engagement_prediction"] = {
                    "likes": int(base_likes * multiplier),
                    "comments": int(base_likes * multiplier * 0.05),
                    "shares": int(base_likes * multiplier * 0.02)
                }
            
            # Análisis de afinidad de audiencia
            if self.affinity_model:
                affinity_data = await self.affinity_model.calculate_affinity({
                    "genre": self.config.target_genre,
                    "content": video_data.get('title', ''),
                    "channel": self.config.youtube_channel_id
                })
                insights.update(affinity_data)
            
            logger.info(f"🧠 ML Analysis complete - Viral score: {insights['viral_score']:.2f}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ ML analysis failed: {str(e)}")
            return insights
    
    def _calculate_optimal_budget(self, ml_insights: Dict[str, Any]) -> float:
        """Calcular budget óptimo basado en insights ML."""
        base_budget = self.config.daily_budget
        viral_score = ml_insights.get("viral_score", 0.5)
        
        # Aumentar budget para contenido con alto potencial viral
        if viral_score > 0.8:
            multiplier = 1.5  # +50% para contenido muy viral
        elif viral_score > 0.6:
            multiplier = 1.25  # +25% para contenido viral
        else:
            multiplier = 0.8   # -20% para contenido normal
        
        optimal_budget = base_budget * multiplier
        
        # Caps de seguridad
        max_budget = base_budget * 2  # Máximo 2x el budget base
        optimal_budget = min(optimal_budget, max_budget)
        
        logger.info(f"💰 Optimal budget calculated: €{optimal_budget:.2f} (viral_score: {viral_score:.2f})")
        return optimal_budget
    
    async def _generate_smart_targeting(self, ml_insights: Dict[str, Any], video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar targeting inteligente basado en ML insights."""
        targeting = {
            "geo_locations": {"countries": self.config.geo_targeting},
            "age_min": 18,
            "age_max": 35,
            "genders": [1, 2],  # All genders
            "interests": [],
            "behaviors": [],
            "custom_audiences": []
        }
        
        # Ajustar targeting basado en insights ML
        demographics = ml_insights.get("target_demographics", ["18-24", "25-34"])
        if "18-24" in demographics:
            targeting["age_min"] = 18
            targeting["age_max"] = 24
        elif "25-34" in demographics:
            targeting["age_min"] = 25 
            targeting["age_max"] = 34
        
        # Intereses específicos para drill/rap español
        targeting["interests"] = [
            {"id": "6003139266461", "name": "Hip hop music"},
            {"id": "6003329194949", "name": "Rap music"}, 
            {"id": "6003348202933", "name": "Spanish language"},
            {"id": "6004854404172", "name": "Music video"},
            {"id": "6003195198708", "name": "YouTube"}
        ]
        
        # Comportamientos relevantes
        targeting["behaviors"] = [
            {"id": "6002714895372", "name": "Music listeners"},
            {"id": "6007828099773", "name": "YouTube users"}
        ]
        
        logger.info("🎯 Smart targeting generated for drill/rap español audience")
        return targeting
    
    async def _create_meta_campaign(self, campaign_data: Dict, targeting: Dict, video_data: Dict) -> Dict[str, Any]:
        """Crear campaña real en Meta Ads API."""
        try:
            if not self.is_production:
                # Simulación para desarrollo
                return {
                    "id": f"dummy_campaign_{datetime.now().timestamp()}",
                    "name": campaign_data["name"],
                    "status": "SIMULATED",
                    "daily_budget": campaign_data["daily_budget"],
                    "success": True
                }
            
            # Crear campaña real
            url = f"{self.meta_base_url}/act_{self.config.meta_ads_account_id}/campaigns"
            params = {"access_token": self.config.meta_access_token}
            
            response = self.session.post(url, params=params, json=campaign_data)
            
            if response.status_code == 200:
                campaign_result = response.json()
                campaign_id = campaign_result["id"]
                
                # Crear Ad Set con targeting
                adset_data = {
                    "name": f"{campaign_data['name']}_AdSet",
                    "campaign_id": campaign_id,
                    "daily_budget": campaign_data["daily_budget"],
                    "optimization_goal": "LINK_CLICKS",
                    "billing_event": "IMPRESSIONS",
                    "targeting": targeting,
                    "status": "ACTIVE"
                }
                
                adset_result = await self._create_adset(adset_data)
                
                # Crear Creative/Ad
                ad_data = {
                    "name": f"{campaign_data['name']}_Ad",
                    "adset_id": adset_result["id"],
                    "creative": {
                        "object_story_spec": {
                            "page_id": self.config.meta_app_id,
                            "link_data": {
                                "link": video_data.get('url', ''),
                                "message": video_data.get('title', ''),
                                "call_to_action": {"type": "LEARN_MORE"}
                            }
                        }
                    },
                    "status": "ACTIVE"
                }
                
                ad_result = await self._create_ad(ad_data)
                
                # Guardar campaña activa
                self.active_campaigns[campaign_id] = {
                    "campaign": campaign_result,
                    "adset": adset_result,
                    "ad": ad_result,
                    "video_data": video_data,
                    "created_at": datetime.now(),
                    "budget": campaign_data["daily_budget"] / 100
                }
                
                return campaign_result
                
            else:
                logger.error(f"❌ Meta campaign creation failed: {response.status_code} - {response.text}")
                return {"error": response.text, "success": False}
                
        except Exception as e:
            logger.error(f"❌ Meta campaign creation error: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def _create_adset(self, adset_data: Dict) -> Dict[str, Any]:
        """Crear Ad Set en Meta Ads."""
        url = f"{self.meta_base_url}/act_{self.config.meta_ads_account_id}/adsets"
        params = {"access_token": self.config.meta_access_token}
        
        response = self.session.post(url, params=params, json=adset_data)
        return response.json()
    
    async def _create_ad(self, ad_data: Dict) -> Dict[str, Any]:
        """Crear Ad en Meta Ads."""
        url = f"{self.meta_base_url}/act_{self.config.meta_ads_account_id}/ads"
        params = {"access_token": self.config.meta_access_token}
        
        response = self.session.post(url, params=params, json=ad_data)
        return response.json()
    
    async def monitor_and_optimize(self):
        """Monitoreo continuo y optimización automática de campañas."""
        logger.info("📊 Starting campaign monitoring and optimization...")
        
        while True:
            try:
                # Revisar performance de campañas activas
                for campaign_id, campaign_info in self.active_campaigns.items():
                    performance = await self._get_campaign_performance(campaign_id)
                    
                    if performance:
                        # Análisis de ROI
                        roi = self._calculate_roi(performance)
                        
                        if roi < self.config.roi_target:
                            # Optimizar campaña con bajo rendimiento
                            await self._optimize_campaign(campaign_id, performance)
                        
                        # Actualizar datos de performance
                        self.performance_data[campaign_id] = performance
                
                # Health check del sistema
                if self.health_monitor:
                    health_status = await self.health_monitor.check_system_health()
                    logger.info(f"💊 System health: {health_status}")
                
                # Esperar antes del siguiente ciclo
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _get_campaign_performance(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Obtener métricas de performance de campaña."""
        try:
            if not self.is_production:
                # Datos simulados para desarrollo
                return {
                    "impressions": 10000 + int(datetime.now().timestamp()) % 5000,
                    "clicks": 150 + int(datetime.now().timestamp()) % 100,
                    "spend": 15.50,
                    "ctr": 1.5,
                    "cpc": 0.10
                }
            
            url = f"{self.meta_base_url}/{campaign_id}/insights"
            params = {
                "access_token": self.config.meta_access_token,
                "fields": "impressions,clicks,spend,ctr,cpc,actions"
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    return data["data"][0]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Performance fetch error: {str(e)}")
            return None
    
    def _calculate_roi(self, performance: Dict[str, Any]) -> float:
        """Calcular ROI de la campaña."""
        spend = float(performance.get("spend", 0))
        if spend == 0:
            return 0.0
        
        # Valor estimado por conversión (suscriptor de YouTube)
        conversion_value = 0.50  # €0.50 por suscriptor
        conversions = performance.get("actions", [])
        
        # Buscar conversiones relevantes
        total_value = 0.0
        for action in conversions:
            if action.get("action_type") in ["link_click", "post_engagement"]:
                total_value += int(action.get("value", 0)) * conversion_value
        
        roi = total_value / spend if spend > 0 else 0.0
        return roi
    
    async def _optimize_campaign(self, campaign_id: str, performance: Dict[str, Any]):
        """Optimizar campaña con bajo rendimiento."""
        logger.info(f"🔧 Optimizing campaign {campaign_id}")
        
        campaign_info = self.active_campaigns.get(campaign_id)
        if not campaign_info:
            return
        
        # Estrategias de optimización
        ctr = float(performance.get("ctr", 0))
        cpc = float(performance.get("cpc", 0))
        
        optimizations = []
        
        if ctr < 1.0:  # CTR bajo
            optimizations.append("improve_creative")
            optimizations.append("refine_targeting")
        
        if cpc > 0.15:  # CPC alto
            optimizations.append("reduce_bid")
            optimizations.append("expand_audience")
        
        # Aplicar optimizaciones
        for optimization in optimizations:
            await self._apply_optimization(campaign_id, optimization)
    
    async def _apply_optimization(self, campaign_id: str, optimization_type: str):
        """Aplicar optimización específica."""
        try:
            if optimization_type == "reduce_bid":
                # Reducir bid en 10%
                new_bid = 0.90  # 90% del bid anterior
                logger.info(f"🎯 Reducing bid for campaign {campaign_id} to {new_bid}")
            
            elif optimization_type == "improve_creative":
                # Activar device farm para engagement orgánico
                if self.device_manager:
                    campaign_info = self.active_campaigns[campaign_id]
                    video_url = campaign_info["video_data"].get("url")
                    if video_url:
                        await self.device_manager.boost_engagement(video_url)
                        logger.info(f"🤖 Device farm activated for campaign {campaign_id}")
            
            elif optimization_type == "refine_targeting":
                # Ajustar targeting basado en performance
                logger.info(f"🎯 Refining targeting for campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"❌ Optimization failed: {str(e)}")
    
    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generar reporte diario de performance."""
        total_spend = sum(
            self.performance_data.get(cid, {}).get("spend", 0) 
            for cid in self.active_campaigns.keys()
        )
        
        total_clicks = sum(
            int(self.performance_data.get(cid, {}).get("clicks", 0))
            for cid in self.active_campaigns.keys()
        )
        
        avg_roi = sum(
            self._calculate_roi(self.performance_data.get(cid, {}))
            for cid in self.active_campaigns.keys()
        ) / len(self.active_campaigns) if self.active_campaigns else 0
        
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_campaigns": len(self.active_campaigns),
            "total_spend": f"€{total_spend:.2f}",
            "total_clicks": total_clicks,
            "average_roi": f"{avg_roi:.2f}x",
            "budget_utilization": f"{(total_spend / self.config.daily_budget) * 100:.1f}%",
            "system_status": "ACTIVE" if self.is_production else "DEVELOPMENT",
            "campaigns": list(self.active_campaigns.keys())
        }
        
        logger.info(f"📊 Daily report: {json.dumps(report, indent=2)}")
        return report


# Sistema principal
async def main():
    """Función principal del sistema Meta Ads Centric."""
    # Configuración desde variables de entorno
    config = MetaCentricConfig(
        meta_access_token=get_env("META_ACCESS_TOKEN"),
        meta_ads_account_id=get_env("META_ADS_ACCOUNT_ID"),
        meta_app_id=get_env("META_APP_ID", "dummy_app_id"),
        meta_pixel_id=get_env("META_PIXEL_ID", "dummy_pixel_id"),
        youtube_channel_id=get_env("YOUTUBE_CHANNEL_ID", "UCgohgqLVu1QPdfa64Vkrgeg")
    )
    
    # Inicializar sistema
    system = MetaAdsCentricSystem(config)
    
    # Inicializar componentes
    if await system.initialize_components():
        logger.info("🎯 Meta Ads Centric System fully initialized!")
        
        # Ejemplo: crear campaña para un video
        sample_video = {
            "title": "Stakas - Nuevo Drill Español 2025 🔥",
            "url": "https://youtube.com/watch?v=example",
            "screenshot_path": "data/screenshots/sample_tiktok.jpg",
            "genre": "drill_rap_espanol",
            "duration": 180
        }
        
        # Crear campaña viral
        campaign = await system.create_viral_campaign(sample_video)
        if campaign.get("success") != False:
            logger.info(f"🚀 Sample campaign created: {campaign}")
            
            # Iniciar monitoreo
            await system.monitor_and_optimize()
    else:
        logger.error("❌ System initialization failed")


if __name__ == "__main__":
    asyncio.run(main())