"""
Metrics Collector Module
Collects, analyzes, and stores engagement metrics and performance data.
Provides analytics and insights for system optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import statistics

from ..config.telegram_config import TelegramConfig
from ..database.models import EngagementMetric, UserActivity, SystemMetric

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics collected."""
    USER_INTERACTION = "user_interaction"
    TASK_EXECUTION = "task_execution"
    ENGAGEMENT_SUCCESS = "engagement_success"
    SYSTEM_PERFORMANCE = "system_performance"
    VIRAL_DETECTION = "viral_detection"
    PLATFORM_SPECIFIC = "platform_specific"

@dataclass
class MetricData:
    """Container for metric data points."""
    metric_type: MetricType
    user_id: Optional[int]
    platform: Optional[str]
    value: float
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class EngagementStats:
    """Engagement statistics summary."""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    success_rate: float = 0.0
    average_completion_time: timedelta = timedelta(0)
    platform_breakdown: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
@dataclass
class UserStats:
    """User-specific statistics."""
    user_id: int
    total_exchanges: int = 0
    successful_exchanges: int = 0
    received_engagement: int = 0
    given_engagement: int = 0
    reciprocity_ratio: float = 0.0
    favorite_platform: Optional[str] = None
    average_priority: float = 0.0
    join_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    engagement_trend: List[float] = field(default_factory=list)

