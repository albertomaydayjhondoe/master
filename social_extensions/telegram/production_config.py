"""
Telegram Production Configuration
Production-ready configuration and settings for Telegram automation
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TelegramProductionConfig:
    """Production configuration for Telegram automation"""
    
    # Telegram API credentials
    api_id: str
    api_hash: str
    phone: str
    session_name: str = "telegram_production"
    
    # Rate limiting
    max_messages_per_minute: int = 20
    max_messages_per_hour: int = 300
    max_groups_to_join_per_day: int = 10
    delay_between_messages: int = 3  # seconds
    
    # Group management
    max_managed_groups: int = 100
    auto_leave_inactive_groups: bool = True
    inactive_threshold_days: int = 30
    
    # Content optimization
    enable_ml_optimization: bool = True
    auto_schedule_posts: bool = True
    optimize_posting_times: bool = True
    
    # Monitoring and alerts
    enable_monitoring: bool = True
    alert_webhook_url: Optional[str] = None
    health_check_interval: int = 300  # 5 minutes
    
    # Security
    enable_2fa: bool = True
    session_encryption: bool = True
    proxy_config: Optional[Dict[str, str]] = None
    
    # Storage
    data_storage_path: str = "data/telegram/"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    
    # Performance
    concurrent_operations: int = 5
    message_cache_size: int = 1000
    metrics_retention_days: int = 30
    
    @classmethod
    def from_env(cls) -> 'TelegramProductionConfig':
        """Create configuration from environment variables"""
        return cls(
            # Required credentials
            api_id=os.getenv('TELEGRAM_API_ID', ''),
            api_hash=os.getenv('TELEGRAM_API_HASH', ''),
            phone=os.getenv('TELEGRAM_PHONE', ''),
            
            # Optional session name
            session_name=os.getenv('TELEGRAM_SESSION_NAME', 'telegram_production'),
            
            # Rate limiting
            max_messages_per_minute=int(os.getenv('TELEGRAM_MAX_MSG_PER_MIN', '20')),
            max_messages_per_hour=int(os.getenv('TELEGRAM_MAX_MSG_PER_HOUR', '300')),
            max_groups_to_join_per_day=int(os.getenv('TELEGRAM_MAX_GROUPS_PER_DAY', '10')),
            delay_between_messages=int(os.getenv('TELEGRAM_MSG_DELAY', '3')),
            
            # Group management
            max_managed_groups=int(os.getenv('TELEGRAM_MAX_GROUPS', '100')),
            auto_leave_inactive_groups=os.getenv('TELEGRAM_AUTO_LEAVE_INACTIVE', 'true').lower() == 'true',
            inactive_threshold_days=int(os.getenv('TELEGRAM_INACTIVE_THRESHOLD_DAYS', '30')),
            
            # Features
            enable_ml_optimization=os.getenv('TELEGRAM_ENABLE_ML_OPT', 'true').lower() == 'true',
            auto_schedule_posts=os.getenv('TELEGRAM_AUTO_SCHEDULE', 'true').lower() == 'true',
            optimize_posting_times=os.getenv('TELEGRAM_OPTIMIZE_TIMES', 'true').lower() == 'true',
            
            # Monitoring
            enable_monitoring=os.getenv('TELEGRAM_ENABLE_MONITORING', 'true').lower() == 'true',
            alert_webhook_url=os.getenv('TELEGRAM_ALERT_WEBHOOK_URL'),
            health_check_interval=int(os.getenv('TELEGRAM_HEALTH_CHECK_INTERVAL', '300')),
            
            # Security
            enable_2fa=os.getenv('TELEGRAM_ENABLE_2FA', 'true').lower() == 'true',
            session_encryption=os.getenv('TELEGRAM_SESSION_ENCRYPTION', 'true').lower() == 'true',
            proxy_config=cls._parse_proxy_config(os.getenv('TELEGRAM_PROXY_CONFIG')),
            
            # Storage
            data_storage_path=os.getenv('TELEGRAM_DATA_PATH', 'data/telegram/'),
            backup_enabled=os.getenv('TELEGRAM_BACKUP_ENABLED', 'true').lower() == 'true',
            backup_interval_hours=int(os.getenv('TELEGRAM_BACKUP_INTERVAL', '24')),
            
            # Performance
            concurrent_operations=int(os.getenv('TELEGRAM_CONCURRENT_OPS', '5')),
            message_cache_size=int(os.getenv('TELEGRAM_CACHE_SIZE', '1000')),
            metrics_retention_days=int(os.getenv('TELEGRAM_METRICS_RETENTION', '30'))
        )
    
    @staticmethod
    def _parse_proxy_config(proxy_string: Optional[str]) -> Optional[Dict[str, str]]:
        """Parse proxy configuration string"""
        if not proxy_string:
            return None
            
        try:
            # Expected format: "type:host:port:username:password"
            parts = proxy_string.split(':')
            if len(parts) >= 3:
                config = {
                    'proxy_type': parts[0],  # socks4, socks5, http
                    'addr': parts[1],
                    'port': int(parts[2])
                }
                
                if len(parts) >= 5:
                    config.update({
                        'username': parts[3],
                        'password': parts[4]
                    })
                
                return config
        except Exception as e:
            logger.error(f"Failed to parse proxy config: {e}")
            
        return None
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        errors = []
        warnings = []
        
        # Required credentials
        if not self.api_id:
            errors.append("TELEGRAM_API_ID is required")
        
        if not self.api_hash:
            errors.append("TELEGRAM_API_HASH is required")
        
        if not self.phone:
            errors.append("TELEGRAM_PHONE is required")
        
        # Rate limiting validation
        if self.max_messages_per_minute > 30:
            warnings.append("Messages per minute > 30 may trigger rate limits")
        
        if self.max_messages_per_hour > 500:
            warnings.append("Messages per hour > 500 may trigger rate limits")
        
        # Storage path validation
        try:
            Path(self.data_storage_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create storage path: {e}")
        
        # Performance validation
        if self.concurrent_operations > 10:
            warnings.append("High concurrent operations may impact performance")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "api_id": self.api_id,
            "api_hash": self.api_hash[:8] + "***" if self.api_hash else "",  # Mask for security
            "phone": self.phone,
            "session_name": self.session_name,
            "max_messages_per_minute": self.max_messages_per_minute,
            "max_messages_per_hour": self.max_messages_per_hour,
            "max_groups_to_join_per_day": self.max_groups_to_join_per_day,
            "delay_between_messages": self.delay_between_messages,
            "max_managed_groups": self.max_managed_groups,
            "auto_leave_inactive_groups": self.auto_leave_inactive_groups,
            "inactive_threshold_days": self.inactive_threshold_days,
            "enable_ml_optimization": self.enable_ml_optimization,
            "auto_schedule_posts": self.auto_schedule_posts,
            "optimize_posting_times": self.optimize_posting_times,
            "enable_monitoring": self.enable_monitoring,
            "alert_webhook_url": bool(self.alert_webhook_url),
            "health_check_interval": self.health_check_interval,
            "enable_2fa": self.enable_2fa,
            "session_encryption": self.session_encryption,
            "proxy_enabled": bool(self.proxy_config),
            "data_storage_path": self.data_storage_path,
            "backup_enabled": self.backup_enabled,
            "backup_interval_hours": self.backup_interval_hours,
            "concurrent_operations": self.concurrent_operations,
            "message_cache_size": self.message_cache_size,
            "metrics_retention_days": self.metrics_retention_days
        }
    
    def get_telethon_config(self) -> Dict[str, Any]:
        """Get configuration for Telethon client"""
        config = {
            'api_id': int(self.api_id),
            'api_hash': self.api_hash,
            'session': self.session_name,
            'timeout': 30,
            'retry_delay': 1,
            'auto_reconnect': True,
            'connection_retries': 5
        }
        
        # Add proxy if configured
        if self.proxy_config:
            import socks
            
            proxy_type_map = {
                'socks4': socks.SOCKS4,
                'socks5': socks.SOCKS5,
                'http': socks.HTTP
            }
            
            proxy_type = proxy_type_map.get(self.proxy_config['proxy_type'], socks.SOCKS5)
            
            config['proxy'] = (
                proxy_type,
                self.proxy_config['addr'],
                self.proxy_config['port'],
                True,  # rdns
                self.proxy_config.get('username'),
                self.proxy_config.get('password')
            )
        
        return config

class TelegramEnvironmentValidator:
    """Validator for Telegram environment setup"""
    
    @staticmethod
    def check_dependencies() -> Dict[str, Any]:
        """Check if required dependencies are installed"""
        dependencies = {}
        
        # Check Telethon
        try:
            import telethon
            dependencies['telethon'] = {
                'available': True,
                'version': telethon.__version__
            }
        except ImportError:
            dependencies['telethon'] = {
                'available': False,
                'install_command': 'pip install telethon'
            }
        
        # Check cryptography
        try:
            import cryptography
            dependencies['cryptography'] = {
                'available': True,
                'version': cryptography.__version__
            }
        except ImportError:
            dependencies['cryptography'] = {
                'available': False,
                'install_command': 'pip install cryptography'
            }
        
        # Check async support
        try:
            import asyncio
            dependencies['asyncio'] = {'available': True}
        except ImportError:
            dependencies['asyncio'] = {
                'available': False,
                'note': 'Python 3.7+ required'
            }
        
        all_available = all(dep.get('available', False) for dep in dependencies.values())
        
        return {
            'all_dependencies_available': all_available,
            'dependencies': dependencies
        }
    
    @staticmethod
    def check_telegram_api_setup() -> Dict[str, Any]:
        """Check if Telegram API is properly set up"""
        config = TelegramProductionConfig.from_env()
        validation = config.validate()
        
        recommendations = []
        
        if not config.api_id or not config.api_hash:
            recommendations.append({
                'type': 'setup',
                'message': 'Get API credentials from https://my.telegram.org/auth',
                'priority': 'high'
            })
        
        if not config.enable_2fa:
            recommendations.append({
                'type': 'security',
                'message': 'Enable 2FA for better account security',
                'priority': 'medium'
            })
        
        if not config.proxy_config and config.max_messages_per_hour > 200:
            recommendations.append({
                'type': 'performance',
                'message': 'Consider using proxy for high-volume messaging',
                'priority': 'low'
            })
        
        return {
            'api_configured': bool(config.api_id and config.api_hash),
            'validation': validation,
            'recommendations': recommendations,
            'config_summary': config.to_dict()
        }

class TelegramProductionSetup:
    """Helper class for production setup"""
    
    @staticmethod
    def generate_env_template() -> str:
        """Generate .env template for Telegram configuration"""
        return """
