"""
🎯 Neural Forge - Satellite Content Distribution
===============================================
Manages 5 satellite accounts for content generation and upload
Main account ONLY collects metrics - NO content upload
"""

import os
import random
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DistributionPlatform(Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

@dataclass
class SatelliteAccount:
    """Configuration for satellite account"""
    id: str
    name: str
    platform: DistributionPlatform
    api_key: str
    client_id: str
    client_secret: str
    refresh_token: str
    channel_id: str
    ad_account_id: Optional[str] = None
    active: bool = True
    upload_enabled: bool = True
    metrics_enabled: bool = True

@dataclass
class MainAccount:
    """Main account - METRICS ONLY, NO UPLOADS"""
    platform: DistributionPlatform
    api_key: str
    client_id: str
    client_secret: str
    refresh_token: str
    channel_id: str
    upload_enabled: bool = False  # CRITICAL: Main account never uploads
    metrics_enabled: bool = True

class SatelliteManager:
    """Manages satellite accounts for content distribution"""
    
    def __init__(self):
        self.satellite_accounts: List[SatelliteAccount] = []
        self.main_accounts: Dict[DistributionPlatform, MainAccount] = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load satellite and main account configurations"""
        
        # Main YouTube Account - METRICS ONLY
        self.main_accounts[DistributionPlatform.YOUTUBE] = MainAccount(
            platform=DistributionPlatform.YOUTUBE,
            api_key=os.getenv('YOUTUBE_API_KEY'),
            client_id=os.getenv('YOUTUBE_CLIENT_ID'),
            client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
            refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
            channel_id=os.getenv('YOUTUBE_CHANNEL_ID'),
            upload_enabled=False,  # NEVER upload with main account
            metrics_enabled=True
        )
        
        # YouTube Satellite Accounts - Content Upload Enabled
        for i in range(1, 6):  # 5 satellite accounts
            satellite = SatelliteAccount(
                id=f"youtube_satellite_{i}",
                name=f"YouTube Satellite {i}",
                platform=DistributionPlatform.YOUTUBE,
                api_key=os.getenv(f'YOUTUBE_SATELLITE_{i}_API_KEY'),
                client_id=os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_ID'),
                client_secret=os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_SECRET'),
                refresh_token=os.getenv(f'YOUTUBE_SATELLITE_{i}_REFRESH_TOKEN'),
                channel_id=os.getenv(f'YOUTUBE_SATELLITE_{i}_CHANNEL_ID'),
                upload_enabled=True,  # Satellites DO upload content
                metrics_enabled=True
            )
            
            if self._validate_satellite_config(satellite):
                self.satellite_accounts.append(satellite)
                logger.info(f"✅ Loaded satellite account: {satellite.name}")
            else:
                logger.warning(f"⚠️  Skipping invalid satellite: {satellite.name}")
    
    def _validate_satellite_config(self, satellite: SatelliteAccount) -> bool:
        """Validate satellite account configuration"""
        required_fields = [
            satellite.api_key,
            satellite.client_id,
            satellite.client_secret,
            satellite.refresh_token,
            satellite.channel_id
        ]
        
        return all(field and field != "your_" + field.lower() for field in required_fields)
    
    def get_upload_accounts(self) -> List[SatelliteAccount]:
        """Get accounts enabled for content upload (satellites only)"""
        return [
            account for account in self.satellite_accounts 
            if account.upload_enabled and account.active
        ]
    
    def get_metrics_accounts(self) -> List[SatelliteAccount]:
        """Get accounts for metrics collection (satellites + main)"""
        metrics_accounts = [
            account for account in self.satellite_accounts 
            if account.metrics_enabled and account.active
        ]
        return metrics_accounts
    
    def get_main_account(self, platform: DistributionPlatform) -> Optional[MainAccount]:
        """Get main account for metrics (NO upload capability)"""
        main = self.main_accounts.get(platform)
        if main and not main.upload_enabled:  # Double-check upload is disabled
            return main
        return None
    
    def select_upload_account(self, strategy: str = "round_robin") -> Optional[SatelliteAccount]:
        """Select satellite account for content upload"""
        upload_accounts = self.get_upload_accounts()
        
        if not upload_accounts:
            logger.error("❌ No satellite accounts available for upload")
            return None
        
        if strategy == "round_robin":
            # Simple round-robin selection
            if not hasattr(self, '_upload_index'):
                self._upload_index = 0
            
            account = upload_accounts[self._upload_index % len(upload_accounts)]
            self._upload_index += 1
            
        elif strategy == "random":
            account = random.choice(upload_accounts)
            
        elif strategy == "least_used":
            # Select account with least recent uploads
            account = min(upload_accounts, key=lambda a: getattr(a, 'last_upload_time', 0))
            
        else:
            account = upload_accounts[0]
        
        logger.info(f"🎯 Selected upload account: {account.name}")
        return account
    
    async def distribute_content(self, content_data: Dict, platforms: List[DistributionPlatform]):
        """Distribute content across satellite accounts"""
        distribution_results = []
        
        for platform in platforms:
            # Get satellite account for upload
            satellite = self.select_upload_account()
            
            if not satellite or satellite.platform != platform:
                logger.error(f"❌ No suitable satellite account for {platform.value}")
                continue
            
            try:
                # Upload content using satellite account
                result = await self._upload_content(satellite, content_data)
                distribution_results.append({
                    'platform': platform.value,
                    'account': satellite.name,
                    'success': result.get('success', False),
                    'content_id': result.get('content_id'),
                    'upload_time': result.get('upload_time')
                })
                
                logger.info(f"✅ Content uploaded via {satellite.name}")
                
            except Exception as e:
                logger.error(f"❌ Upload failed for {satellite.name}: {str(e)}")
                distribution_results.append({
                    'platform': platform.value,
                    'account': satellite.name,
                    'success': False,
                    'error': str(e)
                })
        
        return distribution_results
    
    async def collect_metrics(self, platforms: List[DistributionPlatform]):
        """Collect metrics from main account + satellites"""
        metrics_data = {}
        
        for platform in platforms:
            platform_metrics = []
            
            # Collect from main account (metrics only)
            main_account = self.get_main_account(platform)
            if main_account:
                try:
                    main_metrics = await self._collect_account_metrics(main_account)
                    platform_metrics.append({
                        'account_type': 'main',
                        'account_name': f"Main {platform.value.title()}",
                        'metrics': main_metrics
                    })
                    logger.info(f"📊 Collected metrics from main {platform.value} account")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to collect main metrics: {str(e)}")
            
            # Collect from satellite accounts
            satellite_accounts = [
                acc for acc in self.get_metrics_accounts() 
                if acc.platform == platform
            ]
            
            for satellite in satellite_accounts:
                try:
                    satellite_metrics = await self._collect_account_metrics(satellite)
                    platform_metrics.append({
                        'account_type': 'satellite',
                        'account_name': satellite.name,
                        'metrics': satellite_metrics
                    })
                    logger.info(f"📊 Collected metrics from {satellite.name}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to collect satellite metrics: {str(e)}")
            
            metrics_data[platform.value] = platform_metrics
        
        return metrics_data
    
    async def _upload_content(self, account: SatelliteAccount, content_data: Dict) -> Dict:
        """Upload content using satellite account"""
        
        # CRITICAL: Verify this is NOT a main account
        if not account.upload_enabled:
            raise ValueError("❌ CRITICAL: Attempted upload with non-upload account")
        
        # Platform-specific upload logic
        if account.platform == DistributionPlatform.YOUTUBE:
            return await self._upload_to_youtube(account, content_data)
        elif account.platform == DistributionPlatform.TIKTOK:
            return await self._upload_to_tiktok(account, content_data)
        # Add other platforms as needed
        
        raise NotImplementedError(f"Upload not implemented for {account.platform.value}")
    
    async def _collect_account_metrics(self, account) -> Dict:
        """Collect metrics from account (main or satellite)"""
        
        if isinstance(account, MainAccount):
            platform = account.platform
            api_key = account.api_key
            channel_id = account.channel_id
        else:  # SatelliteAccount
            platform = account.platform
            api_key = account.api_key
            channel_id = account.channel_id
        
        # Platform-specific metrics collection
        if platform == DistributionPlatform.YOUTUBE:
            return await self._collect_youtube_metrics(api_key, channel_id)
        elif platform == DistributionPlatform.TIKTOK:
            return await self._collect_tiktok_metrics(api_key, channel_id)
        
        return {}
    
    async def _upload_to_youtube(self, account: SatelliteAccount, content_data: Dict) -> Dict:
        """Upload video to YouTube using satellite account"""
        from social_extensions.youtube_integration import YouTubeUploader
        
        uploader = YouTubeUploader(
            api_key=account.api_key,
            client_id=account.client_id,
            client_secret=account.client_secret,
            refresh_token=account.refresh_token
        )
        
        result = await uploader.upload_video(
            video_path=content_data['video_path'],
            title=content_data['title'],
            description=content_data['description'],
            tags=content_data.get('tags', []),
            category_id=content_data.get('category_id', '10')  # Music category
        )
        
        return result
    
    async def _collect_youtube_metrics(self, api_key: str, channel_id: str) -> Dict:
        """Collect YouTube metrics"""
        from social_extensions.youtube_integration import YouTubeAnalytics
        
        analytics = YouTubeAnalytics(api_key=api_key)
        
        return await analytics.get_channel_metrics(
            channel_id=channel_id,
            metrics=['views', 'likes', 'comments', 'subscribers', 'watchTime']
        )
    
    def validate_configuration(self) -> Dict:
        """Validate entire satellite configuration"""
        validation_result = {
            'valid': True,
            'issues': [],
            'summary': {
                'main_accounts': len(self.main_accounts),
                'satellite_accounts': len(self.satellite_accounts),
                'upload_enabled_accounts': len(self.get_upload_accounts()),
                'metrics_enabled_accounts': len(self.get_metrics_accounts())
            }
        }
        
        # Check main accounts never have upload enabled
        for platform, main_account in self.main_accounts.items():
            if main_account.upload_enabled:
                validation_result['valid'] = False
                validation_result['issues'].append(
                    f"❌ CRITICAL: Main {platform.value} account has upload enabled!"
                )
        
        # Check satellite accounts configuration
        if len(self.get_upload_accounts()) == 0:
            validation_result['valid'] = False
            validation_result['issues'].append("❌ No satellite accounts configured for upload")
        
        if len(self.get_upload_accounts()) < 5:
            validation_result['issues'].append(
                f"⚠️  Only {len(self.get_upload_accounts())}/5 satellite accounts configured"
            )
        
        return validation_result

# Global satellite manager instance
satellite_manager = SatelliteManager()

# Convenience functions
async def distribute_content(content_data: Dict, platforms: List[str]):
    """Distribute content using satellite accounts"""
    platform_enums = [DistributionPlatform(p) for p in platforms]
    return await satellite_manager.distribute_content(content_data, platform_enums)

async def collect_all_metrics(platforms: List[str]):
    """Collect metrics from all accounts"""
    platform_enums = [DistributionPlatform(p) for p in platforms]
    return await satellite_manager.collect_metrics(platform_enums)

def get_satellite_status():
    """Get status of satellite configuration"""
    return satellite_manager.validate_configuration()