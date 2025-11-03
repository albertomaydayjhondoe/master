"""
GoLogin Configuration - Configuración central del sistema GoLogin

Este módulo maneja toda la configuración del sistema de anonimato GoLogin,
incluyendo perfiles, proxies, patrones humanos y configuraciones avanzadas.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    """Configuración de proxy."""
    enabled: bool = True
    type: str = "http"  # http, socks5, socks4
    host: str = ""
    port: int = 8080
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    sticky_session: bool = False
    rotation_interval: int = 3600  # segundos

@dataclass
class FingerPrintConfig:
    """Configuración de fingerprinting."""
    webrtc_mode: str = "altered"  # disabled, real, altered
    canvas_mode: str = "noise"    # real, block, noise
    webgl_mode: str = "noise"     # real, block, noise
    audio_context: str = "noise"  # real, block, noise
    client_rects: str = "noise"   # real, block, noise
    timezone_mode: str = "auto"   # real, auto, custom
    language_mode: str = "auto"   # real, auto, custom
    geolocation_mode: str = "auto" # real, block, auto
    screen_mode: str = "auto"     # real, auto, custom

@dataclass
class BrowserPreferences:
    """Preferencias del navegador."""
    user_agent_mode: str = "auto"  # real, auto, custom
    platform: str = "Win32"
    do_not_track: bool = False
    hardware_concurrency: int = 4
    memory: int = 8
    
    # Configuraciones específicas
    disable_webgl: bool = False
    disable_web_security: bool = False
    disable_features: List[str] = field(default_factory=lambda: [
        "VizDisplayCompositor",
        "UseMojoVideoCapture"
    ])
    
    # Media
    disable_images: bool = False
    disable_javascript: bool = False
    disable_plugins: bool = False

@dataclass
class SecurityConfig:
    """Configuración de seguridad."""
    max_profile_usage: int = 100
    profile_rotation_interval: int = 7200  # 2 horas
    detection_sensitivity: str = "medium"  # low, medium, high
    auto_rotate_on_detection: bool = True
    
    # Límites de rate
    max_requests_per_minute: int = 60
    max_concurrent_sessions: int = 5
    
    # Timeouts
    page_load_timeout: int = 30
    element_wait_timeout: int = 10
    request_timeout: int = 30

@dataclass
class HumanBehaviorConfig:
    """Configuración de comportamiento humano."""
    # Delays base
    min_action_delay: float = 0.5
    max_action_delay: float = 2.0
    typing_speed_min: float = 0.05
    typing_speed_max: float = 0.15
    
    # Patrones de movimiento
    mouse_movement_steps: int = 5
    mouse_movement_speed: float = 1.0
    
    # Patrones de scroll
    scroll_pause_min: float = 0.3
    scroll_pause_max: float = 1.0
    scroll_distance_min: int = 200
    scroll_distance_max: int = 500
    
    # Patrones de lectura
    reading_pause_min: float = 1.0
    reading_pause_max: float = 5.0
    
    # Patrones de interacción
    interaction_delay_min: float = 0.2
    interaction_delay_max: float = 1.0
    
    # Probabilidades
    random_scroll_probability: float = 0.3
    random_pause_probability: float = 0.2
    back_button_probability: float = 0.1

@dataclass
class GoLoginConfig:
    """Configuración principal de GoLogin."""
    # API Configuration
    api_token: str = ""
    api_base_url: str = "https://api.gologin.com"
    api_timeout: int = 30
    api_max_retries: int = 3
    
    # Paths
    profiles_dir: str = "data/gologin_profiles"
    logs_dir: str = "logs/gologin"
    screenshots_dir: str = "logs/screenshots"
    
    # Limits
    max_profiles: int = 30
    max_active_sessions: int = 5
    cache_ttl: int = 300  # 5 minutos
    
    # Modes
    dummy_mode: bool = True
    debug_mode: bool = False
    headless_mode: bool = False
    
    # Default configurations
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    fingerprint: FingerPrintConfig = field(default_factory=FingerPrintConfig)
    browser: BrowserPreferences = field(default_factory=BrowserPreferences)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    human_behavior: HumanBehaviorConfig = field(default_factory=HumanBehaviorConfig)
    
    # Automation engine
    automation_engine: str = "playwright"  # playwright, selenium
    
    def __post_init__(self):
        """Post inicialización."""
        # Cargar desde variables de entorno
        self.api_token = self.api_token or os.getenv("GOLOGIN_API_TOKEN", "")
        self.dummy_mode = os.getenv("DUMMY_MODE", "true").lower() == "true"
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        
        # Crear directorios
        for dir_path in [self.profiles_dir, self.logs_dir, self.screenshots_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'GoLoginConfig':
        """Cargar configuración desde archivo."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Archivo de configuración no encontrado: {config_path}")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Crear instancias de sub-configuraciones
            if 'proxy' in data:
                data['proxy'] = ProxyConfig(**data['proxy'])
            if 'fingerprint' in data:
                data['fingerprint'] = FingerPrintConfig(**data['fingerprint'])
            if 'browser' in data:
                data['browser'] = BrowserPreferences(**data['browser'])
            if 'security' in data:
                data['security'] = SecurityConfig(**data['security'])
            if 'human_behavior' in data:
                data['human_behavior'] = HumanBehaviorConfig(**data['human_behavior'])
            
            config = cls(**data)
            logger.info(f"Configuración cargada desde: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error cargando configuración desde {config_path}: {e}")
            return cls()
    
    def save_to_file(self, config_path: Union[str, Path]):
        """Guardar configuración a archivo."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = asdict(self)
            
            with open(config_path, 'w') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(data, f, indent=2)
            
            logger.info(f"Configuración guardada en: {config_path}")
            
        except Exception as e:
            logger.error(f"Error guardando configuración en {config_path}: {e}")
    
    def get_browser_args(self) -> List[str]:
        """Obtener argumentos del navegador."""
        args = [
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI"
        ]
        
        if self.headless_mode:
            args.append("--headless")
        
        if self.browser.disable_web_security:
            args.append("--disable-web-security")
        
        if self.browser.disable_features:
            args.append(f"--disable-features={','.join(self.browser.disable_features)}")
        
        return args
    
    def get_proxy_url(self, proxy_config: ProxyConfig = None) -> Optional[str]:
        """Obtener URL del proxy."""
        proxy = proxy_config or self.proxy
        
        if not proxy.enabled or not proxy.host:
            return None
        
        auth = ""
        if proxy.username and proxy.password:
            auth = f"{proxy.username}:{proxy.password}@"
        
        return f"{proxy.type}://{auth}{proxy.host}:{proxy.port}"
    
    def validate(self) -> List[str]:
        """Validar configuración."""
        errors = []
        
        # Validar API token en modo producción
        if not self.dummy_mode and not self.api_token:
            errors.append("API token requerido en modo producción")
        
        # Validar límites
        if self.max_profiles <= 0:
            errors.append("max_profiles debe ser mayor a 0")
        
        if self.max_active_sessions <= 0:
            errors.append("max_active_sessions debe ser mayor a 0")
        
        # Validar proxy solo en modo producción
        if not self.dummy_mode and self.proxy.enabled and not self.proxy.host:
            errors.append("proxy.host requerido cuando proxy está habilitado")
        
        # Validar automation engine
        if self.automation_engine not in ["playwright", "selenium"]:
            errors.append("automation_engine debe ser 'playwright' o 'selenium'")
        
        return errors

class ConfigManager:
    """Gestor de configuración GoLogin."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuraciones por entorno
        self.environments = {
            "development": "gologin_dev.yaml",
            "staging": "gologin_staging.yaml", 
            "production": "gologin_prod.yaml"
        }
        
        self._current_config: Optional[GoLoginConfig] = None
    
    def get_config(self, environment: str = None) -> GoLoginConfig:
        """Obtener configuración para entorno."""
        if self._current_config:
            return self._current_config
        
        # Determinar entorno
        environment = environment or os.getenv("GOLOGIN_ENV", "development")
        
        # Buscar archivo de configuración
        config_file = self.config_dir / self.environments.get(environment, "gologin.yaml")
        
        if not config_file.exists():
            # Crear configuración default
            config = GoLoginConfig()
            config.save_to_file(config_file)
            logger.info(f"Configuración default creada: {config_file}")
        else:
            config = GoLoginConfig.from_file(config_file)
        
        # Validar configuración
        errors = config.validate()
        if errors:
            logger.warning(f"Errores en configuración: {errors}")
        
        self._current_config = config
        return config
    
    def create_default_configs(self):
        """Crear configuraciones default para todos los entornos."""
        configs = {
            "development": GoLoginConfig(
                dummy_mode=True,
                debug_mode=True,
                max_profiles=10,
                max_active_sessions=2
            ),
            "staging": GoLoginConfig(
                dummy_mode=False,
                debug_mode=True,
                max_profiles=20,
                max_active_sessions=3
            ),
            "production": GoLoginConfig(
                dummy_mode=False,
                debug_mode=False,
                max_profiles=30,
                max_active_sessions=5,
                headless_mode=True
            )
        }
        
        for env, config in configs.items():
            config_file = self.config_dir / self.environments[env]
            config.save_to_file(config_file)
        
        logger.info("Configuraciones default creadas para todos los entornos")
    
    def get_profile_template(self, profile_type: str = "standard") -> Dict[str, Any]:
        """Obtener template de perfil."""
        templates = {
            "standard": {
                "os": "win",
                "navigator": {
                    "userAgent": "auto",
                    "language": "en-US",
                    "platform": "Win32",
                    "doNotTrack": False,
                    "hardwareConcurrency": 4
                },
                "webRTC": {"mode": "altered"},
                "canvas": {"mode": "noise"},
                "webGL": {"mode": "noise"},
                "audioContext": {"mode": "noise"},
                "timezone": {"enabled": True, "fillBasedOnIp": True},
                "proxyEnabled": True
            },
            "high_anonymity": {
                "os": "win",
                "navigator": {
                    "userAgent": "auto",
                    "language": "en-US",
                    "platform": "Win32",
                    "doNotTrack": True,
                    "hardwareConcurrency": 4
                },
                "webRTC": {"mode": "disabled"},
                "canvas": {"mode": "block"},
                "webGL": {"mode": "block"},
                "audioContext": {"mode": "block"},
                "timezone": {"enabled": True, "fillBasedOnIp": True},
                "proxyEnabled": True,
                "storage": {"local": False, "extensions": False, "bookmarks": False}
            },
            "social_media": {
                "os": "win",
                "navigator": {
                    "userAgent": "auto",
                    "language": "en-US",
                    "platform": "Win32",
                    "doNotTrack": False,
                    "hardwareConcurrency": 4
                },
                "webRTC": {"mode": "altered"},
                "canvas": {"mode": "noise"},
                "webGL": {"mode": "noise"},
                "audioContext": {"mode": "noise"},
                "timezone": {"enabled": True, "fillBasedOnIp": True},
                "proxyEnabled": True,
                "storage": {"local": True, "extensions": False, "bookmarks": True}
            }
        }
        
        return templates.get(profile_type, templates["standard"])

# Instancia global del gestor de configuración
config_manager = ConfigManager()

def get_gologin_config(environment: str = None) -> GoLoginConfig:
    """Función de conveniencia para obtener configuración."""
    return config_manager.get_config(environment)

# Configuración por defecto para importación directa
DEFAULT_CONFIG = get_gologin_config()

if __name__ == "__main__":
    # Test y creación de configuraciones
    manager = ConfigManager()
    
    # Crear configuraciones default
    manager.create_default_configs()
    
    # Test configuración
    config = manager.get_config("development")
    print(f"Configuración cargada: dummy_mode={config.dummy_mode}")
    print(f"Argumentos del navegador: {config.get_browser_args()}")
    
    # Validación
    errors = config.validate()
    if errors:
        print(f"Errores de validación: {errors}")
    else:
        print("Configuración válida ✅")
