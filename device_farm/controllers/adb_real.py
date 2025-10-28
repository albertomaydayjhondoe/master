"""Real ADB Controller for production device farm management.

This module provides production implementation for controlling physical Android 
devices via ADB for TikTok automation and viral content engagement.
"""
import subprocess
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DeviceInfo:
    """Information about a connected Android device."""
    device_id: str
    model: str
    android_version: str
    status: str
    screen_resolution: str
    battery_level: int
    is_available: bool = True
    last_action: Optional[datetime] = None


class ADBControllerReal:
    """Production ADB controller for managing physical Android devices."""
    
    def __init__(self):
        """Initialize ADB controller with device discovery."""
        self.devices: Dict[str, DeviceInfo] = {}
        self.active_sessions = {}
        self.tiktok_package = "com.zhiliaoapp.musically"
        
        # Human-like interaction patterns
        self.interaction_patterns = {
            "scroll_speed": {"min": 0.5, "max": 2.0},
            "tap_delay": {"min": 0.3, "max": 1.5},
            "session_duration": {"min": 300, "max": 1800},  # 5-30 minutes
            "pause_between_actions": {"min": 2, "max": 8}
        }
        
        logger.info("🤖 Real ADB Controller initialized")
    
    async def discover_devices(self) -> List[DeviceInfo]:
        """Discover and connect to available Android devices."""
        try:
            # Get list of connected devices
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"❌ ADB devices command failed: {result.stderr}")
                return []
            
            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if '\tdevice' in line:
                    device_id = line.split('\t')[0]
                    device_info = await self._get_device_info(device_id)
                    if device_info:
                        devices.append(device_info)
                        self.devices[device_id] = device_info
            
            logger.info(f"📱 Discovered {len(devices)} devices")
            return devices
            
        except subprocess.TimeoutExpired:
            logger.error("❌ ADB device discovery timed out")
            return []
        except Exception as e:
            logger.error(f"❌ Device discovery error: {str(e)}")
            return []
    
    async def _get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Get detailed information about a specific device."""
        try:
            # Get device model
            model_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
                capture_output=True, text=True, timeout=5
            )
            model = model_result.stdout.strip() if model_result.returncode == 0 else "Unknown"
            
            # Get Android version
            version_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop", "ro.build.version.release"],
                capture_output=True, text=True, timeout=5
            )
            version = version_result.stdout.strip() if version_result.returncode == 0 else "Unknown"
            
            # Get screen resolution
            resolution_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "wm", "size"],
                capture_output=True, text=True, timeout=5
            )
            resolution = "Unknown"
            if resolution_result.returncode == 0:
                resolution_line = resolution_result.stdout.strip()
                if "Physical size:" in resolution_line:
                    resolution = resolution_line.split("Physical size: ")[1]
            
            # Get battery level
            battery_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "dumpsys", "battery"],
                capture_output=True, text=True, timeout=5
            )
            battery_level = 50  # Default
            if battery_result.returncode == 0:
                for line in battery_result.stdout.split('\n'):
                    if 'level:' in line:
                        try:
                            battery_level = int(line.split(':')[1].strip())
                            break
                        except (ValueError, IndexError):
                            pass
            
            return DeviceInfo(
                device_id=device_id,
                model=model,
                android_version=version,
                status="connected",
                screen_resolution=resolution,
                battery_level=battery_level,
                is_available=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting device info for {device_id}: {str(e)}")
            return None
    
    async def install_tiktok(self, device_id: str) -> bool:
        """Install TikTok app on device if not present."""
        try:
            # Check if TikTok is already installed
            check_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "pm", "list", "packages", self.tiktok_package],
                capture_output=True, text=True, timeout=10
            )
            
            if self.tiktok_package in check_result.stdout:
                logger.info(f"✅ TikTok already installed on {device_id}")
                return True
            
            # Download and install TikTok APK
            apk_path = "data/apks/tiktok.apk"
            if not Path(apk_path).exists():
                logger.warning(f"⚠️ TikTok APK not found at {apk_path}")
                return False
            
            install_result = subprocess.run(
                ["adb", "-s", device_id, "install", apk_path],
                capture_output=True, text=True, timeout=60
            )
            
            if install_result.returncode == 0:
                logger.info(f"✅ TikTok installed on {device_id}")
                return True
            else:
                logger.error(f"❌ TikTok installation failed on {device_id}: {install_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ TikTok installation error on {device_id}: {str(e)}")
            return False
    
    async def launch_tiktok(self, device_id: str) -> bool:
        """Launch TikTok app on device."""
        try:
            launch_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "am", "start", 
                 "-n", f"{self.tiktok_package}/.MainActivity"],
                capture_output=True, text=True, timeout=15
            )
            
            if launch_result.returncode == 0:
                logger.info(f"📱 TikTok launched on {device_id}")
                await asyncio.sleep(3)  # Wait for app to load
                return True
            else:
                logger.error(f"❌ TikTok launch failed on {device_id}: {launch_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ TikTok launch error on {device_id}: {str(e)}")
            return False
    
    async def navigate_to_video(self, device_id: str, video_url: str) -> bool:
        """Navigate to specific video URL in TikTok."""
        try:
            # Extract video ID from URL (simplified)
            video_id = video_url.split('/')[-1] if '/' in video_url else video_url
            
            # Use intent to open specific video
            intent_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "am", "start",
                 "-a", "android.intent.action.VIEW",
                 "-d", video_url],
                capture_output=True, text=True, timeout=10
            )
            
            if intent_result.returncode == 0:
                logger.info(f"🎯 Navigated to video on {device_id}")
                await asyncio.sleep(2)
                return True
            else:
                logger.error(f"❌ Navigation failed on {device_id}: {intent_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Navigation error on {device_id}: {str(e)}")
            return False
    
    async def perform_engagement_actions(self, device_id: str, actions: List[str]) -> Dict[str, bool]:
        """Perform engagement actions (like, comment, share) on current video."""
        results = {}
        
        try:
            for action in actions:
                success = await self._perform_single_action(device_id, action)
                results[action] = success
                
                # Human-like delay between actions
                delay = random.uniform(
                    self.interaction_patterns["pause_between_actions"]["min"],
                    self.interaction_patterns["pause_between_actions"]["max"]
                )
                await asyncio.sleep(delay)
            
            logger.info(f"🤝 Engagement actions completed on {device_id}: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Engagement actions error on {device_id}: {str(e)}")
            return {action: False for action in actions}
    
    async def _perform_single_action(self, device_id: str, action: str) -> bool:
        """Perform a single engagement action."""
        try:
            if action == "like":
                # Tap like button (right side of screen)
                return await self._tap_coordinate(device_id, 0.9, 0.5)
            
            elif action == "comment":
                # Tap comment button
                success = await self._tap_coordinate(device_id, 0.9, 0.6)
                if success:
                    # Add a comment
                    await asyncio.sleep(1)
                    await self._type_text(device_id, "🔥🔥🔥")
                    await asyncio.sleep(0.5)
                    # Tap send button
                    await self._tap_coordinate(device_id, 0.9, 0.9)
                return success
            
            elif action == "share":
                # Tap share button
                return await self._tap_coordinate(device_id, 0.9, 0.7)
            
            elif action == "follow":
                # Tap follow button (usually top right)
                return await self._tap_coordinate(device_id, 0.9, 0.2)
            
            elif action == "scroll":
                # Scroll to next video
                return await self._swipe(device_id, 0.5, 0.7, 0.5, 0.3)
            
            else:
                logger.warning(f"⚠️ Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Action '{action}' failed on {device_id}: {str(e)}")
            return False
    
    async def _tap_coordinate(self, device_id: str, x_ratio: float, y_ratio: float) -> bool:
        """Tap at relative coordinates (0.0-1.0)."""
        try:
            # Get screen resolution first
            device_info = self.devices.get(device_id)
            if not device_info or device_info.screen_resolution == "Unknown":
                # Default resolution assumption
                screen_x, screen_y = 1080, 1920
            else:
                resolution = device_info.screen_resolution
                try:
                    screen_x, screen_y = map(int, resolution.split('x'))
                except ValueError:
                    screen_x, screen_y = 1080, 1920
            
            # Calculate actual coordinates
            x = int(screen_x * x_ratio)
            y = int(screen_y * y_ratio)
            
            # Add small random offset for more human-like behavior
            x += random.randint(-10, 10)
            y += random.randint(-10, 10)
            
            # Perform tap
            tap_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "input", "tap", str(x), str(y)],
                capture_output=True, text=True, timeout=5
            )
            
            return tap_result.returncode == 0
            
        except Exception as e:
            logger.error(f"❌ Tap coordinate error on {device_id}: {str(e)}")
            return False
    
    async def _swipe(self, device_id: str, x1_ratio: float, y1_ratio: float, 
                    x2_ratio: float, y2_ratio: float) -> bool:
        """Perform swipe gesture."""
        try:
            device_info = self.devices.get(device_id)
            if not device_info or device_info.screen_resolution == "Unknown":
                screen_x, screen_y = 1080, 1920
            else:
                resolution = device_info.screen_resolution
                try:
                    screen_x, screen_y = map(int, resolution.split('x'))
                except ValueError:
                    screen_x, screen_y = 1080, 1920
            
            x1, y1 = int(screen_x * x1_ratio), int(screen_y * y1_ratio)
            x2, y2 = int(screen_x * x2_ratio), int(screen_y * y2_ratio)
            
            # Duration for swipe (human-like)
            duration = random.randint(200, 500)
            
            swipe_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "input", "swipe", 
                 str(x1), str(y1), str(x2), str(y2), str(duration)],
                capture_output=True, text=True, timeout=5
            )
            
            return swipe_result.returncode == 0
            
        except Exception as e:
            logger.error(f"❌ Swipe error on {device_id}: {str(e)}")
            return False
    
    async def _type_text(self, device_id: str, text: str) -> bool:
        """Type text on device."""
        try:
            # Escape text for shell
            escaped_text = text.replace(' ', '%s').replace("'", "\\'")
            
            type_result = subprocess.run(
                ["adb", "-s", device_id, "shell", "input", "text", escaped_text],
                capture_output=True, text=True, timeout=5
            )
            
            return type_result.returncode == 0
            
        except Exception as e:
            logger.error(f"❌ Type text error on {device_id}: {str(e)}")
            return False
    
    async def start_viral_boost_session(self, video_url: str, devices: List[str] = None) -> Dict[str, Any]:
        """Start coordinated viral boost session across multiple devices."""
        if not devices:
            devices = list(self.devices.keys())
        
        if not devices:
            logger.error("❌ No devices available for viral boost")
            return {"success": False, "error": "No devices available"}
        
        logger.info(f"🚀 Starting viral boost session with {len(devices)} devices")
        
        session_id = f"viral_boost_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_results = {}
        
        # Start async tasks for each device
        tasks = []
        for device_id in devices:
            task = asyncio.create_task(
                self._device_viral_session(device_id, video_url, session_id)
            )
            tasks.append((device_id, task))
        
        # Wait for all tasks to complete
        for device_id, task in tasks:
            try:
                result = await task
                session_results[device_id] = result
            except Exception as e:
                logger.error(f"❌ Device session failed {device_id}: {str(e)}")
                session_results[device_id] = {"success": False, "error": str(e)}
        
        total_success = sum(1 for r in session_results.values() if r.get("success", False))
        
        logger.info(f"🎯 Viral boost session completed: {total_success}/{len(devices)} devices successful")
        
        return {
            "success": total_success > 0,
            "session_id": session_id,
            "total_devices": len(devices),
            "successful_devices": total_success,
            "results": session_results
        }
    
    async def _device_viral_session(self, device_id: str, video_url: str, session_id: str) -> Dict[str, Any]:
        """Run viral boost session on a single device."""
        try:
            logger.info(f"📱 Starting viral session on {device_id}")
            
            # 1. Launch TikTok
            if not await self.launch_tiktok(device_id):
                return {"success": False, "error": "Failed to launch TikTok"}
            
            # 2. Navigate to target video
            if not await self.navigate_to_video(device_id, video_url):
                return {"success": False, "error": "Failed to navigate to video"}
            
            # 3. Perform engagement actions
            actions = ["like", "comment", "share"]
            if random.random() > 0.7:  # 30% chance to follow
                actions.append("follow")
            
            engagement_results = await self.perform_engagement_actions(device_id, actions)
            
            # 4. Watch video (simulate viewing time)
            watch_time = random.randint(30, 120)  # 30-120 seconds
            await asyncio.sleep(watch_time)
            
            # 5. Scroll to browse more videos (to appear natural)
            for _ in range(random.randint(2, 5)):
                await self._perform_single_action(device_id, "scroll")
                await asyncio.sleep(random.uniform(3, 8))
            
            successful_actions = sum(1 for success in engagement_results.values() if success)
            
            # Update device status
            if device_id in self.devices:
                self.devices[device_id].last_action = datetime.now()
            
            return {
                "success": True,
                "session_id": session_id,
                "device_id": device_id,
                "actions_performed": engagement_results,
                "successful_actions": successful_actions,
                "watch_time": watch_time,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Viral session error on {device_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_device_status(self) -> Dict[str, Any]:
        """Get status of all managed devices."""
        status = {
            "total_devices": len(self.devices),
            "available_devices": sum(1 for d in self.devices.values() if d.is_available),
            "active_sessions": len(self.active_sessions),
            "devices": {}
        }
        
        for device_id, device_info in self.devices.items():
            status["devices"][device_id] = {
                "model": device_info.model,
                "android_version": device_info.android_version,
                "battery_level": device_info.battery_level,
                "is_available": device_info.is_available,
                "last_action": device_info.last_action.isoformat() if device_info.last_action else None,
                "status": device_info.status
            }
        
        return status


# Device Manager wrapper
def get_device_manager() -> ADBControllerReal:
    """Get device manager instance."""
    return ADBControllerReal()