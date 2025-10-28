"""
Production Configuration - TikTok ML System v4
Core integrations: Supabase + Meta Ads + YouTube/Spotify + Ultralytics
"""
import os
from typing import Optional, Dict, Any, List
from pathlib import Path


class ProductionConfig:
    """Production configuration manager"""
    
    # Core system settings
    PRODUCTION_MODE: bool = True
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1
    
    # Security
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Meta Ads Configuration
    META_APP_ID: str = os.getenv("META_APP_ID", "")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    META_PIXEL_ID: str = os.getenv("META_PIXEL_ID", "")
    
    # YouTube Data API
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_CHANNEL_IDS: List[str] = os.getenv("YOUTUBE_CHANNEL_IDS", "").split(",") if os.getenv("YOUTUBE_CHANNEL_IDS") else []
    
    # Spotify API
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    SPOTIFY_ARTIST_IDS: List[str] = os.getenv("SPOTIFY_ARTIST_IDS", "").split(",") if os.getenv("SPOTIFY_ARTIST_IDS") else []
    SPOTIFY_PLAYLIST_IDS: List[str] = os.getenv("SPOTIFY_PLAYLIST_IDS", "").split(",") if os.getenv("SPOTIFY_PLAYLIST_IDS") else []
    
    # ML Configuration
    ULTRALYTICS_MODEL: str = os.getenv("ULTRALYTICS_MODEL", "yolov8n.pt")
    ML_MODEL_PATH: str = "/app/data/models"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # n8n Configuration
    N8N_WEBHOOK_BASE_URL: str = os.getenv("N8N_WEBHOOK_BASE_URL", "")
    N8N_API_KEY: str = os.getenv("N8N_API_KEY", "")
    
    # Landing Page Configuration
    LANDING_PAGE_URLS: List[str] = os.getenv("LANDING_PAGE_URLS", "").split(",") if os.getenv("LANDING_PAGE_URLS") else []
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Redis (for caching and queues)
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate required configuration"""
        errors = []
        warnings = []
        
        # Required for Supabase
        if not cls.SUPABASE_URL:
            errors.append("SUPABASE_URL is required")
        if not cls.SUPABASE_ANON_KEY:
            errors.append("SUPABASE_ANON_KEY is required")
        
        # Required for Meta Ads
        if not cls.META_APP_ID:
            warnings.append("META_APP_ID not configured - Meta Ads disabled")
        if not cls.META_ACCESS_TOKEN:
            warnings.append("META_ACCESS_TOKEN not configured - Meta Ads disabled")
        
        # Required for security
        if not cls.API_SECRET_KEY:
            errors.append("API_SECRET_KEY is required for production")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @classmethod
    def get_supabase_config(cls) -> Dict[str, str]:
        """Get Supabase configuration"""
        return {
            "url": cls.SUPABASE_URL,
            "anon_key": cls.SUPABASE_ANON_KEY,
            "service_key": cls.SUPABASE_SERVICE_KEY
        }
    
    @classmethod
    def get_meta_config(cls) -> Dict[str, str]:
        """Get Meta Ads configuration"""
        return {
            "app_id": cls.META_APP_ID,
            "app_secret": cls.META_APP_SECRET,
            "access_token": cls.META_ACCESS_TOKEN,
            "pixel_id": cls.META_PIXEL_ID
        }
    
    @classmethod
    def get_social_apis_config(cls) -> Dict[str, Dict[str, str]]:
        """Get YouTube and Spotify API configuration"""
        return {
            "youtube": {
                "api_key": cls.YOUTUBE_API_KEY,
                "channel_id": cls.YOUTUBE_CHANNEL_ID
            },
            "spotify": {
                "client_id": cls.SPOTIFY_CLIENT_ID,
                "client_secret": cls.SPOTIFY_CLIENT_SECRET
            }
        }


# Global configuration instance
config = ProductionConfig()


def get_config() -> ProductionConfig:
    """Get configuration instance"""
    return config


def validate_production_config() -> bool:
    """Validate production configuration on startup"""
    validation = ProductionConfig.validate_config()
    
    if not validation["valid"]:
        print("❌ Configuration validation failed:")
        for error in validation["errors"]:
            print(f"  - {error}")
        return False
    
    if validation["warnings"]:
        print("⚠️  Configuration warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
    
    print("✅ Production configuration validated successfully")
    return True


# Environment-specific settings
if __name__ == "__main__":
    # Test configuration
    validation = ProductionConfig.validate_config()
    print("Configuration validation:", validation)