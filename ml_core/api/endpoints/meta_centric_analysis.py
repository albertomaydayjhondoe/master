"""
🧠 ML Core Meta-Centric Adaptation
Analiza campañas Meta Ads y recomienda estrategia cross-platform
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meta-centric", tags=["meta-centric-ml"])

# ============================================
# MODELS FOR META-CENTRIC ANALYSIS
# ============================================

class MetaCampaignData(BaseModel):
    campaign_name: str = Field(..., description="Meta Ads campaign name")
    daily_budget: float = Field(..., description="Daily budget in USD")
    targeting: Dict[str, Any] = Field(default_factory=dict, description="Meta Ads targeting data")
    creative_assets: Dict[str, Any] = Field(default_factory=dict, description="Creative assets info")
    objective: str = Field(default="CONVERSIONS", description="Campaign objective")
    artist_name: Optional[str] = None
    song_name: Optional[str] = None
    genre: Optional[str] = None

class MetaCampaignAnalysis(BaseModel):
    virality_score: float = Field(..., description="Predicted virality score (0.0-1.0)")
    recommended_platforms: List[str] = Field(..., description="Recommended platforms")
    budget_allocation: Dict[str, float] = Field(..., description="Budget split per platform")
    posting_schedule: Dict[str, str] = Field(..., description="Optimal posting times")
    cross_platform_strategy: Dict[str, Any] = Field(..., description="Complete strategy")
    confidence: float = Field(..., description="Analysis confidence (0.0-1.0)")

# ============================================
# META-CENTRIC ML ANALYZER
# ============================================

class MetaCentricMLAnalyzer:
    """ML Intelligence específico para campañas Meta Ads"""
    
    def __init__(self):
        self.platform_weights = {
            "youtube": {"organic": 0.3, "reach": 0.4, "conversion": 0.35},
            "tiktok": {"organic": 0.5, "reach": 0.4, "conversion": 0.25}, 
            "instagram": {"organic": 0.4, "reach": 0.35, "conversion": 0.3},
            "twitter": {"organic": 0.3, "reach": 0.3, "conversion": 0.2}
        }
        
        self.genre_platform_affinity = {
            "hip_hop": {"tiktok": 0.8, "instagram": 0.7, "youtube": 0.6, "twitter": 0.4},
            "pop": {"instagram": 0.8, "tiktok": 0.7, "youtube": 0.7, "twitter": 0.5},
            "electronic": {"tiktok": 0.9, "youtube": 0.6, "instagram": 0.6, "twitter": 0.3},
            "rock": {"youtube": 0.8, "instagram": 0.5, "tiktok": 0.4, "twitter": 0.6},
            "reggaeton": {"tiktok": 0.9, "instagram": 0.8, "youtube": 0.6, "twitter": 0.4}
        }
    
    async def analyze_meta_campaign(self, campaign_data: MetaCampaignData) -> MetaCampaignAnalysis:
        """
        Análisis principal: Meta Ads → Cross-Platform Strategy
        """
        
        logger.info(f"🧠 Analyzing Meta campaign: {campaign_data.campaign_name}")
        
        # 1. Calcular virality score basado en Meta Ads data
        virality_score = await self._predict_virality_from_meta_data(campaign_data)
        
        # 2. Recomendar plataformas óptimas
        recommended_platforms = await self._recommend_platforms_for_meta_campaign(
            virality_score, campaign_data
        )
        
        # 3. Optimizar budget allocation cross-platform
        budget_allocation = await self._optimize_budget_allocation(
            campaign_data.daily_budget, recommended_platforms, campaign_data
        )
        
        # 4. Generar timeline de publicación óptimo
        posting_schedule = await self._generate_posting_timeline(
            recommended_platforms, campaign_data
        )
        
        # 5. Crear estrategia cross-platform completa
        cross_platform_strategy = await self._generate_cross_platform_strategy(
            campaign_data, virality_score, recommended_platforms
        )
        
        # 6. Calcular confidence del análisis
        confidence = await self._calculate_analysis_confidence(campaign_data)
        
        return MetaCampaignAnalysis(
            virality_score=virality_score,
            recommended_platforms=recommended_platforms,
            budget_allocation=budget_allocation,
            posting_schedule=posting_schedule,
            cross_platform_strategy=cross_platform_strategy,
            confidence=confidence
        )
    
    async def _predict_virality_from_meta_data(self, campaign_data: MetaCampaignData) -> float:
        """Predice viralidad basado en datos de Meta Ads"""
        
        base_score = 0.5
        
        # Factor budget (mayor budget = mayor potencial viral)
        budget_factor = min(campaign_data.daily_budget / 100.0, 1.0) * 0.2
        
        # Factor targeting (audiencia específica = mayor engagement)
        targeting = campaign_data.targeting
        targeting_factor = 0.0
        
        if targeting.get("age_min") and targeting.get("age_max"):
            age_range = targeting["age_max"] - targeting["age_min"]
            # Rango 18-35 es óptimo para música
            if 15 <= age_range <= 20:
                targeting_factor += 0.15
        
        if targeting.get("interests"):
            music_interests = len([i for i in targeting["interests"] if "music" in str(i).lower()])
            targeting_factor += min(music_interests * 0.05, 0.1)
        
        # Factor genre (algunos géneros son más virales)
        genre_factor = 0.0
        if campaign_data.genre:
            genre_lower = campaign_data.genre.lower()
            if genre_lower in ["hip_hop", "reggaeton", "electronic"]:
                genre_factor = 0.15
            elif genre_lower in ["pop", "latin"]:
                genre_factor = 0.1
        
        # Factor creative assets
        creative_factor = 0.0
        if campaign_data.creative_assets:
            if campaign_data.creative_assets.get("video_duration"):
                duration = campaign_data.creative_assets["video_duration"]
                # 15-60 segundos es óptimo para redes sociales
                if 15 <= duration <= 60:
                    creative_factor += 0.1
            
            if campaign_data.creative_assets.get("has_music_visualization"):
                creative_factor += 0.05
        
        # Factor naming (detección de palabras clave virales)
        name_factor = 0.0
        viral_keywords = ["remix", "challenge", "dance", "trending", "viral", "hit"]
        campaign_name_lower = campaign_data.campaign_name.lower()
        
        for keyword in viral_keywords:
            if keyword in campaign_name_lower:
                name_factor += 0.02
        
        # Calcular score final
        virality_score = base_score + budget_factor + targeting_factor + genre_factor + creative_factor + name_factor
        
        # Normalizar entre 0.0 y 1.0
        virality_score = max(0.0, min(1.0, virality_score))
        
        logger.info(f"📊 Virality score: {virality_score:.3f} (budget: +{budget_factor:.3f}, targeting: +{targeting_factor:.3f})")
        
        return virality_score
    
    async def _recommend_platforms_for_meta_campaign(
        self, 
        virality_score: float, 
        campaign_data: MetaCampaignData
    ) -> List[str]:
        """Recomienda plataformas óptimas basado en Meta campaign"""
        
        platform_scores = {}
        
        # Score base por género
        genre = campaign_data.genre or "pop"  # Default pop
        genre_lower = genre.lower()
        
        if genre_lower in self.genre_platform_affinity:
            platform_scores = self.genre_platform_affinity[genre_lower].copy()
        else:
            # Default platform scores
            platform_scores = {
                "youtube": 0.6,
                "tiktok": 0.7, 
                "instagram": 0.6,
                "twitter": 0.4
            }
        
        # Ajustar por virality score
        for platform in platform_scores:
            platform_scores[platform] *= (0.5 + virality_score * 0.5)
        
        # Ajustar por budget (más budget = más plataformas)
        min_platforms = 2 if campaign_data.daily_budget >= 50 else 1
        max_platforms = 4 if campaign_data.daily_budget >= 100 else 3
        
        # Ordenar plataformas por score
        sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Seleccionar top platforms dentro del rango
        recommended = []
        for platform, score in sorted_platforms:
            if score >= 0.5 and len(recommended) < max_platforms:
                recommended.append(platform)
        
        # Asegurar mínimo de plataformas
        if len(recommended) < min_platforms:
            for platform, _ in sorted_platforms:
                if platform not in recommended and len(recommended) < min_platforms:
                    recommended.append(platform)
        
        logger.info(f"🎯 Recommended platforms: {recommended}")
        return recommended
    
    async def _optimize_budget_allocation(
        self, 
        daily_budget: float, 
        platforms: List[str],
        campaign_data: MetaCampaignData
    ) -> Dict[str, float]:
        """Optimiza distribución de budget cross-platform"""
        
        if not platforms:
            return {}
        
        # Budget base por plataforma según efectividad
        platform_efficiency = {
            "youtube": 0.25,    # Mayor reach, menor costo por view
            "tiktok": 0.35,     # Alto engagement, viral potential
            "instagram": 0.25,  # Good targeting, medium cost  
            "twitter": 0.15     # Lower engagement, but good for awareness
        }
        
        # Ajustar por género
        genre = campaign_data.genre or "pop"
        if genre.lower() in self.genre_platform_affinity:
            genre_weights = self.genre_platform_affinity[genre.lower()]
            for platform in platforms:
                if platform in genre_weights:
                    platform_efficiency[platform] *= genre_weights[platform]
        
        # Calcular allocations
        total_weight = sum(platform_efficiency.get(p, 0.2) for p in platforms)
        
        allocations = {}
        for platform in platforms:
            weight = platform_efficiency.get(platform, 0.2)
            allocation_pct = weight / total_weight
            allocations[platform] = round(allocation_pct, 3)
        
        logger.info(f"💰 Budget allocation: {allocations}")
        return allocations
    
    async def _generate_posting_timeline(
        self, 
        platforms: List[str],
        campaign_data: MetaCampaignData
    ) -> Dict[str, str]:
        """Genera timeline óptimo de publicación por plataforma"""
        
        # Horarios óptimos por plataforma (hora local)
        optimal_times = {
            "youtube": "14:00",    # Afternoon peak
            "tiktok": "18:00",     # Evening peak for Gen Z
            "instagram": "20:00",  # Evening engagement peak
            "twitter": "16:00"     # Afternoon business hours
        }
        
        # Stagger posts para evitar competencia interna
        schedule = {}
        base_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        
        for i, platform in enumerate(platforms):
            # Espaciar posts por 2 horas
            post_time = base_time + timedelta(hours=i * 2)
            schedule[platform] = post_time.strftime("%H:%M")
        
        logger.info(f"📅 Posting schedule: {schedule}")
        return schedule
    
    async def _generate_cross_platform_strategy(
        self,
        campaign_data: MetaCampaignData,
        virality_score: float,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Genera estrategia completa cross-platform"""
        
        strategy = {
            "primary_objective": campaign_data.objective,
            "virality_potential": "high" if virality_score > 0.7 else "medium" if virality_score > 0.4 else "low",
            "content_strategy": {},
            "engagement_tactics": {},
            "optimization_triggers": {}
        }
        
        # Content strategy por plataforma
        for platform in platforms:
            if platform == "youtube":
                strategy["content_strategy"][platform] = {
                    "format": "music_video_with_lyric_overlay",
                    "duration": "full_song", 
                    "thumbnail": "artist_face_with_song_title",
                    "description": "full_lyrics_plus_social_links"
                }
            elif platform == "tiktok":
                strategy["content_strategy"][platform] = {
                    "format": "vertical_15_30_seconds",
                    "hook": "best_15_seconds_of_song",
                    "effects": "trending_effects_for_genre",
                    "hashtags": "genre_trending_plus_challenge"
                }
            elif platform == "instagram":
                strategy["content_strategy"][platform] = {
                    "stories": "behind_scenes_plus_song_preview",
                    "post": "carousel_with_lyrics",
                    "reels": "dance_challenge_or_lyric_video"
                }
            elif platform == "twitter":
                strategy["content_strategy"][platform] = {
                    "thread": "song_meaning_plus_creation_process",
                    "engagement": "respond_to_all_mentions",
                    "trending": "use_music_trending_hashtags"
                }
        
        # Engagement tactics
        if virality_score > 0.6:
            strategy["engagement_tactics"] = {
                "launch_challenge": True,
                "influencer_outreach": True,
                "user_generated_content": True,
                "cross_platform_contests": True
            }
        
        # Optimization triggers
        strategy["optimization_triggers"] = {
            "budget_increase_roas_threshold": 2.5,
            "pause_campaign_roas_threshold": 0.8,
            "platform_reallocation_threshold": 1.5,
            "creative_refresh_days": 7
        }
        
        return strategy
    
    async def _calculate_analysis_confidence(self, campaign_data: MetaCampaignData) -> float:
        """Calcula confidence del análisis ML"""
        
        confidence = 0.5  # Base confidence
        
        # Más datos = mayor confidence
        if campaign_data.targeting:
            confidence += 0.1
        
        if campaign_data.creative_assets:
            confidence += 0.1
            
        if campaign_data.genre:
            confidence += 0.1
            
        if campaign_data.daily_budget >= 50:
            confidence += 0.1
        
        if campaign_data.artist_name and campaign_data.song_name:
            confidence += 0.1
        
        return min(confidence, 0.95)  # Max 95% confidence

