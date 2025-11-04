"""
🛰️ SATELLITE ACCOUNTS MANAGER
Sistema de gestión de cuentas satélite para YouTube
Maneja múltiples canales con upload automático y distribución inteligente
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SatelliteAccount:
    """Cuenta satélite de YouTube"""
    id: str
    name: str
    channel_id: str
    niche: str
    upload_frequency: int
    upload_schedule: List[str]
    timezone: str
    credentials: Dict[str, str]
    video_config: Dict[str, Any]
    content_strategy: Dict[str, float]
    
    def __post_init__(self):
        self.last_upload = None
        self.total_uploads = 0
        self.total_views = 0
        self.is_active = True

@dataclass
class UploadTask:
    """Tarea de upload programada"""
    satellite_id: str
    video_path: str
    audio_path: str
    scheduled_time: datetime
    title: str
    description: str
    tags: List[str]
    status: str = "pending"  # pending, uploading, completed, failed

class SatelliteAccountsManager:
    """Gestor principal de cuentas satélite"""
    
    def __init__(self, config_path: str = "config/satellite_accounts_config.json"):
        self.config_path = Path(config_path)
        self.satellites: Dict[str, SatelliteAccount] = {}
        self.upload_queue: List[UploadTask] = []
        self.hub_account = None
        self.load_configuration()
        
        logger.info("🛰️ Satellite Accounts Manager initialized")
    
    def load_configuration(self):
        """Cargar configuración de cuentas satélite"""
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            
            # Cargar hub account
            hub_data = config['satellite_accounts']['hub_account']
            self.hub_account = {
                'channel_id': hub_data['channel_id'],
                'name': hub_data['name'],
                'role': hub_data['role']
            }
            
            # Cargar satélites
            for sat_data in config['satellite_accounts']['satellites']:
                satellite = SatelliteAccount(
                    id=sat_data['id'],
                    name=sat_data['name'],
                    channel_id=sat_data['channel_id'],
                    niche=sat_data['niche'],
                    upload_frequency=sat_data['upload_frequency'],
                    upload_schedule=sat_data['upload_schedule'],
                    timezone=sat_data['timezone'],
                    credentials=sat_data['youtube_credentials'],
                    video_config=sat_data['video_config'],
                    content_strategy=sat_data['content_strategy']
                )
                self.satellites[satellite.id] = satellite
            
            logger.info(f"✅ Loaded {len(self.satellites)} satellite accounts")
            
        except Exception as e:
            logger.error(f"❌ Error loading satellite config: {e}")
            raise
    
    def get_active_satellites(self) -> List[SatelliteAccount]:
        """Obtener satélites activos"""
        return [sat for sat in self.satellites.values() if sat.is_active]
    
    def select_satellite_for_content(self, niche: str = None) -> Optional[SatelliteAccount]:
        """
        Seleccionar satélite óptimo para contenido
        Usa load balancing y estrategia de contenido
        """
        active_sats = self.get_active_satellites()
        
        if not active_sats:
            logger.warning("⚠️ No active satellites available")
            return None
        
        # Filtrar por nicho si se especifica
        if niche:
            niche_sats = [s for s in active_sats if s.niche == niche]
            if niche_sats:
                active_sats = niche_sats
        
        # Seleccionar el menos utilizado (load balancing)
        selected = min(active_sats, key=lambda s: s.total_uploads)
        
        logger.info(f"🎯 Selected satellite: {selected.name} for upload")
        return selected
    
    async def schedule_upload(
        self,
        video_path: str,
        audio_path: str,
        niche: str = None,
        title: str = None,
        description: str = None,
        tags: List[str] = None
    ) -> UploadTask:
        """
        Programar upload en satélite óptimo
        """
        satellite = self.select_satellite_for_content(niche)
        
        if not satellite:
            raise ValueError("No satellite available for upload")
        
        # Calcular próximo slot disponible
        scheduled_time = self._get_next_upload_slot(satellite)
        
        # Generar título y descripción si no se proporcionan
        if not title:
            title = self._generate_title(satellite, audio_path)
        if not description:
            description = self._generate_description(satellite, audio_path)
        if not tags:
            tags = self._generate_tags(satellite, niche)
        
        task = UploadTask(
            satellite_id=satellite.id,
            video_path=video_path,
            audio_path=audio_path,
            scheduled_time=scheduled_time,
            title=title,
            description=description,
            tags=tags
        )
        
        self.upload_queue.append(task)
        logger.info(f"📅 Scheduled upload for {satellite.name} at {scheduled_time}")
        
        return task
    
    def _get_next_upload_slot(self, satellite: SatelliteAccount) -> datetime:
        """Calcular próximo slot de upload disponible"""
        now = datetime.now()
        
        # Buscar próximo horario programado
        for time_str in satellite.upload_schedule:
            hour, minute = map(int, time_str.split(':'))
            scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Si ya pasó hoy, programar para mañana
            if scheduled < now:
                scheduled += timedelta(days=1)
            
            # Verificar que no haya conflicto con otros uploads
            if not self._has_upload_conflict(satellite.id, scheduled):
                return scheduled
        
        # Si no hay slots, programar para mañana en el primer horario
        first_time = satellite.upload_schedule[0]
        hour, minute = map(int, first_time.split(':'))
        return (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def _has_upload_conflict(self, satellite_id: str, scheduled_time: datetime) -> bool:
        """Verificar si hay conflicto de horario"""
        min_delay = timedelta(hours=2)  # Mínimo 2 horas entre uploads
        
        for task in self.upload_queue:
            if task.satellite_id == satellite_id:
                time_diff = abs(task.scheduled_time - scheduled_time)
                if time_diff < min_delay:
                    return True
        return False
    
    def _generate_title(self, satellite: SatelliteAccount, audio_path: str) -> str:
        """Generar título optimizado para SEO"""
        # Extraer nombre de archivo/artista
        audio_name = Path(audio_path).stem
        
        # Templates por nicho
        templates = {
            'trap_spanish_latino': [
                f"🔥 {audio_name} | Trap Español 2025",
                f"💎 {audio_name} - Trap Latino Session",
                f"⚡ {audio_name} | Spanish Trap Beat"
            ],
            'reggaeton_urban': [
                f"🎵 {audio_name} | Reggaeton 2025",
                f"🔊 {audio_name} - Urban Latino Mix",
                f"💃 {audio_name} | Perreo Intenso"
            ],
            'hiphop_drill': [
                f"🎤 {audio_name} | Hip-Hop Underground",
                f"🔫 {audio_name} - Drill Session",
                f"💀 {audio_name} | Real Rap"
            ],
            'pop_latino_urban': [
                f"✨ {audio_name} | Pop Latino 2025",
                f"💫 {audio_name} - Latin Urban Hit",
                f"🌟 {audio_name} | Latin Pop"
            ],
            'freestyle_sessions': [
                f"🎙️ {audio_name} | Freestyle Session",
                f"🔥 {audio_name} - Street Cypher",
                f"💯 {audio_name} | Raw Freestyle"
            ]
        }
        
        niche_templates = templates.get(satellite.niche, templates['trap_spanish_latino'])
        return random.choice(niche_templates)
    
    def _generate_description(self, satellite: SatelliteAccount, audio_path: str) -> str:
        """Generar descripción optimizada"""
        audio_name = Path(audio_path).stem
        
        desc_template = f"""
