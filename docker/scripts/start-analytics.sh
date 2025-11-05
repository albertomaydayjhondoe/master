#!/bin/bash
# 📊 Neural Forge - Analytics Engine Startup Script

set -e

echo "📊 Starting Neural Forge Analytics Engine..."

# Wait for dependencies
echo "⏳ Waiting for dependencies..."
wait-for-it postgres:5432 --timeout=60 --strict

# Initialize analytics database
echo "🗄️ Initializing analytics database..."
python -c "
import sqlite3
import os

os.makedirs('/app/data', exist_ok=True)
conn = sqlite3.connect('/app/data/analytics_engine.db')
conn.execute('SELECT 1')
conn.close()
print('Analytics database ready')
"

# Start the application
echo "🚀 Starting Analytics Engine on port 8501..."
cd /app
exec streamlit run analytics_engine.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false