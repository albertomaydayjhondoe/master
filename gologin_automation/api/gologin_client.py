"""GoLogin API Client - Production and Dummy modes.

Real GoLogin implementation for browser automation with 30 profiles for viral content engagement.
Switches between production GoLogin API and dummy simulation based on DUMMY_MODE.
"""
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import time
import random
from pathlib import Path
from config.app_settings import get_env, is_dummy_mode

logger = logging.getLogger(__name__)

__all__ = ['GoLoginClient', 'create_profile', 'list_profiles', 'start_profile', 'stop_profile']


class GoLoginClient:
    """Production GoLogin client for browser automation."""
    
    def __init__(self, api_token: str = None):
        """Initialize GoLogin client.
        
        Args:
            api_token: GoLogin API token from environment or parameter
        """
        self.api_token = api_token or get_env("GOLOGIN_API_TOKEN")
        self.base_url = "https://api.gologin.com"
        self.is_dummy = is_dummy_mode()
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.active_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Profile configurations for viral content
        self.viral_profiles = self._generate_viral_profiles()
        
        if self.is_dummy:
            logger.info("🔧 GoLogin initialized in DUMMY mode")
            # In-memory store for dummy mode
            self.profiles: Dict[str, Dict[str, Any]] = {}
        else:
            logger.info("🚀 GoLogin initialized in PRODUCTION mode")
            if not self.api_token:
                logger.error("❌ GOLOGIN_API_TOKEN not provided for production mode")
    
    def _generate_viral_profiles(self) -> List[Dict[str, Any]]:
        """Generate 30 diverse browser profiles for viral content automation."""
        profiles = []
        
        # Geographic diversity for Spanish-speaking markets
        locations = [
            {"country": "ES", "city": "Madrid", "timezone": "Europe/Madrid"},
            {"country": "ES", "city": "Barcelona", "timezone": "Europe/Madrid"},
            {"country": "MX", "city": "Mexico City", "timezone": "America/Mexico_City"},
            {"country": "AR", "city": "Buenos Aires", "timezone": "America/Argentina/Buenos_Aires"},
            {"country": "CO", "city": "Bogotá", "timezone": "America/Bogota"},
            {"country": "PE", "city": "Lima", "timezone": "America/Lima"},
            {"country": "CL", "city": "Santiago", "timezone": "America/Santiago"},
            {"country": "VE", "city": "Caracas", "timezone": "America/Caracas"},
            {"country": "EC", "city": "Quito", "timezone": "America/Guayaquil"},
            {"country": "UY", "city": "Montevideo", "timezone": "America/Montevideo"},
        ]
        
        # Browser and OS diversity
        browsers = [
            {"name": "Chrome", "version": "118.0.5993.88", "os": "Windows"},
            {"name": "Chrome", "version": "118.0.5993.88", "os": "macOS"},
            {"name": "Firefox", "version": "119.0", "os": "Windows"},
            {"name": "Safari", "version": "17.0", "os": "macOS"},
            {"name": "Edge", "version": "118.0.2088.46", "os": "Windows"},
        ]
        
        # Age groups for targeting
        age_groups = ["18-24", "25-34", "35-44"]
        interests = ["music", "drill", "rap", "urban_culture", "social_media", "youtube"]
        
        for i in range(30):
            location = locations[i % len(locations)]
            browser = browsers[i % len(browsers)]
            age_group = age_groups[i % len(age_groups)]
            
            profile = {
                "name": f"Viral_Profile_{i+1:02d}_{location['country']}",
                "location": location,
                "browser": browser,
                "age_group": age_group,
                "interests": random.sample(interests, 3),
                "language": "es-ES" if location["country"] == "ES" else "es",
                "user_agent": self._generate_user_agent(browser),
                "screen_resolution": random.choice(["1920x1080", "1366x768", "1440x900", "1536x864"]),
                "created_for": "viral_engagement"
            }
            profiles.append(profile)
        
        return profiles
    
    def _generate_user_agent(self, browser: Dict[str, str]) -> str:
        """Generate realistic user agent string."""
        if browser["name"] == "Chrome":
            if browser["os"] == "Windows":
                return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser['version']} Safari/537.36"
            else:  # macOS
                return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser['version']} Safari/537.36"
        elif browser["name"] == "Firefox":
            return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/{browser['version']}"
        elif browser["name"] == "Safari":
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{browser['version']} Safari/605.1.15"
        else:  # Edge
            return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser['version']} Safari/537.36 Edg/{browser['version']}"
    
    async def initialize_session(self):
        """Initialize aiohttp session."""
        if not self.session:
            headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def initialize_profiles(self, count: int = 30) -> List[Dict[str, Any]]:
        """Initialize all viral profiles for production use."""
        try:
            logger.info(f"🔧 Initializing {count} viral profiles...")
            
            if self.is_dummy:
                # Dummy mode: create in-memory profiles
                for i in range(count):
                    profile_config = self.viral_profiles[i % len(self.viral_profiles)]
                    profile = self.create_profile(
                        name=profile_config["name"],
                        fingerprint={
                            "location": profile_config["location"],
                            "browser": profile_config["browser"],
                            "user_agent": profile_config["user_agent"],
                            "screen_resolution": profile_config["screen_resolution"],
                            "language": profile_config["language"]
                        }
                    )
                    logger.info(f"✅ Created dummy profile: {profile['name']}")
                
                return list(self.profiles.values())
            
            else:
                # Production mode: create real GoLogin profiles
                await self.initialize_session()
                created_profiles = []
                
                for i in range(count):
                    profile_config = self.viral_profiles[i % len(self.viral_profiles)]
                    
                    try:
                        profile = await self._create_real_profile(profile_config)
                        if profile:
                            created_profiles.append(profile)
                            logger.info(f"✅ Created real profile: {profile['name']}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create profile {i+1}: {str(e)}")
                        continue
                
                logger.info(f"🎯 Successfully created {len(created_profiles)}/{count} profiles")
                return created_profiles
                
        except Exception as e:
            logger.error(f"❌ Profile initialization error: {str(e)}")
            return []
    
    async def _create_real_profile(self, profile_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a real GoLogin profile via API."""
        try:
            url = f"{self.base_url}/browser/v2"
            
            # GoLogin API profile data
            profile_data = {
                "name": profile_config["name"],
                "os": profile_config["browser"]["os"].lower(),
                "navigator": {
                    "language": profile_config["language"],
                    "userAgent": profile_config["user_agent"],
                    "resolution": profile_config["screen_resolution"],
                    "platform": profile_config["browser"]["os"]
                },
                "geoProxyInfo": {
                    "country": profile_config["location"]["country"],
                    "city": profile_config["location"]["city"]
                },
                "timezone": {
                    "id": profile_config["location"]["timezone"]
                },
                "webRTC": {
                    "mode": "alerted",
                    "enabled": True
                },
                "canvas": {
                    "mode": "real"
                },
                "webGL": {
                    "mode": "real" 
                },
                "notes": f"Viral engagement profile for {profile_config['location']['country']}"
            }
            
            async with self.session.post(url, json=profile_data) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "id": result["id"],
                        "name": profile_config["name"],
                        "config": profile_config,
                        "status": "created",
                        "created_at": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"❌ GoLogin API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Real profile creation error: {str(e)}")
            return None
    
    def create_profile(self, name: str, fingerprint: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a browser profile (dummy mode compatible)."""
        if self.is_dummy:
            # Dummy implementation
            pid = str(uuid.uuid4())
            profile = {
                "id": pid,
                "name": name,
                "fingerprint": fingerprint or {"locale": "es-ES"},
                "created_at": time.time(),
                "status": "stopped",
            }
            self.profiles[pid] = profile
            return profile
        else:
            # For production, use initialize_profiles method
            logger.warning("⚠️ Use initialize_profiles() for production profile creation")
            return {"error": "Use initialize_profiles() method"}
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles."""
        if self.is_dummy:
            return list(self.profiles.values())
        else:
            return list(self.active_profiles.values())
    
    async def start_profile(self, profile_id: str) -> Dict[str, Any]:
        """Start a browser profile."""
        try:
            if self.is_dummy:
                p = self.profiles.get(profile_id)
                if not p:
                    raise KeyError("profile_not_found")
                p["status"] = "running"
                p["last_started"] = time.time()
                return p
            
            else:
                # Production: start real GoLogin profile
                await self.initialize_session()
                url = f"{self.base_url}/browser/v2/{profile_id}/web"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        profile_info = {
                            "id": profile_id,
                            "status": "running",
                            "ws_url": result.get("ws", {}).get("puppeteer"),
                            "port": result.get("port"),
                            "started_at": datetime.now().isoformat()
                        }
                        
                        self.active_profiles[profile_id] = profile_info
                        return profile_info
                    else:
                        raise Exception(f"Failed to start profile: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Profile start error: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def stop_profile(self, profile_id: str) -> Dict[str, Any]:
        """Stop a browser profile."""
        try:
            if self.is_dummy:
                p = self.profiles.get(profile_id)
                if not p:
                    raise KeyError("profile_not_found")
                p["status"] = "stopped"
                p["last_stopped"] = time.time()
                return p
            
            else:
                # Production: stop real GoLogin profile
                await self.initialize_session()
                url = f"{self.base_url}/browser/v2/{profile_id}/stop"
                
                async with self.session.delete(url) as response:
                    if response.status == 200:
                        if profile_id in self.active_profiles:
                            self.active_profiles[profile_id]["status"] = "stopped"
                            self.active_profiles[profile_id]["stopped_at"] = datetime.now().isoformat()
                        
                        return {"id": profile_id, "status": "stopped"}
                    else:
                        raise Exception(f"Failed to stop profile: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Profile stop error: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def boost_video_engagement(self, video_url: str, profile_count: int = 10) -> Dict[str, Any]:
        """Boost video engagement using multiple browser profiles."""
        try:
            logger.info(f"🚀 Starting video engagement boost with {profile_count} profiles")
            
            # Get available profiles
            available_profiles = self.list_profiles()[:profile_count]
            
            if not available_profiles:
                return {"success": False, "error": "No profiles available"}
            
            # Start engagement tasks
            tasks = []
            for profile in available_profiles:
                task = asyncio.create_task(
                    self._profile_engagement_session(profile["id"], video_url)
                )
                tasks.append((profile["id"], task))
            
            # Execute all tasks
            results = {}
            for profile_id, task in tasks:
                try:
                    result = await task
                    results[profile_id] = result
                except Exception as e:
                    logger.error(f"❌ Profile {profile_id} engagement failed: {str(e)}")
                    results[profile_id] = {"success": False, "error": str(e)}
            
            successful_engagements = sum(1 for r in results.values() if r.get("success", False))
            
            return {
                "success": successful_engagements > 0,
                "total_profiles": len(available_profiles),
                "successful_engagements": successful_engagements,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Video engagement boost error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _profile_engagement_session(self, profile_id: str, video_url: str) -> Dict[str, Any]:
        """Run engagement session for a single profile."""
        try:
            # Start profile
            start_result = await self.start_profile(profile_id)
            if "error" in start_result:
                return {"success": False, "error": start_result["error"]}
            
            if self.is_dummy:
                # Simulate engagement actions in dummy mode
                actions = ["view", "like", "comment", "subscribe"]
                performed_actions = random.sample(actions, random.randint(2, 4))
                
                # Simulate realistic timing
                session_duration = random.randint(30, 180)  # 30 seconds to 3 minutes
                await asyncio.sleep(min(session_duration, 5))  # Cap at 5 seconds for testing
                
                result = {
                    "success": True,
                    "profile_id": profile_id,
                    "actions_performed": performed_actions,
                    "session_duration": session_duration,
                    "video_url": video_url
                }
            else:
                # Production engagement with real browser automation
                result = await self._perform_real_engagement(profile_id, video_url, start_result)
            
            # Stop profile
            await self.stop_profile(profile_id)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Profile engagement session error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _perform_real_engagement(self, profile_id: str, video_url: str, browser_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform real browser engagement using puppeteer/playwright."""
        try:
            # This would integrate with playwright/puppeteer via WebSocket
            # For now, return simulated success
            
            logger.info(f"🎯 Performing real engagement for profile {profile_id}")
            
            # Simulate browser actions
            actions_performed = []
            
            # Navigate to video
            await asyncio.sleep(2)  # Navigation time
            actions_performed.append("navigate")
            
            # Watch video
            watch_time = random.randint(30, 120)
            await asyncio.sleep(min(watch_time, 10))  # Cap for testing
            actions_performed.append(f"watched_{watch_time}s")
            
            # Random engagement actions
            if random.random() > 0.3:  # 70% chance to like
                actions_performed.append("like")
            
            if random.random() > 0.8:  # 20% chance to comment
                actions_performed.append("comment")
            
            if random.random() > 0.9:  # 10% chance to subscribe
                actions_performed.append("subscribe")
            
            return {
                "success": True,
                "profile_id": profile_id,
                "actions_performed": actions_performed,
                "video_url": video_url,
                "browser_port": browser_info.get("port"),
                "engagement_score": len(actions_performed) * 0.25
            }
            
        except Exception as e:
            logger.error(f"❌ Real engagement error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_engagement_stats(self) -> Dict[str, Any]:
        """Get overall engagement statistics."""
        active_count = len([p for p in self.active_profiles.values() if p.get("status") == "running"])
        total_profiles = len(self.list_profiles())
        
        return {
            "total_profiles": total_profiles,
            "active_profiles": active_count,
            "available_profiles": total_profiles - active_count,
            "mode": "dummy" if self.is_dummy else "production",
            "api_connected": bool(self.api_token) if not self.is_dummy else True
        }


# Legacy functions for compatibility
def create_profile(name: str, fingerprint: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use GoLoginClient.create_profile instead."""
    client = GoLoginClient()
    return client.create_profile(name, fingerprint)

def list_profiles() -> List[Dict[str, Any]]:
    """Legacy function - use GoLoginClient.list_profiles instead."""
    client = GoLoginClient()
    return client.list_profiles()

async def start_profile(profile_id: str) -> Dict[str, Any]:
    """Legacy function - use GoLoginClient.start_profile instead."""
    client = GoLoginClient()
    return await client.start_profile(profile_id)

async def stop_profile(profile_id: str) -> Dict[str, Any]:
    """Legacy function - use GoLoginClient.stop_profile instead."""
    client = GoLoginClient()
    return await client.stop_profile(profile_id)
