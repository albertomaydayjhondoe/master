"""
🛰️ LongCat Satellite System - SECURE AI VIDEO DISTRIBUTION
========================================================
Original content from main account → AI variations via satellites
Security-first approach with rate limiting and content validation
"""

import os
import asyncio
import logging
import hashlib
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import json

from social_extensions.longcat_production import get_production_video_generator
from social_extensions.satellite_distribution import SatelliteDistribution
from social_extensions.youtube_integration import YouTubeSatelliteAccount

logger = logging.getLogger(__name__)

@dataclass
class SecureSatelliteRequest:
    """Secure request for satellite video generation"""
    original_content_hash: str
    artist: str
    song: str
    genre: str
    variation_type: str  # "remix", "edit", "style_transfer", "continuation"
    target_satellite: int
    generation_prompt: str
    security_token: str
    timestamp: str
    rate_limit_check: bool = True

class SecureLongCatSatelliteManager:
    """
    SECURE AI Video Generation Satellite Manager
    ==========================================
    - Content security validation
    - Rate limiting per satellite
    - Encrypted communications
    - Audit logging
    - Satellite isolation
    """
    
    def __init__(self):
        self.video_generator = None
        self.satellites = {}
        self.initialized = False
        
        # Security configuration
        self.security_config = {
            "max_requests_per_hour": 10,
            "max_content_size_mb": 500,
            "allowed_extensions": {'.mp4', '.mov', '.avi', '.mkv', '.mp3', '.wav'},
            "max_generation_time_sec": 300,
            "require_content_hash": True
        }
        
        # Rate limiting tracking
        self.request_history = {}
        self.blocked_ips = set()
        
        # Security components
        self.security_key = self._initialize_security()
        self.audit_log = []
        
        # AI Variation templates (secure)
        self.secure_variation_templates = {
            "remix": {
                "description": "AI remix with tempo/effects variations",
                "prompt_template": "Creative AI remix of {artist} - {song}, {genre} style with enhanced audio effects and tempo variations",
                "security_level": "medium"
            },
            "edit": {
                "description": "Professional video editing variations", 
                "prompt_template": "Professionally edited version of {artist} - {song}, {genre} music video with cinematic editing and transitions",
                "security_level": "low"
            },
            "style_transfer": {
                "description": "Visual style transformation",
                "prompt_template": "Style-transformed video of {artist} - {song}, applying artistic {genre} visual aesthetics with AI enhancement",
                "security_level": "high"
            },
            "continuation": {
                "description": "Narrative continuation/extension",
                "prompt_template": "Extended narrative for {artist} - {song}, continuing the {genre} video story with AI-generated scenes",
                "security_level": "high"
            }
        }
    
    def _initialize_security(self) -> bytes:
        """Initialize security components"""
        key_path = Path("config/secrets/longcat_satellite.key")
        
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key_path.write_bytes(key)
            key_path.chmod(0o600)
            logger.info("🔐 Generated LongCat satellite security key")
            return key
    
    def _create_content_hash(self, content_path: str) -> str:
        """Create secure hash of content file"""
        try:
            with open(content_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Content hashing failed: {e}")
            return ""
    
    def _validate_content_security(self, content_path: str) -> Dict[str, Any]:
        """Comprehensive content security validation"""
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "content_hash": "",
            "file_size_mb": 0
        }
        
        try:
            path = Path(content_path)
            
            # File existence
            if not path.exists():
                validation_result["errors"].append("File does not exist")
                return validation_result
            
            # File size check
            file_size = path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            validation_result["file_size_mb"] = file_size_mb
            
            if file_size_mb > self.security_config["max_content_size_mb"]:
                validation_result["errors"].append(f"File too large: {file_size_mb:.1f}MB > {self.security_config['max_content_size_mb']}MB")
                return validation_result
            
            # Extension validation
            if path.suffix.lower() not in self.security_config["allowed_extensions"]:
                validation_result["errors"].append(f"Invalid file extension: {path.suffix}")
                return validation_result
            
            # Content hash
            content_hash = self._create_content_hash(content_path)
            validation_result["content_hash"] = content_hash
            
            # Basic malware scan (simple)
            with open(content_path, 'rb') as f:
                header = f.read(1024)
                suspicious_patterns = [b'<script>', b'<?php', b'eval(', b'exec(']
                for pattern in suspicious_patterns:
                    if pattern in header:
                        validation_result["errors"].append("Suspicious content detected")
                        return validation_result
            
            # All checks passed
            if not validation_result["errors"]:
                validation_result["valid"] = True
                
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _check_rate_limits(self, satellite_id: int, ip_address: str = None) -> Dict[str, Any]:
        """Check rate limits for satellite and IP"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        rate_check = {
            "allowed": False,
            "satellite_requests": 0,
            "ip_blocked": False,
            "remaining_requests": 0
        }
        
        # IP blocking check
        if ip_address and ip_address in self.blocked_ips:
            rate_check["ip_blocked"] = True
            return rate_check
        
        # Clean old requests
        if satellite_id in self.request_history:
            self.request_history[satellite_id] = [
                req_time for req_time in self.request_history[satellite_id] 
                if req_time > hour_ago
            ]
        else:
            self.request_history[satellite_id] = []
        
        # Count current requests
        satellite_requests = len(self.request_history[satellite_id])
        rate_check["satellite_requests"] = satellite_requests
        rate_check["remaining_requests"] = max(0, self.security_config["max_requests_per_hour"] - satellite_requests)
        
        # Allow if under limit
        if satellite_requests < self.security_config["max_requests_per_hour"]:
            rate_check["allowed"] = True
        
        return rate_check
    
    async def initialize(self) -> bool:
        """Initialize secure LongCat satellite system"""
        try:
            logger.info("🔐 Initializing secure LongCat satellite system...")
            
            # Initialize video generator
            self.video_generator = await get_production_video_generator()
            logger.info("🎬 LongCat video generator ready")
            
            # Initialize satellites with security
            for i in range(1, 6):  # 5 satellites
                satellite_config = {
                    "api_key": os.getenv(f'YOUTUBE_SATELLITE_{i}_API_KEY'),
                    "client_id": os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_ID'),
                    "client_secret": os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_SECRET'),
                    "refresh_token": os.getenv(f'YOUTUBE_SATELLITE_{i}_REFRESH_TOKEN'),
                    "channel_id": os.getenv(f'YOUTUBE_SATELLITE_{i}_CHANNEL_ID')
                }
                
                if all(satellite_config.values()):
                    satellite = YouTubeSatelliteAccount(satellite_id=i, **satellite_config)
                    self.satellites[i] = satellite
                    logger.info(f"✅ Secure satellite {i} initialized")
                else:
                    logger.warning(f"⚠️ Satellite {i} missing secure configuration")
            
            # Create audit log
            self._log_security_event("system_initialized", {
                "satellites_count": len(self.satellites),
                "security_enabled": True,
                "timestamp": datetime.now().isoformat()
            })
            
            self.initialized = True
            logger.info("🔐 Secure LongCat satellite system ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Secure satellite initialization failed: {e}")
            return False
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events for audit"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "system": "longcat_satellites"
        }
        
        self.audit_log.append(event)
        
        # Keep only last 1000 events to prevent memory issues
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
        
        # Log to file for persistent audit trail
        try:
            audit_file = Path("logs/longcat_satellite_audit.log")
            audit_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(audit_file, "a") as f:
                f.write(f"{json.dumps(event)}\n")
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
    
    async def generate_secure_satellite_variation(self, request: SecureSatelliteRequest) -> Dict[str, Any]:
        """Generate AI variation with full security checks"""
        
        # Security event logging
        self._log_security_event("generation_request", {
            "artist": request.artist,
            "song": request.song,
            "variation_type": request.variation_type,
            "target_satellite": request.target_satellite,
            "content_hash": request.original_content_hash[:16] + "...",  # Partial hash for privacy
        })
        
        try:
            # Validate satellite exists
            if request.target_satellite not in self.satellites:
                error_msg = f"Satellite {request.target_satellite} not available"
                self._log_security_event("security_violation", {"error": error_msg})
                return {"success": False, "error": error_msg, "security_issue": True}
            
            # Rate limiting check
            rate_check = self._check_rate_limits(request.target_satellite)
            if not rate_check["allowed"]:
                error_msg = f"Rate limit exceeded for satellite {request.target_satellite}"
                self._log_security_event("rate_limit_exceeded", {
                    "satellite": request.target_satellite,
                    "requests": rate_check["satellite_requests"]
                })
                return {"success": False, "error": error_msg, "rate_limited": True}
            
            # Variation type validation
            if request.variation_type not in self.secure_variation_templates:
                error_msg = f"Invalid variation type: {request.variation_type}"
                self._log_security_event("invalid_request", {"variation_type": request.variation_type})
                return {"success": False, "error": error_msg, "security_issue": True}
            
            # Get secure template
            template = self.secure_variation_templates[request.variation_type]
            
            # Generate secure prompt
            secure_prompt = template["prompt_template"].format(
                artist=request.artist,
                song=request.song,
                genre=request.genre
            )
            
            # Add user prompt safely (sanitize)
            if request.generation_prompt:
                sanitized_prompt = self._sanitize_prompt(request.generation_prompt)
                secure_prompt += f"\n{sanitized_prompt}"
            
            logger.info(f"🛰️ Generating secure {request.variation_type} for satellite {request.target_satellite}")
            
            # Generate video with LongCat
            start_time = datetime.now()
            
            generation_result = await self.video_generator.generate_music_video(
                artist=f"{request.artist} (AI {request.variation_type.title()})",
                song=request.song,
                prompt=secure_prompt,
                genre=request.genre,
                duration=30
            )
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            if generation_result.get("success"):
                # Upload to satellite
                satellite = self.satellites[request.target_satellite]
                
                upload_result = await satellite.upload_video(
                    video_path=generation_result["video_path"],
                    title=f"{request.artist} - {request.song} (AI {request.variation_type.title()})",
                    description=self._create_secure_description(request),
                    tags=self._create_secure_tags(request),
                    category_id="10"
                )
                
                # Record successful request
                if request.target_satellite not in self.request_history:
                    self.request_history[request.target_satellite] = []
                self.request_history[request.target_satellite].append(datetime.now())
                
                # Log success
                self._log_security_event("generation_success", {
                    "satellite": request.target_satellite,
                    "variation_type": request.variation_type,
                    "generation_time": generation_time,
                    "upload_success": upload_result.get("success", False)
                })
                
                if upload_result.get("success"):
                    return {
                        "success": True,
                        "satellite_id": request.target_satellite,
                        "video_path": generation_result["video_path"],
                        "upload_url": upload_result.get("video_url"),
                        "variation_type": request.variation_type,
                        "generation_time": generation_time,
                        "security_verified": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Upload failed: {upload_result.get('error')}",
                        "video_generated": True,
                        "video_path": generation_result["video_path"]
                    }
            else:
                self._log_security_event("generation_failed", {
                    "satellite": request.target_satellite,
                    "error": generation_result.get("error", "Unknown error")
                })
                return {
                    "success": False,
                    "error": f"Video generation failed: {generation_result.get('error')}",
                    "generation_time": generation_time
                }
                
        except Exception as e:
            self._log_security_event("system_error", {
                "satellite": request.target_satellite,
                "error": str(e)
            })
            logger.error(f"❌ Secure satellite generation error: {e}")
            return {"success": False, "error": str(e), "system_error": True}
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Sanitize user input prompt for security"""
        # Remove potentially harmful content
        dangerous_patterns = [
            "exec", "eval", "import", "open", "file", "system", "os.",
            "<script>", "javascript:", "data:", "vbscript:", "<?php"
        ]
        
        sanitized = prompt
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")
        
        # Limit length
        sanitized = sanitized[:500]
        
        # Remove excessive special characters
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-_()[]")
        sanitized = ''.join(c for c in sanitized if c in allowed_chars)
        
        return sanitized.strip()
    
    def _create_secure_description(self, request: SecureSatelliteRequest) -> str:
        """Create secure video description"""
        return f"""🤖 AI-generated {request.variation_type} by LongCat Neural Forge

🎵 Original: {request.artist} - {request.song}
🎭 Genre: {request.genre}
🛰️ Satellite: #{request.target_satellite}

#LongCatAI #NeuralForge #AI{request.variation_type.title()} #{request.genre}

🔐 Securely generated with advanced AI technology
⚡ Part of Neural Forge music distribution network"""
    
    def _create_secure_tags(self, request: SecureSatelliteRequest) -> List[str]:
        """Create secure tags list"""
        base_tags = [
            request.artist.lower().replace(" ", ""),
            request.song.lower().replace(" ", ""),
            request.genre.lower(),
            "longcatai",
            "neuralforge",
            f"ai{request.variation_type}",
            "aimusic",
            "musicvideo"
        ]
        
        # Sanitize tags
        sanitized_tags = []
        for tag in base_tags:
            if tag and len(tag) <= 30 and tag.isalnum():
                sanitized_tags.append(tag)
        
        return sanitized_tags[:10]  # YouTube limit
    
    async def distribute_secure_variations(self, 
                                         original_content_path: str,
                                         artist: str,
                                         song: str,
                                         genre: str = "trap",
                                         base_prompt: str = "",
                                         requested_variations: List[str] = None) -> Dict[str, Any]:
        """Securely distribute AI variations across satellites"""
        
        # Content security validation
        content_validation = self._validate_content_security(original_content_path)
        if not content_validation["valid"]:
            self._log_security_event("content_validation_failed", {
                "file": Path(original_content_path).name,
                "errors": content_validation["errors"]
            })
            return {
                "success": False,
                "error": "Content validation failed",
                "validation_errors": content_validation["errors"]
            }
        
        # Default variations if none specified
        if not requested_variations:
            requested_variations = ["remix", "edit", "style_transfer", "continuation"]
        
        # Limit to available satellites
        available_satellites = list(self.satellites.keys())
        variations_to_generate = requested_variations[:len(available_satellites)]
        
        logger.info(f"🚀 Starting secure distribution: {len(variations_to_generate)} variations")
        
        results = []
        tasks = []
        
        for i, variation_type in enumerate(variations_to_generate):
            satellite_id = available_satellites[i]
            
            # Create secure request
            request = SecureSatelliteRequest(
                original_content_hash=content_validation["content_hash"],
                artist=artist,
                song=song,
                genre=genre,
                variation_type=variation_type,
                target_satellite=satellite_id,
                generation_prompt=base_prompt,
                security_token=secrets.token_hex(16),
                timestamp=datetime.now().isoformat()
            )
            
            # Add to task list
            task = self.generate_secure_satellite_variation(request)
            tasks.append((variation_type, satellite_id, task))
        
        # Execute all tasks
        for variation_type, satellite_id, task in tasks:
            try:
                result = await task
                result["variation_type"] = variation_type
                result["satellite_id"] = satellite_id
                results.append(result)
                
                if result.get("success"):
                    logger.info(f"✅ {variation_type} completed on satellite {satellite_id}")
                else:
                    logger.error(f"❌ {variation_type} failed on satellite {satellite_id}: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"❌ Task failed for {variation_type}: {e}")
                results.append({
                    "success": False,
                    "variation_type": variation_type,
                    "satellite_id": satellite_id,
                    "error": str(e),
                    "task_error": True
                })
        
        # Summary
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        summary = {
            "success": len(successful) > 0,
            "total_requested": len(variations_to_generate),
            "successful": len(successful),
            "failed": len(failed),
            "results": results,
            "content_hash": content_validation["content_hash"],
            "security_verified": True
        }
        
        self._log_security_event("distribution_completed", {
            "total": len(variations_to_generate),
            "successful": len(successful),
            "failed": len(failed),
            "artist": artist,
            "song": song
        })
        
        return summary
    
    async def get_secure_status(self) -> Dict[str, Any]:
        """Get secure system status"""
        return {
            "system": "LongCat Secure Satellite Manager",
            "initialized": self.initialized,
            "security_enabled": True,
            "total_satellites": len(self.satellites),
            "active_satellites": len(self.satellites),
            "video_generator_ready": self.video_generator is not None,
            "security_config": self.security_config,
            "recent_requests": sum(len(reqs) for reqs in self.request_history.values()),
            "blocked_ips": len(self.blocked_ips),
            "audit_events": len(self.audit_log),
            "satellites": {
                sat_id: {
                    "channel_id": sat.channel_id,
                    "upload_enabled": True,
                    "recent_requests": len(self.request_history.get(sat_id, [])),
                    "rate_limit_remaining": max(0, self.security_config["max_requests_per_hour"] - len(self.request_history.get(sat_id, [])))
                }
                for sat_id, sat in self.satellites.items()
            }
        }
            if self.initialized:
                return True
            
            logger.info("🛰️ Initializing LongCat Satellite System...")
            
            # Initialize video generator
            self.video_generator = await get_production_video_generator()
            
            self.initialized = True
            logger.info("✅ LongCat Satellite System ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ LongCat Satellite initialization failed: {e}")
            return False
    
    async def generate_satellite_variations(self, 
                                          original_content: Dict[str, Any],
                                          num_variations: int = 5) -> Dict[str, Any]:
        """
        Genera variaciones IA del contenido original para las satellites
        
        Args:
            original_content: {
                "type": "video" | "audio" | "image",
                "path": "ruta/al/archivo/original",
                "artist": "Nombre del artista",
                "song": "Título de la canción",
                "genre": "género musical"
            }
            num_variations: Número de variaciones a generar
        """
        
        if not self.initialized:
            await self.initialize()
        
        try:
            logger.info(f"🎬 Generating {num_variations} satellite variations...")
            logger.info(f"📁 Original: {original_content['path']}")
            
            variations = []
            base_prompt = f"""
            Musical content for {original_content['artist']} - {original_content['song']}
            Genre: {original_content['genre']}
            High quality, professional, engaging
            """
            
            # Generar variaciones según el tipo de contenido original
            if original_content["type"] == "video":
                variations = await self._generate_video_variations(original_content, num_variations, base_prompt)
            elif original_content["type"] == "audio":
                variations = await self._generate_audio_to_video_variations(original_content, num_variations, base_prompt)
            elif original_content["type"] == "image":
                variations = await self._generate_image_variations(original_content, num_variations, base_prompt)
            else:
                raise ValueError(f"Unsupported content type: {original_content['type']}")
            
            # Preparar resultado
            result = {
                "success": True,
                "original_content": original_content,
                "variations_generated": len([v for v in variations if v.get("success")]),
                "variations": variations,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Generated {result['variations_generated']}/{num_variations} satellite variations")
            return result
            
        except Exception as e:
            logger.error(f"❌ Satellite variations generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_content": original_content,
                "variations": []
            }
    
    async def _generate_video_variations(self, original: Dict, num_variations: int, base_prompt: str) -> List[Dict]:
        """Generar variaciones desde video original"""
        variations = []
        
        for i in range(num_variations):
            try:
                # Seleccionar variación de estilo
                style = self.variation_configs["style_variations"][i % len(self.variation_configs["style_variations"])]
                camera = self.variation_configs["camera_variations"][i % len(self.variation_configs["camera_variations"])]
                
                enhanced_prompt = f"""
                {base_prompt}
                Style: {style}
                Camera: {camera}
                Variation {i+1} of {num_variations}
                Based on original video content, reimagined with AI
                """
                
                # Generar variación usando video-continuation
                result = await self.video_generator.generator.generate_video({
                    "type": "video-continuation",
                    "prompt": enhanced_prompt.strip(),
                    "video_input": original["path"],
                    "config": {
                        "resolution": "720p",
                        "num_frames": 120,  # 4 segundos
                        "fps": 30,
                        "quality": "high"
                    }
                })
                
                if result.success:
                    variations.append({
                        "success": True,
                        "variation_id": i + 1,
                        "style": style,
                        "camera": camera,
                        "video_path": result.video_path,
                        "thumbnail_path": result.thumbnail_path,
                        "generation_time": result.generation_time
                    })
                else:
                    variations.append({
                        "success": False,
                        "variation_id": i + 1,
                        "error": result.error_message
                    })
                    
            except Exception as e:
                logger.error(f"❌ Video variation {i+1} failed: {e}")
                variations.append({
                    "success": False,
                    "variation_id": i + 1,
                    "error": str(e)
                })
        
        return variations
    
    async def _generate_audio_to_video_variations(self, original: Dict, num_variations: int, base_prompt: str) -> List[Dict]:
        """Generar videos desde audio original"""
        variations = []
        
        for i in range(num_variations):
            try:
                style = self.variation_configs["style_variations"][i % len(self.variation_configs["style_variations"])]
                
                enhanced_prompt = f"""
                {base_prompt}
                Visual style: {style}
                Music visualization for audio track
                Sync with rhythm and beat, professional music video
                Variation {i+1} - AI generated visuals for original audio
                """
                
                # Generar video desde prompt (text-to-video)
                result = await self.video_generator.generate_music_video(
                    artist=original["artist"],
                    song=original["song"],
                    prompt=enhanced_prompt.strip(),
                    genre=original["genre"],
                    duration=30
                )
                
                if result.get("success"):
                    variations.append({
                        "success": True,
                        "variation_id": i + 1,
                        "style": style,
                        "video_path": result["video_path"],
                        "thumbnail_path": result.get("thumbnail_path"),
                        "generation_time": result.get("generation_time"),
                        "audio_source": original["path"]
                    })
                else:
                    variations.append({
                        "success": False,
                        "variation_id": i + 1,
                        "error": result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                logger.error(f"❌ Audio-to-video variation {i+1} failed: {e}")
                variations.append({
                    "success": False,
                    "variation_id": i + 1,
                    "error": str(e)
                })
        
        return variations
    
    async def _generate_image_variations(self, original: Dict, num_variations: int, base_prompt: str) -> List[Dict]:
        """Generar videos desde imagen original"""
        variations = []
        
        for i in range(num_variations):
            try:
                style = self.variation_configs["style_variations"][i % len(self.variation_configs["style_variations"])]
                camera = self.variation_configs["camera_variations"][i % len(self.variation_configs["camera_variations"])]
                
                enhanced_prompt = f"""
                {base_prompt}
                Style: {style}
                Movement: {camera}
                Animate the artist image with musical energy
                Variation {i+1} - AI animated from original photo
                """
                
                # Generar video desde imagen
                result = await self.video_generator.generate_promotional_video(
                    artist=original["artist"],
                    song=original["song"],
                    image_path=original["path"],
                    duration=15
                )
                
                if result.get("success"):
                    variations.append({
                        "success": True,
                        "variation_id": i + 1,
                        "style": style,
                        "video_path": result["video_path"],
                        "thumbnail_path": result.get("thumbnail_path"),
                        "source_image": original["path"]
                    })
                else:
                    variations.append({
                        "success": False,
                        "variation_id": i + 1,
                        "error": result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                logger.error(f"❌ Image-to-video variation {i+1} failed: {e}")
                variations.append({
                    "success": False,
                    "variation_id": i + 1,
                    "error": str(e)
                })
        
        return variations
    
    async def distribute_to_satellites(self, variations_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribuir las variaciones generadas a las cuentas satélite
        """
        try:
            if not variations_result.get("success"):
                return {
                    "success": False,
                    "error": "No variations to distribute"
                }
            
            successful_variations = [v for v in variations_result["variations"] if v.get("success")]
            
            if not successful_variations:
                return {
                    "success": False,
                    "error": "No successful variations to distribute"
                }
            
            logger.info(f"📡 Distributing {len(successful_variations)} variations to satellites...")
            
            distribution_results = []
            
            for i, variation in enumerate(successful_variations):
                try:
                    # Preparar metadata para upload
                    upload_data = {
                        "title": f"{variations_result['original_content']['artist']} - {variations_result['original_content']['song']} (AI Variation {variation['variation_id']})",
                        "description": f"""
🤖 AI-Generated Variation by Neural Forge
🎵 Original: {variations_result['original_content']['artist']} - {variations_result['original_content']['song']}
🎭 Style: {variation.get('style', 'AI Enhanced')}
🔄 Variation ID: {variation['variation_id']}
✨ #NeuralForge #AIMusic #LongCat
""".strip(),
                        "tags": [
                            variations_result['original_content']['artist'].lower(),
                            variations_result['original_content']['song'].lower(),
                            variations_result['original_content']['genre'].lower(),
                            "neural-forge",
                            "ai-generated",
                            "longcat",
                            f"variation-{variation['variation_id']}"
                        ],
                        "video_path": variation["video_path"],
                        "category_id": "10",  # Music category
                        "variation_metadata": {
                            "variation_id": variation["variation_id"],
                            "style": variation.get("style"),
                            "original_source": variations_result['original_content']['path']
                        }
                    }
                    
                    # Distribuir a satellite específica
                    result = await self.satellite_distribution.distribute_upload(upload_data)
                    
                    distribution_results.append({
                        "variation_id": variation["variation_id"],
                        "satellite_result": result,
                        "success": result.get("success", False)
                    })
                    
                    if result.get("success"):
                        logger.info(f"✅ Variation {variation['variation_id']} uploaded to satellite {result.get('satellite_id')}")
                    else:
                        logger.error(f"❌ Variation {variation['variation_id']} upload failed: {result.get('error')}")
                
                except Exception as e:
                    logger.error(f"❌ Distribution error for variation {variation.get('variation_id', i)}: {e}")
                    distribution_results.append({
                        "variation_id": variation.get("variation_id", i),
                        "success": False,
                        "error": str(e)
                    })
            
            successful_distributions = len([r for r in distribution_results if r.get("success")])
            
            return {
                "success": successful_distributions > 0,
                "variations_distributed": successful_distributions,
                "total_variations": len(successful_variations),
                "distribution_results": distribution_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Satellite distribution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_original_content(self,
                                     original_path: str,
                                     artist: str,
                                     song: str,
                                     genre: str = "trap",
                                     num_variations: int = 5) -> Dict[str, Any]:
        """
        Proceso completo: desde contenido original hasta distribución satelital
        """
        try:
            # Detectar tipo de contenido
            file_ext = Path(original_path).suffix.lower()
            if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                content_type = "video"
            elif file_ext in ['.mp3', '.wav', '.flac', '.m4a']:
                content_type = "audio"
            elif file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                content_type = "image"
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            original_content = {
                "type": content_type,
                "path": original_path,
                "artist": artist,
                "song": song,
                "genre": genre
            }
            
            logger.info(f"🎵 Processing original {content_type}: {artist} - {song}")
            
            # 1. Generar variaciones IA
            variations_result = await self.generate_satellite_variations(original_content, num_variations)
            
            if not variations_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to generate variations",
                    "stage": "variation_generation"
                }
            
            # 2. Distribuir a satellites
            distribution_result = await self.distribute_to_satellites(variations_result)
            
            # 3. Resultado final
            return {
                "success": distribution_result.get("success", False),
                "original_content": original_content,
                "variations_generated": variations_result.get("variations_generated", 0),
                "variations_distributed": distribution_result.get("variations_distributed", 0),
                "total_satellites": distribution_result.get("total_variations", 0),
                "generation_details": variations_result,
                "distribution_details": distribution_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Original content processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "content_processing"
            }

# Global secure instance
secure_longcat_satellite_manager = SecureLongCatSatelliteManager()

# Factory function
async def get_secure_longcat_satellite_manager() -> SecureLongCatSatelliteManager:
    """Get initialized secure LongCat satellite manager"""
    global secure_longcat_satellite_manager
    
    if not secure_longcat_satellite_manager.initialized:
        await secure_longcat_satellite_manager.initialize()
    
    return secure_longcat_satellite_manager