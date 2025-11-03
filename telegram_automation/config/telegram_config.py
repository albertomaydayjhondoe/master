"""
Telegram Configuration Module
Central configuration management for the Telegram automation system.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

class TelegramConfig:
    """Main configuration class for the Telegram automation system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration with default values."""
        
        # Bot configuration
        self.bot_token = os.getenv("BOT_TOKEN", "")
        self.phone_number = os.getenv("PHONE_NUMBER", "")
        self.api_id = int(os.getenv("API_ID", "0"))
        self.api_hash = os.getenv("API_HASH", "")
        self.session_name = "telegram_automation"
        
        # System settings  
        self.max_concurrent_tasks = 5
        self.enable_comments = True
        self.enable_dummy_mode = True
        self.main_loop_interval = 30
        self.min_viral_priority = 0.7
        
        # Database settings
        self.database_url = "sqlite:///telegram_automation.db"
        
        # Security
        self.account_encryption_key = "default_encryption_key_change_in_production"
        
        # ML and Priority Engine
        self.ml_models_path = "/tmp/priority_models"
        
        # Rate limiting settings
        self.youtube_requests_per_hour = 100
        self.instagram_requests_per_hour = 200
        self.tiktok_requests_per_hour = 150
        
        # Monitoring and alerts
        self.alert_webhook_url = None
        self.log_level = "INFO"
        
        # Initialize module configs
        self.telegram_config = self._get_telegram_config()
        self.platform_configs = self._get_platform_configs()
        self.ml_config = self._get_ml_config()
        self.listener_config = self._get_listener_config()
        self.executor_config = self._get_executor_config()
        self.priority_config = self._get_priority_config()
        self.metrics_config = self._get_metrics_config()
        self.message_config = self._get_message_config()
        self.account_config = self._get_account_config()
    
    def _get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram-specific configuration."""
        return {
            'api_id': self.api_id,
            'api_hash': self.api_hash,
            'bot_token': self.bot_token,
            'session_name': self.session_name,
            'dummy_mode': self.enable_dummy_mode
        }
    
    def _get_platform_configs(self) -> Dict[str, Any]:
        """Get platform-specific configurations."""
        return {
            'youtube': {
                'api_key': os.getenv('YOUTUBE_API_KEY', ''),
                'dummy_mode': self.enable_dummy_mode,
                'requests_per_hour': self.youtube_requests_per_hour
            },
            'instagram': {
                'username': os.getenv('INSTAGRAM_USERNAME', ''),
                'password': os.getenv('INSTAGRAM_PASSWORD', ''),
                'dummy_mode': self.enable_dummy_mode,
                'requests_per_hour': self.instagram_requests_per_hour
            },
            'tiktok': {
                'client_key': os.getenv('TIKTOK_CLIENT_KEY', ''),
                'client_secret': os.getenv('TIKTOK_CLIENT_SECRET', ''),
                'dummy_mode': self.enable_dummy_mode,
                'requests_per_hour': self.tiktok_requests_per_hour
            }
        }
    
    def _get_ml_config(self) -> Dict[str, Any]:
        """Get ML/AI configuration."""
        return {
            'models_path': self.ml_models_path,
            'viral_threshold': 0.7,
            'priority_factors': {
                'engagement_rate': 0.3,
                'follower_count': 0.2,
                'content_freshness': 0.2,
                'user_activity': 0.15,
                'platform_performance': 0.15
            }
        }
    
    def _get_listener_config(self) -> Dict[str, Any]:
        """Get listener module configuration."""
        return {
            'groups_to_monitor': os.getenv('TELEGRAM_GROUPS', '').split(','),
            'viral_threshold': 0.7,
            'check_interval': 60,
            'dummy_mode': self.enable_dummy_mode
        }
    
    def _get_executor_config(self) -> Dict[str, Any]:
        """Get executor module configuration."""
        return {
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'retry_attempts': 3,
            'retry_delay': 30,
            'platforms': self.platform_configs
        }
    
    def _get_priority_config(self) -> Dict[str, Any]:
        """Get priority engine configuration."""
        return {
            'ml_models_path': self.ml_models_path,
            'priority_factors': self._get_ml_config()['priority_factors'],
            'learning_rate': 0.01,
            'update_frequency': 3600
        }
    
    def _get_metrics_config(self) -> Dict[str, Any]:
        """Get metrics collector configuration."""
        return {
            'database_url': self.database_url,
            'collection_interval': 300,
            'retention_days': 90,
            'alert_webhook': self.alert_webhook_url
        }
    
    def _get_message_config(self) -> Dict[str, Any]:
        """Get message generator configuration."""
        return {
            'templates_path': 'templates/',
            'personalization_enabled': True,
            'ab_testing_enabled': True,
            'language': 'en'
        }
    
    def _get_account_config(self) -> Dict[str, Any]:
        """Get account manager configuration."""
        return {
            'platforms': self.platform_configs,
            'health_check_interval': 1800,
            'rotation_threshold': 0.3,
            'encryption_key': self.account_encryption_key
        }
    
    # Viral detection thresholds
    viral_detection_thresholds: Dict[str, int] = field(default_factory=lambda: {
        'min_views': 1000,
        'min_forwards': 50,
        'min_replies': 20
    })
    
    # Keywords for engagement detection
    engagement_keywords: List[str] = field(default_factory=lambda: [
        'like4like', 'sub4sub', 'follow4follow', 'intercambio',
        'engagement', 'apoyo mutuo', 'youtube', 'instagram', 'tiktok'
    ])
    
    # Viral content keywords
    viral_keywords: List[str] = field(default_factory=lambda: [
        'viral', 'trending', 'fyp', 'foryou', 'explore', 'viral',
        'challenge', 'trend', 'breaking', 'exclusive'
    ])
    
    # Trending hashtags (would be updated dynamically)
    trending_hashtags: List[str] = field(default_factory=lambda: [
        'viral', 'trending', 'fyp', 'foryou', 'explore',
        'tiktok', 'instagram', 'youtube', 'shorts', 'reels'
    ])
    
    # Group monitoring
    min_group_size: int = 100
    
    @classmethod
    def from_env(cls) -> 'TelegramConfig':
        """Create configuration from environment variables."""
        
        return cls(
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            phone_number=os.getenv('TELEGRAM_PHONE_NUMBER', ''),
            api_id=int(os.getenv('TELEGRAM_API_ID', '0')),
            api_hash=os.getenv('TELEGRAM_API_HASH', ''),
            session_name=os.getenv('TELEGRAM_SESSION_NAME', 'telegram_automation'),
            
            max_concurrent_tasks=int(os.getenv('MAX_CONCURRENT_TASKS', '5')),
            enable_comments=os.getenv('ENABLE_COMMENTS', 'true').lower() == 'true',
            enable_dummy_mode=os.getenv('DUMMY_MODE', 'true').lower() == 'true',
            
            database_url=os.getenv('DATABASE_URL', 'sqlite:///telegram_automation.db'),
            
            account_encryption_key=os.getenv('ACCOUNT_ENCRYPTION_KEY', 'default_encryption_key_change_in_production'),
            
            ml_models_path=os.getenv('ML_MODELS_PATH', '/tmp/priority_models'),
            
            youtube_requests_per_hour=int(os.getenv('YOUTUBE_REQUESTS_PER_HOUR', '100')),
            instagram_requests_per_hour=int(os.getenv('INSTAGRAM_REQUESTS_PER_HOUR', '200')),
            tiktok_requests_per_hour=int(os.getenv('TIKTOK_REQUESTS_PER_HOUR', '150')),
            
            alert_webhook_url=os.getenv('ALERT_WEBHOOK_URL'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            
            # Platform configs would be loaded from separate env vars or files
            youtube_config=cls._load_youtube_config(),
            instagram_config=cls._load_instagram_config(),
            tiktok_config=cls._load_tiktok_config()
        )
    
    @staticmethod
    def _load_youtube_config() -> Dict[str, Any]:
        """Load YouTube-specific configuration."""
        return {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID', ''),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET', ''),
            'redirect_uri': os.getenv('YOUTUBE_REDIRECT_URI', 'http://localhost:8080/callback'),
            'scopes': ['https://www.googleapis.com/auth/youtube.force-ssl']
        }
    
    @staticmethod
    def _load_instagram_config() -> Dict[str, Any]:
        """Load Instagram-specific configuration."""
        return {
            'app_id': os.getenv('INSTAGRAM_APP_ID', ''),
            'app_secret': os.getenv('INSTAGRAM_APP_SECRET', ''),
            'redirect_uri': os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:8080/callback'),
            'scopes': ['user_profile', 'user_media']
        }
    
    @staticmethod
    def _load_tiktok_config() -> Dict[str, Any]:
        """Load TikTok-specific configuration."""
        return {
            'client_key': os.getenv('TIKTOK_CLIENT_KEY', ''),
            'client_secret': os.getenv('TIKTOK_CLIENT_SECRET', ''),
            'redirect_uri': os.getenv('TIKTOK_REDIRECT_URI', 'http://localhost:8080/callback'),
            'scopes': ['user.info.basic', 'video.list']
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.bot_token:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if not self.enable_dummy_mode:
            if not self.api_id or not self.api_hash:
                errors.append("TELEGRAM_API_ID and TELEGRAM_API_HASH are required for production mode")
            
            if not self.phone_number:
                errors.append("TELEGRAM_PHONE_NUMBER is required for production mode")
        
        if self.max_concurrent_tasks <= 0:
            errors.append("MAX_CONCURRENT_TASKS must be positive")
        
        # Validate platform configs if not in dummy mode
        if not self.enable_dummy_mode:
            if not self.youtube_config.get('client_id'):
                errors.append("YouTube client_id is required for production mode")
            
            if not self.instagram_config.get('app_id'):
                errors.append("Instagram app_id is required for production mode")
            
            if not self.tiktok_config.get('client_key'):
                errors.append("TikTok client_key is required for production mode")
        
        return errors
    
    def get_platform_config(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific platform."""
        platform_configs = {
            'youtube': self.youtube_config,
            'instagram': self.instagram_config,
            'tiktok': self.tiktok_config
        }
        
        return platform_configs.get(platform.lower())
    
    def get_rate_limit(self, platform: str) -> int:
        """Get rate limit for a specific platform."""
        rate_limits = {
            'youtube': self.youtube_requests_per_hour,
            'instagram': self.instagram_requests_per_hour,
            'tiktok': self.tiktok_requests_per_hour
        }
        
        return rate_limits.get(platform.lower(), 100)  # Default to 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'bot_token': '***' if self.bot_token else '',  # Mask sensitive data
            'phone_number': '***' if self.phone_number else '',
            'api_id': self.api_id,
            'api_hash': '***' if self.api_hash else '',
            'session_name': self.session_name,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'enable_comments': self.enable_comments,
            'enable_dummy_mode': self.enable_dummy_mode,
            'database_url': self.database_url,
            'ml_models_path': self.ml_models_path,
            'rate_limits': {
                'youtube': self.youtube_requests_per_hour,
                'instagram': self.instagram_requests_per_hour,
                'tiktok': self.tiktok_requests_per_hour
            },
            'viral_detection_thresholds': self.viral_detection_thresholds,
            'engagement_keywords': self.engagement_keywords,
            'viral_keywords': self.viral_keywords,
            'trending_hashtags': self.trending_hashtags,
            'min_group_size': self.min_group_size
        }


def load_config() -> TelegramConfig:
    """Load configuration from environment variables."""
    
    config = TelegramConfig.from_env()
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        
        if not config.enable_dummy_mode:
            print("\nStarting in DUMMY_MODE due to configuration errors...")
            config.enable_dummy_mode = True
    
    return config


def create_default_env_file(file_path: str = ".env.tele"):
    """Create a default environment file with all configuration options."""
    
    env_content = """# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_PHONE_NUMBER=+1234567890
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_SESSION_NAME=telegram_automation

# System Settings
MAX_CONCURRENT_TASKS=5
ENABLE_COMMENTS=true
DUMMY_MODE=true

# Database
DATABASE_URL=sqlite:///telegram_automation.db

# Security
ACCOUNT_ENCRYPTION_KEY=change_this_in_production

# ML and Models
ML_MODELS_PATH=/tmp/priority_models

# Rate Limiting
YOUTUBE_REQUESTS_PER_HOUR=100
INSTAGRAM_REQUESTS_PER_HOUR=200
TIKTOK_REQUESTS_PER_HOUR=150

# Monitoring
LOG_LEVEL=INFO
# ALERT_WEBHOOK_URL=https://your-webhook-url.com

# YouTube API Configuration
# YOUTUBE_CLIENT_ID=your_youtube_client_id
# YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
# YOUTUBE_REDIRECT_URI=http://localhost:8080/callback

# Instagram API Configuration
# INSTAGRAM_APP_ID=your_instagram_app_id
# INSTAGRAM_APP_SECRET=your_instagram_app_secret
# INSTAGRAM_REDIRECT_URI=http://localhost:8080/callback

# TikTok API Configuration
# TIKTOK_CLIENT_KEY=your_tiktok_client_key
# TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
# TIKTOK_REDIRECT_URI=http://localhost:8080/callback
"""
    
    with open(file_path, 'w') as f:
        f.write(env_content)
    
    print(f"Default environment file created at: {file_path}")
    print("Please edit the file with your actual configuration values.")


if __name__ == "__main__":
    # Create default .env file if it doesn't exist
    env_file = ".env.tele"
    if not os.path.exists(env_file):
        create_default_env_file(env_file)