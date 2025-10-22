"""
Configuration for YouTube Executor
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class GoLoginConfig:
    """GoLogin API configuration"""
    api_token: str
    base_url: str = "https://api.gologin.com"
    max_concurrent_profiles: int = 3
    profile_rotation_interval_hours: int = 2
    profile_cooldown_minutes: int = 30


@dataclass 
class YouTubeExecutorConfig:
    """YouTube Executor configuration"""
    # Timing settings (in seconds)
    min_watch_time: int = 30
    max_watch_time: int = 300
    action_delay_min: float = 1.0
    action_delay_max: float = 5.0
    
    # Rate limiting
    max_actions_per_profile_per_day: int = 50
    max_actions_per_hour: int = 10
    execution_queue_max_size: int = 100
    
    # Retry settings
    max_retries: int = 3
    retry_delay_minutes: int = 15
    
    # Browser settings
    page_load_timeout: int = 30
    implicit_wait: int = 10
    screenshot_on_error: bool = True
    
    # Comment generation
    enable_comments: bool = True
    comment_language: str = "en"
    min_comment_length: int = 5
    max_comment_length: int = 50


@dataclass
class SecurityConfig:
    """Security and stealth configuration"""
    # Human behavior simulation
    enable_human_delays: bool = True
    mouse_movement_probability: float = 0.1
    scroll_probability: float = 0.15
    
    # Error handling
    close_popups: bool = True
    handle_captcha: bool = False  # Manual for now
    skip_ads: bool = True
    
    # Profile management
    profile_health_check_interval: int = 3600  # 1 hour
    auto_rotate_profiles: bool = True
    ban_detection_enabled: bool = True


def load_config() -> Dict:
    """Load configuration from environment variables"""
    return {
        'gologin': GoLoginConfig(
            api_token=os.getenv('GOLOGIN_API_TOKEN', 'dummy_token'),
            max_concurrent_profiles=int(os.getenv('GOLOGIN_MAX_PROFILES', '3')),
            profile_rotation_interval_hours=int(os.getenv('GOLOGIN_ROTATION_HOURS', '2')),
            profile_cooldown_minutes=int(os.getenv('GOLOGIN_COOLDOWN_MINUTES', '30'))
        ),
        
        'youtube': YouTubeExecutorConfig(
            min_watch_time=int(os.getenv('YOUTUBE_MIN_WATCH_TIME', '30')),
            max_watch_time=int(os.getenv('YOUTUBE_MAX_WATCH_TIME', '300')),
            action_delay_min=float(os.getenv('YOUTUBE_ACTION_DELAY_MIN', '1.0')),
            action_delay_max=float(os.getenv('YOUTUBE_ACTION_DELAY_MAX', '5.0')),
            max_actions_per_profile_per_day=int(os.getenv('YOUTUBE_MAX_ACTIONS_PER_DAY', '50')),
            max_actions_per_hour=int(os.getenv('YOUTUBE_MAX_ACTIONS_PER_HOUR', '10')),
            max_retries=int(os.getenv('YOUTUBE_MAX_RETRIES', '3')),
            enable_comments=os.getenv('YOUTUBE_ENABLE_COMMENTS', 'true').lower() == 'true',
            comment_language=os.getenv('YOUTUBE_COMMENT_LANGUAGE', 'en')
        ),
        
        'security': SecurityConfig(
            enable_human_delays=os.getenv('SECURITY_HUMAN_DELAYS', 'true').lower() == 'true',
            mouse_movement_probability=float(os.getenv('SECURITY_MOUSE_PROBABILITY', '0.1')),
            scroll_probability=float(os.getenv('SECURITY_SCROLL_PROBABILITY', '0.15')),
            auto_rotate_profiles=os.getenv('SECURITY_AUTO_ROTATE', 'true').lower() == 'true',
            ban_detection_enabled=os.getenv('SECURITY_BAN_DETECTION', 'true').lower() == 'true'
        )
    }


# Default configuration
DEFAULT_CONFIG = load_config()