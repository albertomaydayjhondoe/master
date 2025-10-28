"""Action Generation Framework - Core Components"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import logging

from ..config.app_settings import is_dummy_mode

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be generated"""
    POST = "post"
    COMMENT = "comment"
    LIKE = "like"
    SHARE = "share"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    MESSAGE = "message"
    STORY = "story"
    REEL = "reel"
    ADS = "ads"
    TARGETING = "targeting"
    BUDGET = "budget"
    SCHEDULE = "schedule"


class ActionPriority(Enum):
    """Priority levels for generated actions"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class ActionContext:
    """Context information for action generation"""
    platform: str
    account_id: str
    user_data: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    current_trends: Dict[str, Any]
    constraints: Dict[str, Any]
    target_audience: Optional[Dict[str, Any]] = None
    campaign_goals: Optional[Dict[str, Any]] = None
    time_window: Optional[Dict[str, Any]] = None


@dataclass
class ActionRequest:
    """Request for action generation"""
    context: ActionContext
    action_types: List[ActionType]
    max_actions: int = 10
    priority_filter: Optional[ActionPriority] = None
    time_horizon: Optional[int] = 24  # hours
    ml_confidence_threshold: float = 0.7
    custom_parameters: Optional[Dict[str, Any]] = None


@dataclass
class GeneratedAction:
    """A generated action with ML insights"""
    action_id: str
    action_type: ActionType
    priority: ActionPriority
    confidence: float
    platform: str
    account_id: str
    
    # Action details
    content: Dict[str, Any]
    timing: Dict[str, Any]
    
    # ML insights
    predicted_performance: Dict[str, float]
    risk_factors: List[str]
    optimization_suggestions: List[str]
    
    # Metadata
    generated_at: datetime
    
    # Optional fields with defaults
    targeting: Optional[Dict[str, Any]] = None
    budget_info: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class ActionGenerator(ABC):
    """Abstract base class for action generators"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate_actions(self, request: ActionRequest) -> List[GeneratedAction]:
        """Generate actions based on the request"""
        pass
    
    @abstractmethod
    async def validate_action(self, action: GeneratedAction) -> bool:
        """Validate if an action can be executed"""
        pass
    
    @abstractmethod
    async def estimate_performance(self, action: GeneratedAction) -> Dict[str, float]:
        """Estimate action performance metrics"""
        pass


class DummyActionGenerator(ActionGenerator):
    """Dummy implementation for testing and development"""
    
    def __init__(self, platform: str = "dummy"):
        super().__init__(platform)
        self.logger.info("Initialized DummyActionGenerator")
    
    async def generate_actions(self, request: ActionRequest) -> List[GeneratedAction]:
        """Generate dummy actions for testing"""
        actions = []
        
        for i, action_type in enumerate(request.action_types[:request.max_actions]):
            action = GeneratedAction(
                action_id=f"dummy_action_{i}_{datetime.now().timestamp()}",
                action_type=action_type,
                priority=ActionPriority.MEDIUM,
                confidence=0.8,
                platform=self.platform,
                account_id=request.context.account_id,
                content={
                    "text": f"Dummy {action_type.value} content",
                    "media": [],
                    "hashtags": ["#dummy", f"#{action_type.value}"]
                },
                timing={
                    "scheduled_for": datetime.now().isoformat(),
                    "optimal_hour": 12,
                    "day_of_week": "monday"
                },
                predicted_performance={
                    "engagement_rate": 0.05,
                    "reach": 1000,
                    "conversion_rate": 0.02
                },
                risk_factors=["low_engagement_risk"],
                optimization_suggestions=["Add trending hashtags", "Post during peak hours"],
                generated_at=datetime.now()
            )
            actions.append(action)
        
        self.logger.info(f"Generated {len(actions)} dummy actions")
        return actions
    
    async def validate_action(self, action: GeneratedAction) -> bool:
        """Always validate dummy actions as true"""
        return True
    
    async def estimate_performance(self, action: GeneratedAction) -> Dict[str, float]:
        """Return dummy performance estimates"""
        return {
            "engagement_rate": 0.05,
            "reach": 1000.0,
            "conversion_rate": 0.02,
            "cost_per_click": 0.5,
            "roi": 2.5
        }


def get_action_generator(platform: str) -> ActionGenerator:
    """Factory function to get appropriate action generator"""
    if is_dummy_mode():
        return DummyActionGenerator(platform)
    else:
        # In production, return platform-specific generators
        # This would be implemented based on the platform
        raise NotImplementedError(f"Production action generator for {platform} not implemented")


# Utility functions for action generation
async def batch_generate_actions(
    generators: List[ActionGenerator], 
    requests: List[ActionRequest]
) -> Dict[str, List[GeneratedAction]]:
    """Generate actions from multiple generators in parallel"""
    results = {}
    
    tasks = []
    for generator, request in zip(generators, requests):
        task = asyncio.create_task(generator.generate_actions(request))
        tasks.append((generator.platform, task))
    
    for platform, task in tasks:
        try:
            actions = await task
            results[platform] = actions
        except Exception as e:
            logger.error(f"Error generating actions for {platform}: {e}")
            results[platform] = []
    
    return results


async def filter_actions_by_performance(
    actions: List[GeneratedAction],
    min_confidence: float = 0.7,
    min_predicted_engagement: float = 0.03
) -> List[GeneratedAction]:
    """Filter actions based on performance criteria"""
    filtered = []
    
    for action in actions:
        if (action.confidence >= min_confidence and 
            action.predicted_performance.get('engagement_rate', 0) >= min_predicted_engagement):
            filtered.append(action)
    
    return filtered


def prioritize_actions(actions: List[GeneratedAction]) -> List[GeneratedAction]:
    """Sort actions by priority and confidence"""
    return sorted(
        actions,
        key=lambda x: (x.priority.value, x.confidence),
        reverse=True
    )