#!/bin/bash
# 📊 Neural Forge Discográfica - Monitoring Setup Script
# =======================================================
# Configure Prometheus + Grafana monitoring stack

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_VERSION="3.0"
LOG_FILE="/var/log/neural-forge-monitoring.log"

echo -e "${CYAN}📊 Neural Forge - Monitoring Setup v${SCRIPT_VERSION}${NC}"
echo -e "${CYAN}===================================================${NC}"
echo -e "Date: $(date)"
echo ""

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "${RED}❌ MONITORING SETUP FAILED: $1${NC}"
    exit 1
}

# Create log file
mkdir -p /var/log
touch "$LOG_FILE"
chmod 666 "$LOG_FILE"

log "${BLUE}📋 PHASE 1: Monitoring Configuration${NC}"
log "===================================="

# Create monitoring directories
log "📁 Creating monitoring directories..."
mkdir -p monitoring/{prometheus,grafana/{dashboards,datasources},alertmanager}
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/dashboards/neural-forge

log "${GREEN}✅ Monitoring directories created${NC}"
echo ""

log "${BLUE}⚙️ PHASE 2: Prometheus Configuration${NC}"
log "===================================="

# Create Prometheus configuration
log "📊 Creating Prometheus configuration..."
cat > monitoring/prometheus/prometheus.yml << 'EOF'
# Neural Forge Prometheus Configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'neural-forge'
    environment: 'production'

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
    metrics_path: /metrics
    
  # Production Controller (Gradio)
  - job_name: 'production-controller'
    static_configs:
      - targets: ['production-controller:7860']
    scrape_interval: 30s
    metrics_path: /metrics
    scrape_timeout: 10s
    
  # Analytics Engine (Streamlit)
  - job_name: 'analytics-engine'
    static_configs:
      - targets: ['analytics:8501']
    scrape_interval: 30s
    metrics_path: /metrics
    scrape_timeout: 10s
    
  # ML Core API (FastAPI)
  - job_name: 'ml-core-api'
    static_configs:
      - targets: ['ml-core:8000']
    scrape_interval: 15s
    metrics_path: /metrics
    scrape_timeout: 10s
    
  # N8N Workflows
  - job_name: 'n8n-workflows'
    static_configs:
      - targets: ['n8n:5678']
    scrape_interval: 30s
    metrics_path: /metrics
    scrape_timeout: 10s
    
  # PostgreSQL Database
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s
    metrics_path: /metrics
    scrape_timeout: 10s
    
  # Redis Cache
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
    metrics_path: /metrics
    scrape_timeout: 10s
    
  # Meta Ads Service
  - job_name: 'meta-ads'
    static_configs:
      - targets: ['meta-ads:8002']
    scrape_interval: 60s
    metrics_path: /metrics
    scrape_timeout: 15s
    
  # Node Exporter (System metrics)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s
    metrics_path: /metrics
    
  # Docker containers metrics
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s
    metrics_path: /metrics
    
  # Nginx metrics
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    scrape_interval: 30s
    metrics_path: /nginx_status
    scrape_timeout: 10s
EOF

# Create alerting rules
log "🚨 Creating alerting rules..."
cat > monitoring/prometheus/rules/alerts.yml << 'EOF'
groups:
  - name: neural-forge-alerts
    rules:
      # Service availability alerts
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.job }} has been down for more than 1 minute"
          
      # High CPU usage
      - alert: HighCPUUsage
        expr: (100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes"
          
      # High memory usage
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 90% for more than 5 minutes"
          
      # High disk usage
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage on {{ $labels.instance }}"
          description: "Disk usage is above 85% for more than 5 minutes"
          
      # ML API response time
      - alert: SlowMLAPIResponse
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="ml-core-api"}[5m])) > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "ML API slow response time"
          description: "95th percentile response time is above 5 seconds"
          
      # Campaign failure rate
      - alert: HighCampaignFailureRate
        expr: rate(campaign_failures_total[5m]) > 0.1
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High campaign failure rate"
          description: "Campaign failure rate is above 10% for 3 minutes"
          
      # Database connection issues
      - alert: DatabaseConnectionIssues
        expr: postgresql_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is down"
          description: "Cannot connect to PostgreSQL database"
EOF

log "${GREEN}✅ Prometheus configuration completed${NC}"
echo ""

log "${BLUE}📊 PHASE 3: Grafana Configuration${NC}"
log "=================================="

# Create Grafana datasource configuration
log "🔗 Creating Grafana datasources..."
cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
      queryTimeout: "60s"
      httpMethod: "POST"
EOF

# Create dashboard provisioning configuration
cat > monitoring/grafana/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'Neural Forge Dashboards'
    orgId: 1
    folder: 'Neural Forge'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards/neural-forge
EOF

