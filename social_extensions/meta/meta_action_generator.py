"""
Meta Action Generator
Generates ML-driven actions for Meta Ads campaigns
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Import from existing ML system
try:
    from ml_core.action_generation.action_generator import ActionGenerator, ActionRequest, GeneratedAction
    from ml_core.action_generation.ml_predictor import MLPredictor
    # Import types only to avoid circular imports
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from social_extensions.meta.meta_automator import AdMetrics, MLInsight
except ImportError:
    # Fallback for standalone testing
    ActionGenerator = object
    ActionRequest = dict
    GeneratedAction = dict
    MLPredictor = object

class MetaActionType(Enum):
    CREATE_CAMPAIGN = "create_campaign"
    OPTIMIZE_BUDGET = "optimize_budget" 
    PAUSE_AD = "pause_ad"
    SCALE_AUDIENCE = "scale_audience"
    UPDATE_CREATIVE = "update_creative"
    ADJUST_BIDDING = "adjust_bidding"
    LOOKALIKE_EXPANSION = "lookalike_expansion"
    DAYPARTING_OPTIMIZATION = "dayparting_optimization"

@dataclass
class MetaActionContext:
    """Context data for Meta action generation"""
    account_id: str
    campaign_metrics: List[Any]  # AdMetrics objects
    budget_remaining: float
    campaign_objectives: List[str]
    target_roas: float
    max_cpa: float
    performance_window_hours: int = 24
    min_spend_threshold: float = 50.0
    
class MetaActionGenerator(ActionGenerator):
    """ML-powered Meta Ads action generator"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"{__name__}.MetaActionGenerator")
        
        # Meta-specific configuration
        self.meta_config = config.get('meta', {})
        self.min_roas_threshold = self.meta_config.get('min_roas_threshold', 2.0)
        self.max_cpa_threshold = self.meta_config.get('max_cpa_threshold', 50.0)
        self.budget_scale_factor = self.meta_config.get('budget_scale_factor', 1.2)
        
        # Initialize ML predictor for Meta-specific predictions
        self.meta_predictor = MLPredictor(config.get('meta_ml_config', {}))
        
        self.logger.info("🎯 Meta Action Generator initialized")
    
    async def generate_actions(self, request: ActionRequest) -> List[GeneratedAction]:
        """Generate Meta-specific actions based on ML analysis"""
        
        try:
            # Extract Meta context
            context = self._extract_meta_context(request)
            
            # Analyze current performance
            performance_insights = await self._analyze_performance(context)
            
            # Generate ML-driven insights
            ml_insights = await self._generate_ml_insights(context, performance_insights)
            
            # Convert insights to actionable Meta actions
            actions = await self._insights_to_actions(ml_insights, context)
            
            self.logger.info(f"✅ Generated {len(actions)} Meta actions")
            return actions
            
        except Exception as e:
            self.logger.error(f"❌ Error generating Meta actions: {e}")
            return []
    
    def _extract_meta_context(self, request: ActionRequest) -> MetaActionContext:
        """Extract Meta-specific context from request"""
        
        platform_data = request.get('platform_data', {}).get('meta', {})
        
        return MetaActionContext(
            account_id=platform_data.get('account_id', ''),
            campaign_metrics=platform_data.get('metrics', []),
            budget_remaining=platform_data.get('budget_remaining', 1000.0),
            campaign_objectives=platform_data.get('objectives', []),
            target_roas=platform_data.get('target_roas', 3.0),
            max_cpa=platform_data.get('max_cpa', 30.0),
            performance_window_hours=platform_data.get('window_hours', 24)
        )
    
    async def _analyze_performance(self, context: MetaActionContext) -> Dict[str, Any]:
        """Analyze current campaign performance"""
        
        if not context.campaign_metrics:
            return {'status': 'no_data'}
        
        # Aggregate metrics
        total_spend = sum(m.spend for m in context.campaign_metrics)
        total_conversions = sum(m.conversions for m in context.campaign_metrics)
        total_conversion_value = sum(m.conversion_value for m in context.campaign_metrics)
        total_impressions = sum(m.impressions for m in context.campaign_metrics)
        total_clicks = sum(m.clicks for m in context.campaign_metrics)
        
        # Calculate key metrics
        overall_roas = total_conversion_value / total_spend if total_spend > 0 else 0
        overall_cpa = total_spend / total_conversions if total_conversions > 0 else float('inf')
        overall_ctr = total_clicks / total_impressions * 100 if total_impressions > 0 else 0
        overall_cpc = total_spend / total_clicks if total_clicks > 0 else 0
        
        # Performance by time periods
        recent_metrics = [m for m in context.campaign_metrics 
                         if m.timestamp > datetime.now() - timedelta(hours=6)]
        
        recent_roas = 0
        if recent_metrics:
            recent_spend = sum(m.spend for m in recent_metrics)
            recent_value = sum(m.conversion_value for m in recent_metrics)
            recent_roas = recent_value / recent_spend if recent_spend > 0 else 0
        
        # Performance trends
        roas_trend = self._calculate_trend([m.roas for m in context.campaign_metrics[-10:]])
        cpa_trend = self._calculate_trend([m.cpa for m in context.campaign_metrics[-10:]])
        
        return {
            'overall_performance': {
                'roas': overall_roas,
                'cpa': overall_cpa,
                'ctr': overall_ctr,
                'cpc': overall_cpc,
                'total_spend': total_spend,
                'total_conversions': total_conversions
            },
            'recent_performance': {
                'roas': recent_roas
            },
            'trends': {
                'roas_trend': roas_trend,  # 'increasing', 'decreasing', 'stable'
                'cpa_trend': cpa_trend
            },
            'budget_utilization': total_spend / context.budget_remaining if context.budget_remaining > 0 else 1.0
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from time series data"""
        if len(values) < 3:
            return 'stable'
        
        # Simple linear regression slope
        x = np.arange(len(values))
        y = np.array(values)
        
        # Remove inf and nan values
        mask = np.isfinite(y)
        if np.sum(mask) < 3:
            return 'stable'
        
        x_clean = x[mask]
        y_clean = y[mask]
        
        slope = np.corrcoef(x_clean, y_clean)[0, 1] if len(x_clean) > 1 else 0
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    async def _generate_ml_insights(self, context: MetaActionContext, 
                                  performance: Dict[str, Any]) -> List[Any]:
        """Generate ML-driven insights from performance data"""
        
        insights = []
        
        # Performance-based insights
        overall_perf = performance.get('overall_performance', {})
        trends = performance.get('trends', {})
        
        current_roas = overall_perf.get('roas', 0)
        current_cpa = overall_perf.get('cpa', float('inf'))
        
        # 1. Budget scaling opportunities
        if current_roas > context.target_roas * 1.2:  # 20% above target
            confidence = min(0.9, (current_roas / context.target_roas - 1) / 0.5)
            
            # Create insight-like object to avoid circular imports
            insight_data = {
                'insight_id': f"budget_scale_{datetime.now().timestamp()}",
                'campaign_id': context.account_id,
                'insight_type': "budget_scale",
                'score': current_roas,
                'confidence': confidence,
                'recommended_action': {
                    'type': 'scale_budget',
                    'scale_factor': self.budget_scale_factor,
                    'reason': f'High ROAS ({current_roas:.2f}) exceeds target ({context.target_roas:.2f})'
                },
                'generated_at': datetime.now()
            }
            insights.append(insight_data)
        
        # 2. Budget reduction for poor performance
        elif current_roas < context.target_roas * 0.5:  # 50% below target
            confidence = min(0.8, (context.target_roas - current_roas) / context.target_roas)
            
            insight_data = {
                'insight_id': f"budget_reduce_{datetime.now().timestamp()}",
                'campaign_id': context.account_id,
                'insight_type': "budget_reduction",
                'score': current_roas,
                'confidence': confidence,
                'recommended_action': {
                    'type': 'scale_budget',
                    'scale_factor': 0.7,  # Reduce by 30%
                    'reason': f'Low ROAS ({current_roas:.2f}) below target ({context.target_roas:.2f})'
                },
                'generated_at': datetime.now()
            }
            insights.append(insight_data)
        
        # 3. CPA optimization
        if current_cpa > context.max_cpa:
            confidence = min(0.85, (current_cpa / context.max_cpa - 1) / 2)
            
            insights.append(MLInsight(
                insight_id=f"cpa_optimize_{datetime.now().timestamp()}",
                campaign_id=context.account_id,
                insight_type="cpa_optimization",
                score=current_cpa,
                confidence=confidence,
                recommended_action={
                    'type': 'adjust_bidding',
                    'bid_adjustment': -0.2,  # Reduce bids by 20%
                    'reason': f'High CPA ({current_cpa:.2f}) exceeds limit ({context.max_cpa:.2f})'
                },
                generated_at=datetime.now()
            ))
        
        # 4. Trend-based insights
        if trends.get('roas_trend') == 'decreasing':
            insights.append(MLInsight(
                insight_id=f"trend_alert_{datetime.now().timestamp()}",
                campaign_id=context.account_id,
                insight_type="performance_decline",
                score=0.3,  # Low score indicates concern
                confidence=0.7,
                recommended_action={
                    'type': 'creative_refresh',
                    'reason': 'Declining ROAS trend detected - creative fatigue possible'
                },
                generated_at=datetime.now()
            ))
        
        # 5. Audience expansion opportunities
        ctr = overall_perf.get('ctr', 0)
        if ctr > 2.0 and current_roas > context.target_roas:  # High CTR + Good ROAS
            insights.append(MLInsight(
                insight_id=f"audience_expand_{datetime.now().timestamp()}",
                campaign_id=context.account_id,
                insight_type="audience_expansion",
                score=ctr,
                confidence=0.75,
                recommended_action={
                    'type': 'scale_audience',
                    'expansion_factor': 1.3,
                    'reason': f'High CTR ({ctr:.2f}%) indicates audience resonance'
                },
                generated_at=datetime.now()
            ))
        
        # 6. Dayparting optimization
        hourly_performance = self._analyze_hourly_performance(context.campaign_metrics)
        if hourly_performance.get('has_clear_patterns'):
            insights.append(MLInsight(
                insight_id=f"daypart_optimize_{datetime.now().timestamp()}",
                campaign_id=context.account_id,
                insight_type="dayparting",
                score=hourly_performance.get('optimization_potential', 0),
                confidence=0.65,
                recommended_action={
                    'type': 'dayparting_optimization',
                    'optimal_hours': hourly_performance.get('best_hours', []),
                    'reason': 'Clear performance patterns detected across time periods'
                },
                generated_at=datetime.now()
            ))
        
        return insights
    
    def _analyze_hourly_performance(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Analyze performance by hour of day"""
        
        if len(metrics) < 24:  # Need at least 24 hours of data
            return {'has_clear_patterns': False}
        
        # Group by hour
        hourly_data = {}
        for metric in metrics:
            hour = metric.timestamp.hour
            if hour not in hourly_data:
                hourly_data[hour] = {'roas': [], 'cpa': [], 'spend': []}
            
            hourly_data[hour]['roas'].append(metric.roas)
            hourly_data[hour]['cpa'].append(metric.cpa)
            hourly_data[hour]['spend'].append(metric.spend)
        
        # Calculate average performance by hour
        hourly_avg = {}
        for hour, data in hourly_data.items():
            hourly_avg[hour] = {
                'roas': np.mean(data['roas']) if data['roas'] else 0,
                'cpa': np.mean([cpa for cpa in data['cpa'] if cpa != float('inf')]) if data['cpa'] else 0,
                'spend': np.mean(data['spend']) if data['spend'] else 0
            }
        
        # Find best performing hours (top 25% by ROAS)
        roas_values = [(hour, stats['roas']) for hour, stats in hourly_avg.items()]
        roas_values.sort(key=lambda x: x[1], reverse=True)
        
        top_25_pct = int(len(roas_values) * 0.25) or 1
        best_hours = [hour for hour, roas in roas_values[:top_25_pct]]
        
        # Calculate optimization potential (variance in performance)
        roas_variance = np.var([roas for _, roas in roas_values])
        optimization_potential = min(1.0, roas_variance / 2.0)  # Normalize to 0-1
        
        return {
            'has_clear_patterns': optimization_potential > 0.3,
            'best_hours': best_hours,
            'optimization_potential': optimization_potential,
            'hourly_performance': hourly_avg
        }
    
    async def _insights_to_actions(self, insights: List[Any], 
                                 context: MetaActionContext) -> List[Any]:
        """Convert ML insights to executable Meta actions"""
        
        actions = []
        
        for insight in insights:
            if insight.confidence < 0.6:  # Skip low-confidence insights
                continue
            
            action_data = insight.recommended_action
            action_type = action_data.get('type')
            
            # Build common action properties
            base_action = {
                'platform': 'meta',
                'action_type': action_type,
                'priority': self._calculate_priority(insight),
                'confidence': insight.confidence,
                'reasoning': action_data.get('reason', ''),
                'metadata': {
                    'insight_id': insight.insight_id,
                    'insight_score': insight.score,
                    'account_id': context.account_id
                }
            }
            
            # Build action-specific parameters
            if action_type == 'scale_budget':
                actions.append(GeneratedAction(**{
                    **base_action,
                    'action_id': f"meta_budget_scale_{int(datetime.now().timestamp())}",
                    'parameters': {
                        'scale_factor': action_data.get('scale_factor', 1.0),
                        'budget_type': 'daily',
                        'apply_to': 'all_adsets'
                    }
                }))
            
            elif action_type == 'adjust_bidding':
                actions.append(GeneratedAction(**{
                    **base_action,
                    'action_id': f"meta_bid_adjust_{int(datetime.now().timestamp())}",
                    'parameters': {
                        'bid_adjustment': action_data.get('bid_adjustment', 0.0),
                        'adjustment_type': 'percentage',
                        'apply_to': 'underperforming_adsets'
                    }
                }))
            
            elif action_type == 'scale_audience':
                actions.append(GeneratedAction(**{
                    **base_action,
                    'action_id': f"meta_audience_scale_{int(datetime.now().timestamp())}",
                    'parameters': {
                        'expansion_factor': action_data.get('expansion_factor', 1.0),
                        'expansion_type': 'lookalike',
                        'similarity_threshold': 0.8
                    }
                }))
            
            elif action_type == 'creative_refresh':
                actions.append(GeneratedAction(**{
                    **base_action,
                    'action_id': f"meta_creative_refresh_{int(datetime.now().timestamp())}",
                    'parameters': {
                        'refresh_type': 'rotate_existing',
                        'fatigue_threshold': 0.7,
                        'new_creative_count': 2
                    }
                }))
            
            elif action_type == 'dayparting_optimization':
                actions.append(GeneratedAction(**{
                    **base_action,
                    'action_id': f"meta_daypart_{int(datetime.now().timestamp())}",
                    'parameters': {
                        'optimal_hours': action_data.get('optimal_hours', []),
                        'budget_redistribution': True,
                        'pause_poor_hours': True
                    }
                }))
        
        return actions
    
    def _calculate_priority(self, insight: MLInsight) -> str:
        """Calculate action priority based on insight score and confidence"""
        
        # Priority scoring
        priority_score = insight.confidence * insight.score
        
        if insight.insight_type in ['budget_scale', 'cpa_optimization']:
            priority_score *= 1.2  # Boost budget/cost related actions
        
        if priority_score > 0.8:
            return 'high'
        elif priority_score > 0.5:
            return 'medium'
        else:
            return 'low'

# Factory function
def create_meta_action_generator(config: Dict[str, Any]) -> MetaActionGenerator:
    """Create Meta action generator with configuration"""
    return MetaActionGenerator(config)

# Example configuration for Meta actions
def get_meta_action_config() -> Dict[str, Any]:
    """Get example configuration for Meta action generation"""
    return {
        'meta': {
            'min_roas_threshold': 2.0,
            'max_cpa_threshold': 50.0,
            'budget_scale_factor': 1.2,
            'confidence_threshold': 0.6,
            'max_daily_actions': 5
        },
        'meta_ml_config': {
            'model_type': 'ensemble',
            'features': ['roas', 'cpa', 'ctr', 'spend_velocity'],
            'prediction_window_hours': 24,
            'retraining_frequency_days': 7
        }
    }