# Telegram Production Configuration
# Get these credentials from https://my.telegram.org/auth

# Required: Telegram API Credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890
TELEGRAM_SESSION_NAME=telegram_production

# Rate Limiting (adjust based on your needs)
TELEGRAM_MAX_MSG_PER_MIN=20
TELEGRAM_MAX_MSG_PER_HOUR=300
TELEGRAM_MAX_GROUPS_PER_DAY=10
TELEGRAM_MSG_DELAY=3

# Group Management
TELEGRAM_MAX_GROUPS=100
TELEGRAM_AUTO_LEAVE_INACTIVE=true
TELEGRAM_INACTIVE_THRESHOLD_DAYS=30

# Features
TELEGRAM_ENABLE_ML_OPT=true
TELEGRAM_AUTO_SCHEDULE=true
TELEGRAM_OPTIMIZE_TIMES=true

# Monitoring
TELEGRAM_ENABLE_MONITORING=true
TELEGRAM_ALERT_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
TELEGRAM_HEALTH_CHECK_INTERVAL=300

# Security
TELEGRAM_ENABLE_2FA=true
TELEGRAM_SESSION_ENCRYPTION=true
TELEGRAM_PROXY_CONFIG=socks5:proxy.example.com:1080:username:password

# Storage
TELEGRAM_DATA_PATH=data/telegram/
TELEGRAM_BACKUP_ENABLED=true
TELEGRAM_BACKUP_INTERVAL=24

