"""
🎬 LongCat Video Production Integration
=====================================
Production-ready video generation for Neural Forge campaigns
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Import LongCat Video Generation
from ml_core.video_generation import (
    LongCatVideoGenerator,
    VideoGenerationRequest,
    VideoGenerationConfig,
    create_video_generator
)

logger = logging.getLogger(__name__)

class ProductionVideoGenerator:
    """Production wrapper for LongCat Video Generation"""
    
    def __init__(self):
        self.generator = None
        self.initialized = False
        
        # Production configuration
        self.config = {
            "output_dir": "data/generated_videos/production",
            "models_dir": "data/models/longcat",
            "cache_dir": "data/cache/longcat",
            "quality": "high",
            "production_mode": True
        }
        
        # Create directories
        for dir_path in [self.config["output_dir"], self.config["models_dir"], self.config["cache_dir"]]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self) -> bool:
        """Initialize production video generator"""
        try:
            if self.initialized:
                return True
            
            logger.info("🎬 Initializing LongCat Production Video Generator...")
            
            # Create generator with production config
            self.generator = create_video_generator(self.config)
            
            # Initialize models
            success = await self.generator.initialize()
            
            if success:
                self.initialized = True
                logger.info("✅ LongCat Production Video Generator ready")
                return True
            else:
                logger.error("❌ Failed to initialize video generator")
                return False
                
        except Exception as e:
            logger.error(f"❌ Video generator initialization error: {e}")
            return False
    
    async def generate_music_video(self, 
                                  artist: str,
                                  song: str,
                                  prompt: str,
                                  genre: str = "trap",
                                  duration: int = 30) -> Dict[str, Any]:
        """Generate music video for viral campaign"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Enhanced prompt for music videos
            enhanced_prompt = f"""
            {prompt}
            Musical video for {artist} - {song}
            {genre} music style, professional music video quality
            High energy, engaging visuals, sync with beat
            Urban setting, dynamic camera movements
            Professional lighting, cinematic quality
            """
            
            # Video generation request
            request = VideoGenerationRequest(
                type="text-to-video",
                prompt=enhanced_prompt.strip(),
                negative_prompt="low quality, blurry, distorted, amateur, bad lighting",
                config=VideoGenerationConfig(
                    resolution="720p",
                    num_frames=min(duration * 30, 180),  # Max 6 seconds for now
                    fps=30,
                    quality="high",
                    num_inference_steps=50,
                    guidance_scale=7.5
                ),
                output_name=f"{artist}_{song}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            logger.info(f"🎬 Generating music video: {artist} - {song}")
            logger.info(f"📝 Prompt: {enhanced_prompt[:100]}...")
            
            # Generate video
            result = await self.generator.generate_video(request)
            
            if result.success:
                logger.info(f"✅ Music video generated: {result.video_path}")
                
                return {
                    "success": True,
                    "video_path": result.video_path,
                    "thumbnail_path": result.thumbnail_path,
                    "duration": result.duration,
                    "resolution": result.resolution,
                    "file_size": result.file_size,
                    "generation_time": result.generation_time,
                    "artist": artist,
                    "song": song,
                    "genre": genre,
                    "prompt_used": enhanced_prompt
                }
            else:
                logger.error(f"❌ Video generation failed: {result.error_message}")
                return {
                    "success": False,
                    "error": result.error_message,
                    "artist": artist,
                    "song": song
                }
                
        except Exception as e:
            logger.error(f"❌ Music video generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "artist": artist,
                "song": song
            }
    
    async def generate_promotional_video(self,
                                       artist: str,
                                       song: str,
                                       image_path: str,
                                       duration: int = 15) -> Dict[str, Any]:
        """Generate promotional video from artist image"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Image-to-video generation
            request = VideoGenerationRequest(
                type="image-to-video",
                prompt=f"Promotional video for {artist} - {song}, dynamic movement, music sync",
                image_input=image_path,
                config=VideoGenerationConfig(
                    resolution="720p",
                    num_frames=min(duration * 30, 120),
                    fps=30,
                    quality="high"
                )
            )
            
            result = await self.generator.generate_video(request)
            
            if result.success:
                return {
                    "success": True,
                    "video_path": result.video_path,
                    "thumbnail_path": result.thumbnail_path,
                    "type": "promotional",
                    "source_image": image_path
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message
                }
                
        except Exception as e:
            logger.error(f"❌ Promotional video error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_generator_status(self) -> Dict[str, Any]:
        """Get production video generator status"""
        if not self.generator:
            return {
                "initialized": False,
                "status": "not_initialized"
            }
        
        capabilities = self.generator.get_capabilities()
        health = await self.generator.health_check()
        
        return {
            "initialized": self.initialized,
            "status": "ready" if self.initialized else "initializing",
            "capabilities": capabilities,
            "health": health,
            "config": self.config
        }

# Global production video generator instance
production_video_generator = ProductionVideoGenerator()

# Factory function for easy access
async def get_production_video_generator() -> ProductionVideoGenerator:
    """Get initialized production video generator"""
    global production_video_generator
    
    if not production_video_generator.initialized:
        await production_video_generator.initialize()
    
    return production_video_generator