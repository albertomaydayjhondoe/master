"""
Device Farm v5 - Gologin API Manager
Handles integration with Gologin API for browser profile management
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config_manager import get_config
from ..core.models import get_db_session, GologinProfile


@dataclass
class ProxyConfig:
    """Proxy configuration from Gologin profile"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"  # http or socks5
    
    def to_url(self) -> str:
        """Convert to proxy URL format"""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        return f"{self.proxy_type}://{auth}{self.host}:{self.port}"


@dataclass 
class BrowserFingerprint:
    """Browser fingerprint data from Gologin"""
    user_agent: str
    screen_width: int
    screen_height: int
    timezone: str
    language: str
    platform: str
    hardware_concurrency: int
    webgl_vendor: str
    webgl_renderer: str
    plugins: List[Dict[str, Any]]
    
    def to_js_injection_script(self) -> str:
        """Generate JavaScript code to inject fingerprint"""
        return f"""
        // Gologin Fingerprint Injection
        Object.defineProperty(navigator, 'userAgent', {{
            get: function() {{ return '{self.user_agent}'; }}
        }});
        
        Object.defineProperty(navigator, 'platform', {{
            get: function() {{ return '{self.platform}'; }}
        }});
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: function() {{ return {self.hardware_concurrency}; }}
        }});
        
        Object.defineProperty(navigator, 'language', {{
            get: function() {{ return '{self.language}'; }}
        }});
        
        Object.defineProperty(screen, 'width', {{
            get: function() {{ return {self.screen_width}; }}
        }});
        
        Object.defineProperty(screen, 'height', {{
            get: function() {{ return {self.screen_height}; }}
        }});
        
        // WebGL fingerprint
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{ return '{self.webgl_vendor}'; }}
            if (parameter === 37446) {{ return '{self.webgl_renderer}'; }}
            return getParameter.call(this, parameter);
        }};
        
        console.log('Gologin fingerprint injected successfully');
        """


@dataclass
class GologinProfileData:
    """Complete Gologin profile data"""
    profile_id: str
    name: str
    proxy: Optional[ProxyConfig]
    fingerprint: BrowserFingerprint
    status: str
    created_at: datetime
    
    def is_available(self) -> bool:
        """Check if profile is available for use"""
        return self.status.lower() in ['active', 'available', 'ready']


class GologinAPIError(Exception):
    """Gologin API related errors"""
    pass


