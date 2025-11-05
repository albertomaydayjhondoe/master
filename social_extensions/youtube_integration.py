"""
🎵 Neural Forge - YouTube Integration (Satellite-Aware)
=====================================================
YouTube API integration with satellite account management
Main account: METRICS ONLY (no upload)
Satellite accounts: Content upload enabled
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

class YouTubeAccount:
    """Base YouTube account configuration"""
    
    def __init__(self, api_key: str, client_id: str, client_secret: str, 
                 refresh_token: str, channel_id: str, upload_enabled: bool = False):
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.channel_id = channel_id
        self.upload_enabled = upload_enabled
        self._service = None
        self._credentials = None
    
    def _get_credentials(self):
        """Get OAuth2 credentials"""
        if self._credentials and self._credentials.valid:
            return self._credentials
        
        self._credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        if self._credentials.expired:
            self._credentials.refresh(Request())
        
        return self._credentials
    
    def _get_service(self):
        """Get YouTube API service"""
        if self._service:
            return self._service
        
        if self.upload_enabled:
            # Use OAuth for upload-enabled accounts
            credentials = self._get_credentials()
            self._service = build('youtube', 'v3', credentials=credentials)
        else:
            # Use API key for metrics-only accounts
            self._service = build('youtube', 'v3', developerKey=self.api_key)
        
        return self._service

class YouTubeMainAccount(YouTubeAccount):
    """Main YouTube account - METRICS ONLY"""
    
    def __init__(self, api_key: str, client_id: str, client_secret: str, 
                 refresh_token: str, channel_id: str):
        super().__init__(api_key, client_id, client_secret, refresh_token, 
                        channel_id, upload_enabled=False)
        logger.info("🎯 Main YouTube account initialized - METRICS ONLY")
    
    async def upload_video(self, *args, **kwargs):
        """BLOCKED: Main account cannot upload"""
        raise PermissionError("❌ CRITICAL: Main YouTube account cannot upload content!")
    
    async def get_channel_metrics(self, metrics: List[str] = None) -> Dict:
        """Get channel analytics (main purpose)"""
        if metrics is None:
            metrics = ['views', 'likes', 'comments', 'subscribers', 'estimatedMinutesWatched']
        
        try:
            service = self._get_service()
            
            # Get channel statistics
            channel_response = service.channels().list(
                part='statistics,snippet',
                id=self.channel_id
            ).execute()
            
            if not channel_response['items']:
                return {'error': 'Channel not found'}
            
            channel_data = channel_response['items'][0]
            stats = channel_data['statistics']
            
            # Get recent videos for detailed metrics
            videos_response = service.search().list(
                part='id',
                channelId=self.channel_id,
                maxResults=50,
                order='date',
                type='video'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in videos_response['items']]
            
            # Get video statistics
            videos_stats = {}
            if video_ids:
                videos_response = service.videos().list(
                    part='statistics,snippet',
                    id=','.join(video_ids)
                ).execute()
                
                for video in videos_response['items']:
                    video_id = video['id']
                    videos_stats[video_id] = {
                        'title': video['snippet']['title'],
                        'views': int(video['statistics'].get('viewCount', 0)),
                        'likes': int(video['statistics'].get('likeCount', 0)),
                        'comments': int(video['statistics'].get('commentCount', 0)),
                        'published': video['snippet']['publishedAt']
                    }
            
            return {
                'channel_id': self.channel_id,
                'channel_title': channel_data['snippet']['title'],
                'total_subscribers': int(stats.get('subscriberCount', 0)),
                'total_views': int(stats.get('viewCount', 0)),
                'total_videos': int(stats.get('videoCount', 0)),
                'recent_videos': videos_stats,
                'collected_at': datetime.now().isoformat()
            }
            
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return {'error': str(e)}
    
    async def get_trending_data(self) -> Dict:
        """Get trending videos data for analysis"""
        try:
            service = self._get_service()
            
            trending_response = service.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode='US',  # Can be configured
                videoCategoryId='10',  # Music category
                maxResults=50
            ).execute()
            
            trending_videos = []
            for video in trending_response['items']:
                trending_videos.append({
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'channel': video['snippet']['channelTitle'],
                    'views': int(video['statistics'].get('viewCount', 0)),
                    'likes': int(video['statistics'].get('likeCount', 0)),
                    'comments': int(video['statistics'].get('commentCount', 0)),
                    'published': video['snippet']['publishedAt'],
                    'tags': video['snippet'].get('tags', [])
                })
            
            return {
                'trending_videos': trending_videos,
                'collected_at': datetime.now().isoformat()
            }
            
        except HttpError as e:
            logger.error(f"❌ Trending data error: {e}")
            return {'error': str(e)}

class YouTubeSatelliteAccount(YouTubeAccount):
    """Satellite YouTube account - Upload enabled"""
    
    def __init__(self, satellite_id: str, api_key: str, client_id: str, 
                 client_secret: str, refresh_token: str, channel_id: str):
        super().__init__(api_key, client_id, client_secret, refresh_token, 
                        channel_id, upload_enabled=True)
        self.satellite_id = satellite_id
        self.upload_count = 0
        self.last_upload = None
        logger.info(f"🛰️  Satellite {satellite_id} initialized - UPLOAD ENABLED")
    
    async def upload_video(self, video_path: str, title: str, description: str,
                          tags: List[str] = None, category_id: str = '10',
                          privacy_status: str = 'public') -> Dict:
        """Upload video to YouTube"""
        
        if not self.upload_enabled:
            raise PermissionError("❌ Upload not enabled for this account")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"❌ Video file not found: {video_path}")
        
        try:
            service = self._get_service()
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            # Execute upload
            insert_request = service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            video_id = None
            response = None
            error = None
            
            # Resumable upload with progress tracking
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if status:
                        logger.info(f"📤 Upload progress: {int(status.progress() * 100)}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Retryable error
                        logger.warning(f"⚠️  Retryable error: {e}")
                        await asyncio.sleep(5)
                        continue
                    else:
                        error = str(e)
                        break
            
            if response and 'id' in response:
                video_id = response['id']
                self.upload_count += 1
                self.last_upload = datetime.now()
                
                logger.info(f"✅ Video uploaded successfully: {video_id}")
                
                return {
                    'success': True,
                    'video_id': video_id,
                    'satellite_id': self.satellite_id,
                    'upload_time': self.last_upload.isoformat(),
                    'title': title,
                    'url': f'https://www.youtube.com/watch?v={video_id}'
                }
            else:
                error = error or "Unknown upload error"
                logger.error(f"❌ Upload failed: {error}")
                
                return {
                    'success': False,
                    'satellite_id': self.satellite_id,
                    'error': error
                }
                
        except Exception as e:
            logger.error(f"❌ Upload exception: {str(e)}")
            return {
                'success': False,
                'satellite_id': self.satellite_id,
                'error': str(e)
            }
    
    async def get_upload_metrics(self) -> Dict:
        """Get metrics for uploaded videos"""
        try:
            service = self._get_service()
            
            # Get videos from this channel
            videos_response = service.search().list(
                part='id',
                channelId=self.channel_id,
                maxResults=50,
                order='date',
                type='video'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in videos_response['items']]
            
            if not video_ids:
                return {'videos': [], 'total_metrics': {}}
            
            # Get detailed statistics
            videos_response = service.videos().list(
                part='statistics,snippet',
                id=','.join(video_ids)
            ).execute()
            
            videos_data = []
            total_views = 0
            total_likes = 0
            total_comments = 0
            
            for video in videos_response['items']:
                stats = video['statistics']
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                videos_data.append({
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'published': video['snippet']['publishedAt']
                })
                
                total_views += views
                total_likes += likes
                total_comments += comments
            
            return {
                'satellite_id': self.satellite_id,
                'videos': videos_data,
                'total_metrics': {
                    'total_videos': len(videos_data),
                    'total_views': total_views,
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'avg_views_per_video': total_views / len(videos_data) if videos_data else 0
                },
                'collected_at': datetime.now().isoformat()
            }
            
        except HttpError as e:
            logger.error(f"❌ Metrics error: {e}")
            return {'error': str(e)}

class YouTubeManager:
    """Manages main + satellite YouTube accounts"""
    
    def __init__(self):
        self.main_account: Optional[YouTubeMainAccount] = None
        self.satellite_accounts: List[YouTubeSatelliteAccount] = []
        self._load_accounts()
    
    def _load_accounts(self):
        """Load main and satellite accounts from environment"""
        
        # Load main account (metrics only)
        main_api_key = os.getenv('YOUTUBE_API_KEY')
        main_client_id = os.getenv('YOUTUBE_CLIENT_ID')
        main_client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        main_refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
        main_channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        
        if all([main_api_key, main_client_id, main_client_secret, 
                main_refresh_token, main_channel_id]):
            self.main_account = YouTubeMainAccount(
                api_key=main_api_key,
                client_id=main_client_id,
                client_secret=main_client_secret,
                refresh_token=main_refresh_token,
                channel_id=main_channel_id
            )
            logger.info("✅ Main YouTube account loaded")
        else:
            logger.warning("⚠️  Main YouTube account not configured")
        
        # Load satellite accounts
        for i in range(1, 6):  # 5 satellites
            sat_api_key = os.getenv(f'YOUTUBE_SATELLITE_{i}_API_KEY')
            sat_client_id = os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_ID')
            sat_client_secret = os.getenv(f'YOUTUBE_SATELLITE_{i}_CLIENT_SECRET')
            sat_refresh_token = os.getenv(f'YOUTUBE_SATELLITE_{i}_REFRESH_TOKEN')
            sat_channel_id = os.getenv(f'YOUTUBE_SATELLITE_{i}_CHANNEL_ID')
            
            if all([sat_api_key, sat_client_id, sat_client_secret, 
                    sat_refresh_token, sat_channel_id]):
                satellite = YouTubeSatelliteAccount(
                    satellite_id=f'satellite_{i}',
                    api_key=sat_api_key,
                    client_id=sat_client_id,
                    client_secret=sat_client_secret,
                    refresh_token=sat_refresh_token,
                    channel_id=sat_channel_id
                )
                self.satellite_accounts.append(satellite)
                logger.info(f"✅ Satellite {i} loaded")
            else:
                logger.warning(f"⚠️  Satellite {i} not configured")
    
    async def collect_all_metrics(self) -> Dict:
        """Collect metrics from main + all satellites"""
        all_metrics = {
            'main_account': None,
            'satellite_accounts': [],
            'summary': {}
        }
        
        # Main account metrics
        if self.main_account:
            main_metrics = await self.main_account.get_channel_metrics()
            all_metrics['main_account'] = main_metrics
        
        # Satellite metrics
        total_satellite_views = 0
        total_satellite_videos = 0
        
        for satellite in self.satellite_accounts:
            sat_metrics = await satellite.get_upload_metrics()
            all_metrics['satellite_accounts'].append(sat_metrics)
            
            if 'total_metrics' in sat_metrics:
                total_satellite_views += sat_metrics['total_metrics'].get('total_views', 0)
                total_satellite_videos += sat_metrics['total_metrics'].get('total_videos', 0)
        
        # Summary
        all_metrics['summary'] = {
            'main_account_configured': self.main_account is not None,
            'satellites_configured': len(self.satellite_accounts),
            'total_satellite_views': total_satellite_views,
            'total_satellite_videos': total_satellite_videos,
            'collected_at': datetime.now().isoformat()
        }
        
        return all_metrics
    
    def select_satellite_for_upload(self) -> Optional[YouTubeSatelliteAccount]:
        """Select best satellite for upload (round-robin)"""
        if not self.satellite_accounts:
            logger.error("❌ No satellite accounts available")
            return None
        
        # Simple round-robin selection
        if not hasattr(self, '_upload_index'):
            self._upload_index = 0
        
        satellite = self.satellite_accounts[self._upload_index % len(self.satellite_accounts)]
        self._upload_index += 1
        
        logger.info(f"🎯 Selected satellite: {satellite.satellite_id}")
        return satellite
    
    async def upload_video_via_satellite(self, video_path: str, title: str, 
                                       description: str, **kwargs) -> Dict:
        """Upload video using satellite account"""
        satellite = self.select_satellite_for_upload()
        
        if not satellite:
            return {'success': False, 'error': 'No satellite accounts available'}
        
        return await satellite.upload_video(video_path, title, description, **kwargs)

# Global YouTube manager
youtube_manager = YouTubeManager()

# Convenience functions
async def upload_to_youtube(video_path: str, title: str, description: str, **kwargs):
    """Upload video via satellite account"""
    return await youtube_manager.upload_video_via_satellite(
        video_path, title, description, **kwargs
    )

async def collect_youtube_metrics():
    """Collect all YouTube metrics"""
    return await youtube_manager.collect_all_metrics()

def get_youtube_status():
    """Get YouTube configuration status"""
    return {
        'main_account_configured': youtube_manager.main_account is not None,
        'satellites_configured': len(youtube_manager.satellite_accounts),
        'satellites_list': [sat.satellite_id for sat in youtube_manager.satellite_accounts]
    }