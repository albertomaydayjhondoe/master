#!/bin/bash
# 🛰️ Neural Forge - Meta Ads Startup Script

set -e

echo "🛰️ Starting Neural Forge Meta Ads Automation..."

# Wait for dependencies
echo "⏳ Waiting for dependencies..."
wait-for-it postgres:5432 --timeout=60 --strict

# Validate Meta credentials
echo "🔐 Validating Meta credentials..."
python -c "
import os
required_vars = ['META_APP_ID', 'META_APP_SECRET', 'META_ACCESS_TOKEN']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f'⚠️ Missing Meta credentials: {missing}')
    print('Running in dummy mode')
else:
    print('✅ Meta credentials validated')
"

# Start the application
echo "🚀 Starting Meta Ads API on port 8002..."
cd /app
exec uvicorn meta_automation.api.main:app \
    --host 0.0.0.0 \
    --port 8002 \
    --workers 1 \
    --access-log