"""
Device Farm v5 - Profile Device Synchronizer
Synchronizes Gologin profiles with Android devices and manages connectivity
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from ..config_manager import get_config
from ..core.models import get_db_session, Device, GologinProfile
from ..core.adb_manager import get_adb_manager
from ..integrations.gologin_manager import get_gologin_manager, GologinProfileData
from ..core.appium_controller import get_appium_controller


@dataclass
class DeviceProfileMapping:
    """Device to profile mapping with sync status"""
    device_serial: str
    profile_id: str
    proxy_host: str
    proxy_port: int
    sync_status: str  # synced, syncing, failed, disconnected
    last_sync: datetime
    sync_attempts: int = 0
    
    def is_synced(self) -> bool:
        """Check if device is properly synced with profile"""
        return self.sync_status == "synced"
    
    def needs_resync(self, max_age_minutes: int = 60) -> bool:
        """Check if mapping needs re-synchronization"""
        if self.sync_status != "synced":
            return True
        
        age = datetime.now(timezone.utc) - self.last_sync
        return age > timedelta(minutes=max_age_minutes)


class ProfileDeviceSynchronizer:
    """Synchronizes Gologin profiles with Android devices"""
    
    def __init__(self):
        self.config = get_config()
        self.max_devices = self.config.max_devices
        
        # Active mappings
        self._mappings: Dict[str, DeviceProfileMapping] = {}
        self._device_locks: Dict[str, asyncio.Lock] = {}
        
        # Synchronization settings
        self.sync_interval = 300  # 5 minutes
        self.max_sync_attempts = 3
        self.proxy_test_timeout = 30
        
        logger.info("Profile Device Synchronizer initialized")
    
    async def initialize(self) -> bool:
        """Initialize synchronizer and load existing mappings"""
        try:
            # Load existing mappings from database
            await self._load_mappings_from_db()
            
            # Start background sync task
            asyncio.create_task(self._background_sync_task())
            
            logger.info("Profile Device Synchronizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ProfileDeviceSynchronizer: {e}")
            return False
    
    async def _load_mappings_from_db(self):
        """Load device-profile mappings from database"""
        try:
            session = get_db_session()
            
            # Get devices with assigned profiles
            devices = session.query(Device).filter(
                Device.assigned_profile.isnot(None)
            ).all()
            
            for device in devices:
                if device.assigned_profile and device.proxy_host and device.proxy_port:
                    mapping = DeviceProfileMapping(
                        device_serial=device.serial,
                        profile_id=device.assigned_profile,
                        proxy_host=device.proxy_host,
                        proxy_port=device.proxy_port,
                        sync_status="unknown",  # Will be verified
                        last_sync=device.updated_at or datetime.now(timezone.utc),
                        sync_attempts=0
                    )
                    
                    self._mappings[device.serial] = mapping
                    self._device_locks[device.serial] = asyncio.Lock()
            
            session.close()
            logger.info(f"Loaded {len(self._mappings)} device-profile mappings from database")
            
        except Exception as e:
            logger.error(f"Failed to load mappings from database: {e}")
    
    async def assign_profile_to_device(self, device_serial: str, profile_id: Optional[str] = None) -> bool:
        """Assign a Gologin profile to a device"""
        try:
            # Get device lock
            if device_serial not in self._device_locks:
                self._device_locks[device_serial] = asyncio.Lock()
            
            async with self._device_locks[device_serial]:
                logger.info(f"Assigning profile to device {device_serial}")
                
                # Get managers
                adb_manager = await get_adb_manager()
                gologin_manager = await get_gologin_manager()
                
                # Check if device is online
                device_status = await adb_manager.get_device_status(device_serial)
                if device_status != "device":
                    logger.error(f"Device {device_serial} is not online: {device_status}")
                    return False
                
                # Get available profile
                if not profile_id:
                    profile_id = await self._select_available_profile()
                
                if not profile_id:
                    logger.error("No available profiles for assignment")
                    return False
                
                # Get profile data
                profile_data = await gologin_manager.get_profile_by_id(profile_id)
                if not profile_data or not profile_data.proxy:
                    logger.error(f"Profile {profile_id} not found or has no proxy")
                    return False
                
                # Configure proxy on device
                proxy_success = await adb_manager.configure_proxy(
                    device_serial,
                    profile_data.proxy.host,
                    profile_data.proxy.port
                )
                
                if not proxy_success:
                    logger.error(f"Failed to configure proxy on device {device_serial}")
                    return False
                
                # Test connectivity
                connectivity_ok = await self._test_device_connectivity(
                    device_serial, profile_data.proxy.host, profile_data.proxy.port
                )
                
                if not connectivity_ok:
                    logger.warning(f"Connectivity test failed for device {device_serial}")
                
                # Create mapping
                mapping = DeviceProfileMapping(
                    device_serial=device_serial,
                    profile_id=profile_id,
                    proxy_host=profile_data.proxy.host,
                    proxy_port=profile_data.proxy.port,
                    sync_status="synced" if connectivity_ok else "proxy_only",
                    last_sync=datetime.now(timezone.utc),
                    sync_attempts=1
                )
                
                self._mappings[device_serial] = mapping
                
                # Update database
                await self._update_device_mapping_in_db(mapping)
                
                # Mark profile as in use
                await gologin_manager.mark_profile_in_use(profile_id)
                
                logger.info(f"Successfully assigned profile {profile_id} to device {device_serial}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to assign profile to device {device_serial}: {e}")
            return False
    
    async def _select_available_profile(self) -> Optional[str]:
        """Select an available Gologin profile"""
        try:
            gologin_manager = await get_gologin_manager()
            available_profiles = await gologin_manager.get_available_profiles()
            
            if not available_profiles:
                return None
            
            # Filter out profiles already assigned
            assigned_profiles = {mapping.profile_id for mapping in self._mappings.values()}
            
            for profile in available_profiles:
                if profile.profile_id not in assigned_profiles:
                    return profile.profile_id
            
            # If all profiles are assigned, try to find the least recently used
            logger.warning("All profiles are assigned, looking for least recently used")
            
            session = get_db_session()
            profile = session.query(GologinProfile).filter(
                GologinProfile.status == "available"
            ).order_by(GologinProfile.last_used.asc()).first()
            
            session.close()
            
            return profile.gologin_id if profile else None
            
        except Exception as e:
            logger.error(f"Failed to select available profile: {e}")
            return None
    
    async def _test_device_connectivity(self, device_serial: str, proxy_host: str, proxy_port: int) -> bool:
        """Test internet connectivity through device proxy"""
        try:
            adb_manager = await get_adb_manager()
            
            # Test URL from config
            test_url = self.config.raw_config.get('adb', {}).get('proxy', {}).get('test_url', 'http://httpbin.org/ip')
            
            # Use curl to test connectivity through proxy
            stdout, stderr = await adb_manager._run_adb_command([
                'shell', 'curl', '-s', '--max-time', str(self.proxy_test_timeout), 
                '--proxy', f'{proxy_host}:{proxy_port}', test_url
            ], device_serial)
            
            if stdout and not stderr:
                logger.debug(f"Connectivity test passed for device {device_serial}")
                return True
            else:
                logger.debug(f"Connectivity test failed for device {device_serial}: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Connectivity test error for device {device_serial}: {e}")
            return False
    
    async def unassign_profile_from_device(self, device_serial: str) -> bool:
        """Remove profile assignment from device"""
        try:
            async with self._device_locks.get(device_serial, asyncio.Lock()):
                mapping = self._mappings.get(device_serial)
                
                if not mapping:
                    logger.debug(f"No profile assigned to device {device_serial}")
                    return True
                
                logger.info(f"Unassigning profile {mapping.profile_id} from device {device_serial}")
                
                # Disable proxy on device
                adb_manager = await get_adb_manager()
                await adb_manager.disable_proxy(device_serial)
                
                # Mark profile as available
                gologin_manager = await get_gologin_manager()
                await gologin_manager.mark_profile_available(mapping.profile_id)
                
                # Remove mapping
                del self._mappings[device_serial]
                
                # Update database
                session = get_db_session()
                device = session.query(Device).filter(Device.serial == device_serial).first()
                if device:
                    device.assigned_profile = None
                    device.proxy_host = None
                    device.proxy_port = None
                    session.commit()
                session.close()
                
                logger.info(f"Successfully unassigned profile from device {device_serial}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to unassign profile from device {device_serial}: {e}")
            return False
    
    async def sync_all_devices(self) -> Dict[str, bool]:
        """Synchronize all device mappings"""
        results = {}
        
        try:
            # Get all online devices
            adb_manager = await get_adb_manager()
            devices = await adb_manager.scan_devices()
            online_devices = {d.serial for d in devices if d.status == 'online'}
            
            # Sync existing mappings
            for device_serial in list(self._mappings.keys()):
                if device_serial not in online_devices:
                    logger.warning(f"Device {device_serial} is offline, skipping sync")
                    results[device_serial] = False
                    continue
                
                mapping = self._mappings[device_serial]
                if mapping.needs_resync():
                    success = await self._sync_device_mapping(device_serial)
                    results[device_serial] = success
                else:
                    results[device_serial] = True
            
            # Assign profiles to unassigned online devices
            unassigned_devices = online_devices - set(self._mappings.keys())
            for device_serial in unassigned_devices:
                if len(self._mappings) < self.max_devices:
                    success = await self.assign_profile_to_device(device_serial)
                    results[device_serial] = success
                else:
                    logger.warning(f"Maximum devices ({self.max_devices}) reached, not assigning to {device_serial}")
                    results[device_serial] = False
            
            successful_syncs = sum(1 for success in results.values() if success)
            logger.info(f"Sync completed: {successful_syncs}/{len(results)} devices synced successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during device sync: {e}")
            return results
    
    async def _sync_device_mapping(self, device_serial: str) -> bool:
        """Synchronize a specific device mapping"""
        try:
            mapping = self._mappings.get(device_serial)
            if not mapping:
                return False
            
            async with self._device_locks[device_serial]:
                mapping.sync_status = "syncing"
                mapping.sync_attempts += 1
                
                # Re-configure proxy
                adb_manager = await get_adb_manager()
                proxy_success = await adb_manager.configure_proxy(
                    device_serial, mapping.proxy_host, mapping.proxy_port
                )
                
                if not proxy_success:
                    mapping.sync_status = "failed"
                    logger.error(f"Failed to configure proxy for device {device_serial}")
                    return False
                
                # Test connectivity
                connectivity_ok = await self._test_device_connectivity(
                    device_serial, mapping.proxy_host, mapping.proxy_port
                )
                
                mapping.sync_status = "synced" if connectivity_ok else "proxy_only"
                mapping.last_sync = datetime.now(timezone.utc)
                
                # Update database
                await self._update_device_mapping_in_db(mapping)
                
                logger.info(f"Successfully synced device {device_serial} (status: {mapping.sync_status})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to sync device {device_serial}: {e}")
            if device_serial in self._mappings:
                self._mappings[device_serial].sync_status = "failed"
            return False
    
    async def _update_device_mapping_in_db(self, mapping: DeviceProfileMapping):
        """Update device mapping in database"""
        try:
            session = get_db_session()
            
            device = session.query(Device).filter(Device.serial == mapping.device_serial).first()
            if device:
                device.assigned_profile = mapping.profile_id
                device.proxy_host = mapping.proxy_host
                device.proxy_port = mapping.proxy_port
                device.updated_at = datetime.now(timezone.utc)
                session.commit()
            
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to update device mapping in database: {e}")
            session.rollback()
            session.close()
    
    async def _background_sync_task(self):
        """Background task for periodic synchronization"""
        logger.info("Background sync task started")
        
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                
                # Perform sync
                results = await self.sync_all_devices()
                
                # Log summary
                successful = sum(1 for success in results.values() if success)
                total = len(results)
                
                if total > 0:
                    logger.info(f"Periodic sync: {successful}/{total} devices synced successfully")
                
            except Exception as e:
                logger.error(f"Error in background sync task: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def get_device_mapping(self, device_serial: str) -> Optional[DeviceProfileMapping]:
        """Get device profile mapping"""
        return self._mappings.get(device_serial)
    
    async def get_all_mappings(self) -> Dict[str, DeviceProfileMapping]:
        """Get all device profile mappings"""
        return self._mappings.copy()
    
    async def get_synchronizer_statistics(self) -> Dict[str, any]:
        """Get synchronizer statistics"""
        total_mappings = len(self._mappings)
        synced_mappings = sum(1 for m in self._mappings.values() if m.is_synced())
        failed_mappings = sum(1 for m in self._mappings.values() if m.sync_status == "failed")
        
        return {
            'total_mappings': total_mappings,
            'synced_mappings': synced_mappings,
            'failed_mappings': failed_mappings,
            'sync_success_rate': (synced_mappings / total_mappings) if total_mappings > 0 else 0,
            'max_devices': self.max_devices,
            'sync_interval': self.sync_interval
        }


# Global synchronizer instance
_profile_synchronizer: Optional[ProfileDeviceSynchronizer] = None


async def get_profile_synchronizer() -> ProfileDeviceSynchronizer:
    """Get global profile synchronizer instance"""
    global _profile_synchronizer
    if _profile_synchronizer is None:
        _profile_synchronizer = ProfileDeviceSynchronizer()
        await _profile_synchronizer.initialize()
    return _profile_synchronizer