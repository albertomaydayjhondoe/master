# 🚀 Stakas MVP Viral Dashboard - Bandwidth Optimized
FROM python:3.11-alpine

# Metadata
LABEL app="stakas-mvp-viral-dashboard"
LABEL channel="UCgohgqLVu1QPdfa64Vkrgeg" 
LABEL version="2.0-lightweight"

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apk add --no-cache curl

# Copy requirements first (for better Docker layer caching)
COPY requirements-minimal.txt ./

# Install minimal Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-minimal.txt

# Copy entire repository code
COPY . .

# Create directories
RUN mkdir -p data logs cache uploads

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Expose port for Railway
EXPOSE 8501

# Health check with Railway PORT
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Use lightweight Python launcher
CMD ["python", "app-lightweight.py"]
