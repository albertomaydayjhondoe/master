"""
🚀 Unified Cross-Platform Orchestrator
Maneja la distribución de contenido a todas las plataformas desde Meta Ads
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import httpx
import asyncio
import logging
from datetime import datetime
import json
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Unified Cross-Platform Orchestrator",
    description="Distribuye contenido a todas las plataformas desde Meta Ads triggers",
    version="1.0.0"
)

# URLs de servicios
YOUTUBE_UPLOADER_URL = os.getenv("YOUTUBE_UPLOADER_URL", "http://youtube-uploader:8001")
DEVICE_FARM_URL = os.getenv("DEVICE_FARM_URL", "http://device-farm:8002") 
GOLOGIN_AUTOMATION_URL = os.getenv("GOLOGIN_AUTOMATION_URL", "http://gologin-automation:8003")
ML_CORE_URL = os.getenv("ML_CORE_URL", "http://ml-core:8000")
DUMMY_MODE = os.getenv("DUMMY_MODE", "true").lower() == "true"

# ============================================
# MODELOS DE DATOS
# ============================================

class PlatformDistributionRequest(BaseModel):
    campaign_id: str
    campaign_name: str
    artist_name: str
    song_name: str
    platforms: List[str]  # ["youtube", "tiktok", "instagram", "twitter"]
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    description: Optional[str] = None
    hashtags: List[str] = []
    schedule_time: Optional[datetime] = None
    genre: Optional[str] = "pop"
    target_countries: List[str] = ["US"]

class PlatformUploadResponse(BaseModel):
    platform: str
    status: str
    platform_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = {}

class OrchestrationResult(BaseModel):
    campaign_id: str
    total_platforms: int
    successful_uploads: int
    failed_uploads: int
    platform_results: List[PlatformUploadResponse]
    orchestration_time: datetime
    estimated_reach: int
    ml_predictions: Dict[str, Any] = {}

# ============================================
# UPLOAD HANDLERS POR PLATAFORMA
# ============================================

class YouTubeHandler:
    """Handler para uploads a YouTube"""
    
    async def upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Subir video a YouTube"""
        
        try:
            if DUMMY_MODE:
                return self._dummy_upload(request)
            
            payload = {
                "title": f"{request.artist_name} - {request.song_name}",
                "description": self._generate_youtube_description(request),
                "tags": request.hashtags,
                "video_url": request.video_url,
                "privacy_status": "public",
                "category_id": "10"  # Music category
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{YOUTUBE_UPLOADER_URL}/upload",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return PlatformUploadResponse(
                        platform="youtube",
                        status="success",
                        platform_id=data.get("video_id"),
                        url=data.get("video_url"),
                        metrics={
                            "estimated_views_24h": 1500,
                            "expected_engagement_rate": 4.2
                        }
                    )
                else:
                    return PlatformUploadResponse(
                        platform="youtube",
                        status="failed",
                        error=f"Upload failed: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"YouTube upload error: {str(e)}")
            return PlatformUploadResponse(
                platform="youtube",
                status="failed",
                error=str(e)
            )
    
    def _dummy_upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Dummy upload para testing"""
        return PlatformUploadResponse(
            platform="youtube",
            status="success",
            platform_id="dummy_yt_video_123",
            url=f"https://youtube.com/watch?v=dummy_{request.campaign_id}",
            metrics={
                "estimated_views_24h": 2500,
                "expected_engagement_rate": 4.8
            }
        )
    
    def _generate_youtube_description(self, request: PlatformDistributionRequest) -> str:
        """Generar descripción optimizada para YouTube"""
        
        description = f"""
🎵 {request.artist_name} - {request.song_name}

{request.description or 'Official Music Video'}

Follow {request.artist_name}:
🎵 Spotify: [Link]
🎵 Apple Music: [Link]  
📱 Instagram: @{request.artist_name.lower().replace(' ', '')}
🐦 Twitter: @{request.artist_name.lower().replace(' ', '')}

#{' #'.join(request.hashtags)}

© 2024 {request.artist_name}. All rights reserved.
        """.strip()
        
        return description

class TikTokHandler:
    """Handler para uploads a TikTok"""
    
    async def upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Subir video a TikTok via device farm"""
        
        try:
            if DUMMY_MODE:
                return self._dummy_upload(request)
            
            payload = {
                "video_url": request.video_url,
                "description": self._generate_tiktok_description(request),
                "hashtags": request.hashtags,
                "privacy": "public",
                "allow_comments": True,
                "allow_duets": True
            }
            
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{DEVICE_FARM_URL}/tiktok/upload",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return PlatformUploadResponse(
                        platform="tiktok",
                        status="success",
                        platform_id=data.get("video_id"),
                        url=data.get("video_url"),
                        metrics={
                            "estimated_views_24h": 8500,
                            "expected_engagement_rate": 12.5
                        }
                    )
                else:
                    return PlatformUploadResponse(
                        platform="tiktok",
                        status="failed",
                        error=f"Upload failed: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"TikTok upload error: {str(e)}")
            return PlatformUploadResponse(
                platform="tiktok",
                status="failed",
                error=str(e)
            )
    
    def _dummy_upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Dummy upload para testing"""
        return PlatformUploadResponse(
            platform="tiktok",
            status="success",
            platform_id="dummy_tt_video_456",
            url=f"https://tiktok.com/@artist/video/dummy_{request.campaign_id}",
            metrics={
                "estimated_views_24h": 15000,
                "expected_engagement_rate": 18.2
            }
        )
    
    def _generate_tiktok_description(self, request: PlatformDistributionRequest) -> str:
        """Generar descripción optimizada para TikTok"""
        
        # TikTok descriptions are shorter
        description = f"{request.description or 'New music 🔥'} #{' #'.join(request.hashtags[:8])}"
        
        # Limit to 150 characters
        if len(description) > 150:
            description = description[:147] + "..."
        
        return description

class InstagramHandler:
    """Handler para posts en Instagram"""
    
    async def upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Crear post en Instagram via GoLogin"""
        
        try:
            if DUMMY_MODE:
                return self._dummy_upload(request)
            
            payload = {
                "type": "reel" if request.video_url else "post",
                "media_url": request.video_url or request.image_url,
                "caption": self._generate_instagram_caption(request),
                "hashtags": request.hashtags,
                "location": None
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{GOLOGIN_AUTOMATION_URL}/instagram/post",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return PlatformUploadResponse(
                        platform="instagram",
                        status="success",
                        platform_id=data.get("post_id"),
                        url=data.get("post_url"),
                        metrics={
                            "estimated_reach_24h": 12000,
                            "expected_engagement_rate": 8.5
                        }
                    )
                else:
                    return PlatformUploadResponse(
                        platform="instagram",
                        status="failed",
                        error=f"Upload failed: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"Instagram upload error: {str(e)}")
            return PlatformUploadResponse(
                platform="instagram",
                status="failed",
                error=str(e)
            )
    
    def _dummy_upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Dummy upload para testing"""
        return PlatformUploadResponse(
            platform="instagram",
            status="success", 
            platform_id="dummy_ig_post_789",
            url=f"https://instagram.com/p/dummy_{request.campaign_id}",
            metrics={
                "estimated_reach_24h": 18000,
                "expected_engagement_rate": 9.8
            }
        )
    
    def _generate_instagram_caption(self, request: PlatformDistributionRequest) -> str:
        """Generar caption optimizada para Instagram"""
        
        caption = f"""
🎵 {request.artist_name} - {request.song_name} 

{request.description or 'New music out now! 🔥'}

Stream everywhere 🎧
Link in bio ⬆️

#{' #'.join(request.hashtags)}
        """.strip()
        
        return caption

class TwitterHandler:
    """Handler para tweets"""
    
    async def upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Crear thread en Twitter via GoLogin"""
        
        try:
            if DUMMY_MODE:
                return self._dummy_upload(request)
            
            tweets = self._generate_twitter_thread(request)
            
            payload = {
                "thread": tweets,
                "media_url": request.image_url,  # Twitter doesn't support video in basic API
                "schedule_time": request.schedule_time
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{GOLOGIN_AUTOMATION_URL}/twitter/thread",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return PlatformUploadResponse(
                        platform="twitter",
                        status="success",
                        platform_id=data.get("thread_id"),
                        url=data.get("thread_url"),
                        metrics={
                            "estimated_impressions_24h": 5600,
                            "expected_engagement_rate": 3.2
                        }
                    )
                else:
                    return PlatformUploadResponse(
                        platform="twitter",
                        status="failed",
                        error=f"Upload failed: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"Twitter upload error: {str(e)}")
            return PlatformUploadResponse(
                platform="twitter",
                status="failed",
                error=str(e)
            )
    
    def _dummy_upload(self, request: PlatformDistributionRequest) -> PlatformUploadResponse:
        """Dummy upload para testing"""
        return PlatformUploadResponse(
            platform="twitter",
            status="success",
            platform_id="dummy_twitter_thread_101",
            url=f"https://twitter.com/artist/status/dummy_{request.campaign_id}",
            metrics={
                "estimated_impressions_24h": 8900,
                "expected_engagement_rate": 4.1
            }
        )
    
    def _generate_twitter_thread(self, request: PlatformDistributionRequest) -> List[str]:
        """Generar thread optimizado para Twitter"""
        
        tweets = [
            f"🎵 NEW MUSIC ALERT! 🎵\n\n{request.artist_name} - {request.song_name}\n\nOut now everywhere! 🔥\n\n🧵👇",
            f"{request.description or 'This track is everything! 🔥'}\n\n#{' #'.join(request.hashtags[:3])}",
            f"Stream now:\n🎧 Spotify\n🍎 Apple Music\n📺 YouTube\n\n#{' #'.join(request.hashtags[3:6])}"
        ]
        
        return tweets

# ============================================
# ORQUESTADOR PRINCIPAL
# ============================================

class UnifiedOrchestrator:
    """Orquestador principal para distribución cross-platform"""
    
    def __init__(self):
        self.handlers = {
            "youtube": YouTubeHandler(),
            "tiktok": TikTokHandler(), 
            "instagram": InstagramHandler(),
            "twitter": TwitterHandler()
        }
    
    async def distribute_to_platforms(
        self, 
        request: PlatformDistributionRequest
    ) -> OrchestrationResult:
        """Distribuir contenido a todas las plataformas seleccionadas"""
        
        start_time = datetime.now()
        
        # Ejecutar uploads en paralelo
        tasks = []
        for platform in request.platforms:
            if platform in self.handlers:
                handler = self.handlers[platform]
                task = asyncio.create_task(handler.upload(request))
                tasks.append((platform, task))
        
        # Esperar resultados
        results = []
        for platform, task in tasks:
            try:
                result = await task
                results.append(result)
                logger.info(f"Platform {platform}: {result.status}")
            except Exception as e:
                logger.error(f"Platform {platform} failed: {str(e)}")
                results.append(PlatformUploadResponse(
                    platform=platform,
                    status="failed",
                    error=str(e)
                ))
        
        # Calcular métricas
        successful = len([r for r in results if r.status == "success"])
        failed = len([r for r in results if r.status == "failed"])
        
        # Estimar reach total
        estimated_reach = sum([
            r.metrics.get("estimated_views_24h", 0) + 
            r.metrics.get("estimated_reach_24h", 0) + 
            r.metrics.get("estimated_impressions_24h", 0)
            for r in results
        ])
        
        # Obtener predicciones ML
        ml_predictions = await self._get_ml_predictions(request, results)
        
        return OrchestrationResult(
            campaign_id=request.campaign_id,
            total_platforms=len(request.platforms),
            successful_uploads=successful,
            failed_uploads=failed,
            platform_results=results,
            orchestration_time=start_time,
            estimated_reach=estimated_reach,
            ml_predictions=ml_predictions
        )
    
    async def _get_ml_predictions(
        self, 
        request: PlatformDistributionRequest,
        results: List[PlatformUploadResponse]
    ) -> Dict[str, Any]:
        """Obtener predicciones ML para la campaña"""
        
        try:
            if DUMMY_MODE:
                return {
                    "virality_score": 0.78,
                    "predicted_reach_24h": 45000,
                    "recommended_boost_budget": 75.0,
                    "peak_engagement_hour": 19
                }
            
            payload = {
                "campaign_data": {
                    "artist_name": request.artist_name,
                    "song_name": request.song_name,
                    "genre": request.genre,
                    "platforms": request.platforms,
                    "target_countries": request.target_countries
                },
                "platform_results": [r.dict() for r in results]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ML_CORE_URL}/meta-centric/predict-campaign-performance",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"ML prediction failed: {response.text}")
                    return {}
                    
        except Exception as e:
            logger.error(f"ML prediction error: {str(e)}")
            return {}

# Instanciar orquestador
orchestrator = UnifiedOrchestrator()

# ============================================
# ENDPOINTS API
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified-cross-platform-orchestrator",
        "version": "1.0.0",
        "dummy_mode": DUMMY_MODE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/distribute", response_model=OrchestrationResult)
async def distribute_to_platforms(
    request: PlatformDistributionRequest,
    background_tasks: BackgroundTasks
):
    """
    Distribuir contenido a múltiples plataformas desde Meta Ads trigger
    """
    
    try:
        logger.info(f"Starting distribution for campaign {request.campaign_id}")
        
        # Ejecutar distribución
        result = await orchestrator.distribute_to_platforms(request)
        
        # Programar tareas de seguimiento en background
        background_tasks.add_task(
            _track_campaign_performance, 
            request.campaign_id, 
            result.platform_results
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Distribution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/platforms")
async def get_supported_platforms():
    """Obtener plataformas soportadas"""
    return {
        "supported_platforms": list(orchestrator.handlers.keys()),
        "total_platforms": len(orchestrator.handlers),
        "dummy_mode": DUMMY_MODE
    }

@app.get("/campaign/{campaign_id}/status")
async def get_campaign_status(campaign_id: str):
    """Obtener estado de una campaña distribuida"""
    
    # En production, esto consultaría una base de datos
    # Por ahora retornamos datos mock
    
    return {
        "campaign_id": campaign_id,
        "status": "active",
        "platforms_active": 3,
        "total_reach_24h": 42500,
        "total_engagement": 2890,
        "cross_platform_roas": 2.8,
        "last_updated": datetime.now().isoformat()
    }

# ============================================
# FUNCIONES AUXILIARES
# ============================================

async def _track_campaign_performance(
    campaign_id: str, 
    platform_results: List[PlatformUploadResponse]
):
    """Hacer seguimiento del rendimiento de la campaña (background task)"""
    
    logger.info(f"Starting performance tracking for campaign {campaign_id}")
    
    # Esperar 1 hora para obtener métricas iniciales
    await asyncio.sleep(3600)
    
    # Aquí se implementaría la lógica de seguimiento real
    # Por ahora solo logeamos
    successful_platforms = [r.platform for r in platform_results if r.status == "success"]
    logger.info(f"Campaign {campaign_id} tracking: {len(successful_platforms)} active platforms")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=10000,
        log_level="info"
    )