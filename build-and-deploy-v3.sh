#!/bin/bash

# ═══════════════════════════════════════════════════════════
# 🐳 BUILD & DEPLOY V3
# Build Docker images y deploy del sistema completo
# ═══════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   🐳 Building Docker V3                              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════
# CHECK PREREQUISITES
# ═══════════════════════════════════════════════════════════

echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose first."
    exit 1
fi

if [ ! -f .env ]; then
    echo "⚠️ .env file not found."
    echo "   Run ./setup-credentials.sh first or copy .env.v3 to .env"
    read -p "Continue anyway? (y/n): " continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
fi

echo "✅ Prerequisites OK"
echo ""

# ═══════════════════════════════════════════════════════════
# BUILD IMAGES
# ═══════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔨 Building Docker images..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Build ML Core
echo "🤖 Building ML Core..."
docker build -f docker/ml-core-v3.Dockerfile -t community-manager/ml-core:v3 .
echo "✅ ML Core built"
echo ""

# Build Unified Orchestrator
echo "🚀 Building Unified Orchestrator..."
docker build -f docker/unified-orchestrator-v3.Dockerfile -t community-manager/unified-orchestrator:v3 .
echo "✅ Unified Orchestrator built"
echo ""

# Build Dashboard
echo "🎨 Building Dashboard..."
docker build -f docker/dashboard-v3.Dockerfile -t community-manager/dashboard:v3 .
echo "✅ Dashboard built"
echo ""

# ═══════════════════════════════════════════════════════════
# BUILD COMPLETE
# ═══════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All images built successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# List images
echo "📦 Docker images:"
docker images | grep "community-manager"
echo ""

# ═══════════════════════════════════════════════════════════
# ASK TO DEPLOY
# ═══════════════════════════════════════════════════════════

read -p "🚀 Deploy now with docker-compose? (y/n): " deploy

if [ "$deploy" = "y" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 Deploying Docker V3..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    docker-compose -f docker-compose-v3.yml up -d
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Deployment complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    echo "📡 Services starting..."
    sleep 5
    
    echo ""
    ./v3-docker.sh health
    
    echo ""
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║   🎉 SISTEMA V3 DEPLOYED!                            ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo ""
    echo "Access points:"
    echo "  - Dashboard:   http://localhost:8501"
    echo "  - API:         http://localhost:10000"
    echo "  - ML Core:     http://localhost:8000/docs"
    echo "  - n8n:         http://localhost:5678"
    echo "  - Grafana:     http://localhost:3000"
    echo ""
    echo "Next steps:"
    echo "  1. Open dashboard: http://localhost:8501"
    echo "  2. Configure n8n: ./n8n-setup.sh"
    echo "  3. Launch campaign or monitor channel"
    echo ""
else
    echo ""
    echo "ℹ️ Images built but not deployed."
    echo ""
    echo "To deploy later:"
    echo "  ./v3-docker.sh start"
    echo ""
    echo "Or manually:"
    echo "  docker-compose -f docker-compose-v3.yml up -d"
    echo ""
fi

echo "✅ Done!"
echo ""
