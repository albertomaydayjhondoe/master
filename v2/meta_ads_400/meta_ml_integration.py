"""
🎯 INTEGRACIÓN META ML - Sistema de Optimización Automática
Integra el sistema Meta ML con el workflow existente de €400
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import requests
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaMLIntegrator:
    """Integrador del sistema Meta ML con el workflow €400"""
    
    def __init__(self):
        self.ml_api_url = "http://localhost:8006"
        self.performance_history = []
        self.learning_active = True
        
    async def integrate_ml_with_campaign(
        self, 
        campaign_data: Dict[str, Any],
        youtube_analytics: Dict[str, Any],
        spotify_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integrar ML con campaña Meta Ads €400"""
        
        logger.info("🧠 Iniciando integración ML con campaña €400...")
        
        try:
            # 1. Procesar datos multi-plataforma
            processed_data = await self._process_multiplatform_data(
                campaign_data, youtube_analytics, spotify_analytics
            )
            
            # 2. Entrenar/actualizar modelos si hay datos suficientes
            if len(processed_data.get("high_quality_samples", [])) >= 10:
                training_result = await self._train_ml_models(processed_data)
                logger.info(f"✅ Modelos ML entrenados: {training_result.get('accuracy', 'N/A')}")
            
            # 3. Generar predicciones y optimizaciones
            ml_predictions = await self._get_ml_predictions(campaign_data)
            
            # 4. Aplicar optimizaciones automáticas
            optimization_actions = await self._apply_ml_optimizations(
                campaign_data, ml_predictions
            )
            
            # 5. Actualizar aprendizaje continuo
            if self.learning_active:
                await self._update_continuous_learning(campaign_data)
            
            return {
                "success": True,
                "ml_integration": {
                    "processed_data": processed_data,
                    "predictions": ml_predictions,
                    "optimizations_applied": optimization_actions,
                    "learning_status": "active" if self.learning_active else "paused"
                },
                "next_actions": await self._generate_next_actions(ml_predictions),
                "performance_boost": self._calculate_performance_boost(optimization_actions)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en integración ML: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_actions": await self._get_fallback_actions(campaign_data)
            }
    
    async def _process_multiplatform_data(
        self,
        campaign_data: Dict[str, Any],
        youtube_analytics: Dict[str, Any], 
        spotify_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Procesar datos de múltiples plataformas"""
        
        logger.info("📊 Procesando datos multi-plataforma...")
        
        # Filtrar datos de YouTube (usuarios orgánicos, retención >40%)
        youtube_filtered = []
        if youtube_analytics.get("viewers"):
            for viewer in youtube_analytics["viewers"]:
                if (viewer.get("retention_rate", 0) > 0.40 and 
                    viewer.get("traffic_source") == "organic" and
                    viewer.get("is_recurring", False)):
                    
                    youtube_filtered.append({
                        "user_id": viewer.get("user_id"),
                        "country": viewer.get("country"),
                        "age": viewer.get("age", 25),
                        "retention_rate": viewer["retention_rate"],
                        "watch_time": viewer.get("watch_time", 0),
                        "engagement_actions": viewer.get("actions", [])
                    })
        
        # Filtrar datos de Spotify (oyentes orgánicos, que guardan/repiten)
        spotify_filtered = []
        if spotify_analytics.get("listeners"):
            for listener in spotify_analytics["listeners"]:
                if (listener.get("playlist_source") != "external_paid" and
                    (listener.get("saved_track", False) or listener.get("repeat_listens", 0) > 1)):
                    
                    spotify_filtered.append({
                        "user_id": listener.get("user_id"),
                        "country": listener.get("country"),
                        "age": listener.get("age", 25),
                        "listening_time": listener.get("listening_time", 0),
                        "repeat_listens": listener.get("repeat_listens", 0),
                        "saved_track": listener.get("saved_track", False)
                    })
        
        # Cruzar datos para encontrar usuarios cross-platform
        cross_platform_users = self._find_cross_platform_users(
            youtube_filtered, spotify_filtered, campaign_data
        )
        
        logger.info(f"📈 Datos procesados: {len(youtube_filtered)} YouTube + {len(spotify_filtered)} Spotify = {len(cross_platform_users)} cross-platform")
        
        return {
            "youtube_organic": youtube_filtered,
            "spotify_organic": spotify_filtered,
            "cross_platform_users": cross_platform_users,
            "high_quality_samples": cross_platform_users,
            "data_quality_score": len(cross_platform_users) / max(len(youtube_filtered) + len(spotify_filtered), 1)
        }
    
    def _find_cross_platform_users(
        self, 
        youtube_data: List[Dict], 
        spotify_data: List[Dict],
        campaign_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Encontrar usuarios que aparecen en múltiples plataformas"""
        
        cross_platform = []
        
        # Agrupar por país y edad para encontrar patrones similares
        youtube_by_demo = {}
        spotify_by_demo = {}
        
        for user in youtube_data:
            key = f"{user['country']}_{user['age']//5*5}"  # Agrupar por rangos de 5 años
            if key not in youtube_by_demo:
                youtube_by_demo[key] = []
            youtube_by_demo[key].append(user)
        
        for user in spotify_data:
            key = f"{user['country']}_{user['age']//5*5}"
            if key not in spotify_by_demo:
                spotify_by_demo[key] = []
            spotify_by_demo[key].append(user)
        
        # Encontrar coincidencias demográficas
        for demo_key in set(youtube_by_demo.keys()) & set(spotify_by_demo.keys()):
            youtube_users = youtube_by_demo[demo_key]
            spotify_users = spotify_by_demo[demo_key]
            
            # Crear perfil combinado
            combined_profile = {
                "demographic_key": demo_key,
                "country": demo_key.split("_")[0],
                "age_range": int(demo_key.split("_")[1]),
                "youtube_metrics": {
                    "avg_retention": sum(u["retention_rate"] for u in youtube_users) / len(youtube_users),
                    "avg_watch_time": sum(u["watch_time"] for u in youtube_users) / len(youtube_users),
                    "engagement_rate": len([u for u in youtube_users if u["engagement_actions"]]) / len(youtube_users)
                },
                "spotify_metrics": {
                    "avg_listening_time": sum(u["listening_time"] for u in spotify_users) / len(spotify_users),
                    "avg_repeats": sum(u["repeat_listens"] for u in spotify_users) / len(spotify_users),
                    "save_rate": len([u for u in spotify_users if u["saved_track"]]) / len(spotify_users)
                },
                "cross_platform_score": len(youtube_users) + len(spotify_users),
                "quality_score": (
                    sum(u["retention_rate"] for u in youtube_users) / len(youtube_users) * 0.5 +
                    sum(u["repeat_listens"] for u in spotify_users) / len(spotify_users) * 0.5
                )
            }
            
            cross_platform.append(combined_profile)
        
        # Ordenar por quality score
        return sorted(cross_platform, key=lambda x: x["quality_score"], reverse=True)
    
    async def _train_ml_models(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Entrenar modelos ML con datos procesados"""
        
        logger.info("🤖 Entrenando modelos ML...")
        
        try:
            # Preparar datos para API
            training_data = {
                "meta_data": self._convert_to_meta_format(processed_data),
                "youtube_data": processed_data["youtube_organic"],
                "spotify_data": processed_data["spotify_organic"]
            }
            
            # Llamar API de entrenamiento
            response = requests.post(
                f"{self.ml_api_url}/ml/train",
                json=training_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Modelos ML entrenados exitosamente")
                return result["training_result"]
            else:
                logger.warning(f"⚠️ Error entrenando modelos: {response.status_code}")
                return {"status": "error", "accuracy": 0}
                
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento ML: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _convert_to_meta_format(self, processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convertir datos procesados al formato esperado por la API Meta"""
        
        meta_format = []
        
        for user in processed_data["cross_platform_users"]:
            # Simular datos Meta Ads basados en cross-platform data
            meta_entry = {
                "campaign_id": "current_campaign",
                "creative_id": f"creative_{user['demographic_key']}",
                "utm_source": "meta_ads",
                "ctr": user["quality_score"] * 0.05,  # Convertir quality a CTR
                "retention_rate": user["youtube_metrics"]["avg_retention"],
                "conversions": int(user["cross_platform_score"] * 0.1),
                "cost_per_conversion": 5.0 / max(user["quality_score"], 0.1),
                "engagement_rate": user["youtube_metrics"]["engagement_rate"],
                "country": user["country"],
                "region": "ES" if user["country"] == "ES" else "LATAM",
                "age_range": f"{user['age_range']}-{user['age_range']+9}",
                "gender": "mixed",
                "device_type": "mobile",
                "landing_page_time": int(user["spotify_metrics"]["avg_listening_time"] / 10),
                "landing_page_conversions": int(user["spotify_metrics"]["save_rate"] * 10),
                "timestamp": datetime.now().isoformat()
            }
            
            meta_format.append(meta_entry)
        
        return meta_format
    
    async def _get_ml_predictions(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener predicciones del sistema ML"""
        
        logger.info("🎯 Obteniendo predicciones ML...")
        
        try:
            response = requests.post(
                f"{self.ml_api_url}/ml/predict",
                json=campaign_data,
                timeout=30
            )
            
            if response.status_code == 200:
                predictions = response.json()
                logger.info(f"✅ Predicciones obtenidas - ROI esperado: {predictions.get('expected_roi', 'N/A')}")
                return predictions
            else:
                logger.warning(f"⚠️ Error obteniendo predicciones: {response.status_code}")
                return await self._get_fallback_predictions()
                
        except Exception as e:
            logger.error(f"❌ Error en predicciones ML: {str(e)}")
            return await self._get_fallback_predictions()
    
    async def _get_fallback_predictions(self) -> Dict[str, Any]:
        """Predicciones de respaldo cuando ML no está disponible"""
        
        return {
            "campaign_id": "fallback",
            "target_segments": [
                {
                    "name": "España Core",
                    "age_range": "18-34",
                    "countries": ["ES"],
                    "expected_roi": 2.5,
                    "budget_percentage": 35.0
                },
                {
                    "name": "LATAM High Potential",
                    "age_range": "20-35", 
                    "countries": ["MX", "CO"],
                    "expected_roi": 3.0,
                    "budget_percentage": 65.0
                }
            ],
            "spain_percentage": 35.0,
            "latam_distribution": {"MX": 30.0, "CO": 25.0, "AR": 10.0},
            "budget_recommendations": {"increase_latam": 25.0},
            "viral_creatives": [],
            "confidence_score": 0.6,
            "expected_roi": 2.7,
            "is_fallback": True
        }
    
    async def _apply_ml_optimizations(
        self, 
        campaign_data: Dict[str, Any],
        ml_predictions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Aplicar optimizaciones basadas en ML"""
        
        logger.info("⚡ Aplicando optimizaciones ML...")
        
        optimizations_applied = []
        
        try:
            # 1. Optimización geográfica (España 35% fijo, LATAM variable)
            if ml_predictions.get("latam_distribution"):
                geo_optimization = await self._apply_geographic_optimization(
                    campaign_data, ml_predictions["latam_distribution"]
                )
                optimizations_applied.append(geo_optimization)
            
            # 2. Optimización de segmentos de audiencia
            if ml_predictions.get("target_segments"):
                audience_optimization = await self._apply_audience_optimization(
                    campaign_data, ml_predictions["target_segments"]
                )
                optimizations_applied.append(audience_optimization)
            
            # 3. Boost de creatividades virales
            if ml_predictions.get("viral_creatives"):
                creative_optimization = await self._apply_creative_optimization(
                    campaign_data, ml_predictions["viral_creatives"]
                )
                optimizations_applied.append(creative_optimization)
            
            # 4. Ajustes presupuestarios
            if ml_predictions.get("budget_recommendations"):
                budget_optimization = await self._apply_budget_optimization(
                    campaign_data, ml_predictions["budget_recommendations"]
                )
                optimizations_applied.append(budget_optimization)
            
            logger.info(f"✅ {len(optimizations_applied)} optimizaciones aplicadas")
            
        except Exception as e:
            logger.error(f"❌ Error aplicando optimizaciones: {str(e)}")
            optimizations_applied.append({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        return optimizations_applied
    
    async def _apply_geographic_optimization(
        self, 
        campaign_data: Dict[str, Any],
        latam_distribution: Dict[str, float]
    ) -> Dict[str, Any]:
        """Aplicar optimización de distribución geográfica"""
        
        logger.info("🌍 Aplicando optimización geográfica España-LATAM...")
        
        # España siempre mantiene mínimo 35%
        spain_percentage = max(35.0, campaign_data.get("spain_budget_percentage", 35.0))
        latam_available = 100.0 - spain_percentage
        
        # Redistribuir LATAM según performance ML
        optimized_distribution = {}
        total_latam = sum(latam_distribution.values())
        
        for country, percentage in latam_distribution.items():
            # Normalizar para que sume el % disponible para LATAM
            normalized_percentage = (percentage / total_latam) * latam_available
            optimized_distribution[country] = normalized_percentage
        
        # Identificar cambios significativos
        changes = []
        current_dist = campaign_data.get("current_geo_distribution", {})
        
        for country, new_pct in optimized_distribution.items():
            current_pct = current_dist.get(country, 0)
            change = new_pct - current_pct
            
            if abs(change) > 5.0:  # Cambios mayores al 5%
                changes.append({
                    "country": country,
                    "from": current_pct,
                    "to": new_pct,
                    "change": change,
                    "reason": "ML performance optimization"
                })
        
        return {
            "type": "geographic_optimization",
            "spain_percentage": spain_percentage,
            "latam_distribution": optimized_distribution,
            "changes_applied": changes,
            "impact": f"Redistributed LATAM budget across {len(optimized_distribution)} countries",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _apply_audience_optimization(
        self,
        campaign_data: Dict[str, Any],
        target_segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aplicar optimización de segmentos de audiencia"""
        
        logger.info("👥 Aplicando optimización de audiencias...")
        
        # Encontrar segmentos de alto ROI (>3.0)
        high_roi_segments = [s for s in target_segments if s.get("expected_roi", 0) > 3.0]
        
        # Crear nuevos ad sets para segmentos optimizados
        new_adsets = []
        for segment in high_roi_segments:
            adset = {
                "name": f"ML_Optimized_{segment['name']}",
                "targeting": {
                    "age_min": int(segment["age_range"].split("-")[0]),
                    "age_max": int(segment["age_range"].split("-")[1]),
                    "geo_locations": {"countries": segment.get("countries", ["ES"])},
                    "interests": segment.get("interests", []),
                    "behaviors": segment.get("behaviors", [])
                },
                "budget": campaign_data.get("daily_budget", 400) * segment.get("budget_percentage", 50) / 100,
                "expected_roi": segment["expected_roi"]
            }
            new_adsets.append(adset)
        
        return {
            "type": "audience_optimization",
            "segments_optimized": len(target_segments),
            "high_roi_segments": len(high_roi_segments),
            "new_adsets": new_adsets,
            "impact": f"Created {len(new_adsets)} ML-optimized ad sets",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _apply_creative_optimization(
        self,
        campaign_data: Dict[str, Any],
        viral_creatives: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aplicar optimización de creatividades virales"""
        
        logger.info("🚀 Aplicando boost a creatividades virales...")
        
        boosted_creatives = []
        total_boost_budget = 0
        
        for creative in viral_creatives:
            if creative.get("viral_score", 0) > 85:  # Solo creatividades muy virales
                boost_amount = creative.get("recommended_boost", 0)
                
                boosted_creatives.append({
                    "creative_id": creative["creative_id"],
                    "original_budget": campaign_data.get("creative_budget", 50),
                    "boost_amount": boost_amount,
                    "new_budget": campaign_data.get("creative_budget", 50) + boost_amount,
                    "viral_score": creative["viral_score"],
                    "reason": creative.get("reason", "High viral potential")
                })
                
                total_boost_budget += boost_amount
        
        return {
            "type": "creative_optimization",
            "creatives_boosted": len(boosted_creatives),
            "total_boost_budget": total_boost_budget,
            "boosted_creatives": boosted_creatives,
            "impact": f"Boosted {len(boosted_creatives)} viral creatives with €{total_boost_budget}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _apply_budget_optimization(
        self,
        campaign_data: Dict[str, Any], 
        budget_recommendations: Dict[str, float]
    ) -> Dict[str, Any]:
        """Aplicar optimizaciones presupuestarias"""
        
        logger.info("💰 Aplicando optimización presupuestaria...")
        
        current_budget = campaign_data.get("daily_budget", 400)
        budget_adjustments = []
        total_adjustment = 0
        
        for recommendation, amount in budget_recommendations.items():
            if "increase" in recommendation and amount > 0:
                budget_adjustments.append({
                    "type": "increase",
                    "target": recommendation.replace("increase_", ""),
                    "amount": amount,
                    "reason": "ML detected high performance"
                })
                total_adjustment += amount
                
            elif "reduce" in recommendation and amount < 0:
                budget_adjustments.append({
                    "type": "decrease",
                    "target": recommendation.replace("reduce_", ""),
                    "amount": abs(amount),
                    "reason": "ML detected low performance"
                })
                total_adjustment += amount  # Amount is already negative
        
        new_budget = max(100, current_budget + total_adjustment)  # Mínimo €100/día
        
        return {
            "type": "budget_optimization", 
            "current_budget": current_budget,
            "new_budget": new_budget,
            "total_adjustment": total_adjustment,
            "adjustments": budget_adjustments,
            "impact": f"Budget adjusted from €{current_budget} to €{new_budget}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _update_continuous_learning(self, campaign_data: Dict[str, Any]):
        """Actualizar aprendizaje continuo"""
        
        logger.info("📚 Actualizando aprendizaje continuo...")
        
        try:
            # Preparar datos de performance actuales
            performance_data = [{
                "campaign_id": campaign_data.get("campaign_id", "unknown"),
                "creative_id": "current_creative",
                "utm_source": "meta_ads",
                "ctr": campaign_data.get("current_ctr", 0.05),
                "retention_rate": campaign_data.get("retention_rate", 0.7),
                "conversions": campaign_data.get("conversions", 10),
                "cost_per_conversion": campaign_data.get("cost_per_conversion", 5.0),
                "engagement_rate": campaign_data.get("engagement_rate", 0.08),
                "country": "ES",
                "region": "ES",
                "age_range": "18-34",
                "gender": "mixed",
                "device_type": "mobile",
                "landing_page_time": 45,
                "landing_page_conversions": 3,
                "timestamp": datetime.now().isoformat()
            }]
            
            # Actualizar aprendizaje via API
            response = requests.post(
                f"{self.ml_api_url}/ml/update-learning",
                json=performance_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Aprendizaje continuo actualizado")
            else:
                logger.warning(f"⚠️ Error actualizando aprendizaje: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error en aprendizaje continuo: {str(e)}")
    
    async def _generate_next_actions(self, ml_predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar próximas acciones recomendadas"""
        
        next_actions = []
        
        # Basado en ROI esperado
        expected_roi = ml_predictions.get("expected_roi", 2.0)
        if expected_roi > 3.5:
            next_actions.append({
                "action": "scale_up_campaign",
                "priority": "high",
                "description": f"Scale up campaign - Expected ROI: {expected_roi:.2f}x",
                "estimated_impact": "+50% conversions"
            })
        
        # Basado en distribución geográfica
        latam_dist = ml_predictions.get("latam_distribution", {})
        high_performers = [country for country, pct in latam_dist.items() if pct > 25]
        
        if high_performers:
            next_actions.append({
                "action": "expand_high_performers",
                "priority": "medium",
                "description": f"Expand budget in {', '.join(high_performers)}",
                "estimated_impact": "+30% ROI"
            })
        
        # Basado en creatividades virales
        viral_creatives = ml_predictions.get("viral_creatives", [])
        if viral_creatives:
            next_actions.append({
                "action": "create_viral_variants", 
                "priority": "medium",
                "description": f"Create variants of {len(viral_creatives)} viral creatives",
                "estimated_impact": "+25% reach"
            })
        
        # Exploración de nuevos países (20% regla)
        next_actions.append({
            "action": "explore_new_markets",
            "priority": "low",
            "description": "Test Peru and Ecuador with 20% exploration budget",
            "estimated_impact": "+10% market reach"
        })
        
        return next_actions
    
    def _calculate_performance_boost(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular impacto estimado de las optimizaciones"""
        
        total_budget_change = 0
        roi_improvement = 0
        new_markets = 0
        
        for opt in optimizations:
            if opt["type"] == "budget_optimization":
                total_budget_change += opt.get("total_adjustment", 0)
                
            elif opt["type"] == "geographic_optimization":
                new_markets += len(opt.get("latam_distribution", {}))
                roi_improvement += 0.2  # 20% mejora estimada por geo optimization
                
            elif opt["type"] == "creative_optimization":
                roi_improvement += 0.3 * opt.get("creatives_boosted", 0)  # 30% por creative viral
                
            elif opt["type"] == "audience_optimization":
                roi_improvement += 0.15 * opt.get("high_roi_segments", 0)  # 15% por segmento optimizado
        
        return {
            "estimated_roi_improvement": min(roi_improvement, 1.0),  # Max 100% improvement
            "budget_impact": total_budget_change,
            "new_markets_coverage": new_markets,
            "optimization_score": len(optimizations),
            "performance_boost_percentage": min(roi_improvement * 100, 100)
        }
    
    async def _get_fallback_actions(self, campaign_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Acciones de respaldo cuando ML falla"""
        
        return [
            {
                "action": "maintain_spain_35",
                "description": "Maintain Spain at 35% minimum budget",
                "priority": "high"
            },
            {
                "action": "test_mexico_colombia", 
                "description": "Test increased budget in Mexico and Colombia",
                "priority": "medium"
            },
            {
                "action": "monitor_performance",
                "description": "Continue monitoring for ML data collection",
                "priority": "low"
            }
        ]

# Instancia global del integrador
meta_ml_integrator = MetaMLIntegrator()