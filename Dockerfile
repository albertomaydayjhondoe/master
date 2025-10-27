# TikTok ML Automation System v4 - Production# TikTok ML API v3 - Original Simple Version

# Core system: n8n + ML Ultralytics + Landing Page + Meta Ads + SupabaseFROM python:3.11-slim



FROM python:3.11-slimWORKDIR /app



# System dependencies# Variables de entorno

RUN apt-get update && apt-get install -y \ENV PYTHONUNBUFFERED=1

    curl \ENV DUMMY_MODE=true

    gcc \ENV PORT=8000

    g++ \

    git \# Instalar dependencias básicas del sistema

    && rm -rf /var/lib/apt/lists/*RUN apt-get update && \

    apt-get install -y --no-install-recommends \

WORKDIR /app    curl \

    ca-certificates \

# Install Python dependencies    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \# Copiar requirements básicos

    pip install --no-cache-dir -r requirements.txtCOPY requirements.txt ./



# Install Ultralytics and ML dependencies# Instalar solo dependencias esenciales de FastAPI

RUN pip install --no-cache-dir \RUN pip install --no-cache-dir --upgrade pip && \

    ultralytics==8.1.0 \    pip install --no-cache-dir \

    torch torchvision \    fastapi==0.104.1 \

    opencv-python-headless \    uvicorn==0.24.0 \

    pillow \    python-dotenv==1.0.0 \

    numpy \    pydantic==2.4.2 \

    scikit-learn \    httpx==0.25.0 \

    pandas    python-multipart==0.0.6 \

    pillow==10.1.0 \

# Copy application    prometheus-client==0.18.0 \

COPY . .    python-json-logger==2.0.7



# Create directories# Copiar todo el código fuente

RUN mkdir -p /app/data/models /app/logs /app/uploadsCOPY . /app



# Environment variables# Crear usuario no-root para seguridad

ENV PYTHONPATH=/appRUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \

ENV PYTHONUNBUFFERED=1    chown -R appuser:appuser /app

ENV PRODUCTION_MODE=true

ENV PORT=8000USER appuser



# Health check# Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \

    CMD curl -f http://localhost:${PORT}/health || exit 1    CMD curl -f http://localhost:${PORT}/health || exit 1



EXPOSE $PORT# Exponer puerto

EXPOSE ${PORT}

CMD ["python", "-m", "uvicorn", "ml_core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Comando de inicio - usar la app original
CMD ["sh", "-c", "uvicorn ml_core.api.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]