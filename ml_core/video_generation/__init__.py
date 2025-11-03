"""
🎬 LONGCAT VIDEO MODULE - INIT
==============================

Módulo completo de generación de video usando LongCat-Video
Reemplazo completo y superior del módulo Runway
"""

from .longcat_generator import (
    LongCatVideoGenerator,
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoGenerationConfig,
    create_video_generator,
    generate_video_from_text
)

from .longcat_api import (
    router as video_api_router,
    include_video_api
)

__all__ = [
    "LongCatVideoGenerator",
    "VideoGenerationRequest", 
    "VideoGenerationResult",
    "VideoGenerationConfig",
    "create_video_generator",
    "generate_video_from_text",
    "video_api_router",
    "include_video_api"
]

# Información del módulo
__version__ = "1.0.0"
__description__ = "LongCat-Video integration for musical content generation"
__author__ = "Discográfica ML System"

# Configuración por defecto
DEFAULT_CONFIG = {
    "output_dir": "data/generated_videos",
    "models_dir": "data/models/longcat", 
    "cache_dir": "data/cache/longcat",
    "resolution": "720p",
    "num_frames": 93,
    "fps": 30,
    "quality": "high"
}