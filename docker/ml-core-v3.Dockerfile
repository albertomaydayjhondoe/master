# ═══════════════════════════════════════════════════════════
# Dockerfile: ML Core V3
# YOLOv8 + ML predictions
# ═══════════════════════════════════════════════════════════

FROM python:3.11-slim

LABEL maintainer="Community Manager System V3"
LABEL version="3.0"
LABEL description="ML Core - YOLOv8 analysis + ML predictions"

# Instalar dependencias del sistema (necesarias para OpenCV)
RUN apt-get update && apt-get install -y \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt requirements-dev.txt ./

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir ultralytics opencv-python-headless pillow

# Copiar código
COPY . .

# Crear directorios para modelos
RUN mkdir -p /app/data/models/production \
    /app/data/models/checkpoints \
    /app/logs

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DUMMY_MODE=false

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "ml_core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
