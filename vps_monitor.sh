#!/bin/bash
"""
VPS Health Monitor and System Management
Real-time monitoring and management for MetaSystem VPS deployment
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SERVICES=("metasystem-gradio" "metasystem-streamlit" "metasystem-api" "postgresql" "redis-server" "nginx")
PORTS=("7860" "8501" "8000" "5432" "6379" "80")
LOG_DIR="/var/log/metasystem"
APP_DIR="/home/metasystem/apps/metasystem-core"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $(date '+%H:%M:%S') $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $(date '+%H:%M:%S') $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $(date '+%H:%M:%S') $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $(date '+%H:%M:%S') $1${NC}"
}

log_header() {
    echo -e "${PURPLE}🚀 $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

# Function to check service status
check_service_status() {
    local service=$1
    if systemctl is-active --quiet "$service.service" 2>/dev/null; then
        echo -e "${GREEN}●${NC} $service: RUNNING"
        return 0
    else
        echo -e "${RED}●${NC} $service: STOPPED"
        return 1
    fi
}

# Function to check port availability
check_port() {
    local port=$1
    local service=$2
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}●${NC} Port $port ($service): OPEN"
        return 0
    else
        echo -e "${RED}●${NC} Port $port ($service): CLOSED"
        return 1
    fi
}

# Function to get system metrics
get_system_metrics() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    local memory_usage=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    local disk_usage=$(df -h / | awk 'NR==2{printf("%s", $5)}' | sed 's/%//')
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    echo "CPU: ${cpu_usage}% | Memory: ${memory_usage}% | Disk: ${disk_usage}% | Load: ${load_avg}"
}

# Function to check API health
check_api_health() {
    local api_url="http://localhost:8000/health"
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$api_url" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}●${NC} ML API Health: OK (HTTP $response)"
        return 0
    else
        echo -e "${RED}●${NC} ML API Health: FAILED (HTTP $response)"
        return 1
    fi
}

# Function to check gradio health
check_gradio_health() {
    local gradio_url="http://localhost:7860"
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$gradio_url" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}●${NC} Gradio Interface: OK (HTTP $response)"
        return 0
    else
        echo -e "${RED}●${NC} Gradio Interface: FAILED (HTTP $response)"
        return 1
    fi
}

# Function to check streamlit health
check_streamlit_health() {
    local streamlit_url="http://localhost:8501"
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$streamlit_url" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}●${NC} Streamlit Analytics: OK (HTTP $response)"
        return 0
    else
        echo -e "${RED}●${NC} Streamlit Analytics: FAILED (HTTP $response)"
        return 1
    fi
}

# Function to show comprehensive status
show_status() {
    clear
    log_header "MetaSystem VPS Health Monitor"
    
    echo -e "${CYAN}System Metrics:${NC}"
    echo "$(get_system_metrics)"
    echo
    
    echo -e "${CYAN}Service Status:${NC}"
    local failed_services=0
    for service in "${SERVICES[@]}"; do
        if ! check_service_status "$service"; then
            ((failed_services++))
        fi
    done
    echo
    
    echo -e "${CYAN}Port Status:${NC}"
    local service_names=("Gradio" "Streamlit" "ML-API" "PostgreSQL" "Redis" "Nginx")
    for i in "${!PORTS[@]}"; do
        check_port "${PORTS[$i]}" "${service_names[$i]}"
    done
    echo
    
    echo -e "${CYAN}Application Health:${NC}"
    local failed_apps=0
    if ! check_api_health; then ((failed_apps++)); fi
    if ! check_gradio_health; then ((failed_apps++)); fi
    if ! check_streamlit_health; then ((failed_apps++)); fi
    echo
    
    # Overall status
    if [ $failed_services -eq 0 ] && [ $failed_apps -eq 0 ]; then
        log_success "All systems operational"
    else
        log_error "$failed_services service(s) and $failed_apps application(s) failed"
    fi
    
    echo -e "${CYAN}Last Updated:${NC} $(date)"
}

# Function to restart failed services
restart_failed_services() {
    log_info "Checking and restarting failed services..."
    
    for service in "${SERVICES[@]}"; do
        if ! systemctl is-active --quiet "$service.service" 2>/dev/null; then
            log_warning "Restarting $service..."
            systemctl restart "$service.service"
            sleep 3
            
            if systemctl is-active --quiet "$service.service"; then
                log_success "$service restarted successfully"
            else
                log_error "Failed to restart $service"
            fi
        fi
    done
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        echo "Available services:"
        for s in "${SERVICES[@]}"; do
            echo "  - $s"
        done
        echo
        read -p "Enter service name: " service
    fi
    
    if [[ " ${SERVICES[@]} " =~ " ${service} " ]]; then
        log_info "Showing logs for $service (press Ctrl+C to exit)"
        journalctl -u "$service.service" -f
    else
        log_error "Service '$service' not found"
    fi
}

# Function to manage services
manage_service() {
    local action=$1
    local service=$2
    
    if [ -z "$service" ]; then
        echo "Available services:"
        for s in "${SERVICES[@]}"; do
            echo "  - $s"
        done
        echo
        read -p "Enter service name: " service
    fi
    
    if [[ " ${SERVICES[@]} " =~ " ${service} " ]]; then
        log_info "Performing '$action' on $service..."
        systemctl "$action" "$service.service"
        
        if [ "$action" = "start" ] || [ "$action" = "restart" ]; then
            sleep 3
            if systemctl is-active --quiet "$service.service"; then
                log_success "$service $action completed successfully"
            else
                log_error "$service $action failed"
            fi
        else
            log_success "$service $action completed"
        fi
    else
        log_error "Service '$service' not found"
    fi
}

# Function to check disk space and cleanup
cleanup_system() {
    log_info "Performing system cleanup..."
    
    # Check disk usage
    disk_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    log_info "Current disk usage: ${disk_usage}%"
    
    if [ "$disk_usage" -gt 80 ]; then
        log_warning "High disk usage detected, performing cleanup..."
        
        # Clean package cache
        apt-get clean
        apt-get autoremove -y
        
        # Clean old logs
        journalctl --vacuum-time=7d
        find /var/log -name "*.log" -type f -mtime +7 -delete
        
        # Clean old backups (keep 7 days)
        find /home/metasystem/backups -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
        
        log_success "System cleanup completed"
    else
        log_success "Disk usage is acceptable (${disk_usage}%)"
    fi
}

# Function to backup system
backup_system() {
    log_info "Creating system backup..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="/home/metasystem/backups/$TIMESTAMP"
    
    mkdir -p "$BACKUP_DIR"
    
    # Database backup
    sudo -u metasystem pg_dump metasystem_db | gzip > "$BACKUP_DIR/db_backup.sql.gz"
    
    # Application files backup
    tar -czf "$BACKUP_DIR/app_backup.tar.gz" \
        "$APP_DIR/data" \
        "$APP_DIR/config" \
        "$APP_DIR/.env" \
        "$LOG_DIR" 2>/dev/null || true
    
    # Configuration backup
    cp -r /etc/nginx/sites-available "$BACKUP_DIR/nginx_config" 2>/dev/null || true
    cp -r /etc/systemd/system/metasystem-*.service "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "Backup created in $BACKUP_DIR"
}

# Function to show system information
show_system_info() {
    log_header "System Information"
    
    echo -e "${CYAN}Server Details:${NC}"
    echo "Hostname: $(hostname)"
    echo "Uptime: $(uptime -p)"
    echo "OS: $(lsb_release -d | cut -f2)"
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo
    
    echo -e "${CYAN}Hardware:${NC}"
    echo "CPU: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
    echo "Cores: $(nproc)"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
    echo "Disk: $(df -h / | awk 'NR==2{print $2}')"
    echo
    
    echo -e "${CYAN}Network:${NC}"
    echo "Public IP: $(curl -s ifconfig.me || echo 'N/A')"
    echo "Private IP: $(hostname -I | awk '{print $1}')"
    echo
    
    echo -e "${CYAN}MetaSystem Version:${NC}"
    if [ -f "$APP_DIR/.git/HEAD" ]; then
        cd "$APP_DIR" && git log -1 --format="%h - %s (%cr)" 2>/dev/null || echo "Git info not available"
    else
        echo "Not a git repository"
    fi
}

# Function to show help
show_help() {
    echo "MetaSystem VPS Health Monitor & Management Tool"
    echo "============================================="
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  status              Show comprehensive system status"
    echo "  monitor             Continuous monitoring (auto-refresh)"
    echo "  restart             Restart failed services"
    echo "  logs [service]      Show service logs"
    echo "  start [service]     Start a service"
    echo "  stop [service]      Stop a service"
    echo "  restart [service]   Restart a service"
    echo "  cleanup             Perform system cleanup"
    echo "  backup              Create system backup"
    echo "  info                Show system information"
    echo "  help                Show this help message"
    echo
    echo "Examples:"
    echo "  $0 status                    # Show current status"
    echo "  $0 monitor                   # Continuous monitoring"
    echo "  $0 logs metasystem-api       # Show API logs"
    echo "  $0 restart metasystem-gradio # Restart Gradio service"
    echo
    echo "Services available:"
    for service in "${SERVICES[@]}"; do
        echo "  - $service"
    done
}

# Main function
main() {
    case "${1:-status}" in
        "status")
            show_status
            ;;
        "monitor")
            log_info "Starting continuous monitoring (press Ctrl+C to exit)..."
            while true; do
                show_status
                sleep 30
            done
            ;;
        "restart")
            if [ -n "$2" ]; then
                manage_service "restart" "$2"
            else
                restart_failed_services
            fi
            ;;
        "start")
            manage_service "start" "$2"
            ;;
        "stop")
            manage_service "stop" "$2"
            ;;
        "logs")
            show_logs "$2"
            ;;
        "cleanup")
            cleanup_system
            ;;
        "backup")
            backup_system
            ;;
        "info")
            show_system_info
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Check if running as root for system operations
if [[ $EUID -eq 0 ]] && [[ "$1" =~ ^(restart|start|stop|cleanup|backup)$ ]]; then
    log_warning "Running system management commands as root"
fi

# Run main function
main "$@"