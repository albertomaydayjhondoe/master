"""
GoLogin Anonymity Context - Sistema de Anonimato Avanzado

Este módulo implementa un contexto completo de anonimato usando GoLogin
para navegación web sin detección. Incluye gestión de perfiles, proxies,
fingerprinting, y rotación automática.
"""

import asyncio
import logging
import random
import time
import json
from typing import Dict, List, Optional, Any, Tuple, ContextManager
from dataclasses import dataclass, asdict
from pathlib import Path
from contextlib import asynccontextmanager
import aiohttp
import os

logger = logging.getLogger(__name__)

@dataclass
class AnonymityProfile:
    """Perfil de anonimato completo."""
    profile_id: str
    name: str
    
    # Información geográfica
    country: str
    city: str
    timezone: str
    
    # Configuración del navegador
    user_agent: str
    screen_resolution: str
    language: str
    
    # Proxy y red
    proxy_type: str
    proxy_host: str
    proxy_port: int
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    
    # Fingerprinting
    webrtc_mode: str = "altered"
    canvas_mode: str = "noise"
    webgl_mode: str = "noise"
    audio_context: str = "noise"
    
    # Metadatos
    created_at: float = 0.0
    last_used: float = 0.0
    usage_count: int = 0
    max_usage: int = 100
    is_active: bool = True
    
    def __post_init__(self) -> None:
        if self.created_at == 0.0:
            self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnonymityProfile':
        """Crear desde diccionario."""
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Verificar si el perfil ha expirado."""
        return self.usage_count >= self.max_usage
    
    def can_use(self) -> bool:
        """Verificar si el perfil puede usarse."""
        return self.is_active and not self.is_expired()
    
    def mark_used(self) -> None:
        """Marcar perfil como usado."""
        self.last_used = time.time()
        self.usage_count += 1

@dataclass 
class AnonymityStats:
    """Estadísticas de anonimato."""
    profiles_created: int = 0
    profiles_active: int = 0
    profiles_expired: int = 0
    sessions_started: int = 0
    sessions_completed: int = 0
    detection_events: int = 0
    proxy_rotations: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class GoLoginAnonymityContext:
    """
    Contexto de anonimato completo con GoLogin.
    
    Características:
    - Gestión automática de perfiles múltiples
    - Rotación inteligente de proxies
    - Anti-fingerprinting avanzado
    - Detección y evasión automática
    - Persistencia de configuración
    - Métricas y estadísticas
    """
    
    def __init__(self, 
                 api_token: str = None,
                 profiles_dir: str = None,
                 max_profiles: int = 30,
                 auto_rotate: bool = True,
                 detection_sensitivity: str = "medium"):
        """
        Inicializar contexto de anonimato.
        
        Args:
            api_token: Token API de GoLogin
            profiles_dir: Directorio para almacenar perfiles
            max_profiles: Máximo número de perfiles activos
            auto_rotate: Rotación automática de perfiles
            detection_sensitivity: Sensibilidad detección ("low", "medium", "high")
        """
        self.api_token = api_token or os.getenv("GOLOGIN_API_TOKEN", "dummy_token")
        self.profiles_dir = Path(profiles_dir or "data/gologin_profiles")
        self.max_profiles = max_profiles
        self.auto_rotate = auto_rotate
        self.detection_sensitivity = detection_sensitivity
        
        # Estado interno
        self.profiles: Dict[str, AnonymityProfile] = {}
        self.active_profile: Optional[AnonymityProfile] = None
        self.session = None
        self.stats = AnonymityStats()
        
        # Configuración
        self.api_base = "https://api.gologin.com"
        self.dummy_mode = os.getenv("DUMMY_MODE", "true").lower() == "true"
        
        # Crear directorio de perfiles
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Cargar perfiles existentes
        self._load_profiles()
        
        logger.info(f"GoLogin Anonymity Context inicializado: {len(self.profiles)} perfiles")
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.cleanup()
    
    async def initialize(self):
        """Inicializar sistema de anonimato."""
        logger.info("🔒 Inicializando sistema de anonimato GoLogin...")
        
        # Crear sesión HTTP
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Authorization": f"Bearer {self.api_token}"}
        )
        
        # Verificar conexión API si no está en modo dummy
        if not self.dummy_mode:
            await self._verify_api_connection()
        
        # Asegurar perfiles mínimos
        await self._ensure_min_profiles()
        
        logger.info(f"✅ Sistema de anonimato listo: {len(self.profiles)} perfiles disponibles")
    
    async def cleanup(self):
        """Limpiar recursos."""
        logger.info("🧹 Limpiando contexto de anonimato...")
        
        # Guardar perfiles
        self._save_profiles()
        
        # Cerrar sesión HTTP
        if self.session:
            await self.session.close()
        
        logger.info("✅ Contexto de anonimato cerrado")
    
    def _load_profiles(self):
        """Cargar perfiles desde disco."""
        profiles_file = self.profiles_dir / "profiles.json"
        
        if profiles_file.exists():
            try:
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                
                for profile_data in data.get('profiles', []):
                    profile = AnonymityProfile.from_dict(profile_data)
                    self.profiles[profile.profile_id] = profile
                
                # Cargar estadísticas
                if 'stats' in data:
                    self.stats = AnonymityStats(**data['stats'])
                    
                logger.info(f"📁 Cargados {len(self.profiles)} perfiles desde disco")
                
            except Exception as e:
                logger.warning(f"Error cargando perfiles: {e}")
    
    def _save_profiles(self):
        """Guardar perfiles a disco."""
        profiles_file = self.profiles_dir / "profiles.json"
        
        try:
            data = {
                'profiles': [profile.to_dict() for profile in self.profiles.values()],
                'stats': self.stats.to_dict(),
                'saved_at': time.time()
            }
            
            with open(profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"💾 Guardados {len(self.profiles)} perfiles")
            
        except Exception as e:
            logger.error(f"Error guardando perfiles: {e}")
    
    async def _verify_api_connection(self):
        """Verificar conexión con API de GoLogin."""
        try:
            async with self.session.get(f"{self.api_base}/user") as response:
                if response.status == 200:
                    user_data = await response.json()
                    logger.info(f"✅ Conectado a GoLogin API: {user_data.get('email', 'Usuario')}")
                else:
                    logger.warning(f"⚠️ API GoLogin respuesta: {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ Error verificando API GoLogin: {e}")
    
    async def _ensure_min_profiles(self):
        """Asegurar número mínimo de perfiles."""
        min_profiles = min(5, self.max_profiles)
        active_profiles = [p for p in self.profiles.values() if p.can_use()]
        
        if len(active_profiles) < min_profiles:
            needed = min_profiles - len(active_profiles)
            logger.info(f"🔄 Creando {needed} perfiles adicionales...")
            
            for _ in range(needed):
                await self.create_profile()
    
    async def create_profile(self, 
                           country: str = None,
                           proxy_config: Dict[str, Any] = None) -> AnonymityProfile:
        """
        Crear nuevo perfil de anonimato.
        
        Args:
            country: País para el perfil
            proxy_config: Configuración específica de proxy
            
        Returns:
            Perfil de anonimato creado
        """
        logger.info("🆕 Creando nuevo perfil de anonimato...")
        
        # Seleccionar configuración aleatoria
        country = country or self._get_random_country()
        city, timezone = self._get_city_timezone(country)
        
        # Generar ID único
        profile_id = f"anon_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Configuración del navegador
        user_agent = self._generate_user_agent()
        screen_resolution = self._get_random_resolution()
        language = self._get_language_for_country(country)
        
        # Configuración de proxy
        if not proxy_config:
            proxy_config = self._get_random_proxy_config(country)
        
        # Crear perfil
        profile = AnonymityProfile(
            profile_id=profile_id,
            name=f"Anonymous_{profile_id[-8:]}",
            country=country,
            city=city,
            timezone=timezone,
            user_agent=user_agent,
            screen_resolution=screen_resolution,
            language=language,
            **proxy_config
        )
        
        # Crear en GoLogin API si no está en modo dummy
        if not self.dummy_mode:
            await self._create_gologin_profile(profile)
        
        # Almacenar perfil
        self.profiles[profile_id] = profile
        self.stats.profiles_created += 1
        self.stats.profiles_active += 1
        
        logger.info(f"✅ Perfil creado: {profile_id} ({country}, {city})")
        
        return profile
    
    async def _create_gologin_profile(self, profile: AnonymityProfile):
        """Crear perfil en GoLogin API."""
        try:
            payload = {
                "name": profile.name,
                "os": "win",
                "navigator": {
                    "userAgent": profile.user_agent,
                    "language": profile.language,
                    "platform": "Win32",
                    "doNotTrack": False,
                    "hardwareConcurrency": random.randint(2, 8)
                },
                "geoProxyInfo": {
                    "country": profile.country,
                    "city": profile.city
                },
                "proxyEnabled": True,
                "proxy": {
                    "mode": profile.proxy_type,
                    "host": profile.proxy_host,
                    "port": profile.proxy_port,
                    "username": profile.proxy_username,
                    "password": profile.proxy_password
                },
                "webRTC": {
                    "mode": profile.webrtc_mode,
                    "enabled": True
                },
                "canvas": {"mode": profile.canvas_mode},
                "webGL": {"mode": profile.webgl_mode},
                "audioContext": {"mode": profile.audio_context},
                "timezone": {"enabled": True, "fillBasedOnIp": True}
            }
            
            async with self.session.post(
                f"{self.api_base}/browser/v2",
                json=payload
            ) as response:
                if response.status == 201:
                    data = await response.json()
                    profile.profile_id = data.get('id', profile.profile_id)
                    logger.info(f"✅ Perfil GoLogin creado: {profile.profile_id}")
                else:
                    logger.warning(f"⚠️ Error creando perfil GoLogin: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error creando perfil GoLogin: {e}")
    
    async def get_anonymous_context(self, 
                                  force_new: bool = False,
                                  country_preference: str = None) -> AnonymityProfile:
        """
        Obtener contexto de anonimato listo para usar.
        
        Args:
            force_new: Forzar creación de nuevo perfil
            country_preference: Preferencia de país
            
        Returns:
            Perfil de anonimato activo
        """
        if force_new or not self.active_profile or not self.active_profile.can_use():
            # Seleccionar o crear perfil
            profile = await self._select_best_profile(country_preference)
            
            if not profile:
                profile = await self.create_profile(country=country_preference)
            
            self.active_profile = profile
            self.stats.sessions_started += 1
            
            logger.info(f"🔒 Contexto anonimato activo: {profile.profile_id} ({profile.country})")
        
        # Marcar como usado
        self.active_profile.mark_used()
        
        return self.active_profile
    
    async def _select_best_profile(self, country_preference: str = None) -> Optional[AnonymityProfile]:
        """Seleccionar el mejor perfil disponible."""
        available_profiles = [p for p in self.profiles.values() if p.can_use()]
        
        if not available_profiles:
            return None
        
        # Filtrar por país si se especifica
        if country_preference:
            country_profiles = [p for p in available_profiles if p.country == country_preference]
            if country_profiles:
                available_profiles = country_profiles
        
        # Seleccionar perfil con menor uso
        best_profile = min(available_profiles, key=lambda p: p.usage_count)
        
        return best_profile
    
    async def rotate_profile(self) -> AnonymityProfile:
        """Rotar a un nuevo perfil de anonimato."""
        logger.info("🔄 Rotando perfil de anonimato...")
        
        # Obtener nuevo perfil
        old_profile = self.active_profile
        new_profile = await self.get_anonymous_context(force_new=True)
        
        self.stats.proxy_rotations += 1
        
        if old_profile:
            logger.info(f"🔄 Rotación: {old_profile.profile_id} → {new_profile.profile_id}")
        
        return new_profile
    
    def detect_fingerprinting_attempt(self, indicators: List[str]) -> bool:
        """
        Detectar intento de fingerprinting.
        
        Args:
            indicators: Lista de indicadores de detección
            
        Returns:
            True si se detecta fingerprinting
        """
        risk_indicators = [
            "canvas_fingerprint",
            "webgl_fingerprint", 
            "audio_fingerprint",
            "font_detection",
            "timezone_check",
            "screen_resolution_check",
            "webrtc_leak_check"
        ]
        
        detected_risks = [i for i in indicators if i in risk_indicators]
        
        if detected_risks:
            self.stats.detection_events += 1
            logger.warning(f"🚨 Fingerprinting detectado: {detected_risks}")
            
            # Auto-rotación si está habilitada
            if self.auto_rotate and len(detected_risks) >= 2:
                asyncio.create_task(self.rotate_profile())
            
            return True
        
        return False
    
    def get_browser_config(self) -> Dict[str, Any]:
        """Obtener configuración del navegador para el perfil activo."""
        if not self.active_profile:
            raise ValueError("No hay perfil activo")
        
        profile = self.active_profile
        
        return {
            "user_agent": profile.user_agent,
            "viewport": {"width": int(profile.screen_resolution.split('x')[0]), 
                        "height": int(profile.screen_resolution.split('x')[1])},
            "locale": profile.language,
            "timezone_id": profile.timezone,
            "proxy": {
                "server": f"{profile.proxy_type}://{profile.proxy_host}:{profile.proxy_port}",
                "username": profile.proxy_username,
                "password": profile.proxy_password
            } if profile.proxy_host != "dummy" else None,
            "extra_http_headers": {
                "Accept-Language": f"{profile.language},en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        }
    
    def get_anonymity_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de anonimato."""
        active_profiles = len([p for p in self.profiles.values() if p.can_use()])
        expired_profiles = len([p for p in self.profiles.values() if p.is_expired()])
        
        self.stats.profiles_active = active_profiles
        self.stats.profiles_expired = expired_profiles
        
        return {
            **self.stats.to_dict(),
            "total_profiles": len(self.profiles),
            "current_profile": self.active_profile.profile_id if self.active_profile else None,
            "rotation_rate": self.stats.proxy_rotations / max(self.stats.sessions_started, 1),
            "detection_rate": self.stats.detection_events / max(self.stats.sessions_completed, 1)
        }
    
    # Métodos de utilidad para generar datos aleatorios
    
    def _get_random_country(self) -> str:
        """Obtener país aleatorio."""
        countries = [
            "US", "CA", "GB", "DE", "FR", "ES", "IT", "NL", 
            "AU", "JP", "KR", "SG", "BR", "MX", "AR", "CL"
        ]
        return random.choice(countries)
    
    def _get_city_timezone(self, country: str) -> Tuple[str, str]:
        """Obtener ciudad y timezone para un país."""
        city_tz_map = {
            "US": [("New York", "America/New_York"), ("Los Angeles", "America/Los_Angeles"), 
                   ("Chicago", "America/Chicago"), ("Miami", "America/New_York")],
            "CA": [("Toronto", "America/Toronto"), ("Vancouver", "America/Vancouver")],
            "GB": [("London", "Europe/London"), ("Manchester", "Europe/London")],
            "DE": [("Berlin", "Europe/Berlin"), ("Munich", "Europe/Berlin")],
            "FR": [("Paris", "Europe/Paris"), ("Lyon", "Europe/Paris")],
            "ES": [("Madrid", "Europe/Madrid"), ("Barcelona", "Europe/Madrid")],
            "IT": [("Rome", "Europe/Rome"), ("Milan", "Europe/Rome")],
            "NL": [("Amsterdam", "Europe/Amsterdam"), ("Rotterdam", "Europe/Amsterdam")],
            "AU": [("Sydney", "Australia/Sydney"), ("Melbourne", "Australia/Melbourne")],
            "JP": [("Tokyo", "Asia/Tokyo"), ("Osaka", "Asia/Tokyo")],
            "KR": [("Seoul", "Asia/Seoul"), ("Busan", "Asia/Seoul")],
            "SG": [("Singapore", "Asia/Singapore")],
            "BR": [("São Paulo", "America/Sao_Paulo"), ("Rio de Janeiro", "America/Sao_Paulo")],
            "MX": [("Mexico City", "America/Mexico_City"), ("Guadalajara", "America/Mexico_City")],
            "AR": [("Buenos Aires", "America/Argentina/Buenos_Aires")],
            "CL": [("Santiago", "America/Santiago")]
        }
        
        options = city_tz_map.get(country, [("Unknown", "UTC")])
        return random.choice(options)
    
    def _get_language_for_country(self, country: str) -> str:
        """Obtener idioma para un país."""
        lang_map = {
            "US": "en-US", "CA": "en-CA", "GB": "en-GB",
            "DE": "de-DE", "FR": "fr-FR", "ES": "es-ES", "IT": "it-IT", "NL": "nl-NL",
            "AU": "en-AU", "JP": "ja-JP", "KR": "ko-KR", "SG": "en-SG",
            "BR": "pt-BR", "MX": "es-MX", "AR": "es-AR", "CL": "es-CL"
        }
        return lang_map.get(country, "en-US")
    
    def _generate_user_agent(self) -> str:
        """Generar User-Agent aleatorio."""
        chrome_versions = ["120.0.6099.109", "119.0.6045.159", "118.0.5993.117"]
        webkit_versions = ["537.36"]
        
        chrome_version = random.choice(chrome_versions)
        webkit_version = random.choice(webkit_versions)
        
        return (f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit_version} "
                f"(KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}")
    
    def _get_random_resolution(self) -> str:
        """Obtener resolución aleatoria."""
        resolutions = [
            "1920x1080", "1366x768", "1536x864", "1440x900",
            "1280x720", "1600x900", "1920x1200", "2560x1440"
        ]
        return random.choice(resolutions)
    
    def _get_random_proxy_config(self, country: str) -> Dict[str, Any]:
        """Generar configuración de proxy aleatoria."""
        if self.dummy_mode:
            return {
                "proxy_type": "http",
                "proxy_host": "dummy",
                "proxy_port": 8080,
                "proxy_username": "dummy_user",
                "proxy_password": "dummy_pass"
            }
        
        # En producción, aquí se integraría con proveedores de proxy reales
        proxy_providers = [
            {"host": f"proxy-{country.lower()}.example.com", "port": 8080},
            {"host": f"gateway-{country.lower()}.proxy.com", "port": 3128},
        ]
        
        proxy = random.choice(proxy_providers)
        
        return {
            "proxy_type": "http",
            "proxy_host": proxy["host"],
            "proxy_port": proxy["port"],
            "proxy_username": f"user_{random.randint(1000, 9999)}",
            "proxy_password": f"pass_{random.randint(1000, 9999)}"
        }


