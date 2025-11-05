#!/bin/bash
# 🏥 Neural Forge - System Health Monitor
# =====================================
# Comprehensive health monitoring script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
LOG_FILE="logs/health-check-$(date +%Y%m%d-%H%M%S).log"
ALERTS_FILE="logs/health-alerts.json"
mkdir -p logs

echo -e "${CYAN}🏥 Neural Forge - System Health Check${NC}"
echo -e "${CYAN}=====================================${NC}"

# Logging function
log_result() {
    local level=$1
    local component=$2
    local message=$3
    local timestamp=$(date -Iseconds)
    
    echo "{\"timestamp\": \"$timestamp\", \"level\": \"$level\", \"component\": \"$component\", \"message\": \"$message\"}" >> "$LOG_FILE"
    
    case $level in
        "ERROR")
            echo -e "${RED}❌ $component: $message${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  $component: $message${NC}"
            ;;
        "INFO")
            echo -e "${GREEN}✅ $component: $message${NC}"
            ;;
    esac
}

# System resources check
check_system_resources() {
    echo -e "\n${BLUE}🖥️  System Resources${NC}"
    echo "=================="
    
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    CPU_NUM=${CPU_USAGE%.*}
    if [ "$CPU_NUM" -gt 80 ]; then
        log_result "ERROR" "CPU" "High usage: $CPU_USAGE"
    elif [ "$CPU_NUM" -gt 60 ]; then
        log_result "WARN" "CPU" "Moderate usage: $CPU_USAGE"
    else
        log_result "INFO" "CPU" "Normal usage: $CPU_USAGE"
    fi
    
    # Memory usage
    MEMORY_INFO=$(free -h | awk '/^Mem:/{print $3 "/" $2}')
    MEMORY_PERCENT=$(free | awk '/^Mem:/{printf "%.0f", $3/$2 * 100}')
    if [ "$MEMORY_PERCENT" -gt 85 ]; then
        log_result "ERROR" "Memory" "High usage: $MEMORY_INFO ($MEMORY_PERCENT%)"
    elif [ "$MEMORY_PERCENT" -gt 70 ]; then
        log_result "WARN" "Memory" "Moderate usage: $MEMORY_INFO ($MEMORY_PERCENT%)"
    else
        log_result "INFO" "Memory" "Normal usage: $MEMORY_INFO ($MEMORY_PERCENT%)"
    fi
    
    # Disk usage
    DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    DISK_INFO=$(df -h / | awk 'NR==2{print $3 "/" $2}')
    if [ "$DISK_USAGE" -gt 90 ]; then
        log_result "ERROR" "Disk" "Critical usage: $DISK_INFO ($DISK_USAGE%)"
    elif [ "$DISK_USAGE" -gt 80 ]; then
        log_result "WARN" "Disk" "High usage: $DISK_INFO ($DISK_USAGE%)"
    else
        log_result "INFO" "Disk" "Normal usage: $DISK_INFO ($DISK_USAGE%)"
    fi
    
    # Load average
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
    log_result "INFO" "Load" "Current load average:$LOAD_AVG"
}

# Container health check
check_containers() {
    echo -e "\n${BLUE}🐳 Container Health${NC}"
    echo "=================="
    
    if ! command -v docker >/dev/null 2>&1; then
        log_result "ERROR" "Docker" "Docker not installed or not in PATH"
        return
    fi
    
    # Check Docker daemon
    if ! docker ps >/dev/null 2>&1; then
        log_result "ERROR" "Docker" "Docker daemon not running"
        return
    fi
    
    # Expected services
    EXPECTED_SERVICES=(
        "neural-forge-production-controller"
        "neural-forge-analytics-engine"
        "neural-forge-ml-core"
        "neural-forge-n8n"
        "neural-forge-postgres"
        "neural-forge-redis"
    )
    
    for service in "${EXPECTED_SERVICES[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
            # Check container health
            HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "no-health-check")
            if [ "$HEALTH" = "healthy" ] || [ "$HEALTH" = "no-health-check" ]; then
                log_result "INFO" "$service" "Running and healthy"
            else
                log_result "WARN" "$service" "Running but health check failed: $HEALTH"
            fi
        else
            log_result "ERROR" "$service" "Not running"
        fi
    done
    
    # Check for containers with high resource usage
    echo ""
    echo "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | while read line; do
        if echo "$line" | grep -E "^neural-forge" >/dev/null; then
            echo "  $line"
        fi
    done
}

