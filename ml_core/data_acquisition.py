"""
Real-Time Social Data Acquisition Engine
Continuously acquires metrics, engagement, trends from all social platforms
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

try:
    import aiohttp
except ImportError:
    aiohttp = None
    print("⚠️ aiohttp not available - using dummy mode for HTTP requests")
import os

# Import social extensions
try:
    from social_extensions import SocialPlatform, create_social_orchestrator
except ImportError:
    import sys
    sys.path.append('/workspaces/master')
    from social_extensions import SocialPlatform, create_social_orchestrator

DUMMY_MODE = os.getenv('DUMMY_MODE', 'true').lower() == 'true'

class DataCollectionFrequency(Enum):
    REAL_TIME = 30      # Every 30 seconds
    HIGH = 300          # Every 5 minutes  
    MEDIUM = 900        # Every 15 minutes
    LOW = 3600          # Every hour
    DAILY = 86400       # Every 24 hours

class MetricType(Enum):
    ENGAGEMENT = "engagement"
    FOLLOWERS = "followers"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    VIEWS = "views"
    CONVERSION = "conversion"
    SENTIMENT = "sentiment"
    TRENDING = "trending"
    COMPETITOR = "competitor"
    AUDIENCE = "audience"

@dataclass
class DataCollectionConfig:
    platform: str
    metrics: List[MetricType]
    frequency: DataCollectionFrequency
    endpoints: Dict[str, str]
    authentication: Dict[str, Any]
    filters: Dict[str, Any] = None
    real_time_threshold: float = 0.1  # Trigger immediate collection if change > 10%

@dataclass
class SocialMetric:
    platform: str
    metric_type: MetricType
    timestamp: datetime
    value: float
    previous_value: float = 0.0
    change_percentage: float = 0.0
    context: Dict[str, Any] = None
    confidence: float = 1.0
    source: str = "api"

@dataclass
class TrendingData:
    platform: str
    trend_type: str  # hashtag, topic, content_type
    trend_value: str
    popularity_score: float
    growth_rate: float
    estimated_reach: int
    related_content: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class CompetitorData:
    platform: str
    competitor_id: str
    competitor_name: str
    metrics: Dict[str, float]
    content_strategy: Dict[str, Any]
    posting_frequency: float
    engagement_rate: float
    follower_growth_rate: float
    timestamp: datetime

class RealTimeDataAcquisitionEngine:
    """
    Advanced real-time data acquisition engine that:
    1. Continuously monitors all active social platforms
    2. Collects metrics, engagement data, and trends
    3. Detects significant changes and triggers immediate analysis
    4. Provides unified data interface for ML processing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Collection configurations for each platform
        self.collection_configs = {}
        
        # Active collectors and their tasks
        self.active_collectors = {}
        self.collection_tasks = {}
        
        # Data storage
        self.real_time_metrics = []
        self.trending_data = []
        self.competitor_data = []
        self.historical_metrics = []
        
        # Platform connections
        self.platform_connections = {}
        self.social_orchestrator = None
        
        # Collection state
        self.is_collecting = False
        self.collection_start_time = None
        
        # Change detection
        self.baseline_metrics = {}
        self.alert_thresholds = {
            'engagement_spike': 0.5,     # 50% increase triggers alert
            'follower_loss': 0.1,        # 10% decrease triggers alert
            'reach_drop': 0.3,           # 30% decrease triggers alert
            'viral_threshold': 2.0       # 200% increase suggests viral content
        }
        
        # Callback functions for real-time alerts
        self.alert_callbacks = []
        
        self.logger.info("📡 Real-Time Data Acquisition Engine initialized")
    
    async def initialize(self):
        """Initialize the data acquisition engine"""
        self.logger.info("🚀 Initializing Real-Time Data Acquisition Engine...")
        
        # Initialize social orchestrator for platform access
        self.social_orchestrator = create_social_orchestrator()
        
        # Setup default collection configurations
        await self._setup_default_configs()
        
        # Initialize platform connections
        await self._initialize_platform_connections()
        
        # Load historical baselines
        await self._load_baseline_metrics()
        
        self.logger.info("✅ Real-Time Data Acquisition Engine ready!")
    
    async def start_real_time_collection(self):
        """Start real-time data collection for all active platforms"""
        if self.is_collecting:
            self.logger.warning("⚠️ Collection already running")
            return
        
        self.logger.info("🔄 Starting real-time data collection...")
        self.is_collecting = True
        self.collection_start_time = datetime.now()
        
        # Start collection tasks for each configured platform
        for platform, config in self.collection_configs.items():
            if config:  # Only start if platform is configured
                task = asyncio.create_task(self._platform_collection_loop(platform, config))
                self.collection_tasks[platform] = task
                self.logger.info(f"📊 Started collection for {platform}")
        
        # Start trending data collection
        trending_task = asyncio.create_task(self._trending_collection_loop())
        self.collection_tasks['trending'] = trending_task
        
        # Start competitor monitoring
        competitor_task = asyncio.create_task(self._competitor_monitoring_loop())
        self.collection_tasks['competitor'] = competitor_task
        
        self.logger.info(f"✅ Real-time collection started for {len(self.collection_tasks)} streams")
    
    async def stop_real_time_collection(self):
        """Stop all real-time data collection"""
        self.logger.info("🛑 Stopping real-time data collection...")
        self.is_collecting = False
        
        # Cancel all collection tasks
        for platform, task in self.collection_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.collection_tasks.clear()
        
        # Archive current session data
        await self._archive_session_data()
        
        collection_duration = datetime.now() - self.collection_start_time if self.collection_start_time else timedelta(0)
        self.logger.info(f"✅ Collection stopped after {collection_duration}")
    
    async def activate_platform_collection(self, platform: str, config: DataCollectionConfig = None):
        """Activate data collection for specific platform"""
        self.logger.info(f"🎮 Activating collection for {platform}")
        
        if not config:
            config = await self._create_default_platform_config(platform)
        
        self.collection_configs[platform] = config
        
        # If collection is already running, start this platform immediately
        if self.is_collecting and platform not in self.collection_tasks:
            task = asyncio.create_task(self._platform_collection_loop(platform, config))
            self.collection_tasks[platform] = task
            self.logger.info(f"📊 Started real-time collection for {platform}")
    
    async def deactivate_platform_collection(self, platform: str):
        """Deactivate data collection for specific platform"""
        self.logger.info(f"🛑 Deactivating collection for {platform}")
        
        # Cancel collection task if running
        if platform in self.collection_tasks:
            self.collection_tasks[platform].cancel()
            try:
                await self.collection_tasks[platform]
            except asyncio.CancelledError:
                pass
            del self.collection_tasks[platform]
        
        # Remove from active configurations
        if platform in self.collection_configs:
            del self.collection_configs[platform]
    
    async def get_real_time_data(self, platform: str = None, 
                                metric_types: List[MetricType] = None,
                                time_window_minutes: int = 60) -> List[SocialMetric]:
        """Get real-time data with optional filtering"""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        filtered_data = [
            metric for metric in self.real_time_metrics
            if metric.timestamp >= cutoff_time
        ]
        
        if platform:
            filtered_data = [m for m in filtered_data if m.platform == platform]
        
        if metric_types:
            filtered_data = [m for m in filtered_data if m.metric_type in metric_types]
        
        return filtered_data
    
    async def get_trending_insights(self, platform: str = None) -> List[TrendingData]:
        """Get current trending insights"""
        if platform:
            return [trend for trend in self.trending_data if trend.platform == platform]
        return self.trending_data.copy()
    
    async def get_competitor_analysis(self, platform: str = None) -> List[CompetitorData]:
        """Get competitor analysis data"""
        if platform:
            return [comp for comp in self.competitor_data if comp.platform == platform]
        return self.competitor_data.copy()
    
    async def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in real-time data"""
        anomalies = []
        
        # Group recent metrics by platform and type
        recent_cutoff = datetime.now() - timedelta(minutes=30)
        recent_metrics = [
            metric for metric in self.real_time_metrics
            if metric.timestamp >= recent_cutoff
        ]
        
        # Analyze each metric for anomalies
        for metric in recent_metrics:
            baseline = self.baseline_metrics.get(f"{metric.platform}_{metric.metric_type.value}")
            
            if baseline and abs(metric.change_percentage) > 0.3:  # 30% change threshold
                anomaly = {
                    'platform': metric.platform,
                    'metric_type': metric.metric_type.value,
                    'current_value': metric.value,
                    'baseline_value': baseline,
                    'change_percentage': metric.change_percentage,
                    'severity': self._calculate_anomaly_severity(metric.change_percentage),
                    'timestamp': metric.timestamp,
                    'recommended_action': self._get_anomaly_recommendation(metric)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    async def force_data_collection(self, platform: str) -> Dict[str, Any]:
        """Force immediate data collection for specific platform"""
        self.logger.info(f"🔍 Forcing immediate data collection for {platform}")
        
        if platform not in self.collection_configs:
            raise ValueError(f"Platform {platform} not configured for collection")
        
        config = self.collection_configs[platform]
        collected_data = await self._collect_platform_metrics(platform, config)
        
        return {
            'platform': platform,
            'collection_time': datetime.now(),
            'metrics_collected': len(collected_data),
            'data': [asdict(metric) for metric in collected_data]
        }
    
    def register_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback function for real-time alerts"""
        self.alert_callbacks.append(callback)
        self.logger.info("🔔 Alert callback registered")
    
    # Private methods for data collection loops
    
    async def _platform_collection_loop(self, platform: str, config: DataCollectionConfig):
        """Main collection loop for a specific platform"""
        self.logger.info(f"🔄 Started collection loop for {platform}")
        
        collection_interval = config.frequency.value
        
        while self.is_collecting:
            try:
                loop_start = time.time()
                
                # Collect metrics for this platform
                metrics = await self._collect_platform_metrics(platform, config)
                
                # Process and store metrics
                if metrics:
                    self.real_time_metrics.extend(metrics)
                    await self._process_new_metrics(metrics)
                
                # Calculate sleep time
                loop_duration = time.time() - loop_start
                sleep_time = max(0, collection_interval - loop_duration)
                
                self.logger.debug(f"📊 {platform} collection cycle: {len(metrics)} metrics in {loop_duration:.2f}s")
                await asyncio.sleep(sleep_time)
                
            except asyncio.CancelledError:
                self.logger.info(f"📊 Collection cancelled for {platform}")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in {platform} collection loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _trending_collection_loop(self):
        """Collection loop for trending data across platforms"""
        while self.is_collecting:
            try:
                for platform in self.collection_configs.keys():
                    trending = await self._collect_trending_data(platform)
                    if trending:
                        self.trending_data.extend(trending)
                
                # Keep only recent trending data (last 4 hours)
                cutoff_time = datetime.now() - timedelta(hours=4)
                self.trending_data = [
                    trend for trend in self.trending_data
                    if trend.timestamp >= cutoff_time
                ]
                
                await asyncio.sleep(900)  # Check trends every 15 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in trending collection: {e}")
                await asyncio.sleep(300)
    
    async def _competitor_monitoring_loop(self):
        """Collection loop for competitor monitoring"""
        while self.is_collecting:
            try:
                for platform in self.collection_configs.keys():
                    competitor_data = await self._collect_competitor_data(platform)
                    if competitor_data:
                        self.competitor_data.extend(competitor_data)
                
                # Keep only recent competitor data (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.competitor_data = [
                    comp for comp in self.competitor_data
                    if comp.timestamp >= cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Check competitors every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in competitor monitoring: {e}")
                await asyncio.sleep(600)
    
    # Data collection methods
    
    async def _collect_platform_metrics(self, platform: str, config: DataCollectionConfig) -> List[SocialMetric]:
        """Collect metrics for a specific platform"""
        metrics = []
        current_time = datetime.now()
        
        if DUMMY_MODE:
            # Generate dummy metrics
            for metric_type in config.metrics:
                # Simulate realistic social media metrics
                base_values = {
                    MetricType.ENGAGEMENT: np.random.uniform(2.0, 8.0),
                    MetricType.FOLLOWERS: np.random.randint(1000, 100000),
                    MetricType.REACH: np.random.randint(500, 50000),
                    MetricType.IMPRESSIONS: np.random.randint(1000, 200000),
                    MetricType.LIKES: np.random.randint(10, 1000),
                    MetricType.COMMENTS: np.random.randint(0, 100),
                    MetricType.SHARES: np.random.randint(0, 50),
                    MetricType.VIEWS: np.random.randint(100, 10000),
                }
                
                value = base_values.get(metric_type, np.random.uniform(0, 100))
                
                # Get previous value for change calculation
                baseline_key = f"{platform}_{metric_type.value}"
                previous_value = self.baseline_metrics.get(baseline_key, value)
                
                # Calculate change percentage
                change_percentage = 0.0
                if previous_value > 0:
                    change_percentage = (value - previous_value) / previous_value
                
                # Update baseline
                self.baseline_metrics[baseline_key] = value
                
                metric = SocialMetric(
                    platform=platform,
                    metric_type=metric_type,
                    timestamp=current_time,
                    value=value,
                    previous_value=previous_value,
                    change_percentage=change_percentage,
                    context={
                        "collection_method": "real_time_api",
                        "data_quality": "high",
                        "sample_size": np.random.randint(100, 10000)
                    },
                    confidence=np.random.uniform(0.8, 1.0),
                    source="dummy_api"
                )
                
                metrics.append(metric)
        
        else:
            # Production data collection would go here
            # This would use real API calls to each platform
            pass
        
        return metrics
    
    async def _collect_trending_data(self, platform: str) -> List[TrendingData]:
        """Collect trending data for a specific platform"""
        trending = []
        
        if DUMMY_MODE:
            # Generate dummy trending data
            trending_topics = [
                "#AI", "#MachineLearning", "#SocialMedia", "#Marketing", 
                "#TechTrends", "#Innovation", "#Startup", "#Business"
            ]
            
            for i in range(np.random.randint(2, 6)):
                topic = np.random.choice(trending_topics)
                
                trend = TrendingData(
                    platform=platform,
                    trend_type="hashtag",
                    trend_value=topic,
                    popularity_score=np.random.uniform(0.3, 1.0),
                    growth_rate=np.random.uniform(-0.2, 2.0),
                    estimated_reach=np.random.randint(1000, 1000000),
                    related_content=[
                        {"type": "post", "engagement": np.random.randint(100, 5000)},
                        {"type": "video", "engagement": np.random.randint(500, 20000)}
                    ],
                    timestamp=datetime.now()
                )
                trending.append(trend)
        
        return trending
    
    async def _collect_competitor_data(self, platform: str) -> List[CompetitorData]:
        """Collect competitor analysis data"""
        competitors = []
        
        if DUMMY_MODE:
            # Generate dummy competitor data
            competitor_names = [
                f"competitor_{platform}_1",
                f"competitor_{platform}_2", 
                f"competitor_{platform}_3"
            ]
            
            for name in competitor_names:
                competitor = CompetitorData(
                    platform=platform,
                    competitor_id=f"{name}_id",
                    competitor_name=name,
                    metrics={
                        "followers": np.random.randint(5000, 500000),
                        "engagement_rate": np.random.uniform(1.0, 12.0),
                        "posting_frequency": np.random.uniform(0.5, 5.0),
                        "avg_likes": np.random.randint(100, 10000)
                    },
                    content_strategy={
                        "primary_content_type": np.random.choice(["image", "video", "text", "carousel"]),
                        "posting_times": ["09:00", "13:00", "18:00"],
                        "hashtag_strategy": "targeted"
                    },
                    posting_frequency=np.random.uniform(0.5, 3.0),
                    engagement_rate=np.random.uniform(2.0, 8.0),
                    follower_growth_rate=np.random.uniform(-1.0, 15.0),
                    timestamp=datetime.now()
                )
                competitors.append(competitor)
        
        return competitors
    
    async def _process_new_metrics(self, metrics: List[SocialMetric]):
        """Process newly collected metrics for alerts and analysis"""
        for metric in metrics:
            # Check for significant changes that warrant alerts
            if abs(metric.change_percentage) >= self.alert_thresholds.get('engagement_spike', 0.5):
                await self._trigger_alert({
                    'type': 'significant_change',
                    'platform': metric.platform,
                    'metric_type': metric.metric_type.value,
                    'change_percentage': metric.change_percentage,
                    'current_value': metric.value,
                    'timestamp': metric.timestamp
                })
            
            # Check for viral content indicators
            if (metric.metric_type in [MetricType.ENGAGEMENT, MetricType.REACH, MetricType.VIEWS] and 
                metric.change_percentage >= self.alert_thresholds.get('viral_threshold', 2.0)):
                await self._trigger_alert({
                    'type': 'viral_content_detected',
                    'platform': metric.platform,
                    'metric_type': metric.metric_type.value,
                    'growth_rate': metric.change_percentage,
                    'timestamp': metric.timestamp
                })
    
    async def _trigger_alert(self, alert_data: Dict[str, Any]):
        """Trigger alert to registered callbacks"""
        self.logger.info(f"🚨 Alert triggered: {alert_data['type']} on {alert_data['platform']}")
        
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_data)
                else:
                    callback(alert_data)
            except Exception as e:
                self.logger.error(f"❌ Error in alert callback: {e}")
    
    # Configuration and setup methods
    
    async def _setup_default_configs(self):
        """Setup default collection configurations for all platforms"""
        default_metrics = [
            MetricType.ENGAGEMENT, MetricType.FOLLOWERS, MetricType.REACH,
            MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES
        ]
        
        for platform in ['instagram', 'twitter', 'linkedin', 'whatsapp']:
            config = DataCollectionConfig(
                platform=platform,
                metrics=default_metrics,
                frequency=DataCollectionFrequency.HIGH,  # 5 minutes
                endpoints={},
                authentication={}
            )
            self.collection_configs[platform] = config
    
    async def _create_default_platform_config(self, platform: str) -> DataCollectionConfig:
        """Create default configuration for a specific platform"""
        return DataCollectionConfig(
            platform=platform,
            metrics=[MetricType.ENGAGEMENT, MetricType.FOLLOWERS, MetricType.REACH],
            frequency=DataCollectionFrequency.HIGH,
            endpoints={},
            authentication={}
        )
    
    async def _initialize_platform_connections(self):
        """Initialize connections to all social platforms"""
        # This would setup API connections, authentication, etc.
        # For now, just log the initialization
        for platform in self.collection_configs.keys():
            self.platform_connections[platform] = f"connection_{platform}"
            self.logger.debug(f"🔗 Initialized connection for {platform}")
    
    async def _load_baseline_metrics(self):
        """Load historical baseline metrics for change detection"""
        # In production, this would load from database
        # For now, initialize with dummy baselines
        platforms = ['instagram', 'twitter', 'linkedin', 'whatsapp']
        metric_types = [MetricType.ENGAGEMENT, MetricType.FOLLOWERS, MetricType.REACH]
        
        for platform in platforms:
            for metric_type in metric_types:
                key = f"{platform}_{metric_type.value}"
                # Set realistic baseline values
                if metric_type == MetricType.ENGAGEMENT:
                    self.baseline_metrics[key] = np.random.uniform(3.0, 6.0)
                elif metric_type == MetricType.FOLLOWERS:
                    self.baseline_metrics[key] = np.random.randint(1000, 50000)
                elif metric_type == MetricType.REACH:
                    self.baseline_metrics[key] = np.random.randint(500, 25000)
        
        self.logger.info(f"📊 Loaded {len(self.baseline_metrics)} baseline metrics")
    
    async def _archive_session_data(self):
        """Archive current session data to historical storage"""
        if self.real_time_metrics:
            self.historical_metrics.extend(self.real_time_metrics)
            
            # Keep only last 7 days of historical data
            cutoff_time = datetime.now() - timedelta(days=7)
            self.historical_metrics = [
                metric for metric in self.historical_metrics
                if metric.timestamp >= cutoff_time
            ]
            
            self.logger.info(f"📁 Archived {len(self.real_time_metrics)} metrics to historical storage")
            self.real_time_metrics.clear()
    
    # Utility methods
    
    def _calculate_anomaly_severity(self, change_percentage: float) -> str:
        """Calculate severity level of an anomaly"""
        abs_change = abs(change_percentage)
        
        if abs_change >= 2.0:  # 200%+ change
            return "critical"
        elif abs_change >= 1.0:  # 100%+ change
            return "high"
        elif abs_change >= 0.5:  # 50%+ change
            return "medium"
        else:
            return "low"
    
    def _get_anomaly_recommendation(self, metric: SocialMetric) -> str:
        """Get recommendation for handling an anomaly"""
        if metric.change_percentage > 1.0:  # Large positive change
            return "investigate_viral_content"
        elif metric.change_percentage < -0.5:  # Large negative change
            return "review_content_strategy"
        elif metric.metric_type == MetricType.ENGAGEMENT and metric.change_percentage > 0.5:
            return "scale_successful_content"
        else:
            return "monitor_closely"
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for data acquisition engine"""
        logger = logging.getLogger(f"{__name__}.DataAcquisitionEngine")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

# Factory function
def create_data_acquisition_engine(config: Dict[str, Any] = None) -> RealTimeDataAcquisitionEngine:
    """Create and return a configured data acquisition engine"""
    return RealTimeDataAcquisitionEngine(config)

# Data export utilities
class DataExporter:
    """Utility class for exporting collected data to different formats"""
    
    @staticmethod
    def to_json(data: List[SocialMetric], file_path: str = None) -> str:
        """Export metrics to JSON format"""
        json_data = [asdict(metric) for metric in data]
        
        # Convert datetime objects to strings
        for item in json_data:
            if isinstance(item['timestamp'], datetime):
                item['timestamp'] = item['timestamp'].isoformat()
        
        json_str = json.dumps(json_data, indent=2, default=str)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    @staticmethod
    def to_pandas(data: List[SocialMetric]):
        """Export metrics to pandas DataFrame"""
        try:
            import pandas as pd
            
            # Convert to list of dictionaries
            dict_data = [asdict(metric) for metric in data]
            
            # Flatten context data
            for item in dict_data:
                if item['context']:
                    for key, value in item['context'].items():
                        item[f'context_{key}'] = value
                del item['context']
            
            return pd.DataFrame(dict_data)
            
        except ImportError:
            raise ImportError("pandas is required for DataFrame export")

# Real-time data stream interface
class DataStreamInterface:
    """Interface for consuming real-time data streams"""
    
    def __init__(self, acquisition_engine: RealTimeDataAcquisitionEngine):
        self.acquisition_engine = acquisition_engine
        self.subscribers = []
    
    async def subscribe(self, callback: Callable[[List[SocialMetric]], None]):
        """Subscribe to real-time data stream"""
        self.subscribers.append(callback)
    
    async def start_streaming(self, interval: int = 60):
        """Start streaming data to subscribers"""
        while True:
            # Get latest data
            latest_data = await self.acquisition_engine.get_real_time_data(time_window_minutes=5)
            
            if latest_data:
                # Notify all subscribers
                for callback in self.subscribers:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(latest_data)
                        else:
                            callback(latest_data)
                    except Exception as e:
                        logging.error(f"Error in data stream callback: {e}")
            
            await asyncio.sleep(interval)