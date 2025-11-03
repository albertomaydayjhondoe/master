"""
GoLogin API Client - Cliente avanzado para la API de GoLogin

Este módulo proporciona una interfaz completa para interactuar con la API de GoLogin,
incluyendo gestión de perfiles, sesiones, proxies y operaciones avanzadas de anonimato.
"""

import asyncio
import aiohttp
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import os

logger = logging.getLogger(__name__)

@dataclass
class GoLoginProfile:
    """Representación de un perfil de GoLogin."""
    id: str
    name: str
    os: str = "win"
    status: str = "Active"
    
    # Información del navegador
    user_agent: str = ""
    language: str = "en-US"
    platform: str = "Win32"
    
    # Información geográfica
    country: str = "US"
    city: str = "New York"
    timezone: str = "America/New_York"
    
    # Configuración de proxy
    proxy_enabled: bool = True
    proxy_type: str = "http"
    proxy_host: str = ""
    proxy_port: int = 8080
    proxy_username: str = ""
    proxy_password: str = ""
    
    # Configuración de fingerprinting
    webrtc_mode: str = "altered"
    canvas_mode: str = "noise"
    webgl_mode: str = "noise"
    audio_context_mode: str = "noise"
    
    # Metadatos
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'GoLoginProfile':
        """Crear perfil desde respuesta de API."""
        # Extraer información anidada
        navigator = data.get('navigator', {})
        proxy = data.get('proxy', {})
        geo = data.get('geoProxyInfo', {})
        webrtc = data.get('webRTC', {})
        canvas = data.get('canvas', {})
        webgl = data.get('webGL', {})
        audio = data.get('audioContext', {})
        
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            os=data.get('os', 'win'),
            status=data.get('status', 'Active'),
            user_agent=navigator.get('userAgent', ''),
            language=navigator.get('language', 'en-US'),
            platform=navigator.get('platform', 'Win32'),
            country=geo.get('country', 'US'),
            city=geo.get('city', 'New York'),
            timezone=data.get('timezone', {}).get('id', 'America/New_York'),
            proxy_enabled=data.get('proxyEnabled', True),
            proxy_type=proxy.get('mode', 'http'),
            proxy_host=proxy.get('host', ''),
            proxy_port=proxy.get('port', 8080),
            proxy_username=proxy.get('username', ''),
            proxy_password=proxy.get('password', ''),
            webrtc_mode=webrtc.get('mode', 'altered'),
            canvas_mode=canvas.get('mode', 'noise'),
            webgl_mode=webgl.get('mode', 'noise'),
            audio_context_mode=audio.get('mode', 'noise'),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt')
        )
    
    def to_api_payload(self) -> Dict[str, Any]:
        """Convertir a payload para API."""
        return {
            "name": self.name,
            "os": self.os,
            "navigator": {
                "userAgent": self.user_agent,
                "language": self.language,
                "platform": self.platform,
                "doNotTrack": False,
                "hardwareConcurrency": 4
            },
            "geoProxyInfo": {
                "country": self.country,
                "city": self.city
            },
            "timezone": {
                "enabled": True,
                "fillBasedOnIp": True,
                "id": self.timezone
            },
            "proxyEnabled": self.proxy_enabled,
            "proxy": {
                "mode": self.proxy_type,
                "host": self.proxy_host,
                "port": self.proxy_port,
                "username": self.proxy_username,
                "password": self.proxy_password
            },
            "webRTC": {
                "mode": self.webrtc_mode,
                "enabled": True
            },
            "canvas": {"mode": self.canvas_mode},
            "webGL": {"mode": self.webgl_mode},
            "audioContext": {"mode": self.audio_context_mode}
        }

@dataclass
class BrowserSession:
    """Información de sesión del navegador."""
    profile_id: str
    session_id: str
    port: int
    status: str = "running"
    started_at: float = 0.0
    pid: Optional[int] = None
    
    def __post_init__(self):
        if self.started_at == 0.0:
            self.started_at = time.time()

