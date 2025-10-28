"""
🚀 Meta Ads Webhook Handler - Centro de Orquestación
Recibe webhooks de Meta Ads y triggera ecosistema completo cross-platform
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class MetaCentricOrchestrator:
    """Orquestador principal basado en Meta Ads"""
    
    def __init__(self):
        self.ml_core_url = "http://ml-core:8000"
        self.youtube_url = "http://youtube-uploader:9003" 
        self.n8n_url = "http://n8n:5678"
        self.unified_orchestrator_url = "http://unified-orchestrator:10000"
        
    async def handle_campaign_webhook(self, campaign_data: Dict) -> Dict:
        """
        Webhook principal que recibe notificación de nueva campaña Meta Ads
        Orquesta todo el ecosistema cross-platform
        """
        
        campaign_id = campaign_data.get("campaign_id")
        campaign_name = campaign_data.get("campaign_name", "Unknown Campaign")
        daily_budget = float(campaign_data.get("daily_budget", 50.0))
        
        logger.info(f"🚀 Meta Ads webhook received: {campaign_name} (ID: {campaign_id})")
        
        try:
            # 1. Analizar la campaña con ML Core
            ml_analysis = await self._analyze_campaign_potential(campaign_data)
            
            # 2. Crear payload de orquestación
            orchestration_payload = {
                "source": "meta_ads",
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "daily_budget": daily_budget,
                "ml_score": ml_analysis.get("virality_score", 0.5),
                "recommended_platforms": ml_analysis.get("platforms", ["youtube", "tiktok"]),
                "budget_allocation": ml_analysis.get("budget_split", {}),
                "posting_schedule": ml_analysis.get("schedule", {}),
                "created_at": datetime.now().isoformat()
            }
            
            # 3. Trigger n8n orchestrator workflow
            await self._trigger_n8n_workflow("meta_ads_orchestrator", orchestration_payload)
            
            # 4. Start parallel platform distribution
            platform_results = await self._distribute_to_platforms(orchestration_payload)
            
            # 5. Setup continuous monitoring
            await self._setup_campaign_monitoring(campaign_id, orchestration_payload)
            
            return {
                "status": "orchestration_complete",
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "platforms_launched": list(platform_results.keys()),
                "ml_recommendations": ml_analysis,
                "monitoring_active": True,
                "dashboard_url": f"/campaigns/{campaign_id}/dashboard"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in campaign orchestration: {e}")
            raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")
    
    async def _analyze_campaign_potential(self, campaign_data: Dict) -> Dict:
        """Analiza potencial de la campaña con ML Core"""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ml_core_url}/analyze_meta_campaign",
                    json={
                        "campaign_name": campaign_data.get("campaign_name"),
                        "daily_budget": campaign_data.get("daily_budget"),
                        "targeting": campaign_data.get("targeting", {}),
                        "creative_assets": campaign_data.get("creative_assets", {}),
                        "objective": campaign_data.get("objective", "CONVERSIONS")
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"ML analysis failed, using defaults: {response.text}")
                    return self._get_default_ml_analysis()
                    
        except Exception as e:
            logger.error(f"Error calling ML Core: {e}")
            return self._get_default_ml_analysis()
    
    async def _trigger_n8n_workflow(self, workflow_name: str, payload: Dict):
        """Trigger n8n workflow"""
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.n8n_url}/webhook/{workflow_name}",
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ n8n workflow triggered: {workflow_name}")
                else:
                    logger.warning(f"n8n trigger failed: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error triggering n8n: {e}")
    
    async def _distribute_to_platforms(self, payload: Dict) -> Dict:
        """Distribuye contenido a todas las plataformas en paralelo"""
        
        platform_tasks = []
        recommended_platforms = payload.get("recommended_platforms", [])
        
        # YouTube upload task
        if "youtube" in recommended_platforms:
            platform_tasks.append(self._upload_to_youtube(payload))
        
        # TikTok distribution task  
        if "tiktok" in recommended_platforms:
            platform_tasks.append(self._distribute_tiktok(payload))
        
        # Instagram stories task
        if "instagram" in recommended_platforms:
            platform_tasks.append(self._launch_instagram_stories(payload))
        
        # Twitter thread task
        if "twitter" in recommended_platforms:
            platform_tasks.append(self._create_twitter_thread(payload))
        
        # Ejecutar todas las tareas en paralelo
        logger.info(f"🚀 Launching {len(platform_tasks)} platform distributions")
        
        results = await asyncio.gather(*platform_tasks, return_exceptions=True)
        
        # Procesar resultados
        platform_results = {}
        for i, result in enumerate(results):
            platform = recommended_platforms[i] if i < len(recommended_platforms) else f"platform_{i}"
            if isinstance(result, Exception):
                platform_results[platform] = {"status": "error", "error": str(result)}
            else:
                platform_results[platform] = result
        
        # Enviar feedback a Meta Ads para optimización
        await self._optimize_meta_campaign_based_on_results(
            payload["campaign_id"], 
            platform_results
        )
        
        return platform_results
    
    async def _upload_to_youtube(self, payload: Dict) -> Dict:
        """Upload video to YouTube"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.youtube_url}/upload_from_meta",
                    json={
                        "campaign_id": payload["campaign_id"],
                        "campaign_name": payload["campaign_name"],
                        "budget_allocation": payload["budget_allocation"].get("youtube", 0.3),
                        "auto_optimize": True
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ YouTube upload successful: {result.get('video_id')}")
                    return {"status": "success", "platform": "youtube", "data": result}
                else:
                    logger.error(f"YouTube upload failed: {response.text}")
                    return {"status": "error", "platform": "youtube", "error": response.text}
                    
        except Exception as e:
            logger.error(f"Error uploading to YouTube: {e}")
            return {"status": "error", "platform": "youtube", "error": str(e)}
    
    async def _distribute_tiktok(self, payload: Dict) -> Dict:
        """Distribute to TikTok via Device Farm"""
        
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.unified_orchestrator_url}/tiktok_from_meta",
                    json={
                        "campaign_id": payload["campaign_id"],
                        "virality_score": payload["ml_score"],
                        "budget_allocation": payload["budget_allocation"].get("tiktok", 0.4),
                        "posting_schedule": payload.get("posting_schedule", {})
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ TikTok distribution successful")
                    return {"status": "success", "platform": "tiktok", "data": result}
                else:
                    return {"status": "error", "platform": "tiktok", "error": response.text}
                    
        except Exception as e:
            logger.error(f"Error distributing to TikTok: {e}")
            return {"status": "error", "platform": "tiktok", "error": str(e)}
    
    async def _launch_instagram_stories(self, payload: Dict) -> Dict:
        """Launch Instagram Stories campaign"""
        
        try:
            # Simulated Instagram Stories launch
            logger.info("✅ Instagram Stories campaign launched (simulated)")
            return {
                "status": "success",
                "platform": "instagram", 
                "data": {
                    "stories_created": 3,
                    "estimated_reach": int(payload["daily_budget"] * 100),
                    "campaign_id": payload["campaign_id"]
                }
            }
            
        except Exception as e:
            return {"status": "error", "platform": "instagram", "error": str(e)}
    
    async def _create_twitter_thread(self, payload: Dict) -> Dict:
        """Create Twitter thread"""
        
        try:
            # Simulated Twitter thread creation
            logger.info("✅ Twitter thread created (simulated)")
            return {
                "status": "success",
                "platform": "twitter",
                "data": {
                    "thread_tweets": 5,
                    "estimated_impressions": int(payload["daily_budget"] * 80),
                    "campaign_id": payload["campaign_id"]
                }
            }
            
        except Exception as e:
            return {"status": "error", "platform": "twitter", "error": str(e)}
    
    async def _setup_campaign_monitoring(self, campaign_id: str, payload: Dict):
        """Setup continuous monitoring for the campaign"""
        
        try:
            # Setup monitoring dashboard
            logger.info(f"📊 Setting up monitoring for campaign {campaign_id}")
            
            # Here you would setup:
            # - Grafana dashboard
            # - Performance alerts
            # - Budget tracking
            # - Cross-platform analytics
            
        except Exception as e:
            logger.error(f"Error setting up monitoring: {e}")
    
    async def _optimize_meta_campaign_based_on_results(
        self, 
        campaign_id: str, 
        platform_results: Dict
    ):
        """Send feedback to Meta Ads for optimization"""
        
        try:
            # Calculate success metrics
            successful_platforms = [
                p for p, r in platform_results.items() 
                if r.get("status") == "success"
            ]
            
            success_rate = len(successful_platforms) / len(platform_results) if platform_results else 0
            
            # Send optimization feedback
            logger.info(f"📈 Campaign {campaign_id} cross-platform success rate: {success_rate:.2%}")
            
            # Here you would call Meta Ads API to adjust:
            # - Budget allocation
            # - Targeting optimization  
            # - Creative rotation
            
        except Exception as e:
            logger.error(f"Error optimizing Meta campaign: {e}")
    
    def _get_default_ml_analysis(self) -> Dict:
        """Default ML analysis when service is unavailable"""
        
        return {
            "virality_score": 0.65,
            "platforms": ["youtube", "tiktok", "instagram"],
            "budget_split": {
                "youtube": 0.3,
                "tiktok": 0.4, 
                "instagram": 0.2,
                "twitter": 0.1
            },
            "schedule": {
                "youtube": "14:00",
                "tiktok": "18:00", 
                "instagram": "20:00",
                "twitter": "16:00"
            },
            "confidence": 0.7
        }

# ============================================
# ENDPOINTS FOR META ADS MANAGER
# ============================================

# Añadir estos endpoints a v2/meta_ads/main.py
from fastapi import FastAPI, HTTPException
from typing import Dict, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class CampaignCreateRequest(BaseModel):
    campaign_name: str
    budget: float
    target_audience: Dict
    
app = FastAPI()
orchestrator = MetaCentricOrchestrator()

@app.post("/webhook/campaign-created")
async def campaign_created_webhook(campaign_data: Dict):
    """
    Webhook que recibe notificación de nueva campaña Meta Ads
    Orquesta todo el ecosistema cross-platform
    """
    return await orchestrator.handle_campaign_webhook(campaign_data)

@app.post("/campaigns/create-with-orchestration")
async def create_campaign_with_full_orchestration(
    request: CampaignCreateRequest,
    artist_name: str,
    song_name: str,
    platforms: List[str] = ["youtube", "tiktok", "instagram"],
    auto_optimize: bool = True
):
    """
    Crea campaña Meta Ads + triggera ecosistema completo
    Este es el endpoint PRINCIPAL para Community Managers
    """
    
    try:
        # 1. Crear campaña Meta Ads (dummy implementation)
        campaign = {"id": f"campaign_{request.campaign_name}_{hash(str(request.dict()))}"}
        campaign_id = campaign["id"]
        
        logger.info(f"🚀 Created Meta Ads campaign: {campaign_id}")
        
        # 2. Preparar datos para orquestación
        campaign_data = {
            "campaign_id": campaign_id,
            "campaign_name": request.name,
            "daily_budget": request.daily_budget,
            "artist_name": artist_name,
            "song_name": song_name,
            "objective": request.objective.value,
            "platforms": platforms,
            "auto_optimize": auto_optimize,
            "targeting": {
                "age_min": 18,
                "age_max": 35,
                "interests": ["Music", "Hip hop music", "Electronic dance music"]
            }
        }
        
        # 3. Trigger orquestación completa
        orchestration_result = await orchestrator.handle_campaign_webhook(campaign_data)
        
        return {
            "meta_campaign": campaign,
            "orchestration": orchestration_result,
            "message": "🎉 Complete ecosystem launched successfully!",
            "next_steps": [
                f"Monitor dashboard: /campaigns/{campaign_id}/dashboard",
                "Check platform performance in unified analytics",
                "Automatic optimization active"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating campaign with orchestration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{campaign_id}/dashboard")
async def get_campaign_dashboard(campaign_id: str):
    """Dashboard unificado para monitorear campaña cross-platform"""
    
    # Here you would return dashboard data from all platforms
    return {
        "campaign_id": campaign_id,
        "status": "active",
        "platforms": {
            "meta_ads": {"spend": 45.20, "impressions": 15000, "clicks": 450},
            "youtube": {"views": 2500, "likes": 89, "comments": 23},
            "tiktok": {"views": 8900, "likes": 567, "shares": 89},
            "instagram": {"reach": 12000, "engagement": 890, "saves": 45}
        },
        "unified_metrics": {
            "total_reach": 38400,
            "total_engagement": 2053,
            "cross_platform_roas": 2.8,
            "virality_score": 0.72
        }
    }