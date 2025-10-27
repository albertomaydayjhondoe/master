# TikTok ML Automation System - Fixed Dockerfile
# Production-ready container for ML processing and automation

FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Environment variables
ENV DUMMY_MODE=true
ENV PORT=8000
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install ML dependencies
RUN pip install --no-cache-dir \
    ultralytics==8.1.0 \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-dotenv==1.0.0 \
    pydantic==2.4.2 \
    httpx==0.25.0 \
    python-multipart==0.0.6 \
    pillow==10.1.0 \
    torch \
    torchvision \
    opencv-python-headless \
    numpy \
    scikit-learn \
    pandas \
    prometheus-client==0.18.0 \
    python-json-logger==2.0.7

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/models /app/logs /app/uploads

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE $PORT

# Start the application
CMD ["python", "-m", "uvicorn", "ml_core.api.main:app", "--host", "0.0.0.0", "--port", "8000"]