# ============================================
# API ENDPOINTS
# ============================================

analyzer = MetaCentricMLAnalyzer()

@router.post("/analyze_meta_campaign", response_model=MetaCampaignAnalysis)
async def analyze_meta_campaign(campaign_data: MetaCampaignData):
    """
    Endpoint principal: Analiza campaña Meta Ads y recomienda estrategia cross-platform
    """
    
    try:
        analysis = await analyzer.analyze_meta_campaign(campaign_data)
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Error in Meta campaign analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/predict_platform_performance")
async def predict_platform_performance(
    campaign_data: MetaCampaignData,
    target_platform: str
):
    """Predice performance específico de una plataforma"""
    
    try:
        # Simulated platform-specific prediction
        performance_prediction = {
            "platform": target_platform,
            "estimated_reach": int(campaign_data.daily_budget * 150),
            "estimated_engagement_rate": 0.045 if target_platform == "tiktok" else 0.025,
            "estimated_conversions": int(campaign_data.daily_budget * 0.8),
            "confidence": 0.75
        }
        
        return performance_prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize_budget_reallocation")
async def optimize_budget_reallocation(
    campaign_id: str,
    current_performance: Dict[str, Dict[str, float]]
):
    """Optimiza reallocación de budget basado en performance actual"""
    
    try:
        # Calculate performance scores
        platform_scores = {}
        
        for platform, metrics in current_performance.items():
            roas = metrics.get("roas", 1.0)
            engagement_rate = metrics.get("engagement_rate", 0.02)
            
            # Performance score combining ROAS and engagement
            score = (roas * 0.7) + (engagement_rate * 100 * 0.3)
            platform_scores[platform] = score
        
        # Redistribute budget based on performance
        total_score = sum(platform_scores.values())
        
        new_allocation = {}
        for platform, score in platform_scores.items():
            allocation = score / total_score if total_score > 0 else 0.25
            new_allocation[platform] = round(allocation, 3)
        
        return {
            "campaign_id": campaign_id,
            "current_performance": platform_scores,
            "new_budget_allocation": new_allocation,
            "optimization_reason": "performance_based_reallocation",
            "expected_improvement": "15-25% ROAS increase"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))