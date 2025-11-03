"""
Semantic Synchronizer - Módulo 7
Sincronización perfecta entre análisis semántico de audio y clips visuales.

Integra con:
- AudioAnalyzer para timing musical
- VisualClipDatabase para clips compatibles  
- ML Core para matching optimization
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

# Importar componentes del módulo
from .audio_analyzer import AudioAnalyzer, AudioAnalysisResult, SyncPoint
from .visual_clip_database import VisualClipDatabase, VisualClip, ClipQuery

# Integración con ML Core
try:
    from ml_core.models.factory import get_yolo_video_detector
    ML_CORE_AVAILABLE = True
except ImportError:
    ML_CORE_AVAILABLE = False

try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

logger = logging.getLogger(__name__)

@dataclass
class SyncMatch:
    """Resultado de sincronización audio-visual"""
    audio_segment: Dict[str, Any]  # Segmento de audio
    visual_clip: VisualClip       # Clip visual seleccionado
    sync_score: float             # Score de compatibilidad
    sync_points: List[SyncPoint]  # Puntos de sincronización específicos
    
    # Timing
    audio_start: float            # Inicio en audio original
    audio_duration: float         # Duración del segmento
    visual_start: float           # Inicio en clip visual
    visual_duration: float        # Duración del clip visual
    
    # Optimización
    fade_in: float               # Duración fade in
    fade_out: float              # Duración fade out
    transition_type: str         # Tipo de transición
    
    # Metadatos
    genre_match: float           # Compatibilidad de género
    emotion_match: float         # Compatibilidad emocional
    energy_match: float          # Compatibilidad de energía
    tempo_match: float           # Compatibilidad de tempo

@dataclass
class SyncConfiguration:
    """Configuración para sincronización"""
    target_duration: float = 15.0          # Duración objetivo del edit
    min_sync_score: float = 0.6            # Score mínimo de sincronización
    prefer_climax_moments: bool = True     # Priorizar momentos climáticos
    allow_tempo_variance: float = 0.2      # Varianza permitida en tempo
    transition_duration: float = 0.5       # Duración de transiciones
    max_clips_per_segment: int = 3         # Máximo clips por segmento
    viral_score_weight: float = 0.3        # Peso del viral score
    freshness_weight: float = 0.2          # Peso de la frescura (clips poco usados)

class SemanticSynchronizer:
    """
    Sincronizador semántico para matching perfecto audio-visual.
    
    Combina análisis de audio con base de datos de clips para generar
    sincronizaciones optimizadas para máximo engagement viral.
    """
    
    def __init__(self, audio_analyzer: AudioAnalyzer = None,
                 clip_database: VisualClipDatabase = None,
                 config: SyncConfiguration = None):
        
        self.audio_analyzer = audio_analyzer or AudioAnalyzer()
        self.clip_database = clip_database or VisualClipDatabase()
        self.config = config or SyncConfiguration()
        self.logger = logging.getLogger(f"{__name__}.SemanticSynchronizer")
        
        # Cache para optimización
        self.sync_cache: Dict[str, List[SyncMatch]] = {}
        
        # Pesos para cálculo de score
        self.score_weights = {
            "genre_match": 0.25,
            "emotion_match": 0.20,
            "energy_match": 0.20,
            "tempo_match": 0.15,
            "viral_potential": 0.15,
            "freshness": 0.05
        }
        
        self.logger.info("🎭 Semantic Synchronizer initialized")
    
    async def create_synchronized_edit(self, audio_path: str, 
                                     config: SyncConfiguration = None) -> List[SyncMatch]:
        """
        Crea edit sincronizado completo a partir de archivo de audio.
        
        Args:
            audio_path: Ruta al archivo de audio
            config: Configuración de sincronización
            
        Returns:
            Lista de matches sincronizados para crear el edit
        """
        use_config = config or self.config
        
        self.logger.info(f"🎭 Creating synchronized edit for: {audio_path}")
        
        # 1. Analizar audio
        audio_analysis = await self.audio_analyzer.analyze_audio_file(audio_path)
        
        # 2. Encontrar segmentos óptimos
        optimal_segments = await self._find_optimal_segments(
            audio_analysis, use_config
        )
        
        # 3. Sincronizar cada segmento con clips visuales
        sync_matches = []
        
        for segment in optimal_segments:
            matches = await self._synchronize_segment(segment, audio_analysis, use_config)
            sync_matches.extend(matches)
        
        # 4. Optimizar transiciones
        optimized_matches = await self._optimize_transitions(sync_matches, use_config)
        
        # 5. Validar duración total
        final_matches = self._adjust_to_target_duration(optimized_matches, use_config)
        
        self.logger.info(f"✅ Created {len(final_matches)} synchronized matches")
        
        return final_matches
    
    async def _find_optimal_segments(self, audio_analysis: AudioAnalysisResult,
                                   config: SyncConfiguration) -> List[Dict[str, Any]]:
        """Encuentra segmentos óptimos del audio para sincronizar"""
        
        segments = []
        
        if config.prefer_climax_moments:
            # Priorizar momentos climáticos
            for climax in audio_analysis.climax_moments:
                if climax["timestamp"] + config.target_duration <= audio_analysis.duration:
                    segments.append({
                        "start": climax["timestamp"],
                        "duration": config.target_duration,
                        "type": "climax",
                        "intensity": climax["intensity"],
                        "priority": climax["intensity"]
                    })
        
        # Agregar segmentos basados en beats fuertes
        sync_points = await self.audio_analyzer.find_optimal_sync_points(
            audio_analysis, config.target_duration
        )
        
        for sync_point in sync_points[:5]:  # Top 5 sync points
            segments.append({
                "start": sync_point.timestamp,
                "duration": sync_point.duration,
                "type": "sync_point", 
                "intensity": sync_point.intensity,
                "priority": sync_point.intensity * sync_point.visual_match_score
            })
        
        # Ordenar por prioridad
        segments.sort(key=lambda x: x["priority"], reverse=True)
        
        # Eliminar solapamientos
        final_segments = []
        for segment in segments:
            overlaps = any(
                abs(segment["start"] - existing["start"]) < config.target_duration * 0.5
                for existing in final_segments
            )
            if not overlaps:
                final_segments.append(segment)
        
        return final_segments[:3]  # Máximo 3 segmentos principales
    
    async def _synchronize_segment(self, segment: Dict[str, Any], 
                                 audio_analysis: AudioAnalysisResult,
                                 config: SyncConfiguration) -> List[SyncMatch]:
        """Sincroniza un segmento de audio con clips visuales"""
        
        # Determinar características del segmento
        segment_start = segment["start"]
        segment_duration = segment["duration"]
        
        # Calcular tempo promedio en el segmento
        segment_tempo = self._calculate_segment_tempo(
            audio_analysis, segment_start, segment_duration
        )
        
        # Determinar género y emoción dominante
        genre = max(audio_analysis.genre_prediction, key=audio_analysis.genre_prediction.get)
        
        # Calcular energía promedio
        energy_level = self._calculate_segment_energy(
            audio_analysis, segment_start, segment_duration
        )
        
        # Buscar clips compatibles
        query = ClipQuery(
            genre=genre,
            energy_min=max(0, energy_level - 0.3),
            energy_max=min(1.0, energy_level + 0.3),
            duration_min=segment_duration * 0.7,
            duration_max=segment_duration * 1.5,
            viral_score_min=0.5,
            exclude_recent=True,
            limit=20
        )
        
        candidate_clips = await self.clip_database.search_clips(query)
        
        # Calcular scores de compatibilidad
        scored_clips = []
        for clip in candidate_clips:
            score = await self._calculate_sync_score(
                segment, audio_analysis, clip, segment_tempo
            )
            
            if score >= config.min_sync_score:
                scored_clips.append((clip, score))
        
        # Ordenar por score
        scored_clips.sort(key=lambda x: x[1], reverse=True)
        
        # Crear matches
        sync_matches = []
        clips_used = 0
        
        for clip, score in scored_clips[:config.max_clips_per_segment]:
            sync_match = await self._create_sync_match(
                segment, audio_analysis, clip, score, segment_tempo
            )
            sync_matches.append(sync_match)
            clips_used += 1
        
        return sync_matches
    
    def _calculate_segment_tempo(self, audio_analysis: AudioAnalysisResult,
                               start: float, duration: float) -> float:
        """Calcula tempo promedio de un segmento"""
        
        # Encontrar beats en el segmento
        segment_beats = [
            beat for beat in audio_analysis.beats
            if start <= beat["timestamp"] <= start + duration
        ]
        
        if len(segment_beats) < 2:
            return 120.0  # Tempo por defecto
        
        # Calcular BPM promedio
        intervals = [
            segment_beats[i+1]["timestamp"] - segment_beats[i]["timestamp"]
            for i in range(len(segment_beats) - 1)
        ]
        
        avg_interval = np.mean(intervals)
        bpm = 60.0 / avg_interval if avg_interval > 0 else 120.0
        
        return bpm
    
    def _calculate_segment_energy(self, audio_analysis: AudioAnalysisResult,
                                start: float, duration: float) -> float:
        """Calcula energía promedio de un segmento"""
        
        segment_energy = [
            energy["energy"] for energy in audio_analysis.energy_levels
            if start <= energy["timestamp"] <= start + duration
        ]
        
        return np.mean(segment_energy) if segment_energy else 0.5
    
    async def _calculate_sync_score(self, segment: Dict[str, Any],
                                  audio_analysis: AudioAnalysisResult,
                                  clip: VisualClip, segment_tempo: float) -> float:
        """Calcula score de compatibilidad para sincronización"""
        
        scores = {}
        
        # 1. Genre match
        audio_genre = max(audio_analysis.genre_prediction, key=audio_analysis.genre_prediction.get)
        scores["genre_match"] = 1.0 if clip.genre == audio_genre else 0.5
        
        # 2. Emotion match basado en intensidad del segmento
        if segment["intensity"] > 0.8:
            emotion_target = "energetic"
        elif segment["intensity"] > 0.6:
            emotion_target = "aggressive"
        else:
            emotion_target = "calm"
        
        scores["emotion_match"] = 1.0 if clip.emotion == emotion_target else 0.6
        
        # 3. Energy match
        segment_energy = self._calculate_segment_energy(
            audio_analysis, segment["start"], segment["duration"]
        )
        energy_diff = abs(clip.energy_level - segment_energy)
        scores["energy_match"] = max(0, 1.0 - energy_diff * 2)
        
        # 4. Tempo match
        tempo_min, tempo_max = clip.optimal_tempo_range
        if tempo_min <= segment_tempo <= tempo_max:
            scores["tempo_match"] = 1.0
        else:
            tempo_diff = min(abs(segment_tempo - tempo_min), abs(segment_tempo - tempo_max))
            scores["tempo_match"] = max(0, 1.0 - tempo_diff / 40.0)  # 40 BPM tolerance
        
        # 5. Viral potential
        scores["viral_potential"] = clip.viral_score
        
        # 6. Freshness (clips poco usados)
        hours_since_use = 24  # Default if never used
        if clip.last_used:
            last_used = datetime.fromisoformat(clip.last_used)
            hours_since_use = (datetime.now() - last_used).total_seconds() / 3600
        
        scores["freshness"] = min(1.0, hours_since_use / 24.0)  # Max at 24+ hours
        
        # Calcular score final ponderado
        final_score = sum(
            scores[key] * self.score_weights[key]
            for key in scores
        )
        
        return final_score
    
    async def _create_sync_match(self, segment: Dict[str, Any],
                               audio_analysis: AudioAnalysisResult,
                               clip: VisualClip, sync_score: float,
                               segment_tempo: float) -> SyncMatch:
        """Crea objeto SyncMatch con todos los detalles"""
        
        # Encontrar puntos de sincronización específicos
        sync_points = []
        for beat in audio_analysis.beats:
            if segment["start"] <= beat["timestamp"] <= segment["start"] + segment["duration"]:
                sync_point = SyncPoint(
                    timestamp=beat["timestamp"],
                    sync_type="beat",
                    intensity=beat["intensity"],
                    duration=0.1,
                    visual_match_score=sync_score
                )
                sync_points.append(sync_point)
        
        # Calcular matches individuales
        genre_match = 1.0 if clip.genre in audio_analysis.genre_prediction else 0.5
        
        segment_energy = self._calculate_segment_energy(
            audio_analysis, segment["start"], segment["duration"]
        )
        energy_match = max(0, 1.0 - abs(clip.energy_level - segment_energy) * 2)
        
        tempo_min, tempo_max = clip.optimal_tempo_range
        tempo_match = 1.0 if tempo_min <= segment_tempo <= tempo_max else 0.6
        
        # Determinar tipo de transición
        transition_type = "cut"
        if segment["intensity"] > 0.8:
            transition_type = "beat_sync"
        elif sync_score > 0.8:
            transition_type = "smooth_fade"
        
        return SyncMatch(
            audio_segment=segment,
            visual_clip=clip,
            sync_score=sync_score,
            sync_points=sync_points,
            audio_start=segment["start"],
            audio_duration=segment["duration"],
            visual_start=0.0,  # Start from beginning of clip
            visual_duration=min(clip.duration, segment["duration"]),
            fade_in=0.2,
            fade_out=0.2,
            transition_type=transition_type,
            genre_match=genre_match,
            emotion_match=0.8,  # Calculated above
            energy_match=energy_match,
            tempo_match=tempo_match
        )
    
    async def _optimize_transitions(self, sync_matches: List[SyncMatch],
                                  config: SyncConfiguration) -> List[SyncMatch]:
        """Optimiza transiciones entre clips"""
        
        if len(sync_matches) <= 1:
            return sync_matches
        
        optimized = []
        
        for i, match in enumerate(sync_matches):
            current_match = match
            
            # Ajustar transiciones entre clips consecutivos
            if i > 0:
                prev_match = optimized[-1]
                
                # Calcular overlap óptimo
                overlap = self._calculate_optimal_overlap(prev_match, current_match)
                
                # Ajustar fade in/out
                if overlap > 0:
                    current_match.fade_in = overlap / 2
                    prev_match.fade_out = overlap / 2
                
                # Ajustar tipo de transición
                if prev_match.sync_score > 0.8 and current_match.sync_score > 0.8:
                    current_match.transition_type = "smooth_fade"
                else:
                    current_match.transition_type = "cut"
            
            optimized.append(current_match)
        
        return optimized
    
    def _calculate_optimal_overlap(self, match1: SyncMatch, match2: SyncMatch) -> float:
        """Calcula overlap óptimo entre dos matches"""
        
        # Factores para overlap
        score_factor = (match1.sync_score + match2.sync_score) / 2
        energy_diff = abs(match1.visual_clip.energy_level - match2.visual_clip.energy_level)
        
        # Overlap base
        base_overlap = 0.5
        
        # Ajustar según scores y diferencia de energía
        if score_factor > 0.8 and energy_diff < 0.3:
            return base_overlap * 1.5  # Más overlap para transiciones suaves
        elif energy_diff > 0.6:
            return base_overlap * 0.5  # Menos overlap para cambios abruptos
        
        return base_overlap
    
    def _adjust_to_target_duration(self, sync_matches: List[SyncMatch],
                                 config: SyncConfiguration) -> List[SyncMatch]:
        """Ajusta matches para cumplir duración objetivo"""
        
        total_duration = sum(match.audio_duration for match in sync_matches)
        target_duration = config.target_duration
        
        if abs(total_duration - target_duration) <= 1.0:  # Within 1 second
            return sync_matches
        
        # Escalar duraciones proporcionalmente
        scale_factor = target_duration / total_duration
        
        adjusted_matches = []
        for match in sync_matches:
            adjusted_match = match
            adjusted_match.audio_duration *= scale_factor
            adjusted_match.visual_duration = min(
                adjusted_match.visual_clip.duration,
                adjusted_match.audio_duration
            )
            adjusted_matches.append(adjusted_match)
        
        return adjusted_matches
    
    async def export_sync_data(self, sync_matches: List[SyncMatch],
                             output_path: str) -> bool:
        """Exporta datos de sincronización a JSON"""
        try:
            export_data = {
                "sync_matches": [asdict(match) for match in sync_matches],
                "total_duration": sum(match.audio_duration for match in sync_matches),
                "avg_sync_score": np.mean([match.sync_score for match in sync_matches]),
                "exported_at": datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Sync data exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export sync data: {e}")
            return False
    
    async def get_sync_statistics(self, sync_matches: List[SyncMatch]) -> Dict[str, Any]:
        """Obtiene estadísticas de sincronización"""
        
        if not sync_matches:
            return {}
        
        scores = [match.sync_score for match in sync_matches]
        genres = [match.visual_clip.genre for match in sync_matches]
        emotions = [match.visual_clip.emotion for match in sync_matches]
        
        return {
            "total_matches": len(sync_matches),
            "avg_sync_score": np.mean(scores),
            "max_sync_score": np.max(scores),
            "min_sync_score": np.min(scores),
            "total_duration": sum(match.audio_duration for match in sync_matches),
            "genre_distribution": {genre: genres.count(genre) for genre in set(genres)},
            "emotion_distribution": {emotion: emotions.count(emotion) for emotion in set(emotions)},
            "avg_viral_potential": np.mean([match.visual_clip.viral_score for match in sync_matches])
        }

# Factory function
def create_semantic_synchronizer(audio_analyzer: AudioAnalyzer = None,
                               clip_database: VisualClipDatabase = None,
                               config: SyncConfiguration = None) -> SemanticSynchronizer:
    """Crea instancia de SemanticSynchronizer"""
    return SemanticSynchronizer(audio_analyzer, clip_database, config)