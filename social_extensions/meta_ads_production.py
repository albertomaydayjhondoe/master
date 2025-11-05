# 🚀 Neural Forge - Meta Ads Production API
# =========================================
# Real Meta Ads integration for production campaigns

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.exceptions import FacebookRequestError

logger = logging.getLogger(__name__)

class MetaAdsProductionAPI:
    """Production Meta Ads API with real campaign management"""
    
    def __init__(self):
        self.app_id = os.getenv('META_APP_ID')
        self.app_secret = os.getenv('META_APP_SECRET')
        self.access_token = os.getenv('META_ACCESS_TOKEN')
        self.ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
        self.page_id = os.getenv('META_PAGE_ID')
        self.pixel_id = os.getenv('META_PIXEL_ID')
        
        # Initialize Facebook API
        if all([self.app_id, self.app_secret, self.access_token]):
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.ad_account = AdAccount(f'act_{self.ad_account_id}')
            logger.info("🛰️ Meta Ads Production API initialized")
        else:
            logger.warning("⚠️ Meta Ads credentials not found, running in dummy mode")
            self.ad_account = None
    
    async def create_viral_campaign(self, 
                                   artist: str, 
                                   song: str, 
                                   video_path: str,
                                   budget: float = 100.0,
                                   target_countries: List[str] = ['US', 'MX', 'ES'],
                                   genre: str = 'trap') -> Dict[str, Any]:
        """Create complete viral campaign for music promotion"""
        
        if not self.ad_account:
            return {
                "success": False,
                "error": "Meta Ads not configured",
                "campaign_id": None
            }
        
        try:
            # 1. Upload video
            video_result = await self._upload_video(video_path)
            if not video_result['success']:
                return video_result
            
            # 2. Create campaign
            campaign_data = {
                Campaign.Field.name: f"🎵 {artist} - {song} | Neural Forge Viral",
                Campaign.Field.objective: Campaign.Objective.video_views,
                Campaign.Field.status: Campaign.Status.paused,
                Campaign.Field.special_ad_categories: []
            }
            
            campaign = self.ad_account.create_campaign(fields=[], params=campaign_data)
            logger.info(f"✅ Campaign created: {campaign.get_id()}")
            
            # 3. Create ad sets for each country
            adset_ids = []
            for country in target_countries:
                adset_data = {
                    AdSet.Field.name: f"{artist} - {song} | {country}",
                    AdSet.Field.campaign_id: campaign.get_id(),
                    AdSet.Field.daily_budget: int(budget * 100 / len(target_countries)),  # Convert to cents
                    AdSet.Field.billing_event: AdSet.BillingEvent.video_views,
                    AdSet.Field.optimization_goal: AdSet.OptimizationGoal.video_views,
                    AdSet.Field.targeting: {
                        'geo_locations': {'countries': [country]},
                        'age_min': 18,
                        'age_max': 35,
                        'interests': self._get_music_interests(genre)
                    },
                    AdSet.Field.status: AdSet.Status.paused
                }
                
                adset = self.ad_account.create_ad_set(fields=[], params=adset_data)
                adset_ids.append(adset.get_id())
                logger.info(f"✅ AdSet created for {country}: {adset.get_id()}")
            
            # 4. Create ads with video creative
            ad_ids = []
            for adset_id in adset_ids:
                # Create ad creative
                creative_data = {
                    AdCreative.Field.name: f"{artist} - {song} Creative",
                    AdCreative.Field.object_story_spec: {
                        'page_id': self.page_id,
                        'video_data': {
                            'video_id': video_result['video_id'],
                            'title': f"🎵 {artist} - {song}",
                            'message': f"🔥 Nuevo hit de {artist}! {song} ya disponible ✨ #NeuralForge #{genre}",
                            'call_to_action': {
                                'type': 'LISTEN_MUSIC'
                            }
                        }
                    }
                }
                
                creative = self.ad_account.create_ad_creative(fields=[], params=creative_data)
                
                # Create ad
                ad_data = {
                    Ad.Field.name: f"{artist} - {song} Ad",
                    Ad.Field.adset_id: adset_id,
                    Ad.Field.creative: {'creative_id': creative.get_id()},
                    Ad.Field.status: Ad.Status.paused
                }
                
                ad = self.ad_account.create_ad(fields=[], params=ad_data)
                ad_ids.append(ad.get_id())
                logger.info(f"✅ Ad created: {ad.get_id()}")
            
            # 5. Activate campaign
            campaign.api_update(params={Campaign.Field.status: Campaign.Status.active})
            for adset_id in adset_ids:
                AdSet(adset_id).api_update(params={AdSet.Field.status: AdSet.Status.active})
            for ad_id in ad_ids:
                Ad(ad_id).api_update(params={Ad.Field.status: Ad.Status.active})
            
            logger.info("🚀 Viral campaign activated!")
            
            return {
                "success": True,
                "campaign_id": campaign.get_id(),
                "adset_ids": adset_ids,
                "ad_ids": ad_ids,
                "video_id": video_result['video_id'],
                "total_budget": budget,
                "target_countries": target_countries,
                "status": "active"
            }
            
        except FacebookRequestError as e:
            logger.error(f"Meta Ads API error: {e}")
            return {
                "success": False,
                "error": f"Meta API Error: {e.api_error_message()}",
                "campaign_id": None
            }
        except Exception as e:
            logger.error(f"Campaign creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": None
            }
    
    async def _upload_video(self, video_path: str) -> Dict[str, Any]:
        """Upload video to Meta Ads"""
        try:
            video = AdVideo(parent_id=self.ad_account_id)
            video[AdVideo.Field.filepath] = video_path
            video.remote_create()
            
            return {
                "success": True,
                "video_id": video.get_id(),
                "path": video_path
            }
        except Exception as e:
            logger.error(f"Video upload error: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_id": None
            }
    
    def _get_music_interests(self, genre: str) -> List[Dict]:
        """Get targeting interests based on music genre"""
        genre_interests = {
            'trap': [
                {'id': '6003629266461', 'name': 'Hip hop music'},
                {'id': '6003888579390', 'name': 'Rap music'},
                {'id': '6003367513433', 'name': 'Urban contemporary music'}
            ],
            'reggaeton': [
                {'id': '6003310203330', 'name': 'Latin music'},
                {'id': '6003629266461', 'name': 'Hip hop music'},
                {'id': '6003888579390', 'name': 'Rap music'}
            ],
            'pop': [
                {'id': '6003310203330', 'name': 'Pop music'},
                {'id': '6003629266461', 'name': 'Contemporary R&B'},
                {'id': '6003888579390', 'name': 'Electronic dance music'}
            ]
        }
        
        return genre_interests.get(genre.lower(), genre_interests['trap'])
    
    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign performance metrics"""
        try:
            campaign = Campaign(campaign_id)
            insights = campaign.get_insights(fields=[
                'impressions',
                'reach',
                'video_views',
                'video_view_time',
                'spend',
                'ctr',
                'cpm',
                'cost_per_video_view'
            ])
            
            if insights:
                metrics = insights[0]
                return {
                    "success": True,
                    "campaign_id": campaign_id,
                    "metrics": {
                        "impressions": int(metrics.get('impressions', 0)),
                        "reach": int(metrics.get('reach', 0)),
                        "video_views": int(metrics.get('video_views', 0)),
                        "video_view_time": float(metrics.get('video_view_time', 0)),
                        "spend": float(metrics.get('spend', 0)),
                        "ctr": float(metrics.get('ctr', 0)),
                        "cpm": float(metrics.get('cpm', 0)),
                        "cost_per_video_view": float(metrics.get('cost_per_video_view', 0))
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No metrics available yet",
                    "campaign_id": campaign_id
                }
                
        except Exception as e:
            logger.error(f"Metrics retrieval error: {e}")
            return {
                "success": False,
                "error": str(e),
                "campaign_id": campaign_id
            }

# Factory function for production/dummy mode
def create_meta_ads_api():
    """Create Meta Ads API instance"""
    dummy_mode = os.getenv('DUMMY_MODE', 'true').lower() == 'true'
    
    if dummy_mode:
        from ml_core.bidirectional_engine import DummyPlatformController
        return DummyPlatformController("meta_ads")
    else:
        return MetaAdsProductionAPI()

# Global instance
meta_ads_api = create_meta_ads_api()