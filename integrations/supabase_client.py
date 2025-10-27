"""
Supabase Integration - Core metrics and data management
Handles YouTube, Spotify, Meta Ads metrics storage and retrieval
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import httpx
from config.production_config import get_config

config = get_config()


class SupabaseClient:
    """Supabase client for metrics and data management"""
    
    def __init__(self):
        self.base_url = config.SUPABASE_URL
        self.anon_key = config.SUPABASE_ANON_KEY
        self.service_key = config.SUPABASE_SERVICE_KEY
        
        self.headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Supabase"""
        url = f"{self.base_url}/rest/v1/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=self.headers, json=data)
            elif method.upper() == "PATCH":
                response = await client.patch(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=self.headers)
            
            response.raise_for_status()
            return response.json() if response.text else {}
    
    # YouTube Metrics
    async def store_youtube_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Store YouTube channel/video metrics"""
        data = {
            "channel_id": metrics.get("channel_id", config.YOUTUBE_CHANNEL_ID),
            "video_id": metrics.get("video_id"),
            "title": metrics.get("title"),
            "views": metrics.get("views", 0),
            "likes": metrics.get("likes", 0),
            "comments": metrics.get("comments", 0),
            "subscribers": metrics.get("subscribers", 0),
            "watch_time_hours": metrics.get("watch_time_hours", 0),
            "engagement_rate": metrics.get("engagement_rate", 0),
            "revenue": metrics.get("revenue", 0),
            "cpm": metrics.get("cpm", 0),
            "metadata": metrics.get("metadata", {}),
            "recorded_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self._request("POST", "youtube_metrics", data)
    
    async def get_youtube_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get YouTube metrics for specified period"""
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        endpoint = f"youtube_metrics?recorded_at=gte.{start_date}&order=recorded_at.desc"
        
        return await self._request("GET", endpoint)
    
    # Spotify Metrics
    async def store_spotify_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Store Spotify track/artist metrics"""
        data = {
            "artist_id": metrics.get("artist_id"),
            "track_id": metrics.get("track_id"),
            "artist_name": metrics.get("artist_name"),
            "track_name": metrics.get("track_name"),
            "streams": metrics.get("streams", 0),
            "followers": metrics.get("followers", 0),
            "monthly_listeners": metrics.get("monthly_listeners", 0),
            "playlist_adds": metrics.get("playlist_adds", 0),
            "countries": metrics.get("countries", []),
            "revenue": metrics.get("revenue", 0),
            "metadata": metrics.get("metadata", {}),
            "recorded_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self._request("POST", "spotify_metrics", data)
    
    async def get_spotify_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get Spotify metrics for specified period"""
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        endpoint = f"spotify_metrics?recorded_at=gte.{start_date}&order=recorded_at.desc"
        
        return await self._request("GET", endpoint)
    
    # Meta Ads Metrics
    async def store_meta_ads_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Store Meta Ads campaign metrics"""
        data = {
            "campaign_id": metrics.get("campaign_id"),
            "campaign_name": metrics.get("campaign_name"),
            "ad_set_id": metrics.get("ad_set_id"),
            "ad_id": metrics.get("ad_id"),
            "impressions": metrics.get("impressions", 0),
            "clicks": metrics.get("clicks", 0),
            "spend": metrics.get("spend", 0),
            "cpc": metrics.get("cpc", 0),
            "cpm": metrics.get("cpm", 0),
            "ctr": metrics.get("ctr", 0),
            "conversions": metrics.get("conversions", 0),
            "conversion_value": metrics.get("conversion_value", 0),
            "roas": metrics.get("roas", 0),
            "frequency": metrics.get("frequency", 0),
            "reach": metrics.get("reach", 0),
            "metadata": metrics.get("metadata", {}),
            "recorded_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self._request("POST", "meta_ads_metrics", data)
    
    async def get_meta_ads_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get Meta Ads metrics for specified period"""
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        endpoint = f"meta_ads_metrics?recorded_at=gte.{start_date}&order=recorded_at.desc"
        
        return await self._request("GET", endpoint)
    
    # Landing Page Metrics
    async def store_landing_page_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Store landing page performance metrics"""
        data = {
            "page_url": metrics.get("page_url", config.LANDING_PAGE_URL),
            "visitors": metrics.get("visitors", 0),
            "page_views": metrics.get("page_views", 0),
            "unique_visitors": metrics.get("unique_visitors", 0),
            "bounce_rate": metrics.get("bounce_rate", 0),
            "avg_session_duration": metrics.get("avg_session_duration", 0),
            "conversions": metrics.get("conversions", 0),
            "conversion_rate": metrics.get("conversion_rate", 0),
            "traffic_sources": metrics.get("traffic_sources", {}),
            "devices": metrics.get("devices", {}),
            "locations": metrics.get("locations", {}),
            "metadata": metrics.get("metadata", {}),
            "recorded_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self._request("POST", "landing_page_metrics", data)
    
    # ML Processing Logs
    async def store_ml_processing_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store ML processing results and performance"""
        data = {
            "processing_type": log_data.get("processing_type", "ultralytics"),
            "model_used": log_data.get("model_used", config.ULTRALYTICS_MODEL),
            "input_data_type": log_data.get("input_data_type"),  # image, video, text
            "processing_time_ms": log_data.get("processing_time_ms", 0),
            "confidence_score": log_data.get("confidence_score", 0),
            "results": log_data.get("results", {}),
            "success": log_data.get("success", True),
            "error_message": log_data.get("error_message"),
            "metadata": log_data.get("metadata", {}),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self._request("POST", "ml_processing_logs", data)
    
    # Comprehensive Analytics
    async def get_comprehensive_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics across all platforms"""
        youtube_data = await self.get_youtube_metrics(days)
        spotify_data = await self.get_spotify_metrics(days)
        meta_ads_data = await self.get_meta_ads_metrics(days)
        
        return {
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "youtube": {
                "total_records": len(youtube_data),
                "latest_metrics": youtube_data[0] if youtube_data else None,
                "data": youtube_data
            },
            "spotify": {
                "total_records": len(spotify_data),
                "latest_metrics": spotify_data[0] if spotify_data else None,
                "data": spotify_data
            },
            "meta_ads": {
                "total_records": len(meta_ads_data),
                "latest_metrics": meta_ads_data[0] if meta_ads_data else None,
                "data": meta_ads_data
            }
        }


# Global Supabase client instance
supabase_client = SupabaseClient()


async def init_supabase_tables():
    """Initialize Supabase tables if they don't exist"""
    # This would typically be done through Supabase dashboard or migrations
    # Here we just verify connection
    try:
        # Test connection
        await supabase_client._request("GET", "youtube_metrics?limit=1")
        print("✅ Supabase connection verified")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test Supabase integration
    async def test_supabase():
        success = await init_supabase_tables()
        if success:
            # Test storing sample data
            test_youtube = {
                "video_id": "test_video_123",
                "title": "Test Video",
                "views": 1000,
                "likes": 50
            }
            
            result = await supabase_client.store_youtube_metrics(test_youtube)
            print("Test result:", result)
    
    asyncio.run(test_supabase())