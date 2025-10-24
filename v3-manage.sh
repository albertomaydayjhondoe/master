#!/bin/bash

# ============================================
# UNIFIED SYSTEM V3 - Management CLI
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════╗
    ║   🚀 UNIFIED SYSTEM V3                        ║
    ║   Community Manager - Complete Workflow       ║
    ╚═══════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Help
show_help() {
    echo -e "${CYAN}USAGE:${NC}"
    echo "  ./v3-manage.sh [command] [options]"
    echo ""
    echo -e "${CYAN}COMMANDS:${NC}"
    echo ""
    echo -e "  ${GREEN}test-workflow${NC}"
    echo "    Test complete viral campaign workflow (dummy mode)"
    echo ""
    echo -e "  ${GREEN}launch-campaign${NC}"
    echo "    Launch viral campaign via CLI"
    echo "    Options: --artist, --song, --video, --budget, --countries"
    echo ""
    echo -e "  ${GREEN}dashboard${NC}"
    echo "    Start Community Manager dashboard (Streamlit)"
    echo "    Options: --port (default: 8502)"
    echo ""
    echo -e "  ${GREEN}analytics${NC}"
    echo "    Get current campaign analytics"
    echo ""
    echo -e "  ${GREEN}optimize${NC}"
    echo "    Run ML optimization on active campaign"
    echo ""
    echo -e "  ${GREEN}status${NC}"
    echo "    Show system status (all services)"
    echo ""
    echo -e "  ${GREEN}docker-build${NC}"
    echo "    Build Docker v3 images (unified system)"
    echo ""
    echo -e "  ${GREEN}docker-up${NC}"
    echo "    Start all Docker v3 services"
    echo ""
    echo -e "  ${GREEN}docker-down${NC}"
    echo "    Stop all Docker v3 services"
    echo ""
    echo -e "  ${GREEN}logs${NC}"
    echo "    Show logs for a service"
    echo "    Options: --service [name]"
    echo ""
    echo -e "  ${GREEN}health${NC}"
    echo "    Check health of all services"
    echo ""
    echo -e "${CYAN}EXAMPLES:${NC}"
    echo ""
    echo "  # Test workflow"
    echo "  ./v3-manage.sh test-workflow"
    echo ""
    echo "  # Launch campaign via CLI"
    echo "  ./v3-manage.sh launch-campaign \\"
    echo "    --artist \"Bad Bunny\" \\"
    echo "    --song \"Monaco\" \\"
    echo "    --video \"/data/videos/monaco.mp4\" \\"
    echo "    --budget 200 \\"
    echo "    --countries \"US,MX,PR,ES\""
    echo ""
    echo "  # Start dashboard"
    echo "  ./v3-manage.sh dashboard"
    echo ""
    echo "  # Get analytics"
    echo "  ./v3-manage.sh analytics"
    echo ""
}

# Test Workflow
test_workflow() {
    echo -e "${BLUE}🧪 Testing Unified System V3 Workflow...${NC}\n"
    
    python unified_system_v3.py
    
    echo -e "\n${GREEN}✅ Test completed!${NC}"
}

# Launch Campaign
launch_campaign() {
    echo -e "${BLUE}🚀 Launching Viral Campaign...${NC}\n"
    
    # Parse options
    ARTIST=""
    SONG=""
    VIDEO=""
    BUDGET=50
    COUNTRIES="US,MX,ES"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --artist)
                ARTIST="$2"
                shift 2
                ;;
            --song)
                SONG="$2"
                shift 2
                ;;
            --video)
                VIDEO="$2"
                shift 2
                ;;
            --budget)
                BUDGET="$2"
                shift 2
                ;;
            --countries)
                COUNTRIES="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    # Validation
    if [ -z "$ARTIST" ] || [ -z "$SONG" ] || [ -z "$VIDEO" ]; then
        echo -e "${RED}❌ Error: --artist, --song, and --video are required${NC}"
        echo ""
        echo "Example:"
        echo "  ./v3-manage.sh launch-campaign \\"
        echo "    --artist \"Bad Bunny\" \\"
        echo "    --song \"Monaco\" \\"
        echo "    --video \"/data/videos/monaco.mp4\""
        exit 1
    fi
    
    # Create Python script to launch campaign
    cat > /tmp/launch_campaign.py << EOF
import asyncio
from unified_system_v3 import UnifiedCommunityManagerSystem

