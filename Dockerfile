# Dockerfile Optimizado para Producción - Stakas MVP Viral System
# Multi-stage build con mejores prácticas de seguridad y performance

# ==============================================================================
# STAGE 1: Base Dependencies
# ==============================================================================
FROM python:3.11-slim as base

# Metadata
LABEL maintainer="Stakas MVP Team"
LABEL description="Stakas MVP Viral System - TikTok Automation 24/7"
LABEL version="1.0.0"

# Configurar timezone
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# System dependencies optimizadas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-railway.txt requirements-dummy.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-railway.txt && \
    pip install --no-cache-dir -r requirements-dummy.txt

# Copy application code
COPY . .

# Create necessary directories with correct permissions
RUN mkdir -p /app/data/models/production /app/logs /app/config/secrets && \
    mkdir -p /app/uploads /app/cache

# Create non-root user for security
RUN groupadd -r stakas && useradd -r -g stakas -s /bin/false stakas && \
    chown -R stakas:stakas /app

# Install application if setup.py exists
RUN if [ -f "setup.py" ]; then pip install --no-cache-dir -e .; fi

# Switch to non-root user
USER stakas

# Health check optimizado
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE 8080

# Start the Streamlit application
CMD ["streamlit", "run", "railway_main.py", "--server.port", "8080", "--server.address", "0.0.0.0", "--server.headless", "true"]