# Performance
TELEGRAM_CONCURRENT_OPS=5
TELEGRAM_CACHE_SIZE=1000
TELEGRAM_METRICS_RETENTION=30
"""
    
    @staticmethod
    def create_production_directories(config: TelegramProductionConfig):
        """Create necessary directories for production"""
        directories = [
            config.data_storage_path,
            f"{config.data_storage_path}/sessions",
            f"{config.data_storage_path}/backups",
            f"{config.data_storage_path}/logs",
            f"{config.data_storage_path}/metrics"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    @staticmethod
    def setup_logging(config: TelegramProductionConfig):
        """Set up production logging"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # File handler
        log_file = Path(config.data_storage_path) / "logs" / "telegram.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure logger
        telegram_logger = logging.getLogger('telegram')
        telegram_logger.addHandler(file_handler)
        telegram_logger.addHandler(console_handler)
        telegram_logger.setLevel(logging.INFO)
        
        logger.info(f"Telegram logging configured: {log_file}")

def get_production_config() -> TelegramProductionConfig:
    """Get production configuration instance"""
    return TelegramProductionConfig.from_env()

def validate_production_setup() -> Dict[str, Any]:
    """Validate complete production setup"""
    # Check dependencies
    deps_check = TelegramEnvironmentValidator.check_dependencies()
    
    # Check API setup
    api_check = TelegramEnvironmentValidator.check_telegram_api_setup()
    
    # Overall status
    ready_for_production = (
        deps_check['all_dependencies_available'] and
        api_check['api_configured'] and
        api_check['validation']['valid']
    )
    
    return {
        'ready_for_production': ready_for_production,
        'dependencies': deps_check,
        'api_setup': api_check,
        'next_steps': _get_next_steps(deps_check, api_check)
    }

def _get_next_steps(deps_check: Dict, api_check: Dict) -> List[str]:
    """Get next steps for production setup"""
    steps = []
    
    if not deps_check['all_dependencies_available']:
        steps.append("Install missing dependencies")
    
    if not api_check['api_configured']:
        steps.append("Configure Telegram API credentials")
    
    if api_check['validation']['errors']:
        steps.append("Fix configuration errors")
    
    if not steps:
        steps.append("Run production deployment")
    
    return steps

# Export main classes and functions
__all__ = [
    'TelegramProductionConfig',
    'TelegramEnvironmentValidator', 
    'TelegramProductionSetup',
    'get_production_config',
    'validate_production_setup'
]