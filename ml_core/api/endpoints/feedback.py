"""
Endpoint para recibir feedback cíclico/continuo desde scripts o n8n.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Any, Dict, Optional

router = APIRouter()

class FeedbackPayload(BaseModel):
    timestamp: str
    resultados: Optional[Any] = None  # Puede ser lista o dict según integración
    campaign_id: Optional[int] = None
    cpa: Optional[float] = None
    roas: Optional[float] = None
    extra: Optional[Dict[str, Any]] = None

@router.post("/feedback_update", status_code=200)
async def feedback_update(payload: FeedbackPayload, request: Request):
    # Aquí se puede guardar el feedback, actualizar datasets, lanzar reentrenamiento, etc.
    # Para demo, solo loguea y responde OK
    print(f"[FEEDBACK] Recibido: {payload}")
    # TODO: Integrar con lógica de actualización ML/DB
    return {"status": "received", "timestamp": payload.timestamp}
