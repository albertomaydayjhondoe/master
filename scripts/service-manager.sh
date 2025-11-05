#!/bin/bash
# 🔄 Neural Forge - Service Management
# ===================================
# Manage individual services with advanced controls

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Available services
SERVICES=(
    "production-controller:neural-forge-production-controller"
    "analytics:neural-forge-analytics-engine"
    "ml-core:neural-forge-ml-core"
    "n8n:neural-forge-n8n"
    "postgres:neural-forge-postgres"
    "redis:neural-forge-redis"
    "prometheus:neural-forge-prometheus"
    "grafana:neural-forge-grafana"
    "nginx:neural-forge-nginx"
)

show_help() {
    echo -e "${BLUE}🔄 Neural Forge Service Manager${NC}"
    echo "==============================="
    echo ""
    echo "Usage: $0 <command> [service]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}start${NC}     Start service(s)"
    echo -e "  ${GREEN}stop${NC}      Stop service(s)"
    echo -e "  ${GREEN}restart${NC}   Restart service(s)"
    echo -e "  ${GREEN}logs${NC}      View service logs"
    echo -e "  ${GREEN}status${NC}    Show service status"
    echo -e "  ${GREEN}scale${NC}     Scale service (requires count)"
    echo -e "  ${GREEN}update${NC}    Update service image"
    echo -e "  ${GREEN}shell${NC}     Access service shell"
    echo ""
    echo "Services:"
    for service_info in "${SERVICES[@]}"; do
        service_name=$(echo "$service_info" | cut -d: -f1)
        echo -e "  ${YELLOW}$service_name${NC}"
    done
    echo -e "  ${YELLOW}all${NC}          All services"
    echo ""
    echo "Examples:"
    echo "  $0 start production-controller"
    echo "  $0 logs ml-core"
    echo "  $0 restart all"
    echo "  $0 scale analytics 3"
    echo ""
}

get_container_name() {
    local service_key="$1"
    for service_info in "${SERVICES[@]}"; do
        if [[ "$service_info" == "$service_key:"* ]]; then
            echo "$service_info" | cut -d: -f2
            return
        fi
    done
    echo ""
}

get_compose_service() {
    local service_key="$1"
    case "$service_key" in
        "production-controller") echo "production-controller" ;;
        "analytics") echo "analytics-engine" ;;
        "ml-core") echo "ml-core" ;;
        "n8n") echo "n8n" ;;
        "postgres") echo "postgres" ;;
        "redis") echo "redis" ;;
        "prometheus") echo "prometheus" ;;
        "grafana") echo "grafana" ;;
        "nginx") echo "nginx" ;;
        *) echo "" ;;
    esac
}

service_exists() {
    local service="$1"
    if [ "$service" = "all" ]; then
        return 0
    fi
    
    for service_info in "${SERVICES[@]}"; do
        if [[ "$service_info" == "$service:"* ]]; then
            return 0
        fi
    done
    return 1
}