class GoLoginAPIClient:
    """
    Cliente avanzado para la API de GoLogin.
    
    Características:
    - Gestión completa de perfiles
    - Control de sesiones de navegador
    - Manejo de errores robusto
    - Cache y optimizaciones
    - Modo dummy para desarrollo
    """
    
    def __init__(self, 
                 api_token: str = None,
                 base_url: str = "https://api.gologin.com",
                 timeout: int = 30,
                 max_retries: int = 3):
        """
        Inicializar cliente API.
        
        Args:
            api_token: Token de autenticación
            base_url: URL base de la API
            timeout: Timeout para requests
            max_retries: Máximo número de reintentos
        """
        self.api_token = api_token or os.getenv("GOLOGIN_API_TOKEN", "dummy_token")
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Estado interno
        self.session: Optional[aiohttp.ClientSession] = None
        self.active_sessions: Dict[str, BrowserSession] = {}
        self.profiles_cache: Dict[str, GoLoginProfile] = {}
        self.cache_ttl = 300  # 5 minutos
        self.last_cache_update = 0
        
        # Configuración
        self.dummy_mode = os.getenv("DUMMY_MODE", "true").lower() == "true"
        
        logger.info(f"GoLogin API Client inicializado (dummy_mode: {self.dummy_mode})")
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.cleanup()
    
    async def initialize(self):
        """Inicializar cliente."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "GoLogin-API-Client/1.0"
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=50)
        )
        
        # Verificar conexión en modo producción
        if not self.dummy_mode:
            await self._verify_connection()
        
        logger.info("✅ Cliente API GoLogin inicializado")
    
    async def cleanup(self):
        """Limpiar recursos."""
        # Cerrar sesiones activas
        if self.active_sessions:
            logger.info(f"🧹 Cerrando {len(self.active_sessions)} sesiones activas...")
            for session in list(self.active_sessions.values()):
                try:
                    await self.stop_browser_session(session.profile_id)
                except Exception as e:
                    logger.warning(f"Error cerrando sesión {session.profile_id}: {e}")
        
        # Cerrar cliente HTTP
        if self.session:
            await self.session.close()
        
        logger.info("✅ Cliente API cerrado")
    
    async def _verify_connection(self):
        """Verificar conexión con la API."""
        try:
            user_info = await self.get_user_info()
            logger.info(f"✅ Conectado a GoLogin: {user_info.get('email', 'Usuario')}")
        except Exception as e:
            logger.warning(f"⚠️ Error verificando conexión GoLogin: {e}")
    
    async def _make_request(self, 
                           method: str, 
                           endpoint: str, 
                           data: Optional[Dict] = None,
                           params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Realizar request HTTP con manejo de errores y reintentos.
        
        Args:
            method: Método HTTP
            endpoint: Endpoint de la API
            data: Datos para POST/PUT
            params: Parámetros de query
            
        Returns:
            Respuesta JSON
        """
        if self.dummy_mode:
            return await self._dummy_response(method, endpoint, data)
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    
                    # Manejar códigos de estado
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 201:
                        return await response.json()
                    elif response.status == 204:
                        return {}
                    elif response.status == 404:
                        raise ValueError(f"Recurso no encontrado: {endpoint}")
                    elif response.status == 401:
                        raise ValueError("Token de API inválido")
                    elif response.status == 429:
                        # Rate limiting
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limit alcanzado, esperando {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        error_text = await response.text()
                        raise ValueError(f"Error API {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Timeout en intento {attempt + 1}, reintentando en {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                raise
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Error en intento {attempt + 1}: {e}, reintentando en {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                raise
        
        raise RuntimeError(f"Falló después de {self.max_retries} intentos")
    
    async def _dummy_response(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Generar respuesta dummy para desarrollo."""
        await asyncio.sleep(0.1)  # Simular latencia
        
        if endpoint == "/user":
            return {
                "id": "dummy_user_123",
                "email": "test@example.com",
                "balance": 100.0,
                "subscription": "Premium"
            }
        
        elif endpoint == "/browser/v2" and method == "GET":
            # Lista de perfiles
            return [
                {
                    "id": f"dummy_profile_{i}",
                    "name": f"Dummy Profile {i}",
                    "os": "win",
                    "status": "Active",
                    "navigator": {"userAgent": "Dummy User Agent", "language": "en-US"},
                    "geoProxyInfo": {"country": "US", "city": "New York"},
                    "proxy": {"host": "dummy.proxy.com", "port": 8080},
                    "createdAt": "2024-01-01T00:00:00Z"
                }
                for i in range(1, 4)
            ]
        
        elif endpoint == "/browser/v2" and method == "POST":
            # Crear perfil
            return {
                "id": f"dummy_profile_{int(time.time())}",
                "name": data.get("name", "Dummy Profile"),
                "status": "Active",
                **data
            }
        
        elif "/browser/v2/" in endpoint and method == "GET":
            # Perfil individual
            profile_id = endpoint.split("/")[-1]
            return {
                "id": profile_id,
                "name": f"Profile {profile_id}",
                "os": "win",
                "status": "Active",
                "navigator": {"userAgent": "Dummy User Agent"},
                "geoProxyInfo": {"country": "US", "city": "New York"}
            }
        
        elif "/start" in endpoint:
            # Iniciar sesión
            return {
                "status": "success",
                "port": 3001,
                "session": f"dummy_session_{int(time.time())}"
            }
        
        elif "/stop" in endpoint:
            # Parar sesión
            return {"status": "success"}
        
        else:
            return {"status": "success", "message": "Dummy response"}
    
    # Métodos de gestión de usuario
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Obtener información del usuario."""
        return await self._make_request("GET", "/user")
    
    # Métodos de gestión de perfiles
    
    async def list_profiles(self, limit: int = 50) -> List[GoLoginProfile]:
        """
        Listar perfiles.
        
        Args:
            limit: Límite de perfiles a obtener
            
        Returns:
            Lista de perfiles
        """
        # Verificar cache
        if (time.time() - self.last_cache_update) < self.cache_ttl and self.profiles_cache:
            logger.debug("📋 Usando perfiles desde cache")
            return list(self.profiles_cache.values())[:limit]
        
        # Obtener desde API
        params = {"limit": limit}
        response = await self._make_request("GET", "/browser/v2", params=params)
        
        profiles = []
        if isinstance(response, list):
            for profile_data in response:
                profile = GoLoginProfile.from_api_response(profile_data)
                profiles.append(profile)
                self.profiles_cache[profile.id] = profile
        
        self.last_cache_update = time.time()
        
        logger.info(f"📋 Obtenidos {len(profiles)} perfiles")
        return profiles
    
    async def get_profile(self, profile_id: str) -> GoLoginProfile:
        """
        Obtener perfil específico.
        
        Args:
            profile_id: ID del perfil
            
        Returns:
            Perfil de GoLogin
        """
        # Verificar cache
        if profile_id in self.profiles_cache:
            cache_age = time.time() - self.last_cache_update
            if cache_age < self.cache_ttl:
                logger.debug(f"👤 Usando perfil {profile_id} desde cache")
                return self.profiles_cache[profile_id]
        
        # Obtener desde API
        response = await self._make_request("GET", f"/browser/v2/{profile_id}")
        profile = GoLoginProfile.from_api_response(response)
        
        # Actualizar cache
        self.profiles_cache[profile_id] = profile
        
        logger.info(f"👤 Obtenido perfil: {profile_id}")
        return profile
    
    async def create_profile(self, profile: GoLoginProfile) -> GoLoginProfile:
        """
        Crear nuevo perfil.
        
        Args:
            profile: Perfil a crear
            
        Returns:
            Perfil creado con ID asignado
        """
        payload = profile.to_api_payload()
        response = await self._make_request("POST", "/browser/v2", data=payload)
        
        created_profile = GoLoginProfile.from_api_response(response)
        
        # Actualizar cache
        self.profiles_cache[created_profile.id] = created_profile
        
        logger.info(f"✨ Perfil creado: {created_profile.id} ({created_profile.name})")
        return created_profile
    
    async def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> GoLoginProfile:
        """
        Actualizar perfil existente.
        
        Args:
            profile_id: ID del perfil
            updates: Campos a actualizar
            
        Returns:
            Perfil actualizado
        """
        response = await self._make_request("PUT", f"/browser/v2/{profile_id}", data=updates)
        updated_profile = GoLoginProfile.from_api_response(response)
        
        # Actualizar cache
        self.profiles_cache[profile_id] = updated_profile
        
        logger.info(f"🔄 Perfil actualizado: {profile_id}")
        return updated_profile
    
    async def delete_profile(self, profile_id: str) -> bool:
        """
        Eliminar perfil.
        
        Args:
            profile_id: ID del perfil
            
        Returns:
            True si se eliminó correctamente
        """
        await self._make_request("DELETE", f"/browser/v2/{profile_id}")
        
        # Remover del cache
        self.profiles_cache.pop(profile_id, None)
        
        # Cerrar sesión si está activa
        if profile_id in self.active_sessions:
            await self.stop_browser_session(profile_id)
        
        logger.info(f"🗑️ Perfil eliminado: {profile_id}")
        return True
    
    # Métodos de gestión de sesiones de navegador
    
    async def start_browser_session(self, profile_id: str) -> BrowserSession:
        """
        Iniciar sesión de navegador.
        
        Args:
            profile_id: ID del perfil
            
        Returns:
            Información de la sesión
        """
        # Verificar si ya existe sesión activa
        if profile_id in self.active_sessions:
            existing_session = self.active_sessions[profile_id]
            logger.info(f"🌐 Sesión ya activa para perfil {profile_id}: puerto {existing_session.port}")
            return existing_session
        
        # Iniciar nueva sesión
        response = await self._make_request("POST", f"/browser/v2/{profile_id}/start")
        
        session = BrowserSession(
            profile_id=profile_id,
            session_id=response.get("session", f"session_{profile_id}"),
            port=response.get("port", 3001),
            status="running",
            pid=response.get("pid")
        )
        
        self.active_sessions[profile_id] = session
        
        logger.info(f"🚀 Sesión iniciada: {profile_id} en puerto {session.port}")
        return session
    
    async def stop_browser_session(self, profile_id: str) -> bool:
        """
        Detener sesión de navegador.
        
        Args:
            profile_id: ID del perfil
            
        Returns:
            True si se detuvo correctamente
        """
        if profile_id not in self.active_sessions:
            logger.warning(f"⚠️ No hay sesión activa para perfil {profile_id}")
            return False
        
        try:
            await self._make_request("DELETE", f"/browser/v2/{profile_id}/stop")
            
            session = self.active_sessions.pop(profile_id)
            session.status = "stopped"
            
            logger.info(f"⏹️ Sesión detenida: {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo sesión {profile_id}: {e}")
            # Remover de active_sessions de todas formas
            self.active_sessions.pop(profile_id, None)
            return False
    
    async def get_session_status(self, profile_id: str) -> Optional[BrowserSession]:
        """
        Obtener estado de sesión.
        
        Args:
            profile_id: ID del perfil
            
        Returns:
            Información de la sesión o None si no existe
        """
        return self.active_sessions.get(profile_id)
    
    async def list_active_sessions(self) -> List[BrowserSession]:
        """Listar todas las sesiones activas."""
        return list(self.active_sessions.values())
    
    # Métodos de utilidad
    
    async def get_proxy_info(self, profile_id: str) -> Dict[str, Any]:
        """
        Obtener información del proxy de un perfil.
        
        Args:
            profile_id: ID del perfil
            
        Returns:
            Información del proxy
        """
        profile = await self.get_profile(profile_id)
        
        return {
            "enabled": profile.proxy_enabled,
            "type": profile.proxy_type,
            "host": profile.proxy_host,
            "port": profile.proxy_port,
            "username": profile.proxy_username,
            "country": profile.country,
            "city": profile.city
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar salud del servicio.
        
        Returns:
            Estado del servicio
        """
        try:
            user_info = await self.get_user_info()
            active_sessions = len(self.active_sessions)
            cached_profiles = len(self.profiles_cache)
            
            return {
                "status": "healthy",
                "connected": True,
                "user_id": user_info.get("id"),
                "active_sessions": active_sessions,
                "cached_profiles": cached_profiles,
                "dummy_mode": self.dummy_mode,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "dummy_mode": self.dummy_mode,
                "timestamp": time.time()
            }
    
    def clear_cache(self):
        """Limpiar cache de perfiles."""
        self.profiles_cache.clear()
        self.last_cache_update = 0
        logger.info("🧹 Cache de perfiles limpiado")


# Funciones de conveniencia

async def create_gologin_client(api_token: str = None) -> GoLoginAPIClient:
    """Crear y inicializar cliente GoLogin."""
    client = GoLoginAPIClient(api_token=api_token)
    await client.initialize()
    return client

async def quick_profile_session(profile_id: str, api_token: str = None) -> BrowserSession:
    """Crear sesión rápida para un perfil."""
    async with GoLoginAPIClient(api_token=api_token) as client:
        session = await client.start_browser_session(profile_id)
        return session


if __name__ == "__main__":
    # Test del cliente
    async def test_api_client():
        async with GoLoginAPIClient() as client:
            # Health check
            health = await client.health_check()
            print(f"Health: {health}")
            
            # Listar perfiles
            profiles = await client.list_profiles(limit=5)
            print(f"Perfiles encontrados: {len(profiles)}")
            
            if profiles:
                # Obtener primer perfil
                profile = profiles[0]
                print(f"Perfil: {profile.name} ({profile.country})")
                
                # Iniciar sesión
                session = await client.start_browser_session(profile.id)
                print(f"Sesión iniciada en puerto: {session.port}")
                
                # Parar sesión
                await client.stop_browser_session(profile.id)
                print("Sesión detenida")
    
    asyncio.run(test_api_client())