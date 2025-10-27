"""
Spotify Analytics Client
Integrates with Spotify Web API for analytics and metrics collection
Stores data in Supabase for comprehensive reporting
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import base64
from config.production_config import get_config
from integrations.supabase_client import supabase_client

config = get_config()

class SpotifyClient:
    """Spotify API client for analytics and data collection"""
    
    def __init__(self):
        self.client_id = config.SPOTIFY_CLIENT_ID
        self.client_secret = config.SPOTIFY_CLIENT_SECRET
        self.artist_ids = config.SPOTIFY_ARTIST_IDS
        self.playlist_ids = config.SPOTIFY_PLAYLIST_IDS
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.client = httpx.AsyncClient()
        self.access_token = None
        self.token_expires_at = None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def get_access_token(self) -> Optional[str]:
        """Get Spotify access token using client credentials flow"""
        try:
            # Check if current token is still valid
            if (self.access_token and self.token_expires_at and 
                datetime.utcnow() < self.token_expires_at - timedelta(minutes=5)):
                return self.access_token
            
            # Get new token
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {"grant_type": "client_credentials"}
            
            response = await self.client.post(self.auth_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                return self.access_token
            
            return None
            
        except Exception as e:
            print(f"Error getting Spotify access token: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Test Spotify API connection"""
        try:
            token = await self.get_access_token()
            if not token:
                return False
            
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{self.base_url}/browse/categories", headers=headers)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Spotify connection test failed: {e}")
            return False
    
    async def get_artist_info(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed artist information"""
        try:
            token = await self.get_access_token()
            if not token:
                return None
            
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{self.base_url}/artists/{artist_id}", headers=headers)
            
            if response.status_code == 200:
                artist = response.json()
                return {
                    "artist_id": artist["id"],
                    "name": artist["name"],
                    "followers": artist["followers"]["total"],
                    "genres": artist["genres"],
                    "popularity": artist["popularity"],
                    "image_url": artist["images"][0]["url"] if artist["images"] else "",
                    "external_urls": artist["external_urls"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching artist info: {e}")
            return None
    
    async def get_artist_top_tracks(self, artist_id: str, country: str = "US") -> List[Dict[str, Any]]:
        """Get artist's top tracks"""
        try:
            token = await self.get_access_token()
            if not token:
                return []
            
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{self.base_url}/artists/{artist_id}/top-tracks"
            params = {"country": country}
            
            response = await self.client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                tracks = []
                
                for track in data["tracks"]:
                    track_info = {
                        "track_id": track["id"],
                        "name": track["name"],
                        "album": track["album"]["name"],
                        "popularity": track["popularity"],
                        "duration_ms": track["duration_ms"],
                        "explicit": track["explicit"],
                        "preview_url": track.get("preview_url"),
                        "external_urls": track["external_urls"]
                    }
                    tracks.append(track_info)
                
                return tracks
            
            return []
            
        except Exception as e:
            print(f"Error fetching artist top tracks: {e}")
            return []
    
    async def get_artist_albums(self, artist_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get artist's albums"""
        try:
            token = await self.get_access_token()
            if not token:
                return []
            
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{self.base_url}/artists/{artist_id}/albums"
            params = {
                "include_groups": "album,single",
                "market": "US",
                "limit": limit
            }
            
            response = await self.client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                albums = []
                
                for album in data["items"]:
                    album_info = {
                        "album_id": album["id"],
                        "name": album["name"],
                        "album_type": album["album_type"],
                        "release_date": album["release_date"],
                        "total_tracks": album["total_tracks"],
                        "image_url": album["images"][0]["url"] if album["images"] else "",
                        "external_urls": album["external_urls"]
                    }
                    albums.append(album_info)
                
                return albums
            
            return []
            
        except Exception as e:
            print(f"Error fetching artist albums: {e}")
            return []
    
    async def get_playlist_info(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Get playlist information and tracks"""
        try:
            token = await self.get_access_token()
            if not token:
                return None
            
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.get(f"{self.base_url}/playlists/{playlist_id}", headers=headers)
            
            if response.status_code == 200:
                playlist = response.json()
                
                # Get tracks
                tracks_info = []
                tracks = playlist["tracks"]["items"]
                
                for item in tracks[:50]:  # Limit to 50 tracks
                    if item["track"]:
                        track = item["track"]
                        track_info = {
                            "track_id": track["id"],
                            "name": track["name"],
                            "artist": track["artists"][0]["name"] if track["artists"] else "",
                            "album": track["album"]["name"],
                            "popularity": track["popularity"],
                            "duration_ms": track["duration_ms"],
                            "added_at": item["added_at"]
                        }
                        tracks_info.append(track_info)
                
                return {
                    "playlist_id": playlist["id"],
                    "name": playlist["name"],
                    "description": playlist.get("description", ""),
                    "followers": playlist["followers"]["total"],
                    "total_tracks": playlist["tracks"]["total"],
                    "public": playlist["public"],
                    "collaborative": playlist["collaborative"],
                    "tracks": tracks_info,
                    "image_url": playlist["images"][0]["url"] if playlist["images"] else "",
                    "external_urls": playlist["external_urls"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching playlist info: {e}")
            return None
    
    async def get_artist_analytics(self, artist_id: str) -> Dict[str, Any]:
        """Get comprehensive artist analytics"""
        try:
            # Get artist info
            artist_info = await self.get_artist_info(artist_id)
            if not artist_info:
                return {"error": f"Artist {artist_id} not found"}
            
            # Get top tracks
            top_tracks = await self.get_artist_top_tracks(artist_id)
            
            # Get albums
            albums = await self.get_artist_albums(artist_id)
            
            # Calculate analytics
            avg_popularity = sum(track["popularity"] for track in top_tracks) / len(top_tracks) if top_tracks else 0
            total_duration_mins = sum(track["duration_ms"] for track in top_tracks) / 60000 if top_tracks else 0
            
            analytics = {
                "artist_id": artist_id,
                "artist_info": artist_info,
                "top_tracks_count": len(top_tracks),
                "albums_count": len(albums),
                "avg_track_popularity": round(avg_popularity, 2),
                "total_top_tracks_duration_mins": round(total_duration_mins, 2),
                "top_tracks": top_tracks,
                "recent_albums": albums[:5],  # Most recent 5 albums
                "fetched_at": datetime.utcnow().isoformat()
            }
            
            # Store in Supabase
            await supabase_client.store_spotify_metrics(analytics)
            
            return analytics
            
        except Exception as e:
            print(f"Error fetching artist analytics: {e}")
            return {
                "artist_id": artist_id,
                "error": str(e),
                "fetched_at": datetime.utcnow().isoformat()
            }
    
    async def get_playlist_analytics(self, playlist_id: str) -> Dict[str, Any]:
        """Get playlist analytics"""
        try:
            playlist_info = await self.get_playlist_info(playlist_id)
            if not playlist_info:
                return {"error": f"Playlist {playlist_id} not found"}
            
            # Calculate analytics
            tracks = playlist_info["tracks"]
            if tracks:
                avg_popularity = sum(track["popularity"] for track in tracks) / len(tracks)
                total_duration_mins = sum(track["duration_ms"] for track in tracks) / 60000
                
                # Genre analysis (simplified)
                artists = [track["artist"] for track in tracks]
                unique_artists = len(set(artists))
                
                analytics = {
                    "playlist_id": playlist_id,
                    "playlist_info": {
                        "name": playlist_info["name"],
                        "followers": playlist_info["followers"],
                        "total_tracks": playlist_info["total_tracks"],
                        "public": playlist_info["public"]
                    },
                    "analytics": {
                        "avg_track_popularity": round(avg_popularity, 2),
                        "total_duration_mins": round(total_duration_mins, 2),
                        "unique_artists": unique_artists,
                        "tracks_analyzed": len(tracks)
                    },
                    "top_tracks": tracks[:10],  # Top 10 tracks
                    "fetched_at": datetime.utcnow().isoformat()
                }
            else:
                analytics = {
                    "playlist_id": playlist_id,
                    "error": "No tracks found",
                    "fetched_at": datetime.utcnow().isoformat()
                }
            
            # Store in Supabase
            await supabase_client.store_spotify_metrics(analytics)
            
            return analytics
            
        except Exception as e:
            print(f"Error fetching playlist analytics: {e}")
            return {
                "playlist_id": playlist_id,
                "error": str(e),
                "fetched_at": datetime.utcnow().isoformat()
            }
    
    async def search_trending_tracks(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for trending tracks"""
        try:
            token = await self.get_access_token()
            if not token:
                return []
            
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "q": query,
                "type": "track",
                "market": "US",
                "limit": limit
            }
            
            response = await self.client.get(f"{self.base_url}/search", headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                tracks = []
                
                for track in data["tracks"]["items"]:
                    track_info = {
                        "track_id": track["id"],
                        "name": track["name"],
                        "artist": track["artists"][0]["name"] if track["artists"] else "",
                        "album": track["album"]["name"],
                        "popularity": track["popularity"],
                        "duration_ms": track["duration_ms"],
                        "preview_url": track.get("preview_url"),
                        "external_urls": track["external_urls"]
                    }
                    tracks.append(track_info)
                
                return tracks
            
            return []
            
        except Exception as e:
            print(f"Error searching trending tracks: {e}")
            return []
    
    async def collect_all_analytics(self) -> Dict[str, Any]:
        """Collect analytics for all configured artists and playlists"""
        try:
            comprehensive_report = {
                "report_type": "spotify_comprehensive",
                "artists_analytics": {},
                "playlists_analytics": {},
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Collect artist analytics
            if self.artist_ids:
                for artist_id in self.artist_ids:
                    artist_analytics = await self.get_artist_analytics(artist_id)
                    comprehensive_report["artists_analytics"][artist_id] = artist_analytics
            
            # Collect playlist analytics
            if self.playlist_ids:
                for playlist_id in self.playlist_ids:
                    playlist_analytics = await self.get_playlist_analytics(playlist_id)
                    comprehensive_report["playlists_analytics"][playlist_id] = playlist_analytics
            
            # Calculate summary metrics
            total_followers = 0
            total_tracks = 0
            avg_popularity = 0
            
            for artist_data in comprehensive_report["artists_analytics"].values():
                if "artist_info" in artist_data:
                    total_followers += artist_data["artist_info"]["followers"]
                    total_tracks += artist_data["top_tracks_count"]
            
            for playlist_data in comprehensive_report["playlists_analytics"].values():
                if "playlist_info" in playlist_data:
                    total_followers += playlist_data["playlist_info"]["followers"]
            
            comprehensive_report["summary"] = {
                "total_artists": len(self.artist_ids) if self.artist_ids else 0,
                "total_playlists": len(self.playlist_ids) if self.playlist_ids else 0,
                "total_followers": total_followers,
                "total_tracks_analyzed": total_tracks
            }
            
            # Store comprehensive report
            await supabase_client.store_spotify_metrics(comprehensive_report)
            
            return comprehensive_report
            
        except Exception as e:
            print(f"Error collecting all Spotify analytics: {e}")
            return {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }

# Global client instance
spotify_client = SpotifyClient()

async def test_spotify_connection() -> bool:
    """Test Spotify API connection"""
    return await spotify_client.test_connection()

async def get_spotify_comprehensive_report() -> Dict[str, Any]:
    """Get comprehensive Spotify report"""
    return await spotify_client.collect_all_analytics()

# Cleanup function
async def cleanup_spotify_client():
    """Cleanup Spotify client resources"""
    await spotify_client.close()