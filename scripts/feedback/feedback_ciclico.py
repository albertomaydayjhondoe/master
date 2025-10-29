"""
Feedback cíclico automático para Meta Ads/ML.
Recolecta métricas periódicamente, actualiza datasets y lanza reentrenamiento/ajuste.
Integrable con n8n vía API o trigger programado.
"""
import time
import requests
from datetime import datetime

# Configuración
ML_API_URL = "http://localhost:8000/feedback_update"  # Endpoint a implementar en main
# Frecuencia de feedback cíclico: cada 5 días
INTERVAL_DAYS = 5
INTERVAL_HOURS = INTERVAL_DAYS * 24


def recolectar_metricas():
    # TODO: Implementar extracción real de métricas de campañas
    # Ejemplo dummy
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "resultados": [
            {"campaign_id": 123, "cpa": 2.1, "roas": 3.2},
            {"campaign_id": 456, "cpa": 1.8, "roas": 2.9},
        ]
    }

def enviar_feedback(data):
    try:
        r = requests.post(ML_API_URL, json=data)
        print(f"[{datetime.now()}] Feedback enviado: {r.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] Error enviando feedback: {e}")


def ciclo_feedback():
    while True:
        metricas = recolectar_metricas()
        enviar_feedback(metricas)
        print(f"[{datetime.now()}] Esperando {INTERVAL_DAYS} días para siguiente ciclo...")
        time.sleep(INTERVAL_DAYS * 24 * 3600)


if __name__ == "__main__":
    ciclo_feedback()