# Context manager de conveniencia
@asynccontextmanager
async def anonymous_context(**kwargs):
    """
    Context manager para crear contexto de anonimato temporal.
    
    Usage:
        async with anonymous_context() as ctx:
            profile = await ctx.get_anonymous_context()
            browser_config = ctx.get_browser_config()
    """
    context = GoLoginAnonymityContext(**kwargs)
    
    try:
        await context.initialize()
        yield context
    finally:
        await context.cleanup()


# Función de conveniencia
async def create_anonymous_session(country: str = None, 
                                 api_token: str = None) -> Tuple[AnonymityProfile, Dict[str, Any]]:
    """
    Crear sesión anónima rápida.
    
    Args:
        country: País preferido
        api_token: Token API GoLogin
        
    Returns:
        Tupla con (perfil, configuración_navegador)
    """
    async with anonymous_context(api_token=api_token) as ctx:
        profile = await ctx.get_anonymous_context(country_preference=country)
        browser_config = ctx.get_browser_config()
        
        return profile, browser_config


if __name__ == "__main__":
    # Test del sistema
    async def test_anonymity_context() -> None:
        async with anonymous_context() as ctx:
            # Crear perfil
            profile = await ctx.get_anonymous_context()
            print(f"Perfil activo: {profile.profile_id}")
            
            # Obtener configuración
            config = ctx.get_browser_config()
            print(f"User-Agent: {config['user_agent']}")
            
            # Estadísticas
            stats = ctx.get_anonymity_stats()
            print(f"Estadísticas: {stats}")
    
    asyncio.run(test_anonymity_context())