async def main():
    system = UnifiedCommunityManagerSystem(dummy_mode=True)
    
    results = await system.launch_viral_video_campaign(
        video_path="$VIDEO",
        artist_name="$ARTIST",
        song_name="$SONG",
        genre="Trap",
        daily_ad_budget=float($BUDGET),
        target_countries="$COUNTRIES".split(",")
    )
    
    print(f"\n{'='*60}")
    print(f"CAMPAIGN LAUNCHED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Campaign ID: {results['campaign_id']}")
    print(f"Platforms: {len(results['platforms'])}")
    print(f"Budget: \${$BUDGET}/day")
    print(f"Countries: $COUNTRIES")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    python /tmp/launch_campaign.py
    rm /tmp/launch_campaign.py
    
    echo -e "\n${GREEN}✅ Campaign launched!${NC}"
}

# Start Dashboard
start_dashboard() {
    echo -e "${BLUE}🎨 Starting Community Manager Dashboard...${NC}\n"
    
    PORT=8502
    
    # Parse port option
    if [ "$1" == "--port" ]; then
        PORT=$2
    fi
    
    echo -e "${CYAN}Dashboard URL:${NC} http://localhost:$PORT"
    echo -e "${YELLOW}Press CTRL+C to stop${NC}\n"
    
    streamlit run community_manager_dashboard.py \
        --server.port $PORT \
        --server.address 0.0.0.0
}

