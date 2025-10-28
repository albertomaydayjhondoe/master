# 🚀 Stakas Viral System - Railway Production
FROM python:3.11-slim

# Metadata
LABEL app="stakas-viral-system"
LABEL channel="UCgohgqLVu1QPdfa64Vkrgeg" 
LABEL version="3.0-production"

# Set working directory
WORKDIR /app

# Install system dependencies compatible with Debian Trixie
RUN apt-get update && apt-get install -y \
    git wget curl build-essential \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libgomp1 libgl1-mesa-dev libglu1-mesa-dev \
    libglfw3-dev libglew-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-ml.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit plotly pandas numpy scikit-learn opencv-python-headless fastapi uvicorn

# Copy application code
COPY . .

# Set proper permissions using setup script
RUN chmod +x setup_debian_permissions.sh && \
    ./setup_debian_permissions.sh

# Create directories
RUN mkdir -p data/models/production data/logs uploads cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DUMMY_MODE=false
ENV ENVIRONMENT=production
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/health || exit 1

# Start Railway simple launcher
CMD ["python", "railway_simple_launcher.py"]
