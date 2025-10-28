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

# We'll install packages directly without requirements.txt to avoid conflicts
# COPY requirements*.txt ./

# Copy and install only Streamlit requirements
COPY requirements-streamlit.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-streamlit.txt

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

# Expose default port (Railway will override with PORT env var)
EXPOSE 8501

# Health check with dynamic port
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Start Streamlit dashboard with dynamic port
CMD streamlit run scripts/viral_study_analysis.py \
    --server.port ${PORT:-8501} \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false
