# ═══════════════════════════════════════════════════════════
# Dockerfile: Unified Orchestrator V3
# Servicio principal que coordina todo el sistema V3
# ═══════════════════════════════════════════════════════════

FROM python:3.11-slim

LABEL maintainer="Community Manager System V3"
LABEL version="3.0"
LABEL description="Unified Orchestrator - Sistema completo de auto-viralización"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero (cache layer)
COPY requirements.txt requirements-dev.txt ./

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/data/videos \
    /app/data/models \
    /app/logs \
    /app/data/screenshots

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DUMMY_MODE=false

# Exponer puerto
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "unified_orchestrator_api:app", "--host", "0.0.0.0", "--port", "10000"]