class GologinAPIManager:
    """Manager for Gologin API integration"""
    
    def __init__(self):
        self.config = get_config()
        self.api_url = self.config.gologin.api_url
        self.token = self.config.gologin.token
        self.cache_duration = self.config.gologin.cache_duration
        
        # Internal cache
        self._profile_cache: Dict[str, GologinProfileData] = {}
        self._cache_timestamp: Optional[datetime] = None
        
        # HTTP session
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.info("Gologin API Manager initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session exists"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.gologin.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'DeviceFarm-v5/1.0'
                }
            )
            logger.debug("HTTP session created for Gologin API")
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("HTTP session closed")
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if self._cache_timestamp is None:
            return False
        
        cache_age = datetime.now(timezone.utc) - self._cache_timestamp
        return cache_age.total_seconds() < self.cache_duration
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Gologin API with retry logic"""
        await self._ensure_session()
        
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            async with self._session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise GologinAPIError("Invalid Gologin API token")
                elif response.status == 429:
                    raise GologinAPIError("Rate limit exceeded")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise GologinAPIError(f"API error {response.status}: {error_text}")
                
                data = await response.json()
                logger.debug(f"Request successful, response: {len(str(data))} chars")
                return data
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout making request to {url}")
            raise
        except Exception as e:
            logger.error(f"Error making request to {url}: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test connection to Gologin API"""
        try:
            await self._make_request('GET', '/profile')
            logger.info("Gologin API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Gologin API connection test failed: {e}")
            return False
    
    async def get_profiles(self, force_refresh: bool = False) -> List[GologinProfileData]:
        """Get list of available Gologin profiles"""
        
        # Check cache first
        if not force_refresh and self._is_cache_valid() and self._profile_cache:
            logger.debug(f"Returning {len(self._profile_cache)} profiles from cache")
            return list(self._profile_cache.values())
        
        try:
            logger.info("Fetching profiles from Gologin API")
            
            # Get profiles list
            response = await self._make_request('GET', '/profile')
            profiles_data = response.get('data', [])
            
            if not profiles_data:
                logger.warning("No profiles returned from Gologin API")
                return []
            
            # Parse profiles
            profiles = []
            for profile_data in profiles_data:
                try:
                    parsed_profile = await self._parse_profile(profile_data)
                    if parsed_profile:
                        profiles.append(parsed_profile)
                        self._profile_cache[parsed_profile.profile_id] = parsed_profile
                except Exception as e:
                    logger.warning(f"Failed to parse profile {profile_data.get('id', 'unknown')}: {e}")
                    continue
            
            self._cache_timestamp = datetime.now(timezone.utc)
            logger.info(f"Successfully loaded {len(profiles)} profiles from Gologin API")
            
            # Update database
            await self._sync_profiles_to_db(profiles)
            
            return profiles
            
        except Exception as e:
            logger.error(f"Failed to fetch profiles from Gologin API: {e}")
            
            # Return cached data if available
            if self._profile_cache:
                logger.info(f"Returning {len(self._profile_cache)} cached profiles due to API error")
                return list(self._profile_cache.values())
            
            raise GologinAPIError(f"Failed to fetch profiles: {e}")
    
    async def _parse_profile(self, profile_data: Dict[str, Any]) -> Optional[GologinProfileData]:
        """Parse profile data from API response"""
        try:
            profile_id = profile_data.get('id')
            if not profile_id:
                logger.warning("Profile missing ID, skipping")
                return None
            
            name = profile_data.get('name', f'Profile-{profile_id[:8]}')
            status = profile_data.get('status', 'unknown')
            
            # Parse proxy configuration
            proxy = None
            proxy_data = profile_data.get('proxy')
            if proxy_data and proxy_data.get('mode') != 'none':
                proxy = ProxyConfig(
                    host=proxy_data.get('host', ''),
                    port=int(proxy_data.get('port', 0)),
                    username=proxy_data.get('username'),
                    password=proxy_data.get('password'),
                    proxy_type=proxy_data.get('mode', 'http').lower()
                )
            
            # Parse fingerprint
            navigator_data = profile_data.get('navigator', {})
            screen_data = profile_data.get('screen', {})
            webgl_data = profile_data.get('webgl', {})
            
            fingerprint = BrowserFingerprint(
                user_agent=navigator_data.get('userAgent', ''),
                screen_width=int(screen_data.get('width', 1920)),
                screen_height=int(screen_data.get('height', 1080)),
                timezone=profile_data.get('timezone', {}).get('timezone', 'UTC'),
                language=navigator_data.get('language', 'en-US'),
                platform=navigator_data.get('platform', 'Win32'),
                hardware_concurrency=int(navigator_data.get('hardwareConcurrency', 4)),
                webgl_vendor=webgl_data.get('vendor', 'Google Inc.'),
                webgl_renderer=webgl_data.get('renderer', 'ANGLE'),
                plugins=navigator_data.get('plugins', [])
            )
            
            created_at = datetime.now(timezone.utc)
            if 'createdAt' in profile_data:
                try:
                    created_at = datetime.fromisoformat(profile_data['createdAt'].replace('Z', '+00:00'))
                except:
                    pass
            
            return GologinProfileData(
                profile_id=profile_id,
                name=name,
                proxy=proxy,
                fingerprint=fingerprint,
                status=status,
                created_at=created_at
            )
            
        except Exception as e:
            logger.error(f"Error parsing profile data: {e}")
            return None
    
    async def _sync_profiles_to_db(self, profiles: List[GologinProfileData]):
        """Synchronize profiles to database"""
        try:
            session = get_db_session()
            
            for profile in profiles:
                # Check if profile exists
                existing = session.query(GologinProfile).filter(
                    GologinProfile.gologin_id == profile.profile_id
                ).first()
                
                proxy_config = asdict(profile.proxy) if profile.proxy else None
                fingerprint_config = asdict(profile.fingerprint)
                
                if existing:
                    # Update existing profile
                    existing.name = profile.name
                    existing.status = profile.status
                    existing.proxy_config = proxy_config
                    existing.proxy_host = profile.proxy.host if profile.proxy else None
                    existing.proxy_port = profile.proxy.port if profile.proxy else None
                    existing.proxy_type = profile.proxy.proxy_type if profile.proxy else None
                    existing.fingerprint = fingerprint_config
                    existing.user_agent = profile.fingerprint.user_agent
                    existing.screen_width = profile.fingerprint.screen_width
                    existing.screen_height = profile.fingerprint.screen_height
                    existing.timezone = profile.fingerprint.timezone
                    existing.language = profile.fingerprint.language
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    # Create new profile
                    new_profile = GologinProfile(
                        gologin_id=profile.profile_id,
                        name=profile.name,
                        status=profile.status,
                        proxy_config=proxy_config,
                        proxy_host=profile.proxy.host if profile.proxy else None,
                        proxy_port=profile.proxy.port if profile.proxy else None,
                        proxy_type=profile.proxy.proxy_type if profile.proxy else None,
                        fingerprint=fingerprint_config,
                        user_agent=profile.fingerprint.user_agent,
                        screen_width=profile.fingerprint.screen_width,
                        screen_height=profile.fingerprint.screen_height,
                        timezone=profile.fingerprint.timezone,
                        language=profile.fingerprint.language
                    )
                    session.add(new_profile)
            
            session.commit()
            session.close()
            logger.debug(f"Synchronized {len(profiles)} profiles to database")
            
        except Exception as e:
            logger.error(f"Failed to sync profiles to database: {e}")
            session.rollback()
            session.close()
    
    async def get_profile_by_id(self, profile_id: str) -> Optional[GologinProfileData]:
        """Get specific profile by ID"""
        # Check cache first
        if profile_id in self._profile_cache:
            return self._profile_cache[profile_id]
        
        # Fetch from API
        try:
            response = await self._make_request('GET', f'/profile/{profile_id}')
            profile_data = response.get('data')
            
            if profile_data:
                parsed_profile = await self._parse_profile(profile_data)
                if parsed_profile:
                    self._profile_cache[profile_id] = parsed_profile
                    return parsed_profile
            
        except Exception as e:
            logger.error(f"Failed to fetch profile {profile_id}: {e}")
        
        return None
    
    async def get_available_profiles(self) -> List[GologinProfileData]:
        """Get only available profiles"""
        all_profiles = await self.get_profiles()
        return [p for p in all_profiles if p.is_available()]
    
    async def mark_profile_in_use(self, profile_id: str):
        """Mark profile as in use in database"""
        try:
            session = get_db_session()
            profile = session.query(GologinProfile).filter(
                GologinProfile.gologin_id == profile_id
            ).first()
            
            if profile:
                profile.status = "in_use"
                profile.last_used = datetime.now(timezone.utc)
                session.commit()
                logger.debug(f"Marked profile {profile_id} as in use")
            
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to mark profile {profile_id} as in use: {e}")
            session.rollback()
            session.close()
    
    async def mark_profile_available(self, profile_id: str):
        """Mark profile as available in database"""
        try:
            session = get_db_session()
            profile = session.query(GologinProfile).filter(
                GologinProfile.gologin_id == profile_id
            ).first()
            
            if profile:
                profile.status = "available"
                session.commit()
                logger.debug(f"Marked profile {profile_id} as available")
            
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to mark profile {profile_id} as available: {e}")
            session.rollback()
            session.close()
    
    async def get_profile_statistics(self) -> Dict[str, Any]:
        """Get profile usage statistics"""
        try:
            session = get_db_session()
            
            total_profiles = session.query(GologinProfile).count()
            available_profiles = session.query(GologinProfile).filter(
                GologinProfile.status == "available"
            ).count()
            in_use_profiles = session.query(GologinProfile).filter(
                GologinProfile.status == "in_use"
            ).count()
            
            session.close()
            
            return {
                'total_profiles': total_profiles,
                'available_profiles': available_profiles,
                'in_use_profiles': in_use_profiles,
                'disabled_profiles': total_profiles - available_profiles - in_use_profiles,
                'cache_size': len(self._profile_cache),
                'cache_valid': self._is_cache_valid()
            }
            
        except Exception as e:
            logger.error(f"Failed to get profile statistics: {e}")
            return {}


# Global Gologin manager instance
_gologin_manager: Optional[GologinAPIManager] = None


async def get_gologin_manager() -> GologinAPIManager:
    """Get global Gologin manager instance"""
    global _gologin_manager
    if _gologin_manager is None:
        _gologin_manager = GologinAPIManager()
        # Test connection on first use
        await _gologin_manager.test_connection()
    return _gologin_manager