# Create main system overview dashboard
log "📈 Creating system overview dashboard..."
cat > monitoring/grafana/dashboards/neural-forge/system-overview.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Neural Forge - System Overview",
    "tags": ["neural-forge", "system"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "System Resources",
        "type": "stat",
        "targets": [
          {
            "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "Memory Usage %"
          },
          {
            "expr": "(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100",
            "legendFormat": "Disk Usage %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Service Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"production-controller\"}",
            "legendFormat": "Production Controller"
          },
          {
            "expr": "up{job=\"analytics-engine\"}",
            "legendFormat": "Analytics Engine"
          },
          {
            "expr": "up{job=\"ml-core-api\"}",
            "legendFormat": "ML Core API"
          },
          {
            "expr": "up{job=\"n8n-workflows\"}",
            "legendFormat": "N8N Workflows"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "API Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"ml-core-api\"}[5m]))",
            "legendFormat": "ML API P95"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{job=\"ml-core-api\"}[5m]))",
            "legendFormat": "ML API P50"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "30s"
  }
}
EOF

# Create ML performance dashboard
log "🧠 Creating ML performance dashboard..."
cat > monitoring/grafana/dashboards/neural-forge/ml-performance.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Neural Forge - ML Performance",
    "tags": ["neural-forge", "ml", "ai"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Video Generation Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(video_generation_requests_total[5m])",
            "legendFormat": "Requests/sec"
          },
          {
            "expr": "rate(video_generation_failures_total[5m])",
            "legendFormat": "Failures/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Model Inference Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(model_inference_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Inference Time"
          },
          {
            "expr": "histogram_quantile(0.50, rate(model_inference_duration_seconds_bucket[5m]))",
            "legendFormat": "P50 Inference Time"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "GPU Utilization",
        "type": "graph",
        "targets": [
          {
            "expr": "nvidia_gpu_utilization_gpu",
            "legendFormat": "GPU {{ $labels.gpu }}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "nvidia_gpu_memory_used_bytes / nvidia_gpu_memory_total_bytes * 100",
            "legendFormat": "GPU Memory %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "30s"
  }
}
EOF

# Create campaign metrics dashboard
log "📊 Creating campaign metrics dashboard..."
cat > monitoring/grafana/dashboards/neural-forge/campaign-metrics.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Neural Forge - Campaign Metrics",
    "tags": ["neural-forge", "campaigns", "social-media"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Active Campaigns",
        "type": "stat",
        "targets": [
          {
            "expr": "campaign_active_total",
            "legendFormat": "Active Campaigns"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Campaign Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(campaign_success_total[1h]) / rate(campaign_total[1h]) * 100",
            "legendFormat": "Success Rate %"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Total Views",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(campaign_views_total)",
            "legendFormat": "Total Views"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "ROI",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(campaign_revenue_total) / sum(campaign_cost_total)",
            "legendFormat": "ROI"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 5,
        "title": "Views Over Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(campaign_views_total[5m])",
            "legendFormat": "Views/min"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 6,
        "title": "Engagement Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(campaign_engagements_total[5m]) / rate(campaign_views_total[5m]) * 100",
            "legendFormat": "Engagement Rate %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "time": {"from": "now-24h", "to": "now"},
    "refresh": "1m"
  }
}
EOF

log "${GREEN}✅ Grafana configuration completed${NC}"
echo ""

log "${BLUE}🔔 PHASE 4: Alertmanager Configuration${NC}"
log "====================================="

# Create Alertmanager configuration
log "🚨 Creating Alertmanager configuration..."
cat > monitoring/alertmanager/alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@neuralforge.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'neural-forge-alerts'

receivers:
  - name: 'neural-forge-alerts'
    email_configs:
      - to: 'admin@neuralforge.com'
        subject: '🚨 Neural Forge Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          
          Labels:
          {{ range .Labels.SortedPairs }}  {{ .Name }}: {{ .Value }}
          {{ end }}
          {{ end }}
    
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#neural-forge-alerts'
        title: '🚨 Neural Forge Alert'
        text: |
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ .Annotations.description }}
          {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

log "${GREEN}✅ Alertmanager configuration completed${NC}"
echo ""

log "${BLUE}📱 PHASE 5: Mobile Monitoring Setup${NC}"
log "==================================="

# Create monitoring mobile app script
log "📱 Creating mobile monitoring script..."
cat > scripts/mobile-status.sh << 'EOF'
#!/bin/bash
# Neural Forge Mobile Status - Quick system overview

echo "🎵 Neural Forge Status - $(date '+%H:%M')"
echo "================================"

# System resources
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
MEM=$(free | awk '/^Mem:/{printf "%.1f%%", $3/$2*100}')
DISK=$(df -h / | awk 'NR==2{print $5}')

echo "💻 Resources: CPU ${CPU}% | RAM ${MEM} | Disk ${DISK}"

# Service status
echo "🏃 Services:"
docker compose ps --format "table {{.Service}}\t{{.Status}}" | tail -n +2 | while read line; do
    SERVICE=$(echo $line | awk '{print $1}')
    STATUS=$(echo $line | awk '{print $2}')
    if [[ $STATUS == *"Up"* ]]; then
        echo "  ✅ $SERVICE"
    else
        echo "  ❌ $SERVICE"
    fi
done

# Quick metrics
echo "📊 Quick Metrics:"
echo "  Active Campaigns: $(curl -s http://localhost:7860/api/campaigns/count 2>/dev/null || echo 'N/A')"
echo "  API Requests/min: $(curl -s http://localhost:9090/api/v1/query?query=rate%28http_requests_total%5B1m%5D%29 2>/dev/null | jq -r '.data.result[0].value[1]' 2>/dev/null || echo 'N/A')"

echo ""
echo "📱 View full dashboard: https://$(curl -s ifconfig.me)/grafana"
EOF

chmod +x scripts/mobile-status.sh

# Create WhatsApp/Telegram notification script
log "📲 Creating notification script..."
cat > scripts/send-alert.sh << 'EOF'
#!/bin/bash
# Neural Forge Alert Notification Script

ALERT_TYPE="$1"
MESSAGE="$2"
URGENCY="${3:-normal}"

# Telegram notification
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="🎵 Neural Forge Alert

Type: $ALERT_TYPE
Message: $MESSAGE
Time: $(date)
Urgency: $URGENCY

Check dashboard: https://$(curl -s ifconfig.me)/grafana"
fi

# Slack notification
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -s -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-type: application/json' \
        -d "{
            \"text\": \"🎵 Neural Forge Alert\",
            \"attachments\": [{
                \"color\": \"danger\",
                \"fields\": [{
                    \"title\": \"$ALERT_TYPE\",
                    \"value\": \"$MESSAGE\",
                    \"short\": false
                }]
            }]
        }"
