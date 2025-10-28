#!/bin/bash

# Meta Ads Monitoring Setup Script
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${2:-us-central1}"
NOTIFICATION_EMAIL="${3:-alerts@example.com}"

# Print banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║           Meta Ads Monitoring Setup Script               ║
║                                                          ║
║  This script sets up comprehensive monitoring and        ║
║  alerting for the Meta Ads system                       ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check requirements
if [ -z "$PROJECT_ID" ]; then
    print_error "No project ID found. Please set it with: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

print_status "Setting up monitoring for project: $PROJECT_ID"
print_status "Region: $REGION"
print_status "Notification email: $NOTIFICATION_EMAIL"

# Enable required APIs
print_status "Enabling monitoring APIs..."
gcloud services enable \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudtrace.googleapis.com \
    clouderrorreporting.googleapis.com \
    cloudprofiler.googleapis.com

# Create notification channel for email alerts
print_status "Creating notification channel..."
NOTIFICATION_CHANNEL=$(gcloud alpha monitoring channels create \
    --display-name="Meta Ads Email Alerts" \
    --type=email \
    --channel-labels=email_address="$NOTIFICATION_EMAIL" \
    --format="value(name)" 2>/dev/null || echo "")

if [ -z "$NOTIFICATION_CHANNEL" ]; then
    print_warning "Failed to create notification channel or it already exists"
    # Try to find existing channel
    NOTIFICATION_CHANNEL=$(gcloud alpha monitoring channels list \
        --filter="displayName:'Meta Ads Email Alerts'" \
        --format="value(name)" | head -1)
fi

print_status "Using notification channel: $NOTIFICATION_CHANNEL"

# Create alerting policies
print_status "Creating alerting policies..."

# High CPU utilization alert
cat > /tmp/cpu-alert-policy.yaml << EOF
displayName: "Meta Ads - High CPU Utilization"
documentation:
  content: "CPU utilization is above 80% for Cloud Run service"
conditions:
  - displayName: "CPU utilization"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.label.service_name="meta-ads-api" AND metric.type="run.googleapis.com/container/cpu/utilizations"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.8
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
          crossSeriesReducer: REDUCE_MEAN
          groupByFields:
            - resource.label.service_name
combiner: OR
enabled: true
notificationChannels:
  - "$NOTIFICATION_CHANNEL"
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/cpu-alert-policy.yaml

# High memory utilization alert
cat > /tmp/memory-alert-policy.yaml << EOF
displayName: "Meta Ads - High Memory Utilization"
documentation:
  content: "Memory utilization is above 85% for Cloud Run service"
conditions:
  - displayName: "Memory utilization"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.label.service_name="meta-ads-api" AND metric.type="run.googleapis.com/container/memory/utilizations"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.85
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
          crossSeriesReducer: REDUCE_MEAN
          groupByFields:
            - resource.label.service_name
combiner: OR
enabled: true
notificationChannels:
  - "$NOTIFICATION_CHANNEL"
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/memory-alert-policy.yaml

# High error rate alert
cat > /tmp/error-rate-alert-policy.yaml << EOF
displayName: "Meta Ads - High Error Rate"
documentation:
  content: "Error rate is above 5% for Cloud Run service"
conditions:
  - displayName: "Error rate"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND resource.label.service_name="meta-ads-api" AND metric.type="run.googleapis.com/request_count"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.05
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_SUM
          groupByFields:
            - resource.label.service_name
            - metric.label.response_code_class
combiner: OR
enabled: true
notificationChannels:
  - "$NOTIFICATION_CHANNEL"
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/error-rate-alert-policy.yaml

# Database connection alert
cat > /tmp/db-connection-alert-policy.yaml << EOF
displayName: "Meta Ads - Database Connection Issues"
documentation:
  content: "Database connection failures detected"
conditions:
  - displayName: "DB connection failures"
    conditionThreshold:
      filter: 'resource.type="cloudsql_database" AND metric.type="cloudsql.googleapis.com/database/postgresql/num_backends"'
      comparison: COMPARISON_LESS_THAN
      thresholdValue: 1
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
          crossSeriesReducer: REDUCE_MEAN
          groupByFields:
            - resource.label.database_id
combiner: OR
enabled: true
notificationChannels:
  - "$NOTIFICATION_CHANNEL"
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/db-connection-alert-policy.yaml

