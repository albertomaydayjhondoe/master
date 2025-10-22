"""
Cliente Python para el sistema de marketing musical automatizado.
"""
from typing import Dict, Any, List, Optional
import httpx
import asyncio
from datetime import datetime

class MetaMarketingClient:
    """
    Cliente asíncrono para integrar con el sistema de marketing musical.
    
    Ejemplo:
        ```python
        async with MetaMarketingClient("http://localhost:8000", "your_api_key") as client:
            # Analizar video
            analysis = await client.analyze_video("video123")
            if analysis["safe_for_ads"]:
                # Generar variaciones
                variations = await client.generate_variations(
                    video_id="video123",
                    segment_index=0
                )
                # Crear campaña
                campaign = await client.create_campaign(
                    video_id="video123",
                    pixel_id="pixel_trap",
                    genre="trap",
                    budget=100.0
                )
                # Optimizar
                optimization = await client.optimize_campaign(
                    campaign_id=campaign["campaign_id"]
                )
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str = None,
        timeout: float = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "dummy_development_key"
        self.timeout = timeout
        self._client = None
        
    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-API-Key": self.api_key},
            timeout=self.timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        await self._client.aclose()
        
    async def analyze_video(self, video_id: str) -> Dict[str, Any]:
        """Analizar video y obtener segmentos sugeridos."""
        response = await self._client.post(
            "/api/v1/meta/analyze-video",
            params={"video_id": video_id}
        )
        response.raise_for_status()
        return response.json()
        
    async def generate_variations(
        self,
        video_id: str,
        segment_index: int,
        count: int = 5
    ) -> Dict[str, Any]:
        """Generar variaciones de anuncios para un segmento."""
        response = await self._client.post(
            "/api/v1/meta/generate-variations",
            params={
                "video_id": video_id,
                "segment_index": segment_index,
                "count": count
            }
        )
        response.raise_for_status()
        return response.json()
        
    async def create_campaign(
        self,
        video_id: str,
        pixel_id: str,
        genre: str,
        budget: float
    ) -> Dict[str, Any]:
        """Crear nueva campaña publicitaria."""
        response = await self._client.post(
            "/api/v1/meta/create-campaign",
            json={
                "video_id": video_id,
                "pixel_id": pixel_id,
                "genre": genre,
                "budget": budget
            }
        )
        response.raise_for_status()
        return response.json()
        
    async def optimize_campaign(
        self,
        campaign_id: str,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Obtener recomendaciones de optimización ML."""
        if date_range is None:
            # Default to last 7 days
            date_range = {
                "start": (datetime.now() - timedelta(days=7)).isoformat(),
                "end": datetime.now().isoformat()
            }
            
        response = await self._client.post(
            "/api/v1/meta/optimize-campaign",
            json={
                "campaign_id": campaign_id,
                "date_range": date_range
            }
        )
        response.raise_for_status()
        return response.json()