"""
Base Social Media Extension Framework
Provides common interfaces and functionality for all social media platforms
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported social media platforms"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    TIKTOK = "tiktok"

class ContentType(Enum):
    """Types of content that can be posted"""
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    POLL = "poll"
    STORY = "story"
    LIVE = "live"

class ActionType(Enum):
    """Types of actions that can be performed"""
    POST = "post"
    COMMENT = "comment"
    LIKE = "like"
    SHARE = "share"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    JOIN = "join"
    LEAVE = "leave"
    MESSAGE = "message"
    SCHEDULE = "schedule"

@dataclass
class SocialMediaAccount:
    """Represents a social media account"""
    platform: PlatformType
    account_id: str
    username: str
    display_name: str
    is_verified: bool = False
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

@dataclass  
class SocialMediaPost:
    """Represents a social media post"""
    platform: PlatformType
    post_id: str
    content: str
    content_type: ContentType
    author_id: str
    created_at: datetime
    media_urls: List[str] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    engagement_rate: float = 0.0

@dataclass
class SocialMediaMetrics:
    """Platform-agnostic metrics"""
    platform: PlatformType
    account_id: str
    date: datetime
    impressions: int = 0
    reach: int = 0
    engagement: int = 0
    clicks: int = 0
    saves: int = 0
    shares: int = 0
    comments: int = 0
    likes: int = 0
    follows: int = 0
    unfollows: int = 0

@dataclass
class OptimizationAction:
    """Represents an optimization action"""
    platform: PlatformType
    action_type: ActionType
    target_id: Optional[str]
    parameters: Dict[str, Any]
    priority: float
    expected_impact: str
    reasoning: str
    created_at: datetime = None
    executed_at: Optional[datetime] = None
    success: Optional[bool] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class BaseSocialAutomator(ABC):
    """Base class for all social media automators"""
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.is_connected = False
        self.account: Optional[SocialMediaAccount] = None
        self.rate_limits: Dict[str, Any] = {}
        self.last_action_time: Dict[ActionType, datetime] = {}
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the platform"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the platform"""
        pass
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Optional[SocialMediaAccount]:
        """Get current account information"""
        pass
    
    @abstractmethod
    async def post_content(
        self,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        media_urls: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[SocialMediaPost]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    async def get_posts(
        self,
        limit: int = 50,
        since: Optional[datetime] = None
    ) -> List[SocialMediaPost]:
        """Get recent posts"""
        pass
    
    @abstractmethod
    async def get_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> SocialMediaMetrics:
        """Get platform metrics"""
        pass
    
    async def check_rate_limits(self, action_type: ActionType) -> bool:
        """Check if action is within rate limits"""
        now = datetime.now()
        last_action = self.last_action_time.get(action_type)
        
        if last_action:
            min_interval = self.rate_limits.get(action_type.value, 1)  # Default 1 second
            time_since_last = (now - last_action).total_seconds()
            
            if time_since_last < min_interval:
                return False
        
        self.last_action_time[action_type] = now
        return True
    
    async def wait_for_rate_limit(self, action_type: ActionType):
        """Wait for rate limit to reset"""
        now = datetime.now()
        last_action = self.last_action_time.get(action_type)
        
        if last_action:
            min_interval = self.rate_limits.get(action_type.value, 1)
            time_since_last = (now - last_action).total_seconds()
            
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                logger.info(f"Rate limit: waiting {wait_time:.1f}s for {action_type.value}")
                await asyncio.sleep(wait_time)

class BaseActionGenerator(ABC):
    """Base class for ML-driven action generators"""
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.optimization_history: List[OptimizationAction] = []
        
    @abstractmethod
    async def analyze_performance(
        self,
        account_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Analyze account performance"""
        pass
    
    @abstractmethod
    async def generate_content_recommendations(
        self,
        target_metrics: Optional[Dict[str, float]] = None,
        content_themes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate content recommendations"""
        pass
    
    @abstractmethod
    async def generate_optimization_actions(
        self,
        current_metrics: SocialMediaMetrics,
        target_metrics: Dict[str, float]
    ) -> List[OptimizationAction]:
        """Generate optimization actions"""
        pass
    
    @abstractmethod
    async def execute_action(self, action: OptimizationAction) -> bool:
        """Execute an optimization action"""
        pass
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights from action history"""
        if not self.optimization_history:
            return {"status": "No optimization data available"}
        
        successful_actions = [a for a in self.optimization_history if a.success]
        success_rate = len(successful_actions) / len(self.optimization_history)
        
        # Group by action type
        action_stats = {}
        for action in self.optimization_history:
            action_type = action.action_type.value
            if action_type not in action_stats:
                action_stats[action_type] = {"total": 0, "successful": 0}
            
            action_stats[action_type]["total"] += 1
            if action.success:
                action_stats[action_type]["successful"] += 1
        
        # Calculate success rates by action type
        for stats in action_stats.values():
            stats["success_rate"] = stats["successful"] / stats["total"]
        
        return {
            "platform": self.platform.value,
            "total_actions": len(self.optimization_history),
            "success_rate": success_rate,
            "action_breakdown": action_stats,
            "last_action": self.optimization_history[-1].created_at.isoformat() if self.optimization_history else None
        }

class BaseMonitor(ABC):
    """Base class for platform monitoring"""
    
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self.is_monitoring = False
        self.alerts: List[Dict[str, Any]] = []
        self.metrics_history: List[SocialMediaMetrics] = []
        
    @abstractmethod
    async def start_monitoring(self):
        """Start monitoring the platform"""
        pass
    
    @abstractmethod
    async def stop_monitoring(self):
        """Stop monitoring the platform"""
        pass
    
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check platform health"""
        pass
    
    @abstractmethod
    async def check_account_health(self, account_id: str) -> Dict[str, Any]:
        """Check specific account health"""
        pass
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Dict[str, Any] = None
    ):
        """Create a monitoring alert"""
        alert = {
            "platform": self.platform.value,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
            "resolved": False
        }
        
        self.alerts.append(alert)
        logger.warning(f"🚨 {self.platform.value} Alert ({severity}): {message}")
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts.pop(0)
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        resolved: bool = False
    ) -> List[Dict[str, Any]]:
        """Get monitoring alerts"""
        filtered_alerts = self.alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]
        
        if not resolved:
            filtered_alerts = [a for a in filtered_alerts if not a["resolved"]]
        
        return filtered_alerts
    
    def resolve_alert(self, alert_index: int) -> bool:
        """Resolve a specific alert"""
        try:
            if 0 <= alert_index < len(self.alerts):
                self.alerts[alert_index]["resolved"] = True
                return True
            return False
        except Exception:
            return False

