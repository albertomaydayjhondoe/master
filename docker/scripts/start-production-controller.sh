#!/bin/bash
# 🎮 Neural Forge - Production Controller Startup Script

set -e

echo "🎮 Starting Neural Forge Production Controller..."

# Wait for dependencies
echo "⏳ Waiting for dependencies..."
wait-for-it postgres:5432 --timeout=60 --strict
wait-for-it ml-core:8000 --timeout=60 --strict

# Initialize database if needed
echo "🗄️ Initializing database..."
python -c "
import sqlite3
import os

os.makedirs('/app/data', exist_ok=True)
conn = sqlite3.connect('/app/data/production_control.db')
conn.execute('SELECT 1')
conn.close()
print('Database ready')
"

# Start the application
echo "🚀 Starting Production Controller on port 7860..."
cd /app
exec python production_controller.py