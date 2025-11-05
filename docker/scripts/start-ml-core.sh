#!/bin/bash
# 🧠 Neural Forge - ML Core Startup Script

set -e

echo "🧠 Starting Neural Forge ML Core..."

# Create model directories
echo "📁 Creating model directories..."
mkdir -p /app/data/models/production
mkdir -p /app/data/models/checkpoints
mkdir -p /app/data/torch_cache

# Download required models if in production mode
if [ "${ML_PRODUCTION_MODE}" = "true" ]; then
    echo "📥 Downloading production models..."
    # Add model download logic here
    echo "⚠️ Production models not yet configured - using dummy mode"
fi

# Start the application
echo "🚀 Starting ML Core API on port 8000..."
cd /app
exec uvicorn ml_core.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --access-log \
    --use-colors