fi

# Email notification (if configured)
if command -v mail >/dev/null 2>&1; then
    echo "Neural Forge Alert: $ALERT_TYPE

Message: $MESSAGE
Time: $(date)
Server: $(hostname)

Check dashboard: https://$(curl -s ifconfig.me)/grafana" | mail -s "🚨 Neural Forge Alert: $ALERT_TYPE" alerts@neuralforge.com
fi
EOF

chmod +x scripts/send-alert.sh

log "${GREEN}✅ Mobile monitoring setup completed${NC}"
echo ""

log "${BLUE}📋 PHASE 6: Monitoring Scripts${NC}"
log "==============================="

# Create comprehensive monitoring script
log "📊 Creating monitoring management script..."
cat > monitoring-manager.sh << 'EOF'
#!/bin/bash
# Neural Forge Monitoring Manager

case "$1" in
    start)
        echo "📊 Starting monitoring stack..."
        docker compose up -d prometheus grafana alertmanager node-exporter cadvisor
        ;;
    stop)
        echo "⏹️ Stopping monitoring stack..."
        docker compose stop prometheus grafana alertmanager node-exporter cadvisor
        ;;
    restart)
        echo "🔄 Restarting monitoring stack..."
        docker compose restart prometheus grafana alertmanager
        ;;
    status)
        echo "📊 Monitoring Stack Status:"
        docker compose ps prometheus grafana alertmanager node-exporter cadvisor
        ;;
    logs)
        SERVICE="${2:-prometheus}"
        docker compose logs -f "$SERVICE"
        ;;
    dashboards)
        echo "📈 Available Dashboards:"
        echo "  • System Overview: http://localhost:3000/d/system-overview"
        echo "  • ML Performance: http://localhost:3000/d/ml-performance"
        echo "  • Campaign Metrics: http://localhost:3000/d/campaign-metrics"
        echo "  • Prometheus: http://localhost:9090"
        ;;
    backup)
        echo "💾 Backing up monitoring data..."
        docker run --rm -v prometheus_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/prometheus-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
        docker run --rm -v grafana_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/grafana-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
        echo "✅ Monitoring backup completed"
        ;;
    *)
        echo "Neural Forge Monitoring Manager"
        echo "Usage: $0 {start|stop|restart|status|logs|dashboards|backup}"
        echo ""
        echo "Commands:"
        echo "  start      - Start monitoring services"
        echo "  stop       - Stop monitoring services"
        echo "  restart    - Restart monitoring services"
        echo "  status     - Show service status"
        echo "  logs       - Show logs (specify service name)"
        echo "  dashboards - List dashboard URLs"
        echo "  backup     - Backup monitoring data"
        ;;
esac
EOF

chmod +x monitoring-manager.sh

# Create system health check script
log "🏥 Creating health check script..."
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash
# Neural Forge Comprehensive Health Check

echo "🏥 Neural Forge Health Check - $(date)"
echo "======================================="
echo ""

