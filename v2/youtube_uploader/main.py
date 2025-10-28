"""
YouTube Uploader Service - Docker v2.0
Automated video upload with metadata optimization
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import os
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Uploader v2.0",
    description="Automated YouTube Video Upload & Optimization",
    version="2.0.0"
)

# ============================================
# CONFIGURATION
# ============================================

DUMMY_MODE = os.getenv("DUMMY_MODE", "true") == "true"
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# ============================================
# MODELS
# ============================================

class VideoUploadRequest(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=5000)
    tags: List[str] = Field(default_factory=list, max_items=500)
    category_id: str = "10"  # Music category
    privacy_status: str = "public"  # public, unlisted, private
    publish_at: Optional[datetime] = None
    playlist_id: Optional[str] = None
    made_for_kids: bool = False
    
class VideoMetadataOptimization(BaseModel):
    artist_name: str
    song_name: str
    genre: str
    release_date: Optional[str] = None
    record_label: Optional[str] = None
    
class VideoAnalyticsRequest(BaseModel):
    video_id: str
    metrics: List[str] = ["views", "likes", "comments", "shares", "watchTime"]

# ============================================
# YOUTUBE CLIENT
# ============================================

class YouTubeClient:
    def __init__(self):
        self.client_id = YOUTUBE_CLIENT_ID
        self.client_secret = YOUTUBE_CLIENT_SECRET
        self.refresh_token = YOUTUBE_REFRESH_TOKEN
        self.youtube_service = None
        
        if not DUMMY_MODE:
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize YouTube API service"""
        try:
            credentials = Credentials(
                None,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            self.youtube_service = build(
                YOUTUBE_API_SERVICE_NAME,
                YOUTUBE_API_VERSION,
                credentials=credentials,
                cache_discovery=False
            )
            
            logger.info("YouTube API service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize YouTube service: {e}")
            raise
    
    def optimize_metadata(
        self,
        optimization: VideoMetadataOptimization
    ) -> Dict[str, Any]:
        """Generate optimized title, description, and tags"""
        
        # Optimized title (max 100 chars, front-load keywords)
        title = f"{optimization.artist_name} - {optimization.song_name}"
        if optimization.genre:
            title += f" ({optimization.genre})"
        
        # Optimized description with timestamps and links
        description = f"""
🎵 {optimization.song_name} by {optimization.artist_name}

Listen on all platforms:
🎧 Spotify: [Your Spotify Link]
🍎 Apple Music: [Your Apple Music Link]
🎶 YouTube Music: [Your YouTube Music Link]
💿 Tidal: [Your Tidal Link]

📅 Released: {optimization.release_date or 'Now Available'}
🎸 Genre: {optimization.genre}
{f'🏢 Label: {optimization.record_label}' if optimization.record_label else ''}

Follow {optimization.artist_name}:
📷 Instagram: @your_instagram
🎵 TikTok: @your_tiktok
🐦 Twitter: @your_twitter

#{"#".join([optimization.genre.lower(), 'music', optimization.artist_name.lower().replace(' ', '')])}

© {datetime.now().year} {optimization.record_label or optimization.artist_name}. All rights reserved.
"""
        
        # Optimized tags (max 500 chars total, most important first)
        tags = [
            optimization.artist_name,
            optimization.song_name,
            optimization.genre,
            f"{optimization.genre} music",
            "music",
            "new music",
            f"{datetime.now().year} music",
            "official",
            "audio",
            "trap" if "trap" in optimization.genre.lower() else optimization.genre
        ]
        
        # Add related genre tags
        if "trap" in optimization.genre.lower():
            tags.extend(["trap latino", "latin trap", "hip hop", "rap"])
        elif "reggaeton" in optimization.genre.lower():
            tags.extend(["reggaeton", "latin music", "urbano", "dembow"])
        
        return {
            "title": title[:100],  # YouTube limit
            "description": description[:5000],  # YouTube limit
            "tags": tags[:500]  # YouTube limit
        }
    
    async def upload_video(
        self,
        video_path: str,
        request: VideoUploadRequest
    ) -> Dict:
        """Upload video to YouTube"""
        
        if DUMMY_MODE:
            logger.info(f"DUMMY MODE: Would upload {video_path}")
            return {
                "id": f"dummy_video_{datetime.now().timestamp()}",
                "title": request.title,
                "url": f"https://youtube.com/watch?v=dummy_id",
                "status": "uploaded"
            }
        
        try:
            # Prepare request body
            body = {
                "snippet": {
                    "title": request.title,
                    "description": request.description,
                    "tags": request.tags,
                    "categoryId": request.category_id
                },
                "status": {
                    "privacyStatus": request.privacy_status,
                    "selfDeclaredMadeForKids": request.made_for_kids
                }
            }
            
            if request.publish_at:
                body["status"]["publishAt"] = request.publish_at.isoformat()
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype="video/*"
            )
            
            # Execute upload
            upload_request = self.youtube_service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = upload_request.execute()
            
            # Add to playlist if specified
            if request.playlist_id:
                await self.add_to_playlist(response["id"], request.playlist_id)
            
            logger.info(f"Video uploaded: {response['id']}")
            
            return {
                "id": response["id"],
                "title": response["snippet"]["title"],
                "url": f"https://youtube.com/watch?v={response['id']}",
                "status": "uploaded"
            }
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def add_to_playlist(self, video_id: str, playlist_id: str):
        """Add video to playlist"""
        
        if DUMMY_MODE:
            logger.info(f"DUMMY MODE: Would add video to playlist")
            return {"status": "added"}
        
        try:
            self.youtube_service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
            
            logger.info(f"Video {video_id} added to playlist {playlist_id}")
            
        except Exception as e:
            logger.error(f"Failed to add to playlist: {e}")
            raise
    
    async def get_video_analytics(
        self,
        video_id: str,
        request: VideoAnalyticsRequest
    ) -> Dict:
        """Get video analytics"""
        
        if DUMMY_MODE:
            return {
                "video_id": video_id,
                "views": 15000,
                "likes": 850,
                "comments": 120,
                "shares": 45,
                "watchTime": 8500,  # minutes
                "ctr": 4.5,
                "avgViewDuration": 125  # seconds
            }
        
        try:
            # Get video statistics
            video_response = self.youtube_service.videos().list(
                part="statistics,contentDetails",
                id=video_id
            ).execute()
            
            if not video_response.get("items"):
                raise HTTPException(status_code=404, detail="Video not found")
            
            stats = video_response["items"][0]["statistics"]
            
            return {
                "video_id": video_id,
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "favorites": int(stats.get("favoriteCount", 0))
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# ============================================
# API ENDPOINTS
# ============================================

youtube_client = YouTubeClient()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "youtube-uploader-v2",
        "dummy_mode": DUMMY_MODE,
        "channel_id": YOUTUBE_CHANNEL_ID,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/optimize-metadata")
async def optimize_metadata(optimization: VideoMetadataOptimization):
    """Generate optimized video metadata"""
    try:
        result = youtube_client.optimize_metadata(optimization)
        return result
    except Exception as e:
        logger.error(f"Metadata optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    video_path: str,
    request: VideoUploadRequest
):
    """Upload video to YouTube"""
    try:
        # Validate video file exists
        if not DUMMY_MODE and not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        result = await youtube_client.upload_video(video_path, request)
        return result
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quick-upload")
async def quick_upload(
    video_path: str,
    artist_name: str,
    song_name: str,
    genre: str = "Trap"
):
    """Quick upload with automatic optimization"""
    try:
        # Optimize metadata
        optimization = VideoMetadataOptimization(
            artist_name=artist_name,
            song_name=song_name,
            genre=genre,
            release_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        metadata = youtube_client.optimize_metadata(optimization)
        
        # Upload video
        request = VideoUploadRequest(
            title=metadata["title"],
            description=metadata["description"],
            tags=metadata["tags"],
            privacy_status="public"
        )
        
        result = await youtube_client.upload_video(video_path, request)
        
        return {
            **result,
            "metadata_optimized": True,
            "next_steps": [
                "Add custom thumbnail",
                "Enable monetization",
                "Promote on social media"
            ]
        }
        
    except Exception as e:
        logger.error(f"Quick upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/{video_id}")
async def get_analytics(video_id: str):
    """Get video analytics"""
    try:
        request = VideoAnalyticsRequest(video_id=video_id)
        result = await youtube_client.get_video_analytics(video_id, request)
        return result
    except Exception as e:
        logger.error(f"Analytics fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/playlist/add")
async def add_to_playlist(video_id: str, playlist_id: str):
    """Add video to playlist"""
    try:
        await youtube_client.add_to_playlist(video_id, playlist_id)
        return {"status": "success", "message": "Video added to playlist"}
    except Exception as e:
        logger.error(f"Add to playlist failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9003)
