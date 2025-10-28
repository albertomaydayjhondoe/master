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

# Copy requirements first (for better Docker layer caching)
COPY requirements-streamlit.txt requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-streamlit.txt

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

# Expose default port (Railway will override with PORT env var)
EXPOSE 8501

# Health check with dynamic port
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
if [ "$APP_TYPE" = "api" ]; then\n\
    echo "Starting FastAPI server on port ${PORT:-8000}"\n\
    exec uvicorn ml_core.api.main:app --host 0.0.0.0 --port ${PORT:-8000}\n\
else\n\
    echo "Starting Streamlit dashboard on port ${PORT:-8501}"\n\
    exec streamlit run scripts/viral_study_analysis.py \\\n\
        --server.port ${PORT:-8501} \\\n\
        --server.address 0.0.0.0 \\\n\
        --server.headless true \\\n\
        --server.enableCORS false \\\n\
        --server.enableXsrfProtection false \\\n\
        --browser.gatherUsageStats false\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Start using the script
CMD ["/app/start.sh"]