🎵 {audio_name} - {satellite.name}

🔥 Nuevo video generado con IA
✨ Video exclusivo en {satellite.name}
📺 Suscríbete para más contenido

#trap #latino #hiphop #reggaeton #music2025 #aimusic #viral

⚠️ Todos los derechos reservados
📧 Contacto: contacto@{satellite.name.lower().replace(' ', '')}.com
        """.strip()
        
        return desc_template
    
    def _generate_tags(self, satellite: SatelliteAccount, niche: str = None) -> List[str]:
        """Generar tags optimizados para SEO"""
        base_tags = ["music", "2025", "ai generated", "viral"]
        
        niche_tags = {
            'trap_spanish_latino': ["trap", "trap español", "trap latino", "spanish trap"],
            'reggaeton_urban': ["reggaeton", "urban", "latino", "perreo"],
            'hiphop_drill': ["hip hop", "drill", "rap", "underground"],
            'pop_latino_urban': ["pop latino", "latin pop", "urban pop"],
            'freestyle_sessions': ["freestyle", "cypher", "street rap", "session"]
        }
        
        niche_specific = niche_tags.get(niche or satellite.niche, [])
        return base_tags + niche_specific
    
    async def process_upload_queue(self):
        """
        Procesar cola de uploads
        Ejecuta uploads programados en el momento correcto
        """
        logger.info("🔄 Starting upload queue processor")
        
        while True:
            now = datetime.now()
            
            # Buscar tasks pendientes que ya es hora de ejecutar
            for task in self.upload_queue[:]:
                if task.status == "pending" and task.scheduled_time <= now:
                    try:
                        await self._execute_upload(task)
                        task.status = "completed"
                        self.upload_queue.remove(task)
                        
                        # Actualizar contador del satélite
                        satellite = self.satellites[task.satellite_id]
                        satellite.total_uploads += 1
                        satellite.last_upload = now
                        
                        logger.info(f"✅ Upload completed for {satellite.name}")
                        
                    except Exception as e:
                        logger.error(f"❌ Upload failed: {e}")
                        task.status = "failed"
            
            # Esperar 1 minuto antes de revisar de nuevo
            await asyncio.sleep(60)
    
    async def _execute_upload(self, task: UploadTask):
        """
        Ejecutar upload a YouTube
        Combina video + audio y sube al canal satélite
        """
        satellite = self.satellites[task.satellite_id]
        
        logger.info(f"⬆️ Uploading to {satellite.name}...")
        task.status = "uploading"
        
        # TODO: Implementar upload real a YouTube API
        # Por ahora simulación
        await asyncio.sleep(5)
        
        logger.info(f"✅ Video uploaded successfully to {satellite.name}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de satélites"""
        active_sats = self.get_active_satellites()
        
        total_uploads = sum(s.total_uploads for s in self.satellites.values())
        total_views = sum(s.total_views for s in self.satellites.values())
        pending_uploads = len([t for t in self.upload_queue if t.status == "pending"])
        
        return {
            "total_satellites": len(self.satellites),
            "active_satellites": len(active_sats),
            "total_uploads": total_uploads,
            "total_views": total_views,
            "pending_uploads": pending_uploads,
            "satellites": [
                {
                    "id": sat.id,
                    "name": sat.name,
                    "uploads": sat.total_uploads,
                    "views": sat.total_views,
                    "last_upload": sat.last_upload.isoformat() if sat.last_upload else None
                }
                for sat in self.satellites.values()
            ]
        }

# Función de conveniencia para uso global
def create_satellite_manager(config_path: str = None) -> SatelliteAccountsManager:
    """Crear instancia del gestor de satélites"""
    return SatelliteAccountsManager(config_path or "config/satellite_accounts_config.json")
