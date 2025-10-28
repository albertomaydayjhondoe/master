"""
Meta Ads Monitoring System
Comprehensive monitoring, alerting, and performance tracking for Meta Ads campaigns
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import statistics

try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    PERFORMANCE = "performance"
    BUDGET = "budget" 
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    TECHNICAL = "technical"

@dataclass
class MetaAlert:
    alert_id: str
    campaign_id: str
    severity: AlertSeverity
    metric_type: MetricType
    title: str
    description: str
    current_value: float
    threshold_value: float
    recommendation: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class PerformanceMetric:
    metric_id: str
    campaign_id: str
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend: str  # 'up', 'down', 'stable'
    timestamp: datetime
    is_healthy: bool

@dataclass
class CampaignHealthScore:
    campaign_id: str
    overall_score: float  # 0-100
    performance_score: float
    budget_efficiency_score: float
    engagement_score: float
    technical_score: float
    health_status: str  # 'excellent', 'good', 'fair', 'poor'
    critical_issues: List[str]
    recommendations: List[str]
    last_updated: datetime

class MetaAdsMonitor:
    """Comprehensive monitoring system for Meta Ads campaigns"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MetaAdsMonitor")
        
        # Monitoring configuration
        self.monitoring_config = config.get('monitoring', {})
        self.alert_thresholds = config.get('alert_thresholds', {})
        self.performance_window = self.monitoring_config.get('performance_window_hours', 24)
        
        # Data storage
        self.active_alerts: Dict[str, MetaAlert] = {}
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.campaign_health_scores: Dict[str, CampaignHealthScore] = {}
        
        # Metrics tracking
        self.metric_windows = {
            'roas': deque(maxlen=50),
            'cpa': deque(maxlen=50),
            'ctr': deque(maxlen=50),
            'spend_rate': deque(maxlen=50),
            'conversion_rate': deque(maxlen=50)
        }
        
        # Alert counters
        self.alert_counts = defaultdict(int)
        self.last_alert_check = datetime.now()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        self.logger.info("📊 Meta Ads Monitor initialized")
    
    async def start_monitoring(self, meta_automator):
        """Start continuous monitoring of Meta Ads campaigns"""
        
        if self.is_monitoring:
            self.logger.warning("⚠️ Monitoring already active")
            return
        
        self.meta_automator = meta_automator
        self.is_monitoring = True
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("🎯 Meta Ads monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("🛑 Meta Ads monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        
        while self.is_monitoring:
            try:
                await self._run_monitoring_cycle()
                await asyncio.sleep(self.monitoring_config.get('check_interval_seconds', 300))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        
        try:
            # Get all active campaigns
            active_campaigns = list(self.meta_automator.active_campaigns.keys())
            
            for campaign_id in active_campaigns:
                # Collect metrics
                metrics = await self.meta_automator.get_campaign_metrics(campaign_id, 1)
                
                if metrics:
                    # Update performance tracking
                    await self._update_performance_metrics(campaign_id, metrics)
                    
                    # Check alert conditions
                    await self._check_alert_conditions(campaign_id, metrics)
                    
                    # Calculate health score
                    health_score = await self._calculate_campaign_health(campaign_id, metrics)
                    self.campaign_health_scores[campaign_id] = health_score
            
            # Clean up old data
            await self._cleanup_old_data()
            
            # Send scheduled reports
            await self._send_scheduled_reports()
            
        except Exception as e:
            self.logger.error(f"❌ Error in monitoring cycle: {e}")
    
    async def _update_performance_metrics(self, campaign_id: str, metrics: List):
        """Update performance metrics tracking"""
        
        if not metrics:
            return
        
        # Calculate current performance
        total_spend = sum(m.spend for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_conversion_value = sum(m.conversion_value for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        
        # Current metrics
        current_roas = total_conversion_value / total_spend if total_spend > 0 else 0
        current_cpa = total_spend / total_conversions if total_conversions > 0 else float('inf')
        current_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        current_conversion_rate = total_conversions / total_clicks * 100 if total_clicks > 0 else 0
        
        # Update metric windows
        timestamp = datetime.now()
        
        performance_data = {
            'timestamp': timestamp,
            'roas': current_roas,
            'cpa': current_cpa if current_cpa != float('inf') else 0,
            'ctr': current_ctr,
            'spend': total_spend,
            'conversions': total_conversions,
            'conversion_rate': current_conversion_rate
        }
        
        # Store in campaign history
        self.performance_history[campaign_id].append(performance_data)
        
        # Update global metric windows
        self.metric_windows['roas'].append(current_roas)
        self.metric_windows['cpa'].append(current_cpa if current_cpa != float('inf') else 0)
        self.metric_windows['ctr'].append(current_ctr)
        self.metric_windows['conversion_rate'].append(current_conversion_rate)
    
    async def _check_alert_conditions(self, campaign_id: str, metrics: List):
        """Check for alert conditions"""
        
        if not metrics:
            return
        
        # Calculate current performance
        total_spend = sum(m.spend for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_conversion_value = sum(m.conversion_value for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        
        current_roas = total_conversion_value / total_spend if total_spend > 0 else 0
        current_cpa = total_spend / total_conversions if total_conversions > 0 else float('inf')
        
        # Check ROAS alert
        min_roas = self.alert_thresholds.get('min_roas', 2.0)
        if current_roas < min_roas and current_roas > 0:
            await self._create_alert(
                campaign_id=campaign_id,
                severity=AlertSeverity.WARNING,
                metric_type=MetricType.PERFORMANCE,
                title="Low ROAS Performance",
                description=f"Campaign ROAS ({current_roas:.2f}) below threshold ({min_roas})",
                current_value=current_roas,
                threshold_value=min_roas,
                recommendation="Consider optimizing targeting, creative, or pausing campaign"
            )
        
        # Check CPA alert
        max_cpa = self.alert_thresholds.get('max_cpa', 50.0)
        if current_cpa > max_cpa and current_cpa != float('inf'):
            await self._create_alert(
                campaign_id=campaign_id,
                severity=AlertSeverity.ERROR,
                metric_type=MetricType.CONVERSION,
                title="High Cost Per Acquisition",
                description=f"Campaign CPA (${current_cpa:.2f}) exceeds threshold (${max_cpa})",
                current_value=current_cpa,
                threshold_value=max_cpa,
                recommendation="Adjust bidding strategy or improve conversion funnel"
            )
        
        # Check budget burn rate
        campaign_info = self.meta_automator.active_campaigns.get(campaign_id, {})
        brief = campaign_info.get('brief', {})
        total_budget = brief.get('budget_total', 0)
        
        if total_budget > 0:
            budget_used_pct = (total_spend / total_budget) * 100
            
            # Alert if spending too fast
            if budget_used_pct > 80:
                await self._create_alert(
                    campaign_id=campaign_id,
                    severity=AlertSeverity.WARNING,
                    metric_type=MetricType.BUDGET,
                    title="High Budget Usage",
                    description=f"Campaign has used {budget_used_pct:.1f}% of total budget",
                    current_value=budget_used_pct,
                    threshold_value=80.0,
                    recommendation="Monitor closely or extend campaign duration"
                )
        
        # Check for zero conversions
        if total_conversions == 0 and total_spend > 50:
            await self._create_alert(
                campaign_id=campaign_id,
                severity=AlertSeverity.ERROR,
                metric_type=MetricType.CONVERSION,
                title="No Conversions Detected",
                description=f"Campaign has spent ${total_spend:.2f} with no conversions",
                current_value=0,
                threshold_value=1,
                recommendation="Check conversion tracking and landing page"
            )
    
    async def _create_alert(self, campaign_id: str, severity: AlertSeverity, 
                          metric_type: MetricType, title: str, description: str,
                          current_value: float, threshold_value: float, 
                          recommendation: str):
        """Create new alert"""
        
        # Generate alert ID
        alert_id = f"{campaign_id}_{metric_type.value}_{int(time.time())}"
        
        # Check if similar alert already exists
        existing_alert = self._find_similar_alert(campaign_id, metric_type, title)
        if existing_alert:
            # Update existing alert
            existing_alert.current_value = current_value
            existing_alert.timestamp = datetime.now()
            existing_alert.description = description
            return existing_alert.alert_id
        
        # Create new alert
        alert = MetaAlert(
            alert_id=alert_id,
            campaign_id=campaign_id,
            severity=severity,
            metric_type=metric_type,
            title=title,
            description=description,
            current_value=current_value,
            threshold_value=threshold_value,
            recommendation=recommendation,
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_counts[severity.value] += 1
        
        # Log alert
        self.logger.warning(f"🚨 {severity.value.upper()} Alert: {title} - {description}")
        
        # Send alert notification (if configured)
        await self._send_alert_notification(alert)
        
        return alert_id
    
    def _find_similar_alert(self, campaign_id: str, metric_type: MetricType, 
                          title: str) -> Optional[MetaAlert]:
        """Find similar unresolved alert"""
        
        for alert in self.active_alerts.values():
            if (alert.campaign_id == campaign_id and 
                alert.metric_type == metric_type and 
                alert.title == title and 
                not alert.resolved):
                return alert
        
        return None
    
    async def _calculate_campaign_health(self, campaign_id: str, metrics: List) -> CampaignHealthScore:
        """Calculate comprehensive campaign health score"""
        
        if not metrics:
            return CampaignHealthScore(
                campaign_id=campaign_id,
                overall_score=0,
                performance_score=0,
                budget_efficiency_score=0,
                engagement_score=0,
                technical_score=0,
                health_status='poor',
                critical_issues=['No metrics available'],
                recommendations=['Check campaign configuration'],
                last_updated=datetime.now()
            )
        
        # Calculate component scores
        performance_score = await self._calculate_performance_score(metrics)
        budget_score = await self._calculate_budget_efficiency_score(campaign_id, metrics)
        engagement_score = await self._calculate_engagement_score(metrics)
        technical_score = await self._calculate_technical_score(campaign_id)
        
        # Overall score (weighted average)
        overall_score = (
            performance_score * 0.4 +
            budget_score * 0.3 +
            engagement_score * 0.2 +
            technical_score * 0.1
        )
        
        # Determine health status
        if overall_score >= 80:
            health_status = 'excellent'
        elif overall_score >= 65:
            health_status = 'good'
        elif overall_score >= 50:
            health_status = 'fair'
        else:
            health_status = 'poor'
        
        # Identify critical issues
        critical_issues = []
        recommendations = []
        
        if performance_score < 50:
            critical_issues.append("Poor performance metrics")
            recommendations.append("Review targeting and creative strategy")
        
        if budget_score < 50:
            critical_issues.append("Inefficient budget usage")
            recommendations.append("Optimize bidding strategy")
        
        if engagement_score < 50:
            critical_issues.append("Low audience engagement")
            recommendations.append("Refresh creative content")
        
        return CampaignHealthScore(
            campaign_id=campaign_id,
            overall_score=overall_score,
            performance_score=performance_score,
            budget_efficiency_score=budget_score,
            engagement_score=engagement_score,
            technical_score=technical_score,
            health_status=health_status,
            critical_issues=critical_issues,
            recommendations=recommendations,
            last_updated=datetime.now()
        )
    
    async def _calculate_performance_score(self, metrics: List) -> float:
        """Calculate performance score based on ROAS and CPA"""
        
        total_spend = sum(m.spend for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        total_conversion_value = sum(m.conversion_value for m in metrics)
        
        if total_spend == 0:
            return 0
        
        roas = total_conversion_value / total_spend
        cpa = total_spend / total_conversions if total_conversions > 0 else float('inf')
        
        # ROAS scoring (0-70 points)
        roas_score = min(70, max(0, (roas - 1) * 35))  # 2.0 ROAS = 35 points, 3.0+ = 70
        
        # CPA scoring (0-30 points)
        target_cpa = self.alert_thresholds.get('max_cpa', 50.0)
        if cpa == float('inf'):
            cpa_score = 0
        else:
            cpa_score = min(30, max(0, 30 * (target_cpa - cpa) / target_cpa))
        
        return roas_score + cpa_score
    
    async def _calculate_budget_efficiency_score(self, campaign_id: str, metrics: List) -> float:
        """Calculate budget efficiency score"""
        
        total_spend = sum(m.spend for m in metrics)
        
        # Get campaign budget info
        campaign_info = self.meta_automator.active_campaigns.get(campaign_id, {})
        brief = campaign_info.get('brief', {})
        
        total_budget = brief.get('budget_total', 1000)
        start_date = brief.get('start_date')
        end_date = brief.get('end_date')
        
        if not start_date or not end_date:
            return 50  # Default score if dates unknown
        
        # Calculate expected spend rate
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        campaign_duration = (end_date - start_date).days or 1
        elapsed_days = (datetime.now() - start_date).days
        expected_spend = (elapsed_days / campaign_duration) * total_budget
        
        # Score based on spend efficiency
        if expected_spend == 0:
            return 50
        
        spend_efficiency = total_spend / expected_spend
        
        # Optimal range is 80-120% of expected spend
        if 0.8 <= spend_efficiency <= 1.2:
            return 100
        elif spend_efficiency < 0.5:
            return 20  # Underspending
        elif spend_efficiency > 2.0:
            return 20  # Overspending
        else:
            return max(20, 100 - abs(spend_efficiency - 1) * 80)
    
    async def _calculate_engagement_score(self, metrics: List) -> float:
        """Calculate engagement score based on CTR and interaction rates"""
        
        total_clicks = sum(m.clicks for m in metrics)
        total_impressions = sum(m.impressions for m in metrics)
        
        if total_impressions == 0:
            return 0
        
        ctr = total_clicks / total_impressions * 100
        
        # CTR scoring (industry benchmarks)
        if ctr >= 2.0:
            return 100
        elif ctr >= 1.5:
            return 80
        elif ctr >= 1.0:
            return 60
        elif ctr >= 0.5:
            return 40
        else:
            return 20
    
    async def _calculate_technical_score(self, campaign_id: str) -> float:
        """Calculate technical health score"""
        
        # Check for recent errors or issues
        campaign_alerts = [
            alert for alert in self.active_alerts.values() 
            if alert.campaign_id == campaign_id and alert.metric_type == MetricType.TECHNICAL
        ]
        
        if not campaign_alerts:
            return 100
        
        # Deduct points for technical issues
        critical_count = sum(1 for alert in campaign_alerts if alert.severity == AlertSeverity.CRITICAL)
        error_count = sum(1 for alert in campaign_alerts if alert.severity == AlertSeverity.ERROR)
        warning_count = sum(1 for alert in campaign_alerts if alert.severity == AlertSeverity.WARNING)
        
        score = 100 - (critical_count * 40) - (error_count * 20) - (warning_count * 10)
        
        return max(0, score)
    
    async def _cleanup_old_data(self):
        """Clean up old alerts and data"""
        
        cutoff_time = datetime.now() - timedelta(hours=48)
        
        # Clean up resolved alerts older than 48 hours
        old_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.resolved and alert.timestamp < cutoff_time
        ]
        
        for alert_id in old_alerts:
            del self.active_alerts[alert_id]
    
    async def _send_alert_notification(self, alert: MetaAlert):
        """Send alert notification"""
        
        if DUMMY_MODE:
            self.logger.info(f"🎭 DUMMY: Would send alert notification - {alert.title}")
            return
        
        # Implementation depends on notification channels configured
        # Could send to Slack, email, webhook, etc.
        
        notification_data = {
            'alert_id': alert.alert_id,
            'campaign_id': alert.campaign_id,
            'severity': alert.severity.value,
            'title': alert.title,
            'description': alert.description,
            'recommendation': alert.recommendation,
            'timestamp': alert.timestamp.isoformat()
        }
        
        # Log the notification (replace with actual notification service)
        self.logger.info(f"📢 Alert notification: {json.dumps(notification_data, indent=2)}")
    
    async def _send_scheduled_reports(self):
        """Send scheduled performance reports"""
        
        # Check if it's time for daily/weekly reports
        now = datetime.now()
        
        # Daily report at 9 AM
        if now.hour == 9 and now.minute < 5:
            await self._send_daily_report()
        
        # Weekly report on Mondays at 10 AM
        if now.weekday() == 0 and now.hour == 10 and now.minute < 5:
            await self._send_weekly_report()
    
    async def _send_daily_report(self):
        """Send daily performance report"""
        
        if DUMMY_MODE:
            self.logger.info("🎭 DUMMY: Would send daily report")
            return
        
        report_data = {
            'report_type': 'daily',
            'timestamp': datetime.now().isoformat(),
            'active_campaigns': len(self.meta_automator.active_campaigns),
            'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
            'health_scores': {
                cid: score.overall_score 
                for cid, score in self.campaign_health_scores.items()
            }
        }
        
        self.logger.info(f"📊 Daily report: {json.dumps(report_data, indent=2)}")
    
    async def _send_weekly_report(self):
        """Send weekly performance report"""
        
        if DUMMY_MODE:
            self.logger.info("🎭 DUMMY: Would send weekly report")
            return
        
        # Calculate weekly trends
        weekly_metrics = {}
        for campaign_id, history in self.performance_history.items():
            if len(history) >= 7:
                recent_week = list(history)[-7:]
                avg_roas = statistics.mean([h['roas'] for h in recent_week])
                avg_cpa = statistics.mean([h['cpa'] for h in recent_week if h['cpa'] > 0])
                
                weekly_metrics[campaign_id] = {
                    'avg_roas': avg_roas,
                    'avg_cpa': avg_cpa
                }
        
        report_data = {
            'report_type': 'weekly',
            'timestamp': datetime.now().isoformat(),
            'weekly_metrics': weekly_metrics,
            'alert_summary': {
                severity.value: count 
                for severity, count in self.alert_counts.items()
            }
        }
        
        self.logger.info(f"📈 Weekly report: {json.dumps(report_data, indent=2)}")
    
    # Public API methods
    
    async def get_active_alerts(self, campaign_id: Optional[str] = None) -> List[MetaAlert]:
        """Get active alerts"""
        
        if campaign_id:
            return [
                alert for alert in self.active_alerts.values() 
                if alert.campaign_id == campaign_id and not alert.resolved
            ]
        else:
            return [alert for alert in self.active_alerts.values() if not alert.resolved]
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            self.logger.info(f"✅ Alert acknowledged: {alert_id}")
            return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            self.logger.info(f"✅ Alert resolved: {alert_id}")
            return True
        return False
    
    async def get_campaign_health(self, campaign_id: str) -> Optional[CampaignHealthScore]:
        """Get campaign health score"""
        return self.campaign_health_scores.get(campaign_id)
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring system summary"""
        
        active_alert_count = len([a for a in self.active_alerts.values() if not a.resolved])
        
        return {
            'is_monitoring': self.is_monitoring,
            'monitored_campaigns': len(self.campaign_health_scores),
            'active_alerts': active_alert_count,
            'alert_breakdown': dict(self.alert_counts),
            'last_check': self.last_alert_check.isoformat() if self.last_alert_check else None,
            'health_summary': {
                campaign_id: {
                    'overall_score': score.overall_score,
                    'health_status': score.health_status
                }
                for campaign_id, score in self.campaign_health_scores.items()
            }
        }

# Factory function
def create_meta_ads_monitor(config: Dict[str, Any]) -> MetaAdsMonitor:
    """Create Meta Ads monitoring system"""
    return MetaAdsMonitor(config)

# Example monitoring configuration
def get_monitoring_config() -> Dict[str, Any]:
    """Get example monitoring configuration"""
    return {
        'monitoring': {
            'check_interval_seconds': 300,  # 5 minutes
            'performance_window_hours': 24,
            'enable_performance_tracking': True,
            'enable_alerting': True,
            'enable_reporting': True
        },
        'alert_thresholds': {
            'min_roas': 2.0,
            'max_cpa': 50.0,
            'min_ctr': 0.5,
            'max_frequency': 3.0,
            'budget_burn_rate_warning': 80.0,
            'zero_conversions_spend_threshold': 50.0
        },
        'notifications': {
            'slack_webhook_url': None,
            'email_recipients': [],
            'webhook_urls': []
        },
        'reporting': {
            'daily_report_time': '09:00',
            'weekly_report_day': 'monday',
            'weekly_report_time': '10:00'
        }
    }