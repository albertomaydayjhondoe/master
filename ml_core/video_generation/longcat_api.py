"""
🎬 LONGCAT VIDEO API - INTEGRACIÓN ML CORE
==========================================

API completa para integración de LongCat-Video en el sistema ML
Proporciona endpoints REST para generación de video
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
import os
import asyncio
from pathlib import Path

from .longcat_generator import (
    LongCatVideoGenerator,
    VideoGenerationRequest,
    VideoGenerationResult,
    VideoGenerationConfig,
    create_video_generator
)

# Router para la API
router = APIRouter(prefix="/api/v1/video", tags=["Video Generation"])

# Instancia global del generador
video_generator: Optional[LongCatVideoGenerator] = None

# Modelos Pydantic para la API
class TextToVideoRequest(BaseModel):
    prompt: str = Field(..., description="Texto descriptivo para generar el video")
    negative_prompt: Optional[str] = Field(None, description="Elementos a evitar en el video")
    resolution: Literal["480p", "720p"] = Field("720p", description="Resolución del video")
    num_frames: int = Field(93, ge=1, le=300, description="Número de frames")
    num_inference_steps: int = Field(50, ge=10, le=100, description="Pasos de inferencia")
    guidance_scale: float = Field(4.0, ge=1.0, le=20.0, description="Escala de guidance")

class ImageToVideoRequest(BaseModel):
    prompt: str = Field(..., description="Texto descriptivo para generar el video")
    negative_prompt: Optional[str] = Field(None, description="Elementos a evitar")
    resolution: Literal["480p", "720p"] = Field("720p", description="Resolución del video")
    num_frames: int = Field(93, ge=1, le=300, description="Número de frames")
    num_inference_steps: int = Field(50, ge=10, le=100, description="Pasos de inferencia")
    guidance_scale: float = Field(4.0, ge=1.0, le=20.0, description="Escala de guidance")

class VideoContinuationRequest(BaseModel):
    prompt: Optional[str] = Field("", description="Texto para guiar la continuación")
    negative_prompt: Optional[str] = Field(None, description="Elementos a evitar")
    resolution: Literal["480p", "720p"] = Field("720p", description="Resolución del video")
    num_frames: int = Field(93, ge=1, le=300, description="Número de frames a generar")
    num_inference_steps: int = Field(50, ge=10, le=100, description="Pasos de inferencia")
    guidance_scale: float = Field(4.0, ge=1.0, le=20.0, description="Escala de guidance")

class VideoGenerationResponse(BaseModel):
    success: bool
    task_id: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    resolution: Optional[str] = None
    file_size: Optional[int] = None
    generation_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

async def get_video_generator() -> LongCatVideoGenerator:
    """Obtener instancia del generador de video"""
    global video_generator
    
    if video_generator is None:
        config = {
            "output_dir": "data/generated_videos",
            "models_dir": "data/models/longcat",
            "cache_dir": "data/cache/longcat"
        }
        video_generator = create_video_generator(config)
        await video_generator.initialize()
    
    return video_generator

@router.get("/health")
async def health_check():
    """Verificar estado del sistema de video"""
    try:
        generator = await get_video_generator()
        health = await generator.health_check()
        return JSONResponse(content=health)
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

@router.get("/capabilities")
async def get_capabilities():
    """Obtener capacidades del sistema"""
    try:
        generator = await get_video_generator()
        capabilities = generator.get_capabilities()
        return JSONResponse(content=capabilities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/text-to-video", response_model=VideoGenerationResponse)
async def generate_text_to_video(request: TextToVideoRequest, background_tasks: BackgroundTasks):
    """Generar video desde texto"""
    try:
        generator = await get_video_generator()
        
        # Crear request interno
        video_request = VideoGenerationRequest(
            type="text-to-video",
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            config=VideoGenerationConfig(
                resolution=request.resolution,
                num_frames=request.num_frames,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale
            )
        )
        
        # Generar video
        result = await generator.generate_video(video_request)
        
        # Preparar respuesta
        return VideoGenerationResponse(
            success=result.success,
            video_url=f"/api/v1/video/download/{Path(result.video_path).name}" if result.video_path else None,
            thumbnail_url=f"/api/v1/video/thumbnail/{Path(result.thumbnail_path).name}" if result.thumbnail_path else None,
            duration=result.duration,
            resolution=result.resolution,
            file_size=result.file_size,
            generation_time=result.generation_time,
            error_message=result.error_message,
            metadata=result.metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/image-to-video", response_model=VideoGenerationResponse)
async def generate_image_to_video(
    image: UploadFile = File(...),
    prompt: str = "",
    negative_prompt: Optional[str] = None,
    resolution: Literal["480p", "720p"] = "720p",
    num_frames: int = 93,
    num_inference_steps: int = 50,
    guidance_scale: float = 4.0
):
    """Generar video desde imagen"""
    try:
        generator = await get_video_generator()
        
        # Guardar imagen temporal
        temp_dir = Path("data/temp")
        temp_dir.mkdir(exist_ok=True)
        image_path = temp_dir / f"temp_image_{os.urandom(8).hex()}.{image.filename.split('.')[-1]}"
        
        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        try:
            # Crear request interno
            video_request = VideoGenerationRequest(
                type="image-to-video",
                prompt=prompt,
                negative_prompt=negative_prompt,
                image_input=str(image_path),
                config=VideoGenerationConfig(
                    resolution=resolution,
                    num_frames=num_frames,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale
                )
            )
            
            # Generar video
            result = await generator.generate_video(video_request)
            
            return VideoGenerationResponse(
                success=result.success,
                video_url=f"/api/v1/video/download/{Path(result.video_path).name}" if result.video_path else None,
                thumbnail_url=f"/api/v1/video/thumbnail/{Path(result.thumbnail_path).name}" if result.thumbnail_path else None,
                duration=result.duration,
                resolution=result.resolution,
                file_size=result.file_size,
                generation_time=result.generation_time,
                error_message=result.error_message,
                metadata=result.metadata
            )
            
        finally:
            # Limpiar archivo temporal
            if image_path.exists():
                image_path.unlink()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/video-continuation", response_model=VideoGenerationResponse)
async def generate_video_continuation(
    video: UploadFile = File(...),
    request: VideoContinuationRequest = None
):
    """Continuar/extender video existente"""
    try:
        generator = await get_video_generator()
        
        # Usar valores por defecto si no se proporciona request
        if request is None:
            request = VideoContinuationRequest()
        
        # Guardar video temporal
        temp_dir = Path("data/temp")
        temp_dir.mkdir(exist_ok=True)
        video_path = temp_dir / f"temp_video_{os.urandom(8).hex()}.{video.filename.split('.')[-1]}"
        
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        try:
            # Crear request interno
            video_request = VideoGenerationRequest(
                type="video-continuation",
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                video_input=str(video_path),
                config=VideoGenerationConfig(
                    resolution=request.resolution,
                    num_frames=request.num_frames,
                    num_inference_steps=request.num_inference_steps,
                    guidance_scale=request.guidance_scale
                )
            )
            
            # Generar video
            result = await generator.generate_video(video_request)
            
            return VideoGenerationResponse(
                success=result.success,
                video_url=f"/api/v1/video/download/{Path(result.video_path).name}" if result.video_path else None,
                thumbnail_url=f"/api/v1/video/thumbnail/{Path(result.thumbnail_path).name}" if result.thumbnail_path else None,
                duration=result.duration,
                resolution=result.resolution,
                file_size=result.file_size,
                generation_time=result.generation_time,
                error_message=result.error_message,
                metadata=result.metadata
            )
            
        finally:
            # Limpiar archivo temporal
            if video_path.exists():
                video_path.unlink()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_video(filename: str):
    """Descargar video generado"""
    try:
        video_path = Path("data/generated_videos") / filename
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video no encontrado")
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/thumbnail/{filename}")
async def download_thumbnail(filename: str):
    """Descargar thumbnail de video"""
    try:
        thumbnail_path = Path("data/generated_videos") / filename
        
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail no encontrado")
        
        return FileResponse(
            path=str(thumbnail_path),
            media_type="image/jpeg",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_generated_videos():
    """Listar videos generados"""
    try:
        videos_dir = Path("data/generated_videos")
        
        if not videos_dir.exists():
            return {"videos": []}
        
        videos = []
        for video_file in videos_dir.glob("*.mp4"):
            # Buscar thumbnail correspondiente
            thumbnail_file = video_file.with_suffix("").with_suffix("_thumb.jpg")
            
            video_info = {
                "filename": video_file.name,
                "video_url": f"/api/v1/video/download/{video_file.name}",
                "thumbnail_url": f"/api/v1/video/thumbnail/{thumbnail_file.name}" if thumbnail_file.exists() else None,
                "size": video_file.stat().st_size,
                "created": video_file.stat().st_mtime
            }
            videos.append(video_info)
        
        return {"videos": sorted(videos, key=lambda x: x["created"], reverse=True)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_old_videos(days_old: int = 7):
    """Limpiar videos antiguos"""
    try:
        import time
        
        videos_dir = Path("data/generated_videos")
        temp_dir = Path("data/temp")
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        # Limpiar videos generados antiguos
        for video_file in videos_dir.glob("*"):
            if video_file.stat().st_mtime < cutoff_time:
                video_file.unlink()
                deleted_count += 1
        
        # Limpiar archivos temporales
        for temp_file in temp_dir.glob("*"):
            if temp_file.stat().st_mtime < cutoff_time:
                temp_file.unlink()
                deleted_count += 1
        
        return {"deleted_files": deleted_count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Función para integrar en la aplicación principal
def include_video_api(app):
    """Incluir API de video en la aplicación principal"""
    app.include_router(router)

# Export del router para uso externo
longcat_router = router