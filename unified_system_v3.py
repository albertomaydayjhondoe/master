"""
🚀 UNIFIED SYSTEM V3 - Community Manager de Discográfica
Sistema completo para lanzamiento viral de video musical

Integra:
- Docker v1: ML Core + Device Farm + GoLogin + Viral TikTok/IG
- Docker v2: Meta Ads + Facebook Pixel + Landing Pages + YouTube
- Workflow: Lanzamiento coordinado en TODAS las redes sociales

Community Manager Workflow:
1. Upload video a TODAS las plataformas simultáneamente
2. Meta Ads campaign para amplificar alcance
3. Device Farm + GoLogin para engagement orgánico
4. ML optimization para maximizar viralidad
5. Analytics unificado de TODAS las plataformas
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Imports del sistema v1 (existente)
from ml_core.platform_toggle import InstagramController, TwitterController
from device_farm.controllers.device_manager import DeviceManager
from social_extensions.base import CrossPlatformManager
from social_extensions.meta.meta_automator import MetaPixelManager
from social_extensions.tiktok.tiktok_cross_platform_system import CrossPlatformCampaignManager
from telegram_automation.youtube_executor.youtube_executor import YouTubeExecutorService
from awakener import ServiceOrchestrator

# Imports del sistema v2 (nuevo)
sys.path.insert(0, str(Path(__file__).parent / "v2"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# UNIFIED ORCHESTRATOR V3
# ============================================

class UnifiedCommunityManagerSystem:
    """
    Sistema unificado para Community Manager de discográfica
    
    Coordina TODAS las funcionalidades:
    - Publicación multi-plataforma (TikTok, IG, YouTube, Twitter, etc.)
    - Meta Ads campaigns
    - Engagement automation (Device Farm + GoLogin)
    - ML optimization
    - Analytics unificado
    """
    
    def __init__(self, dummy_mode: bool = True):
        self.dummy_mode = dummy_mode
        logger.info(f"Initializing Unified System v3 (DUMMY_MODE={dummy_mode})")
        
        # ========================================
        # ML CORE (from v1)
        # ========================================
        self.ml_core_url = "http://localhost:8000" if not dummy_mode else None
        self.ml_client = None  # Will be initialized when needed
        
        # ML Capabilities:
        # - Screenshot analysis (YOLOv8)
        # - Anomaly detection (shadowban)
        # - Posting time prediction
        # - Content optimization
        # - Affinity calculation
        # - Viral probability prediction
        
        # ========================================
        # Components from v1 (Organic Viral)
        # ========================================
        try:
            self.cross_platform_manager = CrossPlatformManager()
        except:
            self.cross_platform_manager = None
            
        self.device_manager = None  # Will be initialized when needed
        self.instagram_controller = None
        self.twitter_controller = None
        self.youtube_service = None
        
        # ========================================
        # Components from v2 (Paid Acquisition)
        # ========================================
        self.meta_ads_api_url = "http://localhost:9000" if not dummy_mode else None
        self.pixel_tracker_url = "http://localhost:9001" if not dummy_mode else None
        self.youtube_uploader_url = "http://localhost:9003" if not dummy_mode else None
        
        # ========================================
        # State
        # ========================================
        self.current_campaign = None
        self.published_posts = []
        self.analytics = {}
        
    # ============================================
    # WORKFLOW 1: LANZAMIENTO VIRAL DE VIDEO
    # ============================================
    
    async def launch_viral_video_campaign(
        self,
        video_path: str,
        artist_name: str,
        song_name: str,
        genre: str = "Trap",
        daily_ad_budget: float = 50.0,
        target_countries: List[str] = None
    ) -> Dict[str, Any]:
        """
        🎬 WORKFLOW COMPLETO DE LANZAMIENTO VIRAL
        
        Este es el flujo principal para Community Manager:
        
        1. PREPARACIÓN
           - Validar video
           - Generar metadata optimizada
           - Preparar creative assets
        
        2. PUBLICACIÓN MULTI-PLATAFORMA (Simultánea)
           - YouTube (con SEO optimization)
           - TikTok (10 cuentas device farm)
           - Instagram Reels (5 cuentas GoLogin)
           - Twitter (video native)
           - Facebook (página artista)
        
        3. AMPLIFICACIÓN PAGADA
           - Meta Ads campaign ($50/día)
           - Targeting: fans de trap/reggaeton
           - Objetivo: Landing page views
        
        4. ENGAGEMENT AUTOMATION
           - Device Farm: Likes/comments en TikTok/IG
           - GoLogin: Engagement web-based
           - ML-driven: Timing y cantidad
        
        5. TRACKING & OPTIMIZATION
           - Facebook Pixel: Track conversions
           - ML Predictor: Optimize budget
           - Analytics: Unified dashboard
        
        Returns:
            Dict con IDs de publicaciones, URLs, métricas iniciales
        """
        
        logger.info(f"🚀 LAUNCHING VIRAL CAMPAIGN: {artist_name} - {song_name}")
        
        if target_countries is None:
            target_countries = ["US", "MX", "ES", "AR", "CL", "CO"]
        
        campaign_results = {
            "campaign_id": f"viral_{datetime.now().timestamp()}",
            "artist": artist_name,
            "song": song_name,
            "genre": genre,
            "start_time": datetime.now().isoformat(),
            "platforms": {},
            "meta_ads": {},
            "engagement": {},
            "status": "in_progress"
        }
        
        try:
            # ========================================
            # FASE 1: PREPARACIÓN
            # ========================================
            logger.info("📋 FASE 1: Preparando assets...")
            
            preparation = await self._prepare_campaign_assets(
                video_path, artist_name, song_name, genre
            )
            campaign_results["preparation"] = preparation
            
            # ========================================
            # FASE 2: PUBLICACIÓN MULTI-PLATAFORMA
            # ========================================
            logger.info("📱 FASE 2: Publicando en TODAS las plataformas...")
            
            # 2.1 YouTube (Priority 1)
            youtube_result = await self._publish_to_youtube(
                video_path, artist_name, song_name, genre, preparation
            )
            campaign_results["platforms"]["youtube"] = youtube_result
            logger.info(f"✅ YouTube: {youtube_result.get('url')}")
            
            # 2.2 TikTok (Device Farm - 10 cuentas)
            tiktok_results = await self._publish_to_tiktok_farm(
                video_path, artist_name, song_name, preparation
            )
            campaign_results["platforms"]["tiktok"] = tiktok_results
            logger.info(f"✅ TikTok: {len(tiktok_results.get('accounts', []))} cuentas")
            
            # 2.3 Instagram Reels (GoLogin - 5 cuentas)
            instagram_results = await self._publish_to_instagram_farm(
                video_path, artist_name, song_name, preparation
            )
            campaign_results["platforms"]["instagram"] = instagram_results
            logger.info(f"✅ Instagram: {len(instagram_results.get('accounts', []))} cuentas")
            
            # 2.4 Twitter
            twitter_result = await self._publish_to_twitter(
                video_path, artist_name, song_name, youtube_result.get("url")
            )
            campaign_results["platforms"]["twitter"] = twitter_result
            logger.info(f"✅ Twitter: {twitter_result.get('tweet_id')}")
            
            # 2.5 Facebook Page
            facebook_result = await self._publish_to_facebook_page(
                video_path, artist_name, song_name, preparation
            )
            campaign_results["platforms"]["facebook"] = facebook_result
            logger.info(f"✅ Facebook: {facebook_result.get('post_id')}")
            
            # ========================================
            # FASE 3: META ADS CAMPAIGN
            # ========================================
            logger.info("💰 FASE 3: Lanzando Meta Ads campaign...")
            
            meta_campaign = await self._create_meta_ads_campaign(
                artist_name,
                song_name,
                daily_ad_budget,
                target_countries,
                youtube_result.get("url")
            )
            campaign_results["meta_ads"] = meta_campaign
            logger.info(f"✅ Meta Ads: Campaign ID {meta_campaign.get('campaign_id')}")
            
            # ========================================
            # FASE 4: ENGAGEMENT AUTOMATION
            # ========================================
            logger.info("🤖 FASE 4: Activando engagement automation...")
            
            engagement_strategy = await self._activate_engagement_automation(
                campaign_results["platforms"]
            )
            campaign_results["engagement"] = engagement_strategy
            logger.info(f"✅ Engagement: {engagement_strategy.get('actions_scheduled')} acciones programadas")
            
            # ========================================
            # FASE 5: TRACKING SETUP
            # ========================================
            logger.info("📊 FASE 5: Configurando tracking...")
            
            tracking_setup = await self._setup_tracking(
                campaign_results,
                youtube_result.get("url")
            )
            campaign_results["tracking"] = tracking_setup
            logger.info(f"✅ Tracking: Pixel instalado, eventos configurados")
            
            # ========================================
            # FINALIZATION
            # ========================================
            campaign_results["status"] = "launched"
            campaign_results["end_time"] = datetime.now().isoformat()
            
            self.current_campaign = campaign_results
            
            logger.info("🎉 CAMPAIGN LAUNCHED SUCCESSFULLY!")
            logger.info(f"📊 Summary:")
            logger.info(f"   - Platforms: {len(campaign_results['platforms'])}")
            logger.info(f"   - Total accounts: {self._count_total_accounts(campaign_results)}")
            logger.info(f"   - Meta Ads budget: ${daily_ad_budget}/day")
            logger.info(f"   - Estimated reach: {self._estimate_reach(campaign_results)}")
            
            return campaign_results
            
        except Exception as e:
            logger.error(f"❌ Campaign launch failed: {e}", exc_info=True)
            campaign_results["status"] = "failed"
            campaign_results["error"] = str(e)
            return campaign_results
    
    # ============================================
    # INTERNAL METHODS - CADA FASE
    # ============================================
    
    async def _prepare_campaign_assets(
        self,
        video_path: str,
        artist_name: str,
        song_name: str,
        genre: str
    ) -> Dict[str, Any]:
        """Prepara todos los assets necesarios CON ML OPTIMIZATION"""
        
        if self.dummy_mode:
            # Simulate ML optimization
            ml_optimization = {
                "best_posting_time": "19:30",  # ML prediction
                "predicted_virality": 0.78,    # ML score
                "optimal_hashtags": [f"#{genre.lower()}", "#music", "#viral", "#trending"],
                "caption_sentiment": "positive",
                "thumbnail_score": 8.2,
                "content_quality_score": 9.1
            }
            
            return {
                "video_validated": True,
                "thumbnail_generated": f"/data/thumbnails/{song_name}_thumb.jpg",
                "ml_optimization": ml_optimization,  # ← ML CORE OUTPUT
                "captions_generated": {
                    "tiktok": f"🔥 {song_name} - {artist_name} 🎵 #trap #music",
                    "instagram": f"🎶 Nueva música! {song_name} ya disponible\n\n#{genre.lower()} #music #{artist_name.lower().replace(' ', '')}",
                    "twitter": f"🎵 {song_name} - {artist_name}\n\nEscúchala ahora: [link]\n\n#{genre} #NewMusic",
                    "youtube": f"{artist_name} - {song_name} (Official Video)"
                },
                "hashtags": ml_optimization["optimal_hashtags"],  # ← ML optimized
                "optimized_metadata": {
                    "title": f"{artist_name} - {song_name}",
                    "description": f"Official video for {song_name} by {artist_name}",
                    "tags": [artist_name, song_name, genre, "music", "official"]
                }
            }
        
        # ========================================
        # REAL ML IMPLEMENTATION (for production)
        # ========================================
        # 1. Validate video exists
        # if not os.path.exists(video_path):
        #     raise FileNotFoundError(f"Video not found: {video_path}")
        
        # 2. ML: Predict virality
        # virality_score = await self._ml_predict_virality(
        #     video_path=video_path,
        #     metadata={"artist": artist_name, "genre": genre}
        # )
        
        # 3. ML: Optimize posting time
        # best_time = await self._ml_optimize_posting_time(
        #     artist_name=artist_name,
        #     target_countries=target_countries
        # )
        
        # 4. ML: Optimize captions for each platform
        # captions = {}
        # for platform in ["tiktok", "instagram", "twitter", "youtube"]:
        #     base_caption = f"{song_name} - {artist_name}"
        #     captions[platform] = await self._ml_optimize_captions(
        #         base_caption=base_caption,
        #         platform=platform,
        #         target_audience={"genre": genre}
        #     )
        
        # 5. Generate thumbnail with PIL + ML thumbnail scorer
        # from PIL import Image
        # import cv2
        # video = cv2.VideoCapture(video_path)
        # # Extract best frame using ML
        # thumbnail_path = f"/data/thumbnails/{song_name}_thumb.jpg"
        
        # 6. Hashtag research with ML effectiveness scoring
        # hashtags = await self._ml_research_hashtags(genre, platform="tiktok")
        
        return {}
    
    async def _publish_to_youtube(
        self,
        video_path: str,
        artist_name: str,
        song_name: str,
        genre: str,
        preparation: Dict
    ) -> Dict[str, Any]:
        """Publica video en YouTube con metadata optimizada"""
        
        if self.dummy_mode:
            video_id = f"dummy_yt_{int(datetime.now().timestamp())}"
            return {
                "video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
                "status": "published",
                "metadata_optimized": True,
                "published_at": datetime.now().isoformat()
            }
        
        # TODO: Call v2/youtube_uploader service
        # POST http://localhost:9003/quick-upload
        
        return {}
    
    async def _publish_to_tiktok_farm(
        self,
        video_path: str,
        artist_name: str,
        song_name: str,
        preparation: Dict
    ) -> Dict[str, Any]:
        """Publica en 10 cuentas TikTok usando Device Farm"""
        
        if self.dummy_mode:
            accounts = []
            for i in range(10):
                accounts.append({
                    "account_id": f"tiktok_{i+1}",
                    "username": f"@music_account_{i+1}",
                    "video_id": f"tiktok_video_{i+1}_{int(datetime.now().timestamp())}",
                    "url": f"https://tiktok.com/@music_account_{i+1}/video/dummy",
                    "status": "published",
                    "published_at": datetime.now().isoformat()
                })
            
            return {
                "accounts": accounts,
                "total_published": len(accounts),
                "method": "device_farm",
                "caption": preparation.get("captions_generated", {}).get("tiktok", "")
            }
        
        # TODO: Use Device Farm v1
        # device_manager.publish_to_tiktok(accounts=10, video=video_path)
        
        return {}
    
    async def _publish_to_instagram_farm(
        self,
        video_path: str,
        artist_name: str,
        song_name: str,
        preparation: Dict
    ) -> Dict[str, Any]:
        """Publica en 5 cuentas Instagram usando GoLogin"""
        
        if self.dummy_mode:
            accounts = []
            for i in range(5):
                accounts.append({
                    "account_id": f"instagram_{i+1}",
                    "username": f"@artist_fanpage_{i+1}",
                    "post_id": f"ig_post_{i+1}_{int(datetime.now().timestamp())}",
                    "url": f"https://instagram.com/p/dummy_{i+1}",
                    "status": "published",
                    "published_at": datetime.now().isoformat()
                })
            
            return {
                "accounts": accounts,
                "total_published": len(accounts),
                "method": "gologin",
                "caption": preparation.get("captions_generated", {}).get("instagram", "")
            }
        
        # TODO: Use GoLogin automation v1
        # gologin_automation.publish_to_instagram(accounts=5, video=video_path)
        
        return {}
    
    async def _publish_to_twitter(
        self,
        video_path: str,
        artist_name: str,
        song_name: str,
        youtube_url: str
    ) -> Dict[str, Any]:
        """Publica en Twitter con video y link a YouTube"""
        
        if self.dummy_mode:
            return {
                "tweet_id": f"tweet_{int(datetime.now().timestamp())}",
                "url": f"https://twitter.com/artist/status/dummy",
                "status": "published",
                "includes_video": True,
                "youtube_link": youtube_url,
                "published_at": datetime.now().isoformat()
            }
        
        # TODO: Use TwitterController from v1
        # self.twitter_controller.post_video(video_path, caption)
        
        return {}
    
    async def _publish_to_facebook_page(
        self,
        video_path: str,
        artist_name: str,
        song_name: str,
        preparation: Dict
    ) -> Dict[str, Any]:
        """Publica en página oficial de Facebook"""
        
        if self.dummy_mode:
            return {
                "post_id": f"fb_post_{int(datetime.now().timestamp())}",
                "url": f"https://facebook.com/artist/posts/dummy",
                "status": "published",
                "page_id": "dummy_page_id",
                "published_at": datetime.now().isoformat()
            }
        
        # TODO: Use Meta Graph API
        # POST to /{page_id}/videos
        
        return {}
    
    async def _create_meta_ads_campaign(
        self,
        artist_name: str,
        song_name: str,
        daily_budget: float,
        target_countries: List[str],
        landing_url: str
    ) -> Dict[str, Any]:
        """Crea campaña de Meta Ads"""
        
        if self.dummy_mode:
            return {
                "campaign_id": f"campaign_{int(datetime.now().timestamp())}",
                "adset_id": f"adset_{int(datetime.now().timestamp())}",
                "ad_id": f"ad_{int(datetime.now().timestamp())}",
                "daily_budget": daily_budget,
                "objective": "CONVERSIONS",
                "optimization_goal": "LANDING_PAGE_VIEWS",
                "targeting": {
                    "countries": target_countries,
                    "interests": ["trap music", "hip hop", "new music"],
                    "age_range": [18, 35]
                },
                "status": "ACTIVE",
                "created_at": datetime.now().isoformat()
            }
        
        # TODO: Call v2/meta_ads service
        # POST http://localhost:9000/quick-campaign
        
        return {}
    
    async def _activate_engagement_automation(
        self,
        platforms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Activa bots de engagement en todas las publicaciones"""
        
        if self.dummy_mode:
            actions = []
            
            # TikTok engagement
            if "tiktok" in platforms:
                for account in platforms["tiktok"].get("accounts", [])[:3]:  # Top 3
                    actions.append({
                        "platform": "tiktok",
                        "action": "like",
                        "target": account["video_id"],
                        "quantity": 200,
                        "schedule": "next_2_hours"
                    })
            
            # Instagram engagement
            if "instagram" in platforms:
                for account in platforms["instagram"].get("accounts", [])[:3]:
                    actions.append({
                        "platform": "instagram",
                        "action": "like",
                        "target": account["post_id"],
                        "quantity": 150,
                        "schedule": "next_2_hours"
                    })
            
            return {
                "actions_scheduled": len(actions),
                "actions": actions,
                "total_likes": sum(a["quantity"] for a in actions),
                "method": "ml_driven",
                "status": "active"
            }
        
        # TODO: Use ML-driven bot engine from v1
        # bot_engine.schedule_engagement(platforms)
        
        return {}
    
    async def _setup_tracking(
        self,
        campaign_results: Dict,
        landing_url: str
    ) -> Dict[str, Any]:
        """Configura tracking con Facebook Pixel"""
        
        if self.dummy_mode:
            return {
                "pixel_id": "dummy_pixel_123456",
                "conversion_api_enabled": True,
                "events_tracked": [
                    "PageView",
                    "ViewContent",
                    "SpotifyClick",
                    "YouTubeClick",
                    "VideoWatch75"
                ],
                "landing_url": landing_url,
                "pixel_installed": True
            }
        
        # TODO: Configure Pixel Tracker service v2
        # GET http://localhost:9001/pixel/snippet
        
        return {}
    
    # ============================================
    # ANALYTICS & MONITORING
    # ============================================
    
    async def get_campaign_analytics(
        self,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtiene analytics unificados de TODAS las plataformas"""
        
        campaign = self.current_campaign if campaign_id is None else None
        
        if not campaign:
            return {"error": "No active campaign"}
        
        if self.dummy_mode:
            return {
                "campaign_id": campaign["campaign_id"],
                "elapsed_time": "2 hours",
                "platforms": {
                    "youtube": {
                        "views": 5400,
                        "likes": 320,
                        "comments": 45,
                        "shares": 28
                    },
                    "tiktok": {
                        "total_views": 127000,
                        "avg_views_per_account": 12700,
                        "total_likes": 8900,
                        "total_comments": 450,
                        "viral_probability": 0.72
                    },
                    "instagram": {
                        "total_views": 34000,
                        "avg_views_per_account": 6800,
                        "total_likes": 3200,
                        "total_comments": 180
                    },
                    "twitter": {
                        "views": 8900,
                        "retweets": 145,
                        "likes": 560,
                        "replies": 34
                    }
                },
                "meta_ads": {
                    "impressions": 45000,
                    "clicks": 1350,
                    "ctr": 3.0,
                    "spend": 25.00,
                    "landing_page_views": 980,
                    "cost_per_view": 0.026
                },
                "engagement_automation": {
                    "likes_given": 1400,
                    "comments_posted": 85,
                    "accounts_used": 18
                },
                "totals": {
                    "total_views": 220300,
                    "total_engagement": 15334,
                    "estimated_reach": 180000,
                    "viral_score": 8.5  # ← ML Core calculates this
                },
                "ml_insights": {  # ← NEW: ML Core insights
                    "virality_prediction": 0.78,
                    "predicted_peak_time": "23:00 UTC",
                    "sentiment_analysis": {
                        "positive": 0.82,
                        "neutral": 0.15,
                        "negative": 0.03
                    },
                    "shadowban_detected": False,
                    "engagement_health": "excellent",
                    "algorithm_favor_score": 0.89
                },
                "recommendations": [
                    "Aumentar presupuesto Meta Ads (+20%): ROAS actual 3.2x",
                    "Boost engagement en TikTok cuenta #3 (85k views)",
                    "Crear lookalike audience con mejores performers"
                ]
            }
        
        # TODO: Aggregate real analytics from all platforms
        
        return {}
    
    async def optimize_ongoing_campaign(self) -> Dict[str, Any]:
        """Optimiza campaña en curso basado en performance"""
        
        if not self.current_campaign:
            return {"error": "No active campaign"}
        
        analytics = await self.get_campaign_analytics()
        
        if self.dummy_mode:
            optimizations = []
            
            # Check Meta Ads performance
            meta_ads = analytics.get("meta_ads", {})
            if meta_ads.get("ctr", 0) > 2.5:
                optimizations.append({
                    "action": "increase_budget",
                    "platform": "meta_ads",
                    "current": 50,
                    "new": 60,
                    "reason": "High CTR (3.0%)"
                })
            
            # Check TikTok virality
            tiktok = analytics.get("platforms", {}).get("tiktok", {})
            if tiktok.get("viral_probability", 0) > 0.7:
                optimizations.append({
                    "action": "boost_engagement",
                    "platform": "tiktok",
                    "target_accounts": [1, 3, 5],
                    "additional_likes": 500,
                    "reason": "High viral probability (0.72)"
                })
            
            return {
                "optimizations_applied": len(optimizations),
                "optimizations": optimizations,
                "estimated_impact": "+35% reach",
                "timestamp": datetime.now().isoformat()
            }
        
        # TODO: Use ML Predictor v2 to suggest optimizations
        # POST http://localhost:9004/optimize
        
        return {}
    
    # ============================================
    # WORKFLOW 2: MONITOR Y AUTO-VIRALIZAR CANAL
    # ============================================
    
    async def monitor_and_viralize_channel(
        self,
        youtube_channel_id: str,
        auto_launch: bool = True,
        virality_threshold: float = 0.70,
        max_campaigns_per_day: int = 2,
        daily_ad_budget_per_video: float = 50.0,
        target_countries: List[str] = None,
        check_interval_hours: int = 6
    ) -> Dict[str, Any]:
        """
        🔄 WORKFLOW DE MONITOREO CONTINUO DE CANAL
        
        Monitorea un canal de YouTube 24/7 y automáticamente viraliza
        videos nuevos que tengan alto potencial viral.
        
        CONTROL DE CARGA INTELIGENTE:
        - max_campaigns_per_day: Límite diario de campañas (default: 2)
        - virality_threshold: Score mínimo para auto-launch (default: 0.70)
        - check_interval_hours: Cada cuántas horas revisar (default: 6)
        - Prioriza videos con mayor score si hay múltiples nuevos
        - Respeta límites de UTM (Meta Ads, Device Farm, GoLogin)
        
        Args:
            youtube_channel_id: ID del canal a monitorear (UC_xxx)
            auto_launch: Si True, auto-lanza campañas. Si False, solo notifica
            virality_threshold: Score ML mínimo (0.0-1.0) para auto-launch
            max_campaigns_per_day: Máximo de campañas por día (evita sobrecarga)
            daily_ad_budget_per_video: Budget Meta Ads por video
            target_countries: Países objetivo
            check_interval_hours: Intervalo de revisión en horas
        
        Returns:
            Dict con estado del monitor, videos detectados, campañas lanzadas
        """
        
        logger.info(f"🔄 STARTING CHANNEL MONITOR: {youtube_channel_id}")
        logger.info(f"   - Auto-launch: {auto_launch}")
        logger.info(f"   - Virality threshold: {virality_threshold}")
        logger.info(f"   - Max campaigns/day: {max_campaigns_per_day}")
        logger.info(f"   - Check interval: {check_interval_hours}h")
        
        if target_countries is None:
            target_countries = ["US", "MX", "ES", "AR", "CL", "CO"]
        
        monitor_state = {
            "channel_id": youtube_channel_id,
            "started_at": datetime.now().isoformat(),
            "auto_launch_enabled": auto_launch,
            "virality_threshold": virality_threshold,
            "max_campaigns_per_day": max_campaigns_per_day,
            "campaigns_launched_today": 0,
            "videos_monitored": [],
            "campaigns": [],
            "status": "monitoring"
        }
        
        try:
            # ========================================
            # FASE 1: VERIFICAR LÍMITES DIARIOS
            # ========================================
            campaigns_today = self._count_campaigns_today(monitor_state)
            
            if campaigns_today >= max_campaigns_per_day:
                logger.warning(f"⚠️ Daily campaign limit reached: {campaigns_today}/{max_campaigns_per_day}")
                logger.info(f"   Next check in {check_interval_hours} hours...")
                
                return {
                    **monitor_state,
                    "status": "waiting",
                    "message": f"Daily limit reached ({campaigns_today}/{max_campaigns_per_day})",
                    "next_check": self._calculate_next_check(check_interval_hours)
                }
            
            # ========================================
            # FASE 2: DETECTAR VIDEOS NUEVOS
            # ========================================
            logger.info("📹 Buscando videos nuevos en el canal...")
            
            new_videos = await self._fetch_new_videos_from_channel(
                youtube_channel_id,
                hours_lookback=check_interval_hours * 2  # 2x para evitar perder videos
            )
            
            logger.info(f"   Encontrados: {len(new_videos)} videos nuevos")
            
            if not new_videos:
                logger.info("   No hay videos nuevos. Esperando...")
                
                return {
                    **monitor_state,
                    "status": "waiting",
                    "message": "No new videos found",
                    "next_check": self._calculate_next_check(check_interval_hours)
                }
            
            # ========================================
            # FASE 3: ANÁLISIS ML DE CADA VIDEO
            # ========================================
            logger.info("🧠 Analizando potencial viral con ML...")
            
            analyzed_videos = []
            
            for video in new_videos:
                logger.info(f"   Analizando: {video['title']}")
                
                # ML: Predict virality score
                virality_score = await self._ml_predict_virality(
                    video_path=video.get("video_id"),  # In production: download video
                    metadata={
                        "title": video["title"],
                        "description": video.get("description", ""),
                        "channel": youtube_channel_id,
                        "published_at": video["published_at"]
                    }
                )
                
                analyzed_videos.append({
                    **video,
                    "virality_score": virality_score,
                    "above_threshold": virality_score >= virality_threshold
                })
                
                logger.info(f"      Score: {virality_score:.2f} {'✅' if virality_score >= virality_threshold else '❌'}")
            
            # ========================================
            # FASE 4: PRIORIZAR Y FILTRAR
            # ========================================
            # Sort by virality score (highest first)
            analyzed_videos.sort(key=lambda v: v["virality_score"], reverse=True)
            
            # Filter: only above threshold
            viral_candidates = [v for v in analyzed_videos if v["above_threshold"]]
            
            logger.info(f"   Videos con potencial viral: {len(viral_candidates)}/{len(analyzed_videos)}")
            
            if not viral_candidates:
                logger.info("   Ningún video supera el threshold. Esperando...")
                
                monitor_state["videos_monitored"] = analyzed_videos
                
                return {
                    **monitor_state,
                    "status": "waiting",
                    "message": f"No videos above threshold ({virality_threshold})",
                    "analyzed_videos": analyzed_videos,
                    "next_check": self._calculate_next_check(check_interval_hours)
                }
            
            # ========================================
            # FASE 5: LANZAR CAMPAÑAS (CON LÍMITE)
            # ========================================
            remaining_slots = max_campaigns_per_day - campaigns_today
            
            videos_to_launch = viral_candidates[:remaining_slots]
            
            logger.info(f"🚀 Lanzando {len(videos_to_launch)} campañas (quedan {remaining_slots} slots)")
            
            launched_campaigns = []
            
            for i, video in enumerate(videos_to_launch, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"CAMPAÑA {i}/{len(videos_to_launch)}: {video['title']}")
                logger.info(f"Virality Score: {video['virality_score']:.2f}")
                logger.info(f"{'='*60}\n")
                
                if auto_launch:
                    try:
                        # Extract artist name from channel or video title
                        artist_name = self._extract_artist_name(video, youtube_channel_id)
                        song_name = video["title"]
                        
                        # Launch full viral campaign
                        campaign_result = await self.launch_viral_video_campaign(
                            video_path=video["video_id"],  # In production: download first
                            artist_name=artist_name,
                            song_name=song_name,
                            genre="Music",  # Could be ML-predicted
                            daily_ad_budget=daily_ad_budget_per_video,
                            target_countries=target_countries
                        )
                        
                        launched_campaigns.append({
                            "video": video,
                            "campaign": campaign_result,
                            "launched_at": datetime.now().isoformat()
                        })
                        
                        logger.info(f"✅ Campaña lanzada: {campaign_result.get('campaign_id')}")
                        
                        # Update counter
                        monitor_state["campaigns_launched_today"] += 1
                        
                        # Delay between campaigns (avoid rate limits)
                        if i < len(videos_to_launch):
                            logger.info("⏳ Esperando 5 minutos antes de siguiente campaña...")
                            await asyncio.sleep(300)  # 5 min
                        
                    except Exception as e:
                        logger.error(f"❌ Error lanzando campaña: {e}", exc_info=True)
                        launched_campaigns.append({
                            "video": video,
                            "error": str(e),
                            "launched_at": datetime.now().isoformat()
                        })
                else:
                    # Solo notificar (no auto-launch)
                    logger.info(f"📧 NOTIFICACIÓN: Video '{video['title']}' tiene score {video['virality_score']:.2f}")
                    logger.info(f"   Auto-launch deshabilitado. Requiere aprobación manual.")
            
            # ========================================
            # FASE 6: RESUMEN Y NEXT STEPS
            # ========================================
            monitor_state["videos_monitored"] = analyzed_videos
            monitor_state["campaigns"] = launched_campaigns
            monitor_state["status"] = "active"
            
            logger.info(f"\n{'='*60}")
            logger.info(f"RESUMEN DEL CICLO:")
            logger.info(f"{'='*60}")
            logger.info(f"   Videos analizados: {len(analyzed_videos)}")
            logger.info(f"   Con potencial viral: {len(viral_candidates)}")
            logger.info(f"   Campañas lanzadas: {len(launched_campaigns)}")
            logger.info(f"   Campañas hoy: {monitor_state['campaigns_launched_today']}/{max_campaigns_per_day}")
            logger.info(f"   Próxima revisión: {check_interval_hours} horas")
            logger.info(f"{'='*60}\n")
            
            return monitor_state
            
        except Exception as e:
            logger.error(f"❌ Monitor error: {e}", exc_info=True)
            monitor_state["status"] = "error"
            monitor_state["error"] = str(e)
            return monitor_state
    
    async def _fetch_new_videos_from_channel(
        self,
        channel_id: str,
        hours_lookback: int = 12
    ) -> List[Dict[str, Any]]:
        """Obtiene videos nuevos del canal en las últimas N horas"""
        
        if self.dummy_mode:
            # Simulate 2 new videos found
            from datetime import timedelta
            now = datetime.now()
            
            return [
                {
                    "video_id": f"dummy_video_1_{int(now.timestamp())}",
                    "title": "Nuevo Single 2025 - Official Video",
                    "description": "Official music video for my new single",
                    "url": "https://youtube.com/watch?v=dummy1",
                    "published_at": (now - timedelta(hours=3)).isoformat(),
                    "duration": "3:45",
                    "views": 1250,
                    "likes": 89,
                    "comments": 12
                },
                {
                    "video_id": f"dummy_video_2_{int(now.timestamp())}",
                    "title": "Behind The Scenes - Nuevo Album",
                    "description": "Behind the scenes footage",
                    "url": "https://youtube.com/watch?v=dummy2",
                    "published_at": (now - timedelta(hours=8)).isoformat(),
                    "duration": "5:20",
                    "views": 450,
                    "likes": 32,
                    "comments": 5
                }
            ]
        
        # TODO: Real YouTube Data API v3 call
        # GET https://www.googleapis.com/youtube/v3/search
        # ?part=snippet
        # &channelId={channel_id}
        # &publishedAfter={hours_lookback}
        # &type=video
        # &order=date
        
        return []
    
    def _count_campaigns_today(self, monitor_state: Dict) -> int:
        """Cuenta campañas lanzadas hoy (para rate limiting)"""
        
        # In production: query database
        # SELECT COUNT(*) FROM campaigns
        # WHERE DATE(created_at) = CURRENT_DATE
        
        return monitor_state.get("campaigns_launched_today", 0)
    
    def _calculate_next_check(self, hours: int) -> str:
        """Calcula timestamp de próxima revisión"""
        from datetime import timedelta
        
        next_check = datetime.now() + timedelta(hours=hours)
        return next_check.isoformat()
    
    def _extract_artist_name(self, video: Dict, channel_id: str) -> str:
        """Extrae nombre del artista del video o canal"""
        
        # Try from video title (pattern: "Artist - Song")
        title = video.get("title", "")
        if " - " in title:
            return title.split(" - ")[0].strip()
        
        # TODO: In production, fetch channel info from YouTube API
        # GET https://www.googleapis.com/youtube/v3/channels?id={channel_id}
        
        # Fallback
        return "Artist"
    
    # ============================================
    # ML CORE METHODS (from Docker v1)
    # ============================================
    
    async def _ml_predict_virality(
        self,
        video_path: str,
        metadata: Dict[str, Any]
    ) -> float:
        """
        Predice probabilidad de viralidad usando ML Core
        
        En producción:
        - POST http://localhost:8000/predict_virality
        - YOLOv8 analiza video frame by frame
        - LSTM predice engagement basado en histórico
        - Returns: 0.0-1.0 score
        """
        if self.dummy_mode:
            # Simulated ML prediction
            import random
            base_score = 0.65
            
            # Adjust based on metadata
            if "trap" in str(metadata).lower() or "reggaeton" in str(metadata).lower():
                base_score += 0.10  # Trap/Reggaeton trend bonus
            
            if metadata.get("has_hook", False):
                base_score += 0.05  # Hook bonus
            
            return min(base_score + random.uniform(-0.05, 0.10), 0.95)
        
        # TODO: Real ML Core API call
        # response = await httpx.post(f"{self.ml_core_url}/predict_virality", ...)
        return 0.0
    
    async def _ml_optimize_posting_time(
        self,
        artist_name: str,
        target_countries: List[str]
    ) -> str:
        """
        ML predicts best posting time based on:
        - Historical engagement patterns
        - Audience timezone distribution
        - Platform algorithms
        
        Returns: "HH:MM" (24h format)
        """
        if self.dummy_mode:
            # Simulated ML optimization
            # Best times for music content: 7pm-9pm local time
            return "19:30"
        
        # TODO: Real ML Core API call
        # POST http://localhost:8000/predict_posting_time
        return "18:00"
    
    async def _ml_detect_shadowban(
        self,
        account_id: str,
        platform: str,
        recent_posts: List[Dict]
    ) -> bool:
        """
        ML-based shadowban detection
        
        Analyzes:
        - Engagement drop patterns
        - View distribution anomalies
        - Follower/view ratio
        
        Returns: True if shadowbanned
        """
        if self.dummy_mode:
            # Simulate no shadowban
            return False
        
        # TODO: Real ML Core API call
        # POST http://localhost:8000/detect_anomaly
        return False
    
    async def _ml_optimize_captions(
        self,
        base_caption: str,
        platform: str,
        target_audience: Dict
    ) -> str:
        """
        ML-optimized caption generation
        
        Uses:
        - NLP sentiment analysis
        - Emoji optimization
        - Hashtag effectiveness scoring
        - Platform-specific best practices
        """
        if self.dummy_mode:
            # Basic optimization
            if platform == "tiktok":
                return f"🔥 {base_caption} 🎵 #fyp #viral"
            elif platform == "instagram":
                return f"✨ {base_caption} 💫\n\n#music #newmusic #viral"
            else:
                return base_caption
        
        # TODO: Real ML Core API call
        # POST http://localhost:8000/optimize_caption
        return base_caption
    
    async def _ml_calculate_affinity(
        self,
        account_id: str,
        target_account_id: str
    ) -> float:
        """
        Calculate affinity score between accounts
        
        Used for:
        - Engagement target selection
        - Collaboration opportunities
        - Audience overlap analysis
        
        Returns: 0.0-1.0 affinity score
        """
        if self.dummy_mode:
            import random
            return random.uniform(0.5, 0.9)
        
        # TODO: Real ML Core API call
        # POST http://localhost:8000/calculate_affinity
        return 0.0
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _count_total_accounts(self, campaign_results: Dict) -> int:
        """Cuenta total de cuentas usadas"""
        count = 0
        platforms = campaign_results.get("platforms", {})
        
        count += len(platforms.get("tiktok", {}).get("accounts", []))
        count += len(platforms.get("instagram", {}).get("accounts", []))
        count += 1 if "youtube" in platforms else 0
        count += 1 if "twitter" in platforms else 0
        count += 1 if "facebook" in platforms else 0
        
        return count
    
    def _estimate_reach(self, campaign_results: Dict) -> str:
        """Estima alcance potencial"""
        # Simplified estimation
        num_accounts = self._count_total_accounts(campaign_results)
        ad_budget = campaign_results.get("meta_ads", {}).get("daily_budget", 50)
        
        organic_reach = num_accounts * 5000  # 5k avg per account
        paid_reach = ad_budget * 1000  # $1 = 1k impressions
        
        total = organic_reach + paid_reach
        
        if total < 100000:
            return f"{total:,} (Local)"
        elif total < 500000:
            return f"{total:,} (Regional)"
        else:
            return f"{total:,} (Nacional)"


# ============================================
# COMMAND LINE INTERFACE
# ============================================

async def main():
    """
    CLI para testear el sistema unificado
    
    Modos:
    - launch: Lanza campaña viral de un video
    - monitor-channel: Monitorea canal y auto-viraliza videos nuevos
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🚀 Unified System V3 - Community Manager"
    )
    
    parser.add_argument(
        "--mode",
        choices=["launch", "monitor-channel", "demo"],
        default="demo",
        help="Modo de operación"
    )
    
    # Launch mode arguments
    parser.add_argument("--video", help="Path o URL del video")
    parser.add_argument("--campaign-name", help="Nombre de la campaña")
    parser.add_argument("--artist-name", help="Nombre del artista")
    parser.add_argument("--genre", default="Music", help="Género musical")
    parser.add_argument("--target-views", type=int, default=1000000, help="Views objetivo")
    parser.add_argument("--paid-budget", type=float, default=50.0, help="Budget diario Meta Ads")
    
    # Monitor mode arguments
    parser.add_argument("--youtube-channel", help="ID del canal de YouTube (UC_xxx)")
    parser.add_argument("--auto-launch", action="store_true", help="Auto-lanzar campañas")
    parser.add_argument("--virality-threshold", type=float, default=0.70, help="Score mínimo (0.0-1.0)")
    parser.add_argument("--max-campaigns-per-day", type=int, default=2, help="Máx campañas/día")
    parser.add_argument("--check-interval", type=int, default=6, help="Intervalo revisión (horas)")
    
    args = parser.parse_args()
    
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║   🚀 UNIFIED SYSTEM V3 - Community Manager           ║
    ║   Sistema Completo de Lanzamiento Viral              ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Initialize system
    system = UnifiedCommunityManagerSystem(dummy_mode=True)
    
    # ============================================
    # MODE: LAUNCH
    # ============================================
    if args.mode == "launch":
        if not args.video or not args.campaign_name:
            print("❌ Error: --video y --campaign-name son requeridos")
            return
        
        print(f"\n� LANZANDO CAMPAÑA: {args.campaign_name}\n")
        
        results = await system.launch_viral_video_campaign(
            video_path=args.video,
            artist_name=args.artist_name or "Artist",
            song_name=args.campaign_name,
            genre=args.genre,
            daily_ad_budget=args.paid_budget,
            target_countries=["US", "MX", "ES", "AR", "CL", "CO"]
        )
        
        print("\n" + "="*60)
        print("CAMPAIGN RESULTS:")
        print("="*60)
        print(json.dumps(results, indent=2))
        
        print(f"\n✅ Campaña lanzada: {results.get('campaign_id')}")
        print(f"📊 Target: {args.target_views:,} views")
        print(f"💰 Budget: ${args.paid_budget}/día")
        print(f"📈 Estimated reach: {system._estimate_reach(results)}")
    
    # ============================================
    # MODE: MONITOR-CHANNEL
    # ============================================
    elif args.mode == "monitor-channel":
        if not args.youtube_channel:
            print("❌ Error: --youtube-channel es requerido")
            return
        
        print(f"\n🔄 MONITOREANDO CANAL: {args.youtube_channel}\n")
        print(f"   Auto-launch: {'SÍ' if args.auto_launch else 'NO'}")
        print(f"   Threshold: {args.virality_threshold:.2f}")
        print(f"   Max campañas/día: {args.max_campaigns_per_day}")
        print(f"   Intervalo: {args.check_interval}h\n")
        
        monitor_result = await system.monitor_and_viralize_channel(
            youtube_channel_id=args.youtube_channel,
            auto_launch=args.auto_launch,
            virality_threshold=args.virality_threshold,
            max_campaigns_per_day=args.max_campaigns_per_day,
            daily_ad_budget_per_video=args.paid_budget,
            target_countries=["US", "MX", "ES", "AR", "CL", "CO"],
            check_interval_hours=args.check_interval
        )
        
        print("\n" + "="*60)
        print("MONITOR RESULTS:")
        print("="*60)
        print(json.dumps(monitor_result, indent=2))
        
        print(f"\n✅ Status: {monitor_result.get('status')}")
        print(f"📹 Videos analizados: {len(monitor_result.get('videos_monitored', []))}")
        print(f"🚀 Campañas lanzadas: {len(monitor_result.get('campaigns', []))}")
        print(f"📊 Campañas hoy: {monitor_result.get('campaigns_launched_today')}/{args.max_campaigns_per_day}")
    
    # ============================================
    # MODE: DEMO (default)
    # ============================================
    else:
        print("\n�📋 Ejemplo: Lanzamiento de 'Nueva Vida' por Stakas\n")
        
        # Launch campaign
        results = await system.launch_viral_video_campaign(
            video_path="/data/videos/nueva_vida_official.mp4",
            artist_name="Stakas",
            song_name="Nueva Vida",
            genre="Trap",
            daily_ad_budget=50.0,
            target_countries=["US", "MX", "ES", "AR", "CL", "CO"]
        )
        
        print("\n" + "="*60)
        print("CAMPAIGN RESULTS:")
        print("="*60)
        print(json.dumps(results, indent=2))
        
        # Wait and get analytics
        print("\n⏳ Esperando 2 horas (simulado)...\n")
        await asyncio.sleep(2)  # Simulate time passing
        
        analytics = await system.get_campaign_analytics()
        
        print("\n" + "="*60)
        print("CAMPAIGN ANALYTICS (2h):")
        print("="*60)
        print(json.dumps(analytics, indent=2))
        
        # Optimize
        print("\n🎯 Optimizando campaña...\n")
        optimizations = await system.optimize_ongoing_campaign()
        
        print("\n" + "="*60)
        print("OPTIMIZATIONS APPLIED:")
        print("="*60)
        print(json.dumps(optimizations, indent=2))
        
        print("\n✅ DEMO COMPLETADO\n")


if __name__ == "__main__":
    asyncio.run(main())
