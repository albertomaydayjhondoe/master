"""
Meta Ads Automator
Complete Facebook/Instagram advertising automation with ML optimization
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
import hashlib
import hmac
import requests
from urllib.parse import urlencode

# Import configuration
try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

# Meta Business SDK (only load in production)
if not DUMMY_MODE:
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.adaccount import AdAccount
        from facebook_business.adobjects.campaign import Campaign
        from facebook_business.adobjects.adset import AdSet
        from facebook_business.adobjects.ad import Ad
        from facebook_business.adobjects.adcreative import AdCreative
        from facebook_business.adobjects.adimage import AdImage
        from facebook_business.adobjects.advideo import AdVideo
        from facebook_business.exceptions import FacebookRequestError
import numpy as np
        META_SDK_AVAILABLE = True
    except ImportError:
        META_SDK_AVAILABLE = False
        print("⚠️ Meta Business SDK not installed - using dummy mode")
        DUMMY_MODE = True
else:
    META_SDK_AVAILABLE = False

class CampaignObjective(Enum):
    REACH = "REACH"
    TRAFFIC = "LINK_CLICKS" 
    ENGAGEMENT = "ENGAGEMENT"
    APP_INSTALLS = "APP_INSTALLS"
    VIDEO_VIEWS = "VIDEO_VIEWS"
    LEAD_GENERATION = "LEAD_GENERATION"
    CONVERSIONS = "CONVERSIONS"

class OptimizationGoal(Enum):
    IMPRESSIONS = "IMPRESSIONS"
    CLICKS = "LINK_CLICKS"
    LANDING_PAGE_VIEWS = "LANDING_PAGE_VIEWS"
    CONVERSIONS = "CONVERSIONS"
    VALUE = "OFFSITE_CONVERSIONS"

class BidStrategy(Enum):
    LOWEST_COST = "LOWEST_COST_WITHOUT_CAP"
    TARGET_COST = "LOWEST_COST_WITH_BID_CAP"
    VALUE_OPTIMIZATION = "COST_CAP"

class CreativeType(Enum):
    SINGLE_IMAGE = "single_image"
    SINGLE_VIDEO = "single_video"
    CAROUSEL = "carousel"
    COLLECTION = "collection"

@dataclass
class TargetingSpec:
    countries: List[str]
    age_min: int = 18
    age_max: int = 65
    genders: List[int] = None  # [1] = male, [2] = female, [1,2] = all
    interests: List[str] = None
    behaviors: List[str] = None
    custom_audiences: List[str] = None
    lookalike_audiences: List[str] = None
    detailed_targeting: Dict[str, Any] = None

@dataclass
class Creative:
    creative_id: str
    name: str
    type: CreativeType
    title: str
    body: str
    call_to_action: str
    link_url: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

@dataclass
class CampaignBrief:
    campaign_name: str
    objective: CampaignObjective
    budget_total: float
    start_date: datetime
    end_date: datetime
    targeting: TargetingSpec
    creatives: List[Creative]
    optimization_goal: OptimizationGoal = OptimizationGoal.CONVERSIONS
    bid_strategy: BidStrategy = BidStrategy.LOWEST_COST
    pixel_id: Optional[str] = None
    conversion_event: str = "Purchase"

@dataclass
class AdMetrics:
    campaign_id: str
    adset_id: str
    ad_id: str
    timestamp: datetime
    impressions: int
    clicks: int
    spend: float
    conversions: int
    conversion_value: float
    ctr: float
    cpc: float
    cpm: float
    cpa: float
    roas: float

@dataclass
class MLInsight:
    insight_id: str
    campaign_id: str
    insight_type: str  # creative_score, audience_score, budget_recommendation
    score: float
    confidence: float
    recommended_action: Dict[str, Any]
    generated_at: datetime

class MetaPixelManager:
    """Manages Meta Pixel and Conversions API events"""
    
    def __init__(self, pixel_id: str, access_token: str):
        self.pixel_id = pixel_id
        self.access_token = access_token
        self.conversions_api_url = f"https://graph.facebook.com/v18.0/{pixel_id}/events"
        self.logger = logging.getLogger(f"{__name__}.MetaPixel")
    
    async def send_conversion_event(self, event_data: Dict[str, Any]) -> bool:
        """Send conversion event via Conversions API"""
        
        if DUMMY_MODE:
            return await self._dummy_send_event(event_data)
        
        try:
            # Hash user data for privacy
            if 'user_data' in event_data:
                event_data['user_data'] = self._hash_user_data(event_data['user_data'])
            
            payload = {
                'data': [event_data],
                'access_token': self.access_token
            }
            
            response = requests.post(self.conversions_api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('events_received', 0) > 0:
                self.logger.info(f"✅ Conversion event sent: {event_data.get('event_name')}")
                return True
            else:
                self.logger.error(f"❌ Event not received by Meta: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error sending conversion event: {e}")
            return False
    
    def _hash_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hash PII data for privacy compliance"""
        hashed_data = {}
        
        for key, value in user_data.items():
            if value and key in ['em', 'ph', 'fn', 'ln']:  # email, phone, first_name, last_name
                # Normalize and hash
                normalized = str(value).lower().strip()
                hashed_data[key] = hashlib.sha256(normalized.encode()).hexdigest()
            else:
                hashed_data[key] = value
        
        return hashed_data
    
    async def _dummy_send_event(self, event_data: Dict[str, Any]) -> bool:
        """Dummy implementation for testing"""
        self.logger.info(f"🎭 DUMMY: Conversion event - {event_data.get('event_name', 'Unknown')}")
        await asyncio.sleep(0.1)  # Simulate API delay
        return True

