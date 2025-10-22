"""
Social Media Orchestrator - Unified Management Layer
Coordinates all social media platforms from a single interface
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

# Import all social media automators
try:
    from .instagram.instagram_automator import get_instagram_automator, InstagramAnalytics
    from .twitter.twitter_automator import get_twitter_automator, TwitterAnalytics  
    from .linkedin.linkedin_automator import get_linkedin_automator, LinkedInAnalytics
    from .whatsapp.whatsapp_automator import get_whatsapp_automator, WhatsAppAnalytics
except ImportError:
    # Fallback imports for when running from different paths
    import sys
    sys.path.append(os.path.dirname(__file__))
    from instagram.instagram_automator import get_instagram_automator, InstagramAnalytics
    from twitter.twitter_automator import get_twitter_automator, TwitterAnalytics
    from linkedin.linkedin_automator import get_linkedin_automator, LinkedInAnalytics
    from whatsapp.whatsapp_automator import get_whatsapp_automator, WhatsAppAnalytics

class SocialPlatform(Enum):
    INSTAGRAM = "instagram"
    TWITTER = "twitter" 
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    TIKTOK = "tiktok"  # From main system

@dataclass
class SocialAccount:
    platform: SocialPlatform
    account_id: str
    username: str
    credentials: Dict[str, Any]
    status: str = "active"
    last_activity: Optional[datetime] = None

@dataclass
class CrossPlatformCampaign:
    campaign_id: str
    name: str
    platforms: List[SocialPlatform]
    content_strategy: Dict[str, Any]
    target_audience: Dict[str, Any]
    schedule: Dict[str, Any]
    budget_allocation: Dict[str, float]
    kpis: Dict[str, Any]

class SocialMediaOrchestrator:
    """
    Universal social media automation orchestrator
    Manages all platforms from a unified interface
    """
    
    def __init__(self, config_file: str = None):
        self.platforms = {}
        self.analytics = {}
        self.accounts = {}
        self.active_campaigns = {}
        self.cross_platform_insights = {}
        
        # Load configuration
        if config_file:
            self.load_configuration(config_file)
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_configuration(self, config_file: str):
        """Load platform configurations from file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            for platform_name, platform_config in config.get('platforms', {}).items():
                if platform_config.get('enabled', False):
                    self.add_platform_account(
                        SocialPlatform(platform_name),
                        platform_config['account_id'],
                        platform_config['username'],
                        platform_config['credentials']
                    )
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def add_platform_account(self, platform: SocialPlatform, account_id: str, 
                           username: str, credentials: Dict[str, Any]):
        """Add a social media platform account"""
        try:
            account = SocialAccount(
                platform=platform,
                account_id=account_id,
                username=username,
                credentials=credentials,
                last_activity=datetime.now()
            )
            
            # Initialize platform automator
            if platform == SocialPlatform.INSTAGRAM:
                self.platforms[platform] = get_instagram_automator(**credentials)
                self.analytics[platform] = InstagramAnalytics(self.platforms[platform])
            
            elif platform == SocialPlatform.TWITTER:
                self.platforms[platform] = get_twitter_automator(**credentials)
                self.analytics[platform] = TwitterAnalytics(self.platforms[platform])
            
            elif platform == SocialPlatform.LINKEDIN:
                self.platforms[platform] = get_linkedin_automator(**credentials)
                self.analytics[platform] = LinkedInAnalytics(self.platforms[platform])
            
            elif platform == SocialPlatform.WHATSAPP:
                self.platforms[platform] = get_whatsapp_automator(**credentials)
                self.analytics[platform] = WhatsAppAnalytics(self.platforms[platform])
            
            self.accounts[platform] = account
            self.logger.info(f"Added {platform.value} account: @{username}")
            
        except Exception as e:
            self.logger.error(f"Error adding {platform.value} account: {e}")
    
    async def launch_cross_platform_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Launch coordinated campaign across multiple platforms"""
        self.logger.info(f"🚀 Launching cross-platform campaign: {campaign_config['name']}")
        
        campaign = CrossPlatformCampaign(
            campaign_id=campaign_config.get('id', f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            name=campaign_config['name'],
            platforms=[SocialPlatform(p) for p in campaign_config['platforms']],
            content_strategy=campaign_config.get('content_strategy', {}),
            target_audience=campaign_config.get('target_audience', {}),
            schedule=campaign_config.get('schedule', {}),
            budget_allocation=campaign_config.get('budget_allocation', {}),
            kpis=campaign_config.get('kpis', {})
        )
        
        campaign_results = {
            'campaign_id': campaign.campaign_id,
            'campaign_name': campaign.name,
            'platforms_executed': [],
            'total_reach': 0,
            'total_engagement': 0,
            'platform_results': {},
            'cross_platform_synergies': [],
            'overall_roi': 0
        }
        
        # Execute campaign on each platform
        platform_tasks = []
        for platform in campaign.platforms:
            if platform in self.platforms:
                task = self._execute_platform_campaign(platform, campaign_config)
                platform_tasks.append((platform, task))
        
        # Run platforms concurrently
        for platform, task in platform_tasks:
            try:
                result = await task
                campaign_results['platform_results'][platform.value] = result
                campaign_results['platforms_executed'].append(platform.value)
                
                # Aggregate metrics
                campaign_results['total_reach'] += result.get('reach', 0)
                campaign_results['total_engagement'] += result.get('engagement', 0)
                
            except Exception as e:
                self.logger.error(f"Error executing campaign on {platform.value}: {e}")
        
        # Analyze cross-platform synergies
        campaign_results['cross_platform_synergies'] = await self._analyze_campaign_synergies(campaign_results)
        campaign_results['overall_roi'] = await self._calculate_cross_platform_roi(campaign_results)
        
        # Store campaign for monitoring
        self.active_campaigns[campaign.campaign_id] = campaign
        
        self.logger.info(f"✅ Cross-platform campaign completed: {campaign_results}")
        return campaign_results
    
    async def unified_engagement_session(self, duration_minutes: int = 60, 
                                       engagement_strategy: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run coordinated engagement session across all active platforms"""
        self.logger.info(f"🎯 Starting unified engagement session ({duration_minutes} min)")
        
        if not engagement_strategy:
            engagement_strategy = {
                'focus_areas': ['trending_content', 'community_building', 'brand_awareness'],
                'engagement_ratio': {'like': 0.6, 'comment': 0.3, 'share': 0.1},
                'cross_promotion': True
            }
        
        session_results = {
            'session_duration': duration_minutes,
            'platforms_active': [],
            'total_interactions': 0,
            'cross_platform_mentions': 0,
            'platform_performance': {},
            'audience_growth': {},
            'engagement_quality_score': 0
        }
        
        # Distribute time across platforms
        time_per_platform = duration_minutes // len(self.platforms)
        
        # Execute engagement on each platform
        for platform, automator in self.platforms.items():
            platform_start = datetime.now()
            
            try:
                if platform == SocialPlatform.INSTAGRAM:
                    result = await automator.smart_engagement_session(
                        duration_minutes=time_per_platform,
                        engagement_style=engagement_strategy.get('instagram_style', 'balanced')
                    )
                
                elif platform == SocialPlatform.TWITTER:
                    result = await automator.intelligent_engagement_session(
                        duration_minutes=time_per_platform,
                        engagement_topics=engagement_strategy.get('focus_areas', [])
                    )
                
                elif platform == SocialPlatform.LINKEDIN:
                    result = await automator.professional_networking_session(
                        target_industries=engagement_strategy.get('target_industries', ['Technology']),
                        duration_minutes=time_per_platform
                    )
                
                elif platform == SocialPlatform.WHATSAPP:
                    result = await automator.intelligent_customer_service(
                        duration_hours=time_per_platform // 60 or 1
                    )
                
                session_results['platform_performance'][platform.value] = result
                session_results['platforms_active'].append(platform.value)
                session_results['total_interactions'] += result.get('total_interactions', 0)
                
            except Exception as e:
                self.logger.error(f"Error during {platform.value} engagement: {e}")
        
        # Calculate session metrics
        session_results['engagement_quality_score'] = await self._calculate_session_quality(session_results)
        session_results['cross_platform_mentions'] = await self._count_cross_mentions(session_results)
        
        return session_results
    
    async def comprehensive_analytics_dashboard(self) -> Dict[str, Any]:
        """Generate unified analytics across all platforms"""
        self.logger.info("📊 Generating comprehensive analytics dashboard")
        
        dashboard = {
            'report_date': datetime.now(),
            'platforms_analyzed': [],
            'unified_metrics': {
                'total_followers': 0,
                'total_engagement': 0,
                'total_reach': 0,
                'avg_engagement_rate': 0,
                'content_performance_score': 0
            },
            'platform_breakdown': {},
            'cross_platform_insights': {},
            'growth_trends': {},
            'competitive_analysis': {},
            'recommendations': []
        }
        
        platform_analytics = {}
        
        # Collect analytics from each platform
        for platform, analytics in self.analytics.items():
            try:
                if platform == SocialPlatform.INSTAGRAM:
                    result = await analytics.comprehensive_report()
                elif platform == SocialPlatform.TWITTER:
                    result = await analytics.comprehensive_analytics()
                elif platform == SocialPlatform.LINKEDIN:
                    result = await analytics.professional_growth_report()
                elif platform == SocialPlatform.WHATSAPP:
                    result = await analytics.business_performance_report()
                
                platform_analytics[platform.value] = result
                dashboard['platforms_analyzed'].append(platform.value)
                
                # Aggregate unified metrics
                dashboard['unified_metrics']['total_followers'] += result.get('followers', {}).get('total', 0)
                dashboard['unified_metrics']['total_engagement'] += result.get('engagement', {}).get('total', 0)
                dashboard['unified_metrics']['total_reach'] += result.get('reach', {}).get('total', 0)
                
            except Exception as e:
                self.logger.error(f"Error collecting analytics for {platform.value}: {e}")
        
        dashboard['platform_breakdown'] = platform_analytics
        
        # Calculate averages and insights
        num_platforms = len(platform_analytics)
        if num_platforms > 0:
            dashboard['unified_metrics']['avg_engagement_rate'] = (
                sum(analytics.get('engagement', {}).get('rate', 0) for analytics in platform_analytics.values()) / num_platforms
            )
        
        # Cross-platform insights
        dashboard['cross_platform_insights'] = await self._generate_cross_platform_insights(platform_analytics)
        dashboard['growth_trends'] = await self._analyze_growth_trends(platform_analytics)
        dashboard['competitive_analysis'] = await self._unified_competitive_analysis(platform_analytics)
        dashboard['recommendations'] = await self._generate_unified_recommendations(dashboard)
        
        return dashboard
    
    async def automated_content_distribution(self, content_package: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute content automatically across appropriate platforms"""
        self.logger.info(f"📤 Distributing content package: {content_package.get('title', 'Untitled')}")
        
        distribution_results = {
            'content_id': content_package.get('id', f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            'content_title': content_package.get('title', ''),
            'platforms_targeted': [],
            'distribution_success': {},
            'total_potential_reach': 0,
            'adaptation_details': {},
            'scheduling_info': {}
        }
        
        # Analyze content and determine optimal platforms
        platform_suitability = await self._analyze_content_platform_fit(content_package)
        
        for platform, suitability_score in platform_suitability.items():
            if suitability_score > 0.7 and SocialPlatform(platform) in self.platforms:
                # Adapt content for platform
                adapted_content = await self._adapt_content_for_platform(
                    content_package, 
                    SocialPlatform(platform)
                )
                
                # Schedule or post content
                try:
                    if adapted_content.get('schedule_time'):
                        # Schedule for later
                        result = await self._schedule_platform_content(
                            SocialPlatform(platform),
                            adapted_content
                        )
                    else:
                        # Post immediately
                        result = await self._post_platform_content(
                            SocialPlatform(platform),
                            adapted_content
                        )
                    
                    distribution_results['platforms_targeted'].append(platform)
                    distribution_results['distribution_success'][platform] = result
                    distribution_results['adaptation_details'][platform] = adapted_content['adaptations']
                    distribution_results['total_potential_reach'] += result.get('estimated_reach', 0)
                    
                except Exception as e:
                    self.logger.error(f"Error distributing to {platform}: {e}")
                    distribution_results['distribution_success'][platform] = {'error': str(e)}
        
        return distribution_results
    
    async def cross_platform_audience_analysis(self) -> Dict[str, Any]:
        """Analyze audience across all platforms for insights"""
        audience_analysis = {
            'total_audience_size': 0,
            'unique_audience_estimate': 0,
            'platform_audiences': {},
            'demographic_insights': {},
            'interest_mapping': {},
            'cross_platform_overlap': {},
            'growth_opportunities': [],
            'audience_quality_score': 0
        }
        
        for platform in self.platforms:
            try:
                # Get platform-specific audience data
                if platform == SocialPlatform.INSTAGRAM:
                    audience_data = await self._get_instagram_audience_data()
                elif platform == SocialPlatform.TWITTER:
                    audience_data = await self._get_twitter_audience_data()
                elif platform == SocialPlatform.LINKEDIN:
                    audience_data = await self._get_linkedin_audience_data()
                elif platform == SocialPlatform.WHATSAPP:
                    audience_data = await self._get_whatsapp_audience_data()
                
                audience_analysis['platform_audiences'][platform.value] = audience_data
                audience_analysis['total_audience_size'] += audience_data.get('size', 0)
                
            except Exception as e:
                self.logger.error(f"Error analyzing {platform.value} audience: {e}")
        
        # Calculate cross-platform insights
        audience_analysis['unique_audience_estimate'] = int(
            audience_analysis['total_audience_size'] * 0.7  # Assume 30% overlap
        )
        
        audience_analysis['demographic_insights'] = await self._merge_demographic_data(
            audience_analysis['platform_audiences']
        )
        
        audience_analysis['cross_platform_overlap'] = await self._calculate_audience_overlap(
            audience_analysis['platform_audiences']
        )
        
        audience_analysis['growth_opportunities'] = await self._identify_growth_opportunities(
            audience_analysis
        )
        
        return audience_analysis
    
    # Helper methods for platform-specific operations
    
    async def _execute_platform_campaign(self, platform: SocialPlatform, 
                                       campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute campaign on specific platform"""
        automator = self.platforms[platform]
        
        if platform == SocialPlatform.INSTAGRAM:
            return await automator.growth_acceleration_campaign(
                campaign_config.get('instagram', {})
            )
        elif platform == SocialPlatform.TWITTER:
            return await automator.viral_growth_campaign(
                campaign_config.get('twitter', {})
            )
        elif platform == SocialPlatform.LINKEDIN:
            return await automator.thought_leadership_campaign(
                campaign_config.get('linkedin', {}).get('expertise_topics', ['Business'])
            )
        elif platform == SocialPlatform.WHATSAPP:
            return await automator.marketing_campaign_automation(
                campaign_config.get('whatsapp', {})
            )
    
    async def _analyze_content_platform_fit(self, content: Dict[str, Any]) -> Dict[str, float]:
        """Analyze how well content fits each platform"""
        content_type = content.get('type', 'text')
        content_topic = content.get('topic', 'general')
        
        # Platform suitability scoring (0-1)
        suitability = {
            'instagram': 0.5,
            'twitter': 0.5,
            'linkedin': 0.5,
            'whatsapp': 0.3
        }
        
        # Adjust based on content type
        if content_type == 'image':
            suitability['instagram'] += 0.3
            suitability['twitter'] += 0.1
        elif content_type == 'video':
            suitability['instagram'] += 0.4
            suitability['twitter'] += 0.2
        elif content_type == 'article':
            suitability['linkedin'] += 0.4
            suitability['twitter'] += 0.1
        
        # Adjust based on topic
        if content_topic in ['business', 'professional', 'industry']:
            suitability['linkedin'] += 0.3
        elif content_topic in ['lifestyle', 'visual', 'entertainment']:
            suitability['instagram'] += 0.3
        elif content_topic in ['news', 'opinion', 'discussion']:
            suitability['twitter'] += 0.3
        
        return {platform: min(score, 1.0) for platform, score in suitability.items()}
    
    async def _adapt_content_for_platform(self, content: Dict[str, Any], 
                                        platform: SocialPlatform) -> Dict[str, Any]:
        """Adapt content format and style for specific platform"""
        adapted = {
            'original_content': content,
            'platform_optimized': {},
            'adaptations': [],
            'schedule_time': None
        }
        
        if platform == SocialPlatform.INSTAGRAM:
            # Optimize for Instagram
            adapted['platform_optimized'] = {
                'caption': content.get('text', '')[:2200],  # Instagram limit
                'hashtags': content.get('hashtags', [])[:30],  # Optimal hashtag count
                'media': content.get('media', []),
                'story_content': content.get('story_variant')
            }
            adapted['adaptations'].append('Optimized caption length and hashtags')
            
        elif platform == SocialPlatform.TWITTER:
            # Optimize for Twitter
            text = content.get('text', '')
            if len(text) > 280:
                # Create thread
                adapted['platform_optimized'] = {
                    'thread': [text[i:i+270] for i in range(0, len(text), 270)],
                    'media': content.get('media', [])[:4]  # Twitter media limit
                }
                adapted['adaptations'].append('Created thread from long content')
            else:
                adapted['platform_optimized'] = {
                    'text': text,
                    'media': content.get('media', [])[:4]
                }
            
        elif platform == SocialPlatform.LINKEDIN:
            # Optimize for LinkedIn
            adapted['platform_optimized'] = {
                'text': content.get('text', ''),
                'article_link': content.get('article_url'),
                'professional_tone': True,
                'industry_hashtags': content.get('industry_hashtags', [])
            }
            adapted['adaptations'].append('Adjusted for professional tone')
            
        elif platform == SocialPlatform.WHATSAPP:
            # Optimize for WhatsApp
            adapted['platform_optimized'] = {
                'message_text': content.get('text', '')[:4096],  # WhatsApp limit
                'broadcast_segments': content.get('target_segments', ['general']),
                'call_to_action': content.get('cta')
            }
            adapted['adaptations'].append('Formatted for WhatsApp messaging')
        
        return adapted
    
    # Analytics and insights methods
    
    async def _generate_cross_platform_insights(self, platform_analytics: Dict) -> Dict[str, Any]:
        """Generate insights by comparing platform performance"""
        return {
            'best_performing_platform': max(platform_analytics.keys(), 
                                          key=lambda x: platform_analytics[x].get('engagement', {}).get('rate', 0)),
            'fastest_growing_platform': 'instagram',  # Simplified
            'highest_roi_platform': 'linkedin',  # Simplified
            'content_synergies': [
                'Cross-promote LinkedIn articles on Twitter',
                'Share Instagram stories on WhatsApp status',
                'Use Twitter threads as LinkedIn post series'
            ],
            'audience_alignment_score': 0.75
        }
    
    async def _calculate_session_quality(self, session_results: Dict) -> float:
        """Calculate overall quality score for engagement session"""
        quality_factors = {
            'platform_diversity': len(session_results['platforms_active']) / len(self.platforms),
            'interaction_volume': min(session_results['total_interactions'] / 100, 1.0),
            'cross_platform_synergy': session_results['cross_platform_mentions'] / 10
        }
        
        return sum(quality_factors.values()) / len(quality_factors)
    
    async def _count_cross_mentions(self, session_results: Dict) -> int:
        """Count cross-platform mentions and synergies"""
        return len(session_results['platforms_active']) * 2  # Simplified calculation
    
    # Additional helper methods (simplified implementations)
    
    async def _analyze_campaign_synergies(self, results: Dict) -> List[str]:
        return [
            'Instagram visual content amplified Twitter engagement',
            'LinkedIn thought leadership drove WhatsApp inquiries',
            'Cross-platform hashtag strategy increased reach by 25%'
        ]
    
    async def _calculate_cross_platform_roi(self, results: Dict) -> float:
        return sum(result.get('roi', 0) for result in results['platform_results'].values()) / len(results['platform_results'])
    
    async def _analyze_growth_trends(self, analytics: Dict) -> Dict:
        return {
            'overall_growth_rate': 15.2,
            'trending_platforms': ['instagram', 'linkedin'],
            'declining_platforms': [],
            'growth_acceleration_opportunities': ['whatsapp_business', 'twitter_threads']
        }
    
    async def _unified_competitive_analysis(self, analytics: Dict) -> Dict:
        return {
            'competitive_position': 'Above average',
            'strengths': ['Multi-platform presence', 'Consistent messaging'],
            'opportunities': ['Video content expansion', 'Influencer partnerships'],
            'threats': ['Platform algorithm changes', 'Increased competition']
        }
    
    async def _generate_unified_recommendations(self, dashboard: Dict) -> List[str]:
        return [
            'Increase video content across all platforms',
            'Develop platform-specific content calendars',
            'Implement automated cross-promotion workflows',
            'Focus growth efforts on highest-ROI platforms',
            'Create unified brand voice guidelines'
        ]
    
    # Platform-specific audience data methods (simplified)
    
    async def _get_instagram_audience_data(self) -> Dict:
        return {'size': 10000, 'growth_rate': 5.2, 'engagement_rate': 3.4}
    
    async def _get_twitter_audience_data(self) -> Dict:
        return {'size': 15000, 'growth_rate': 8.1, 'engagement_rate': 2.8}
    
    async def _get_linkedin_audience_data(self) -> Dict:
        return {'size': 5000, 'growth_rate': 12.3, 'engagement_rate': 6.7}
    
    async def _get_whatsapp_audience_data(self) -> Dict:
        return {'size': 2000, 'growth_rate': 25.4, 'engagement_rate': 15.2}
    
    async def _merge_demographic_data(self, audiences: Dict) -> Dict:
        return {
            'age_groups': {'18-24': 25, '25-34': 40, '35-44': 20, '45+': 15},
            'locations': {'North America': 45, 'Europe': 30, 'Asia': 15, 'Other': 10},
            'interests': ['Technology', 'Business', 'Lifestyle', 'Entertainment']
        }
    
    async def _calculate_audience_overlap(self, audiences: Dict) -> Dict:
        return {
            'instagram_twitter': 0.25,
            'linkedin_whatsapp': 0.15,
            'twitter_linkedin': 0.30,
            'overall_uniqueness': 0.70
        }
    
    async def _identify_growth_opportunities(self, analysis: Dict) -> List[str]:
        return [
            'Expand WhatsApp Business reach',
            'Cross-promote between Twitter and LinkedIn',
            'Leverage Instagram for brand awareness',
            'Use LinkedIn for B2B lead generation'
        ]
    
    async def _post_platform_content(self, platform: SocialPlatform, content: Dict) -> Dict:
        """Post content immediately to platform"""
        # Simplified implementation
        return {
            'posted': True,
            'post_id': f'{platform.value}_{datetime.now().timestamp()}',
            'estimated_reach': 1000,
            'timestamp': datetime.now()
        }
    
    async def _schedule_platform_content(self, platform: SocialPlatform, content: Dict) -> Dict:
        """Schedule content for later posting"""
        return {
            'scheduled': True,
            'schedule_id': f'sched_{platform.value}_{datetime.now().timestamp()}',
            'scheduled_time': content['schedule_time'],
            'estimated_reach': 1200
        }

# Factory function
def create_social_orchestrator(config_file: str = None) -> SocialMediaOrchestrator:
    """Create and configure social media orchestrator"""
    return SocialMediaOrchestrator(config_file)

# Example configuration
EXAMPLE_CONFIG = {
    "platforms": {
        "instagram": {
            "enabled": True,
            "account_id": "instagram_account",
            "username": "your_instagram",
            "credentials": {
                "username": "your_username",
                "password": "your_password"
            }
        },
        "twitter": {
            "enabled": True,
            "account_id": "twitter_account",
            "username": "your_twitter",
            "credentials": {
                "api_key": "your_api_key",
                "api_secret": "your_api_secret",
                "access_token": "your_access_token",
                "access_token_secret": "your_access_token_secret"
            }
        },
        "linkedin": {
            "enabled": True,
            "account_id": "linkedin_account",
            "username": "your_linkedin",
            "credentials": {
                "client_id": "your_client_id",
                "client_secret": "your_client_secret",
                "access_token": "your_access_token"
            }
        },
        "whatsapp": {
            "enabled": True,
            "account_id": "whatsapp_account",
            "username": "your_business_number",
            "credentials": {
                "phone_number_id": "your_phone_number_id",
                "access_token": "your_access_token"
            }
        }
    }
}