# Create custom dashboard
print_status "Creating monitoring dashboard..."
cat > /tmp/meta-ads-dashboard.json << 'EOF'
{
  "displayName": "Meta Ads System Dashboard",
  "mosaicLayout": {
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run CPU Utilization",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"meta-ads-api\" AND metric.type=\"run.googleapis.com/container/cpu/utilizations\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_MEAN",
                      "crossSeriesReducer": "REDUCE_MEAN",
                      "groupByFields": ["resource.label.service_name"]
                    }
                  }
                }
              }
            ]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run Memory Utilization",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"meta-ads-api\" AND metric.type=\"run.googleapis.com/container/memory/utilizations\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_MEAN",
                      "crossSeriesReducer": "REDUCE_MEAN",
                      "groupByFields": ["resource.label.service_name"]
                    }
                  }
                }
              }
            ]
          }
        }
      },
      {
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Count",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"meta-ads-api\" AND metric.type=\"run.googleapis.com/request_count\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_RATE",
                      "crossSeriesReducer": "REDUCE_SUM",
                      "groupByFields": ["resource.label.service_name"]
                    }
                  }
                }
              }
            ]
          }
        }
      },
      {
        "xPos": 6,
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Latency",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"meta-ads-api\" AND metric.type=\"run.googleapis.com/request_latencies\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_DELTA",
                      "crossSeriesReducer": "REDUCE_MEAN",
                      "groupByFields": ["resource.label.service_name"]
                    }
                  }
                }
              }
            ]
          }
        }
      },
      {
        "yPos": 8,
        "width": 12,
        "height": 4,
        "widget": {
          "title": "Database Connections",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_MEAN",
                      "crossSeriesReducer": "REDUCE_MEAN",
                      "groupByFields": ["resource.label.database_id"]
                    }
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
EOF

gcloud monitoring dashboards create --config-from-file=/tmp/meta-ads-dashboard.json

# Set up log-based metrics
print_status "Creating log-based metrics..."

# API error rate metric
gcloud logging metrics create meta_ads_api_errors \
    --description="Meta Ads API error rate" \
    --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="meta-ads-api" AND (severity="ERROR" OR httpRequest.status>=400)' \
    --value-extractor='EXTRACT(httpRequest.status)'

# Campaign creation metric
gcloud logging metrics create meta_ads_campaigns_created \
    --description="Meta Ads campaigns created" \
    --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="meta-ads-api" AND jsonPayload.action="campaign_created"'

# ML model performance metric
gcloud logging metrics create meta_ads_ml_performance \
    --description="Meta Ads ML model performance" \
    --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="meta-ads-api" AND jsonPayload.component="ml_model"' \
    --value-extractor='EXTRACT(jsonPayload.performance_score)'

# Set up uptime checks
print_status "Creating uptime checks..."

# Health endpoint uptime check
cat > /tmp/uptime-check.json << EOF
{
  "displayName": "Meta Ads API Health Check",
  "monitoredResource": {
    "type": "uptime_url"
  },
  "httpCheck": {
    "path": "/health",
    "port": 443,
    "useSsl": true,
    "validateSsl": true
  },
  "period": "60s",
  "timeout": "10s",
  "contentMatchers": [
    {
      "content": "healthy"
    }
  ]
}
EOF

# Get the service URL
SERVICE_URL=$(gcloud run services describe meta-ads-api --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    # Extract hostname from URL
    HOSTNAME=$(echo "$SERVICE_URL" | sed 's|https://||' | sed 's|http://||')
    
    # Update the uptime check config with the actual hostname
    sed -i.bak "s|\"httpCheck\": {|\"httpCheck\": {\n    \"requestMethod\": \"GET\",\n    \"host\": \"$HOSTNAME\",|" /tmp/uptime-check.json
    
    gcloud monitoring uptime create --config-from-file=/tmp/uptime-check.json
else
    print_warning "Could not find Cloud Run service URL. Skipping uptime check creation."
fi

# Create log sink for error analysis
print_status "Setting up log sink for error analysis..."
gcloud logging sinks create meta-ads-errors \
    bigquery.googleapis.com/projects/"$PROJECT_ID"/datasets/meta_ads_logs \
    --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="meta-ads-api" AND severity>=ERROR' || true

# Clean up temporary files
rm -f /tmp/*alert-policy.yaml /tmp/meta-ads-dashboard.json /tmp/uptime-check.json /tmp/uptime-check.json.bak

print_status "Monitoring setup completed successfully! 📊"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗"
echo -e "║                    MONITORING SUMMARY                           ║"
echo -e "╠══════════════════════════════════════════════════════════════════╣"
echo -e "║ Notification Email:   $NOTIFICATION_EMAIL"
echo -e "║ Alerting Policies:    4 created (CPU, Memory, Errors, DB)"
echo -e "║ Dashboard:            Meta Ads System Dashboard"
echo -e "║ Log Metrics:          3 created"
echo -e "║ Uptime Checks:        API health endpoint"
echo -e "╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_status "Access your monitoring:"
echo "  Cloud Console:    https://console.cloud.google.com/monitoring"
echo "  Dashboards:       https://console.cloud.google.com/monitoring/dashboards"
echo "  Alerting:         https://console.cloud.google.com/monitoring/alerting"
echo "  Logs:            https://console.cloud.google.com/logs"
echo ""

print_warning "NEXT STEPS:"
echo "1. Verify your notification email and accept any confirmation emails"
echo "2. Customize alerting thresholds if needed"
echo "3. Set up additional custom metrics in your application"
echo "4. Configure Slack notifications if desired"
echo ""

print_status "Monitoring is now active for your Meta Ads system!"