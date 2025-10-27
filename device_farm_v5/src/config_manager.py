"""
Device Farm v5 - Configuration Management
Handles loading and validation of system configuration
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from decouple import config
from loguru import logger


@dataclass
class GologinConfig:
    """Gologin API configuration"""
    api_url: str
    token: str
    cache_duration: int
    max_retries: int
    timeout: int


@dataclass  
class ADBConfig:
    """ADB configuration"""
    adb_path: str
    connection_timeout: int
    command_timeout: int
    max_retries: int


@dataclass
class AppiumConfig:
    """Appium configuration"""
    base_port: int
    port_range: int
    server_timeout: int
    session_timeout: int


@dataclass
class TaskQueueConfig:
    """Task queue configuration"""
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: Optional[str]
    max_retries: int
    task_timeout: int


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    host: str
    port: int
    debug: bool
    secret_key: str


@dataclass
class DeviceFarmConfig:
    """Main configuration container"""
    gologin: GologinConfig
    adb: ADBConfig
    appium: AppiumConfig
    task_queue: TaskQueueConfig
    dashboard: DashboardConfig
    database_url: str
    max_devices: int
    log_level: str
    
    # Raw config for advanced features
    raw_config: Dict[str, Any]


class ConfigManager:
    """Configuration manager for Device Farm v5"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config: Optional[DeviceFarmConfig] = None
        
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        current_dir = Path(__file__).parent
        return str(current_dir / "config.yaml")
    
    def load_config(self) -> DeviceFarmConfig:
        """Load configuration from YAML file and environment variables"""
        try:
            # Load YAML configuration
            with open(self.config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
            
            # Load environment variables
            env_config = self._load_env_config()
            
            # Merge configurations
            merged_config = self._merge_configs(yaml_config, env_config)
            
            # Create configuration objects
            self.config = self._create_config_objects(merged_config)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            'gologin_token': config('GOLOGIN_API_TOKEN', default=''),
            'redis_password': config('REDIS_PASSWORD', default=None),
            'dashboard_secret_key': config('DASHBOARD_SECRET_KEY', default='dev-secret-key'),
            'dashboard_username': config('DASHBOARD_USERNAME', default='admin'),
            'dashboard_password': config('DASHBOARD_PASSWORD', default='admin'),
            'api_secret_key': config('API_SECRET_KEY', default='dev-api-key'),
            'jwt_secret_key': config('JWT_SECRET_KEY', default='dev-jwt-key'),
            'alert_webhook_url': config('ALERT_WEBHOOK_URL', default=''),
            'telegram_bot_token': config('TELEGRAM_BOT_TOKEN', default=''),
            'telegram_chat_id': config('TELEGRAM_CHAT_ID', default=''),
            'encryption_key': config('ENCRYPTION_KEY', default=''),
            'environment': config('ENVIRONMENT', default='development'),
            'debug': config('DEBUG', default='false').lower() == 'true',
            'log_level': config('LOG_LEVEL', default='INFO'),
        }
    
    def _merge_configs(self, yaml_config: Dict, env_config: Dict) -> Dict:
        """Merge YAML and environment configurations"""
        # Environment variables override YAML values
        if env_config['gologin_token']:
            yaml_config['gologin']['token'] = env_config['gologin_token']
            
        if env_config['redis_password']:
            yaml_config['task_queue']['redis']['password'] = env_config['redis_password']
            
        yaml_config['dashboard']['secret_key'] = env_config['dashboard_secret_key']
        yaml_config['dashboard']['debug'] = env_config['debug']
        
        # Override log level
        yaml_config['system']['log_level'] = env_config['log_level']
        
        return yaml_config
    
    def _create_config_objects(self, config_dict: Dict) -> DeviceFarmConfig:
        """Create typed configuration objects from dictionary"""
        
        # Gologin configuration
        gologin_cfg = GologinConfig(
            api_url=config_dict['gologin']['api_url'],
            token=config_dict['gologin']['token'],
            cache_duration=config_dict['gologin']['cache_duration'],
            max_retries=config_dict['gologin']['max_retries'],
            timeout=config_dict['gologin']['timeout']
        )
        
        # ADB configuration
        adb_cfg = ADBConfig(
            adb_path=config_dict['adb']['adb_path'],
            connection_timeout=config_dict['adb']['connection_timeout'],
            command_timeout=config_dict['adb']['command_timeout'],
            max_retries=config_dict['adb']['max_retries']
        )
        
        # Appium configuration
        appium_cfg = AppiumConfig(
            base_port=config_dict['appium']['base_port'],
            port_range=config_dict['appium']['port_range'],
            server_timeout=config_dict['appium']['server_timeout'],
            session_timeout=config_dict['appium']['session_timeout']
        )
        
        # Task queue configuration
        task_queue_cfg = TaskQueueConfig(
            redis_host=config_dict['task_queue']['redis']['host'],
            redis_port=config_dict['task_queue']['redis']['port'],
            redis_db=config_dict['task_queue']['redis']['db'],
            redis_password=config_dict['task_queue']['redis'].get('password'),
            max_retries=config_dict['task_queue']['queue']['max_retries'],
            task_timeout=config_dict['task_queue']['queue']['task_timeout']
        )
        
        # Dashboard configuration
        dashboard_cfg = DashboardConfig(
            host=config_dict['dashboard']['host'],
            port=config_dict['dashboard']['port'],
            debug=config_dict['dashboard']['debug'],
            secret_key=config_dict['dashboard']['secret_key']
        )
        
        return DeviceFarmConfig(
            gologin=gologin_cfg,
            adb=adb_cfg,
            appium=appium_cfg,
            task_queue=task_queue_cfg,
            dashboard=dashboard_cfg,
            database_url=config_dict['database']['url'],
            max_devices=config_dict['system']['max_devices'],
            log_level=config_dict['system']['log_level'],
            raw_config=config_dict
        )
    
    def validate_config(self) -> bool:
        """Validate configuration completeness"""
        if not self.config:
            logger.error("Configuration not loaded")
            return False
            
        # Validate required fields
        required_checks = [
            (self.config.gologin.token, "Gologin API token"),
            (self.config.adb.adb_path, "ADB path"),
            (self.config.dashboard.secret_key, "Dashboard secret key")
        ]
        
        for value, name in required_checks:
            if not value or value.strip() == "":
                logger.error(f"Missing required configuration: {name}")
                return False
                
        logger.info("Configuration validation passed")
        return True
    
    def get_config(self) -> DeviceFarmConfig:
        """Get current configuration"""
        if not self.config:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self.config


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.load_config()
    return _config_manager


def get_config() -> DeviceFarmConfig:
    """Get current configuration"""
    return get_config_manager().get_config()


def validate_configuration() -> bool:
    """Validate current configuration"""
    return get_config_manager().validate_config()