# 🚀 Stakas MVP Viral Dashboard - Railway Production
FROM python:3.11-slim

# Metadata
LABEL app="stakas-mvp-viral-dashboard"
LABEL channel="UCgohgqLVu1QPdfa64Vkrgeg" 
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        streamlit==1.50.0 \
        matplotlib==3.10.7 \
        seaborn==0.13.2 \
        plotly==6.3.1 \
        pandas==2.3.2 \
        numpy==2.3.2

# Copy application code
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

# Expose port (Railway will set PORT env var)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:$PORT/_stcore/health || exit 1

# Start Streamlit dashboard
CMD streamlit run scripts/viral_study_analysis.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false
