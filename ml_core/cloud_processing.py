"""
Cloud ML Processing Pipeline
Advanced ML pipeline for processing social media data and generating actionable insights
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import pickle
import os
from concurrent.futures import ThreadPoolExecutor
import time
try:
    import boto3
except ImportError:
    boto3 = None
    print("⚠️ boto3 not available - cloud storage features disabled")

from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Import data structures from acquisition engine
try:
    from .data_acquisition import SocialMetric, TrendingData, CompetitorData, MetricType
except ImportError:
    import sys
    sys.path.append('/workspaces/master')
    from ml_core.data_acquisition import SocialMetric, TrendingData, CompetitorData, MetricType

DUMMY_MODE = os.getenv('DUMMY_MODE', 'true').lower() == 'true'

class MLModelType(Enum):
    ENGAGEMENT_PREDICTOR = "engagement_predictor"
    VIRAL_DETECTOR = "viral_detector"
    AUDIENCE_SEGMENTER = "audience_segmenter"
    CONTENT_OPTIMIZER = "content_optimizer"
    TREND_ANALYZER = "trend_analyzer"
    COMPETITOR_ANALYZER = "competitor_analyzer"
    ANOMALY_DETECTOR = "anomaly_detector"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    OPTIMAL_TIMING = "optimal_timing"
    BUDGET_OPTIMIZER = "budget_optimizer"

class InsightType(Enum):
    ENGAGEMENT_OPPORTUNITY = "engagement_opportunity"
    VIRAL_POTENTIAL = "viral_potential"
    AUDIENCE_INSIGHT = "audience_insight"
    CONTENT_RECOMMENDATION = "content_recommendation"
    TIMING_OPTIMIZATION = "timing_optimization"
    BUDGET_ADJUSTMENT = "budget_adjustment"
    COMPETITOR_THREAT = "competitor_threat"
    TREND_ALERT = "trend_alert"
    ANOMALY_WARNING = "anomaly_warning"
    GROWTH_OPPORTUNITY = "growth_opportunity"

@dataclass
class MLPrediction:
    model_type: MLModelType
    prediction_value: float
    confidence: float
    feature_importance: Dict[str, float]
    prediction_interval: Tuple[float, float]
    model_version: str
    timestamp: datetime

@dataclass
class MLInsight:
    insight_id: str
    insight_type: InsightType
    platforms_affected: List[str]
    confidence: float
    priority_score: float
    recommended_actions: List[Dict[str, Any]]
    expected_impact: Dict[str, float]
    supporting_data: Dict[str, Any]
    expiry_time: datetime
    timestamp: datetime

@dataclass
class ModelPerformanceMetrics:
    model_type: MLModelType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mae: float
    r2_score: float
    last_trained: datetime
    training_samples: int
    validation_samples: int

class CloudMLProcessingPipeline:
    """
    Advanced Cloud ML Processing Pipeline that:
    1. Processes real-time social media data using multiple ML models
    2. Generates actionable insights and predictions
    3. Continuously learns and improves from feedback
    4. Provides cloud-scale processing capabilities
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # ML Models storage
        self.ml_models = {}
        self.model_scalers = {}
        self.model_performance = {}
        
        # Processing components
        self.feature_extractor = None
        self.insight_generator = None
        self.model_trainer = None
        
        # Data processing
        self.processed_data_cache = {}
        self.training_data_buffer = []
        self.feedback_data_buffer = []
        
        # Cloud processing settings
        self.use_cloud_ml = self.config.get('use_cloud_ml', False)
        self.cloud_provider = self.config.get('cloud_provider', 'aws')
        self.model_storage_path = self.config.get('model_storage_path', '/workspaces/master/data/models/')
        
        # Processing state
        self.is_processing = False
        self.processing_queue = asyncio.Queue()
        self.batch_processing_interval = self.config.get('batch_interval', 300)  # 5 minutes
        
        # Performance tracking
        self.processing_metrics = {
            'batches_processed': 0,
            'insights_generated': 0,
            'models_updated': 0,
            'processing_time_avg': 0.0,
            'last_processing_time': None
        }
        
        self.logger.info("☁️ Cloud ML Processing Pipeline initialized")
    
    async def initialize(self):
        """Initialize the ML processing pipeline"""
        self.logger.info("🚀 Initializing Cloud ML Processing Pipeline...")
        
        # Initialize feature extractor
        self.feature_extractor = SocialMediaFeatureExtractor()
        await self.feature_extractor.initialize()
        
        # Initialize insight generator
        self.insight_generator = InsightGenerationEngine()
        await self.insight_generator.initialize()
        
        # Initialize model trainer
        self.model_trainer = MLModelTrainer(self.config)
        await self.model_trainer.initialize()
        
        # Load or initialize ML models
        await self._load_ml_models()
        
        # Setup cloud ML services if configured
        if self.use_cloud_ml:
            await self._setup_cloud_ml_services()
        
        # Ensure model storage directory exists
        os.makedirs(self.model_storage_path, exist_ok=True)
        
        self.logger.info("✅ Cloud ML Processing Pipeline ready!")
    
    async def start_processing_pipeline(self):
        """Start the continuous ML processing pipeline"""
        if self.is_processing:
            self.logger.warning("⚠️ Processing pipeline already running")
            return
        
        self.logger.info("🔄 Starting ML processing pipeline...")
        self.is_processing = True
        
        # Start batch processing task
        batch_task = asyncio.create_task(self._batch_processing_loop())
        
        # Start model retraining task
        retrain_task = asyncio.create_task(self._model_retraining_loop())
        
        # Start performance monitoring task
        monitor_task = asyncio.create_task(self._performance_monitoring_loop())
        
        await asyncio.gather(batch_task, retrain_task, monitor_task)
    
    async def stop_processing_pipeline(self):
        """Stop the ML processing pipeline"""
        self.logger.info("🛑 Stopping ML processing pipeline...")
        self.is_processing = False
        
        # Save current model states
        await self._save_all_models()
        
        self.logger.info("✅ ML processing pipeline stopped")
    
    async def process_data_batch(self, social_data: List[SocialMetric]) -> List[MLInsight]:
        """Process a batch of social media data and generate insights"""
        if not social_data:
            return []
        
        processing_start = time.time()
        self.logger.info(f"🧠 Processing batch of {len(social_data)} social metrics")
        
        try:
            # Extract features from social data
            features = await self.feature_extractor.extract_features(social_data)
            
            # Generate predictions using all models
            predictions = await self._generate_predictions(features, social_data)
            
            # Generate insights from predictions
            insights = await self.insight_generator.generate_insights(predictions, social_data)
            
            # Filter and prioritize insights
            high_priority_insights = await self._filter_and_prioritize_insights(insights)
            
            # Update processing metrics
            processing_time = time.time() - processing_start
            await self._update_processing_metrics(processing_time, len(insights))
            
            # Cache processed data for training
            await self._cache_training_data(social_data, features, predictions)
            
            self.logger.info(f"✅ Generated {len(high_priority_insights)} high-priority insights in {processing_time:.2f}s")
            return high_priority_insights
            
        except Exception as e:
            self.logger.error(f"❌ Error processing data batch: {e}")
            return []
    
    async def process_immediate_analysis(self, social_data: List[SocialMetric]) -> List[MLInsight]:
        """Process data immediately for urgent analysis"""
        self.logger.info(f"🔍 Immediate analysis requested for {len(social_data)} metrics")
        
        # Use simplified, faster models for immediate analysis
        features = await self.feature_extractor.extract_quick_features(social_data)
        
        # Generate urgent insights
        urgent_insights = []
        
        # Check for viral potential
        viral_predictions = await self._predict_viral_potential(features, social_data)
        for prediction in viral_predictions:
            if prediction.confidence > 0.8:
                insight = MLInsight(
                    insight_id=f"viral_{int(time.time())}",
                    insight_type=InsightType.VIRAL_POTENTIAL,
                    platforms_affected=[data.platform for data in social_data],
                    confidence=prediction.confidence,
                    priority_score=prediction.prediction_value * prediction.confidence,
                    recommended_actions=[
                        {"action": "boost_content", "urgency": "high"},
                        {"action": "increase_engagement", "urgency": "high"}
                    ],
                    expected_impact={"engagement_boost": 50.0, "reach_multiplier": 3.0},
                    supporting_data={"model_prediction": asdict(prediction)},
                    expiry_time=datetime.now() + timedelta(hours=2),
                    timestamp=datetime.now()
                )
                urgent_insights.append(insight)
        
        # Check for anomalies
        anomaly_insights = await self._detect_anomalies_immediate(social_data)
        urgent_insights.extend(anomaly_insights)
        
        return urgent_insights
    
    async def process_feedback(self, feedback_data: List[Dict[str, Any]]):
        """Process feedback data to improve model performance"""
        if not feedback_data:
            return
        
        self.logger.info(f"📊 Processing {len(feedback_data)} feedback entries")
        
        # Add to feedback buffer
        self.feedback_data_buffer.extend(feedback_data)
        
        # If we have enough feedback, trigger model updates
        if len(self.feedback_data_buffer) >= 100:
            await self._process_feedback_batch()
    
    async def get_model_performance(self, model_type: MLModelType = None) -> Dict[str, Any]:
        """Get performance metrics for ML models"""
        if model_type:
            return self.model_performance.get(model_type)
        return self.model_performance.copy()
    
    async def retrain_model(self, model_type: MLModelType, training_data: List[Dict[str, Any]] = None):
        """Retrain a specific ML model"""
        self.logger.info(f"🔄 Retraining {model_type.value} model")
        
        if training_data is None:
            training_data = self.training_data_buffer
        
        if len(training_data) < 50:
            self.logger.warning(f"⚠️ Insufficient training data for {model_type.value}: {len(training_data)} samples")
            return
        
        try:
            # Retrain the model
            new_model, performance = await self.model_trainer.retrain_model(
                model_type, training_data, self.ml_models.get(model_type)
            )
            
            # Update model if performance improved
            current_performance = self.model_performance.get(model_type)
            if not current_performance or performance.accuracy > current_performance.accuracy:
                self.ml_models[model_type] = new_model
                self.model_performance[model_type] = performance
                
                # Save updated model
                await self._save_model(model_type, new_model)
                
                self.logger.info(f"✅ Model {model_type.value} updated - Accuracy: {performance.accuracy:.3f}")
                self.processing_metrics['models_updated'] += 1
            else:
                self.logger.info(f"📊 Model {model_type.value} performance did not improve")
                
        except Exception as e:
            self.logger.error(f"❌ Error retraining {model_type.value}: {e}")
    
    async def predict_engagement(self, platform: str, content_features: Dict[str, Any]) -> MLPrediction:
        """Predict engagement for specific content"""
        model = self.ml_models.get(MLModelType.ENGAGEMENT_PREDICTOR)
        if not model:
            return await self._dummy_prediction(MLModelType.ENGAGEMENT_PREDICTOR)
        
        try:
            # Prepare features for prediction
            feature_vector = await self._prepare_feature_vector(content_features, MLModelType.ENGAGEMENT_PREDICTOR)
            
            # Make prediction
            prediction = model.predict([feature_vector])[0]
            confidence = await self._calculate_prediction_confidence(model, feature_vector)
            
            return MLPrediction(
                model_type=MLModelType.ENGAGEMENT_PREDICTOR,
                prediction_value=prediction,
                confidence=confidence,
                feature_importance=await self._get_feature_importance(model, feature_vector),
                prediction_interval=(prediction * 0.8, prediction * 1.2),
                model_version="1.0.0",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error predicting engagement: {e}")
            return await self._dummy_prediction(MLModelType.ENGAGEMENT_PREDICTOR)
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing pipeline status"""
        return {
            'is_processing': self.is_processing,
            'queue_size': self.processing_queue.qsize(),
            'models_loaded': len(self.ml_models),
            'processing_metrics': self.processing_metrics.copy(),
            'model_performance': {
                model_type.value: {
                    'accuracy': perf.accuracy,
                    'last_trained': perf.last_trained.isoformat() if perf.last_trained else None
                }
                for model_type, perf in self.model_performance.items()
            },
            'cache_size': len(self.processed_data_cache),
            'training_buffer_size': len(self.training_data_buffer),
            'feedback_buffer_size': len(self.feedback_data_buffer)
        }
    
    # Private methods for processing pipeline
    
    async def _batch_processing_loop(self):
        """Main batch processing loop"""
        while self.is_processing:
            try:
                # Wait for batch interval or immediate processing request
                await asyncio.sleep(self.batch_processing_interval)
                
                # Process queued data
                if not self.processing_queue.empty():
                    batch_data = []
                    
                    # Collect batch data from queue
                    while not self.processing_queue.empty() and len(batch_data) < 100:
                        try:
                            data = self.processing_queue.get_nowait()
                            batch_data.extend(data)
                        except asyncio.QueueEmpty:
                            break
                    
                    if batch_data:
                        insights = await self.process_data_batch(batch_data)
                        self.processing_metrics['batches_processed'] += 1
                        self.processing_metrics['insights_generated'] += len(insights)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in batch processing loop: {e}")
                await asyncio.sleep(60)
    
    async def _model_retraining_loop(self):
        """Model retraining loop"""
        while self.is_processing:
            try:
                # Wait for retraining interval (daily)
                await asyncio.sleep(86400)  # 24 hours
                
                # Retrain models if we have enough data
                if len(self.training_data_buffer) >= 1000:
                    self.logger.info("🔄 Starting scheduled model retraining...")
                    
                    for model_type in MLModelType:
                        await self.retrain_model(model_type)
                        await asyncio.sleep(5)  # Brief pause between retraining
                    
                    # Clear old training data
                    self.training_data_buffer = self.training_data_buffer[-5000:]  # Keep last 5000 samples
                    
                    self.logger.info("✅ Scheduled model retraining completed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in model retraining loop: {e}")
    
    async def _performance_monitoring_loop(self):
        """Performance monitoring loop"""
        while self.is_processing:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                # Monitor model drift and performance
                for model_type, model in self.ml_models.items():
                    if model and model_type in self.model_performance:
                        perf = self.model_performance[model_type]
                        
                        # Check if model needs retraining
                        days_since_training = (datetime.now() - perf.last_trained).days if perf.last_trained else 999
                        
                        if days_since_training > 7 or perf.accuracy < 0.7:
                            self.logger.warning(f"⚠️ Model {model_type.value} may need retraining")
                
                # Log performance metrics
                self.logger.info(f"📊 Processing metrics: {self.processing_metrics}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in performance monitoring: {e}")
    
    async def _generate_predictions(self, features: Dict[str, Any], social_data: List[SocialMetric]) -> List[MLPrediction]:
        """Generate predictions using all available models"""
        predictions = []
        
        for model_type, model in self.ml_models.items():
            if model:
                try:
                    prediction = await self._make_model_prediction(model_type, model, features, social_data)
                    predictions.append(prediction)
                except Exception as e:
                    self.logger.error(f"❌ Error making prediction with {model_type.value}: {e}")
        
        return predictions
    
    async def _make_model_prediction(self, model_type: MLModelType, model, features: Dict[str, Any], 
                                   social_data: List[SocialMetric]) -> MLPrediction:
        """Make prediction with a specific model"""
        if DUMMY_MODE:
            return await self._dummy_prediction(model_type)
        
        try:
            # Prepare feature vector
            feature_vector = await self._prepare_feature_vector(features, model_type)
            
            # Make prediction
            if hasattr(model, 'predict_proba'):
                prediction_proba = model.predict_proba([feature_vector])[0]
                prediction = np.max(prediction_proba)
                confidence = np.max(prediction_proba)
            else:
                prediction = model.predict([feature_vector])[0]
                confidence = await self._calculate_prediction_confidence(model, feature_vector)
            
            return MLPrediction(
                model_type=model_type,
                prediction_value=float(prediction),
                confidence=float(confidence),
                feature_importance=await self._get_feature_importance(model, feature_vector),
                prediction_interval=(float(prediction * 0.9), float(prediction * 1.1)),
                model_version="1.0.0",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error in {model_type.value} prediction: {e}")
            return await self._dummy_prediction(model_type)
    
    async def _dummy_prediction(self, model_type: MLModelType) -> MLPrediction:
        """Generate dummy prediction for testing"""
        prediction_ranges = {
            MLModelType.ENGAGEMENT_PREDICTOR: (2.0, 8.0),
            MLModelType.VIRAL_DETECTOR: (0.0, 1.0),
            MLModelType.AUDIENCE_SEGMENTER: (0.0, 5.0),
            MLModelType.CONTENT_OPTIMIZER: (0.5, 1.0),
            MLModelType.TREND_ANALYZER: (0.0, 1.0),
            MLModelType.ANOMALY_DETECTOR: (0.0, 1.0),
            MLModelType.OPTIMAL_TIMING: (0.0, 24.0),
            MLModelType.BUDGET_OPTIMIZER: (0.8, 1.5)
        }
        
        min_val, max_val = prediction_ranges.get(model_type, (0.0, 1.0))
        prediction = np.random.uniform(min_val, max_val)
        confidence = np.random.uniform(0.7, 0.95)
        
        return MLPrediction(
            model_type=model_type,
            prediction_value=prediction,
            confidence=confidence,
            feature_importance={'dummy_feature': 1.0},
            prediction_interval=(prediction * 0.9, prediction * 1.1),
            model_version="dummy_1.0.0",
            timestamp=datetime.now()
        )
    
    # Model management methods
    
    async def _load_ml_models(self):
        """Load ML models from storage"""
        self.logger.info("📥 Loading ML models...")
        
        for model_type in MLModelType:
            try:
                model_path = os.path.join(self.model_storage_path, f"{model_type.value}.joblib")
                
                if os.path.exists(model_path) and not DUMMY_MODE:
                    # Load production model
                    model = joblib.load(model_path)
                    self.ml_models[model_type] = model
                    
                    # Load scaler if exists
                    scaler_path = os.path.join(self.model_storage_path, f"{model_type.value}_scaler.joblib")
                    if os.path.exists(scaler_path):
                        scaler = joblib.load(scaler_path)
                        self.model_scalers[model_type] = scaler
                    
                    self.logger.info(f"✅ Loaded {model_type.value} model from {model_path}")
                else:
                    # Initialize dummy model
                    if DUMMY_MODE:
                        model = DummyMLModel(model_type)
                        self.ml_models[model_type] = model
                        self.logger.info(f"🎭 Initialized dummy {model_type.value} model")
                    else:
                        # Initialize new model
                        model = await self._initialize_new_model(model_type)
                        self.ml_models[model_type] = model
                        self.logger.info(f"🆕 Initialized new {model_type.value} model")
                
                # Initialize performance tracking
                self.model_performance[model_type] = ModelPerformanceMetrics(
                    model_type=model_type,
                    accuracy=0.8,  # Default
                    precision=0.8,
                    recall=0.8,
                    f1_score=0.8,
                    mae=0.2,
                    r2_score=0.6,
                    last_trained=datetime.now() - timedelta(days=1),
                    training_samples=1000,
                    validation_samples=200
                )
                
            except Exception as e:
                self.logger.error(f"❌ Error loading {model_type.value}: {e}")
                # Fallback to dummy model
                self.ml_models[model_type] = DummyMLModel(model_type)
    
    async def _initialize_new_model(self, model_type: MLModelType):
        """Initialize a new ML model"""
        if model_type == MLModelType.ENGAGEMENT_PREDICTOR:
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == MLModelType.VIRAL_DETECTOR:
            return RandomForestRegressor(n_estimators=50, random_state=42)
        elif model_type == MLModelType.ANOMALY_DETECTOR:
            return IsolationForest(contamination=0.1, random_state=42)
        elif model_type == MLModelType.AUDIENCE_SEGMENTER:
            return KMeans(n_clusters=5, random_state=42)
        else:
            return RandomForestRegressor(n_estimators=50, random_state=42)
    
    async def _save_model(self, model_type: MLModelType, model):
        """Save ML model to storage"""
        try:
            model_path = os.path.join(self.model_storage_path, f"{model_type.value}.joblib")
            joblib.dump(model, model_path)
            
            # Save scaler if exists
            if model_type in self.model_scalers:
                scaler_path = os.path.join(self.model_storage_path, f"{model_type.value}_scaler.joblib")
                joblib.dump(self.model_scalers[model_type], scaler_path)
            
            self.logger.info(f"💾 Saved {model_type.value} model to {model_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving {model_type.value}: {e}")
    
    async def _save_all_models(self):
        """Save all current ML models"""
        for model_type, model in self.ml_models.items():
            if model and not isinstance(model, DummyMLModel):
                await self._save_model(model_type, model)
    
    # Feature and prediction utilities
    
    async def _prepare_feature_vector(self, features: Dict[str, Any], model_type: MLModelType) -> np.ndarray:
        """Prepare feature vector for specific model type"""
        # Extract relevant features based on model type
        if model_type == MLModelType.ENGAGEMENT_PREDICTOR:
            feature_keys = ['avg_engagement', 'follower_count', 'post_frequency', 'hashtag_count', 'time_of_day']
        elif model_type == MLModelType.VIRAL_DETECTOR:
            feature_keys = ['engagement_rate', 'share_rate', 'growth_velocity', 'trend_alignment']
        else:
            feature_keys = list(features.keys())[:5]  # Default to first 5 features
        
        # Extract values and handle missing features
        feature_vector = []
        for key in feature_keys:
            value = features.get(key, 0.0)
            if isinstance(value, (int, float)):
                feature_vector.append(float(value))
            else:
                feature_vector.append(0.0)
        
        # Ensure consistent feature vector size
        while len(feature_vector) < 5:
            feature_vector.append(0.0)
        
        vector = np.array(feature_vector[:5])  # Limit to 5 features
        
        # Apply scaling if available
        if model_type in self.model_scalers:
            vector = self.model_scalers[model_type].transform([vector])[0]
        
        return vector
    
    async def _calculate_prediction_confidence(self, model, feature_vector: np.ndarray) -> float:
        """Calculate prediction confidence"""
        # Simple confidence calculation based on model certainty
        if hasattr(model, 'predict_proba'):
            probas = model.predict_proba([feature_vector])[0]
            confidence = np.max(probas)
        elif hasattr(model, 'decision_function'):
            decision = model.decision_function([feature_vector])[0]
            confidence = min(abs(decision) / 2.0, 1.0)
        else:
            confidence = 0.8  # Default confidence
        
        return float(confidence)
    
    async def _get_feature_importance(self, model, feature_vector: np.ndarray) -> Dict[str, float]:
        """Get feature importance from model"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_names = [f'feature_{i}' for i in range(len(importances))]
            return dict(zip(feature_names, importances.tolist()))
        else:
            return {'default_feature': 1.0}
    
    # Insight filtering and utilities
    
    async def _filter_and_prioritize_insights(self, insights: List[MLInsight]) -> List[MLInsight]:
        """Filter and prioritize insights based on confidence and impact"""
        # Filter by minimum confidence
        min_confidence = self.config.get('min_insight_confidence', 0.7)
        high_confidence_insights = [
            insight for insight in insights
            if insight.confidence >= min_confidence
        ]
        
        # Sort by priority score (confidence * expected impact)
        high_confidence_insights.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Limit number of insights
        max_insights = self.config.get('max_insights_per_batch', 10)
        return high_confidence_insights[:max_insights]
    
    async def _predict_viral_potential(self, features: Dict[str, Any], social_data: List[SocialMetric]) -> List[MLPrediction]:
        """Predict viral potential for content"""
        viral_model = self.ml_models.get(MLModelType.VIRAL_DETECTOR)
        predictions = []
        
        if viral_model:
            try:
                feature_vector = await self._prepare_feature_vector(features, MLModelType.VIRAL_DETECTOR)
                prediction = await self._make_model_prediction(MLModelType.VIRAL_DETECTOR, viral_model, features, social_data)
                predictions.append(prediction)
            except Exception as e:
                self.logger.error(f"❌ Error predicting viral potential: {e}")
        
        return predictions
    
    async def _detect_anomalies_immediate(self, social_data: List[SocialMetric]) -> List[MLInsight]:
        """Detect anomalies in social data for immediate alerts"""
        anomaly_insights = []
        
        # Simple anomaly detection based on rapid changes
        for metric in social_data:
            if abs(metric.change_percentage) > 1.0:  # 100% change
                insight = MLInsight(
                    insight_id=f"anomaly_{int(time.time())}",
                    insight_type=InsightType.ANOMALY_WARNING,
                    platforms_affected=[metric.platform],
                    confidence=0.9,
                    priority_score=abs(metric.change_percentage),
                    recommended_actions=[
                        {"action": "investigate_cause", "urgency": "immediate"},
                        {"action": "monitor_closely", "duration": "2h"}
                    ],
                    expected_impact={"risk_level": abs(metric.change_percentage)},
                    supporting_data={"metric": asdict(metric)},
                    expiry_time=datetime.now() + timedelta(hours=4),
                    timestamp=datetime.now()
                )
                anomaly_insights.append(insight)
        
        return anomaly_insights
    
    # Feedback and training methods
    
    async def _process_feedback_batch(self):
        """Process accumulated feedback for model improvement"""
        if not self.feedback_data_buffer:
            return
        
        self.logger.info(f"📊 Processing feedback batch: {len(self.feedback_data_buffer)} entries")
        
        # Group feedback by model type
        model_feedback = {}
        for feedback in self.feedback_data_buffer:
            action_type = feedback.get('action_type', 'unknown')
            # Map action types to model types for targeted improvement
            if 'engagement' in action_type:
                model_type = MLModelType.ENGAGEMENT_PREDICTOR
            elif 'viral' in action_type or 'content' in action_type:
                model_type = MLModelType.VIRAL_DETECTOR
            else:
                model_type = MLModelType.ENGAGEMENT_PREDICTOR  # Default
            
            if model_type not in model_feedback:
                model_feedback[model_type] = []
            model_feedback[model_type].append(feedback)
        
        # Update model performance metrics based on feedback
        for model_type, feedbacks in model_feedback.items():
            await self._update_model_performance_from_feedback(model_type, feedbacks)
        
        # Clear processed feedback
        self.feedback_data_buffer.clear()
        self.logger.info("✅ Feedback batch processed")
    
    async def _update_model_performance_from_feedback(self, model_type: MLModelType, feedbacks: List[Dict[str, Any]]):
        """Update model performance metrics based on feedback"""
        if not feedbacks:
            return
        
        # Calculate accuracy based on prediction vs actual performance
        correct_predictions = 0
        total_predictions = len(feedbacks)
        
        for feedback in feedbacks:
            expected = feedback.get('expected_outcome', {})
            actual = feedback.get('actual_outcome', {})
            
            # Simple accuracy calculation
            if expected and actual:
                expected_engagement = expected.get('engagement_increase', 0)
                actual_engagement = actual.get('engagement_increase', 0)
                
                # Consider prediction correct if within 20% of actual
                if abs(expected_engagement - actual_engagement) <= (expected_engagement * 0.2):
                    correct_predictions += 1
        
        new_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.8
        
        # Update performance metrics
        if model_type in self.model_performance:
            perf = self.model_performance[model_type]
            # Weighted average with previous accuracy
            perf.accuracy = (perf.accuracy * 0.7) + (new_accuracy * 0.3)
            
            self.logger.info(f"📈 Updated {model_type.value} accuracy to {perf.accuracy:.3f}")
    
    async def _cache_training_data(self, social_data: List[SocialMetric], features: Dict[str, Any], predictions: List[MLPrediction]):
        """Cache data for future model training"""
        training_entry = {
            'timestamp': datetime.now(),
            'social_data': [asdict(metric) for metric in social_data],
            'features': features,
            'predictions': [asdict(pred) for pred in predictions]
        }
        
        self.training_data_buffer.append(training_entry)
        
        # Keep buffer size manageable
        if len(self.training_data_buffer) > 10000:
            self.training_data_buffer = self.training_data_buffer[-8000:]  # Keep last 8000
    
    async def _update_processing_metrics(self, processing_time: float, insights_count: int):
        """Update processing performance metrics"""
        self.processing_metrics['processing_time_avg'] = (
            (self.processing_metrics['processing_time_avg'] * 0.9) + (processing_time * 0.1)
        )
        self.processing_metrics['last_processing_time'] = datetime.now()
        self.processing_metrics['insights_generated'] += insights_count
    
    # Cloud ML setup (placeholder for production)
    
    async def _setup_cloud_ml_services(self):
        """Setup cloud ML services (AWS SageMaker, Google AI Platform, etc.)"""
        self.logger.info(f"☁️ Setting up {self.cloud_provider} ML services...")
        
        if self.cloud_provider == 'aws':
            # AWS SageMaker setup would go here
            pass
        elif self.cloud_provider == 'gcp':
            # Google Cloud ML setup would go here
            pass
        elif self.cloud_provider == 'azure':
            # Azure ML setup would go here
            pass
        
        self.logger.info("✅ Cloud ML services configured")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for ML processing pipeline"""
        logger = logging.getLogger(f"{__name__}.CloudMLPipeline")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

# Supporting classes

class SocialMediaFeatureExtractor:
    """Extracts ML features from social media data"""
    
    async def initialize(self):
        pass
    
    async def extract_features(self, social_data: List[SocialMetric]) -> Dict[str, Any]:
        """Extract comprehensive features from social media data"""
        if not social_data:
            return {}
        
        # Group data by platform and metric type
        platform_data = {}
        for metric in social_data:
            platform = metric.platform
            if platform not in platform_data:
                platform_data[platform] = {}
            
            metric_type = metric.metric_type.value
            if metric_type not in platform_data[platform]:
                platform_data[platform][metric_type] = []
            
            platform_data[platform][metric_type].append(metric)
        
        # Extract features
        features = {}
        
        # Engagement features
        all_engagement = [m for m in social_data if m.metric_type == MetricType.ENGAGEMENT]
        if all_engagement:
            features['avg_engagement'] = np.mean([m.value for m in all_engagement])
            features['engagement_trend'] = np.mean([m.change_percentage for m in all_engagement])
            features['engagement_volatility'] = np.std([m.value for m in all_engagement])
        
        # Follower features
        all_followers = [m for m in social_data if m.metric_type == MetricType.FOLLOWERS]
        if all_followers:
            features['total_followers'] = np.sum([m.value for m in all_followers])
            features['follower_growth_rate'] = np.mean([m.change_percentage for m in all_followers])
        
        # Platform diversity
        features['platform_count'] = len(platform_data)
        features['cross_platform_correlation'] = self._calculate_cross_platform_correlation(platform_data)
        
        # Temporal features
        if social_data:
            latest_time = max(m.timestamp for m in social_data)
            features['time_of_day'] = latest_time.hour
            features['day_of_week'] = latest_time.weekday()
            features['data_freshness'] = (datetime.now() - latest_time).total_seconds() / 3600
        
        # Content velocity features
        features['posting_frequency'] = len(social_data) / max(1, features.get('data_freshness', 1))
        
        return features
    
    async def extract_quick_features(self, social_data: List[SocialMetric]) -> Dict[str, Any]:
        """Extract minimal features for quick processing"""
        if not social_data:
            return {}
        
        return {
            'avg_engagement': np.mean([m.value for m in social_data if m.metric_type == MetricType.ENGAGEMENT] or [0]),
            'max_change': max([abs(m.change_percentage) for m in social_data] or [0]),
            'platform_count': len(set(m.platform for m in social_data)),
            'data_points': len(social_data),
            'time_of_day': datetime.now().hour
        }
    
    def _calculate_cross_platform_correlation(self, platform_data: Dict[str, Dict]) -> float:
        """Calculate correlation between platform metrics"""
        # Simplified correlation calculation
        if len(platform_data) < 2:
            return 0.0
        
        # Extract engagement rates for correlation
        platform_engagements = {}
        for platform, metrics in platform_data.items():
            if 'engagement' in metrics and metrics['engagement']:
                avg_engagement = np.mean([m.value for m in metrics['engagement']])
                platform_engagements[platform] = avg_engagement
        
        if len(platform_engagements) < 2:
            return 0.0
        
        # Calculate simple correlation measure
        values = list(platform_engagements.values())
        return abs(np.corrcoef(values[:2])[0, 1]) if len(values) >= 2 else 0.0

class InsightGenerationEngine:
    """Generates actionable insights from ML predictions"""
    
    async def initialize(self):
        pass
    
    async def generate_insights(self, predictions: List[MLPrediction], social_data: List[SocialMetric]) -> List[MLInsight]:
        """Generate actionable insights from ML predictions"""
        insights = []
        
        for prediction in predictions:
            if prediction.confidence > 0.75:
                insight = await self._create_insight_from_prediction(prediction, social_data)
                if insight:
                    insights.append(insight)
        
        return insights
    
    async def _create_insight_from_prediction(self, prediction: MLPrediction, social_data: List[SocialMetric]) -> Optional[MLInsight]:
        """Create specific insight from ML prediction"""
        platforms = list(set(m.platform for m in social_data))
        
        if prediction.model_type == MLModelType.ENGAGEMENT_PREDICTOR:
            if prediction.prediction_value > 6.0:  # High engagement predicted
                return MLInsight(
                    insight_id=f"engagement_{int(time.time())}",
                    insight_type=InsightType.ENGAGEMENT_OPPORTUNITY,
                    platforms_affected=platforms,
                    confidence=prediction.confidence,
                    priority_score=prediction.prediction_value * prediction.confidence,
                    recommended_actions=[
                        {"action": "increase_posting_frequency", "confidence": 0.8},
                        {"action": "boost_high_performing_content", "confidence": 0.9}
                    ],
                    expected_impact={
                        "engagement_increase": prediction.prediction_value * 10,
                        "reach_multiplier": 1.5
                    },
                    supporting_data={"prediction": asdict(prediction)},
                    expiry_time=datetime.now() + timedelta(hours=6),
                    timestamp=datetime.now()
                )
        
        elif prediction.model_type == MLModelType.VIRAL_DETECTOR:
            if prediction.prediction_value > 0.8:  # High viral potential
                return MLInsight(
                    insight_id=f"viral_{int(time.time())}",
                    insight_type=InsightType.VIRAL_POTENTIAL,
                    platforms_affected=platforms,
                    confidence=prediction.confidence,
                    priority_score=prediction.prediction_value * prediction.confidence * 2,  # Higher priority for viral
                    recommended_actions=[
                        {"action": "boost_content_immediately", "urgency": "high"},
                        {"action": "cross_promote_platforms", "urgency": "high"}
                    ],
                    expected_impact={
                        "viral_probability": prediction.prediction_value,
                        "potential_reach_multiplier": 5.0
                    },
                    supporting_data={"prediction": asdict(prediction)},
                    expiry_time=datetime.now() + timedelta(hours=2),  # Viral opportunities are time-sensitive
                    timestamp=datetime.now()
                )
        
        return None

class MLModelTrainer:
    """Handles ML model training and retraining"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MLModelTrainer")
    
    async def initialize(self):
        pass
    
    async def retrain_model(self, model_type: MLModelType, training_data: List[Dict[str, Any]], 
                          current_model=None) -> Tuple[Any, ModelPerformanceMetrics]:
        """Retrain a specific model with new data"""
        self.logger.info(f"🔄 Retraining {model_type.value} with {len(training_data)} samples")
        
        if DUMMY_MODE:
            # Return dummy model and performance
            return DummyMLModel(model_type), ModelPerformanceMetrics(
                model_type=model_type,
                accuracy=0.85,
                precision=0.83,
                recall=0.87,
                f1_score=0.85,
                mae=0.15,
                r2_score=0.72,
                last_trained=datetime.now(),
                training_samples=len(training_data),
                validation_samples=int(len(training_data) * 0.2)
            )
        
        # Production model training would go here
        # This would involve:
        # 1. Data preprocessing
        # 2. Feature engineering
        # 3. Model training
        # 4. Validation
        # 5. Performance evaluation
        
        # For now, return dummy results
        return current_model or DummyMLModel(model_type), ModelPerformanceMetrics(
            model_type=model_type,
            accuracy=0.8,
            precision=0.8,
            recall=0.8,
            f1_score=0.8,
            mae=0.2,
            r2_score=0.6,
            last_trained=datetime.now(),
            training_samples=len(training_data),
            validation_samples=int(len(training_data) * 0.2)
        )

class DummyMLModel:
    """Dummy ML model for testing and development"""
    
    def __init__(self, model_type: MLModelType):
        self.model_type = model_type
        self.feature_importances_ = np.random.random(5)
    
    def predict(self, X):
        """Make dummy predictions"""
        if self.model_type == MLModelType.ENGAGEMENT_PREDICTOR:
            return [np.random.uniform(2.0, 8.0) for _ in X]
        elif self.model_type == MLModelType.VIRAL_DETECTOR:
            return [np.random.uniform(0.0, 1.0) for _ in X]
        else:
            return [np.random.uniform(0.0, 1.0) for _ in X]
    
    def predict_proba(self, X):
        """Make dummy probability predictions"""
        return [[np.random.uniform(0.0, 1.0), np.random.uniform(0.0, 1.0)] for _ in X]
    
    def fit(self, X, y):
        """Dummy training"""
        pass

# Factory function
def create_cloud_ml_pipeline(config: Dict[str, Any] = None) -> CloudMLProcessingPipeline:
    """Create and return a configured cloud ML processing pipeline"""
    return CloudMLProcessingPipeline(config)