# Check Docker services
echo "🐳 Docker Services:"
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}" | while read line; do
    echo "  $line"
done
echo ""

# Check system resources
echo "💻 System Resources:"
echo "  CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')"
echo "  Memory: $(free -h | awk '/^Mem:/{printf "Used: %s / Total: %s (%.1f%%)", $3, $2, $3/$2*100}')"
echo "  Disk: $(df -h / | awk 'NR==2{printf "Used: %s / Total: %s (%s)", $3, $2, $5}')"
echo ""

# Check service endpoints
echo "🌐 Service Endpoints:"
ENDPOINTS=(
    "http://localhost:7860/health:Production Controller"
    "http://localhost:8501/health:Analytics Engine"
    "http://localhost:8000/health:ML Core API"
    "http://localhost:5678/healthz:N8N Workflows"
    "http://localhost:3000/api/health:Grafana"
    "http://localhost:9090/-/healthy:Prometheus"
)

for ENDPOINT_INFO in "${ENDPOINTS[@]}"; do
    IFS=':' read -r URL NAME <<< "$ENDPOINT_INFO"
    if curl -sf "$URL" >/dev/null 2>&1; then
        echo "  ✅ $NAME"
    else
        echo "  ❌ $NAME (not responding)"
    fi
done
echo ""

# Check recent errors
echo "📋 Recent Errors (last 24h):"
docker compose logs --since 24h 2>&1 | grep -i error | tail -5 | while read line; do
    echo "  🔴 $line"
done
echo ""

# Performance metrics
echo "📊 Performance Metrics:"
if curl -s http://localhost:9090/api/v1/query?query=up >/dev/null 2>&1; then
    echo "  ✅ Prometheus metrics available"
    
    # Get key metrics
    CPU_USAGE=$(curl -s "http://localhost:9090/api/v1/query?query=100-(avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m]))*100)" | jq -r '.data.result[0].value[1]' 2>/dev/null)
    if [ "$CPU_USAGE" != "null" ] && [ -n "$CPU_USAGE" ]; then
        echo "  📈 Average CPU Usage: ${CPU_USAGE}%"
    fi
    
    MEMORY_USAGE=$(curl -s "http://localhost:9090/api/v1/query?query=(1-((node_memory_MemFree_bytes+node_memory_Cached_bytes+node_memory_Buffers_bytes)/node_memory_MemTotal_bytes))*100" | jq -r '.data.result[0].value[1]' 2>/dev/null)
    if [ "$MEMORY_USAGE" != "null" ] && [ -n "$MEMORY_USAGE" ]; then
        echo "  📈 Memory Usage: ${MEMORY_USAGE}%"
    fi
else
    echo "  ⚠️ Prometheus metrics unavailable"
fi

echo ""
echo "🎵 Health check completed!"
EOF

chmod +x scripts/health-check.sh

log "${GREEN}✅ Monitoring scripts created${NC}"
echo ""

log "${CYAN}🎉 MONITORING SETUP COMPLETED!${NC}"
log "==============================="
log ""
log "${GREEN}✅ Monitoring Summary:${NC}"
log "  • Prometheus: Metrics collection and alerting"
log "  • Grafana: Dashboards and visualization"
log "  • Alertmanager: Alert routing and notifications"
log "  • Custom dashboards: System, ML, Campaigns"
log "  • Mobile monitoring: Quick status scripts"
log "  • Health checks: Comprehensive system monitoring"
log ""
log "${YELLOW}📊 Access URLs (after deployment):${NC}"
log "  🔍 Prometheus: http://localhost:9090"
log "  📈 Grafana: http://localhost:3000 (admin/neuralforge2025)"
log "  🚨 Alertmanager: http://localhost:9093"
log ""
log "${YELLOW}🔧 Management Commands:${NC}"
log "  • ./monitoring-manager.sh start        (Start monitoring)"
log "  • ./monitoring-manager.sh dashboards   (List dashboards)"
log "  • ./scripts/health-check.sh            (Full health check)"
log "  • ./scripts/mobile-status.sh           (Quick mobile status)"
log ""
log "${YELLOW}📱 Mobile Notifications:${NC}"
log "  • Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
log "  • Configure SLACK_WEBHOOK_URL for Slack alerts"
log "  • Run: ./scripts/send-alert.sh \"test\" \"System is healthy\""
log ""
log "${BLUE}💡 Next Steps:${NC}"
log "  1. Deploy services: ./deploy/hetzner/deploy-services.sh"
log "  2. Access Grafana and import dashboards"
log "  3. Configure alert recipients in alertmanager.yml"
log "  4. Set up mobile notifications"
log "  5. Test alerting with: ./scripts/send-alert.sh"
log ""
log "${PURPLE}📊 Your Neural Forge monitoring is ready! 🚀${NC}"

exit 0