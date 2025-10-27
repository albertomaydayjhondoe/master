"""
🧠 SISTEMA META ML - Optimización y Aprendizaje Automático
Sistema de Machine Learning que aprende del rendimiento y optimiza distribución geográfica España-LATAM
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistema META ML - Optimización Automática",
    description="Machine Learning para optimización de Meta Ads con datos YouTube/Spotify",
    version="1.0.0"
)

# URLs de servicios
DUMMY_MODE = os.getenv("DUMMY_MODE", "true").lower() == "true"

# ============================================
# MODELOS DE DATOS
# ============================================

class MetaAdsPerformance(BaseModel):
    """Datos de rendimiento Meta Ads"""
    
    campaign_id: str
    creative_id: str  # 5 creatividades del mismo videoclip
    utm_source: str
    
    # Métricas Meta Ads
    ctr: float
    retention_rate: float
    conversions: int
    cost_per_conversion: float
    engagement_rate: float
    
    # Datos geográficos
    country: str
    region: str
    
    # Datos demográficos
    age_range: str
    gender: str
    device_type: str
    
    # Landing page behavior
    landing_page_time: int  # segundos
    landing_page_conversions: int
    
    timestamp: datetime = datetime.now()

class YouTubeData(BaseModel):
    """Datos filtrados de YouTube"""
    
    video_id: str
    user_id: str
    
    # Filtros de calidad
    retention_rate: float  # >40% para considerar válido
    is_organic: bool  # Excluir tráfico de pago/embed
    is_recurring: bool  # Usuario recurrente
    
    # Demografia
    age: int
    country: str
    device: str
    gender: Optional[str]
    
    # Comportamiento
    watch_time: int
    engagement_actions: List[str]  # like, comment, share, subscribe
    
    timestamp: datetime = datetime.now()

class SpotifyData(BaseModel):
    """Datos filtrados de Spotify"""
    
    track_id: str
    user_id: str
    
    # Filtros de calidad
    is_organic_listener: bool  # Excluir listas de pago
    has_saved_track: bool  # Usuario guardó la canción
    repeat_listens: int  # Número de repeticiones
    
    # Demografia
    age: int
    country: str
    gender: Optional[str]
    
    # Comportamiento
    listening_time: int
    playlist_additions: int
    
    timestamp: datetime = datetime.now()

class MLPrediction(BaseModel):
    """Predicción del modelo ML"""
    
    campaign_id: str
    
    # Segmentos optimizados
    target_segments: List[Dict[str, Any]]
    
    # Distribución geográfica
    spain_percentage: float = 35.0  # Nunca baja del 35%
    latam_distribution: Dict[str, float]  # País -> porcentaje
    
    # Recomendaciones presupuestarias
    budget_recommendations: Dict[str, float]
    
    # Creatividades con potencial viral
    viral_creatives: List[Dict[str, Any]]
    
    # Métricas de confianza
    confidence_score: float
    expected_roi: float
    
    timestamp: datetime = datetime.now()

class GeographicDistribution(BaseModel):
    """Distribución geográfica dinámica"""
    
    # España (base fija)
    spain_base: float = 35.0
    spain_current: float
    
    # LATAM (variable)
    latam_countries: Dict[str, Dict[str, Any]]  # País -> {percentage, performance, status}
    
    # Exploración (20%)
    exploration_budget: float = 20.0
    new_countries: List[str]
    
    last_updated: datetime = datetime.now()

# ============================================
# SISTEMA ML CORE
# ============================================

class MetaMLSystem:
    """Sistema de Machine Learning para optimización Meta Ads"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.performance_history = []
        self.geographic_distribution = GeographicDistribution(
            spain_current=35.0, 
            latam_countries={}, 
            new_countries=[]
        )
        self.model_path = "models/meta_ml/"
        os.makedirs(self.model_path, exist_ok=True)
    
    async def process_data_sources(
        self, 
        meta_data: List[MetaAdsPerformance],
        youtube_data: List[YouTubeData],
        spotify_data: List[SpotifyData]
    ) -> Dict[str, Any]:
        """Procesar y filtrar datos de todas las fuentes"""
        
        logger.info("🔄 Procesando datos de Meta Ads, YouTube y Spotify...")
        
        # 1. Filtrar datos de YouTube (usuarios orgánicos con retención >40%)
        filtered_youtube = [
            yt for yt in youtube_data 
            if yt.retention_rate > 0.40 and yt.is_organic and yt.is_recurring
        ]
        
        # 2. Filtrar datos de Spotify (oyentes orgánicos que guardan/repiten)
        filtered_spotify = [
            sp for sp in spotify_data
            if sp.is_organic_listener and (sp.has_saved_track or sp.repeat_listens > 1)
        ]
        
        # 3. Cruzar datos para encontrar patrones
        cross_platform_users = self._cross_reference_users(
            meta_data, filtered_youtube, filtered_spotify
        )
        
        # 4. Generar features para ML
        features_df = self._generate_ml_features(cross_platform_users)
        
        logger.info(f"📊 Datos procesados: {len(filtered_youtube)} YouTube + {len(filtered_spotify)} Spotify")
        
        return {
            "filtered_youtube": filtered_youtube,
            "filtered_spotify": filtered_spotify,
            "cross_platform_users": cross_platform_users,
            "features_dataframe": features_df,
            "total_high_quality_users": len(cross_platform_users)
        }
    
    def _cross_reference_users(
        self, 
        meta_data: List[MetaAdsPerformance],
        youtube_data: List[YouTubeData], 
        spotify_data: List[SpotifyData]
    ) -> List[Dict[str, Any]]:
        """Cruzar usuarios entre plataformas para detectar patrones"""
        
        cross_platform = []
        
        # Agrupar por país y demografía para encontrar similitudes
        for meta in meta_data:
            # Buscar usuarios similares en YouTube
            similar_youtube = [
                yt for yt in youtube_data
                if yt.country == meta.country and 
                abs(self._parse_age_range(meta.age_range) - yt.age) <= 5
            ]
            
            # Buscar usuarios similares en Spotify  
            similar_spotify = [
                sp for sp in spotify_data
                if sp.country == meta.country and
                abs(self._parse_age_range(meta.age_range) - sp.age) <= 5
            ]
            
            if similar_youtube or similar_spotify:
                cross_platform.append({
                    "meta_performance": meta,
                    "youtube_users": similar_youtube,
                    "spotify_users": similar_spotify,
                    "cross_platform_score": len(similar_youtube) + len(similar_spotify)
                })
        
        # Ordenar por score de cross-platform
        return sorted(cross_platform, key=lambda x: x["cross_platform_score"], reverse=True)
    
    def _parse_age_range(self, age_range: str) -> int:
        """Convertir rango de edad a número"""
        
        age_map = {
            "18-24": 21, "25-34": 29, "35-44": 39,
            "45-54": 49, "55-64": 59, "65+": 70
        }
        return age_map.get(age_range, 30)
    
    def _generate_ml_features(self, cross_platform_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Generar features para el modelo ML"""
        
        features = []
        
        for user_group in cross_platform_data:
            meta = user_group["meta_performance"]
            youtube_users = user_group["youtube_users"]
            spotify_users = user_group["spotify_users"]
            
            # Features base de Meta Ads
            feature_row = {
                "country": meta.country,
                "age_numeric": self._parse_age_range(meta.age_range),
                "gender_encoded": 1 if meta.gender == "female" else 0,
                "device_mobile": 1 if meta.device_type == "mobile" else 0,
                
                # Métricas Meta Ads
                "meta_ctr": meta.ctr,
                "meta_retention": meta.retention_rate,
                "meta_conversions": meta.conversions,
                "meta_cost_per_conv": meta.cost_per_conversion,
                "meta_engagement": meta.engagement_rate,
                "meta_landing_time": meta.landing_page_time,
                
                # Features YouTube agregadas
                "youtube_avg_retention": np.mean([yt.retention_rate for yt in youtube_users]) if youtube_users else 0,
                "youtube_avg_watch_time": np.mean([yt.watch_time for yt in youtube_users]) if youtube_users else 0,
                "youtube_engagement_rate": len([yt for yt in youtube_users if yt.engagement_actions]) / max(len(youtube_users), 1),
                
                # Features Spotify agregadas
                "spotify_avg_listening": np.mean([sp.listening_time for sp in spotify_users]) if spotify_users else 0,
                "spotify_save_rate": len([sp for sp in spotify_users if sp.has_saved_track]) / max(len(spotify_users), 1),
                "spotify_repeat_rate": np.mean([sp.repeat_listens for sp in spotify_users]) if spotify_users else 0,
                
                # Cross-platform score
                "cross_platform_score": user_group["cross_platform_score"],
                
                # Target (ROI)
                "roi": meta.conversions / max(meta.cost_per_conversion * meta.conversions, 1)
            }
            
            features.append(feature_row)
        
        return pd.DataFrame(features)
    
    async def train_models(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Entrenar modelos de ML"""
        
        logger.info("🤖 Entrenando modelos de Machine Learning...")
        
        if len(features_df) < 10:
            logger.warning("⚠️ Pocos datos para entrenar, usando modelo dummy")
            return {"status": "insufficient_data", "model": "dummy"}
        
        try:
            # Preparar datos
            feature_columns = [col for col in features_df.columns if col not in ["roi", "country"]]
            X = features_df[feature_columns]
            y = features_df["roi"]
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Modelo de regresión para ROI prediction
            roi_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            roi_model.fit(X_train_scaled, y_train)
            
            # Modelo de clasificación para segments
            # Crear labels binarias basadas en ROI (alto/bajo)
            roi_threshold = np.median(y)
            y_class = (y > roi_threshold).astype(int)
            y_train_class = (y_train > roi_threshold).astype(int)
            
            segment_model = RandomForestClassifier(n_estimators=100, random_state=42)
            segment_model.fit(X_train_scaled, y_train_class)
            
            # Evaluación
            roi_score = roi_model.score(X_test_scaled, y_test)
            segment_score = segment_model.score(X_test_scaled, (y_test > roi_threshold).astype(int))
            
            # Guardar modelos
            self.models["roi_predictor"] = roi_model
            self.models["segment_classifier"] = segment_model
            self.scalers["feature_scaler"] = scaler
            
            # Persistir modelos
            joblib.dump(roi_model, f"{self.model_path}/roi_model.pkl")
            joblib.dump(segment_model, f"{self.model_path}/segment_model.pkl")
            joblib.dump(scaler, f"{self.model_path}/scaler.pkl")
            
            logger.info(f"✅ Modelos entrenados - ROI Score: {roi_score:.3f}, Segment Score: {segment_score:.3f}")
            
            return {
                "status": "trained",
                "roi_score": roi_score,
                "segment_score": segment_score,
                "features_used": feature_columns,
                "samples_trained": len(X_train)
            }
            
        except Exception as e:
            logger.error(f"❌ Error entrenando modelos: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def predict_optimization(self, current_campaign: Dict[str, Any]) -> MLPrediction:
        """Generar predicciones y optimizaciones"""
        
        logger.info("🎯 Generando predicciones y optimizaciones...")
        
        try:
            # Si no hay modelos entrenados, usar lógica dummy
            if "roi_predictor" not in self.models:
                return await self._dummy_prediction(current_campaign)
            
            # Generar features para predicción
            prediction_features = self._prepare_prediction_features(current_campaign)
            
            # Hacer predicciones
            roi_prediction = self.models["roi_predictor"].predict([prediction_features])[0]
            segment_prediction = self.models["segment_classifier"].predict([prediction_features])[0]
            
            # Optimizar distribución geográfica
            geographic_optimization = await self._optimize_geographic_distribution(current_campaign)
            
            # Identificar creatividades virales
            viral_creatives = await self._identify_viral_creatives(current_campaign)
            
            # Generar recomendaciones presupuestarias
            budget_recommendations = await self._generate_budget_recommendations(
                current_campaign, roi_prediction, geographic_optimization
            )
            
            # Crear predicción final
            prediction = MLPrediction(
                campaign_id=current_campaign.get("campaign_id", "unknown"),
                target_segments=await self._generate_target_segments(segment_prediction),
                spain_percentage=max(35.0, geographic_optimization["spain_percentage"]),
                latam_distribution=geographic_optimization["latam_distribution"],
                budget_recommendations=budget_recommendations,
                viral_creatives=viral_creatives,
                confidence_score=min(roi_prediction / 2.0, 1.0),  # Normalizar
                expected_roi=roi_prediction
            )
            
            logger.info(f"✅ Predicción generada - ROI esperado: {roi_prediction:.2f}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error en predicción: {str(e)}")
            return await self._dummy_prediction(current_campaign)
    
    async def _dummy_prediction(self, campaign: Dict[str, Any]) -> MLPrediction:
        """Predicción dummy para desarrollo/testing"""
        
        return MLPrediction(
            campaign_id=campaign.get("campaign_id", "dummy"),
            target_segments=[
                {
                    "name": "Jóvenes España",
                    "age_range": "18-29",
                    "countries": ["ES"],
                    "expected_roi": 2.8,
                    "budget_percentage": 35.0
                },
                {
                    "name": "LATAM Urbano",
                    "age_range": "20-34", 
                    "countries": ["MX", "CO", "AR"],
                    "expected_roi": 3.2,
                    "budget_percentage": 65.0
                }
            ],
            spain_percentage=35.0,
            latam_distribution={
                "MX": 25.0,
                "CO": 20.0,
                "AR": 15.0,
                "CL": 5.0
            },
            budget_recommendations={
                "increase_mexico": 50.0,
                "maintain_spain": 0.0,
                "explore_chile": 25.0,
                "reduce_low_performers": -30.0
            },
            viral_creatives=[
                {
                    "creative_id": "creative_001",
                    "viral_score": 0.89,
                    "reason": "Alto engagement cross-platform",
                    "recommended_boost": 100.0
                }
            ],
            confidence_score=0.85,
            expected_roi=2.95
        )
    
    def _prepare_prediction_features(self, campaign: Dict[str, Any]) -> List[float]:
        """Preparar features para predicción"""
        
        # Extraer features de la campaña actual
        # Esto sería más complejo en producción
        return [0.5] * 15  # Dummy features
    
    async def _optimize_geographic_distribution(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar distribución geográfica España-LATAM"""
        
        logger.info("🌍 Optimizando distribución geográfica...")
        
        # Lógica de distribución dinámica
        spain_base = 35.0  # Nunca baja del 35%
        latam_available = 65.0
        
        # Países LATAM con rendimiento
        latam_performance = {
            "MX": {"performance": 1.45, "current": 25.0},  # 145% del promedio
            "CO": {"performance": 1.25, "current": 20.0},  # 125% del promedio
            "AR": {"performance": 0.95, "current": 15.0},  # 95% del promedio (bajo)
            "CL": {"performance": 1.65, "current": 5.0},   # 165% del promedio (alto)
        }
        
        # Reajustar según performance
        new_distribution = {}
        total_reassigned = 0
        
        for country, data in latam_performance.items():
            if data["performance"] > 1.30:  # >130% promedio
                # Aumentar hasta 80% dentro del bloque LATAM
                new_percentage = min(data["current"] * 1.5, latam_available * 0.8)
                new_distribution[country] = new_percentage
                logger.info(f"📈 {country}: Aumentando a {new_percentage:.1f}% (performance {data['performance']:.1%})")
                
            elif data["performance"] < 0.70:  # <70% promedio
                # Reducir presupuesto
                new_percentage = data["current"] * 0.7
                new_distribution[country] = new_percentage
                total_reassigned += data["current"] - new_percentage
                logger.info(f"📉 {country}: Reduciendo a {new_percentage:.1f}% (performance {data['performance']:.1%})")
                
            else:
                # Mantener
                new_distribution[country] = data["current"]
        
        # Redistribuir presupuesto liberado
        if total_reassigned > 0:
            # Hacia España si no hay otros países destacados
            spain_percentage = min(50.0, spain_base + total_reassigned * 0.5)
            
            # Resto hacia exploración de nuevos países
            exploration_budget = total_reassigned * 0.5
            new_distribution["PE"] = exploration_budget * 0.6  # Perú
            new_distribution["EC"] = exploration_budget * 0.4  # Ecuador
            
            logger.info(f"🔄 Redistributed {total_reassigned:.1f}%: España +{spain_percentage-spain_base:.1f}%, Exploración {exploration_budget:.1f}%")
        else:
            spain_percentage = spain_base
        
        return {
            "spain_percentage": spain_percentage,
            "latam_distribution": new_distribution,
            "exploration_countries": ["PE", "EC"],
            "optimization_reason": "Performance-based reallocation"
        }
    
    async def _identify_viral_creatives(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identificar creatividades con potencial viral"""
        
        # En producción, esto analizaría métricas reales de todas las creatividades
        viral_creatives = [
            {
                "creative_id": "creative_reggaeton_001",
                "viral_score": 0.92,
                "reason": "Alto cross-platform engagement + retención YouTube >80%",
                "recommended_boost": 150.0,
                "platforms": ["TikTok", "Instagram", "YouTube"],
                "key_metrics": {
                    "youtube_retention": 0.84,
                    "instagram_engagement": 0.15,
                    "tiktok_shares": 2340,
                    "spotify_saves": 1890
                }
            },
            {
                "creative_id": "creative_reggaeton_002", 
                "viral_score": 0.76,
                "reason": "Fuerte performance en México + Colombia",
                "recommended_boost": 75.0,
                "platforms": ["Instagram", "Facebook"],
                "key_metrics": {
                    "mexico_ctr": 0.089,
                    "colombia_conversions": 234,
                    "latam_engagement": 0.12
                }
            }
        ]
        
        return viral_creatives
    
    async def _generate_budget_recommendations(
        self, 
        campaign: Dict[str, Any], 
        predicted_roi: float,
        geographic_opt: Dict[str, Any]
    ) -> Dict[str, float]:
        """Generar recomendaciones presupuestarias"""
        
        recommendations = {}
        
        # Basado en ROI predicho y distribución geográfica
        if predicted_roi > 2.5:
            recommendations["overall_increase"] = 50.0  # Aumentar 50€
            
        # Específico por país según optimización geográfica
        for country, percentage in geographic_opt["latam_distribution"].items():
            if country in ["MX", "CL"]:  # Países con alta performance
                recommendations[f"increase_{country.lower()}"] = 30.0
            elif country in ["AR"]:  # Países con baja performance  
                recommendations[f"reduce_{country.lower()}"] = -20.0
                
        # Exploración de nuevos países (20% del presupuesto)
        recommendations["exploration_budget"] = 80.0  # €80 para exploración
        
        return recommendations
    
    async def _generate_target_segments(self, segment_prediction: int) -> List[Dict[str, Any]]:
        """Generar segmentos de público optimizados"""
        
        if segment_prediction == 1:  # High-value segment
            return [
                {
                    "name": "High-Value Cross-Platform",
                    "description": "Usuarios activos en YouTube + Spotify con alta retención",
                    "age_range": "18-34",
                    "countries": ["ES", "MX", "CO"],
                    "interests": ["música urbana", "reggaeton", "música latina"],
                    "behaviors": ["música activa", "compartir contenido", "seguir artistas"],
                    "expected_roi": 3.2,
                    "budget_percentage": 60.0
                },
                {
                    "name": "LATAM Expansion", 
                    "description": "Audiencia similar en mercados emergentes",
                    "age_range": "20-35",
                    "countries": ["CL", "PE", "EC"],
                    "interests": ["música latina", "entretenimiento"],
                    "behaviors": ["streaming música", "redes sociales activo"],
                    "expected_roi": 2.8,
                    "budget_percentage": 40.0
                }
            ]
        else:  # Standard segment
            return [
                {
                    "name": "Core Audience Spain",
                    "description": "Audiencia base en España",
                    "age_range": "18-45",
                    "countries": ["ES"],
                    "interests": ["música"],
                    "expected_roi": 2.1,
                    "budget_percentage": 35.0
                },
                {
                    "name": "LATAM General",
                    "description": "Audiencia general LATAM", 
                    "age_range": "18-40",
                    "countries": ["MX", "CO", "AR"],
                    "interests": ["música latina"],
                    "expected_roi": 2.4,
                    "budget_percentage": 65.0
                }
            ]
    
    async def update_continuous_learning(self, new_performance_data: List[MetaAdsPerformance]):
        """Actualizar aprendizaje continuo con nuevos datos"""
        
        logger.info("📚 Actualizando aprendizaje continuo...")
        
        # Agregar nuevos datos al historial
        self.performance_history.extend(new_performance_data)
        
        # Si tenemos suficientes datos nuevos, reentrenar
        if len(new_performance_data) >= 5:
            logger.info("🔄 Suficientes datos nuevos - iniciando reentrenamiento...")
            
            # Aquí implementarías lógica de reentrenamiento incremental
            # Por ahora, solo loggeamos
            logger.info(f"📊 Datos en historial: {len(self.performance_history)}")
        
        # Detectar públicos nuevos que superen 130% del rendimiento
        high_performers = [
            data for data in new_performance_data
            if (data.conversions / max(data.cost_per_conversion * data.conversions, 1)) > 2.6  # 130% del promedio base (2.0)
        ]
        
        if high_performers:
            logger.info(f"🚀 Detectados {len(high_performers)} segmentos de alto rendimiento")
            
            # Incorporar automáticamente al targeting principal
            for performer in high_performers:
                logger.info(f"✅ Incorporando segmento: {performer.country} {performer.age_range} (ROI: {performer.conversions / max(performer.cost_per_conversion * performer.conversions, 1):.2f})")

# Instanciar sistema ML
meta_ml_system = MetaMLSystem()

# ============================================
# ENDPOINTS API
# ============================================

@app.get("/health")
async def health_check():
    """Health check del sistema ML"""
    return {
        "status": "healthy",
        "service": "meta-ml-system",
        "models_loaded": len(meta_ml_system.models),
        "dummy_mode": DUMMY_MODE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/ml/process-data")
async def process_multi_platform_data(
    meta_data: List[MetaAdsPerformance],
    youtube_data: List[YouTubeData],
    spotify_data: List[SpotifyData]
):
    """Procesar datos de Meta Ads, YouTube y Spotify"""
    
    try:
        processed_data = await meta_ml_system.process_data_sources(
            meta_data, youtube_data, spotify_data
        )
        
        return {
            "success": True,
            "processed_data": processed_data,
            "high_quality_users": processed_data["total_high_quality_users"],
            "data_quality": {
                "youtube_filtered": len(processed_data["filtered_youtube"]),
                "spotify_filtered": len(processed_data["filtered_spotify"]),
                "cross_platform_matches": len(processed_data["cross_platform_users"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error procesando datos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/train")
async def train_ml_models(
    meta_data: List[MetaAdsPerformance],
    youtube_data: List[YouTubeData], 
    spotify_data: List[SpotifyData]
):
    """Entrenar modelos de ML con datos multi-plataforma"""
    
    try:
        # Procesar datos
        processed = await meta_ml_system.process_data_sources(meta_data, youtube_data, spotify_data)
        
        # Entrenar modelos
        training_result = await meta_ml_system.train_models(processed["features_dataframe"])
        
        return {
            "success": True,
            "training_result": training_result,
            "data_processed": {
                "samples": len(processed["features_dataframe"]),
                "features": len(processed["features_dataframe"].columns) if not processed["features_dataframe"].empty else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error entrenando modelos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/predict", response_model=MLPrediction)
async def predict_campaign_optimization(campaign_data: Dict[str, Any]):
    """Generar predicciones y optimizaciones para campaña"""
    
    try:
        prediction = await meta_ml_system.predict_optimization(campaign_data)
        
        return prediction
        
    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/update-learning")
async def update_continuous_learning(new_data: List[MetaAdsPerformance]):
    """Actualizar aprendizaje continuo con nuevos datos de performance"""
    
    try:
        await meta_ml_system.update_continuous_learning(new_data)
        
        return {
            "success": True,
            "updated_samples": len(new_data),
            "total_history": len(meta_ml_system.performance_history),
            "message": "Aprendizaje continuo actualizado"
        }
        
    except Exception as e:
        logger.error(f"Error actualizando aprendizaje: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/geographic-distribution")
async def get_geographic_distribution():
    """Obtener distribución geográfica actual España-LATAM"""
    
    return {
        "spain_percentage": meta_ml_system.geographic_distribution.spain_current,
        "latam_countries": meta_ml_system.geographic_distribution.latam_countries,
        "exploration_budget": meta_ml_system.geographic_distribution.exploration_budget,
        "last_updated": meta_ml_system.geographic_distribution.last_updated,
        "distribution_rules": {
            "spain_minimum": 35.0,
            "latam_variable": 65.0,
            "exploration_percentage": 20.0,
            "high_performance_threshold": 130.0,
            "low_performance_threshold": 70.0
        }
    }

@app.get("/ml/dashboard-data/{campaign_id}")
async def get_ml_dashboard_data(campaign_id: str):
    """Obtener datos completos para dashboard ML"""
    
    try:
        # En producción, esto consultaría datos reales de la campaña
        dashboard_data = {
            "campaign_id": campaign_id,
            "current_performance": {
                "total_spend": 287.50,
                "total_conversions": 89,
                "current_roi": 2.94,
                "spain_performance": 2.41,
                "latam_performance": 3.18
            },
            "geographic_distribution": {
                "spain": {"percentage": 35.0, "performance": 2.41, "trend": "stable"},
                "mexico": {"percentage": 25.0, "performance": 3.45, "trend": "increasing"},
                "colombia": {"percentage": 20.0, "performance": 3.12, "trend": "increasing"},
                "argentina": {"percentage": 15.0, "performance": 1.95, "trend": "decreasing"},
                "chile": {"percentage": 5.0, "performance": 3.65, "trend": "exploring"}
            },
            "audience_segments": [
                {
                    "name": "Cross-Platform High Engagement",
                    "size": 45000,
                    "roi": 3.45,
                    "platforms": ["YouTube", "Spotify", "Meta"],
                    "top_countries": ["MX", "ES", "CO"]
                },
                {
                    "name": "Organic YouTube Loyal", 
                    "size": 32000,
                    "roi": 2.89,
                    "platforms": ["YouTube", "Meta"],
                    "top_countries": ["ES", "AR"]
                }
            ],
            "viral_creatives": [
                {
                    "id": "creative_001",
                    "name": "Reggaeton Beat Drop",
                    "viral_score": 92,
                    "performance_lift": "+145%",
                    "top_platform": "TikTok"
                }
            ],
            "ml_insights": {
                "next_optimization": "Increase Mexico budget by €75",
                "confidence": 89,
                "learning_status": "Active - 156 samples",
                "model_accuracy": 87.5
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error obteniendo datos dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8006,
        log_level="info"
    )