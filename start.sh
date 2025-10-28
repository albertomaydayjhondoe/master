#!/bin/bash

# Stakas MVP Startup Script - Railway Production
echo "🚀 STARTING STAKAS MVP SYSTEM"
echo "📺 Canal: UCgohgqLVu1QPdfa64Vkrgeg"
echo "🌍 Environment: ${RAILWAY_ENVIRONMENT:-production}"

# Set default port if not provided
export PORT=${PORT:-8501}

echo "🔧 PORT: $PORT"
echo "🎯 APP_TYPE: ${APP_TYPE:-dashboard}"

# Start the appropriate service
if [ "$APP_TYPE" = "api" ]; then
    echo "🚀 Starting FastAPI ML API on port $PORT"
    exec uvicorn ml_core.api.main:app --host 0.0.0.0 --port $PORT
else
    echo "📊 Starting Streamlit Dashboard on port $PORT"
    exec streamlit run scripts/viral_study_analysis.py \
        --server.port $PORT \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.enableCORS false \
        --server.enableXsrfProtection false \
        --browser.gatherUsageStats false
fi