# Network connectivity check
check_network() {
    echo -e "\n${BLUE}🌐 Network Connectivity${NC}"
    echo "======================"
    
    # Check internet connectivity
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log_result "INFO" "Internet" "Connection available"
    else
        log_result "ERROR" "Internet" "No internet connection"
    fi
    
    # Check DNS resolution
    if nslookup google.com >/dev/null 2>&1; then
        log_result "INFO" "DNS" "Resolution working"
    else
        log_result "ERROR" "DNS" "DNS resolution failed"
    fi
    
    # Check service ports
    PORTS_TO_CHECK=(
        "80:HTTP"
        "443:HTTPS"
        "5432:PostgreSQL"
        "6379:Redis"
    )
    
    for port_info in "${PORTS_TO_CHECK[@]}"; do
        port=$(echo "$port_info" | cut -d: -f1)
        service=$(echo "$port_info" | cut -d: -f2)
        
        if netstat -tuln | grep ":$port " >/dev/null 2>&1; then
            log_result "INFO" "$service" "Port $port is listening"
        else
            log_result "WARN" "$service" "Port $port is not listening"
        fi
    done
}

# Application health check
check_applications() {
    echo -e "\n${BLUE}🎯 Application Health${NC}"
    echo "===================="
    
    # Check API endpoints
    API_ENDPOINTS=(
        "http://localhost:8000/health:ML Core API"
        "http://localhost:7860:Production Controller"
        "http://localhost:8501:Analytics Engine"
        "http://localhost:5678:N8N Workflows"
    )
    
    for endpoint_info in "${API_ENDPOINTS[@]}"; do
        endpoint=$(echo "$endpoint_info" | cut -d: -f1,2)
        service=$(echo "$endpoint_info" | cut -d: -f3)
        
        if curl -s --max-time 10 "$endpoint" >/dev/null 2>&1; then
            log_result "INFO" "$service" "Endpoint responding: $endpoint"
        else
            log_result "ERROR" "$service" "Endpoint not responding: $endpoint"
        fi
    done
    
    # Check database connectivity
    if docker compose ps postgres | grep -q "Up"; then
        if docker compose exec -T postgres pg_isready -U neural_forge >/dev/null 2>&1; then
            log_result "INFO" "PostgreSQL" "Database connection successful"
        else
            log_result "ERROR" "PostgreSQL" "Database connection failed"
        fi
    else
        log_result "ERROR" "PostgreSQL" "Container not running"
    fi
    
    # Check Redis connectivity
    if docker compose ps redis | grep -q "Up"; then
        if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
            log_result "INFO" "Redis" "Cache connection successful"
        else
            log_result "ERROR" "Redis" "Cache connection failed"
        fi
    else
        log_result "ERROR" "Redis" "Container not running"
    fi
}

