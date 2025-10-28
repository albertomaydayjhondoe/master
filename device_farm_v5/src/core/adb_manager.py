"""
Device Farm v5 - ADB Device Manager
Manages Android devices connected via ADB with proxy configuration
"""
import asyncio
import subprocess
import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from loguru import logger
import psutil

from ..config_manager import get_config
from ..core.models import get_db_session, Device


@dataclass
class DeviceInfo:
    """Android device information"""
    serial: str
    model: str
    android_version: str
    screen_resolution: str
    status: str
    battery_level: Optional[int] = None
    wifi_ip: Optional[str] = None
    
    def __post_init__(self):
        """Clean up device info after initialization"""
        # Clean serial (remove transport info)
        if ':' in self.serial and not self.serial.startswith('emulator'):
            self.serial = self.serial.split(':')[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'serial': self.serial,
            'model': self.model,
            'android_version': self.android_version,
            'screen_resolution': self.screen_resolution,
            'status': self.status,
            'battery_level': self.battery_level,
            'wifi_ip': self.wifi_ip
        }


@dataclass
class ProxySettings:
    """Proxy settings for Android device"""
    host: str
    port: int
    enabled: bool = True
    
    def to_android_format(self) -> str:
        """Convert to Android settings format"""
        if self.enabled and self.host and self.port:
            return f"{self.host}:{self.port}"
        return ""


class ADBError(Exception):
    """ADB related errors"""
    pass


