# ═══════════════════════════════════════════════════════════
# Dockerfile: Dashboard V3
# Streamlit UI para gestión de campañas
# ═══════════════════════════════════════════════════════════

FROM python:3.11-slim

LABEL maintainer="Community Manager System V3"
LABEL version="3.0"
LABEL description="Dashboard UI - Streamlit para gestión de campañas"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements
COPY requirements.txt requirements-dev.txt ./

# Instalar dependencias Python + Streamlit
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit plotly pandas

# Copiar código
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Exponer puerto Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando Streamlit
CMD ["streamlit", "run", "dashboard_v3.py", "--server.port=8501", "--server.address=0.0.0.0"]
