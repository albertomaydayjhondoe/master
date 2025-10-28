"""
Artistic Campaign Monitoring System
Real-time monitoring, learning analytics, and performance tracking for artistic campaigns
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque, defaultdict
import statistics

# Remove numpy dependency for dummy mode compatibility
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

class AlertSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class MetricType(Enum):
    ENGAGEMENT = "engagement"
    REACH = "reach" 
    SENTIMENT = "sentiment"
    CONVERSION = "conversion"
    ARTISTIC_APPRECIATION = "artistic_appreciation"
    VIRALITY = "virality"
    COST_EFFICIENCY = "cost_efficiency"

@dataclass
class ArtisticAlert:
    """Alert specific to artistic campaigns"""
    alert_id: str
    campaign_id: str
    severity: AlertSeverity
    metric_type: MetricType
    title: str
    description: str
    current_value: float
    threshold_value: float
    recommendation: str
    created_at: datetime
    acknowledged: bool = False
    resolved: bool = False
    artistic_context: Optional[str] = None

@dataclass
class LearningMetric:
    """Metric for tracking learning progress"""
    metric_id: str
    campaign_id: str
    learning_type: str  # pattern_detection, optimization_effectiveness, prediction_accuracy
    value: float
    confidence: float
    data_points: int
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class ArtisticHealthScore:
    """Health scoring specific to artistic campaigns"""
    campaign_id: str
    overall_score: float  # 0-100
    creative_resonance_score: float
    audience_engagement_score: float
    artistic_appreciation_score: float
    virality_potential_score: float
    cost_effectiveness_score: float
    learning_progress_score: float
    health_status: str  # excellent, good, fair, poor
    critical_issues: List[str]
    recommendations: List[str]
    artistic_insights: List[str]
    last_updated: datetime

class ArtisticCampaignMonitor:
    """Advanced monitoring system for artistic campaigns with ML insights"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        
        # Artistic campaign system reference
        self.artistic_system = None
        
        # Alert management
        self.active_alerts: Dict[str, ArtisticAlert] = {}
        self.alert_history: List[ArtisticAlert] = []
        self.alert_counts = defaultdict(int)
        self.last_alert_check = None
        
        # Learning metrics tracking
        self.learning_metrics: Dict[str, List[LearningMetric]] = defaultdict(list)
        self.pattern_detection_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.optimization_effectiveness: Dict[str, List[float]] = defaultdict(list)
        
        # Performance tracking
        self.campaign_health_scores: Dict[str, ArtisticHealthScore] = {}
        self.performance_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.artistic_insights_cache: Dict[str, List[str]] = defaultdict(list)
        
        # Real-time analytics
        self.real_time_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=500))
        self.learning_convergence_tracking: Dict[str, Dict[str, float]] = {}
        self.model_accuracy_history: Dict[str, List[float]] = defaultdict(list)
        
        # Configuration
        self.monitoring_interval = config.get('monitoring_interval', 60)  # seconds
        self.alert_thresholds = config.get('alert_thresholds', {
            'engagement_drop': 0.3,  # 30% drop
            'sentiment_decline': 0.2,  # 20% decline
            'cost_spike': 2.0,  # 2x increase
            'artistic_appreciation_drop': 0.25  # 25% drop
        })
        
        self.logger.info("🎨 Artistic Campaign Monitor initialized")

    async def start_monitoring(self, artistic_system):
        """Start continuous monitoring of artistic campaigns"""
        if self.is_monitoring:
            self.logger.warning("⚠️ Monitoring already active")
            return
        
        self.artistic_system = artistic_system
        self.is_monitoring = True
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("🚀 Artistic campaign monitoring started")

    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("🛑 Artistic campaign monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop with artistic-specific insights"""
        
        while self.is_monitoring:
            try:
                await self._run_artistic_monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _run_artistic_monitoring_cycle(self):
        """Run complete artistic monitoring cycle"""
        
        try:
            if not self.artistic_system:
                return
            
            # Get all active artistic campaigns
            active_campaigns = list(self.artistic_system.active_campaigns.keys())
            
            for campaign_id in active_campaigns:
                # Collect artistic-specific metrics
                await self._collect_artistic_metrics(campaign_id)
                
                # Check artistic alert conditions
                await self._check_artistic_alert_conditions(campaign_id)
                
                # Track learning progress
                await self._track_learning_progress(campaign_id)
                
                # Calculate artistic health score
                health_score = await self._calculate_artistic_health(campaign_id)
                self.campaign_health_scores[campaign_id] = health_score
                
                # Generate artistic insights
                await self._generate_artistic_insights(campaign_id)
            
            # Cross-campaign analysis
            await self._perform_cross_campaign_analysis()
            
            # Clean up old data
            await self._cleanup_old_monitoring_data()
            
            # Send monitoring reports
            await self._send_artistic_monitoring_reports()
            
        except Exception as e:
            self.logger.error(f"❌ Error in artistic monitoring cycle: {e}")

    async def _collect_artistic_metrics(self, campaign_id: str):
        """Collect artistic-specific metrics"""
        
        # Get performance history
        performance_history = self.artistic_system.campaign_history.get(campaign_id, [])
        if not performance_history:
            return
        
        latest_performance = performance_history[-1]
        
        # Store real-time metrics
        timestamp = datetime.now()
        
        artistic_metrics = {
            'timestamp': timestamp,
            'artistic_appreciation': latest_performance.artistic_appreciation_score,
            'creative_resonance': latest_performance.creative_resonance_score,
            'virality_coefficient': latest_performance.virality_coefficient,
            'sentiment_score': latest_performance.sentiment_score,
            'engagement_rate': latest_performance.engagement_rate,
            'audience_quality': latest_performance.audience_quality_score
        }
        
        # Store in real-time tracking
        for metric, value in artistic_metrics.items():
            if metric != 'timestamp':
                self.real_time_metrics[f"{campaign_id}_{metric}"].append({
                    'timestamp': timestamp,
                    'value': value
                })

    async def _check_artistic_alert_conditions(self, campaign_id: str):
        """Check for artistic campaign specific alerts"""
        
        metrics_key_prefix = f"{campaign_id}_"
        
        # Check artistic appreciation drop
        appreciation_metrics = self.real_time_metrics.get(f"{metrics_key_prefix}artistic_appreciation")
        if appreciation_metrics and len(appreciation_metrics) >= 5:
            recent_values = [m['value'] for m in appreciation_metrics[-5:]]
            if len(recent_values) >= 2:
                current = recent_values[-1]
                previous = statistics.mean(recent_values[:-1])
                
                if current < previous * (1 - self.alert_thresholds['artistic_appreciation_drop']):
                    await self._create_artistic_alert(
                        campaign_id, AlertSeverity.WARNING, MetricType.ARTISTIC_APPRECIATION,
                        "Artistic Appreciation Decline",
                        f"Artistic appreciation dropped {((previous - current) / previous * 100):.1f}%",
                        current, previous,
                        "Review content strategy and audience alignment",
                        "Consider A/B testing different artistic styles or messaging"
                    )
        
        # Check creative resonance
        resonance_metrics = self.real_time_metrics.get(f"{metrics_key_prefix}creative_resonance")
        if resonance_metrics and len(resonance_metrics) >= 3:
            recent_resonance = [m['value'] for m in resonance_metrics[-3:]]
            avg_resonance = statistics.mean(recent_resonance)
            
            if avg_resonance < 0.5:
                await self._create_artistic_alert(
                    campaign_id, AlertSeverity.CRITICAL, MetricType.ENGAGEMENT,
                    "Low Creative Resonance",
                    f"Creative resonance below threshold: {avg_resonance:.2f}",
                    avg_resonance, 0.5,
                    "Creative content may not be connecting with target audience",
                    "Analyze audience feedback and consider creative pivot"
                )
        
        # Check virality potential
        virality_metrics = self.real_time_metrics.get(f"{metrics_key_prefix}virality_coefficient")
        if virality_metrics and len(virality_metrics) >= 2:
            current_virality = virality_metrics[-1]['value']
            
            if current_virality > 3.0:  # High virality detected
                await self._create_artistic_alert(
                    campaign_id, AlertSeverity.INFO, MetricType.VIRALITY,
                    "High Viral Potential Detected",
                    f"Content showing strong viral signals: {current_virality:.2f}x",
                    current_virality, 3.0,
                    "Capitalize on viral momentum with increased budget allocation",
                    "Consider amplifying reach and preparing for scale"
                )

    async def _track_learning_progress(self, campaign_id: str):
        """Track learning system progress and effectiveness"""
        
        # Get learning patterns
        learning_patterns = self.artistic_system.learning_patterns.get(campaign_id, [])
        if not learning_patterns:
            return
        
        # Track pattern detection effectiveness
        recent_patterns = [p for p in learning_patterns if 
                          isinstance(p, dict) and 
                          'generated_at' in p and
                          datetime.fromisoformat(p['generated_at']) > datetime.now() - timedelta(hours=1)]
        
        if recent_patterns:
            # Calculate learning metrics
            avg_confidence = statistics.mean([p.get('confidence', 0) for p in recent_patterns])
            pattern_diversity = len(set([p.get('insight_type', '') for p in recent_patterns]))
            
            learning_metric = LearningMetric(
                metric_id=f"learning_{campaign_id}_{int(time.time())}",
                campaign_id=campaign_id,
                learning_type='pattern_detection',
                value=avg_confidence,
                confidence=avg_confidence,
                data_points=len(recent_patterns),
                timestamp=datetime.now(),
                metadata={
                    'pattern_diversity': pattern_diversity,
                    'total_patterns': len(learning_patterns)
                }
            )
            
            self.learning_metrics[campaign_id].append(learning_metric)
        
        # Track optimization effectiveness
        optimization_history = self.artistic_system.optimization_history.get(campaign_id, [])
        if optimization_history:
            # Calculate effectiveness based on performance improvements
            recent_optimizations = [opt for opt in optimization_history if 
                                  'applied_at' in opt and
                                  datetime.fromisoformat(opt['applied_at']) > datetime.now() - timedelta(hours=6)]
            
            if recent_optimizations:
                effectiveness_scores = []
                for opt in recent_optimizations:
                    expected_improvement = opt.get('expected_improvement', 0)
                    # In a real system, we'd measure actual improvement
                    actual_improvement = expected_improvement * (0.7 + 0.3 * avg_confidence)  # Simulated
                    effectiveness = actual_improvement / expected_improvement if expected_improvement > 0 else 1.0
                    effectiveness_scores.append(effectiveness)
                
                self.optimization_effectiveness[campaign_id].extend(effectiveness_scores)

    async def _calculate_artistic_health(self, campaign_id: str) -> ArtisticHealthScore:
        """Calculate comprehensive artistic campaign health score"""
        
        # Get latest performance data
        performance_history = self.artistic_system.campaign_history.get(campaign_id, [])
        if not performance_history:
            return ArtisticHealthScore(
                campaign_id=campaign_id,
                overall_score=0,
                creative_resonance_score=0,
                audience_engagement_score=0,
                artistic_appreciation_score=0,
                virality_potential_score=0,
                cost_effectiveness_score=0,
                learning_progress_score=0,
                health_status='insufficient_data',
                critical_issues=['No performance data available'],
                recommendations=['Wait for campaign data to accumulate'],
                artistic_insights=['Campaign needs more runtime for analysis'],
                last_updated=datetime.now()
            )
        
        latest_performance = performance_history[-1]
        
        # Calculate component scores (0-100)
        creative_resonance = latest_performance.creative_resonance_score * 100
        audience_engagement = latest_performance.engagement_rate * 1000  # Scale up
        artistic_appreciation = latest_performance.artistic_appreciation_score * 100
        
        # Virality potential (normalized)
        virality_potential = min(latest_performance.virality_coefficient / 5.0, 1.0) * 100
        
        # Cost effectiveness (inverse of cost per engagement, normalized)
        cost_effectiveness = max(0, 100 - (latest_performance.cost_per_engagement * 10))
        
        # Learning progress (based on learning metrics)
        learning_metrics = self.learning_metrics.get(campaign_id, [])
        if learning_metrics:
            recent_learning = [m for m in learning_metrics if 
                              m.timestamp > datetime.now() - timedelta(hours=24)]
            learning_progress = statistics.mean([m.value for m in recent_learning]) * 100 if recent_learning else 0
        else:
            learning_progress = 0
        
        # Overall score (weighted average)
        overall_score = (
            creative_resonance * 0.25 +
            audience_engagement * 0.20 +
            artistic_appreciation * 0.20 +
            virality_potential * 0.15 +
            cost_effectiveness * 0.10 +
            learning_progress * 0.10
        )
        
        # Determine health status
        if overall_score >= 80:
            health_status = 'excellent'
        elif overall_score >= 60:
            health_status = 'good'
        elif overall_score >= 40:
            health_status = 'fair'
        else:
            health_status = 'poor'
        
        # Generate issues and recommendations
        critical_issues = []
        recommendations = []
        artistic_insights = []
        
        if creative_resonance < 50:
            critical_issues.append("Low creative resonance with audience")
            recommendations.append("Review creative strategy and audience alignment")
        
        if artistic_appreciation < 60:
            critical_issues.append("Below-average artistic appreciation")
            recommendations.append("Consider artistic style adjustments based on feedback")
            artistic_insights.append("Audience may prefer different artistic approach")
        
        if cost_effectiveness < 40:
            critical_issues.append("High cost per engagement")
            recommendations.append("Optimize targeting and budget allocation")
        
        if learning_progress < 30:
            recommendations.append("Increase data collection for better learning")
        
        # Positive insights
        if virality_potential > 70:
            artistic_insights.append("Strong viral potential - consider amplification")
        
        if audience_engagement > 80:
            artistic_insights.append("Excellent audience engagement - replicate approach")
        
        return ArtisticHealthScore(
            campaign_id=campaign_id,
            overall_score=round(overall_score, 1),
            creative_resonance_score=round(creative_resonance, 1),
            audience_engagement_score=round(audience_engagement, 1),
            artistic_appreciation_score=round(artistic_appreciation, 1),
            virality_potential_score=round(virality_potential, 1),
            cost_effectiveness_score=round(cost_effectiveness, 1),
            learning_progress_score=round(learning_progress, 1),
            health_status=health_status,
            critical_issues=critical_issues,
            recommendations=recommendations,
            artistic_insights=artistic_insights,
            last_updated=datetime.now()
        )

    async def _generate_artistic_insights(self, campaign_id: str):
        """Generate artistic-specific insights"""
        
        insights = []
        
        # Analyze artistic trends
        performance_history = self.artistic_system.campaign_history.get(campaign_id, [])
        if len(performance_history) >= 5:
            # Trend analysis for artistic appreciation
            appreciation_trend = [p.artistic_appreciation_score for p in performance_history[-5:]]
            if len(appreciation_trend) >= 3:
                trend_slope = (appreciation_trend[-1] - appreciation_trend[0]) / len(appreciation_trend)
                
                if trend_slope > 0.02:  # Improving
                    insights.append("Artistic appreciation is trending upward - current approach is resonating")
                elif trend_slope < -0.02:  # Declining
                    insights.append("Artistic appreciation declining - consider creative strategy review")
        
        # Analyze creative resonance patterns
        resonance_metrics = self.real_time_metrics.get(f"{campaign_id}_creative_resonance")
        if resonance_metrics and len(resonance_metrics) >= 10:
            recent_resonance = [m['value'] for m in resonance_metrics[-10:]]
            resonance_volatility = statistics.stdev(recent_resonance) if len(recent_resonance) > 1 else 0
            
            if resonance_volatility > 0.2:
                insights.append("High creative resonance volatility - audience response is inconsistent")
            elif resonance_volatility < 0.05:
                insights.append("Consistent creative resonance - stable audience connection")
        
        # Store insights
        self.artistic_insights_cache[campaign_id] = insights

    async def _perform_cross_campaign_analysis(self):
        """Analyze patterns across multiple artistic campaigns"""
        
        if len(self.artistic_system.active_campaigns) < 2:
            return
        
        # Cross-campaign learning insights
        all_campaigns = list(self.artistic_system.active_campaigns.keys())
        
        # Analyze which artistic mediums perform best
        medium_performance = defaultdict(list)
        for campaign_id in all_campaigns:
            campaign_data = self.artistic_system.active_campaigns[campaign_id]
            medium = campaign_data.get('content', {}).get('medium', 'unknown')
            
            performance_history = self.artistic_system.campaign_history.get(campaign_id, [])
            if performance_history:
                avg_engagement = statistics.mean([p.engagement_rate for p in performance_history[-5:]])
                medium_performance[medium].append(avg_engagement)
        
        # Generate cross-campaign insights
        cross_insights = []
        for medium, performances in medium_performance.items():
            if len(performances) >= 2:
                avg_performance = statistics.mean(performances)
                if avg_performance > 0.08:  # High performance threshold
                    cross_insights.append(f"'{medium}' medium showing strong performance (avg: {avg_performance:.1%})")
        
        # Store cross-campaign insights
        if cross_insights:
            self.logger.info(f"🎨 Cross-campaign insights: {'; '.join(cross_insights)}")

    async def _create_artistic_alert(
        self, campaign_id: str, severity: AlertSeverity, metric_type: MetricType,
        title: str, description: str, current_value: float, threshold_value: float,
        recommendation: str, artistic_context: str
    ):
        """Create artistic campaign specific alert"""
        
        alert_id = f"artistic_alert_{int(time.time())}_{campaign_id}"
        
        alert = ArtisticAlert(
            alert_id=alert_id,
            campaign_id=campaign_id,
            severity=severity,
            metric_type=metric_type,
            title=title,
            description=description,
            current_value=current_value,
            threshold_value=threshold_value,
            recommendation=recommendation,
            created_at=datetime.now(),
            artistic_context=artistic_context
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.alert_counts[severity.value] += 1
        
        await self._send_artistic_alert_notification(alert)
        
        self.logger.warning(f"🚨 Artistic alert created: {title} (Campaign: {campaign_id})")

    async def _send_artistic_alert_notification(self, alert: ArtisticAlert):
        """Send artistic campaign alert notification"""
        
        if DUMMY_MODE:
            self.logger.info(f"🎭 DUMMY: Would send artistic alert - {alert.title}")
            return
        
        # In production, integrate with notification systems
        notification_data = {
            'alert_type': 'artistic_campaign',
            'severity': alert.severity.value,
            'campaign_id': alert.campaign_id,
            'title': alert.title,
            'description': alert.description,
            'artistic_context': alert.artistic_context,
            'recommendation': alert.recommendation,
            'timestamp': alert.created_at.isoformat()
        }
        
        self.logger.info(f"📢 Artistic alert notification: {json.dumps(notification_data, indent=2)}")

    async def _cleanup_old_monitoring_data(self):
        """Clean up old monitoring data"""
        
        cutoff_time = datetime.now() - timedelta(days=7)
        
        # Clean old learning metrics
        for campaign_id in list(self.learning_metrics.keys()):
            self.learning_metrics[campaign_id] = [
                m for m in self.learning_metrics[campaign_id]
                if m.timestamp >= cutoff_time
            ]
        
        # Clean old alert history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.created_at >= cutoff_time
        ]

    async def _send_artistic_monitoring_reports(self):
        """Send periodic artistic monitoring reports"""
        
        if DUMMY_MODE:
            self.logger.info("🎭 DUMMY: Would send artistic monitoring reports")
            return
        
        # Generate summary report
        active_campaigns = len(self.artistic_system.active_campaigns)
        total_alerts = len(self.active_alerts)
        avg_health_score = 0
        
        if self.campaign_health_scores:
            avg_health_score = statistics.mean([
                score.overall_score for score in self.campaign_health_scores.values()
            ])
        
        report_data = {
            'report_type': 'artistic_monitoring_summary',
            'timestamp': datetime.now().isoformat(),
            'active_campaigns': active_campaigns,
            'active_alerts': total_alerts,
            'avg_health_score': round(avg_health_score, 1),
            'top_performing_campaigns': self._get_top_performing_campaigns(),
            'learning_progress_summary': self._get_learning_progress_summary()
        }
        
        self.logger.info(f"📊 Artistic monitoring report: {json.dumps(report_data, indent=2)}")

    def _get_top_performing_campaigns(self) -> List[Dict[str, Any]]:
        """Get top performing artistic campaigns"""
        
        campaign_scores = [
            {
                'campaign_id': campaign_id,
                'health_score': score.overall_score,
                'artistic_appreciation': score.artistic_appreciation_score
            }
            for campaign_id, score in self.campaign_health_scores.items()
        ]
        
        # Sort by health score
        campaign_scores.sort(key=lambda x: x['health_score'], reverse=True)
        
        return campaign_scores[:5]  # Top 5

    def _get_learning_progress_summary(self) -> Dict[str, Any]:
        """Get learning progress summary across all campaigns"""
        
        total_insights = sum(len(patterns) for patterns in self.learning_metrics.values())
        
        avg_effectiveness = 0
        if self.optimization_effectiveness:
            all_effectiveness = []
            for effectiveness_list in self.optimization_effectiveness.values():
                all_effectiveness.extend(effectiveness_list)
            if all_effectiveness:
                avg_effectiveness = statistics.mean(all_effectiveness)
        
        return {
            'total_learning_insights': total_insights,
            'avg_optimization_effectiveness': round(avg_effectiveness, 3),
            'campaigns_with_learning': len(self.learning_metrics),
            'pattern_detection_active': len(self.pattern_detection_history)
        }

    # Public API methods
    
    async def get_campaign_health(self, campaign_id: str) -> Optional[ArtisticHealthScore]:
        """Get artistic campaign health score"""
        return self.campaign_health_scores.get(campaign_id)

    async def get_active_alerts(self, campaign_id: Optional[str] = None) -> List[ArtisticAlert]:
        """Get active artistic alerts"""
        if campaign_id:
            return [alert for alert in self.active_alerts.values() 
                   if alert.campaign_id == campaign_id and not alert.resolved]
        return [alert for alert in self.active_alerts.values() if not alert.resolved]

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an artistic alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            return True
        return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an artistic alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            return True
        return False

    async def get_learning_metrics(self, campaign_id: str) -> List[LearningMetric]:
        """Get learning metrics for campaign"""
        return self.learning_metrics.get(campaign_id, [])

    async def get_artistic_insights(self, campaign_id: str) -> List[str]:
        """Get artistic insights for campaign"""
        return self.artistic_insights_cache.get(campaign_id, [])

# Factory function
def create_artistic_monitor(config: Dict[str, Any]) -> ArtisticCampaignMonitor:
    """Create artistic campaign monitoring system"""
    return ArtisticCampaignMonitor(config)