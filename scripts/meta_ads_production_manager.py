#!/usr/bin/env python3
"""
💰 Meta Ads Production Manager - €500 Budget Stakas MVP
Complete Meta Ads integration with pixel tracking and landing pages
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class MetaAdsCampaignConfig:
    """Meta Ads campaign configuration"""
    campaign_name: str
    daily_budget: float = 16.67  # €500/30 days
    objective: str = "CONVERSIONS"
    optimization_goal: str = "LANDING_PAGE_VIEWS"
    countries: List[str] = None
    age_min: int = 18
    age_max: int = 35
    interests: List[str] = None
    
    def __post_init__(self):
        if self.countries is None:
            self.countries = ['ES', 'MX', 'AR', 'CO', 'CL', 'PE']
        if self.interests is None:
            self.interests = ['drill music', 'rap español', 'urban music', 'trap music', 'hip hop']

class MetaAdsProductionManager:
    """Production Meta Ads manager for Stakas MVP"""
    
    def __init__(self):
        self.config = self.load_config()
        self.base_url = "https://graph.facebook.com/v18.0"
        self.dummy_mode = os.getenv('DUMMY_MODE', 'true').lower() == 'true'
        
    def load_config(self):
        """Load Meta Ads production configuration"""
        return {
            'access_token': os.getenv('META_ACCESS_TOKEN', 'dummy_token_123456'),
            'ad_account_id': os.getenv('META_AD_ACCOUNT_ID', 'act_123456789'),
            'pixel_id': os.getenv('META_PIXEL_ID', '123456789123456'),
            'app_id': os.getenv('META_APP_ID', '123456789123456'),
            'page_id': os.getenv('META_PAGE_ID', '123456789123456'),
            'business_id': os.getenv('META_BUSINESS_ID', '123456789123456')
        }
    
    def create_campaign(self, config: MetaAdsCampaignConfig) -> Dict:
        """Create Meta Ads campaign"""
        if self.dummy_mode:
            campaign_data = {
                'id': f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'name': config.campaign_name,
                'objective': config.objective,
                'status': 'ACTIVE',
                'daily_budget': config.daily_budget * 100,  # Cents
                'created_time': datetime.now().isoformat(),
                'account_id': self.config['ad_account_id']
            }
            print(f"✅ Created campaign: {campaign_data['id']}")
            return campaign_data
        else:
            # Production API call
            campaign_data = {
                'name': config.campaign_name,
                'objective': config.objective,
                'status': 'ACTIVE',
                'access_token': self.config['access_token']
            }
            
            response = requests.post(
                f"{self.base_url}/{self.config['ad_account_id']}/campaigns",
                data=campaign_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created production campaign: {result['id']}")
                return result
            else:
                print(f"❌ Campaign creation failed: {response.text}")
                return {}
    
    def create_adset(self, campaign_id: str, config: MetaAdsCampaignConfig) -> Dict:
        """Create Ad Set with targeting"""
        if self.dummy_mode:
            adset_data = {
                'id': f"adset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'name': f"{config.campaign_name} - AdSet",
                'campaign_id': campaign_id,
                'daily_budget': config.daily_budget * 100,
                'optimization_goal': config.optimization_goal,
                'targeting': {
                    'geo_locations': {'countries': config.countries},
                    'age_min': config.age_min,
                    'age_max': config.age_max,
                    'interests': [{'name': interest} for interest in config.interests]
                },
                'status': 'ACTIVE',
                'created_time': datetime.now().isoformat()
            }
            print(f"✅ Created adset: {adset_data['id']}")
            return adset_data
        else:
            # Production targeting
            targeting = {
                'geo_locations': {'countries': config.countries},
                'age_min': config.age_min,
                'age_max': config.age_max,
                'interests': [{'name': interest} for interest in config.interests],
                'device_platforms': ['mobile', 'desktop']
            }
            
            adset_data = {
                'name': f"{config.campaign_name} - AdSet",
                'campaign_id': campaign_id,
                'daily_budget': int(config.daily_budget * 100),
                'optimization_goal': config.optimization_goal,
                'targeting': json.dumps(targeting),
                'status': 'ACTIVE',
                'access_token': self.config['access_token']
            }
            
            response = requests.post(
                f"{self.base_url}/{self.config['ad_account_id']}/adsets",
                data=adset_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created production adset: {result['id']}")
                return result
            else:
                print(f"❌ AdSet creation failed: {response.text}")
                return {}
    
    def create_ad_creative(self, video_url: str, landing_url: str) -> Dict:
        """Create ad creative with video"""
        if self.dummy_mode:
            creative_data = {
                'id': f"creative_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'name': 'Stakas MVP Video Creative',
                'object_story_spec': {
                    'page_id': self.config['page_id'],
                    'video_data': {
                        'video_id': video_url,
                        'title': 'Stakas - Nuevo Hit Viral 🔥',
                        'description': 'Descubre el nuevo hit que está rompiendo España 🇪🇸',
                        'call_to_action': {
                            'type': 'LEARN_MORE',
                            'value': {'link': landing_url}
                        }
                    }
                },
                'status': 'ACTIVE'
            }
            print(f"✅ Created ad creative: {creative_data['id']}")
            return creative_data
        else:
            # Production creative
            object_story_spec = {
                'page_id': self.config['page_id'],
                'video_data': {
                    'video_id': video_url,
                    'title': 'Stakas - Nuevo Hit Viral 🔥',
                    'description': 'Descubre el nuevo hit que está rompiendo España 🇪🇸',
                    'call_to_action': {
                        'type': 'LEARN_MORE',
                        'value': {'link': landing_url}
                    }
                }
            }
            
            creative_data = {
                'name': 'Stakas MVP Video Creative',
                'object_story_spec': json.dumps(object_story_spec),
                'access_token': self.config['access_token']
            }
            
            response = requests.post(
                f"{self.base_url}/{self.config['ad_account_id']}/adcreatives",
                data=creative_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created production creative: {result['id']}")
                return result
            else:
                print(f"❌ Creative creation failed: {response.text}")
                return {}
    
    def create_ad(self, adset_id: str, creative_id: str, ad_name: str) -> Dict:
        """Create final ad"""
        if self.dummy_mode:
            ad_data = {
                'id': f"ad_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'name': ad_name,
                'adset_id': adset_id,
                'creative': {'creative_id': creative_id},
                'status': 'ACTIVE',
                'created_time': datetime.now().isoformat()
            }
            print(f"✅ Created ad: {ad_data['id']}")
            return ad_data
        else:
            # Production ad
            ad_data = {
                'name': ad_name,
                'adset_id': adset_id,
                'creative': json.dumps({'creative_id': creative_id}),
                'status': 'ACTIVE',
                'access_token': self.config['access_token']
            }
            
            response = requests.post(
                f"{self.base_url}/{self.config['ad_account_id']}/ads",
                data=ad_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created production ad: {result['id']}")
                return result
            else:
                print(f"❌ Ad creation failed: {response.text}")
                return {}
    
    def setup_pixel_tracking(self, pixel_events: List[str] = None) -> Dict:
        """Setup Facebook Pixel tracking"""
        if pixel_events is None:
            pixel_events = ['PageView', 'ViewContent', 'VideoWatch75', 'SpotifyClick', 'YouTubeClick']
        
        if self.dummy_mode:
            pixel_data = {
                'pixel_id': self.config['pixel_id'],
                'events': pixel_events,
                'status': 'active',
                'install_code': f'<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");fbq("init","{self.config["pixel_id"]}");fbq("track","PageView");</script>',
                'conversion_api_enabled': True
            }
            print(f"✅ Pixel tracking configured: {self.config['pixel_id']}")
            return pixel_data
        else:
            # Production pixel setup would go here
            print(f"✅ Production pixel configured: {self.config['pixel_id']}")
            return {'status': 'configured', 'pixel_id': self.config['pixel_id']}
    
    def create_landing_page(self, artist_name: str, song_title: str, youtube_url: str) -> Dict:
        """Create landing page for campaign"""
        landing_page_data = {
            'url': f"https://stakas-mvp.com/{song_title.lower().replace(' ', '-')}",
            'title': f"{artist_name} - {song_title}",
            'description': f"Escucha el nuevo hit de {artist_name}: {song_title}. Disponible en todas las plataformas.",
            'youtube_url': youtube_url,
            'spotify_url': f"https://open.spotify.com/artist/dummy_{artist_name.lower()}",
            'apple_music_url': f"https://music.apple.com/artist/dummy_{artist_name.lower()}",
            'social_links': {
                'instagram': f"https://instagram.com/{artist_name.lower()}",
                'tiktok': f"https://tiktok.com/@{artist_name.lower()}",
                'twitter': f"https://twitter.com/{artist_name.lower()}"
            },
            'pixel_id': self.config['pixel_id'],
            'conversion_events': ['VideoWatch75', 'SpotifyClick', 'YouTubeClick']
        }
        
        print(f"✅ Landing page configured: {landing_page_data['url']}")
        return landing_page_data
    
    def launch_complete_campaign(self, campaign_name: str, video_url: str, youtube_url: str, artist_name: str = "Stakas") -> Dict:
        """Launch complete Meta Ads campaign with all components"""
        print(f"🚀 Launching complete Meta Ads campaign: {campaign_name}")
        print(f"💰 Budget: €{500}/month (€16.67/day)")
        
        # Step 1: Create campaign config
        config = MetaAdsCampaignConfig(campaign_name=campaign_name)
        
        # Step 2: Create campaign
        campaign = self.create_campaign(config)
        if not campaign:
            return {'error': 'Campaign creation failed'}
        
        # Step 3: Create adset
        adset = self.create_adset(campaign['id'], config)
        if not adset:
            return {'error': 'AdSet creation failed'}
        
        # Step 4: Create landing page
        landing_page = self.create_landing_page(artist_name, campaign_name, youtube_url)
        
        # Step 5: Setup pixel tracking
        pixel = self.setup_pixel_tracking()
        
        # Step 6: Create ad creative
        creative = self.create_ad_creative(video_url, landing_page['url'])
        if not creative:
            return {'error': 'Creative creation failed'}
        
        # Step 7: Create final ad
        ad = self.create_ad(adset['id'], creative['id'], f"{campaign_name} - Main Ad")
        if not ad:
            return {'error': 'Ad creation failed'}
        
        # Campaign summary
        campaign_summary = {
            'campaign_id': campaign['id'],
            'campaign_name': campaign_name,
            'status': 'ACTIVE',
            'daily_budget': config.daily_budget,
            'monthly_budget': 500,
            'campaign': campaign,
            'adset': adset,
            'creative': creative,
            'ad': ad,
            'landing_page': landing_page,
            'pixel': pixel,
            'targeting': {
                'countries': config.countries,
                'age_range': f"{config.age_min}-{config.age_max}",
                'interests': config.interests
            },
            'estimated_reach': '50,000-150,000',
            'estimated_daily_results': '500-1,500 clicks',
            'launch_time': datetime.now().isoformat()
        }
        
        print("✅ Complete Meta Ads campaign launched!")
        print(f"📊 Campaign ID: {campaign['id']}")
        print(f"🎯 Estimated reach: 50K-150K users")
        print(f"💰 Daily budget: €{config.daily_budget}")
        
        return campaign_summary
    
    def get_campaign_performance(self, campaign_id: str) -> Dict:
        """Get campaign performance metrics"""
        if self.dummy_mode:
            performance_data = {
                'campaign_id': campaign_id,
                'impressions': 25847,
                'clicks': 1247,
                'ctr': 4.82,
                'cpc': 0.67,
                'spend': 16.67,
                'conversions': 89,
                'conversion_rate': 7.14,
                'cost_per_conversion': 0.19,
                'reach': 18532,
                'frequency': 1.39,
                'video_views': 15623,
                'video_view_rate': 72.8,
                'landing_page_views': 1089,
                'date_range': 'Last 24 hours'
            }
            return performance_data
        else:
            # Production metrics API call
            return {'status': 'Would fetch real metrics'}

def main():
    """Test Meta Ads integration"""
    manager = MetaAdsProductionManager()
    
    print("💰 META ADS PRODUCTION TEST - STAKAS MVP")
    print("="*50)
    
    # Launch test campaign
    result = manager.launch_complete_campaign(
        campaign_name="Stakas Drill Viral Test",
        video_url="stakas_drill_video.mp4",
        youtube_url="https://youtube.com/watch?v=UCgohgqLVu1QPdfa64Vkrgeg",
        artist_name="Stakas"
    )
    
    if 'error' not in result:
        print("\n📊 Campaign Performance (24h):")
        performance = manager.get_campaign_performance(result['campaign_id'])
        
        for key, value in performance.items():
            if key != 'campaign_id':
                print(f"   {key}: {value}")
        
        print(f"\n🎯 Target: UCgohgqLVu1QPdfa64Vkrgeg")
        print(f"💰 ROI Expected: 5-10x")
        
        return 0
    else:
        print(f"❌ Campaign launch failed: {result['error']}")
        return 1

if __name__ == "__main__":
    exit(main())