class CrossPlatformManager:
    """Manages multiple social media platforms"""
    
    def __init__(self):
        self.automators: Dict[PlatformType, BaseSocialAutomator] = {}
        self.action_generators: Dict[PlatformType, BaseActionGenerator] = {}
        self.monitors: Dict[PlatformType, BaseMonitor] = {}
        self.cross_platform_actions: List[OptimizationAction] = []
        
    def register_platform(
        self,
        platform: PlatformType,
        automator: BaseSocialAutomator,
        action_generator: BaseActionGenerator,
        monitor: BaseMonitor
    ):
        """Register a platform with its components"""
        self.automators[platform] = automator
        self.action_generators[platform] = action_generator
        self.monitors[platform] = monitor
        
        logger.info(f"Registered platform: {platform.value}")
    
    async def connect_all(self) -> Dict[PlatformType, bool]:
        """Connect to all registered platforms"""
        results = {}
        
        for platform, automator in self.automators.items():
            try:
                success = await automator.connect()
                results[platform] = success
                logger.info(f"Connection to {platform.value}: {'✅' if success else '❌'}")
            except Exception as e:
                logger.error(f"Failed to connect to {platform.value}: {e}")
                results[platform] = False
        
        return results
    
    async def disconnect_all(self):
        """Disconnect from all platforms"""
        for platform, automator in self.automators.items():
            try:
                await automator.disconnect()
                logger.info(f"Disconnected from {platform.value}")
            except Exception as e:
                logger.error(f"Error disconnecting from {platform.value}: {e}")
    
    async def post_to_multiple_platforms(
        self,
        platforms: List[PlatformType],
        content: str,
        content_type: ContentType = ContentType.TEXT,
        **kwargs
    ) -> Dict[PlatformType, Optional[SocialMediaPost]]:
        """Post content to multiple platforms"""
        results = {}
        
        for platform in platforms:
            automator = self.automators.get(platform)
            if automator and automator.is_connected:
                try:
                    post = await automator.post_content(content, content_type, **kwargs)
                    results[platform] = post
                    logger.info(f"Posted to {platform.value}: {content[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to post to {platform.value}: {e}")
                    results[platform] = None
            else:
                logger.warning(f"Platform {platform.value} not connected")
                results[platform] = None
        
        return results
    
    async def get_cross_platform_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[PlatformType, SocialMediaMetrics]:
        """Get metrics from all platforms"""
        results = {}
        
        for platform, automator in self.automators.items():
            if automator.is_connected:
                try:
                    metrics = await automator.get_metrics(start_date, end_date)
                    results[platform] = metrics
                except Exception as e:
                    logger.error(f"Failed to get metrics from {platform.value}: {e}")
        
        return results
    
    async def generate_cross_platform_strategy(
        self,
        target_metrics: Dict[str, float]
    ) -> List[OptimizationAction]:
        """Generate cross-platform optimization strategy"""
        all_actions = []
        
        for platform, generator in self.action_generators.items():
            automator = self.automators.get(platform)
            
            if automator and automator.is_connected and automator.account:
                try:
                    # Get current metrics
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=7)
                    current_metrics = await automator.get_metrics(start_date, end_date)
                    
                    # Generate platform-specific actions
                    actions = await generator.generate_optimization_actions(
                        current_metrics, target_metrics
                    )
                    all_actions.extend(actions)
                    
                except Exception as e:
                    logger.error(f"Failed to generate actions for {platform.value}: {e}")
        
        # Sort by priority
        all_actions.sort(key=lambda x: x.priority, reverse=True)
        
        # Store cross-platform actions
        self.cross_platform_actions.extend(all_actions)
        
        return all_actions
    
    async def start_all_monitoring(self):
        """Start monitoring on all platforms"""
        for platform, monitor in self.monitors.items():
            try:
                await monitor.start_monitoring()
                logger.info(f"Started monitoring for {platform.value}")
            except Exception as e:
                logger.error(f"Failed to start monitoring for {platform.value}: {e}")
    
    async def stop_all_monitoring(self):
        """Stop monitoring on all platforms"""
        for platform, monitor in self.monitors.items():
            try:
                await monitor.stop_monitoring()
                logger.info(f"Stopped monitoring for {platform.value}")
            except Exception as e:
                logger.error(f"Failed to stop monitoring for {platform.value}: {e}")
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health across all platforms"""
        platform_health = {}
        total_alerts = 0
        
        for platform, monitor in self.monitors.items():
            alerts = monitor.get_alerts()
            platform_health[platform.value] = {
                "connected": self.automators[platform].is_connected,
                "active_alerts": len(alerts),
                "monitoring": monitor.is_monitoring
            }
            total_alerts += len(alerts)
        
        connected_count = sum(1 for h in platform_health.values() if h["connected"])
        monitoring_count = sum(1 for h in platform_health.values() if h["monitoring"])
        
        return {
            "platforms_registered": len(self.automators),
            "platforms_connected": connected_count,
            "platforms_monitoring": monitoring_count,
            "total_active_alerts": total_alerts,
            "platform_status": platform_health,
            "overall_health": "healthy" if connected_count > 0 and total_alerts < 10 else "needs_attention"
        }

# Utility functions
def create_cross_platform_manager() -> CrossPlatformManager:
    """Factory function to create cross-platform manager"""
    return CrossPlatformManager()

def get_supported_platforms() -> List[PlatformType]:
    """Get list of supported platforms"""
    return list(PlatformType)

def get_supported_content_types() -> List[ContentType]:
    """Get list of supported content types"""
    return list(ContentType)

def get_supported_action_types() -> List[ActionType]:
    """Get list of supported action types"""
    return list(ActionType)

# Export all main classes and functions
__all__ = [
    'PlatformType',
    'ContentType', 
    'ActionType',
    'SocialMediaAccount',
    'SocialMediaPost',
    'SocialMediaMetrics',
    'OptimizationAction',
    'BaseSocialAutomator',
    'BaseActionGenerator',
    'BaseMonitor',
    'CrossPlatformManager',
    'create_cross_platform_manager',
    'get_supported_platforms',
    'get_supported_content_types',
    'get_supported_action_types'
]
