"""
Action Generation System
Converts ML insights into specific, executable actions for each social media platform
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
import numpy as np
from abc import ABC, abstractmethod

# Import ML components
try:
    from .cloud_processing import MLInsight, InsightType, MLPrediction
    from .data_acquisition import SocialMetric, MetricType
except ImportError:
    import sys
    sys.path.append('/workspaces/master')
    from ml_core.cloud_processing import MLInsight, InsightType, MLPrediction
    from ml_core.data_acquisition import SocialMetric, MetricType

# Import social extensions
try:
    from social_extensions import SocialPlatform, create_social_orchestrator
except ImportError:
    import sys
    sys.path.append('/workspaces/master')
    from social_extensions import SocialPlatform, create_social_orchestrator

class ActionPriority(Enum):
    CRITICAL = "critical"    # Execute immediately
    HIGH = "high"           # Execute within 15 minutes
    MEDIUM = "medium"       # Execute within 1 hour
    LOW = "low"             # Execute within 24 hours
    SCHEDULED = "scheduled"  # Execute at specific time

class ActionStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"

class ActionCategory(Enum):
    CONTENT_CREATION = "content_creation"
    ENGAGEMENT = "engagement"
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"
    CRISIS_RESPONSE = "crisis_response"
    GROWTH = "growth"
    ANALYTICS = "analytics"

@dataclass
class ExecutableAction:
    action_id: str
    platform: str
    category: ActionCategory
    priority: ActionPriority
    status: ActionStatus
    action_type: str
    parameters: Dict[str, Any]
    expected_outcome: Dict[str, float]
    confidence: float
    created_at: datetime
    scheduled_for: datetime
    expiry_time: datetime
    retry_count: int = 0
    max_retries: int = 3
    execution_duration_estimate: int = 300  # seconds
    dependencies: List[str] = None
    source_insight_id: str = None

@dataclass
class ActionResult:
    action_id: str
    platform: str
    status: ActionStatus
    execution_start: datetime
    execution_end: datetime
    actual_outcome: Dict[str, Any]
    performance_metrics: Dict[str, float]
    error_message: Optional[str] = None
    side_effects: List[Dict[str, Any]] = None

class ActionGenerator:
    """
    Generates executable actions from ML insights for specific platforms
    """
    
    def __init__(self, platform: str):
        self.platform = platform
        self.action_templates = self._load_platform_action_templates()
        self.logger = logging.getLogger(f"{__name__}.ActionGenerator.{platform}")
    
    @abstractmethod
    async def generate_actions_from_insight(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate platform-specific actions from ML insight"""
        pass
    
    def _load_platform_action_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load action templates for the platform"""
        # This would load from configuration or database
        # For now, return platform-specific templates
        return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get default action templates"""
        return {
            "boost_content": {
                "category": ActionCategory.OPTIMIZATION,
                "priority": ActionPriority.HIGH,
                "execution_time": 180,
                "expected_impact": {"engagement_increase": 25.0}
            },
            "create_content": {
                "category": ActionCategory.CONTENT_CREATION,
                "priority": ActionPriority.MEDIUM,
                "execution_time": 600,
                "expected_impact": {"reach_increase": 15.0}
            },
            "engage_audience": {
                "category": ActionCategory.ENGAGEMENT,
                "priority": ActionPriority.HIGH,
                "execution_time": 300,
                "expected_impact": {"engagement_rate_increase": 10.0}
            }
        }