class MetaAdsAutomator:
    """Complete Meta Ads automation and optimization system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MetaAdsAutomator")
        
        # Meta API configuration
        self.app_id = config.get('app_id')
        self.app_secret = config.get('app_secret') 
        self.access_token = config.get('access_token')
        self.ad_account_id = config.get('ad_account_id')
        
        # Initialize API
        if not DUMMY_MODE and META_SDK_AVAILABLE:
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            self.ad_account = AdAccount(f"act_{self.ad_account_id}")
        else:
            self.ad_account = None
        
        # Pixel manager
        pixel_id = config.get('pixel_id')
        if pixel_id:
            self.pixel_manager = MetaPixelManager(pixel_id, self.access_token)
        else:
            self.pixel_manager = None
        
        # Campaign tracking
        self.active_campaigns: Dict[str, Dict[str, Any]] = {}
        self.campaign_metrics: Dict[str, List[AdMetrics]] = {}
        
        self.logger.info("🎯 Meta Ads Automator initialized")
    
    async def create_campaign_from_brief(self, brief: CampaignBrief) -> Dict[str, str]:
        """Create complete campaign from brief"""
        
        if DUMMY_MODE:
            return await self._dummy_create_campaign(brief)
        
        try:
            self.logger.info(f"🚀 Creating campaign: {brief.campaign_name}")
            
            # Create campaign
            campaign_id = await self._create_campaign(brief)
            
            # Create adsets and ads
            adset_ids = []
            ad_ids = []
            
            for creative in brief.creatives:
                # Upload creative assets
                creative_id = await self._create_creative(creative, brief)
                
                # Create adset
                adset_id = await self._create_adset(campaign_id, brief, creative.name)
                adset_ids.append(adset_id)
                
                # Create ad
                ad_id = await self._create_ad(adset_id, creative_id, brief)
                ad_ids.append(ad_id)
            
            # Store campaign info
            campaign_info = {
                'campaign_id': campaign_id,
                'adset_ids': adset_ids,
                'ad_ids': ad_ids,
                'brief': asdict(brief),
                'created_at': datetime.now(),
                'status': 'ACTIVE'
            }
            
            self.active_campaigns[campaign_id] = campaign_info
            
            self.logger.info(f"✅ Campaign created successfully: {campaign_id}")
            
            return {
                'campaign_id': campaign_id,
                'adset_ids': adset_ids,
                'ad_ids': ad_ids,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error creating campaign: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _create_campaign(self, brief: CampaignBrief) -> str:
        """Create Facebook campaign"""
        
        campaign_params = {
            Campaign.Field.name: brief.campaign_name,
            Campaign.Field.objective: brief.objective.value,
            Campaign.Field.status: Campaign.Status.active,
            Campaign.Field.buying_type: 'AUCTION'
        }
        
        if brief.budget_total:
            campaign_params[Campaign.Field.lifetime_budget] = int(brief.budget_total * 100)  # cents
        
        campaign = self.ad_account.create_campaign(params=campaign_params)
        return campaign['id']
    
    async def _create_adset(self, campaign_id: str, brief: CampaignBrief, adset_name: str) -> str:
        """Create Facebook adset"""
        
        # Build targeting
        targeting = {
            'geo_locations': {'countries': brief.targeting.countries},
            'age_min': brief.targeting.age_min,
            'age_max': brief.targeting.age_max
        }
        
        if brief.targeting.genders:
            targeting['genders'] = brief.targeting.genders
        
        if brief.targeting.interests:
            targeting['interests'] = [{'name': interest} for interest in brief.targeting.interests]
        
        if brief.targeting.behaviors:
            targeting['behaviors'] = [{'name': behavior} for behavior in brief.targeting.behaviors]
        
        # Adset parameters
        adset_params = {
            AdSet.Field.name: f"{brief.campaign_name} - {adset_name}",
            AdSet.Field.campaign_id: campaign_id,
            AdSet.Field.optimization_goal: brief.optimization_goal.value,
            AdSet.Field.bid_strategy: brief.bid_strategy.value,
            AdSet.Field.targeting: targeting,
            AdSet.Field.start_time: brief.start_date.isoformat(),
            AdSet.Field.end_time: brief.end_date.isoformat(),
            AdSet.Field.status: AdSet.Status.active
        }
        
        # Budget allocation (split evenly across creatives for now)
        daily_budget = (brief.budget_total / len(brief.creatives)) / ((brief.end_date - brief.start_date).days or 1)
        adset_params[AdSet.Field.daily_budget] = int(daily_budget * 100)  # cents
        
        # Add pixel for conversion tracking
        if brief.pixel_id and brief.objective == CampaignObjective.CONVERSIONS:
            adset_params[AdSet.Field.promoted_object] = {
                'pixel_id': brief.pixel_id,
                'custom_event_type': brief.conversion_event
            }
        
        adset = self.ad_account.create_ad_set(params=adset_params)
        return adset['id']
    
    async def _create_creative(self, creative: Creative, brief: CampaignBrief) -> str:
        """Create and upload creative assets"""
        
        creative_params = {
            AdCreative.Field.name: creative.name,
            AdCreative.Field.object_story_spec: {
                'page_id': self.config.get('page_id'),
                'link_data': {
                    'message': creative.body,
                    'link': creative.link_url,
                    'name': creative.title,
                    'call_to_action': {
                        'type': creative.call_to_action.upper(),
                        'value': {'link': creative.link_url}
                    }
                }
            }
        }
        
        # Handle different creative types
        if creative.type == CreativeType.SINGLE_IMAGE and creative.image_url:
            # Upload image
            image = self.ad_account.create_ad_image()
            image[AdImage.Field.filename] = creative.image_url
            image.remote_create()
            
            creative_params[AdCreative.Field.object_story_spec]['link_data']['image_hash'] = image[AdImage.Field.hash]
        
        elif creative.type == CreativeType.SINGLE_VIDEO and creative.video_url:
            # Upload video
            video = self.ad_account.create_ad_video()
            video[AdVideo.Field.source] = creative.video_url
            video.remote_create()
            
            creative_params[AdCreative.Field.object_story_spec]['video_data'] = {
                'video_id': video['id'],
                'message': creative.body,
                'call_to_action': {
                    'type': creative.call_to_action.upper(),
                    'value': {'link': creative.link_url}
                }
            }
        
        ad_creative = self.ad_account.create_ad_creative(params=creative_params)
        return ad_creative['id']
    
    async def _create_ad(self, adset_id: str, creative_id: str, brief: CampaignBrief) -> str:
        """Create Facebook ad"""
        
        ad_params = {
            Ad.Field.name: f"{brief.campaign_name} - Ad",
            Ad.Field.adset_id: adset_id,
            Ad.Field.creative: {'creative_id': creative_id},
            Ad.Field.status: Ad.Status.active
        }
        
        ad = self.ad_account.create_ad(params=ad_params)
        return ad['id']
    
    async def get_campaign_metrics(self, campaign_id: str, date_range: int = 7) -> List[AdMetrics]:
        """Get comprehensive campaign metrics"""
        
        if DUMMY_MODE:
            return await self._dummy_get_metrics(campaign_id, date_range)
        
        try:
            campaign_info = self.active_campaigns.get(campaign_id)
            if not campaign_info:
                return []
            
            metrics = []
            
            # Get insights for all ads
            for ad_id in campaign_info['ad_ids']:
                ad = Ad(ad_id)
                
                insights = ad.get_insights(
                    fields=[
                        'impressions', 'clicks', 'spend', 'conversions',
                        'conversion_values', 'ctr', 'cpc', 'cpm', 'cost_per_conversion'
                    ],
                    params={
                        'time_range': {
                            'since': (datetime.now() - timedelta(days=date_range)).strftime('%Y-%m-%d'),
                            'until': datetime.now().strftime('%Y-%m-%d')
                        },
                        'breakdowns': ['hourly_stats_aggregated_by_advertiser_time_zone']
                    }
                )
                
                for insight in insights:
                    conversions = float(insight.get('conversions', [{'value': '0'}])[0]['value'])
                    conversion_value = float(insight.get('conversion_values', [{'value': '0'}])[0]['value'])
                    spend = float(insight.get('spend', 0))
                    
                    metrics.append(AdMetrics(
                        campaign_id=campaign_id,
                        adset_id=insight.get('adset_id', ''),
                        ad_id=ad_id,
                        timestamp=datetime.now(),
                        impressions=int(insight.get('impressions', 0)),
                        clicks=int(insight.get('clicks', 0)),
                        spend=spend,
                        conversions=int(conversions),
                        conversion_value=conversion_value,
                        ctr=float(insight.get('ctr', 0)),
                        cpc=float(insight.get('cpc', 0)),
                        cpm=float(insight.get('cpm', 0)),
                        cpa=float(insight.get('cost_per_conversion', 0)),
                        roas=conversion_value / spend if spend > 0 else 0
                    ))
            
            # Cache metrics
            self.campaign_metrics[campaign_id] = metrics
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Error getting metrics for {campaign_id}: {e}")
            return []
    
    async def optimize_campaign(self, campaign_id: str, insights: List[MLInsight]) -> Dict[str, Any]:
        """Apply ML-driven optimizations to campaign"""
        
        if DUMMY_MODE:
            return await self._dummy_optimize_campaign(campaign_id, insights)
        
        try:
            results = {'optimizations_applied': 0, 'actions': []}
            
            for insight in insights:
                if insight.confidence < 0.7:  # Skip low-confidence insights
                    continue
                
                action = insight.recommended_action
                action_type = action.get('type')
                
                if action_type == 'scale_budget':
                    result = await self._scale_adset_budget(
                        action['adset_id'], 
                        action['scale_factor']
                    )
                    results['actions'].append({'type': 'scale_budget', 'result': result})
                
                elif action_type == 'pause_ad':
                    result = await self._pause_ad(action['ad_id'])
                    results['actions'].append({'type': 'pause_ad', 'result': result})
                
                elif action_type == 'adjust_targeting':
                    result = await self._adjust_adset_targeting(
                        action['adset_id'],
                        action['targeting_changes']
                    )
                    results['actions'].append({'type': 'adjust_targeting', 'result': result})
                
                results['optimizations_applied'] += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizing campaign {campaign_id}: {e}")
            return {'error': str(e)}
    
    async def _scale_adset_budget(self, adset_id: str, scale_factor: float) -> bool:
        """Scale adset daily budget"""
        try:
            adset = AdSet(adset_id)
            current_budget = int(adset[AdSet.Field.daily_budget])
            new_budget = int(current_budget * scale_factor)
            
            adset.update(params={AdSet.Field.daily_budget: new_budget})
            
            self.logger.info(f"✅ Scaled adset {adset_id} budget: {current_budget/100} -> {new_budget/100}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error scaling budget for adset {adset_id}: {e}")
            return False
    
    async def _pause_ad(self, ad_id: str) -> bool:
        """Pause underperforming ad"""
        try:
            ad = Ad(ad_id)
            ad.update(params={Ad.Field.status: Ad.Status.paused})
            
            self.logger.info(f"⏸️ Paused ad {ad_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error pausing ad {ad_id}: {e}")
            return False
    
    async def _adjust_adset_targeting(self, adset_id: str, targeting_changes: Dict[str, Any]) -> bool:
        """Adjust adset targeting parameters"""
        try:
            adset = AdSet(adset_id)
            current_targeting = adset[AdSet.Field.targeting]
            
            # Merge targeting changes
            new_targeting = {**current_targeting, **targeting_changes}
            
            adset.update(params={AdSet.Field.targeting: new_targeting})
            
            self.logger.info(f"🎯 Updated targeting for adset {adset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating targeting for adset {adset_id}: {e}")
            return False
    
    # Dummy implementations for testing
    
    async def _dummy_create_campaign(self, brief: CampaignBrief) -> Dict[str, str]:
        """Dummy campaign creation for testing"""
        self.logger.info(f"🎭 DUMMY: Creating campaign - {brief.campaign_name}")
        
        # Simulate API delay
        await asyncio.sleep(1.0)
        
        campaign_id = f"dummy_campaign_{int(time.time())}"
        adset_ids = [f"dummy_adset_{i}_{int(time.time())}" for i in range(len(brief.creatives))]
        ad_ids = [f"dummy_ad_{i}_{int(time.time())}" for i in range(len(brief.creatives))]
        
        # Store dummy campaign
        self.active_campaigns[campaign_id] = {
            'campaign_id': campaign_id,
            'adset_ids': adset_ids,
            'ad_ids': ad_ids,
            'brief': asdict(brief),
            'created_at': datetime.now(),
            'status': 'ACTIVE'
        }
        
        return {
            'campaign_id': campaign_id,
            'adset_ids': adset_ids,
            'ad_ids': ad_ids,
            'status': 'success'
        }
    
    async def _dummy_get_metrics(self, campaign_id: str, date_range: int) -> List[AdMetrics]:
        """Generate dummy metrics for testing"""
        
        campaign_info = self.active_campaigns.get(campaign_id)
        if not campaign_info:
            return []
        
        metrics = []
        base_time = datetime.now() - timedelta(hours=24)
        
        # Generate hourly metrics for last 24 hours
        for hour in range(24):
            timestamp = base_time + timedelta(hours=hour)
            
            for i, ad_id in enumerate(campaign_info['ad_ids']):
                # Simulate realistic metrics with some randomness
                impressions = np.random.randint(500, 2000)
                clicks = int(impressions * np.random.uniform(0.01, 0.05))  # 1-5% CTR
                spend = np.random.uniform(20, 100)
                conversions = int(clicks * np.random.uniform(0.02, 0.08))  # 2-8% conversion rate
                conversion_value = conversions * np.random.uniform(30, 150)
                
                metrics.append(AdMetrics(
                    campaign_id=campaign_id,
                    adset_id=campaign_info['adset_ids'][i],
                    ad_id=ad_id,
                    timestamp=timestamp,
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    conversions=conversions,
                    conversion_value=conversion_value,
                    ctr=clicks / impressions * 100 if impressions > 0 else 0,
                    cpc=spend / clicks if clicks > 0 else 0,
                    cpm=spend / impressions * 1000 if impressions > 0 else 0,
                    cpa=spend / conversions if conversions > 0 else 0,
                    roas=conversion_value / spend if spend > 0 else 0
                ))
        
        return metrics
    
    async def _dummy_optimize_campaign(self, campaign_id: str, insights: List[MLInsight]) -> Dict[str, Any]:
        """Dummy optimization for testing"""
        self.logger.info(f"🎭 DUMMY: Optimizing campaign {campaign_id} with {len(insights)} insights")
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            'optimizations_applied': len(insights),
            'actions': [
                {'type': insight.recommended_action.get('type', 'unknown'), 'result': True}
                for insight in insights
            ]
        }

# Factory function
def create_meta_automator(config: Dict[str, Any]) -> MetaAdsAutomator:
    """Create Meta Ads automator with configuration"""
    return MetaAdsAutomator(config)

# Example configuration
def get_example_config() -> Dict[str, Any]:
    """Get example configuration for Meta Ads"""
    return {
        'app_id': 'your_facebook_app_id',
        'app_secret': 'your_facebook_app_secret',
        'access_token': 'your_long_lived_access_token',
        'ad_account_id': '1234567890',
        'page_id': '0987654321',
        'pixel_id': 'your_pixel_id',
        'webhook_verify_token': 'your_webhook_verify_token'
    }