"""
YouTube Analytics Client
Integrates with YouTube Data API v3 for analytics and metrics collection
Stores data in Supabase for comprehensive reporting
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from config.production_config import get_config
from integrations.supabase_client import supabase_client

config = get_config()

class YouTubeClient:
    """YouTube API client for analytics and data collection"""
    
    def __init__(self):
        self.api_key = config.YOUTUBE_API_KEY
        self.channel_ids = config.YOUTUBE_CHANNEL_IDS
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.client = httpx.AsyncClient()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def test_connection(self) -> bool:
        """Test YouTube API connection"""
        try:
            if not self.api_key:
                return False
            
            url = f"{self.base_url}/channels"
            params = {
                "key": self.api_key,
                "part": "id",
                "mine": "true"
            }
            
            response = await self.client.get(url, params=params)
            return response.status_code == 200
            
        except Exception as e:
            print(f"YouTube connection test failed: {e}")
            return False
    
    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed channel information"""
        try:
            url = f"{self.base_url}/channels"
            params = {
                "key": self.api_key,
                "part": "snippet,statistics,brandingSettings",
                "id": channel_id
            }
            
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["items"]:
                    channel = data["items"][0]
                    return {
                        "channel_id": channel["id"],
                        "title": channel["snippet"]["title"],
                        "description": channel["snippet"]["description"],
                        "subscriber_count": int(channel["statistics"].get("subscriberCount", 0)),
                        "video_count": int(channel["statistics"].get("videoCount", 0)),
                        "view_count": int(channel["statistics"].get("viewCount", 0)),
                        "thumbnail_url": channel["snippet"]["thumbnails"]["high"]["url"],
                        "country": channel["snippet"].get("country", ""),
                        "custom_url": channel["snippet"].get("customUrl", ""),
                        "published_at": channel["snippet"]["publishedAt"]
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching channel info: {e}")
            return None
    
    async def get_channel_analytics(self, channel_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive channel analytics"""
        try:
            # Get recent videos
            videos = await self.get_recent_videos(channel_id, days)
            
            # Calculate totals
            total_views = sum(video["view_count"] for video in videos)
            total_likes = sum(video["like_count"] for video in videos)
            total_comments = sum(video["comment_count"] for video in videos)
            
            # Get channel info for current stats
            channel_info = await self.get_channel_info(channel_id)
            
            analytics = {
                "channel_id": channel_id,
                "period_days": days,
                "total_videos": len(videos),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_views_per_video": total_views / len(videos) if videos else 0,
                "engagement_rate": (total_likes + total_comments) / total_views if total_views > 0 else 0,
                "videos": videos,
                "channel_stats": channel_info,
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            # Store in Supabase
            await supabase_client.store_youtube_metrics(analytics)
            
            return analytics
            
        except Exception as e:
            print(f"Error fetching YouTube analytics: {e}")
            return {
                "channel_id": channel_id,
                "error": str(e),
                "fetched_at": datetime.utcnow().isoformat()
            }
    
    async def get_recent_videos(self, channel_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent videos from channel"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Search for videos
            url = f"{self.base_url}/search"
            params = {
                "key": self.api_key,
                "part": "id,snippet",
                "channelId": channel_id,
                "type": "video",
                "order": "date",
                "publishedAfter": start_date.isoformat() + "Z",
                "publishedBefore": end_date.isoformat() + "Z",
                "maxResults": 50
            }
            
            response = await self.client.get(url, params=params)
            if response.status_code != 200:
                return []
            
            search_data = response.json()
            video_ids = [item["id"]["videoId"] for item in search_data["items"]]
            
            if not video_ids:
                return []
            
            # Get detailed video statistics
            videos_url = f"{self.base_url}/videos"
            videos_params = {
                "key": self.api_key,
                "part": "statistics,snippet,contentDetails",
                "id": ",".join(video_ids)
            }
            
            videos_response = await self.client.get(videos_url, params=videos_params)
            if videos_response.status_code != 200:
                return []
            
            videos_data = videos_response.json()
            
            videos = []
            for video in videos_data["items"]:
                video_info = {
                    "video_id": video["id"],
                    "title": video["snippet"]["title"],
                    "description": video["snippet"]["description"][:500],  # Truncate
                    "published_at": video["snippet"]["publishedAt"],
                    "view_count": int(video["statistics"].get("viewCount", 0)),
                    "like_count": int(video["statistics"].get("likeCount", 0)),
                    "comment_count": int(video["statistics"].get("commentCount", 0)),
                    "duration": video["contentDetails"]["duration"],
                    "thumbnail_url": video["snippet"]["thumbnails"]["high"]["url"],
                    "tags": video["snippet"].get("tags", [])[:10]  # Max 10 tags
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"Error fetching recent videos: {e}")
            return []
    
    async def get_video_performance(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed performance metrics for a specific video"""
        try:
            url = f"{self.base_url}/videos"
            params = {
                "key": self.api_key,
                "part": "statistics,snippet,contentDetails",
                "id": video_id
            }
            
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["items"]:
                    video = data["items"][0]
                    return {
                        "video_id": video["id"],
                        "title": video["snippet"]["title"],
                        "published_at": video["snippet"]["publishedAt"],
                        "view_count": int(video["statistics"].get("viewCount", 0)),
                        "like_count": int(video["statistics"].get("likeCount", 0)),
                        "dislike_count": int(video["statistics"].get("dislikeCount", 0)),
                        "comment_count": int(video["statistics"].get("commentCount", 0)),
                        "favorite_count": int(video["statistics"].get("favoriteCount", 0)),
                        "duration": video["contentDetails"]["duration"],
                        "category_id": video["snippet"]["categoryId"],
                        "tags": video["snippet"].get("tags", []),
                        "fetched_at": datetime.utcnow().isoformat()
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching video performance: {e}")
            return None
    
    async def search_trending_content(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """Search for trending content related to query"""
        try:
            url = f"{self.base_url}/search"
            params = {
                "key": self.api_key,
                "part": "snippet",
                "q": query,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z",
                "maxResults": max_results
            }
            
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                trending_videos = []
                for item in data["items"]:
                    video_info = {
                        "video_id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "channel_title": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
                        "description": item["snippet"]["description"][:200]
                    }
                    trending_videos.append(video_info)
                
                return trending_videos
            
            return []
            
        except Exception as e:
            print(f"Error searching trending content: {e}")
            return []
    
    async def collect_all_channels_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Collect analytics for all configured channels"""
        try:
            if not self.channel_ids:
                return {"error": "No channels configured"}
            
            all_analytics = {}
            total_metrics = {
                "total_videos": 0,
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_subscribers": 0
            }
            
            for channel_id in self.channel_ids:
                channel_analytics = await self.get_channel_analytics(channel_id, days)
                all_analytics[channel_id] = channel_analytics
                
                # Aggregate totals
                if "total_videos" in channel_analytics:
                    total_metrics["total_videos"] += channel_analytics["total_videos"]
                    total_metrics["total_views"] += channel_analytics["total_views"]
                    total_metrics["total_likes"] += channel_analytics["total_likes"]
                    total_metrics["total_comments"] += channel_analytics["total_comments"]
                
                if channel_analytics.get("channel_stats", {}).get("subscriber_count"):
                    total_metrics["total_subscribers"] += channel_analytics["channel_stats"]["subscriber_count"]
            
            comprehensive_report = {
                "report_type": "youtube_comprehensive",
                "period_days": days,
                "total_channels": len(self.channel_ids),
                "aggregated_metrics": total_metrics,
                "channel_analytics": all_analytics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Store comprehensive report
            await supabase_client.store_youtube_metrics(comprehensive_report)
            
            return comprehensive_report
            
        except Exception as e:
            print(f"Error collecting all channels analytics: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }

# Global client instance
youtube_client = YouTubeClient()

async def test_youtube_connection() -> bool:
    """Test YouTube API connection"""
    return await youtube_client.test_connection()

async def get_youtube_comprehensive_report(days: int = 30) -> Dict[str, Any]:
    """Get comprehensive YouTube report for all channels"""
    return await youtube_client.collect_all_channels_analytics(days)

# Cleanup function
async def cleanup_youtube_client():
    """Cleanup YouTube client resources"""
    await youtube_client.close()