class InstagramActionGenerator(ActionGenerator):
    """Action generator specific to Instagram"""
    
    def __init__(self):
        super().__init__("instagram")
    
    async def generate_actions_from_insight(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate Instagram-specific actions"""
        actions = []
        
        if insight.insight_type == InsightType.VIRAL_POTENTIAL:
            actions.extend(await self._generate_viral_actions(insight))
        elif insight.insight_type == InsightType.ENGAGEMENT_OPPORTUNITY:
            actions.extend(await self._generate_engagement_actions(insight))
        elif insight.insight_type == InsightType.CONTENT_RECOMMENDATION:
            actions.extend(await self._generate_content_actions(insight))
        elif insight.insight_type == InsightType.GROWTH_OPPORTUNITY:
            actions.extend(await self._generate_growth_actions(insight))
        
        return actions
    
    async def _generate_viral_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate actions for viral content opportunities"""
        actions = []
        
        # Boost viral content immediately
        boost_action = ExecutableAction(
            action_id=f"ig_boost_{int(time.time())}",
            platform="instagram",
            category=ActionCategory.OPTIMIZATION,
            priority=ActionPriority.CRITICAL,
            status=ActionStatus.PENDING,
            action_type="boost_story_content",
            parameters={
                "boost_type": "viral_amplification",
                "target_audience": "lookalike_engaged",
                "budget_multiplier": 3.0,
                "duration_hours": 6
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=2),
            expiry_time=datetime.now() + timedelta(hours=4),
            source_insight_id=insight.insight_id
        )
        actions.append(boost_action)
        
        # Cross-promote to Stories
        story_action = ExecutableAction(
            action_id=f"ig_story_{int(time.time())}",
            platform="instagram",
            category=ActionCategory.CONTENT_CREATION,
            priority=ActionPriority.HIGH,
            status=ActionStatus.PENDING,
            action_type="create_story_highlight",
            parameters={
                "content_type": "viral_showcase",
                "include_cta": True,
                "story_duration": 24,
                "add_to_highlights": True
            },
            expected_outcome={"story_views": 2000, "profile_visits": 300},
            confidence=0.8,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=10),
            expiry_time=datetime.now() + timedelta(hours=2),
            source_insight_id=insight.insight_id
        )
        actions.append(story_action)
        
        return actions
    
    async def _generate_engagement_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate engagement optimization actions"""
        actions = []
        
        # Increase engagement activity
        engage_action = ExecutableAction(
            action_id=f"ig_engage_{int(time.time())}",
            platform="instagram",
            category=ActionCategory.ENGAGEMENT,
            priority=ActionPriority.HIGH,
            status=ActionStatus.PENDING,
            action_type="smart_engagement_session",
            parameters={
                "duration_minutes": 45,
                "engagement_style": "aggressive",
                "target_hashtags": ["#trending", "#viral"],
                "interaction_types": ["like", "comment", "follow"]
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=5),
            expiry_time=datetime.now() + timedelta(hours=6),
            source_insight_id=insight.insight_id
        )
        actions.append(engage_action)
        
        return actions
    
    async def _generate_content_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate content creation actions"""
        actions = []
        
        # Create optimized content
        content_action = ExecutableAction(
            action_id=f"ig_content_{int(time.time())}",
            platform="instagram",
            category=ActionCategory.CONTENT_CREATION,
            priority=ActionPriority.MEDIUM,
            status=ActionStatus.PENDING,
            action_type="create_optimized_post",
            parameters={
                "content_theme": "trending_topic",
                "post_type": "carousel",
                "hashtag_strategy": "trending_mix",
                "posting_time": "optimal",
                "include_cta": True
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(hours=2),
            expiry_time=datetime.now() + timedelta(hours=24),
            source_insight_id=insight.insight_id
        )
        actions.append(content_action)
        
        return actions
    
    async def _generate_growth_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate growth optimization actions"""
        actions = []
        
        # Growth acceleration campaign
        growth_action = ExecutableAction(
            action_id=f"ig_growth_{int(time.time())}",
            platform="instagram",
            category=ActionCategory.GROWTH,
            priority=ActionPriority.MEDIUM,
            status=ActionStatus.PENDING,
            action_type="growth_acceleration_campaign",
            parameters={
                "target_audience": {"age_range": "18-35", "interests": ["technology"]},
                "daily_interactions": 400,
                "growth_rate_target": 12.0,
                "campaign_duration": 7
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=30),
            expiry_time=datetime.now() + timedelta(days=1),
            source_insight_id=insight.insight_id
        )
        actions.append(growth_action)
        
        return actions

class TwitterActionGenerator(ActionGenerator):
    """Action generator specific to Twitter"""
    
    def __init__(self):
        super().__init__("twitter")
    
    async def generate_actions_from_insight(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate Twitter-specific actions"""
        actions = []
        
        if insight.insight_type == InsightType.VIRAL_POTENTIAL:
            actions.extend(await self._generate_viral_twitter_actions(insight))
        elif insight.insight_type == InsightType.TREND_ALERT:
            actions.extend(await self._generate_trending_actions(insight))
        elif insight.insight_type == InsightType.ENGAGEMENT_OPPORTUNITY:
            actions.extend(await self._generate_twitter_engagement_actions(insight))
        
        return actions
    
    async def _generate_viral_twitter_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate actions for viral Twitter opportunities"""
        actions = []
        
        # Create viral thread
        thread_action = ExecutableAction(
            action_id=f"tw_thread_{int(time.time())}",
            platform="twitter",
            category=ActionCategory.CONTENT_CREATION,
            priority=ActionPriority.CRITICAL,
            status=ActionStatus.PENDING,
            action_type="create_viral_thread",
            parameters={
                "thread_length": 8,
                "topic": "trending_insight",
                "include_media": True,
                "engagement_hooks": ["question", "poll", "cta"],
                "hashtag_strategy": "viral_trending"
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=3),
            expiry_time=datetime.now() + timedelta(hours=2),
            source_insight_id=insight.insight_id
        )
        actions.append(thread_action)
        
        return actions
    
    async def _generate_trending_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate actions for trending topics"""
        actions = []
        
        # Trend participation
        trend_action = ExecutableAction(
            action_id=f"tw_trend_{int(time.time())}",
            platform="twitter",
            category=ActionCategory.ENGAGEMENT,
            priority=ActionPriority.HIGH,
            status=ActionStatus.PENDING,
            action_type="participate_in_trend",
            parameters={
                "trending_hashtags": ["#trending1", "#trending2"],
                "content_angle": "expert_opinion",
                "engagement_level": "high",
                "retweet_strategy": "selective"
            },
            expected_outcome={"tweet_impressions": 5000, "profile_visits": 200},
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=5),
            expiry_time=datetime.now() + timedelta(hours=4),
            source_insight_id=insight.insight_id
        )
        actions.append(trend_action)
        
        return actions
    
    async def _generate_twitter_engagement_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate Twitter engagement actions"""
        actions = []
        
        # Intelligent engagement session
        engagement_action = ExecutableAction(
            action_id=f"tw_engage_{int(time.time())}",
            platform="twitter",
            category=ActionCategory.ENGAGEMENT,
            priority=ActionPriority.HIGH,
            status=ActionStatus.PENDING,
            action_type="intelligent_engagement_session",
            parameters={
                "duration_minutes": 30,
                "engagement_topics": ["AI", "technology", "innovation"],
                "interaction_types": ["reply", "retweet", "quote_tweet"],
                "target_accounts": ["industry_leaders", "potential_followers"]
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=10),
            expiry_time=datetime.now() + timedelta(hours=4),
            source_insight_id=insight.insight_id
        )
        actions.append(engagement_action)
        
        return actions

class LinkedInActionGenerator(ActionGenerator):
    """Action generator specific to LinkedIn"""
    
    def __init__(self):
        super().__init__("linkedin")
    
    async def generate_actions_from_insight(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate LinkedIn-specific actions"""
        actions = []
        
        if insight.insight_type == InsightType.ENGAGEMENT_OPPORTUNITY:
            actions.extend(await self._generate_professional_engagement_actions(insight))
        elif insight.insight_type == InsightType.GROWTH_OPPORTUNITY:
            actions.extend(await self._generate_networking_actions(insight))
        elif insight.insight_type == InsightType.CONTENT_RECOMMENDATION:
            actions.extend(await self._generate_thought_leadership_actions(insight))
        
        return actions
    
    async def _generate_professional_engagement_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate professional engagement actions"""
        actions = []
        
        # Professional networking session
        network_action = ExecutableAction(
            action_id=f"li_network_{int(time.time())}",
            platform="linkedin",
            category=ActionCategory.ENGAGEMENT,
            priority=ActionPriority.HIGH,
            status=ActionStatus.PENDING,
            action_type="professional_networking_session",
            parameters={
                "target_industries": ["Technology", "Marketing"],
                "duration_minutes": 45,
                "connection_limit": 15,
                "engagement_style": "professional"
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=15),
            expiry_time=datetime.now() + timedelta(hours=8),
            source_insight_id=insight.insight_id
        )
        actions.append(network_action)
        
        return actions
    
    async def _generate_networking_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate networking and lead generation actions"""
        actions = []
        
        # B2B lead generation
        lead_action = ExecutableAction(
            action_id=f"li_leads_{int(time.time())}",
            platform="linkedin",
            category=ActionCategory.GROWTH,
            priority=ActionPriority.MEDIUM,
            status=ActionStatus.PENDING,
            action_type="b2b_lead_generation",
            parameters={
                "target_companies": ["Fortune 500", "Tech Startups"],
                "job_titles": ["Director", "VP", "Manager"],
                "outreach_strategy": "value_first",
                "daily_limit": 10
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(hours=1),
            expiry_time=datetime.now() + timedelta(days=1),
            source_insight_id=insight.insight_id
        )
        actions.append(lead_action)
        
        return actions
    
    async def _generate_thought_leadership_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate thought leadership content actions"""
        actions = []
        
        # Thought leadership campaign
        thought_action = ExecutableAction(
            action_id=f"li_thought_{int(time.time())}",
            platform="linkedin",
            category=ActionCategory.CONTENT_CREATION,
            priority=ActionPriority.MEDIUM,
            status=ActionStatus.PENDING,
            action_type="thought_leadership_campaign",
            parameters={
                "expertise_topics": ["AI", "Business Strategy", "Innovation"],
                "content_types": ["insights", "predictions", "analysis"],
                "posting_schedule": "3x_per_week",
                "engagement_strategy": "discussion_starter"
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(hours=4),
            expiry_time=datetime.now() + timedelta(days=7),
            source_insight_id=insight.insight_id
        )
        actions.append(thought_action)
        
        return actions

class WhatsAppActionGenerator(ActionGenerator):
    """Action generator specific to WhatsApp Business"""
    
    def __init__(self):
        super().__init__("whatsapp")
    
    async def generate_actions_from_insight(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate WhatsApp-specific actions"""
        actions = []
        
        if insight.insight_type == InsightType.ENGAGEMENT_OPPORTUNITY:
            actions.extend(await self._generate_customer_service_actions(insight))
        elif insight.insight_type == InsightType.GROWTH_OPPORTUNITY:
            actions.extend(await self._generate_marketing_actions(insight))
        elif insight.insight_type == InsightType.ANOMALY_WARNING:
            actions.extend(await self._generate_crisis_response_actions(insight))
        
        return actions
    
    async def _generate_customer_service_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate customer service optimization actions"""
        actions = []
        
        # Intelligent customer service
        service_action = ExecutableAction(
            action_id=f"wa_service_{int(time.time())}",
            platform="whatsapp",
            category=ActionCategory.ENGAGEMENT,
            priority=ActionPriority.HIGH,
            status=ActionStatus.PENDING,
            action_type="intelligent_customer_service",
            parameters={
                "duration_hours": 4,
                "response_time_target": 30,  # seconds
                "automation_level": "high",
                "escalation_threshold": 3
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=5),
            expiry_time=datetime.now() + timedelta(hours=12),
            source_insight_id=insight.insight_id
        )
        actions.append(service_action)
        
        return actions
    
    async def _generate_marketing_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate marketing campaign actions"""
        actions = []
        
        # Marketing campaign
        marketing_action = ExecutableAction(
            action_id=f"wa_marketing_{int(time.time())}",
            platform="whatsapp",
            category=ActionCategory.GROWTH,
            priority=ActionPriority.MEDIUM,
            status=ActionStatus.PENDING,
            action_type="marketing_campaign_automation",
            parameters={
                "campaign_type": "engagement_boost",
                "target_segments": ["active_customers", "at_risk_customers"],
                "message_personalization": "high",
                "campaign_duration": 7
            },
            expected_outcome=insight.expected_impact,
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(hours=2),
            expiry_time=datetime.now() + timedelta(days=1),
            source_insight_id=insight.insight_id
        )
        actions.append(marketing_action)
        
        return actions
    
    async def _generate_crisis_response_actions(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate crisis response actions"""
        actions = []
        
        # Crisis response
        crisis_action = ExecutableAction(
            action_id=f"wa_crisis_{int(time.time())}",
            platform="whatsapp",
            category=ActionCategory.CRISIS_RESPONSE,
            priority=ActionPriority.CRITICAL,
            status=ActionStatus.PENDING,
            action_type="crisis_communication",
            parameters={
                "communication_type": "proactive_outreach",
                "target_audience": "all_customers",
                "message_tone": "reassuring",
                "follow_up_schedule": "24h_48h_72h"
            },
            expected_outcome={"customer_retention": 95.0, "satisfaction_recovery": 80.0},
            confidence=insight.confidence,
            created_at=datetime.now(),
            scheduled_for=datetime.now() + timedelta(minutes=1),
            expiry_time=datetime.now() + timedelta(hours=6),
            source_insight_id=insight.insight_id
        )
        actions.append(crisis_action)
        
        return actions

class UniversalActionGenerationSystem:
    """
    Universal Action Generation System that coordinates action generation across all platforms
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Platform action generators
        self.action_generators = {
            "instagram": InstagramActionGenerator(),
            "twitter": TwitterActionGenerator(),
            "linkedin": LinkedInActionGenerator(),
            "whatsapp": WhatsAppActionGenerator()
        }
        
        # Action management
        self.pending_actions = []
        self.executing_actions = []
        self.completed_actions = []
        self.failed_actions = []
        
        # Execution management
        self.max_concurrent_actions = self.config.get('max_concurrent_actions', 10)
        self.action_timeout = self.config.get('action_timeout', 1800)  # 30 minutes
        self.retry_delays = [30, 300, 900]  # 30s, 5m, 15m
        
        # Performance tracking
        self.execution_metrics = {
            'total_actions_generated': 0,
            'total_actions_executed': 0,
            'success_rate': 0.0,
            'avg_execution_time': 0.0,
            'platform_performance': {}
        }
        
        # Execution state
        self.is_executing = False
        self.execution_tasks = []
        
        self.logger.info("⚡ Universal Action Generation System initialized")
    
    async def initialize(self):
        """Initialize the action generation system"""
        self.logger.info("🚀 Initializing Universal Action Generation System...")
        
        # Initialize platform generators
        for platform, generator in self.action_generators.items():
            self.execution_metrics['platform_performance'][platform] = {
                'actions_generated': 0,
                'actions_executed': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0
            }
        
        self.logger.info("✅ Universal Action Generation System ready!")
    
    async def generate_actions_from_insight(self, insight: MLInsight) -> List[ExecutableAction]:
        """Generate actions from ML insight for all affected platforms"""
        all_actions = []
        
        for platform in insight.platforms_affected:
            if platform in self.action_generators:
                try:
                    generator = self.action_generators[platform]
                    platform_actions = await generator.generate_actions_from_insight(insight)
                    
                    # Add platform-specific metadata
                    for action in platform_actions:
                        action.source_insight_id = insight.insight_id
                        self._apply_global_action_policies(action)
                    
                    all_actions.extend(platform_actions)
                    
                    self.execution_metrics['platform_performance'][platform]['actions_generated'] += len(platform_actions)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error generating actions for {platform}: {e}")
        
        # Sort actions by priority and confidence
        all_actions.sort(key=lambda x: (x.priority.value, -x.confidence))
        
        # Add to pending actions
        self.pending_actions.extend(all_actions)
        
        self.execution_metrics['total_actions_generated'] += len(all_actions)
        
        self.logger.info(f"⚡ Generated {len(all_actions)} actions from insight {insight.insight_id}")
        return all_actions
    
    async def generate_immediate_actions(self, insights: List[MLInsight]) -> List[ExecutableAction]:
        """Generate immediate actions from multiple insights"""
        all_actions = []
        
        for insight in insights:
            actions = await self.generate_actions_from_insight(insight)
            all_actions.extend(actions)
        
        # Filter for immediate execution (Critical and High priority)
        immediate_actions = [
            action for action in all_actions
            if action.priority in [ActionPriority.CRITICAL, ActionPriority.HIGH]
        ]
        
        return immediate_actions
    
    async def start_action_execution_engine(self):
        """Start the action execution engine"""
        if self.is_executing:
            self.logger.warning("⚠️ Action execution engine already running")
            return
        
        self.logger.info("🔄 Starting action execution engine...")
        self.is_executing = True
        
        # Start execution loop
        execution_task = asyncio.create_task(self._action_execution_loop())
        self.execution_tasks.append(execution_task)
        
        # Start monitoring task
        monitoring_task = asyncio.create_task(self._execution_monitoring_loop())
        self.execution_tasks.append(monitoring_task)
        
        # Start cleanup task
        cleanup_task = asyncio.create_task(self._action_cleanup_loop())
        self.execution_tasks.append(cleanup_task)
    
    async def stop_action_execution_engine(self):
        """Stop the action execution engine"""
        self.logger.info("🛑 Stopping action execution engine...")
        self.is_executing = False
        
        # Cancel all execution tasks
        for task in self.execution_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.execution_tasks.clear()
        
        # Cancel executing actions
        for action in self.executing_actions:
            action.status = ActionStatus.CANCELLED
        
        self.logger.info("✅ Action execution engine stopped")
    
    async def execute_action_immediately(self, action: ExecutableAction) -> ActionResult:
        """Execute a single action immediately"""
        self.logger.info(f"🎯 Executing action immediately: {action.action_id} on {action.platform}")
        
        action.status = ActionStatus.EXECUTING
        execution_start = datetime.now()
        
        try:
            # Get platform executor
            executor = await self._get_platform_executor(action.platform)
            
            # Execute the action
            result = await executor.execute_action(action)
            
            execution_end = datetime.now()
            execution_time = (execution_end - execution_start).total_seconds()
            
            # Create action result
            action_result = ActionResult(
                action_id=action.action_id,
                platform=action.platform,
                status=ActionStatus.COMPLETED,
                execution_start=execution_start,
                execution_end=execution_end,
                actual_outcome=result.get('outcome', {}),
                performance_metrics=result.get('metrics', {}),
                side_effects=result.get('side_effects', [])
            )
            
            action.status = ActionStatus.COMPLETED
            
            # Update metrics
            await self._update_execution_metrics(action.platform, execution_time, True)
            
            self.logger.info(f"✅ Action {action.action_id} completed in {execution_time:.2f}s")
            return action_result
            
        except Exception as e:
            execution_end = datetime.now()
            execution_time = (execution_end - execution_start).total_seconds()
            
            # Create failure result
            action_result = ActionResult(
                action_id=action.action_id,
                platform=action.platform,
                status=ActionStatus.FAILED,
                execution_start=execution_start,
                execution_end=execution_end,
                actual_outcome={},
                performance_metrics={},
                error_message=str(e)
            )
            
            action.status = ActionStatus.FAILED
            action.retry_count += 1
            
            # Update metrics
            await self._update_execution_metrics(action.platform, execution_time, False)
            
            self.logger.error(f"❌ Action {action.action_id} failed: {e}")
            return action_result
    
    async def get_action_status(self, action_id: str) -> Optional[ExecutableAction]:
        """Get status of specific action"""
        # Search in all action lists
        all_actions = self.pending_actions + self.executing_actions + self.completed_actions + self.failed_actions
        
        for action in all_actions:
            if action.action_id == action_id:
                return action
        
        return None
    
    async def get_execution_metrics(self) -> Dict[str, Any]:
        """Get execution performance metrics"""
        return {
            'system_metrics': self.execution_metrics.copy(),
            'queue_status': {
                'pending_actions': len(self.pending_actions),
                'executing_actions': len(self.executing_actions),
                'completed_actions': len(self.completed_actions),
                'failed_actions': len(self.failed_actions)
            },
            'execution_state': {
                'is_executing': self.is_executing,
                'max_concurrent': self.max_concurrent_actions,
                'current_concurrent': len(self.executing_actions)
            },
            'platform_breakdown': {
                platform: {
                    'pending': len([a for a in self.pending_actions if a.platform == platform]),
                    'executing': len([a for a in self.executing_actions if a.platform == platform]),
                    'completed_today': len([
                        a for a in self.completed_actions 
                        if a.platform == platform and a.created_at.date() == datetime.now().date()
                    ])
                }
                for platform in self.action_generators.keys()
            }
        }
    
    # Private methods for action execution
    
    async def _action_execution_loop(self):
        """Main action execution loop"""
        while self.is_executing:
            try:
                # Get actions ready for execution
                ready_actions = await self._get_ready_actions()
                
                if ready_actions and len(self.executing_actions) < self.max_concurrent_actions:
                    # Select actions to execute
                    slots_available = self.max_concurrent_actions - len(self.executing_actions)
                    actions_to_execute = ready_actions[:slots_available]
                    
                    # Execute actions concurrently
                    execution_tasks = []
                    for action in actions_to_execute:
                        task = asyncio.create_task(self._execute_single_action(action))
                        execution_tasks.append(task)
                        
                        # Move to executing list
                        if action in self.pending_actions:
                            self.pending_actions.remove(action)
                        self.executing_actions.append(action)
                    
                    # Wait for any execution to complete
                    if execution_tasks:
                        done, pending = await asyncio.wait(
                            execution_tasks, 
                            return_when=asyncio.FIRST_COMPLETED,
                            timeout=30
                        )
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in action execution loop: {e}")
                await asyncio.sleep(30)
    
    async def _execute_single_action(self, action: ExecutableAction):
        """Execute a single action with error handling and retries"""
        max_attempts = action.max_retries + 1
        
        for attempt in range(max_attempts):
            try:
                result = await self.execute_action_immediately(action)
                
                # Move to completed list
                if action in self.executing_actions:
                    self.executing_actions.remove(action)
                self.completed_actions.append(action)
                
                return result
                
            except Exception as e:
                self.logger.error(f"❌ Attempt {attempt + 1} failed for action {action.action_id}: {e}")
                
                if attempt < max_attempts - 1:
                    # Wait before retry
                    retry_delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(retry_delay)
                else:
                    # Final failure
                    action.status = ActionStatus.FAILED
                    
                    if action in self.executing_actions:
                        self.executing_actions.remove(action)
                    self.failed_actions.append(action)
    
    async def _get_ready_actions(self) -> List[ExecutableAction]:
        """Get actions ready for execution"""
        now = datetime.now()
        
        ready_actions = []
        for action in self.pending_actions:
            # Check if action is ready to execute
            if action.scheduled_for <= now and action.expiry_time > now:
                # Check dependencies
                if await self._check_action_dependencies(action):
                    ready_actions.append(action)
        
        # Sort by priority
        ready_actions.sort(key=lambda x: (x.priority.value, -x.confidence))
        
        return ready_actions
    
    async def _check_action_dependencies(self, action: ExecutableAction) -> bool:
        """Check if action dependencies are satisfied"""
        if not action.dependencies:
            return True
        
        for dependency_id in action.dependencies:
            dependency_action = await self.get_action_status(dependency_id)
            if not dependency_action or dependency_action.status != ActionStatus.COMPLETED:
                return False
        
        return True
    
    async def _get_platform_executor(self, platform: str):
        """Get executor for specific platform"""
        # This would return the actual platform automator
        # For now, return a dummy executor
        return DummyPlatformExecutor(platform)
    
    async def _execution_monitoring_loop(self):
        """Monitor action execution and handle timeouts"""
        while self.is_executing:
            try:
                now = datetime.now()
                
                # Check for timed out actions
                timed_out_actions = []
                for action in self.executing_actions:
                    execution_time = (now - action.scheduled_for).total_seconds()
                    if execution_time > self.action_timeout:
                        timed_out_actions.append(action)
                
                # Handle timeouts
                for action in timed_out_actions:
                    self.logger.warning(f"⏰ Action {action.action_id} timed out")
                    action.status = ActionStatus.FAILED
                    self.executing_actions.remove(action)
                    self.failed_actions.append(action)
                
                # Check for expired actions
                expired_actions = []
                for action in self.pending_actions:
                    if action.expiry_time <= now:
                        expired_actions.append(action)
                
                # Remove expired actions
                for action in expired_actions:
                    self.logger.info(f"⏰ Action {action.action_id} expired")
                    action.status = ActionStatus.CANCELLED
                    self.pending_actions.remove(action)
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in execution monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _action_cleanup_loop(self):
        """Clean up old completed and failed actions"""
        while self.is_executing:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up old actions (keep last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                self.completed_actions = [
                    action for action in self.completed_actions
                    if action.created_at >= cutoff_time
                ]
                
                self.failed_actions = [
                    action for action in self.failed_actions
                    if action.created_at >= cutoff_time
                ]
                
                self.logger.info(f"🧹 Cleaned up old actions - Completed: {len(self.completed_actions)}, Failed: {len(self.failed_actions)}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in action cleanup: {e}")
    
    def _apply_global_action_policies(self, action: ExecutableAction):
        """Apply global policies to actions"""
        # Rate limiting per platform
        platform_actions_today = len([
            a for a in self.completed_actions + self.executing_actions + self.pending_actions
            if a.platform == action.platform and a.created_at.date() == datetime.now().date()
        ])
        
        max_daily_actions = self.config.get('max_daily_actions_per_platform', 100)
        
        if platform_actions_today >= max_daily_actions:
            # Downgrade priority or schedule for tomorrow
            action.priority = ActionPriority.LOW
            action.scheduled_for = datetime.now() + timedelta(days=1)
    
    async def _update_execution_metrics(self, platform: str, execution_time: float, success: bool):
        """Update execution performance metrics"""
        platform_metrics = self.execution_metrics['platform_performance'][platform]
        
        platform_metrics['actions_executed'] += 1
        self.execution_metrics['total_actions_executed'] += 1
        
        if success:
            # Update success rate
            total_executed = platform_metrics['actions_executed']
            current_success_rate = platform_metrics['success_rate']
            platform_metrics['success_rate'] = ((current_success_rate * (total_executed - 1)) + 1) / total_executed
            
            # Update execution time
            current_avg_time = platform_metrics['avg_execution_time']
            platform_metrics['avg_execution_time'] = ((current_avg_time * (total_executed - 1)) + execution_time) / total_executed
        
        # Update global success rate
        total_executed = self.execution_metrics['total_actions_executed']
        if total_executed > 0:
            successful_actions = sum([
                perf['actions_executed'] * perf['success_rate']
                for perf in self.execution_metrics['platform_performance'].values()
            ])
            self.execution_metrics['success_rate'] = successful_actions / total_executed
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for action generation system"""
        logger = logging.getLogger(f"{__name__}.ActionGenerationSystem")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

# Dummy platform executor for testing
class DummyPlatformExecutor:
    """Dummy platform executor for testing action execution"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.logger = logging.getLogger(f"{__name__}.DummyExecutor.{platform}")
    
    async def execute_action(self, action: ExecutableAction) -> Dict[str, Any]:
        """Execute action (dummy implementation)"""
        self.logger.info(f"🎭 DUMMY: Executing {action.action_type} on {self.platform}")
        
        # Simulate execution time
        await asyncio.sleep(np.random.uniform(1, 5))
        
        # Simulate success/failure
        success = np.random.random() > 0.1  # 90% success rate
        
        if success:
            return {
                'status': 'success',
                'outcome': {
                    'engagement_increase': np.random.uniform(5.0, 25.0),
                    'reach_increase': np.random.uniform(10.0, 50.0)
                },
                'metrics': {
                    'execution_time': np.random.uniform(1, 5),
                    'success_score': np.random.uniform(0.8, 1.0)
                },
                'side_effects': []
            }
        else:
            raise Exception(f"Simulated execution failure for {action.action_type}")

# Factory function
def create_action_generation_system(config: Dict[str, Any] = None) -> UniversalActionGenerationSystem:
    """Create and return a configured action generation system"""
    return UniversalActionGenerationSystem(config)