# Log file analysis
check_logs() {
    echo -e "\n${BLUE}📋 Log Analysis${NC}"
    echo "==============="
    
    # Check for recent errors in container logs
    ERROR_COUNT=$(docker compose logs --since="1h" 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
    if [ "$ERROR_COUNT" -gt 10 ]; then
        log_result "ERROR" "Logs" "$ERROR_COUNT errors found in last hour"
    elif [ "$ERROR_COUNT" -gt 5 ]; then
        log_result "WARN" "Logs" "$ERROR_COUNT errors found in last hour"
    else
        log_result "INFO" "Logs" "$ERROR_COUNT errors found in last hour"
    fi
    
    # Check log file sizes
    if [ -d "logs" ]; then
        LARGE_LOGS=$(find logs/ -name "*.log" -size +100M 2>/dev/null | wc -l)
        if [ "$LARGE_LOGS" -gt 0 ]; then
            log_result "WARN" "Logs" "$LARGE_LOGS log files larger than 100MB found"
        else
            log_result "INFO" "Logs" "Log file sizes are normal"
        fi
    fi
}

# Security checks
check_security() {
    echo -e "\n${BLUE}🔐 Security Status${NC}"
    echo "=================="
    
    # Check for security updates
    if command -v apt >/dev/null 2>&1; then
        SECURITY_UPDATES=$(apt list --upgradable 2>/dev/null | grep -i security | wc -l)
        if [ "$SECURITY_UPDATES" -gt 0 ]; then
            log_result "WARN" "Security" "$SECURITY_UPDATES security updates available"
        else
            log_result "INFO" "Security" "No security updates pending"
        fi
    fi
    
    # Check file permissions
    if [ -f ".env" ]; then
        ENV_PERMS=$(stat -c "%a" .env)
        if [ "$ENV_PERMS" != "600" ]; then
            log_result "WARN" "Security" ".env file permissions: $ENV_PERMS (should be 600)"
        else
            log_result "INFO" "Security" ".env file permissions are secure"
        fi
    fi
    
    # Check SSH configuration (if running on server)
    if [ -f "/etc/ssh/sshd_config" ]; then
        if grep -q "PermitRootLogin no" /etc/ssh/sshd_config; then
            log_result "INFO" "Security" "SSH root login disabled"
        else
            log_result "WARN" "Security" "SSH root login may be enabled"
        fi
    fi
    
    # Check firewall status
    if command -v ufw >/dev/null 2>&1; then
        if ufw status | grep -q "Status: active"; then
            log_result "INFO" "Security" "Firewall is active"
        else
            log_result "WARN" "Security" "Firewall is not active"
        fi
    fi
}

# Performance metrics
check_performance() {
    echo -e "\n${BLUE}⚡ Performance Metrics${NC}"
    echo "====================="
    
    # Response time checks
    START_TIME=$(date +%s%3N)
    curl -s --max-time 5 http://localhost:8000/health >/dev/null 2>&1
    END_TIME=$(date +%s%3N)
    RESPONSE_TIME=$((END_TIME - START_TIME))
    
    if [ "$RESPONSE_TIME" -gt 5000 ]; then
        log_result "ERROR" "Performance" "API response time too slow: ${RESPONSE_TIME}ms"
    elif [ "$RESPONSE_TIME" -gt 2000 ]; then
        log_result "WARN" "Performance" "API response time slow: ${RESPONSE_TIME}ms"
    else
        log_result "INFO" "Performance" "API response time good: ${RESPONSE_TIME}ms"
    fi
    
    # Database performance check
    if docker compose ps postgres | grep -q "Up"; then
        DB_START=$(date +%s%3N)
        docker compose exec -T postgres psql -U neural_forge -d neural_forge -c "SELECT 1;" >/dev/null 2>&1
        DB_END=$(date +%s%3N)
        DB_TIME=$((DB_END - DB_START))
        
        if [ "$DB_TIME" -gt 1000 ]; then
            log_result "WARN" "Performance" "Database response slow: ${DB_TIME}ms"
        else
            log_result "INFO" "Performance" "Database response good: ${DB_TIME}ms"
        fi
    fi
}

# Generate summary report
generate_summary() {
    echo -e "\n${CYAN}📊 Health Check Summary${NC}"
    echo "======================="
    
    TOTAL_CHECKS=$(grep -c "\"level\":" "$LOG_FILE")
    ERROR_COUNT=$(grep -c "\"level\": \"ERROR\"" "$LOG_FILE")
    WARN_COUNT=$(grep -c "\"level\": \"WARN\"" "$LOG_FILE")
    INFO_COUNT=$(grep -c "\"level\": \"INFO\"" "$LOG_FILE")
    
    echo "Total checks performed: $TOTAL_CHECKS"
    echo -e "${RED}Errors: $ERROR_COUNT${NC}"
    echo -e "${YELLOW}Warnings: $WARN_COUNT${NC}"
    echo -e "${GREEN}Passed: $INFO_COUNT${NC}"
    
    # Overall health score
    HEALTH_SCORE=$(echo "scale=2; ($INFO_COUNT * 100) / $TOTAL_CHECKS" | bc -l 2>/dev/null || echo "N/A")
    
    if [ "$ERROR_COUNT" -eq 0 ] && [ "$WARN_COUNT" -eq 0 ]; then
        echo -e "\n${GREEN}🎉 System Status: EXCELLENT${NC}"
        echo -e "Health Score: ${GREEN}$HEALTH_SCORE%${NC}"
    elif [ "$ERROR_COUNT" -eq 0 ]; then
        echo -e "\n${YELLOW}👍 System Status: GOOD${NC}"
        echo -e "Health Score: ${YELLOW}$HEALTH_SCORE%${NC}"
    elif [ "$ERROR_COUNT" -lt 3 ]; then
        echo -e "\n${YELLOW}⚠️  System Status: ATTENTION NEEDED${NC}"
        echo -e "Health Score: ${YELLOW}$HEALTH_SCORE%${NC}"
    else
        echo -e "\n${RED}🚨 System Status: CRITICAL${NC}"
        echo -e "Health Score: ${RED}$HEALTH_SCORE%${NC}"
    fi
    
    echo ""
    echo "📋 Detailed log: $LOG_FILE"
    
    # Generate alerts for critical issues
    if [ "$ERROR_COUNT" -gt 0 ]; then
        {
            echo "{"
            echo "  \"timestamp\": \"$(date -Iseconds)\","
            echo "  \"level\": \"ALERT\","
            echo "  \"errors\": $ERROR_COUNT,"
            echo "  \"warnings\": $WARN_COUNT,"
            echo "  \"health_score\": \"$HEALTH_SCORE\","
            echo "  \"log_file\": \"$LOG_FILE\""
            echo "}"
        } > "$ALERTS_FILE"
        
        echo -e "${RED}🚨 Alert generated: $ALERTS_FILE${NC}"
    fi
}

# Main execution
main() {
    echo "Health check started at $(date)"
    echo "Log file: $LOG_FILE"
    echo ""
    
    check_system_resources
    check_containers
    check_network
    check_applications
    check_logs
    check_security
    check_performance
    generate_summary
    
    echo ""
    echo -e "${CYAN}Health check completed at $(date)${NC}"
}

# Execute main function
main "$@"