class MetricsCollector:
    """
    Collects and analyzes system metrics for performance monitoring and optimization.
    Provides real-time analytics and historical trend analysis.
    """
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.is_running = False
        
        # Metric storage
        self.metrics_buffer: deque = deque(maxlen=10000)  # Recent metrics buffer
        self.user_stats_cache: Dict[int, UserStats] = {}
        self.daily_stats: Dict[date, EngagementStats] = {}
        self.platform_metrics: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        # Real-time counters
        self.realtime_counters = {
            'total_users': 0,
            'active_users_today': set(),
            'exchanges_today': 0,
            'successful_exchanges_today': 0,
            'viral_content_detected_today': 0,
            'total_engagement_given': 0,
            'total_engagement_received': 0
        }
        
        # Performance metrics
        self.system_metrics = {
            'cpu_usage': deque(maxlen=100),
            'memory_usage': deque(maxlen=100),
            'response_times': deque(maxlen=100),
            'error_rates': deque(maxlen=100),
            'queue_lengths': deque(maxlen=100)
        }
        
        # Analytics
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # Reporting
        self.last_daily_report = None
        self.last_weekly_report = None
    
    async def initialize(self):
        """Initialize the metrics collector."""
        try:
            logger.info("Initializing metrics collector...")
            
            # Load historical data
            await self._load_historical_metrics()
            
            # Initialize user stats cache
            await self._initialize_user_stats()
            
            # Start background tasks
            self._start_background_tasks()
            
            logger.info("Metrics collector initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics collector: {e}")
            raise
    
    async def _load_historical_metrics(self):
        """Load historical metrics from database."""
        try:
            # This would typically load from database
            # For now, initialize empty structures
            logger.info("Loaded historical metrics data")
            
        except Exception as e:
            logger.warning(f"Could not load historical metrics: {e}")
    
    async def _initialize_user_stats(self):
        """Initialize user statistics cache."""
        try:
            # Load user statistics from database
            self.user_stats_cache = {}
            logger.info("Initialized user statistics cache")
            
        except Exception as e:
            logger.warning(f"Could not initialize user stats: {e}")
    
    def _start_background_tasks(self):
        """Start background metric collection tasks."""
        
        # System metrics collection
        asyncio.create_task(self._collect_system_metrics())
        
        # Daily reset task
        asyncio.create_task(self._daily_reset_task())
        
        # Trend analysis task
        asyncio.create_task(self._trend_analysis_task())
    
    async def track_user_interaction(self, user_id: int, interaction_type: str, metadata: Optional[Dict[str, Any]] = None):
        """Track user interaction with the bot."""
        
        metric = MetricData(
            metric_type=MetricType.USER_INTERACTION,
            user_id=user_id,
            platform="telegram",
            value=1.0,
            metadata={
                'interaction_type': interaction_type,
                **(metadata or {})
            }
        )
        
        await self._record_metric(metric)
        
        # Update real-time counters
        self.realtime_counters['active_users_today'].add(user_id)
        
        # Update user stats
        await self._update_user_activity(user_id, interaction_type)
    
    async def track_exchange_request(self, user_id: int, exchange_data: Dict[str, Any]):
        """Track when a user requests an engagement exchange."""
        
        metric = MetricData(
            metric_type=MetricType.TASK_EXECUTION,
            user_id=user_id,
            platform=exchange_data.get('platform'),
            value=1.0,
            metadata={
                'action': 'exchange_requested',
                'platform': exchange_data.get('platform'),
                'content_url': exchange_data.get('content_url'),
                'priority': exchange_data.get('priority', 5.0)
            }
        )
        
        await self._record_metric(metric)
        
        # Update counters
        self.realtime_counters['exchanges_today'] += 1
        
        # Update user stats
        await self._update_user_exchange_stats(user_id, 'requested', exchange_data)
    
    async def track_exchange_completion(self, user_id: int, task_id: str, success: bool, 
                                      execution_time: timedelta, platform: str, details: Dict[str, Any]):
        """Track completion of an engagement exchange."""
        
        metric = MetricData(
            metric_type=MetricType.ENGAGEMENT_SUCCESS,
            user_id=user_id,
            platform=platform,
            value=1.0 if success else 0.0,
            metadata={
                'task_id': task_id,
                'success': success,
                'execution_time_seconds': execution_time.total_seconds(),
                'platform': platform,
                'details': details
            }
        )
        
        await self._record_metric(metric)
        
        # Update counters
        if success:
            self.realtime_counters['successful_exchanges_today'] += 1
            self.realtime_counters['total_engagement_given'] += len(details.get('actions_performed', []))
        
        # Update user stats
        await self._update_user_exchange_stats(user_id, 'completed', {
            'success': success,
            'platform': platform,
            'execution_time': execution_time
        })
        
        # Update platform metrics
        self.platform_metrics[platform]['success_rate'].append(1.0 if success else 0.0)
        self.platform_metrics[platform]['execution_time'].append(execution_time.total_seconds())
    
    async def track_viral_content(self, chat_id: int, message_id: int, engagement_score: float, 
                                platform: Optional[str] = None):
        """Track detection of viral content."""
        
        metric = MetricData(
            metric_type=MetricType.VIRAL_DETECTION,
            user_id=None,  # Viral content is not user-specific
            platform=platform,
            value=engagement_score,
            metadata={
                'chat_id': chat_id,
                'message_id': message_id,
                'engagement_score': engagement_score,
                'platform': platform
            }
        )
        
        await self._record_metric(metric)
        
        # Update counter
        self.realtime_counters['viral_content_detected_today'] += 1
    
    async def track_message(self, user_id: int, message_text: str):
        """Track user messages for analysis."""
        
        metric = MetricData(
            metric_type=MetricType.USER_INTERACTION,
            user_id=user_id,
            platform="telegram",
            value=len(message_text),
            metadata={
                'interaction_type': 'message',
                'message_length': len(message_text),
                'has_url': 'http' in message_text.lower(),
                'has_mention': '@' in message_text
            }
        )
        
        await self._record_metric(metric)
    
    async def track_system_performance(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Track system performance metrics."""
        
        metric = MetricData(
            metric_type=MetricType.SYSTEM_PERFORMANCE,
            user_id=None,
            platform=None,
            value=value,
            metadata={
                'metric_name': metric_name,
                **(metadata or {})
            }
        )
        
        await self._record_metric(metric)
        
        # Update system metrics
        if metric_name in self.system_metrics:
            self.system_metrics[metric_name].append(value)
    
    async def _record_metric(self, metric: MetricData):
        """Record a metric to the buffer and process it."""
        
        self.metrics_buffer.append(metric)
        
        # Process metric for real-time analytics
        await self._process_metric_realtime(metric)
        
        # Store in database (would be implemented)
        # await self._store_metric_in_db(metric)
    
    async def _process_metric_realtime(self, metric: MetricData):
        """Process metric for real-time analytics."""
        
        # Update daily stats
        today = datetime.now().date()
        if today not in self.daily_stats:
            self.daily_stats[today] = EngagementStats()
        
        daily_stat = self.daily_stats[today]
        
        if metric.metric_type == MetricType.TASK_EXECUTION:
            daily_stat.total_tasks += 1
            
        elif metric.metric_type == MetricType.ENGAGEMENT_SUCCESS:
            if metric.value > 0.5:  # Success
                daily_stat.successful_tasks += 1
            else:
                daily_stat.failed_tasks += 1
            
            # Update platform breakdown
            platform = metric.platform or 'unknown'
            if platform not in daily_stat.platform_breakdown:
                daily_stat.platform_breakdown[platform] = {'total': 0, 'successful': 0}
            
            daily_stat.platform_breakdown[platform]['total'] += 1
            if metric.value > 0.5:
                daily_stat.platform_breakdown[platform]['successful'] += 1
        
        # Calculate success rate
        total = daily_stat.successful_tasks + daily_stat.failed_tasks
        if total > 0:
            daily_stat.success_rate = daily_stat.successful_tasks / total * 100
    
    async def _update_user_activity(self, user_id: int, interaction_type: str):
        """Update user activity statistics."""
        
        if user_id not in self.user_stats_cache:
            self.user_stats_cache[user_id] = UserStats(
                user_id=user_id,
                join_date=datetime.now()
            )
        
        user_stats = self.user_stats_cache[user_id]
        user_stats.last_activity = datetime.now()
        
        # Update total user count
        if len(self.user_stats_cache) > self.realtime_counters['total_users']:
            self.realtime_counters['total_users'] = len(self.user_stats_cache)
    
    async def _update_user_exchange_stats(self, user_id: int, action: str, data: Dict[str, Any]):
        """Update user exchange statistics."""
        
        if user_id not in self.user_stats_cache:
            self.user_stats_cache[user_id] = UserStats(
                user_id=user_id,
                join_date=datetime.now()
            )
        
        user_stats = self.user_stats_cache[user_id]
        
        if action == 'requested':
            user_stats.total_exchanges += 1
            
            # Update favorite platform
            platform = data.get('platform')
            if platform:
                # Simple logic to track favorite platform
                # In practice, you'd maintain a more sophisticated counter
                user_stats.favorite_platform = platform
        
        elif action == 'completed':
            if data.get('success'):
                user_stats.successful_exchanges += 1
                user_stats.given_engagement += 1
            
            # Update engagement trend
            success_rate = user_stats.successful_exchanges / max(user_stats.total_exchanges, 1)
            user_stats.engagement_trend.append(success_rate)
            
            # Keep only last 10 data points
            if len(user_stats.engagement_trend) > 10:
                user_stats.engagement_trend = user_stats.engagement_trend[-10:]
            
            # Calculate reciprocity ratio
            if user_stats.received_engagement > 0:
                user_stats.reciprocity_ratio = user_stats.given_engagement / user_stats.received_engagement
    
    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Get statistics for a specific user."""
        return self.user_stats_cache.get(user_id)
    
    async def get_detailed_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get detailed statistics for a user."""
        
        user_stats = self.user_stats_cache.get(user_id)
        if not user_stats:
            return {'error': 'User not found'}
        
        # Calculate additional metrics
        recent_metrics = [
            metric for metric in list(self.metrics_buffer)
            if metric.user_id == user_id and 
               metric.timestamp > datetime.now() - timedelta(days=7)
        ]
        
        return {
            'user_id': user_id,
            'total_exchanges': user_stats.total_exchanges,
            'successful_exchanges': user_stats.successful_exchanges,
            'success_rate': (user_stats.successful_exchanges / max(user_stats.total_exchanges, 1)) * 100,
            'reciprocity_ratio': user_stats.reciprocity_ratio,
            'favorite_platform': user_stats.favorite_platform,
            'join_date': user_stats.join_date.isoformat() if user_stats.join_date else None,
            'last_activity': user_stats.last_activity.isoformat() if user_stats.last_activity else None,
            'engagement_trend': user_stats.engagement_trend,
            'weekly_activity': len(recent_metrics),
            'rank': await self._calculate_user_rank(user_id)
        }
    
    async def _calculate_user_rank(self, user_id: int) -> int:
        """Calculate user rank based on performance metrics."""
        
        user_stats = self.user_stats_cache.get(user_id)
        if not user_stats:
            return len(self.user_stats_cache)
        
        # Calculate score based on various factors
        user_score = (
            user_stats.successful_exchanges * 2 +
            user_stats.reciprocity_ratio * 10 +
            len(user_stats.engagement_trend) * 1
        )
        
        # Count users with higher scores
        rank = 1
        for other_user_id, other_stats in self.user_stats_cache.items():
            if other_user_id == user_id:
                continue
            
            other_score = (
                other_stats.successful_exchanges * 2 +
                other_stats.reciprocity_ratio * 10 +
                len(other_stats.engagement_trend) * 1
            )
            
            if other_score > user_score:
                rank += 1
        
        return rank
    
    async def get_total_users(self) -> int:
        """Get total number of users."""
        return self.realtime_counters['total_users']
    
    async def get_exchanges_today(self) -> int:
        """Get number of exchanges today."""
        return self.realtime_counters['exchanges_today']
    
    async def get_success_rate(self) -> float:
        """Get overall success rate."""
        total_exchanges = self.realtime_counters['exchanges_today']
        successful_exchanges = self.realtime_counters['successful_exchanges_today']
        
        if total_exchanges == 0:
            return 0.0
        
        return (successful_exchanges / total_exchanges) * 100
    
    async def get_average_completion_time(self) -> str:
        """Get average task completion time."""
        
        execution_times = []
        for platform_metrics in self.platform_metrics.values():
            execution_times.extend(platform_metrics.get('execution_time', []))
        
        if not execution_times:
            return "N/A"
        
        avg_seconds = statistics.mean(execution_times)
        avg_timedelta = timedelta(seconds=avg_seconds)
        
        # Format as human-readable string
        total_seconds = int(avg_timedelta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    async def get_platform_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics breakdown by platform."""
        
        platform_stats = {}
        
        for platform, metrics in self.platform_metrics.items():
            success_rates = metrics.get('success_rate', [])
            execution_times = metrics.get('execution_time', [])
            
            platform_stats[platform] = {
                'total_tasks': len(success_rates),
                'success_rate': statistics.mean(success_rates) * 100 if success_rates else 0,
                'average_execution_time': statistics.mean(execution_times) if execution_times else 0,
                'trend': success_rates[-10:] if len(success_rates) >= 10 else success_rates
            }
        
        return platform_stats
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        
        return {
            'status': 'healthy' if self.is_running else 'stopped',
            'uptime': datetime.now() - getattr(self, 'start_time', datetime.now()),
            'total_metrics_collected': len(self.metrics_buffer),
            'active_users': len(self.realtime_counters['active_users_today']),
            'queue_health': 'good',  # Would check actual queue status
            'memory_usage': list(self.system_metrics['memory_usage'])[-5:] if self.system_metrics['memory_usage'] else [],
            'error_rate': statistics.mean(list(self.system_metrics['error_rates'])[-10:]) if self.system_metrics['error_rates'] else 0
        }
    
    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily analytics report."""
        
        today = datetime.now().date()
        daily_stats = self.daily_stats.get(today, EngagementStats())
        
        report = {
            'date': today.isoformat(),
            'summary': {
                'total_tasks': daily_stats.total_tasks,
                'successful_tasks': daily_stats.successful_tasks,
                'failed_tasks': daily_stats.failed_tasks,
                'success_rate': daily_stats.success_rate,
                'active_users': len(self.realtime_counters['active_users_today']),
                'viral_content_detected': self.realtime_counters['viral_content_detected_today']
            },
            'platform_breakdown': daily_stats.platform_breakdown,
            'top_users': await self._get_top_users_today(),
            'trends': await self._analyze_daily_trends(),
            'recommendations': await self._generate_daily_recommendations()
        }
        
        self.last_daily_report = report
        return report
    
    async def _get_top_users_today(self) -> List[Dict[str, Any]]:
        """Get top performing users today."""
        
        # Get users active today
        today_metrics = [
            metric for metric in list(self.metrics_buffer)
            if metric.timestamp.date() == datetime.now().date() and
               metric.user_id is not None
        ]
        
        user_scores = defaultdict(int)
        
        for metric in today_metrics:
            if metric.metric_type == MetricType.ENGAGEMENT_SUCCESS and metric.value > 0.5:
                user_scores[metric.user_id] += 1
        
        # Sort by score
        top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [
            {
                'user_id': user_id,
                'successful_exchanges': score,
                'rank': i + 1
            }
            for i, (user_id, score) in enumerate(top_users)
        ]
    
    async def _analyze_daily_trends(self) -> Dict[str, Any]:
        """Analyze daily trends."""
        
        # Compare with previous days
        recent_days = []
        for i in range(7):
            day = datetime.now().date() - timedelta(days=i)
            daily_stats = self.daily_stats.get(day, EngagementStats())
            recent_days.append({
                'date': day.isoformat(),
                'total_tasks': daily_stats.total_tasks,
                'success_rate': daily_stats.success_rate
            })
        
        return {
            'weekly_trend': recent_days,
            'growth_rate': self._calculate_growth_rate(recent_days),
            'peak_hours': await self._identify_peak_hours()
        }
    
    def _calculate_growth_rate(self, daily_data: List[Dict[str, Any]]) -> float:
        """Calculate growth rate over the period."""
        
        if len(daily_data) < 2:
            return 0.0
        
        latest = daily_data[0]['total_tasks']
        previous = daily_data[-1]['total_tasks']
        
        if previous == 0:
            return 100.0 if latest > 0 else 0.0
        
        return ((latest - previous) / previous) * 100
    
    async def _identify_peak_hours(self) -> List[int]:
        """Identify peak activity hours."""
        
        hour_counts = defaultdict(int)
        
        for metric in list(self.metrics_buffer):
            if metric.timestamp.date() == datetime.now().date():
                hour_counts[metric.timestamp.hour] += 1
        
        # Return top 3 peak hours
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [hour for hour, count in peak_hours]
    
    async def _generate_daily_recommendations(self) -> List[str]:
        """Generate daily recommendations based on metrics."""
        
        recommendations = []
        
        today_stats = self.daily_stats.get(datetime.now().date(), EngagementStats())
        
        # Success rate recommendations
        if today_stats.success_rate < 70:
            recommendations.append("Mejorar la calidad del contenido para aumentar la tasa de éxito")
        
        # Activity recommendations
        active_users = len(self.realtime_counters['active_users_today'])
        if active_users < 50:
            recommendations.append("Incrementar promoción para atraer más usuarios activos")
        
        # Platform recommendations
        best_platform = max(
            today_stats.platform_breakdown.items(),
            key=lambda x: x[1].get('successful', 0) / max(x[1].get('total', 1), 1),
            default=(None, {})
        )[0]
        
        if best_platform:
            recommendations.append(f"Enfocarse en {best_platform} que muestra mejor rendimiento")
        
        return recommendations
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics."""
        
        while self.is_running:
            try:
                # Collect CPU, memory, etc. (would use psutil or similar)
                await self.track_system_performance('cpu_usage', 50.0)  # Placeholder
                await self.track_system_performance('memory_usage', 60.0)  # Placeholder
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(60)
    
    async def _daily_reset_task(self):
        """Reset daily counters at midnight."""
        
        while self.is_running:
            now = datetime.now()
            
            # Calculate seconds until midnight
            tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            seconds_until_midnight = (tomorrow - now).total_seconds()
            
            await asyncio.sleep(seconds_until_midnight)
            
            # Reset daily counters
            self.realtime_counters['active_users_today'] = set()
            self.realtime_counters['exchanges_today'] = 0
            self.realtime_counters['successful_exchanges_today'] = 0
            self.realtime_counters['viral_content_detected_today'] = 0
            
            logger.info("Daily counters reset")
    
    async def _trend_analysis_task(self):
        """Background task for trend analysis."""
        
        while self.is_running:
            try:
                # Perform trend analysis every hour
                await self.trend_analyzer.analyze_trends(list(self.metrics_buffer))
                await self.anomaly_detector.detect_anomalies(list(self.metrics_buffer))
                
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error(f"Error in trend analysis: {e}")
                await asyncio.sleep(3600)
    
    async def start(self):
        """Start the metrics collector."""
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("Metrics collector started")
    
    async def stop(self):
        """Stop the metrics collector."""
        self.is_running = False
        
        # Generate final report
        final_report = await self.generate_daily_report()
        logger.info(f"Final daily report: {json.dumps(final_report, indent=2, default=str)}")
        
        logger.info("Metrics collector stopped")


class TrendAnalyzer:
    """Analyzes trends in collected metrics."""
    
    async def analyze_trends(self, metrics: List[MetricData]):
        """Analyze trends in the metrics data."""
        # Implement trend analysis logic
        pass


class AnomalyDetector:
    """Detects anomalies in system metrics."""
    
    async def detect_anomalies(self, metrics: List[MetricData]):
        """Detect anomalies in the metrics data."""
        # Implement anomaly detection logic
        pass