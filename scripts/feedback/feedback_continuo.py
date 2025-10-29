"""
Feedback continuo para Meta Ads/ML.
Escucha resultados nuevos y actualiza el sistema en tiempo real.
Integrable con n8n vía webhook o trigger.
"""
import requests
from datetime import datetime

# Configuración
ML_API_URL = "http://localhost:8000/feedback_update"  # Endpoint a implementar en main


def procesar_nuevo_resultado(resultado):
    # resultado: dict con info de campaña/optimización
    try:
        r = requests.post(ML_API_URL, json=resultado)
        print(f"[{datetime.now()}] Feedback enviado: {r.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] Error enviando feedback: {e}")

# Ejemplo de integración con n8n:
# 1. n8n detecta nuevo resultado y llama este script vía subprocess o API
# 2. O bien, este script expone un endpoint Flask/FastAPI para recibir triggers

if __name__ == "__main__":
    # Ejemplo de uso manual
    resultado_ejemplo = {
        "timestamp": datetime.utcnow().isoformat(),
        "campaign_id": 789,
        "cpa": 1.5,
        "roas": 3.5
    }
    procesar_nuevo_resultado(resultado_ejemplo)
