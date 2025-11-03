"""
Priority Engine Module
Calculates and manages task priorities based on multiple factors.
Optimizes engagement distribution for maximum viral potential.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle
import os

from ..config.telegram_config import TelegramConfig
from ..database.models import UserMetrics, ContentAnalysis, PriorityScore

logger = logging.getLogger(__name__)

class PriorityFactor(Enum):
    """Different factors that influence task priority."""
    USER_ENGAGEMENT_HISTORY = "user_engagement_history"
    CONTENT_VIRAL_POTENTIAL = "content_viral_potential" 
    PLATFORM_ALGORITHM = "platform_algorithm"
    TIME_SENSITIVITY = "time_sensitivity"
    RECIPROCITY_BALANCE = "reciprocity_balance"
    NETWORK_EFFECT = "network_effect"
    RESOURCE_AVAILABILITY = "resource_availability"

@dataclass
class PriorityFactors:
    """Container for priority calculation factors."""
    user_engagement_score: float = 0.0
    viral_potential_score: float = 0.0
    platform_algorithm_score: float = 0.0
    time_sensitivity_score: float = 0.0
    reciprocity_score: float = 0.0
    network_effect_score: float = 0.0
    resource_availability_score: float = 0.0
    
    # Weights for each factor
    weights: Dict[str, float] = field(default_factory=lambda: {
        'user_engagement_score': 0.20,
        'viral_potential_score': 0.25,
        'platform_algorithm_score': 0.15,
        'time_sensitivity_score': 0.15,
        'reciprocity_score': 0.10,
        'network_effect_score': 0.10,
        'resource_availability_score': 0.05
    })

@dataclass 
class PriorityResult:
    """Result of priority calculation."""
    final_score: float
    factors: PriorityFactors
    reasoning: List[str]
    confidence: float
    recommended_timing: Optional[datetime] = None

class PriorityEngine:
    """
    Calculates task priorities using machine learning and heuristic approaches.
    Optimizes for maximum engagement, viral potential, and system efficiency.
    """
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.is_initialized = False
        
        # ML Models (would be loaded from files)
        self.engagement_predictor = None
        self.viral_predictor = None
        self.scaler = StandardScaler()
        
        # Historical data for learning
        self.user_metrics_cache: Dict[int, UserMetrics] = {}
        self.content_analysis_cache: Dict[str, ContentAnalysis] = {}
        self.priority_history: List[PriorityResult] = {}
        
        # Platform-specific factors
        self.platform_peak_hours = {
            'youtube': [(18, 22), (12, 14)],  # Evening and lunch
            'instagram': [(19, 21), (11, 13)], # Evening and late morning
            'tiktok': [(19, 23), (15, 17)],    # Evening and afternoon
            'telegram': [(20, 22), (12, 14)]   # Evening and lunch
        }
        
        self.platform_algorithm_factors = {
            'youtube': {
                'subscriber_ratio_weight': 0.3,
                'watch_time_weight': 0.4,
                'engagement_rate_weight': 0.3
            },
            'instagram': {
                'follower_ratio_weight': 0.25,
                'story_completion_weight': 0.35,
                'save_rate_weight': 0.4
            },
            'tiktok': {
                'completion_rate_weight': 0.4,
                'share_rate_weight': 0.35,
                'comment_rate_weight': 0.25
            }
        }
        
        # Dynamic adjustment factors
        self.learning_rate = 0.1
        self.feedback_history: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize the priority engine and load ML models."""
        try:
            logger.info("Initializing priority engine...")
            
            # Load pre-trained models if available
            await self._load_ml_models()
            
            # Load historical data
            await self._load_historical_data()
            
            # Initialize user metrics cache
            await self._initialize_user_metrics()
            
            self.is_initialized = True
            logger.info("Priority engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize priority engine: {e}")
            raise
    
    async def _load_ml_models(self):
        """Load pre-trained ML models for priority calculation."""
        try:
            model_dir = self.config.ml_models_path or "/tmp/priority_models"
            
            # Load engagement predictor
            engagement_model_path = os.path.join(model_dir, "engagement_predictor.pkl")
            if os.path.exists(engagement_model_path):
                with open(engagement_model_path, 'rb') as f:
                    self.engagement_predictor = pickle.load(f)
                logger.info("Loaded engagement predictor model")
            
            # Load viral potential predictor
            viral_model_path = os.path.join(model_dir, "viral_predictor.pkl")
            if os.path.exists(viral_model_path):
                with open(viral_model_path, 'rb') as f:
                    self.viral_predictor = pickle.load(f)
                logger.info("Loaded viral predictor model")
            
            # Load scaler
            scaler_path = os.path.join(model_dir, "priority_scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("Loaded feature scaler")
                
        except Exception as e:
            logger.warning(f"Could not load ML models: {e}. Using heuristic approach.")
    
    async def _load_historical_data(self):
        """Load historical priority data for learning."""
        try:
            # This would typically load from database
            # For now, initialize empty structures
            self.priority_history = []
            logger.info("Loaded historical priority data")
            
        except Exception as e:
            logger.warning(f"Could not load historical data: {e}")
    
    async def _initialize_user_metrics(self):
        """Initialize user metrics cache."""
        try:
            # This would load from database
            self.user_metrics_cache = {}
            logger.info("Initialized user metrics cache")
            
        except Exception as e:
            logger.warning(f"Could not initialize user metrics: {e}")
    
    async def calculate_priority(self, user_id: int, task_data: Dict[str, Any]) -> float:
        """Calculate priority score for a task."""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Get detailed priority analysis
            priority_result = await self.calculate_detailed_priority(user_id, task_data)
            
            return priority_result.final_score
            
        except Exception as e:
            logger.error(f"Error calculating priority: {e}")
            return 5.0  # Default medium priority
    
    async def calculate_detailed_priority(self, user_id: int, task_data: Dict[str, Any]) -> PriorityResult:
        """Calculate detailed priority with reasoning."""
        
        factors = PriorityFactors()
        reasoning = []
        
        # 1. User Engagement History Score
        factors.user_engagement_score = await self._calculate_user_engagement_score(user_id)
        if factors.user_engagement_score > 7.0:
            reasoning.append("High user engagement history")
        elif factors.user_engagement_score < 3.0:
            reasoning.append("Low user engagement - opportunity for improvement")
        
        # 2. Content Viral Potential Score
        factors.viral_potential_score = await self._calculate_viral_potential(task_data)
        if factors.viral_potential_score > 8.0:
            reasoning.append("High viral potential detected")
        
        # 3. Platform Algorithm Score
        factors.platform_algorithm_score = await self._calculate_platform_algorithm_score(task_data)
        if factors.platform_algorithm_score > 7.0:
            reasoning.append("Favorable platform algorithm conditions")
        
        # 4. Time Sensitivity Score
        factors.time_sensitivity_score = await self._calculate_time_sensitivity(task_data)
        if factors.time_sensitivity_score > 8.0:
            reasoning.append("Optimal timing window detected")
        
        # 5. Reciprocity Balance Score
        factors.reciprocity_score = await self._calculate_reciprocity_score(user_id)
        if factors.reciprocity_score < 3.0:
            reasoning.append("User needs to improve reciprocity balance")
        
        # 6. Network Effect Score
        factors.network_effect_score = await self._calculate_network_effect(user_id, task_data)
        if factors.network_effect_score > 7.0:
            reasoning.append("Strong network effect potential")
        
        # 7. Resource Availability Score
        factors.resource_availability_score = await self._calculate_resource_availability(task_data)
        if factors.resource_availability_score < 4.0:
            reasoning.append("Limited resources available")
        
        # Calculate weighted final score
        final_score = self._calculate_weighted_score(factors)
        
        # Calculate confidence based on data availability
        confidence = await self._calculate_confidence(user_id, task_data, factors)
        
        # Recommend optimal timing
        recommended_timing = await self._calculate_optimal_timing(task_data, factors)
        
        result = PriorityResult(
            final_score=final_score,
            factors=factors,
            reasoning=reasoning,
            confidence=confidence,
            recommended_timing=recommended_timing
        )
        
        # Store for learning
        self.priority_history.append(result)
        
        return result
    
    async def _calculate_user_engagement_score(self, user_id: int) -> float:
        """Calculate user's historical engagement performance."""
        
        if user_id in self.user_metrics_cache:
            metrics = self.user_metrics_cache[user_id]
            
            # Calculate based on historical performance
            engagement_rate = getattr(metrics, 'avg_engagement_rate', 0.05)
            reciprocity_rate = getattr(metrics, 'reciprocity_rate', 0.5)
            consistency_score = getattr(metrics, 'consistency_score', 0.5)
            
            # Weighted combination
            score = (
                engagement_rate * 40 +  # Max 40 points
                reciprocity_rate * 30 + # Max 30 points  
                consistency_score * 30  # Max 30 points
            ) / 10  # Scale to 0-10
            
            return min(max(score, 0.0), 10.0)
        
        # New user - give moderate score
        return 5.0
    
    async def _calculate_viral_potential(self, task_data: Dict[str, Any]) -> float:
        """Calculate content's viral potential using ML if available."""
        
        content_url = task_data.get('content_url', '')
        platform = task_data.get('platform', '')
        
        # Extract features for ML prediction
        features = await self._extract_content_features(content_url, platform)
        
        if self.viral_predictor and features:
            try:
                # Use ML model to predict viral potential
                feature_vector = self._prepare_feature_vector(features)
                prediction = self.viral_predictor.predict_proba([feature_vector])[0]
                
                # Return probability of high engagement
                return prediction[1] * 10 if len(prediction) > 1 else prediction[0] * 10
                
            except Exception as e:
                logger.error(f"ML viral prediction failed: {e}")
        
        # Fallback to heuristic approach
        return await self._heuristic_viral_potential(content_url, platform)
    
    async def _extract_content_features(self, content_url: str, platform: str) -> Optional[Dict[str, Any]]:
        """Extract features from content URL for ML analysis."""
        try:
            features = {
                'platform': platform,
                'url_length': len(content_url),
                'has_timestamp': '?t=' in content_url or '#t=' in content_url,
                'is_short_form': False,
                'hour_posted': datetime.now().hour,
                'day_of_week': datetime.now().weekday()
            }
            
            # Platform-specific feature extraction
            if platform == 'youtube':
                features['is_short_form'] = 'shorts' in content_url
                features['has_playlist'] = 'list=' in content_url
                
            elif platform == 'instagram':
                features['is_reel'] = '/reel/' in content_url
                features['is_story'] = '/stories/' in content_url
                
            elif platform == 'tiktok':
                features['is_short_form'] = True  # All TikTok content is short-form
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    async def _heuristic_viral_potential(self, content_url: str, platform: str) -> float:
        """Calculate viral potential using heuristic rules."""
        
        score = 5.0  # Base score
        
        # Short-form content bonus
        if platform == 'tiktok' or 'shorts' in content_url or '/reel/' in content_url:
            score += 2.0
        
        # Platform-specific factors
        platform_bonuses = {
            'tiktok': 1.5,      # TikTok has highest viral potential
            'instagram': 1.2,   # Instagram reels have good potential
            'youtube': 1.0      # YouTube shorts good, regular videos moderate
        }
        
        score *= platform_bonuses.get(platform, 1.0)
        
        # Time-based factors
        hour = datetime.now().hour
        if platform in self.platform_peak_hours:
            peak_hours = self.platform_peak_hours[platform]
            in_peak = any(start <= hour <= end for start, end in peak_hours)
            if in_peak:
                score += 1.5
        
        return min(score, 10.0)
    
    async def _calculate_platform_algorithm_score(self, task_data: Dict[str, Any]) -> float:
        """Calculate how well the content aligns with platform algorithms."""
        
        platform = task_data.get('platform', '')
        content_url = task_data.get('content_url', '')
        
        base_score = 5.0
        
        if platform not in self.platform_algorithm_factors:
            return base_score
        
        # Time-based algorithm factors
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Platform-specific algorithm optimization
        if platform == 'youtube':
            # YouTube favors consistent uploading and longer watch times
            if 'shorts' in content_url:
                base_score += 1.5  # Shorts get algorithm boost
            
            # Peak hours bonus
            if 18 <= current_hour <= 22:
                base_score += 1.0
                
        elif platform == 'instagram':
            # Instagram favors recent, engaging content
            base_score += 1.0  # Recent posts get boost
            
            if '/reel/' in content_url:
                base_score += 2.0  # Reels heavily favored
            
            # Peak hours bonus
            if 19 <= current_hour <= 21:
                base_score += 1.0
                
        elif platform == 'tiktok':
            # TikTok favors completion rates and shares
            base_score += 1.5  # TikTok algorithm is very active
            
            # Peak hours bonus (TikTok has longer peak window)
            if 19 <= current_hour <= 23:
                base_score += 1.0
        
        # Day of week factors
        weekend_bonus = {
            'youtube': 0.5,
            'instagram': 1.0,
            'tiktok': 1.0
        }
        
        if current_day in [5, 6]:  # Weekend
            base_score += weekend_bonus.get(platform, 0)
        
        return min(base_score, 10.0)
    
    async def _calculate_time_sensitivity(self, task_data: Dict[str, Any]) -> float:
        """Calculate urgency based on timing factors."""
        
        platform = task_data.get('platform', '')
        current_time = datetime.now()
        
        score = 5.0  # Base score
        
        # Check if we're in peak engagement hours
        if platform in self.platform_peak_hours:
            peak_hours = self.platform_peak_hours[platform]
            
            for start_hour, end_hour in peak_hours:
                # Check if current time is within peak hours
                if start_hour <= current_time.hour <= end_hour:
                    score += 3.0
                    break
                
                # Check if peak time is approaching (within 1 hour)
                elif start_hour - 1 <= current_time.hour < start_hour:
                    score += 2.0
                    break
                
                # Check if peak time recently passed (within 1 hour)
                elif end_hour < current_time.hour <= end_hour + 1:
                    score += 1.0
                    break
        
        # Day of week factors
        day_of_week = current_time.weekday()
        
        # Weekend boost for entertainment platforms
        if day_of_week in [5, 6] and platform in ['tiktok', 'instagram']:
            score += 1.0
        
        # Weekday boost for professional content
        elif day_of_week in range(5) and platform == 'youtube':
            score += 0.5
        
        return min(score, 10.0)
    
    async def _calculate_reciprocity_score(self, user_id: int) -> float:
        """Calculate user's reciprocity balance."""
        
        if user_id in self.user_metrics_cache:
            metrics = self.user_metrics_cache[user_id]
            
            tasks_completed = getattr(metrics, 'tasks_completed', 0)
            tasks_received = getattr(metrics, 'tasks_received', 0)
            
            if tasks_received == 0:
                return 10.0  # New user gets high priority
            
            reciprocity_ratio = tasks_completed / tasks_received
            
            # Ideal ratio is around 1.0 (balanced)
            if reciprocity_ratio >= 0.8:
                return 8.0 + min(reciprocity_ratio, 2.0)  # Reward high reciprocity
            elif reciprocity_ratio >= 0.5:
                return 6.0 + reciprocity_ratio * 2
            else:
                return max(reciprocity_ratio * 10, 1.0)  # Low reciprocity gets low priority
        
        return 7.0  # New user gets good starting score
    
    async def _calculate_network_effect(self, user_id: int, task_data: Dict[str, Any]) -> float:
        """Calculate potential network effect of the engagement."""
        
        platform = task_data.get('platform', '')
        
        base_score = 5.0
        
        # Platform network effect multipliers
        network_multipliers = {
            'tiktok': 1.5,      # Strong algorithm amplification
            'instagram': 1.3,   # Good sharing and discovery
            'youtube': 1.2,     # Subscriber notifications
            'telegram': 1.0     # Limited network effect
        }
        
        base_score *= network_multipliers.get(platform, 1.0)
        
        # User influence factors (would be calculated from follower counts, etc.)
        if user_id in self.user_metrics_cache:
            metrics = self.user_metrics_cache[user_id]
            influence_score = getattr(metrics, 'influence_score', 1.0)
            base_score *= influence_score
        
        # Content type network effects
        content_url = task_data.get('content_url', '')
        if 'shorts' in content_url or '/reel/' in content_url or platform == 'tiktok':
            base_score += 1.0  # Short form content spreads faster
        
        return min(base_score, 10.0)
    
    async def _calculate_resource_availability(self, task_data: Dict[str, Any]) -> float:
        """Calculate current resource availability for the platform."""
        
        platform = task_data.get('platform', '')
        
        # This would check actual system resources, account limits, etc.
        # For now, use time-based approximation
        
        current_hour = datetime.now().hour
        
        # Assume resources are more available during off-peak hours
        if 2 <= current_hour <= 8:  # Early morning
            return 9.0
        elif 14 <= current_hour <= 17:  # Afternoon
            return 7.0
        elif 22 <= current_hour <= 24 or 0 <= current_hour <= 2:  # Late night
            return 8.0
        else:  # Peak hours
            return 5.0
    
    def _calculate_weighted_score(self, factors: PriorityFactors) -> float:
        """Calculate final weighted priority score."""
        
        total_score = 0.0
        
        # Apply weights to each factor
        for factor_name, weight in factors.weights.items():
            factor_value = getattr(factors, factor_name, 0.0)
            total_score += factor_value * weight
        
        # Ensure score is within valid range
        return min(max(total_score, 0.0), 10.0)
    
    async def _calculate_confidence(self, user_id: int, task_data: Dict[str, Any], factors: PriorityFactors) -> float:
        """Calculate confidence in the priority calculation."""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on available data
        if user_id in self.user_metrics_cache:
            confidence += 0.2
        
        if task_data.get('content_url'):
            confidence += 0.1
        
        if task_data.get('platform') in self.platform_algorithm_factors:
            confidence += 0.1
        
        # ML model availability increases confidence  
        if self.viral_predictor:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def _calculate_optimal_timing(self, task_data: Dict[str, Any], factors: PriorityFactors) -> Optional[datetime]:
        """Calculate optimal timing for task execution."""
        
        platform = task_data.get('platform', '')
        
        if platform not in self.platform_peak_hours:
            return None
        
        current_time = datetime.now()
        peak_hours = self.platform_peak_hours[platform]
        
        # Find next peak period
        for start_hour, end_hour in peak_hours:
            # Check if we're currently in peak
            if start_hour <= current_time.hour <= end_hour:
                return current_time  # Execute now
            
            # Find next peak today
            elif current_time.hour < start_hour:
                optimal_time = current_time.replace(
                    hour=start_hour, minute=0, second=0, microsecond=0
                )
                return optimal_time
        
        # If no more peaks today, return first peak tomorrow
        tomorrow = current_time + timedelta(days=1)
        first_peak_start = peak_hours[0][0]
        optimal_time = tomorrow.replace(
            hour=first_peak_start, minute=0, second=0, microsecond=0
        )
        
        return optimal_time
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> List[float]:
        """Prepare feature vector for ML model."""
        
        # Convert features to numerical vector
        # This would be customized based on trained model requirements
        vector = [
            float(features.get('url_length', 0)),
            float(features.get('has_timestamp', False)),
            float(features.get('is_short_form', False)),
            float(features.get('hour_posted', 12)),
            float(features.get('day_of_week', 0)),
            # Add more features as needed
        ]
        
        return vector
    
    async def update_priority_weights(self, feedback_data: Dict[str, Any]):
        """Update priority calculation weights based on feedback."""
        
        # This would implement online learning to adjust weights
        # based on actual engagement results vs predicted priorities
        
        self.feedback_history.append(feedback_data)
        
        # Simple learning: adjust weights based on prediction accuracy
        if len(self.feedback_history) >= 10:
            await self._adjust_weights_from_feedback()
    
    async def _adjust_weights_from_feedback(self):
        """Adjust priority weights based on historical feedback."""
        
        # Implement gradient descent or other optimization
        # to improve priority prediction accuracy
        
        logger.info("Adjusting priority weights based on feedback")
        
        # This is a simplified implementation
        # In practice, you'd use more sophisticated optimization
        
        for factor_name in PriorityFactors().weights.keys():
            # Analyze correlation between factor and actual success
            # Adjust weight accordingly
            pass
    
    async def get_user_priority_info(self, user_id: int) -> Dict[str, Any]:
        """Get priority information for a specific user."""
        
        user_metrics = self.user_metrics_cache.get(user_id, None)
        
        return {
            'user_engagement_score': await self._calculate_user_engagement_score(user_id),
            'reciprocity_score': await self._calculate_reciprocity_score(user_id),
            'total_tasks_completed': getattr(user_metrics, 'tasks_completed', 0) if user_metrics else 0,
            'total_tasks_received': getattr(user_metrics, 'tasks_received', 0) if user_metrics else 0,
            'average_priority': sum(
                result.final_score for result in self.priority_history[-10:] 
                if hasattr(result, 'user_id') and getattr(result, 'user_id', None) == user_id
            ) / min(len(self.priority_history), 10) if self.priority_history else 5.0,
            'recommendation': await self._generate_priority_recommendation(user_id)
        }
    
    async def _generate_priority_recommendation(self, user_id: int) -> str:
        """Generate personalized priority improvement recommendations."""
        
        reciprocity_score = await self._calculate_reciprocity_score(user_id)
        engagement_score = await self._calculate_user_engagement_score(user_id)
        
        if reciprocity_score < 3.0:
            return "Mejora tu balance de reciprocidad completando más intercambios"
        elif engagement_score < 4.0:
            return "Enfócate en contenido de mayor calidad para obtener mejor engagement"
        elif reciprocity_score > 8.0 and engagement_score > 7.0:
            return "¡Excelente! Mantienes un balance perfecto de reciprocidad y calidad"
        else:
            return "Continúa con el buen trabajo, tu perfil de prioridad es sólido"
    
    async def analyze_priority_trends(self) -> Dict[str, Any]:
        """Analyze priority calculation trends and performance."""
        
        if not self.priority_history:
            return {'message': 'No hay datos históricos disponibles'}
        
        recent_priorities = self.priority_history[-100:]  # Last 100 calculations
        
        avg_score = sum(result.final_score for result in recent_priorities) / len(recent_priorities)
        
        factor_averages = {}
        for factor_name in PriorityFactors().weights.keys():
            factor_values = [
                getattr(result.factors, factor_name, 0.0) 
                for result in recent_priorities
            ]
            factor_averages[factor_name] = sum(factor_values) / len(factor_values)
        
        return {
            'total_calculations': len(self.priority_history),
            'recent_average_score': round(avg_score, 2),
            'factor_averages': {k: round(v, 2) for k, v in factor_averages.items()},
            'confidence_average': round(
                sum(result.confidence for result in recent_priorities) / len(recent_priorities), 2
            ),
            'most_common_reasoning': self._get_most_common_reasoning(recent_priorities)
        }
    
    def _get_most_common_reasoning(self, priority_results: List[PriorityResult]) -> List[str]:
        """Get most common reasoning patterns from priority calculations."""
        
        reasoning_counts = {}
        
        for result in priority_results:
            for reason in result.reasoning:
                reasoning_counts[reason] = reasoning_counts.get(reason, 0) + 1
        
        # Return top 5 most common reasons
        sorted_reasons = sorted(reasoning_counts.items(), key=lambda x: x[1], reverse=True)
        return [reason for reason, count in sorted_reasons[:5]]
    
    async def start(self):
        """Start the priority engine."""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("Priority engine started")
    
    async def stop(self):
        """Stop the priority engine."""
        # Save models and data if needed
        await self._save_models()
        
        logger.info("Priority engine stopped")
    
    async def _save_models(self):
        """Save ML models and learning data."""
        try:
            model_dir = self.config.ml_models_path or "/tmp/priority_models"
            os.makedirs(model_dir, exist_ok=True)
            
            # Save updated weights and feedback history
            # This would save the learned parameters for next session
            
            logger.info("Saved priority engine models and data")
            
        except Exception as e:
            logger.error(f"Failed to save priority models: {e}")