class ADBDeviceManager:
    """Manager for ADB devices with proxy configuration"""
    
    def __init__(self):
        self.config = get_config()
        self.adb_path = self.config.adb.adb_path
        self.connection_timeout = self.config.adb.connection_timeout
        self.command_timeout = self.config.adb.command_timeout
        self.max_retries = self.config.adb.max_retries
        
        # Device registry
        self._devices: Dict[str, DeviceInfo] = {}
        self._device_proxies: Dict[str, ProxySettings] = {}
        self._last_scan: Optional[datetime] = None
        
        logger.info("ADB Device Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize ADB and verify connection"""
        try:
            # Check if ADB binary exists
            if not Path(self.adb_path).exists():
                logger.error(f"ADB binary not found at {self.adb_path}")
                return False
            
            # Start ADB server
            await self._run_adb_command(["start-server"])
            
            # Initial device scan
            await self.scan_devices()
            
            logger.info("ADB Device Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ADB Device Manager: {e}")
            return False
    
    async def _run_adb_command(self, args: List[str], device_serial: Optional[str] = None) -> Tuple[str, str]:
        """Run ADB command with timeout and error handling"""
        cmd = [self.adb_path]
        
        if device_serial:
            cmd.extend(['-s', device_serial])
        
        cmd.extend(args)
        
        try:
            logger.debug(f"Running ADB command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.command_timeout
                )
                
                stdout_str = stdout.decode('utf-8', errors='ignore').strip()
                stderr_str = stderr.decode('utf-8', errors='ignore').strip()
                
                if process.returncode != 0 and stderr_str:
                    logger.debug(f"ADB command returned {process.returncode}: {stderr_str}")
                
                return stdout_str, stderr_str
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise ADBError(f"ADB command timed out after {self.command_timeout}s")
                
        except Exception as e:
            logger.error(f"Error running ADB command {' '.join(cmd)}: {e}")
            raise ADBError(f"Failed to run ADB command: {e}")
    
    async def scan_devices(self) -> List[DeviceInfo]:
        """Scan for connected Android devices"""
        try:
            logger.info("Scanning for Android devices...")
            
            # Get device list
            stdout, stderr = await self._run_adb_command(['devices', '-l'])
            
            if not stdout:
                logger.warning("No devices found")
                return []
            
            devices = []
            lines = stdout.split('\n')[1:]  # Skip header line
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('*'):
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                serial = parts[0]
                status = parts[1]
                
                if status == 'device':
                    # Get detailed device info
                    device_info = await self._get_device_info(serial)
                    if device_info:
                        devices.append(device_info)
                        self._devices[serial] = device_info
                        logger.info(f"Found device: {serial} ({device_info.model})")
                
            self._last_scan = datetime.now(timezone.utc)
            
            # Update database
            await self._sync_devices_to_db(devices)
            
            logger.info(f"Scan completed: {len(devices)} devices found")
            return devices
            
        except Exception as e:
            logger.error(f"Device scan failed: {e}")
            return []
    
    async def _get_device_info(self, serial: str) -> Optional[DeviceInfo]:
        """Get detailed information about a device"""
        try:
            # Get device properties
            model = await self._get_device_property(serial, 'ro.product.model')
            android_version = await self._get_device_property(serial, 'ro.build.version.release')
            
            # Get screen resolution
            resolution = await self._get_screen_resolution(serial)
            
            # Get battery level
            battery_level = await self._get_battery_level(serial)
            
            # Get WiFi IP
            wifi_ip = await self._get_wifi_ip(serial)
            
            return DeviceInfo(
                serial=serial,
                model=model or 'Unknown',
                android_version=android_version or 'Unknown',
                screen_resolution=resolution or 'Unknown',
                status='online',
                battery_level=battery_level,
                wifi_ip=wifi_ip
            )
            
        except Exception as e:
            logger.error(f"Failed to get info for device {serial}: {e}")
            return None
    
    async def _get_device_property(self, serial: str, property_name: str) -> Optional[str]:
        """Get device property via getprop"""
        try:
            stdout, _ = await self._run_adb_command(['shell', 'getprop', property_name], serial)
            return stdout.strip() if stdout else None
        except:
            return None
    
    async def _get_screen_resolution(self, serial: str) -> Optional[str]:
        """Get device screen resolution"""
        try:
            stdout, _ = await self._run_adb_command(['shell', 'wm', 'size'], serial)
            if stdout and 'Physical size:' in stdout:
                resolution = stdout.split('Physical size:')[1].strip()
                return resolution
            return None
        except:
            return None
    
    async def _get_battery_level(self, serial: str) -> Optional[int]:
        """Get device battery level"""
        try:
            stdout, _ = await self._run_adb_command(
                ['shell', 'dumpsys', 'battery', '|', 'grep', 'level'], 
                serial
            )
            if stdout:
                match = re.search(r'level: (\d+)', stdout)
                if match:
                    return int(match.group(1))
            return None
        except:
            return None
    
    async def _get_wifi_ip(self, serial: str) -> Optional[str]:
        """Get device WiFi IP address"""
        try:
            stdout, _ = await self._run_adb_command(
                ['shell', 'ip', 'route', '|', 'grep', 'wlan0'], 
                serial
            )
            if stdout:
                # Extract IP from route output
                lines = stdout.split('\n')
                for line in lines:
                    if 'src' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'src' and i + 1 < len(parts):
                                return parts[i + 1]
            return None
        except:
            return None
    
    async def configure_proxy(self, serial: str, proxy_host: str, proxy_port: int) -> bool:
        """Configure HTTP proxy on Android device"""
        try:
            logger.info(f"Configuring proxy {proxy_host}:{proxy_port} on device {serial}")
            
            proxy_settings = ProxySettings(
                host=proxy_host,
                port=proxy_port,
                enabled=True
            )
            
            # Set global HTTP proxy
            proxy_string = proxy_settings.to_android_format()
            
            # Use settings command to configure proxy
            stdout, stderr = await self._run_adb_command([
                'shell', 'settings', 'put', 'global', 'http_proxy', proxy_string
            ], serial)
            
            if stderr:
                logger.warning(f"Proxy configuration warning on {serial}: {stderr}")
            
            # Verify proxy was set
            verification_success = await self._verify_proxy(serial, proxy_host, proxy_port)
            
            if verification_success:
                self._device_proxies[serial] = proxy_settings
                logger.info(f"Proxy configured successfully on device {serial}")
                return True
            else:
                logger.error(f"Proxy verification failed on device {serial}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to configure proxy on device {serial}: {e}")
            return False
    
    async def _verify_proxy(self, serial: str, proxy_host: str, proxy_port: int) -> bool:
        """Verify proxy configuration by testing connectivity"""
        try:
            # Get current proxy setting
            stdout, _ = await self._run_adb_command([
                'shell', 'settings', 'get', 'global', 'http_proxy'
            ], serial)
            
            expected = f"{proxy_host}:{proxy_port}"
            current = stdout.strip()
            
            if current == expected:
                logger.debug(f"Proxy setting verified: {current}")
                
                # Optional: Test actual connectivity through proxy
                test_url = self.config.raw_config.get('adb', {}).get('proxy', {}).get('test_url', '')
                if test_url:
                    return await self._test_proxy_connectivity(serial, test_url)
                
                return True
            else:
                logger.warning(f"Proxy mismatch - Expected: {expected}, Got: {current}")
                return False
                
        except Exception as e:
            logger.error(f"Proxy verification failed on device {serial}: {e}")
            return False
    
    async def _test_proxy_connectivity(self, serial: str, test_url: str) -> bool:
        """Test internet connectivity through configured proxy"""
        try:
            # Use curl or wget to test connectivity
            stdout, stderr = await self._run_adb_command([
                'shell', 'curl', '-s', '--max-time', '10', test_url
            ], serial)
            
            if stdout and not stderr:
                logger.debug(f"Proxy connectivity test passed for device {serial}")
                return True
            else:
                logger.debug(f"Proxy connectivity test failed for device {serial}: {stderr}")
                return False
                
        except Exception as e:
            logger.debug(f"Proxy connectivity test error for device {serial}: {e}")
            # Don't fail proxy configuration just because connectivity test failed
            return True
    
    async def disable_proxy(self, serial: str) -> bool:
        """Disable proxy on Android device"""
        try:
            logger.info(f"Disabling proxy on device {serial}")
            
            # Clear proxy setting
            stdout, stderr = await self._run_adb_command([
                'shell', 'settings', 'delete', 'global', 'http_proxy'
            ], serial)
            
            if serial in self._device_proxies:
                del self._device_proxies[serial]
            
            logger.info(f"Proxy disabled on device {serial}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable proxy on device {serial}: {e}")
            return False
    
    async def get_device_status(self, serial: str) -> str:
        """Get current status of a device"""
        try:
            stdout, _ = await self._run_adb_command(['get-state'], serial)
            return stdout.strip() if stdout else 'unknown'
        except:
            return 'offline'
    
    async def reboot_device(self, serial: str) -> bool:
        """Reboot Android device"""
        try:
            logger.info(f"Rebooting device {serial}")
            await self._run_adb_command(['reboot'], serial)
            
            # Wait for device to come back online
            await asyncio.sleep(5)
            
            # Wait for device to be ready
            for _ in range(30):  # Wait up to 5 minutes
                status = await self.get_device_status(serial)
                if status == 'device':
                    logger.info(f"Device {serial} is back online after reboot")
                    return True
                await asyncio.sleep(10)
            
            logger.warning(f"Device {serial} did not come back online after reboot")
            return False
            
        except Exception as e:
            logger.error(f"Failed to reboot device {serial}: {e}")
            return False
    
    async def install_apk(self, serial: str, apk_path: str) -> bool:
        """Install APK on device"""
        try:
            logger.info(f"Installing APK {apk_path} on device {serial}")
            
            if not Path(apk_path).exists():
                logger.error(f"APK file not found: {apk_path}")
                return False
            
            stdout, stderr = await self._run_adb_command(['install', '-r', apk_path], serial)
            
            if 'Success' in stdout:
                logger.info(f"APK installed successfully on device {serial}")
                return True
            else:
                logger.error(f"APK installation failed on device {serial}: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install APK on device {serial}: {e}")
            return False
    
    async def get_installed_packages(self, serial: str) -> List[str]:
        """Get list of installed packages on device"""
        try:
            stdout, _ = await self._run_adb_command(['shell', 'pm', 'list', 'packages'], serial)
            
            packages = []
            for line in stdout.split('\n'):
                if line.startswith('package:'):
                    package = line.replace('package:', '').strip()
                    packages.append(package)
            
            return packages
            
        except Exception as e:
            logger.error(f"Failed to get packages for device {serial}: {e}")
            return []
    
    async def _sync_devices_to_db(self, devices: List[DeviceInfo]):
        """Synchronize devices to database"""
        try:
            session = get_db_session()
            
            for device_info in devices:
                # Check if device exists
                existing = session.query(Device).filter(
                    Device.serial == device_info.serial
                ).first()
                
                if existing:
                    # Update existing device
                    existing.model = device_info.model
                    existing.android_version = device_info.android_version
                    existing.screen_resolution = device_info.screen_resolution
                    existing.status = device_info.status
                    existing.last_seen = datetime.now(timezone.utc)
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    # Create new device
                    new_device = Device(
                        serial=device_info.serial,
                        name=f"{device_info.model}-{device_info.serial[:8]}",
                        model=device_info.model,
                        android_version=device_info.android_version,
                        screen_resolution=device_info.screen_resolution,
                        status=device_info.status
                    )
                    session.add(new_device)
            
            session.commit()
            session.close()
            logger.debug(f"Synchronized {len(devices)} devices to database")
            
        except Exception as e:
            logger.error(f"Failed to sync devices to database: {e}")
            session.rollback()
            session.close()
    
    async def get_device_statistics(self) -> Dict[str, Any]:
        """Get device statistics"""
        try:
            session = get_db_session()
            
            total_devices = session.query(Device).count()
            online_devices = session.query(Device).filter(Device.status == 'online').count()
            busy_devices = session.query(Device).filter(Device.status == 'busy').count()
            offline_devices = session.query(Device).filter(Device.status == 'offline').count()
            
            session.close()
            
            return {
                'total_devices': total_devices,
                'online_devices': online_devices,
                'busy_devices': busy_devices,
                'offline_devices': offline_devices,
                'detected_devices': len(self._devices),
                'configured_proxies': len(self._device_proxies),
                'last_scan': self._last_scan.isoformat() if self._last_scan else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get device statistics: {e}")
            return {}
    
    def get_detected_devices(self) -> Dict[str, DeviceInfo]:
        """Get currently detected devices"""
        return self._devices.copy()
    
    def get_device_proxy(self, serial: str) -> Optional[ProxySettings]:
        """Get proxy settings for a device"""
        return self._device_proxies.get(serial)


# Global ADB manager instance
_adb_manager: Optional[ADBDeviceManager] = None


async def get_adb_manager() -> ADBDeviceManager:
    """Get global ADB manager instance"""
    global _adb_manager
    if _adb_manager is None:
        _adb_manager = ADBDeviceManager()
        await _adb_manager.initialize()
    return _adb_manager