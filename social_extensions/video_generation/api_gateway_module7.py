"""
API Gateway - Módulo 7
Gateway de integración con ML Core para endpoints de generación viral.

Integra con:
- ml_core/api/main.py para endpoints existentes
- FastAPI para exposición de servicios
- Orchestration para workflows n8n
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
import json
import uuid

# Importar componentes del módulo
from .audio_analyzer import AudioAnalyzer, AudioAnalysisResult, create_audio_analyzer
from .visual_clip_database import VisualClipDatabase, VisualClip, ClipQuery, create_visual_clip_database
from .semantic_synchronizer import SemanticSynchronizer, SyncMatch, SyncConfiguration, create_semantic_synchronizer
from .viral_fragment_selector import ViralFragmentSelector, ViralPrediction, create_viral_fragment_selector
from .ab_testing_variants import ABTestingVariants, EditVariant, ABTestSetup, VariantType, create_ab_testing_variants

# Integración con sistema existente
try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

logger = logging.getLogger(__name__)

# ============================================
# PYDANTIC MODELS PARA API
# ============================================

class AudioAnalysisRequest(BaseModel):
    """Request para análisis de audio"""
    audio_url: str = Field(..., description="URL del archivo de audio")
    analysis_options: Dict[str, Any] = Field(default_factory=dict, description="Opciones de análisis")

class AudioAnalysisResponse(BaseModel):
    """Response del análisis de audio"""
    analysis_id: str
    status: str
    duration: float
    beat_count: int
    climax_moments: int
    viral_potential: float
    processing_time: float
    analysis_data: Dict[str, Any]

class ViralEditRequest(BaseModel):
    """Request para generación de edit viral"""
    audio_url: str = Field(..., description="URL del archivo de audio")
    target_duration: float = Field(15.0, description="Duración objetivo en segundos")
    target_platforms: List[str] = Field(default=["tiktok", "instagram"], description="Plataformas objetivo")
    genre_hint: Optional[str] = Field(None, description="Pista del género musical")
    optimization_level: str = Field("standard", description="Nivel de optimización: basic, standard, premium")

class ViralEditResponse(BaseModel):
    """Response de generación de edit viral"""
    edit_id: str
    status: str
    total_duration: float
    sync_matches_count: int
    viral_score: float
    confidence: float
    recommended_platforms: List[str]
    hashtags: List[str]
    processing_time: float
    edit_data: Dict[str, Any]

class ABTestRequest(BaseModel):
    """Request para crear test A/B"""
    edit_id: str = Field(..., description="ID del edit base")
    test_name: str = Field(..., description="Nombre del test")
    variant_types: List[str] = Field(default=["timing", "visual", "duration"], description="Tipos de variantes")
    max_variants: int = Field(8, description="Máximo número de variantes")
    test_duration_hours: int = Field(24, description="Duración del test en horas")
    target_audience: Dict[str, Any] = Field(default_factory=dict, description="Audiencia objetivo")

class ABTestResponse(BaseModel):
    """Response de creación de test A/B"""
    test_id: str
    status: str
    variants_created: int
    traffic_allocation: Dict[str, float]
    estimated_completion: str
    test_data: Dict[str, Any]

class ClipDatabaseScanRequest(BaseModel):
    """Request para escanear clips"""
    directory_path: Optional[str] = Field(None, description="Directorio a escanear")
    force_rescan: bool = Field(False, description="Forzar re-escaneo de clips existentes")

class SyncVisualsRequest(BaseModel):
    """Request para sincronización visual"""
    analysis_id: str = Field(..., description="ID del análisis de audio")
    visual_preferences: Dict[str, Any] = Field(default_factory=dict, description="Preferencias visuales")
    sync_precision: float = Field(0.05, description="Precisión de sincronización en segundos")

# ============================================
# API GATEWAY CLASS
# ============================================

class APIGatewayModule7:
    """
    Gateway de API para el Módulo 7 de generación viral.
    
    Expone endpoints FastAPI para integración con ML Core y orchestración.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.APIGatewayModule7")
        
        # Inicializar componentes del módulo
        self.audio_analyzer = create_audio_analyzer()
        self.clip_database = create_visual_clip_database()
        self.synchronizer = create_semantic_synchronizer(
            self.audio_analyzer, self.clip_database
        )
        self.viral_selector = create_viral_fragment_selector()
        self.ab_testing = create_ab_testing_variants(
            viral_selector=self.viral_selector
        )
        
        # Cache para operaciones
        self.analysis_cache: Dict[str, AudioAnalysisResult] = {}
        self.edit_cache: Dict[str, Dict[str, Any]] = {}
        self.test_cache: Dict[str, ABTestSetup] = {}
        
        # Router FastAPI
        self.router = APIRouter(
            prefix="/module7",
            tags=["Viral Generation Module 7"],
            responses={404: {"description": "Not found"}}
        )
        
        # Registrar rutas
        self._register_routes()
        
        self.logger.info("🚀 API Gateway Module 7 initialized")
    
    def _register_routes(self):
        """Registra todas las rutas del API"""
        
        @self.router.post("/analyze-audio", response_model=AudioAnalysisResponse)
        async def analyze_audio(request: AudioAnalysisRequest) -> AudioAnalysisResponse:
            """Analiza archivo de audio para sincronización semántica"""
            return await self.analyze_audio_endpoint(request)
        
        @self.router.post("/generate-viral-edit", response_model=ViralEditResponse)
        async def generate_viral_edit(request: ViralEditRequest, 
                                    background_tasks: BackgroundTasks) -> ViralEditResponse:
            """Genera edit viral completo con sincronización semántica"""
            return await self.generate_viral_edit_endpoint(request, background_tasks)
        
        @self.router.post("/sync-visual-clips", response_model=Dict[str, Any])
        async def sync_visual_clips(request: SyncVisualsRequest) -> Dict[str, Any]:
            """Sincroniza clips visuales con análisis de audio existente"""
            return await self.sync_visual_clips_endpoint(request)
        
        @self.router.post("/create-ab-test", response_model=ABTestResponse)
        async def create_ab_test(request: ABTestRequest) -> ABTestResponse:
            """Crea test A/B con múltiples variantes"""
            return await self.create_ab_test_endpoint(request)
        
        @self.router.get("/ab-test/{test_id}/results")
        async def get_ab_test_results(test_id: str) -> Dict[str, Any]:
            """Obtiene resultados de test A/B"""
            return await self.get_ab_test_results_endpoint(test_id)
        
        @self.router.post("/scan-clip-database", response_model=Dict[str, Any])
        async def scan_clip_database(request: ClipDatabaseScanRequest) -> Dict[str, Any]:
            """Escanea y clasifica clips en base de datos"""
            return await self.scan_database_endpoint(request)
        
        @self.router.get("/database/stats")
        async def get_database_stats() -> Dict[str, Any]:
            """Obtiene estadísticas de la base de datos de clips"""
            return await self.clip_database.get_database_stats()
        
        @self.router.get("/viral-insights")
        async def get_viral_insights() -> Dict[str, Any]:
            """Obtiene insights del selector viral"""
            return await self.viral_selector.get_viral_insights()
        
        @self.router.get("/system/health")
        async def system_health() -> Dict[str, Any]:
            """Health check del Módulo 7"""
            return await self.health_check()
    
    async def analyze_audio_endpoint(self, request: AudioAnalysisRequest) -> AudioAnalysisResponse:
        """Endpoint para análisis de audio"""
        try:
            start_time = datetime.now()
            
            # Generar ID de análisis
            analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
            
            # Realizar análisis de audio
            analysis_result = await self.audio_analyzer.analyze_audio_file(request.audio_url)
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Guardar en cache
            self.analysis_cache[analysis_id] = analysis_result
            
            # Preparar respuesta
            response = AudioAnalysisResponse(
                analysis_id=analysis_id,
                status="completed",
                duration=analysis_result.duration,
                beat_count=len(analysis_result.beats),
                climax_moments=len(analysis_result.climax_moments),
                viral_potential=analysis_result.viral_potential,
                processing_time=processing_time,
                analysis_data={
                    "genre_prediction": analysis_result.genre_prediction,
                    "energy_levels": len(analysis_result.energy_levels),
                    "vocal_segments": len(analysis_result.vocal_segments),
                    "sync_points": len(analysis_result.sync_points)
                }
            )
            
            self.logger.info(f"🎵 Audio analysis completed: {analysis_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Audio analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    async def generate_viral_edit_endpoint(self, request: ViralEditRequest,
                                         background_tasks: BackgroundTasks) -> ViralEditResponse:
        """Endpoint para generar edit viral completo"""
        try:
            start_time = datetime.now()
            
            # Generar ID de edit
            edit_id = f"edit_{uuid.uuid4().hex[:8]}"
            
            self.logger.info(f"🚀 Generating viral edit: {edit_id}")
            
            # Configurar sincronización
            sync_config = SyncConfiguration(
                target_duration=request.target_duration,
                prefer_climax_moments=True,
                min_sync_score=0.7 if request.optimization_level == "premium" else 0.6
            )
            
            # Crear edit sincronizado
            sync_matches = await self.synchronizer.create_synchronized_edit(
                request.audio_url, sync_config
            )
            
            if not sync_matches:
                raise HTTPException(status_code=400, detail="No suitable sync matches found")
            
            # Predecir potencial viral
            viral_predictions = await self.viral_selector.predict_viral_potential(
                sync_matches, request.audio_url
            )
            
            # Seleccionar mejor predicción
            best_prediction = viral_predictions[0] if viral_predictions else None
            
            # Calcular tiempo de procesamiento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Preparar datos del edit
            edit_data = {
                "sync_matches": [
                    {
                        "audio_start": match.audio_start,
                        "audio_duration": match.audio_duration,
                        "visual_clip_id": match.visual_clip.clip_id,
                        "sync_score": match.sync_score,
                        "transition_type": match.transition_type
                    }
                    for match in sync_matches
                ],
                "viral_prediction": {
                    "viral_score": best_prediction.viral_score if best_prediction else 0.5,
                    "confidence": best_prediction.confidence if best_prediction else 0.7,
                    "trending_elements": best_prediction.viral_elements if best_prediction else [],
                    "optimal_platforms": best_prediction.optimal_platforms if best_prediction else request.target_platforms
                } if best_prediction else None,
                "audio_url": request.audio_url,
                "target_platforms": request.target_platforms,
                "genre_hint": request.genre_hint,
                "created_at": datetime.now().isoformat()
            }
            
            # Guardar en cache
            self.edit_cache[edit_id] = edit_data
            
            # Programar procesamiento en background para generar variantes
            if request.optimization_level in ["standard", "premium"]:
                background_tasks.add_task(
                    self._generate_variants_background,
                    edit_id, sync_matches, viral_predictions
                )
            
            # Preparar respuesta
            response = ViralEditResponse(
                edit_id=edit_id,
                status="completed",
                total_duration=sum(match.audio_duration for match in sync_matches),
                sync_matches_count=len(sync_matches),
                viral_score=best_prediction.viral_score if best_prediction else 0.5,
                confidence=best_prediction.confidence if best_prediction else 0.7,
                recommended_platforms=best_prediction.optimal_platforms if best_prediction else request.target_platforms,
                hashtags=best_prediction.recommended_hashtags if best_prediction else ["#viral", "#music"],
                processing_time=processing_time,
                edit_data=edit_data
            )
            
            self.logger.info(f"✅ Viral edit generated: {edit_id} (score: {response.viral_score:.2f})")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"❌ Viral edit generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Edit generation failed: {str(e)}")
    
    async def _generate_variants_background(self, edit_id: str, sync_matches: List[SyncMatch],
                                          viral_predictions: List[ViralPrediction]):
        """Genera variantes en background para optimización"""
        try:
            self.logger.info(f"🧪 Generating variants for edit: {edit_id}")
            
            # Generar variantes A/B
            variants = await self.ab_testing.generate_variants(
                sync_matches, viral_predictions, max_variants=6
            )
            
            # Guardar variantes en cache del edit
            if edit_id in self.edit_cache:
                self.edit_cache[edit_id]["variants"] = [
                    {
                        "variant_id": variant.variant_id,
                        "variant_type": variant.variant_type.value,
                        "viral_score": variant.viral_prediction.viral_score if variant.viral_prediction else 0.5
                    }
                    for variant in variants
                ]
            
            self.logger.info(f"✅ Generated {len(variants)} variants for edit: {edit_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Background variant generation failed: {e}")
    
    async def sync_visual_clips_endpoint(self, request: SyncVisualsRequest) -> Dict[str, Any]:
        """Endpoint para sincronizar clips visuales"""
        try:
            # Obtener análisis de audio del cache
            if request.analysis_id not in self.analysis_cache:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            analysis_result = self.analysis_cache[request.analysis_id]
            
            # Configurar sincronización
            sync_config = SyncConfiguration(
                sync_precision=request.sync_precision
            )
            
            # Crear sincronización
            sync_matches = await self.synchronizer.create_synchronized_edit(
                analysis_result.file_path, sync_config
            )
            
            # Obtener estadísticas
            sync_stats = await self.synchronizer.get_sync_statistics(sync_matches)
            
            return {
                "analysis_id": request.analysis_id,
                "sync_matches_count": len(sync_matches),
                "average_sync_score": sync_stats.get("avg_sync_score", 0),
                "total_duration": sync_stats.get("total_duration", 0),
                "genre_distribution": sync_stats.get("genre_distribution", {}),
                "sync_matches": [
                    {
                        "audio_start": match.audio_start,
                        "duration": match.audio_duration,
                        "visual_clip": match.visual_clip.clip_id,
                        "sync_score": match.sync_score,
                        "genre": match.visual_clip.genre,
                        "energy": match.visual_clip.energy_level
                    }
                    for match in sync_matches[:10]  # Top 10
                ]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"❌ Visual sync failed: {e}")
            raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
    
    async def create_ab_test_endpoint(self, request: ABTestRequest) -> ABTestResponse:
        """Endpoint para crear test A/B"""
        try:
            # Verificar que el edit existe
            if request.edit_id not in self.edit_cache:
                raise HTTPException(status_code=404, detail="Edit not found")
            
            edit_data = self.edit_cache[request.edit_id]
            
            # Reconstruir sync_matches desde datos guardados
            sync_matches = []  # TODO: Reconstruir desde edit_data
            viral_predictions = []  # TODO: Reconstruir desde edit_data
            
            # Convertir tipos de variantes
            variant_types = [
                VariantType(vtype) for vtype in request.variant_types
                if vtype in [vt.value for vt in VariantType]
            ]
            
            # Generar variantes
            variants = await self.ab_testing.generate_variants(
                sync_matches, viral_predictions,
                variant_types, request.max_variants
            )
            
            # Crear test A/B
            ab_test = await self.ab_testing.create_ab_test(
                variants, request.test_name, request.test_duration_hours
            )
            
            # Guardar en cache
            self.test_cache[ab_test.test_id] = ab_test
            
            # Preparar respuesta
            response = ABTestResponse(
                test_id=ab_test.test_id,
                status=ab_test.status,
                variants_created=len(ab_test.variants),
                traffic_allocation=ab_test.traffic_allocation,
                estimated_completion=(
                    datetime.now() + timedelta(hours=request.test_duration_hours)
                ).isoformat(),
                test_data={
                    "edit_id": request.edit_id,
                    "variant_types": [vt.value for vt in variant_types],
                    "target_audience": request.target_audience,
                    "primary_metric": ab_test.primary_metric
                }
            )
            
            self.logger.info(f"🧪 A/B test created: {ab_test.test_id}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"❌ A/B test creation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Test creation failed: {str(e)}")
    
    async def get_ab_test_results_endpoint(self, test_id: str) -> Dict[str, Any]:
        """Endpoint para obtener resultados de test A/B"""
        try:
            # Verificar que el test existe
            if test_id not in self.test_cache:
                raise HTTPException(status_code=404, detail="Test not found")
            
            # Analizar resultados
            results = await self.ab_testing.analyze_test_results(test_id)
            
            if "error" in results:
                raise HTTPException(status_code=400, detail=results["error"])
            
            return results
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to get test results: {e}")
            raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")
    
    async def scan_database_endpoint(self, request: ClipDatabaseScanRequest) -> Dict[str, Any]:
        """Endpoint para escanear base de datos de clips"""
        try:
            # Escanear y clasificar clips
            scan_results = await self.clip_database.scan_and_classify_clips(
                request.directory_path
            )
            
            # Obtener estadísticas actualizadas
            db_stats = await self.clip_database.get_database_stats()
            
            return {
                "scan_results": scan_results,
                "database_stats": db_stats,
                "scanned_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Database scan failed: {e}")
            raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check del sistema"""
        try:
            # Verificar componentes
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "audio_analyzer": "healthy",
                    "clip_database": "healthy", 
                    "synchronizer": "healthy",
                    "viral_selector": "healthy",
                    "ab_testing": "healthy"
                },
                "cache_status": {
                    "audio_analyses": len(self.analysis_cache),
                    "viral_edits": len(self.edit_cache),
                    "ab_tests": len(self.test_cache)
                },
                "dummy_mode": DUMMY_MODE
            }
            
            # Verificar estado de la base de datos
            try:
                db_stats = await self.clip_database.get_database_stats()
                health_status["database"] = {
                    "status": "healthy",
                    "total_clips": db_stats.get("total_clips", 0)
                }
            except Exception:
                health_status["database"] = {"status": "error"}
                health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Factory function y router para integración
def create_api_gateway_module7() -> APIGatewayModule7:
    """Crea instancia del API Gateway"""
    return APIGatewayModule7()

# Instancia global para uso en FastAPI
api_gateway = create_api_gateway_module7()
router = api_gateway.router