start_service() {
    local service="$1"
    
    if [ "$service" = "all" ]; then
        echo -e "${BLUE}🚀 Starting all services...${NC}"
        docker compose up -d
        echo -e "${GREEN}✅ All services started${NC}"
        return
    fi
    
    local compose_service=$(get_compose_service "$service")
    if [ -n "$compose_service" ]; then
        echo -e "${BLUE}🚀 Starting $service...${NC}"
        docker compose up -d "$compose_service"
        
        # Wait for service to be ready
        echo "Waiting for service to be ready..."
        sleep 3
        
        local container_name=$(get_container_name "$service")
        if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
            echo -e "${GREEN}✅ $service started successfully${NC}"
        else
            echo -e "${RED}❌ $service failed to start${NC}"
            docker compose logs "$compose_service"
        fi
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

stop_service() {
    local service="$1"
    
    if [ "$service" = "all" ]; then
        echo -e "${BLUE}🛑 Stopping all services...${NC}"
        docker compose down
        echo -e "${GREEN}✅ All services stopped${NC}"
        return
    fi
    
    local compose_service=$(get_compose_service "$service")
    if [ -n "$compose_service" ]; then
        echo -e "${BLUE}🛑 Stopping $service...${NC}"
        docker compose stop "$compose_service"
        echo -e "${GREEN}✅ $service stopped${NC}"
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

restart_service() {
    local service="$1"
    
    if [ "$service" = "all" ]; then
        echo -e "${BLUE}🔄 Restarting all services...${NC}"
        docker compose restart
        echo -e "${GREEN}✅ All services restarted${NC}"
        return
    fi
    
    local compose_service=$(get_compose_service "$service")
    if [ -n "$compose_service" ]; then
        echo -e "${BLUE}🔄 Restarting $service...${NC}"
        docker compose restart "$compose_service"
        
        # Wait for service to be ready
        sleep 3
        
        echo -e "${GREEN}✅ $service restarted${NC}"
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

show_logs() {
    local service="$1"
    local lines="${2:-100}"
    
    if [ "$service" = "all" ]; then
        echo -e "${BLUE}📋 Showing logs for all services...${NC}"
        docker compose logs -f --tail="$lines"
        return
    fi
    
    local compose_service=$(get_compose_service "$service")
    if [ -n "$compose_service" ]; then
        echo -e "${BLUE}📋 Showing logs for $service (last $lines lines)...${NC}"
        docker compose logs -f --tail="$lines" "$compose_service"
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

show_status() {
    local service="$1"
    
    if [ "$service" = "all" ]; then
        echo -e "${BLUE}📊 Status of all services:${NC}"
        echo ""
        docker compose ps
        echo ""
        
        # Show resource usage
        echo -e "${BLUE}💻 Resource Usage:${NC}"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | grep neural-forge || echo "No containers running"
        return
    fi
    
    local container_name=$(get_container_name "$service")
    if [ -n "$container_name" ]; then
        echo -e "${BLUE}📊 Status of $service:${NC}"
        
        # Check if container is running
        if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
            echo -e "Status: ${GREEN}Running${NC}"
            
            # Show container details
            docker inspect "$container_name" --format='
Image: {{.Config.Image}}
Started: {{.State.StartedAt}}
Status: {{.State.Status}}
Health: {{if .State.Health}}{{.State.Health.Status}}{{else}}No health check{{end}}
Ports: {{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}{{$p}} -> {{(index $conf 0).HostPort}} {{end}}{{end}}'
            
            # Show resource usage
            echo ""
            docker stats --no-stream --format "CPU: {{.CPUPerc}}, Memory: {{.MemUsage}}" "$container_name"
            
        else
            echo -e "Status: ${RED}Not Running${NC}"
            
            # Show last exit status if container exists
            if docker ps -a --filter "name=$container_name" | grep -q "$container_name"; then
                EXIT_CODE=$(docker inspect "$container_name" --format='{{.State.ExitCode}}')
                echo "Last exit code: $EXIT_CODE"
            fi
        fi
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

scale_service() {
    local service="$1"
    local scale="$2"
    
    if [ -z "$scale" ] || ! [[ "$scale" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ Please provide a valid scale number${NC}"
        echo "Usage: $0 scale <service> <number>"
        return
    fi
    
    local compose_service=$(get_compose_service "$service")
    if [ -n "$compose_service" ]; then
        echo -e "${BLUE}⚖️  Scaling $service to $scale instances...${NC}"
        docker compose up -d --scale "$compose_service=$scale" "$compose_service"
        echo -e "${GREEN}✅ $service scaled to $scale instances${NC}"
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

update_service() {
    local service="$1"
    
    local compose_service=$(get_compose_service "$service")
    if [ -n "$compose_service" ]; then
        echo -e "${BLUE}🔄 Updating $service...${NC}"
        
        # Stop service
        docker compose stop "$compose_service"
        
        # Pull latest image
        docker compose pull "$compose_service"
        
        # Rebuild if necessary
        docker compose build "$compose_service"
        
        # Start service
        docker compose up -d "$compose_service"
        
        echo -e "${GREEN}✅ $service updated${NC}"
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

access_shell() {
    local service="$1"
    local shell="${2:-/bin/bash}"
    
    local container_name=$(get_container_name "$service")
    if [ -n "$container_name" ]; then
        echo -e "${BLUE}🐚 Accessing shell for $service...${NC}"
        
        # Check if container is running
        if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
            # Try bash first, then sh
            if docker exec -it "$container_name" bash -c "exit" 2>/dev/null; then
                docker exec -it "$container_name" bash
            else
                docker exec -it "$container_name" sh
            fi
        else
            echo -e "${RED}❌ Container is not running${NC}"
        fi
    else
        echo -e "${RED}❌ Service not found: $service${NC}"
    fi
}

# Main command handler
case "$1" in
    start)
        service="${2:-all}"
        if service_exists "$service"; then
            start_service "$service"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    stop)
        service="${2:-all}"
        if service_exists "$service"; then
            stop_service "$service"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    restart)
        service="${2:-all}"
        if service_exists "$service"; then
            restart_service "$service"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    logs)
        service="${2:-all}"
        lines="${3:-100}"
        if service_exists "$service"; then
            show_logs "$service" "$lines"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    status)
        service="${2:-all}"
        if service_exists "$service"; then
            show_status "$service"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    scale)
        service="$2"
        scale="$3"
        if [ -z "$service" ] || [ -z "$scale" ]; then
            echo -e "${RED}❌ Usage: $0 scale <service> <number>${NC}"
            exit 1
        fi
        if service_exists "$service"; then
            scale_service "$service" "$scale"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    update)
        service="${2:-all}"
        if [ "$service" = "all" ]; then
            echo -e "${BLUE}🔄 Updating all services...${NC}"
            docker compose pull
            docker compose build --parallel
            docker compose up -d
            echo -e "${GREEN}✅ All services updated${NC}"
        elif service_exists "$service"; then
            update_service "$service"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    shell)
        service="$2"
        if [ -z "$service" ]; then
            echo -e "${RED}❌ Usage: $0 shell <service>${NC}"
            exit 1
        fi
        if service_exists "$service"; then
            access_shell "$service"
        else
            echo -e "${RED}❌ Service not found: $service${NC}"
            exit 1
        fi
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        if [ -z "$1" ]; then
            show_status "all"
        else
            echo -e "${RED}❌ Unknown command: $1${NC}"
            show_help
            exit 1
        fi
        ;;
esac

exit 0