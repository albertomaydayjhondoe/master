"""API integration examples and usage guide.

This module provides examples of integrating with the TikTok Viral ML API
in both dummy and production modes.
"""
import httpx
import asyncio
from typing import Dict, Any
import os
from pathlib import Path


class MLClient:
    """Cliente para integrar con la API ML.
    
    Examples:
        ```python
        # Uso asíncrono
        async with MLClient("http://localhost:8000", "your_api_key") as client:
            # Analizar screenshot
            with open("screenshot.png", "rb") as f:
                result = await client.analyze_screenshot(f.read())
                
            # Detectar anomalías
            anomalies = await client.detect_anomaly(
                account_id="acc_123",
                recent_actions=["like", "follow"]
            )
            
            # Predecir mejor momento
            timing = await client.predict_posting_time(
                account_id="acc_123",
                timezone="Europe/Madrid"
            )
            
            # Calcular afinidad
            affinity = await client.calculate_affinity(
                account_ids=["acc_1", "acc_2"]
            )
        
        # Uso síncrono
        client = MLClient("http://localhost:8000", "your_api_key")
        try:
            result = client.analyze_screenshot_sync(screenshot_bytes)
            print(f"Detected {len(result['detected_elements'])} elements")
        finally:
            client.close()
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str = None,
        timeout: float = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("ML_API_KEY", "dummy_development_key")
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
        
    def close(self):
        """Cerrar cliente HTTP (uso síncrono)."""
        if hasattr(self, "_sync_client"):
            self._sync_client.close()
            
    def _get_sync_client(self):
        if not hasattr(self, "_sync_client"):
            self._sync_client = httpx.Client(
                base_url=self.base_url,
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
        return self._sync_client
            
    async def analyze_screenshot(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analizar screenshot usando el detector YOLO.
        
        Args:
            image_bytes: Bytes del archivo de imagen
            
        Returns:
            Dict con elementos detectados y recomendaciones
        """
        files = {"file": ("image.png", image_bytes, "image/png")}
        response = await self._client.post("/api/v1/analyze_screenshot", files=files)
        response.raise_for_status()
        return response.json()
    
    def analyze_screenshot_sync(self, image_bytes: bytes) -> Dict[str, Any]:
        """Versión síncrona de analyze_screenshot."""
        client = self._get_sync_client()
        files = {"file": ("image.png", image_bytes, "image/png")}
        response = client.post("/api/v1/analyze_screenshot", files=files)
        response.raise_for_status()
        return response.json()
        
    async def detect_anomaly(
        self,
        account_id: str,
        recent_actions: list = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Detectar anomalías para una cuenta.
        
        Args:
            account_id: ID de la cuenta a analizar
            recent_actions: Lista opcional de acciones recientes
            context: Contexto adicional opcional
            
        Returns:
            Dict con resultados de detección
        """
        data = {
            "account_id": account_id,
            "recent_actions": recent_actions or [],
            "context": context or {}
        }
        response = await self._client.post("/api/v1/detect_anomaly", json=data)
        response.raise_for_status()
        return response.json()
        
    async def predict_posting_time(
        self,
        account_id: str,
        timezone: str = "UTC",
        historical_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Predecir mejor momento para publicar.
        
        Args:
            account_id: ID de la cuenta
            timezone: Zona horaria para predicciones
            historical_data: Datos históricos opcionales
            
        Returns:
            Dict con predicciones y recomendaciones
        """
        data = {
            "account_id": account_id,
            "timezone": timezone,
            "historical_data": historical_data or {}
        }
        response = await self._client.post("/api/v1/predict_posting_time", json=data)
        response.raise_for_status()
        return response.json()
        
    async def calculate_affinity(
        self,
        account_ids: list,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calcular afinidad entre cuentas.
        
        Args:
            account_ids: Lista de IDs de cuenta
            context: Contexto adicional opcional
            
        Returns:
            Dict con scores de afinidad y recomendaciones
        """
        data = {
            "account_ids": account_ids,
            "context": context or {}
        }
        response = await self._client.post("/api/v1/calculate_affinity", json=data)
        response.raise_for_status()
        return response.json()


async def main():
    """Example usage of the ML client."""
    async with MLClient() as client:
        # Analyze a screenshot
        image_path = Path("examples/screenshot.png")
        if image_path.exists():
            result = await client.analyze_screenshot(image_path.read_bytes())
            print("Screenshot analysis:", result)
            
        # Detect anomalies
        anomalies = await client.detect_anomaly(
            account_id="test_account",
            recent_actions=["like", "follow", "comment"]
        )
        print("\nAnomaly detection:", anomalies)
        
        # Get posting time prediction
        timing = await client.predict_posting_time(
            account_id="test_account",
            timezone="Europe/Madrid"
        )
        print("\nPosting time prediction:", timing)
        
        # Calculate affinity
        affinity = await client.calculate_affinity(
            account_ids=["acc_1", "acc_2", "acc_3"]
        )
        print("\nAffinity calculation:", affinity)


if __name__ == "__main__":
    asyncio.run(main())