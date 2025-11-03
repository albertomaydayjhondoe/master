"""
Visual Clip Database - Módulo 7
Base de datos inteligente de clips visuales clasificados para sincronización semántica.

Integra con:
- data/video_clips/ existente
- ML Core para clasificación
- Database para storage
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import sqlite3
import hashlib

# Integración con sistema existente
try:
    from config.app_settings import is_dummy_mode
    DUMMY_MODE = is_dummy_mode()
except ImportError:
    DUMMY_MODE = True

try:
    from ml_core.models.factory import get_yolo_video_detector
    ML_CORE_AVAILABLE = True
except ImportError:
    ML_CORE_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class VisualClip:
    """Representación de un clip visual clasificado"""
    clip_id: str
    file_path: str
    duration: float
    resolution: Tuple[int, int]
    fps: int
    
    # Clasificaciones
    genre: str
    emotion: str
    energy_level: float
    visual_style: str
    color_dominant: str
    
    # Análisis de contenido
    objects_detected: List[Dict[str, Any]]
    scene_type: str
    movement_intensity: float
    
    # Metadatos de sync
    sync_compatibility: Dict[str, float]  # Compatibilidad con tipos de audio
    optimal_tempo_range: Tuple[float, float]
    cut_points: List[float]  # Puntos óptimos de corte
    
    # Performance histórica
    viral_score: float
    usage_count: int
    avg_engagement: float
    
    # Metadatos
    created_at: str
    last_used: Optional[str]
    tags: List[str]

@dataclass
class ClipQuery:
    """Query para búsqueda de clips"""
    genre: Optional[str] = None
    emotion: Optional[str] = None
    energy_min: Optional[float] = None
    energy_max: Optional[float] = None
    duration_min: Optional[float] = None
    duration_max: Optional[float] = None
    scene_type: Optional[str] = None
    viral_score_min: Optional[float] = None
    exclude_recent: bool = False
    limit: int = 20

class VisualClipDatabase:
    """
    Base de datos inteligente de clips visuales para sincronización semántica.
    
    Gestiona clasificación, búsqueda y optimización de clips para edits virales.
    """
    
    def __init__(self, database_path: str = None, clips_directory: str = None):
        self.database_path = database_path or "data/video_clips/clips_database.db"
        self.clips_directory = clips_directory or "data/video_clips"
        self.logger = logging.getLogger(f"{__name__}.VisualClipDatabase")
        
        # Ensure directories exist
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.clips_directory).mkdir(parents=True, exist_ok=True)
        
        # Integración ML
        if ML_CORE_AVAILABLE and not DUMMY_MODE:
            self.ml_video_detector = get_yolo_video_detector()
        else:
            self.ml_video_detector = None
        
        # Clasificaciones predefinidas
        self.genre_categories = [
            "trap", "drill", "reggaeton", "hip_hop", "electronic", 
            "pop", "rock", "urban", "latin", "ambient"
        ]
        
        self.emotion_categories = [
            "energetic", "aggressive", "calm", "romantic", "dark",
            "uplifting", "melancholic", "party", "intense", "chill"
        ]
        
        self.scene_types = [
            "urban_street", "studio", "club", "nature", "abstract",
            "performance", "lifestyle", "action", "cinematic", "minimal"
        ]
        
        # Inicializar base de datos
        self._initialize_database()
        
        self.logger.info("🎬 Visual Clip Database initialized")
    
    def _initialize_database(self):
        """Inicializa la base de datos SQLite"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS visual_clips (
                        clip_id TEXT PRIMARY KEY,
                        file_path TEXT NOT NULL,
                        duration REAL,
                        width INTEGER,
                        height INTEGER,
                        fps INTEGER,
                        genre TEXT,
                        emotion TEXT,
                        energy_level REAL,
                        visual_style TEXT,
                        color_dominant TEXT,
                        objects_detected TEXT,
                        scene_type TEXT,
                        movement_intensity REAL,
                        sync_compatibility TEXT,
                        optimal_tempo_min REAL,
                        optimal_tempo_max REAL,
                        cut_points TEXT,
                        viral_score REAL,
                        usage_count INTEGER DEFAULT 0,
                        avg_engagement REAL DEFAULT 0.0,
                        created_at TEXT,
                        last_used TEXT,
                        tags TEXT
                    )
                """)
                
                # Índices para búsqueda rápida
                conn.execute("CREATE INDEX IF NOT EXISTS idx_genre ON visual_clips(genre)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_emotion ON visual_clips(emotion)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_energy ON visual_clips(energy_level)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_viral_score ON visual_clips(viral_score)")
                
                conn.commit()
                
            self.logger.info("📋 Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
    
    async def scan_and_classify_clips(self, directory: str = None) -> Dict[str, Any]:
        """
        Escanea directorio y clasifica clips nuevos.
        
        Args:
            directory: Directorio a escanear (usa self.clips_directory por defecto)
            
        Returns:
            Estadísticas del proceso de clasificación
        """
        scan_dir = Path(directory or self.clips_directory)
        
        if not scan_dir.exists():
            self.logger.warning(f"📁 Directory not found: {scan_dir}")
            return {"error": "Directory not found"}
        
        self.logger.info(f"🔍 Scanning clips in: {scan_dir}")
        
        stats = {
            "scanned": 0,
            "new_clips": 0,
            "updated_clips": 0,
            "errors": 0
        }
        
        # Buscar archivos de video
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
        video_files = [
            f for f in scan_dir.rglob("*") 
            if f.suffix.lower() in video_extensions
        ]
        
        for video_file in video_files:
            stats["scanned"] += 1
            
            try:
                # Generar ID único para el clip
                clip_id = self._generate_clip_id(str(video_file))
                
                # Verificar si ya existe
                existing_clip = await self.get_clip(clip_id)
                
                if existing_clip:
                    self.logger.debug(f"📋 Clip already classified: {video_file.name}")
                    continue
                
                # Clasificar nuevo clip
                visual_clip = await self._classify_video_file(str(video_file))
                
                if visual_clip:
                    await self.add_clip(visual_clip)
                    stats["new_clips"] += 1
                    self.logger.info(f"✅ Classified: {video_file.name}")
                else:
                    stats["errors"] += 1
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing {video_file}: {e}")
                stats["errors"] += 1
        
        self.logger.info(f"🎬 Scan complete: {stats}")
        return stats
    
    async def _classify_video_file(self, file_path: str) -> Optional[VisualClip]:
        """Clasifica un archivo de video usando ML"""
        
        if DUMMY_MODE:
            return self._generate_dummy_classification(file_path)
        
        try:
            # TODO: Implementar clasificación real con ML
            # - Análisis de contenido con YOLOv8
            # - Análisis de color y movimiento
            # - Clasificación de escena
            
            return self._generate_dummy_classification(file_path)
            
        except Exception as e:
            self.logger.error(f"❌ Classification failed for {file_path}: {e}")
            return None
    
    def _generate_dummy_classification(self, file_path: str) -> VisualClip:
        """Genera clasificación dummy para testing"""
        
        clip_id = self._generate_clip_id(file_path)
        
        # Simular propiedades básicas
        duration = np.random.uniform(5, 30)
        resolution = np.random.choice([(1920, 1080), (1280, 720), (1080, 1920)])
        fps = np.random.choice([24, 30, 60])
        
        # Clasificaciones aleatorias pero coherentes
        genre = np.random.choice(self.genre_categories)
        emotion = np.random.choice(self.emotion_categories)
        energy_level = np.random.uniform(0.2, 1.0)
        
        # Estilos visuales
        visual_styles = ["cinematic", "urban_raw", "colorful", "monochrome", 
                        "neon", "natural", "abstract", "minimalist"]
        visual_style = np.random.choice(visual_styles)
        
        # Colores dominantes
        colors = ["red", "blue", "purple", "gold", "green", "pink", 
                 "orange", "black", "white", "multicolor"]
        color_dominant = np.random.choice(colors)
        
        # Objetos detectados simulados
        common_objects = ["person", "car", "building", "stage", "microphone",
                         "crowd", "lights", "urban_scene", "interior"]
        objects_detected = [
            {"object": obj, "confidence": np.random.uniform(0.6, 0.95)}
            for obj in np.random.choice(common_objects, size=np.random.randint(2, 6), replace=False)
        ]
        
        scene_type = np.random.choice(self.scene_types)
        movement_intensity = np.random.uniform(0.1, 1.0)
        
        # Compatibilidad de sync
        sync_compatibility = {}
        for sync_type in ["beat_heavy", "vocal_focused", "ambient", "aggressive"]:
            sync_compatibility[sync_type] = np.random.uniform(0.3, 1.0)
        
        # Tempo óptimo
        base_tempo = np.random.uniform(80, 160)
        optimal_tempo_range = (base_tempo - 20, base_tempo + 20)
        
        # Puntos de corte
        cut_points = []
        for i in range(int(duration // 3)):  # Cada ~3 segundos
            cut_points.append(np.random.uniform(i * 3, (i + 1) * 3))
        
        # Scores de performance
        viral_score = np.random.uniform(0.4, 0.95)
        usage_count = np.random.randint(0, 50)
        avg_engagement = np.random.uniform(0.2, 0.9)
        
        # Tags basados en clasificación
        tags = [genre, emotion, scene_type, visual_style]
        if energy_level > 0.7:
            tags.append("high_energy")
        if viral_score > 0.8:
            tags.append("viral_potential")
        
        return VisualClip(
            clip_id=clip_id,
            file_path=file_path,
            duration=duration,
            resolution=resolution,
            fps=fps,
            genre=genre,
            emotion=emotion,
            energy_level=energy_level,
            visual_style=visual_style,
            color_dominant=color_dominant,
            objects_detected=objects_detected,
            scene_type=scene_type,
            movement_intensity=movement_intensity,
            sync_compatibility=sync_compatibility,
            optimal_tempo_range=optimal_tempo_range,
            cut_points=cut_points,
            viral_score=viral_score,
            usage_count=usage_count,
            avg_engagement=avg_engagement,
            created_at=datetime.now().isoformat(),
            last_used=None,
            tags=tags
        )
    
    def _generate_clip_id(self, file_path: str) -> str:
        """Genera ID único para un clip basado en path y metadatos"""
        # Usar hash del path y timestamp de modificación
        file_stat = Path(file_path).stat()
        content = f"{file_path}_{file_stat.st_size}_{file_stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def add_clip(self, clip: VisualClip) -> bool:
        """Añade clip a la base de datos"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO visual_clips (
                        clip_id, file_path, duration, width, height, fps,
                        genre, emotion, energy_level, visual_style, color_dominant,
                        objects_detected, scene_type, movement_intensity,
                        sync_compatibility, optimal_tempo_min, optimal_tempo_max,
                        cut_points, viral_score, usage_count, avg_engagement,
                        created_at, last_used, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    clip.clip_id, clip.file_path, clip.duration,
                    clip.resolution[0], clip.resolution[1], clip.fps,
                    clip.genre, clip.emotion, clip.energy_level,
                    clip.visual_style, clip.color_dominant,
                    json.dumps(clip.objects_detected), clip.scene_type, clip.movement_intensity,
                    json.dumps(clip.sync_compatibility), clip.optimal_tempo_range[0], clip.optimal_tempo_range[1],
                    json.dumps(clip.cut_points), clip.viral_score, clip.usage_count, clip.avg_engagement,
                    clip.created_at, clip.last_used, json.dumps(clip.tags)
                ))
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add clip {clip.clip_id}: {e}")
            return False
    
    async def get_clip(self, clip_id: str) -> Optional[VisualClip]:
        """Obtiene clip por ID"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM visual_clips WHERE clip_id = ?", (clip_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_clip(row)
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get clip {clip_id}: {e}")
            return None
    
    async def search_clips(self, query: ClipQuery) -> List[VisualClip]:
        """
        Busca clips basado en criterios específicos.
        
        Args:
            query: Criterios de búsqueda
            
        Returns:
            Lista de clips que coinciden con los criterios
        """
        try:
            conditions = []
            params = []
            
            if query.genre:
                conditions.append("genre = ?")
                params.append(query.genre)
            
            if query.emotion:
                conditions.append("emotion = ?")
                params.append(query.emotion)
            
            if query.energy_min is not None:
                conditions.append("energy_level >= ?")
                params.append(query.energy_min)
            
            if query.energy_max is not None:
                conditions.append("energy_level <= ?")
                params.append(query.energy_max)
            
            if query.duration_min is not None:
                conditions.append("duration >= ?")
                params.append(query.duration_min)
            
            if query.duration_max is not None:
                conditions.append("duration <= ?")
                params.append(query.duration_max)
            
            if query.scene_type:
                conditions.append("scene_type = ?")
                params.append(query.scene_type)
            
            if query.viral_score_min is not None:
                conditions.append("viral_score >= ?")
                params.append(query.viral_score_min)
            
            if query.exclude_recent:
                # Excluir clips usados en las últimas 24 horas
                recent_threshold = (datetime.now() - timedelta(hours=24)).isoformat()
                conditions.append("(last_used IS NULL OR last_used < ?)")
                params.append(recent_threshold)
            
            # Construir query SQL
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            sql_query = f"""
                SELECT * FROM visual_clips 
                WHERE {where_clause}
                ORDER BY viral_score DESC, avg_engagement DESC
                LIMIT ?
            """
            params.append(query.limit)
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute(sql_query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_clip(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"❌ Search failed: {e}")
            return []
    
    def _row_to_clip(self, row: tuple) -> VisualClip:
        """Convierte fila de DB a objeto VisualClip"""
        return VisualClip(
            clip_id=row[0],
            file_path=row[1],
            duration=row[2],
            resolution=(row[3], row[4]),
            fps=row[5],
            genre=row[6],
            emotion=row[7],
            energy_level=row[8],
            visual_style=row[9],
            color_dominant=row[10],
            objects_detected=json.loads(row[11]) if row[11] else [],
            scene_type=row[12],
            movement_intensity=row[13],
            sync_compatibility=json.loads(row[14]) if row[14] else {},
            optimal_tempo_range=(row[15], row[16]),
            cut_points=json.loads(row[17]) if row[17] else [],
            viral_score=row[18],
            usage_count=row[19],
            avg_engagement=row[20],
            created_at=row[21],
            last_used=row[22],
            tags=json.loads(row[23]) if row[23] else []
        )
    
    async def update_clip_usage(self, clip_id: str, engagement_score: float = None):
        """Actualiza estadísticas de uso de un clip"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                # Incrementar contador de uso
                conn.execute("""
                    UPDATE visual_clips 
                    SET usage_count = usage_count + 1, last_used = ?
                    WHERE clip_id = ?
                """, (datetime.now().isoformat(), clip_id))
                
                # Actualizar engagement promedio si se proporciona
                if engagement_score is not None:
                    # Obtener engagement actual
                    cursor = conn.execute(
                        "SELECT avg_engagement, usage_count FROM visual_clips WHERE clip_id = ?",
                        (clip_id,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        current_avg, usage_count = row
                        # Calcular nuevo promedio
                        new_avg = ((current_avg * (usage_count - 1)) + engagement_score) / usage_count
                        
                        conn.execute("""
                            UPDATE visual_clips 
                            SET avg_engagement = ?
                            WHERE clip_id = ?
                        """, (new_avg, clip_id))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update clip usage {clip_id}: {e}")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la base de datos"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM visual_clips")
                total_clips = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT AVG(viral_score) FROM visual_clips")
                avg_viral_score = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("SELECT AVG(duration) FROM visual_clips")
                avg_duration = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("""
                    SELECT genre, COUNT(*) FROM visual_clips 
                    GROUP BY genre ORDER BY COUNT(*) DESC
                """)
                genre_distribution = dict(cursor.fetchall())
                
                cursor = conn.execute("""
                    SELECT emotion, COUNT(*) FROM visual_clips 
                    GROUP BY emotion ORDER BY COUNT(*) DESC
                """)
                emotion_distribution = dict(cursor.fetchall())
                
                return {
                    "total_clips": total_clips,
                    "avg_viral_score": round(avg_viral_score, 3),
                    "avg_duration": round(avg_duration, 2),
                    "genre_distribution": genre_distribution,
                    "emotion_distribution": emotion_distribution
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get database stats: {e}")
            return {}

# Factory function
def create_visual_clip_database(database_path: str = None, 
                               clips_directory: str = None) -> VisualClipDatabase:
    """Crea instancia de VisualClipDatabase"""
    return VisualClipDatabase(database_path, clips_directory)