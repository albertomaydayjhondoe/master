"""""""""

Telegram Monitoring System - Advanced Health and Performance Monitoring

"""Telegram Monitoring - Advanced System Health and Performance MonitoringTelegram Monitoring - Advanced System Health and Performance Monitoring



import logging"""Tracks activity, performance metrics, alerts and provides comprehensive analytics

import asyncio

from typing import Dict, List, Optional, Any"""

from datetime import datetime, timedelta

from dataclasses import dataclassimport logging

from collections import defaultdict, deque

import statisticsimport asyncioimport logging



from ...config.app_settings import is_dummy_modefrom typing import Dict, List, Optional, Anyimport asyncio



from datetime import datetime, timedeltafrom typing import Dict, List, Optional, Any

@dataclass

class TelegramAlert:from dataclasses import dataclassfrom datetime import datetime, timedelta

    """Telegram alert data structure"""

    id: strfrom collections import defaultdict, dequefrom dataclasses import dataclass, asdict

    type: str

    severity: strimport statisticsimport json

    message: str

    timestamp: datetimefrom collections import defaultdict, deque

    group_id: Optional[int] = None

    data: Optional[Dict[str, Any]] = Nonefrom ...config.app_settings import is_dummy_modeimport statistics

    resolved: bool = False

    resolved_at: Optional[datetime] = None



@dataclassfrom ...config.app_settings import is_dummy_mode

@dataclass

class ActivityMetric:class TelegramAlert:

    """Activity metric data structure"""

    timestamp: datetime    """Telegram alert data structure"""@dataclass

    type: str

    group_id: Optional[int]    id: strclass TelegramAlert:

    success: bool

    duration_ms: Optional[float]    type: str    """Telegram alert data structure"""

    metadata: Dict[str, Any]

    severity: str  # critical, warning, info    id: str