# Get Analytics
get_analytics() {
    echo -e "${BLUE}📊 Getting Campaign Analytics...${NC}\n"
    
    cat > /tmp/get_analytics.py << EOF
import asyncio
import json
from unified_system_v3 import UnifiedCommunityManagerSystem

async def main():
    system = UnifiedCommunityManagerSystem(dummy_mode=True)
    
    # Check if campaign exists
    if not system.current_campaign:
        print("❌ No active campaign found")
        print("\nLaunch a campaign first:")
        print("  ./v3-manage.sh launch-campaign --artist \"Artist\" --song \"Song\" --video \"/path/to/video.mp4\"")
        return
    
    analytics = await system.get_campaign_analytics()
    
    print(json.dumps(analytics, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    python /tmp/get_analytics.py
    rm /tmp/get_analytics.py
}

# Optimize Campaign
optimize_campaign() {
    echo -e "${BLUE}🎯 Optimizing Active Campaign...${NC}\n"
    
    cat > /tmp/optimize.py << EOF
import asyncio
import json
from unified_system_v3 import UnifiedCommunityManagerSystem

async def main():
    system = UnifiedCommunityManagerSystem(dummy_mode=True)
    
    if not system.current_campaign:
        print("❌ No active campaign found")
        return
    
    optimizations = await system.optimize_ongoing_campaign()
    
    print(f"\n{'='*60}")
    print(f"OPTIMIZATIONS APPLIED: {optimizations.get('optimizations_applied', 0)}")
    print(f"{'='*60}\n")
    
    for opt in optimizations.get('optimizations', []):
        print(f"🔧 {opt['action'].replace('_', ' ').title()}")
        print(f"   Platform: {opt['platform']}")
        print(f"   Reason: {opt['reason']}\n")
    
    print(f"Estimated Impact: {optimizations.get('estimated_impact', 'N/A')}\n")

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    python /tmp/optimize.py
    rm /tmp/optimize.py
    
    echo -e "${GREEN}✅ Optimization completed!${NC}"
}

# System Status
show_status() {
    echo -e "${BLUE}📊 System Status${NC}\n"
    
    echo -e "${CYAN}Python Environment:${NC}"
    python --version
    echo ""
    
    echo -e "${CYAN}Required Packages:${NC}"
    packages=("streamlit" "asyncio" "fastapi" "httpx")
    for pkg in "${packages[@]}"; do
        if python -c "import $pkg" 2>/dev/null; then
            echo -e "  ✅ $pkg"
        else
            echo -e "  ❌ $pkg ${RED}(missing)${NC}"
        fi
    done
    echo ""
    
    echo -e "${CYAN}Services Status:${NC}"
    
    # Check if dashboard is running
    if lsof -Pi :8502 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "  🟢 Dashboard (port 8502)"
    else
        echo -e "  ⚫ Dashboard (stopped)"
    fi
    
    # Check Docker v1
    if docker ps --filter "name=ml-core" --format "{{.Names}}" 2>/dev/null | grep -q ml-core; then
        echo -e "  🟢 Docker v1 (running)"
    else
        echo -e "  ⚫ Docker v1 (stopped)"
    fi
    
    # Check Docker v2
    if docker ps --filter "name=meta-ads-manager" --format "{{.Names}}" 2>/dev/null | grep -q meta-ads-manager; then
        echo -e "  🟢 Docker v2 (running)"
    else
        echo -e "  ⚫ Docker v2 (stopped)"
    fi
    
    echo ""
}

# Docker Build
docker_build() {
    echo -e "${BLUE}🐳 Building Docker V3 Images...${NC}\n"
    
    if [ ! -f "docker-compose-v3.yml" ]; then
        echo -e "${YELLOW}⚠️  docker-compose-v3.yml not found yet${NC}"
        echo "This will be created after testing phase"
        exit 1
    fi
    
    docker-compose -f docker-compose-v3.yml build
    
    echo -e "\n${GREEN}✅ Docker images built!${NC}"
}

# Docker Up
docker_up() {
    echo -e "${BLUE}🐳 Starting Docker V3 Services...${NC}\n"
    
    if [ ! -f "docker-compose-v3.yml" ]; then
        echo -e "${YELLOW}⚠️  docker-compose-v3.yml not found yet${NC}"
        echo "This will be created after testing phase"
        exit 1
    fi
    
    docker-compose -f docker-compose-v3.yml up -d
    
    echo -e "\n${GREEN}✅ All services started!${NC}"
    echo -e "\nAccess points:"
    echo "  - Unified Orchestrator: http://localhost:10000"
    echo "  - Dashboard: http://localhost:8502"
    echo "  - ML Core: http://localhost:8000"
    echo "  - Meta Ads Manager: http://localhost:9000"
}

# Docker Down
docker_down() {
    echo -e "${BLUE}🐳 Stopping Docker V3 Services...${NC}\n"
    
    if [ ! -f "docker-compose-v3.yml" ]; then
        echo -e "${YELLOW}⚠️  docker-compose-v3.yml not found yet${NC}"
        exit 0
    fi
    
    docker-compose -f docker-compose-v3.yml down
    
    echo -e "\n${GREEN}✅ All services stopped!${NC}"
}

# Show Logs
show_logs() {
    SERVICE=""
    
    if [ "$1" == "--service" ]; then
        SERVICE=$2
    else
        echo -e "${RED}❌ Error: --service is required${NC}"
        echo "Example: ./v3-manage.sh logs --service unified-orchestrator"
        exit 1
    fi
    
    if [ ! -f "docker-compose-v3.yml" ]; then
        echo -e "${YELLOW}⚠️  docker-compose-v3.yml not found yet${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}📋 Logs for $SERVICE:${NC}\n"
    
    docker-compose -f docker-compose-v3.yml logs -f $SERVICE
}

# Health Check
health_check() {
    echo -e "${BLUE}🏥 Health Check${NC}\n"
    
    echo -e "${CYAN}Checking services...${NC}\n"
    
    # Check unified system script
    if [ -f "unified_system_v3.py" ]; then
        echo -e "  ✅ unified_system_v3.py"
    else
        echo -e "  ❌ unified_system_v3.py ${RED}(missing)${NC}"
    fi
    
    # Check dashboard
    if [ -f "community_manager_dashboard.py" ]; then
        echo -e "  ✅ community_manager_dashboard.py"
    else
        echo -e "  ❌ community_manager_dashboard.py ${RED}(missing)${NC}"
    fi
    
    # Check dependencies
    echo -e "\n${CYAN}Checking dependencies...${NC}\n"
    
    if python -c "import unified_system_v3" 2>/dev/null; then
        echo -e "  ✅ Python imports working"
    else
        echo -e "  ❌ Python imports ${RED}(failed)${NC}"
    fi
    
    # Test dummy mode
    echo -e "\n${CYAN}Testing dummy mode...${NC}\n"
    
    python -c "
from unified_system_v3 import UnifiedCommunityManagerSystem
system = UnifiedCommunityManagerSystem(dummy_mode=True)
print('  ✅ Dummy mode working')
" 2>/dev/null || echo -e "  ❌ Dummy mode ${RED}(failed)${NC}"
    
    echo ""
}

# ============================================
# MAIN
# ============================================

print_banner

# Check arguments
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

COMMAND=$1
shift

case $COMMAND in
    test-workflow)
        test_workflow "$@"
        ;;
    launch-campaign)
        launch_campaign "$@"
        ;;
    dashboard)
        start_dashboard "$@"
        ;;
    analytics)
        get_analytics
        ;;
    optimize)
        optimize_campaign
        ;;
    status)
        show_status
        ;;
    docker-build)
        docker_build
        ;;
    docker-up)
        docker_up
        ;;
    docker-down)
        docker_down
        ;;
    logs)
        show_logs "$@"
        ;;
    health)
        health_check
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