class TelegramMonitor:    message: str    type: str

    """Advanced Telegram Groups Monitoring System"""

        timestamp: datetime    severity: str  # critical, warning, info

    def __init__(self):

        self.dummy_mode = is_dummy_mode()    group_id: Optional[int] = None    message: str

        self.logger = logging.getLogger(__name__)

            data: Optional[Dict[str, Any]] = None    timestamp: datetime

        # Monitoring configuration

        self.alert_thresholds = {    resolved: bool = False    group_id: Optional[int] = None

            "low_engagement": 0.05,

            "high_failure_rate": 0.2,    resolved_at: Optional[datetime] = None    data: Optional[Dict[str, Any]] = None

            "flood_wait_frequent": 5,

            "group_inactive": 24,    resolved: bool = False

            "high_response_time": 5000,

            "rate_limit_threshold": 0.8,@dataclass    resolved_at: Optional[datetime] = None

            "error_spike": 10,

            "engagement_drop": 0.5class ActivityMetric:

        }

            """Activity metric data structure"""@dataclass

        # Monitoring data structures

        self.activity_log = deque(maxlen=10000)    timestamp: datetimeclass ActivityMetric:

        self.performance_metrics = defaultdict(list)

        self.active_alerts = {}    type: str    """Activity metric data structure"""

        self.alert_history = deque(maxlen=1000)

        self.group_metrics = defaultdict(lambda: defaultdict(list))    group_id: Optional[int]    timestamp: datetime

        self.system_stats = {}

            success: bool    type: str

        # Real-time monitoring

        self.monitoring_enabled = True    duration_ms: Optional[float]    group_id: Optional[int]

        self.last_health_check = datetime.now()

            metadata: Dict[str, Any]    success: bool

        if self.dummy_mode:

            self.logger.info("🎭 Running Telegram monitor in dummy mode")    duration_ms: Optional[float]

            self._initialize_dummy_data()

    class TelegramMonitor:    metadata: Dict[str, Any]

    def _initialize_dummy_data(self):

        """Initialize dummy data for development"""    """Advanced Telegram Groups Monitoring System"""

        now = datetime.now()

        for i in range(50):    class TelegramMonitor:

            activity = ActivityMetric(

                timestamp=now - timedelta(minutes=i*10),    def __init__(self):    """Advanced Telegram Groups Monitoring System"""

                type=["message_sent", "content_generated", "group_analyzed"][i % 3],

                group_id=[-1001234567890, -1001234567891][i % 2],        self.dummy_mode = is_dummy_mode()    

                success=i % 10 != 0,

                duration_ms=500 + (i * 10),        self.logger = logging.getLogger(__name__)    def __init__(self):

                metadata={"size": 100 + i, "engagement": 0.1 + (i * 0.01)}

            )                self.dummy_mode = is_dummy_mode()

            self.activity_log.append(activity)

            # Monitoring configuration        self.logger = logging.getLogger(__name__)

    async def log_activity(self, activity_type: str, data: Dict[str, Any]):

        """Log Telegram activity with comprehensive metrics tracking"""        self.alert_thresholds = {        

        activity = ActivityMetric(

            timestamp=datetime.now(),            "low_engagement": 0.05,                   # Monitoring configuration

            type=activity_type,

            group_id=data.get("group_id"),            "high_failure_rate": 0.2,                 self.alert_thresholds = {

            success=data.get("success", True),

            duration_ms=data.get("duration_ms"),            "flood_wait_frequent": 5,                     "low_engagement": 0.05,           # Below 5% engagement rate

            metadata=data

        )            "group_inactive": 24,                         "high_failure_rate": 0.2,         # Above 20% message failures  

        

        self.activity_log.append(activity)            "high_response_time": 5000,                   "flood_wait_frequent": 5,         # More than 5 flood waits per hour

        

        # Update metrics            "rate_limit_threshold": 0.8,                  "group_inactive": 24,             # No posts for 24 hours

        await self._update_performance_metrics(activity)

        if activity.group_id:            "error_spike": 10,                            "high_response_time": 5000,       # Above 5 seconds response time

            await self._update_group_metrics(activity)

        await self._check_activity_alerts(activity)            "engagement_drop": 0.5                        "rate_limit_threshold": 0.8,      # 80% of rate limit reached

        

        # Update system stats periodically        }            "error_spike": 10,                # 10+ errors in 10 minutes

        if (datetime.now() - self.last_health_check).seconds > 300:

            await self._update_system_stats()                    "engagement_drop": 0.5            # 50% drop in engagement

            self.last_health_check = datetime.now()

                # Monitoring data structures        }

        self.logger.debug(f"📊 Activity logged: {activity_type}")

            self.activity_log = deque(maxlen=10000)        

    async def _update_performance_metrics(self, activity: ActivityMetric):

        """Update performance metrics based on activity"""        self.performance_metrics = defaultdict(list)        # Monitoring data structures

        if activity.duration_ms:

            self.performance_metrics["response_times"].append({        self.active_alerts = {}        self.activity_log = deque(maxlen=10000)  # Recent activities

                "timestamp": activity.timestamp,

                "duration_ms": activity.duration_ms,        self.alert_history = deque(maxlen=1000)        self.performance_metrics = defaultdict(list)  # Performance data

                "type": activity.type

            })        self.group_metrics = defaultdict(lambda: defaultdict(list))        self.active_alerts = {}  # Active alerts by ID

        

        self.performance_metrics["success_rate"].append({        self.system_stats = {}        self.alert_history = deque(maxlen=1000)  # Alert history

            "timestamp": activity.timestamp,

            "success": activity.success,                self.group_metrics = defaultdict(lambda: defaultdict(list))  # Per-group metrics

            "type": activity.type

        })        # Real-time monitoring        self.system_stats = {}  # System-wide statistics

        

        # Keep metrics for last 24 hours only        self.monitoring_enabled = True        

        cutoff_time = datetime.now() - timedelta(hours=24)

        for metric_type in self.performance_metrics:        self.last_health_check = datetime.now()        # Real-time monitoring

            self.performance_metrics[metric_type] = [

                m for m in self.performance_metrics[metric_type]                 self.monitoring_enabled = True

                if m["timestamp"] > cutoff_time

            ]        if self.dummy_mode:        self.last_health_check = datetime.now()

    

    async def _update_group_metrics(self, activity: ActivityMetric):            self.logger.info("🎭 Running Telegram monitor in dummy mode")        

        """Update group-specific metrics"""

        group_id = activity.group_id            self._initialize_dummy_data()        if self.dummy_mode:

        

        if activity.type == "message_sent" and activity.success:                self.logger.info("🎭 Running Telegram monitor in dummy mode")

            engagement = activity.metadata.get("engagement", 0)

            self.group_metrics[group_id]["engagement"].append({    def _initialize_dummy_data(self):            self._initialize_dummy_data()

                "timestamp": activity.timestamp,

                "rate": engagement        """Initialize dummy data for development"""    

            })

                now = datetime.now()    def _initialize_dummy_data(self):

        if activity.type == "message_sent":

            self.group_metrics[group_id]["posts"].append({        for i in range(50):        """Initialize dummy data for development"""

                "timestamp": activity.timestamp,

                "success": activity.success            activity = ActivityMetric(        

            })

                        timestamp=now - timedelta(minutes=i*10),        # Add some dummy activities

        if activity.duration_ms:

            self.group_metrics[group_id]["response_times"].append({                type=["message_sent", "content_generated", "group_analyzed"][i % 3],        now = datetime.now()

                "timestamp": activity.timestamp,

                "duration_ms": activity.duration_ms                group_id=[-1001234567890, -1001234567891][i % 2],        for i in range(50):

            })

                    success=i % 10 != 0,  # 10% failure rate            activity = ActivityMetric(

    async def _check_activity_alerts(self, activity: ActivityMetric):

        """Check for alert conditions"""                duration_ms=500 + (i * 10),                timestamp=now - timedelta(minutes=i*10),

        if not activity.success:

            await self._check_failure_pattern_alert()                metadata={"size": 100 + i, "engagement": 0.1 + (i * 0.01)}                type=["message_sent", "content_generated", "group_analyzed"][i % 3],

        

        if activity.duration_ms and activity.duration_ms > self.alert_thresholds["high_response_time"]:            )                group_id=[-1001234567890, -1001234567891][i % 2],

            await self._create_alert(

                "high_response_time",            self.activity_log.append(activity)                success=i % 10 != 0,  # 10% failure rate

                "warning",

                f"High response time: {activity.duration_ms}ms",                    duration_ms=500 + (i * 10),

                {"duration_ms": activity.duration_ms, "type": activity.type}

            )    async def log_activity(self, activity_type: str, data: Dict[str, Any]):                metadata={"size": 100 + i, "engagement": 0.1 + (i * 0.01)}

    

    async def _check_failure_pattern_alert(self):        """Log Telegram activity with comprehensive metrics tracking"""            )

        """Check for concerning failure patterns"""

        recent_time = datetime.now() - timedelta(minutes=10)        activity = ActivityMetric(            self.activity_log.append(activity)

        recent_failures = [

            a for a in self.activity_log             timestamp=datetime.now(),    

            if a.timestamp > recent_time and not a.success

        ]            type=activity_type,    async def log_activity(self, activity_type: str, data: Dict[str, Any]):

        

        if len(recent_failures) >= self.alert_thresholds["error_spike"]:            group_id=data.get("group_id"),        """Log Telegram activity with comprehensive metrics tracking"""

            await self._create_alert(

                "error_spike",            success=data.get("success", True),        

                "critical",

                f"Error spike: {len(recent_failures)} failures in 10 minutes",            duration_ms=data.get("duration_ms"),        activity = ActivityMetric(

                {"failure_count": len(recent_failures)}

            )            metadata=data            timestamp=datetime.now(),

    

    async def _create_alert(self, alert_type: str, severity: str, message: str,         )            type=activity_type,

                           data: Dict[str, Any], group_id: Optional[int] = None):

        """Create and manage alerts"""                    group_id=data.get("group_id"),

        alert_id = f"{alert_type}_{group_id or 'system'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                self.activity_log.append(activity)            success=data.get("success", True),

        # Check for duplicate alerts

        existing_alert = None                    duration_ms=data.get("duration_ms"),

        for alert in self.active_alerts.values():

            if (alert.type == alert_type and         # Update metrics            metadata=data

                alert.group_id == group_id and

                (datetime.now() - alert.timestamp).seconds < 3600 and        await self._update_performance_metrics(activity)        )

                not alert.resolved):

                existing_alert = alert        if activity.group_id:        

                break

                    await self._update_group_metrics(activity)        self.activity_log.append(activity)

        if existing_alert:

            existing_alert.data.update(data)        await self._check_activity_alerts(activity)        

            existing_alert.timestamp = datetime.now()

            return                # Update performance metrics

        

        # Create new alert        # Update system stats periodically        await self._update_performance_metrics(activity)

        alert = TelegramAlert(

            id=alert_id,        if (datetime.now() - self.last_health_check).seconds > 300:        

            type=alert_type,

            severity=severity,            await self._update_system_stats()        # Update group-specific metrics

            message=message,

            timestamp=datetime.now(),            self.last_health_check = datetime.now()        if activity.group_id:

            group_id=group_id,

            data=data                    await self._update_group_metrics(activity)

        )

                self.logger.debug(f"📊 Logged activity: {activity_type}")        

        self.active_alerts[alert_id] = alert

        self.alert_history.append(alert)            # Check for alert conditions

        

        # Log alert    async def _update_performance_metrics(self, activity: ActivityMetric):        await self._check_activity_alerts(activity)

        if severity == "critical":

            self.logger.error(f"🚨 CRITICAL ALERT: {message}")        """Update performance metrics based on activity"""        

        elif severity == "warning":

            self.logger.warning(f"⚠️ WARNING ALERT: {message}")        if activity.duration_ms:        # Update system stats periodically

        else:

            self.logger.info(f"ℹ️ INFO ALERT: {message}")            self.performance_metrics["response_times"].append({        if (datetime.now() - self.last_health_check).seconds > 300:  # Every 5 minutes

    

    async def _update_system_stats(self):                "timestamp": activity.timestamp,            await self._update_system_stats()

        """Update system-wide statistics"""

        now = datetime.now()                "duration_ms": activity.duration_ms,            self.last_health_check = datetime.now()

        recent_activities = [a for a in self.activity_log if (now - a.timestamp).seconds < 3600]

                        "type": activity.type        

        if recent_activities:

            success_rate = len([a for a in recent_activities if a.success]) / len(recent_activities)            })        self.logger.debug(f"📊 Logged activity: {activity_type} - Group: {activity.group_id} - Success: {activity.success}")

            avg_response_time = statistics.mean([

                a.duration_ms for a in recent_activities             

                if a.duration_ms is not None

            ]) if any(a.duration_ms for a in recent_activities) else 0        self.performance_metrics["success_rate"].append({    async def _update_performance_metrics(self, activity: ActivityMetric):

        else:

            success_rate = 1.0            "timestamp": activity.timestamp,        """Update performance metrics based on activity"""

            avg_response_time = 0

                    "success": activity.success,        

        self.system_stats = {

            "last_updated": now,            "type": activity.type        # Track response times

            "activities_last_hour": len(recent_activities),

            "success_rate_1h": success_rate,        })        if activity.duration_ms:

            "avg_response_time_1h": avg_response_time,

            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),                    self.performance_metrics["response_times"].append({

            "total_groups_monitored": len(self.group_metrics),

            "uptime_status": "healthy" if len(self.active_alerts) == 0 else "degraded"        # Keep metrics for last 24 hours only                "timestamp": activity.timestamp,

        }

            cutoff_time = datetime.now() - timedelta(hours=24)                "duration_ms": activity.duration_ms,

    async def get_system_health(self) -> Dict[str, Any]:

        """Get comprehensive system health status"""        for metric_type in self.performance_metrics:                "type": activity.type

        await self._update_system_stats()

                    self.performance_metrics[metric_type] = [            })

        if self.dummy_mode:

            return {                m for m in self.performance_metrics[metric_type]         

                "status": "healthy",

                "uptime_percentage": 99.8,                if m["timestamp"] > cutoff_time        # Track success/failure rates

                "response_time_ms": 1200,

                "success_rate": 0.985,            ]        self.performance_metrics["success_rate"].append({

                "active_groups": len(self.group_metrics),

                "messages_sent_24h": len([a for a in self.activity_log if a.type == "message_sent"]),                "timestamp": activity.timestamp,

                "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),

                "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == "critical" and not a.resolved]),    async def _update_group_metrics(self, activity: ActivityMetric):            "success": activity.success,

                "last_updated": datetime.now().isoformat(),

                "monitoring_enabled": self.monitoring_enabled,        """Update group-specific metrics"""            "type": activity.type

                "system_load": "normal"

            }        group_id = activity.group_id        })

        

        # Calculate real metrics                

        day_ago = datetime.now() - timedelta(days=1)

        activities_24h = [a for a in self.activity_log if a.timestamp > day_ago]        if activity.type == "message_sent" and activity.success:        # Track activity frequency

        

        success_rate = (len([a for a in activities_24h if a.success]) / len(activities_24h)) if activities_24h else 1.0            engagement = activity.metadata.get("engagement", 0)        self.performance_metrics["activity_frequency"].append({

        response_times = [a.duration_ms for a in activities_24h if a.duration_ms is not None]

        avg_response_time = statistics.mean(response_times) if response_times else 0            self.group_metrics[group_id]["engagement"].append({            "timestamp": activity.timestamp,

        

        return {                "timestamp": activity.timestamp,            "type": activity.type

            "status": self.system_stats.get("uptime_status", "unknown"),

            "success_rate": success_rate,                "rate": engagement        })

            "response_time_ms": avg_response_time,

            "activities_24h": len(activities_24h),            })        

            "messages_sent_24h": len([a for a in activities_24h if a.type == "message_sent"]),

            "active_groups": len(self.group_metrics),                # Keep metrics for last 24 hours only

            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),

            "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == "critical" and not a.resolved]),        if activity.type == "message_sent":        cutoff_time = datetime.now() - timedelta(hours=24)

            "monitoring_enabled": self.monitoring_enabled,

            "last_updated": datetime.now().isoformat()            self.group_metrics[group_id]["posts"].append({        for metric_type in self.performance_metrics:

        }

                    "timestamp": activity.timestamp,            self.performance_metrics[metric_type] = [

    async def get_alerts(self, severity: Optional[str] = None, hours: int = 24, 

                        resolved: bool = False) -> List[Dict[str, Any]]:                "success": activity.success                m for m in self.performance_metrics[metric_type] 

        """Get alerts with filtering options"""

        time_ago = datetime.now() - timedelta(hours=hours)            })                if m["timestamp"] > cutoff_time

        

        filtered_alerts = []                    ]

        for alert in self.active_alerts.values():

            if alert.timestamp <= time_ago:        if activity.duration_ms:    

                continue

            if severity and alert.severity != severity:            self.group_metrics[group_id]["response_times"].append({    async def _update_group_metrics(self, activity: ActivityMetric):

                continue

            if alert.resolved != resolved:                "timestamp": activity.timestamp,        """Update group-specific metrics"""

                continue

                            "duration_ms": activity.duration_ms        

            filtered_alerts.append({

                "id": alert.id,            })        group_id = activity.group_id

                "type": alert.type,

                "severity": alert.severity,            

                "message": alert.message,

                "timestamp": alert.timestamp.isoformat(),    async def _check_activity_alerts(self, activity: ActivityMetric):        # Track engagement rates

                "group_id": alert.group_id,

                "data": alert.data,        """Check for alert conditions"""        if activity.type == "message_sent" and activity.success:

                "resolved": alert.resolved,

                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None        if not activity.success:            engagement = activity.metadata.get("engagement", 0)

            })

                    await self._check_failure_pattern_alert()            self.group_metrics[group_id]["engagement"].append({

        filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)

        return filtered_alerts                        "timestamp": activity.timestamp,

    

    async def resolve_alert(self, alert_id: str) -> bool:        if activity.duration_ms and activity.duration_ms > self.alert_thresholds["high_response_time"]:                "rate": engagement

        """Mark an alert as resolved"""

        if alert_id in self.active_alerts:            await self._create_alert(            })

            alert = self.active_alerts[alert_id]

            alert.resolved = True                "high_response_time",        

            alert.resolved_at = datetime.now()

            self.logger.info(f"✅ Resolved alert: {alert.type}")                "warning",        # Track posting frequency

            return True

        return False                f"High response time: {activity.duration_ms}ms",        if activity.type == "message_sent":

    

    async def get_group_health_scores(self) -> Dict[str, Dict[str, Any]]:                {"duration_ms": activity.duration_ms, "type": activity.type}            self.group_metrics[group_id]["posts"].append({

        """Calculate health scores for all monitored groups"""

        group_health = {}            )                "timestamp": activity.timestamp,

        

        for group_id, metrics in self.group_metrics.items():                    "success": activity.success

            # Calculate engagement trend

            recent_engagement = [    async def _check_failure_pattern_alert(self):            })

                m["rate"] for m in metrics.get("engagement", [])

                if (datetime.now() - m["timestamp"]).days <= 7        """Check for concerning failure patterns"""        

            ]

                    recent_time = datetime.now() - timedelta(minutes=10)        # Track response times per group

            # Calculate post success rate

            recent_posts = [        recent_failures = [        if activity.duration_ms:

                p for p in metrics.get("posts", [])

                if (datetime.now() - p["timestamp"]).days <= 7            a for a in self.activity_log             self.group_metrics[group_id]["response_times"].append({

            ]

                        if a.timestamp > recent_time and not a.success                "timestamp": activity.timestamp,

            success_rate = (len([p for p in recent_posts if p["success"]]) / len(recent_posts)) if recent_posts else 1.0

                    ]                "duration_ms": activity.duration_ms

            # Calculate response time

            recent_response_times = [                    })

                rt["duration_ms"] for rt in metrics.get("response_times", [])

                if (datetime.now() - rt["timestamp"]).days <= 1        if len(recent_failures) >= self.alert_thresholds["error_spike"]:    

            ]

                        await self._create_alert(    async def _check_activity_alerts(self, activity: ActivityMetric):

            avg_response_time = statistics.mean(recent_response_times) if recent_response_times else 0

                            "error_spike",        """Comprehensive alert checking based on activity patterns"""

            # Calculate health score (0-10)

            base_score = 10.0                "critical",        

            

            # Deduct for low engagement                f"Error spike: {len(recent_failures)} failures in 10 minutes",        # Check for immediate failure

            if recent_engagement:

                avg_engagement = statistics.mean(recent_engagement)                {"failure_count": len(recent_failures)}        if not activity.success:

                if avg_engagement < 0.1:

                    base_score -= 2.0            )            await self._check_failure_pattern_alert()

                elif avg_engagement < 0.15:

                    base_score -= 1.0            

            

            # Deduct for low success rate    async def _create_alert(self, alert_type: str, severity: str, message: str,         # Check response time alerts

            if success_rate < 0.95:

                base_score -= (0.95 - success_rate) * 10                           data: Dict[str, Any], group_id: Optional[int] = None):        if activity.duration_ms and activity.duration_ms > self.alert_thresholds["high_response_time"]:

            

            # Deduct for high response time        """Create and manage alerts"""            await self._create_alert(

            if avg_response_time > 3000:

                base_score -= min(2.0, (avg_response_time - 3000) / 1000)        alert_id = f"{alert_type}_{group_id or 'system'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"                "high_response_time",

            

            # Check for active alerts                        "warning",

            group_alerts = [

                a for a in self.active_alerts.values()         # Check for duplicate alerts                f"High response time detected: {activity.duration_ms}ms for {activity.type}",

                if a.group_id == group_id and not a.resolved

            ]        existing_alert = None                {"duration_ms": activity.duration_ms, "type": activity.type}

            

            base_score -= len(group_alerts) * 0.5        for alert in self.active_alerts.values():            )

            health_score = max(0, min(10, base_score))

                        if (alert.type == alert_type and         

            # Determine trend

            if len(recent_engagement) >= 2:                alert.group_id == group_id and        # Check for flood wait patterns

                recent_avg = statistics.mean(recent_engagement[-5:]) if len(recent_engagement) >= 5 else statistics.mean(recent_engagement)

                older_avg = statistics.mean(recent_engagement[:-5]) if len(recent_engagement) >= 10 else statistics.mean(recent_engagement[:-2])                (datetime.now() - alert.timestamp).seconds < 3600 and        if activity.type == "flood_wait" or (not activity.success and "flood" in str(activity.metadata.get("error", "")).lower()):

                

                if recent_avg > older_avg * 1.1:                not alert.resolved):            await self._check_flood_wait_pattern()

                    trend = "improving"

                elif recent_avg < older_avg * 0.9:                existing_alert = alert        

                    trend = "declining"

                else:                break        # Check engagement drop alerts

                    trend = "stable"

            else:                if activity.type == "message_sent" and activity.group_id:

                trend = "insufficient_data"

                    if existing_alert:            await self._check_engagement_drop_alert(activity.group_id, activity.metadata.get("engagement", 0))

            group_health[str(group_id)] = {

                "health_score": round(health_score, 1),            existing_alert.data.update(data)        

                "engagement_trend": trend,

                "success_rate": round(success_rate, 3),            existing_alert.timestamp = datetime.now()        # Check for error spikes

                "avg_engagement": round(statistics.mean(recent_engagement), 3) if recent_engagement else 0,

                "avg_response_time_ms": round(avg_response_time, 0),            return        await self._check_error_spike_alert()

                "posts_last_week": len(recent_posts),

                "active_alerts": len(group_alerts),            

                "last_activity": max([p["timestamp"] for p in recent_posts]).isoformat() if recent_posts else None

            }        # Create new alert    async def _check_failure_pattern_alert(self):

        

        return group_health        alert = TelegramAlert(        """Check for concerning failure patterns"""

    

    async def generate_comprehensive_report(self, hours: int = 24) -> Dict[str, Any]:            id=alert_id,        

        """Generate comprehensive monitoring report"""

        health = await self.get_system_health()            type=alert_type,        # Get recent failures (last 10 minutes)

        alerts = await self.get_alerts(hours=hours)

        group_health = await self.get_group_health_scores()            severity=severity,        recent_time = datetime.now() - timedelta(minutes=10)

        

        return {            message=message,        recent_failures = [

            "report_metadata": {

                "generated_at": datetime.now().isoformat(),            timestamp=datetime.now(),            a for a in self.activity_log 

                "period_hours": hours,

                "monitoring_version": "2.0",            group_id=group_id,            if a.timestamp > recent_time and not a.success

                "dummy_mode": self.dummy_mode

            },            data=data        ]

            "executive_summary": {

                "overall_status": health.get("status", "unknown"),        )        

                "success_rate": health.get("success_rate", 0),

                "active_alerts": health.get("active_alerts", 0),                if len(recent_failures) >= self.alert_thresholds["error_spike"]:

                "critical_issues": len([a for a in alerts if a.get("severity") == "critical"])

            },        self.active_alerts[alert_id] = alert            await self._create_alert(

            "system_health": health,

            "group_performance": group_health,        self.alert_history.append(alert)                "error_spike",

            "alerts_summary": {

                "total_alerts": len(alerts),                        "critical",

                "by_severity": {

                    "critical": len([a for a in alerts if a.get("severity") == "critical"]),        # Log alert                f"Error spike detected: {len(recent_failures)} failures in 10 minutes",

                    "warning": len([a for a in alerts if a.get("severity") == "warning"]),

                    "info": len([a for a in alerts if a.get("severity") == "info"])        if severity == "critical":                {"failure_count": len(recent_failures), "time_window": "10_minutes"}

                },

                "recent_alerts": alerts[:10]            self.logger.error(f"🚨 CRITICAL ALERT: {message}")            )

            },

            "recommendations": self._generate_recommendations(health, alerts),        elif severity == "warning":    

            "next_review": (datetime.now() + timedelta(hours=6)).isoformat()

        }            self.logger.warning(f"⚠️ WARNING ALERT: {message}")    async def _check_flood_wait_pattern(self):

    

    def _generate_recommendations(self, health: Dict[str, Any], alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:        else:        """Check for flood wait patterns"""

        """Generate actionable recommendations"""

        recommendations = []            self.logger.info(f"ℹ️ INFO ALERT: {message}")        

        

        # Success rate recommendations            hour_ago = datetime.now() - timedelta(hours=1)

        success_rate = health.get("success_rate", 1.0)

        if success_rate < 0.95:    async def _update_system_stats(self):        flood_waits = [

            recommendations.append({

                "priority": "high" if success_rate < 0.9 else "medium",        """Update system-wide statistics"""            a for a in self.activity_log 

                "category": "reliability",

                "title": "Improve Message Success Rate",        now = datetime.now()            if (a.timestamp > hour_ago and 

                "description": f"Current success rate is {success_rate:.1%}. Investigate failure patterns.",

                "actions": [        recent_activities = [a for a in self.activity_log if (now - a.timestamp).seconds < 3600]                (a.type == "flood_wait" or "flood" in str(a.metadata.get("error", "")).lower()))

                    "Review error logs for common failure patterns",

                    "Check API rate limits and adjust frequency",                ]

                    "Verify group permissions and access rights"

                ]        if recent_activities:        

            })

                    success_rate = len([a for a in recent_activities if a.success]) / len(recent_activities)        if len(flood_waits) > self.alert_thresholds["flood_wait_frequent"]:

        # Alert-based recommendations

        critical_alerts = len([a for a in alerts if a.get("severity") == "critical"])            avg_response_time = statistics.mean([            await self._create_alert(

        if critical_alerts > 0:

            recommendations.append({                a.duration_ms for a in recent_activities                 "frequent_flood_waits",

                "priority": "critical",

                "category": "stability",                if a.duration_ms is not None                "warning",

                "title": "Address Critical Alerts",

                "description": f"There are {critical_alerts} critical alerts requiring attention.",            ]) if any(a.duration_ms for a in recent_activities) else 0                f"Frequent flood waits: {len(flood_waits)} in last hour",

                "actions": [

                    "Review and resolve all critical alerts",        else:                {"flood_wait_count": len(flood_waits), "time_window": "1_hour"}

                    "Investigate root causes of critical issues",

                    "Implement preventive measures"            success_rate = 1.0            )

                ]

            })            avg_response_time = 0    

        

        # General maintenance recommendations            async def _check_engagement_drop_alert(self, group_id: int, current_engagement: float):

        if not recommendations:

            recommendations.extend([        self.system_stats = {        """Check for significant engagement drops"""

                {

                    "priority": "low",            "last_updated": now,        

                    "category": "maintenance",

                    "title": "System Health Maintenance",            "activities_last_hour": len(recent_activities),        # Get historical engagement for this group

                    "description": "System is operating normally. Consider routine maintenance.",

                    "actions": [            "success_rate_1h": success_rate,        recent_engagements = [

                        "Review and archive old logs",

                        "Update monitoring thresholds",            "avg_response_time_1h": avg_response_time,            m["rate"] for m in self.group_metrics[group_id]["engagement"]

                        "Test backup procedures"

                    ]            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),            if (datetime.now() - m["timestamp"]).days <= 7

                }

            ])            "total_groups_monitored": len(self.group_metrics),        ]

        

        return recommendations            "uptime_status": "healthy" if len(self.active_alerts) == 0 else "degraded"        

        }        if len(recent_engagements) >= 5:

                avg_engagement = statistics.mean(recent_engagements)

    async def get_system_health(self) -> Dict[str, Any]:            

        """Get comprehensive system health status"""            # Check if current engagement is significantly lower

        await self._update_system_stats()            if (avg_engagement > 0 and 

                        current_engagement < avg_engagement * self.alert_thresholds["engagement_drop"]):

        if self.dummy_mode:                

            return {                await self._create_alert(

                "status": "healthy",                    "engagement_drop",

                "uptime_percentage": 99.8,                    "warning",

                "response_time_ms": 1200,                    f"Engagement drop in group {group_id}: {current_engagement:.3f} vs avg {avg_engagement:.3f}",

                "success_rate": 0.985,                    {

                "active_groups": len(self.group_metrics),                        "group_id": group_id,

                "messages_sent_24h": len([a for a in self.activity_log if a.type == "message_sent"]),                        "current_engagement": current_engagement,

                "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),                        "avg_engagement": avg_engagement,

                "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == "critical" and not a.resolved]),                        "drop_percentage": (1 - current_engagement/avg_engagement) * 100

                "last_updated": datetime.now().isoformat(),                    },

                "monitoring_enabled": self.monitoring_enabled,                    group_id=group_id

                "system_load": "normal"                )

            }    

            async def _check_error_spike_alert(self):

        # Calculate real metrics        """Check for error spikes across all activities"""

        day_ago = datetime.now() - timedelta(days=1)        

        activities_24h = [a for a in self.activity_log if a.timestamp > day_ago]        # Get activities from last 10 minutes

                recent_time = datetime.now() - timedelta(minutes=10)

        success_rate = (len([a for a in activities_24h if a.success]) / len(activities_24h)) if activities_24h else 1.0        recent_activities = [a for a in self.activity_log if a.timestamp > recent_time]

        response_times = [a.duration_ms for a in activities_24h if a.duration_ms is not None]        

        avg_response_time = statistics.mean(response_times) if response_times else 0        if len(recent_activities) < 5:  # Need minimum sample

                    return

        return {        

            "status": self.system_stats.get("uptime_status", "unknown"),        failure_rate = len([a for a in recent_activities if not a.success]) / len(recent_activities)

            "success_rate": success_rate,        

            "response_time_ms": avg_response_time,        if failure_rate > self.alert_thresholds["high_failure_rate"]:

            "activities_24h": len(activities_24h),            await self._create_alert(

            "messages_sent_24h": len([a for a in activities_24h if a.type == "message_sent"]),                "high_failure_rate",

            "active_groups": len(self.group_metrics),                "critical" if failure_rate > 0.5 else "warning",

            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),                f"High failure rate: {failure_rate:.1%} ({len([a for a in recent_activities if not a.success])}/{len(recent_activities)})",

            "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == "critical" and not a.resolved]),                {

            "monitoring_enabled": self.monitoring_enabled,                    "failure_rate": failure_rate,

            "last_updated": datetime.now().isoformat()                    "total_activities": len(recent_activities),

        }                    "time_window": "10_minutes"

                    }

    async def get_alerts(self, severity: Optional[str] = None, hours: int = 24,             )

                        resolved: bool = False) -> List[Dict[str, Any]]:    

        """Get alerts with filtering options"""    async def _create_alert(self, alert_type: str, severity: str, message: str, 

        time_ago = datetime.now() - timedelta(hours=hours)                           data: Dict[str, Any], group_id: Optional[int] = None):

                """Create and manage alerts"""

        filtered_alerts = []        

        for alert in self.active_alerts.values():        alert_id = f"{alert_type}_{group_id or 'system'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if alert.timestamp <= time_ago:        

                continue        # Check for duplicate alerts (same type, group, within last hour)

            if severity and alert.severity != severity:        existing_alert = None

                continue        for alert in self.active_alerts.values():

            if alert.resolved != resolved:            if (alert.type == alert_type and 

                continue                alert.group_id == group_id and

                            (datetime.now() - alert.timestamp).seconds < 3600 and

            filtered_alerts.append({                not alert.resolved):

                "id": alert.id,                existing_alert = alert

                "type": alert.type,                break

                "severity": alert.severity,        

                "message": alert.message,        if existing_alert:

                "timestamp": alert.timestamp.isoformat(),            # Update existing alert data

                "group_id": alert.group_id,            existing_alert.data.update(data)

                "data": alert.data,            existing_alert.timestamp = datetime.now()

                "resolved": alert.resolved,            self.logger.debug(f"🔄 Updated existing alert: {alert_type}")

                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None            return

            })        

                # Create new alert

        filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)        alert = TelegramAlert(

        return filtered_alerts            id=alert_id,

                type=alert_type,

    async def resolve_alert(self, alert_id: str) -> bool:            severity=severity,

        """Mark an alert as resolved"""            message=message,

        if alert_id in self.active_alerts:            timestamp=datetime.now(),

            alert = self.active_alerts[alert_id]            group_id=group_id,

            alert.resolved = True            data=data

            alert.resolved_at = datetime.now()        )

            self.logger.info(f"✅ Resolved alert: {alert.type}")        

            return True        self.active_alerts[alert_id] = alert

        return False        self.alert_history.append(alert)

            

    async def generate_comprehensive_report(self, hours: int = 24) -> Dict[str, Any]:        # Log alert based on severity

        """Generate comprehensive monitoring report"""        if severity == "critical":

        health = await self.get_system_health()            self.logger.error(f"🚨 CRITICAL ALERT: {message}")

        alerts = await self.get_alerts(hours=hours)        elif severity == "warning":

                    self.logger.warning(f"⚠️ WARNING ALERT: {message}")

        return {        else:

            "report_metadata": {            self.logger.info(f"ℹ️ INFO ALERT: {message}")

                "generated_at": datetime.now().isoformat(),        

                "period_hours": hours,        # In production, this would trigger notifications

                "monitoring_version": "2.0",        await self._send_alert_notification(alert)

                "dummy_mode": self.dummy_mode    

            },    async def _send_alert_notification(self, alert: TelegramAlert):

            "executive_summary": {        """Send alert notifications (placeholder for actual implementation)"""

                "overall_status": health.get("status", "unknown"),        

                "success_rate": health.get("success_rate", 0),        if self.dummy_mode:

                "active_alerts": health.get("active_alerts", 0),            self.logger.info(f"🎭 Would send notification for alert: {alert.type}")

                "critical_issues": len([a for a in alerts if a.get("severity") == "critical"])            return

            },        

            "system_health": health,        # In production, implement:

            "alerts_summary": {        # - Email notifications

                "total_alerts": len(alerts),        # - Slack/Discord webhooks

                "by_severity": {        # - SMS alerts for critical issues

                    "critical": len([a for a in alerts if a.get("severity") == "critical"]),        # - Dashboard updates

                    "warning": len([a for a in alerts if a.get("severity") == "warning"]),        # - Webhook notifications

                    "info": len([a for a in alerts if a.get("severity") == "info"])    

                },    async def _update_system_stats(self):

                "recent_alerts": alerts[:10]        """Update system-wide statistics"""

            },        

            "next_review": (datetime.now() + timedelta(hours=6)).isoformat()        now = datetime.now()

        }        
        # Calculate system metrics
        recent_activities = [a for a in self.activity_log if (now - a.timestamp).seconds < 3600]
        
        if recent_activities:
            success_rate = len([a for a in recent_activities if a.success]) / len(recent_activities)
            avg_response_time = statistics.mean([
                a.duration_ms for a in recent_activities 
                if a.duration_ms is not None
            ]) if any(a.duration_ms for a in recent_activities) else 0
        else:
            success_rate = 1.0
            avg_response_time = 0
        
        self.system_stats = {
            "last_updated": now,
            "activities_last_hour": len(recent_activities),
            "success_rate_1h": success_rate,
            "avg_response_time_1h": avg_response_time,
            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
            "total_groups_monitored": len(self.group_metrics),
            "uptime_status": "healthy" if len(self.active_alerts) == 0 else "degraded"
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        
        await self._update_system_stats()
        
        if self.dummy_mode:
            return {
                "status": "healthy",
                "uptime_percentage": 99.8,
                "response_time_ms": 1200,
                "success_rate": 0.985,
                "active_groups": len(self.group_metrics),
                "messages_sent_24h": len([a for a in self.activity_log if a.type == "message_sent"]),
                "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
                "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == "critical" and not a.resolved]),
                "last_updated": datetime.now().isoformat(),
                "monitoring_enabled": self.monitoring_enabled,
                "system_load": "normal"
            }
        
        # Calculate real metrics
        day_ago = datetime.now() - timedelta(days=1)
        activities_24h = [a for a in self.activity_log if a.timestamp > day_ago]
        
        success_rate = (len([a for a in activities_24h if a.success]) / len(activities_24h)) if activities_24h else 1.0
        
        response_times = [a.duration_ms for a in activities_24h if a.duration_ms is not None]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        return {
            "status": self.system_stats.get("uptime_status", "unknown"),
            "success_rate": success_rate,
            "response_time_ms": avg_response_time,
            "activities_24h": len(activities_24h),
            "messages_sent_24h": len([a for a in activities_24h if a.type == "message_sent"]),
            "active_groups": len(self.group_metrics),
            "active_alerts": len([a for a in self.active_alerts.values() if not a.resolved]),
            "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == "critical" and not a.resolved]),
            "monitoring_enabled": self.monitoring_enabled,
            "last_updated": datetime.now().isoformat()
        }
    
    async def get_recent_activity(self, hours: int = 24) -> Dict[str, Any]:
        """Get recent activity summary"""
        
        time_ago = datetime.now() - timedelta(hours=hours)
        recent_activities = [a for a in self.activity_log if a.timestamp > time_ago]
        
        # Group by activity type
        activity_counts = defaultdict(int)
        success_counts = defaultdict(int)
        
        for activity in recent_activities:
            activity_counts[activity.type] += 1
            if activity.success:
                success_counts[activity.type] += 1
        
        # Calculate hourly distribution
        hourly_counts = defaultdict(int)
        for activity in recent_activities:
            hour_key = activity.timestamp.strftime("%Y-%m-%d %H:00")
            hourly_counts[hour_key] += 1
        
        return {
            "time_period_hours": hours,
            "total_activities": len(recent_activities),
            "activity_breakdown": dict(activity_counts),
            "success_breakdown": dict(success_counts),
            "hourly_distribution": dict(hourly_counts),
            "messages_sent": activity_counts.get("message_sent", 0),
            "avg_engagement": statistics.mean([
                a.metadata.get("engagement", 0) 
                for a in recent_activities 
                if a.type == "message_sent" and a.metadata.get("engagement")
            ]) if any(a.metadata.get("engagement") for a in recent_activities if a.type == "message_sent") else 0
        }
    
    async def get_group_health_scores(self) -> Dict[str, Dict[str, Any]]:
        """Calculate health scores for all monitored groups"""
        
        group_health = {}
        
        for group_id, metrics in self.group_metrics.items():
            # Calculate engagement trend
            recent_engagement = [
                m["rate"] for m in metrics.get("engagement", [])
                if (datetime.now() - m["timestamp"]).days <= 7
            ]
            
            # Calculate post success rate
            recent_posts = [
                p for p in metrics.get("posts", [])
                if (datetime.now() - p["timestamp"]).days <= 7
            ]
            
            success_rate = (len([p for p in recent_posts if p["success"]]) / len(recent_posts)) if recent_posts else 1.0
            
            # Calculate response time
            recent_response_times = [
                rt["duration_ms"] for rt in metrics.get("response_times", [])
                if (datetime.now() - rt["timestamp"]).days <= 1
            ]
            
            avg_response_time = statistics.mean(recent_response_times) if recent_response_times else 0
            
            # Calculate health score (0-10)
            base_score = 10.0
            
            # Deduct for low engagement
            if recent_engagement:
                avg_engagement = statistics.mean(recent_engagement)
                if avg_engagement < 0.1:
                    base_score -= 2.0
                elif avg_engagement < 0.15:
                    base_score -= 1.0
            
            # Deduct for low success rate
            if success_rate < 0.95:
                base_score -= (0.95 - success_rate) * 10
            
            # Deduct for high response time
            if avg_response_time > 3000:
                base_score -= min(2.0, (avg_response_time - 3000) / 1000)
            
            # Check for active alerts
            group_alerts = [
                a for a in self.active_alerts.values() 
                if a.group_id == group_id and not a.resolved
            ]
            
            base_score -= len(group_alerts) * 0.5
            
            # Ensure score is between 0 and 10
            health_score = max(0, min(10, base_score))
            
            # Determine trend
            if len(recent_engagement) >= 2:
                recent_avg = statistics.mean(recent_engagement[-5:]) if len(recent_engagement) >= 5 else statistics.mean(recent_engagement)
                older_avg = statistics.mean(recent_engagement[:-5]) if len(recent_engagement) >= 10 else statistics.mean(recent_engagement[:-2])
                
                if recent_avg > older_avg * 1.1:
                    trend = "improving"
                elif recent_avg < older_avg * 0.9:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            group_health[str(group_id)] = {
                "health_score": round(health_score, 1),
                "engagement_trend": trend,
                "success_rate": round(success_rate, 3),
                "avg_engagement": round(statistics.mean(recent_engagement), 3) if recent_engagement else 0,
                "avg_response_time_ms": round(avg_response_time, 0),
                "posts_last_week": len(recent_posts),
                "active_alerts": len(group_alerts),
                "last_activity": max([p["timestamp"] for p in recent_posts]).isoformat() if recent_posts else None
            }
        
        return group_health
    
    async def get_alerts(self, severity: Optional[str] = None, hours: int = 24, 
                        resolved: bool = False) -> List[Dict[str, Any]]:
        """Get alerts with filtering options"""
        
        time_ago = datetime.now() - timedelta(hours=hours)
        
        filtered_alerts = []
        for alert in self.active_alerts.values():
            # Filter by time
            if alert.timestamp <= time_ago:
                continue
            
            # Filter by severity
            if severity and alert.severity != severity:
                continue
            
            # Filter by resolved status
            if alert.resolved != resolved:
                continue
            
            filtered_alerts.append({
                "id": alert.id,
                "type": alert.type,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "group_id": alert.group_id,
                "data": alert.data,
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            })
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return filtered_alerts
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            self.logger.info(f"✅ Resolved alert: {alert.type}")
            return True
        
        return False
    
    async def clear_alerts(self, alert_type: Optional[str] = None, 
                          group_id: Optional[int] = None):
        """Clear alerts with optional filtering"""
        
        cleared_count = 0
        
        for alert_id, alert in list(self.active_alerts.items()):
            should_clear = True
            
            if alert_type and alert.type != alert_type:
                should_clear = False
            
            if group_id and alert.group_id != group_id:
                should_clear = False
            
            if should_clear:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                cleared_count += 1
        
        self.logger.info(f"🧹 Cleared {cleared_count} alerts")
        return cleared_count
    
    async def generate_comprehensive_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        
        health = await self.get_system_health()
        recent_activity = await self.get_recent_activity(hours)
        group_health = await self.get_group_health_scores()
        alerts = await self.get_alerts(hours=hours)
        
        # Calculate additional insights
        performance_trends = await self._calculate_performance_trends(hours)
        recommendations = await self._generate_actionable_recommendations(health, recent_activity, alerts)
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "period_hours": hours,
                "monitoring_version": "2.0",
                "dummy_mode": self.dummy_mode
            },
            "executive_summary": {
                "overall_status": health.get("status", "unknown"),
                "system_health_score": self._calculate_system_health_score(health),
                "total_activities": recent_activity["total_activities"],
                "success_rate": health.get("success_rate", 0),
                "active_alerts": health.get("active_alerts", 0),
                "critical_issues": len([a for a in alerts if a.get("severity") == "critical"])
            },
            "system_health": health,
            "activity_analysis": recent_activity,
            "group_performance": group_health,
            "alerts_summary": {
                "total_alerts": len(alerts),
                "by_severity": {
                    "critical": len([a for a in alerts if a.get("severity") == "critical"]),
                    "warning": len([a for a in alerts if a.get("severity") == "warning"]),
                    "info": len([a for a in alerts if a.get("severity") == "info"])
                },
                "by_type": self._group_alerts_by_type(alerts),
                "recent_alerts": alerts[:10]  # Most recent 10 alerts
            },
            "performance_trends": performance_trends,
            "recommendations": recommendations,
            "next_review": (datetime.now() + timedelta(hours=6)).isoformat()
        }
    
    def _calculate_system_health_score(self, health: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)"""
        
        base_score = 100.0
        
        # Deduct for low success rate
        success_rate = health.get("success_rate", 1.0)
        if success_rate < 1.0:
            base_score -= (1.0 - success_rate) * 50
        
        # Deduct for active alerts
        active_alerts = health.get("active_alerts", 0)
        critical_alerts = health.get("critical_alerts", 0)
        
        base_score -= active_alerts * 2
        base_score -= critical_alerts * 10
        
        # Deduct for high response time
        response_time = health.get("response_time_ms", 0)
        if response_time > 2000:
            base_score -= min(20, (response_time - 2000) / 100)
        
        return max(0, min(100, base_score))
    
    def _group_alerts_by_type(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group alerts by type"""
        
        alert_counts = defaultdict(int)
        for alert in alerts:
            alert_counts[alert["type"]] += 1
        
        return dict(alert_counts)
    
    async def _calculate_performance_trends(self, hours: int) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        
        time_ago = datetime.now() - timedelta(hours=hours)
        recent_activities = [a for a in self.activity_log if a.timestamp > time_ago]
        
        if not recent_activities:
            return {"trend": "insufficient_data"}
        
        # Group activities by hour for trend analysis
        hourly_success_rates = defaultdict(list)
        hourly_response_times = defaultdict(list)
        
        for activity in recent_activities:
            hour_key = activity.timestamp.strftime("%Y-%m-%d %H")
            hourly_success_rates[hour_key].append(1.0 if activity.success else 0.0)
            
            if activity.duration_ms:
                hourly_response_times[hour_key].append(activity.duration_ms)
        
        # Calculate trends
        success_rate_trend = []
        response_time_trend = []
        
        for hour in sorted(hourly_success_rates.keys()):
            if hourly_success_rates[hour]:
                success_rate_trend.append(statistics.mean(hourly_success_rates[hour]))
            
            if hourly_response_times[hour]:
                response_time_trend.append(statistics.mean(hourly_response_times[hour]))
        
        return {
            "success_rate_trend": {
                "direction": self._calculate_trend_direction(success_rate_trend),
                "data_points": len(success_rate_trend),
                "current_rate": success_rate_trend[-1] if success_rate_trend else 0
            },
            "response_time_trend": {
                "direction": self._calculate_trend_direction(response_time_trend, reverse=True),
                "data_points": len(response_time_trend),
                "current_avg": response_time_trend[-1] if response_time_trend else 0
            },
            "activity_volume_trend": {
                "total_activities": len(recent_activities),
                "peak_hour": max(hourly_success_rates.keys(), key=lambda h: len(hourly_success_rates[h])) if hourly_success_rates else None
            }
        }
    
    def _calculate_trend_direction(self, values: List[float], reverse: bool = False) -> str:
        """Calculate trend direction from a series of values"""
        
        if len(values) < 3:
            return "insufficient_data"
        
        # Compare first third vs last third of values
        first_third = values[:len(values)//3] or [values[0]]
        last_third = values[-(len(values)//3):] or [values[-1]]
        
        first_avg = statistics.mean(first_third)
        last_avg = statistics.mean(last_third)
        
        threshold = 0.05  # 5% change threshold
        
        if reverse:
            # For response time, lower is better
            if last_avg < first_avg * (1 - threshold):
                return "improving"
            elif last_avg > first_avg * (1 + threshold):
                return "declining"
        else:
            # For success rate, higher is better
            if last_avg > first_avg * (1 + threshold):
                return "improving"
            elif last_avg < first_avg * (1 - threshold):
                return "declining"
        
        return "stable"
    
    async def _generate_actionable_recommendations(self, health: Dict[str, Any], 
                                                 activity: Dict[str, Any], 
                                                 alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific, actionable recommendations"""
        
        recommendations = []
        
        # Success rate recommendations
        success_rate = health.get("success_rate", 1.0)
        if success_rate < 0.95:
            recommendations.append({
                "priority": "high" if success_rate < 0.9 else "medium",
                "category": "reliability",
                "title": "Improve Message Success Rate",
                "description": f"Current success rate is {success_rate:.1%}. Investigate common failure patterns.",
                "actions": [
                    "Review recent error logs for common failure patterns",
                    "Check API rate limits and adjust sending frequency",
                    "Verify group permissions and access rights",
                    "Implement exponential backoff for failed messages"
                ]
            })
        
        # Response time recommendations
        response_time = health.get("response_time_ms", 0)
        if response_time > 2000:
            recommendations.append({
                "priority": "medium",
                "category": "performance",
                "title": "Optimize Response Times",
                "description": f"Average response time is {response_time:.0f}ms. Consider performance optimizations.",
                "actions": [
                    "Profile slow API calls and optimize bottlenecks",
                    "Implement request caching where appropriate",
                    "Consider connection pooling for API clients",
                    "Monitor network latency to Telegram servers"
                ]
            })
        
        # Alert-based recommendations
        critical_alerts = len([a for a in alerts if a.get("severity") == "critical"])
        if critical_alerts > 0:
            recommendations.append({
                "priority": "critical",
                "category": "stability",
                "title": "Address Critical Alerts",
                "description": f"There are {critical_alerts} critical alerts requiring immediate attention.",
                "actions": [
                    "Review and resolve all critical alerts",
                    "Investigate root causes of critical issues",
                    "Implement preventive measures for recurring issues",
                    "Set up enhanced monitoring for critical components"
                ]
            })
        
        # Activity-based recommendations
        total_activities = activity.get("total_activities", 0)
        if total_activities == 0:
            recommendations.append({
                "priority": "high",
                "category": "monitoring",
                "title": "No Activity Detected",
                "description": "No activities recorded in the monitoring period.",
                "actions": [
                    "Verify monitoring system is properly configured",
                    "Check if automation services are running",
                    "Review system logs for startup errors",
                    "Ensure proper integration with activity logging"
                ]
            })
        
        # General maintenance recommendations
        if not recommendations:  # System is healthy
            recommendations.extend([
                {
                    "priority": "low",
                    "category": "maintenance",
                    "title": "System Health Maintenance",
                    "description": "System is operating normally. Consider routine maintenance tasks.",
                    "actions": [
                        "Review and archive old logs and metrics",
                        "Update monitoring thresholds based on recent trends",
                        "Test backup and recovery procedures",
                        "Review and update documentation"
                    ]
                },
                {
                    "priority": "low",
                    "category": "optimization",
                    "title": "Performance Optimization Opportunities",
                    "description": "Explore opportunities to enhance system performance.",
                    "actions": [
                        "Analyze engagement patterns for posting optimization",
                        "Consider expanding monitoring to additional metrics",
                        "Review group performance for growth opportunities",
                        "Implement predictive analytics for proactive management"
                    ]
                }
            ])
        
        return recommendations
                return {
                    "group_id": group_id,
                    "status": "inactive",
                    "last_message": None,
                    "message_count_24h": 0,
                    "engagement_rate": 0.0
                }
            
            # Analyze recent activity
            now = datetime.now()
            recent_messages = [
                msg for msg in messages
                if (now - msg.date).total_seconds() < 86400  # 24 hours
            ]
            
            last_message = max(messages, key=lambda x: x.date) if messages else None
            
            # Calculate engagement metrics
            total_views = sum(msg.views or 0 for msg in recent_messages)
            total_forwards = sum(msg.forwards or 0 for msg in recent_messages)
            
            engagement_rate = 0.0
            if recent_messages and group_id in self.automator.managed_groups:
                group_info = self.automator.managed_groups[group_id]
                total_interactions = total_views + (total_forwards * 2)
                engagement_rate = total_interactions / (group_info.members_count * len(recent_messages))
            
            return {
                "group_id": group_id,
                "status": "active" if recent_messages else "low_activity",
                "last_message": last_message.date.isoformat() if last_message else None,
                "message_count_24h": len(recent_messages),
                "total_views_24h": total_views,
                "total_forwards_24h": total_forwards,
                "engagement_rate": engagement_rate,
                "health_score": self._calculate_group_health_score(
                    len(recent_messages), engagement_rate
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to check group {group_id} health: {e}")
            return {
                "group_id": group_id,
                "status": "error",
                "message": str(e)
            }
    
    async def monitor_message_delivery(
        self,
        group_id: int,
        message_id: Optional[int] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Monitor message delivery and performance"""
        if is_dummy_mode():
            return self._generate_dummy_delivery_metrics(group_id, message_id)
        
        start_time = datetime.now()
        
        try:
            # Monitor delivery status
            delivery_status = "pending"
            metrics = None
            
            # Wait for delivery confirmation
            for _ in range(timeout):
                if message_id and self.automator:
                    metrics = await self.automator.get_post_metrics(group_id, message_id)
                    if metrics and metrics.views > 0:
                        delivery_status = "delivered"
                        break
                
                await asyncio.sleep(1)
            
            end_time = datetime.now()
            delivery_time = (end_time - start_time).total_seconds()
            
            # Record response time
            self.response_times.append(delivery_time)
            if len(self.response_times) > 100:  # Keep last 100 measurements
                self.response_times.pop(0)
            
            # Update counters
            if delivery_status == "delivered":
                self.messages_sent_today += 1
            else:
                self.failed_messages_today += 1
                await self._create_alert(
                    "message_delivery_failed",
                    "medium",
                    group_id,
                    f"Message delivery failed in group {group_id}",
                    {"message_id": message_id, "delivery_time": delivery_time}
                )
            
            return {
                "group_id": group_id,
                "message_id": message_id,
                "delivery_status": delivery_status,
                "delivery_time_seconds": delivery_time,
                "metrics": {
                    "views": metrics.views if metrics else 0,
                    "forwards": metrics.forwards if metrics else 0,
                    "timestamp": metrics.timestamp.isoformat() if metrics else None
                } if metrics else None
            }
            
        except Exception as e:
            logger.error(f"Message monitoring failed: {e}")
            self.failed_messages_today += 1
            
            await self._create_alert(
                "message_monitoring_error",
                "high",
                group_id,
                f"Message monitoring error: {str(e)}",
                {"message_id": message_id, "error": str(e)}
            )
            
            return {
                "group_id": group_id,
                "message_id": message_id,
                "delivery_status": "error",
                "error": str(e)
            }
    
    async def detect_rate_limits(self) -> Dict[str, Any]:
        """Detect and monitor rate limiting"""
        if is_dummy_mode():
            return {"rate_limited": False, "hits_count": 0}
        
        # Check recent rate limit hits
        recent_hits = self.rate_limit_hits
        
        # Analyze patterns
        is_rate_limited = recent_hits > self.alert_thresholds["rate_limit_hits"]
        
        if is_rate_limited:
            await self._create_alert(
                "rate_limit_detected",
                "high",
                None,
                f"Rate limiting detected: {recent_hits} hits",
                {"hits_count": recent_hits, "threshold": self.alert_thresholds["rate_limit_hits"]}
            )
        
        return {
            "rate_limited": is_rate_limited,
            "hits_count": recent_hits,
            "threshold": self.alert_thresholds["rate_limit_hits"],
            "recommendation": "Reduce posting frequency" if is_rate_limited else "Normal operation"
        }
    
    async def analyze_group_engagement(
        self,
        group_id: int,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze group engagement trends"""
        if is_dummy_mode():
            return self._generate_dummy_engagement_analysis(group_id)
        
        if not self.automator:
            return {"status": "error", "message": "Automator not available"}
        
        try:
            # Get messages from the specified time period
            cutoff_time = datetime.now() - timedelta(hours=hours)
            messages = await self.automator.get_group_messages(group_id, limit=200)
            
            # Filter messages by time period
            period_messages = [
                msg for msg in messages
                if msg.date >= cutoff_time
            ]
            
            if not period_messages:
                return {
                    "group_id": group_id,
                    "analysis_period_hours": hours,
                    "status": "no_activity",
                    "message_count": 0
                }
            
            # Analyze engagement metrics
            total_messages = len(period_messages)
            total_views = sum(msg.views or 0 for msg in period_messages)
            total_forwards = sum(msg.forwards or 0 for msg in period_messages)
            
            # Calculate hourly distribution
            hourly_distribution = [0] * 24
            for msg in period_messages:
                hourly_distribution[msg.date.hour] += 1
            
            peak_hour = hourly_distribution.index(max(hourly_distribution))
            
            # Engagement trend analysis
            avg_views_per_message = total_views / total_messages if total_messages > 0 else 0
            avg_forwards_per_message = total_forwards / total_messages if total_messages > 0 else 0
            
            # Engagement quality score
            engagement_score = self._calculate_engagement_score(
                avg_views_per_message, avg_forwards_per_message, total_messages
            )
            
            return {
                "group_id": group_id,
                "analysis_period_hours": hours,
                "message_count": total_messages,
                "total_views": total_views,
                "total_forwards": total_forwards,
                "avg_views_per_message": avg_views_per_message,
                "avg_forwards_per_message": avg_forwards_per_message,
                "peak_activity_hour": peak_hour,
                "hourly_distribution": hourly_distribution,
                "engagement_score": engagement_score,
                "trend": "increasing" if engagement_score > 0.5 else "stable" if engagement_score > 0.3 else "decreasing"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze engagement for group {group_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        resolved: bool = False
    ) -> List[Dict[str, Any]]:
        """Get monitoring alerts"""
        filtered_alerts = self.alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if not resolved:
            filtered_alerts = [a for a in filtered_alerts if not a.resolved]
        
        return [
            {
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "group_id": alert.group_id,
                "message": alert.message,
                "details": alert.details,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved
            }
            for alert in filtered_alerts
        ]
    
    def resolve_alert(self, alert_index: int) -> bool:
        """Resolve a specific alert"""
        try:
            if 0 <= alert_index < len(self.alerts):
                self.alerts[alert_index].resolved = True
                return True
            return False
        except Exception:
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if is_dummy_mode():
            return self._generate_dummy_performance_summary()
        
        # Calculate success rate
        total_messages = self.messages_sent_today + self.failed_messages_today
        success_rate = (
            self.messages_sent_today / total_messages
            if total_messages > 0 else 1.0
        )
        
        # Get recent health metrics
        recent_health = self.health_history[-1] if self.health_history else None
        
        return {
            "messages_sent_today": self.messages_sent_today,
            "failed_messages_today": self.failed_messages_today,
            "success_rate": success_rate,
            "avg_response_time": (
                sum(self.response_times) / len(self.response_times)
                if self.response_times else 0.0
            ),
            "rate_limit_hits": self.rate_limit_hits,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "connection_status": recent_health.connection_status if recent_health else False,
            "total_groups": recent_health.total_groups if recent_health else 0,
            "monitoring_status": "active" if self.is_monitoring else "inactive"
        }
    
    # Helper methods
    async def _count_active_groups(self) -> int:
        """Count groups with recent activity"""
        if not self.automator:
            return 0
        
        active_count = 0
        for group_id in self.automator.managed_groups.keys():
            health = await self.check_group_health(group_id)
            if health.get("message_count_24h", 0) > 0:
                active_count += 1
        
        return active_count
    
    async def _check_health_alerts(self, metrics: TelegramHealthMetrics):
        """Check for health-based alerts"""
        # Check failure rate
        total_messages = metrics.messages_sent_today + metrics.failed_messages_today
        if total_messages > 0:
            failure_rate = metrics.failed_messages_today / total_messages
            if failure_rate > self.alert_thresholds["message_failure_rate"]:
                await self._create_alert(
                    "high_failure_rate",
                    "high",
                    None,
                    f"Message failure rate is {failure_rate:.1%}",
                    {"failure_rate": failure_rate, "threshold": self.alert_thresholds["message_failure_rate"]}
                )
        
        # Check response time
        if metrics.avg_response_time > self.alert_thresholds["response_time"]:
            await self._create_alert(
                "slow_response_time",
                "medium",
                None,
                f"Average response time is {metrics.avg_response_time:.1f}s",
                {"response_time": metrics.avg_response_time, "threshold": self.alert_thresholds["response_time"]}
            )
        
        # Check connection status
        if not metrics.connection_status:
            await self._create_alert(
                "connection_lost",
                "critical",
                None,
                "Telegram connection lost",
                {"last_activity": metrics.last_activity.isoformat()}
            )
    
    async def _create_alert(
        self,
        alert_type: str,
        severity: str,
        group_id: Optional[int],
        message: str,
        details: Dict[str, Any]
    ):
        """Create a new alert"""
        alert = TelegramAlert(
            alert_type=alert_type,
            severity=severity,
            group_id=group_id,
            message=message,
            details=details,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        logger.warning(f"🚨 Telegram Alert ({severity}): {message}")
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts.pop(0)
    
    def _calculate_group_health_score(self, message_count: int, engagement_rate: float) -> float:
        """Calculate health score for a group"""
        # Simple scoring algorithm
        activity_score = min(message_count / 10.0, 1.0)  # Normalize to 0-1
        engagement_score = min(engagement_rate * 10, 1.0)  # Normalize to 0-1
        
        return (activity_score + engagement_score) / 2
    
    def _calculate_engagement_score(
        self,
        avg_views: float,
        avg_forwards: float,
        message_count: int
    ) -> float:
        """Calculate engagement score"""
        # Weighted scoring
        views_score = min(avg_views / 100.0, 1.0)  # Normalize views
        forwards_score = min(avg_forwards / 10.0, 1.0)  # Normalize forwards
        activity_score = min(message_count / 50.0, 1.0)  # Normalize activity
        
        return (views_score * 0.4 + forwards_score * 0.4 + activity_score * 0.2)
    
    # Monitoring loops
    async def _real_monitoring_loop(self):
        """Real monitoring loop"""
        while self.is_monitoring:
            try:
                await self.check_health()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _dummy_monitoring_loop(self):
        """Dummy monitoring loop for testing"""
        while self.is_monitoring:
            try:
                # Generate dummy alerts occasionally
                if len(self.alerts) < 3:
                    await self._create_alert(
                        "dummy_alert",
                        "low",
                        1001,
                        "Dummy monitoring alert",
                        {"test": True}
                    )
                
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Dummy monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    # Dummy data generators
    def _generate_dummy_health_metrics(self) -> TelegramHealthMetrics:
        """Generate dummy health metrics"""
        return TelegramHealthMetrics(
            connection_status=True,
            total_groups=8,
            active_groups=6,
            messages_sent_today=45,
            failed_messages_today=2,
            avg_response_time=1.2,
            rate_limit_hits=0,
            last_activity=datetime.now()
        )
    
    def _generate_error_health_metrics(self) -> TelegramHealthMetrics:
        """Generate error health metrics"""
        return TelegramHealthMetrics(
            connection_status=False,
            total_groups=0,
            active_groups=0,
            messages_sent_today=0,
            failed_messages_today=0,
            avg_response_time=0.0,
            rate_limit_hits=0,
            last_activity=datetime.now()
        )
    
    def _generate_dummy_group_health(self, group_id: int) -> Dict[str, Any]:
        """Generate dummy group health data"""
        return {
            "group_id": group_id,
            "status": "active",
            "last_message": (datetime.now() - timedelta(hours=2)).isoformat(),
            "message_count_24h": 12,
            "total_views_24h": 850,
            "total_forwards_24h": 25,
            "engagement_rate": 0.08,
            "health_score": 0.75
        }
    
    def _generate_dummy_delivery_metrics(
        self,
        group_id: int,
        message_id: Optional[int]
    ) -> Dict[str, Any]:
        """Generate dummy delivery metrics"""
        return {
            "group_id": group_id,
            "message_id": message_id,
            "delivery_status": "delivered",
            "delivery_time_seconds": 1.5,
            "metrics": {
                "views": 25,
                "forwards": 3,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _generate_dummy_engagement_analysis(self, group_id: int) -> Dict[str, Any]:
        """Generate dummy engagement analysis"""
        return {
            "group_id": group_id,
            "analysis_period_hours": 24,
            "message_count": 15,
            "total_views": 450,
            "total_forwards": 18,
            "avg_views_per_message": 30.0,
            "avg_forwards_per_message": 1.2,
            "peak_activity_hour": 14,
            "hourly_distribution": [2, 1, 0, 0, 0, 1, 2, 3, 1, 2, 1, 1, 2, 3, 4, 2, 1, 1, 2, 3, 2, 1, 1, 1],
            "engagement_score": 0.65,
            "trend": "increasing"
        }
    
    def _generate_dummy_performance_summary(self) -> Dict[str, Any]:
        """Generate dummy performance summary"""
        return {
            "messages_sent_today": 45,
            "failed_messages_today": 2,
            "success_rate": 0.96,
            "avg_response_time": 1.2,
            "rate_limit_hits": 0,
            "active_alerts": 1,
            "connection_status": True,
            "total_groups": 8,
            "monitoring_status": "active"
        }

# Factory function for dependency injection
def create_telegram_monitor(**kwargs) -> TelegramMonitor:
    """Create TelegramMonitor instance with dependency injection"""
    return TelegramMonitor(**kwargs)