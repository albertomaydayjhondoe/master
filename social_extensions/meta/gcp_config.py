"""
Meta Ads Google Cloud Configuration
Configuration and deployment setup for Meta Ads system on Google Cloud Platform
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class MetaAdsGCPConfig:
    """Google Cloud Platform configuration for Meta Ads system"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent.parent / "config" / "gcp"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def create_gcp_deployment_config(self) -> Dict[str, Any]:
        """Create comprehensive GCP deployment configuration"""
        
        config = {
            "project_info": {
                "project_id": "${GCP_PROJECT_ID}",
                "region": "${GCP_REGION}",
                "zone": "${GCP_ZONE}",
                "service_account": "${GCP_SERVICE_ACCOUNT}",
                "billing_account": "${GCP_BILLING_ACCOUNT}"
            },
            "compute_engine": {
                "meta_ads_api": {
                    "name": "meta-ads-api-vm",
                    "machine_type": "e2-standard-4",
                    "disk_size_gb": 50,
                    "disk_type": "pd-ssd",
                    "image_family": "ubuntu-2204-lts",
                    "image_project": "ubuntu-os-cloud",
                    "tags": ["meta-ads-api", "http-server", "https-server"],
                    "startup_script": "startup-meta-ads.sh"
                },
                "ml_processor": {
                    "name": "meta-ads-ml-vm",
                    "machine_type": "n1-standard-4",
                    "gpu_type": "nvidia-tesla-t4",
                    "gpu_count": 1,
                    "disk_size_gb": 100,
                    "disk_type": "pd-ssd",
                    "image_family": "pytorch-latest-gpu",
                    "image_project": "deeplearning-platform-release",
                    "tags": ["meta-ads-ml", "ml-processor"],
                    "startup_script": "startup-ml-processor.sh"
                }
            },
            "cloud_sql": {
                "instance_name": "meta-ads-db",
                "database_version": "POSTGRES_14",
                "tier": "db-custom-2-7680",
                "region": "${GCP_REGION}",
                "database_name": "meta_ads",
                "username": "meta_ads_user",
                "password": "${DB_PASSWORD}",
                "backup_enabled": True,
                "maintenance_window": {
                    "day": 7,
                    "hour": 2,
                    "update_track": "stable"
                }
            },
            "cloud_storage": {
                "buckets": {
                    "meta_ads_data": {
                        "name": "${GCP_PROJECT_ID}-meta-ads-data",
                        "location": "${GCP_REGION}",
                        "storage_class": "STANDARD",
                        "lifecycle_rules": [
                            {
                                "condition": {"age": 90},
                                "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"}
                            }
                        ]
                    },
                    "meta_ads_models": {
                        "name": "${GCP_PROJECT_ID}-meta-ads-models",
                        "location": "${GCP_REGION}",
                        "storage_class": "STANDARD",
                        "versioning_enabled": True
                    },
                    "meta_ads_logs": {
                        "name": "${GCP_PROJECT_ID}-meta-ads-logs",
                        "location": "${GCP_REGION}",
                        "storage_class": "COLDLINE",
                        "lifecycle_rules": [
                            {
                                "condition": {"age": 365},
                                "action": {"type": "Delete"}
                            }
                        ]
                    }
                }
            },
            "cloud_run": {
                "meta_ads_api_service": {
                    "name": "meta-ads-api",
                    "image": "gcr.io/${GCP_PROJECT_ID}/meta-ads-api:latest",
                    "port": 8000,
                    "memory": "2Gi",
                    "cpu": "2",
                    "max_instances": 10,
                    "min_instances": 1,
                    "concurrency": 80,
                    "timeout": "300s",
                    "env_vars": {
                        "DUMMY_MODE": "false",
                        "DATABASE_URL": "postgresql://meta_ads_user:${DB_PASSWORD}@${DB_PRIVATE_IP}/meta_ads",
                        "GCS_BUCKET": "${GCP_PROJECT_ID}-meta-ads-data",
                        "META_APP_ID": "${META_APP_ID}",
                        "META_APP_SECRET": "${META_APP_SECRET}",
                        "META_ACCESS_TOKEN": "${META_ACCESS_TOKEN}"
                    }
                }
            },
            "cloud_functions": {
                "meta_webhook_handler": {
                    "name": "meta-webhook-handler",
                    "runtime": "python39",
                    "entry_point": "handle_webhook",
                    "memory": "256MB",
                    "timeout": "60s",
                    "trigger": "https",
                    "env_vars": {
                        "META_WEBHOOK_SECRET": "${META_WEBHOOK_SECRET}",
                        "DATABASE_URL": "postgresql://meta_ads_user:${DB_PASSWORD}@${DB_PRIVATE_IP}/meta_ads"
                    }
                },
                "meta_optimization_scheduler": {
                    "name": "meta-optimization-scheduler",
                    "runtime": "python39",
                    "entry_point": "run_optimization",
                    "memory": "512MB",
                    "timeout": "540s",
                    "trigger": "pubsub",
                    "topic": "meta-ads-optimization",
                    "schedule": "0 */6 * * *"
                }
            },
            "pub_sub": {
                "topics": {
                    "meta_ads_optimization": {
                        "name": "meta-ads-optimization",
                        "message_retention_duration": "604800s"
                    },
                    "meta_ads_alerts": {
                        "name": "meta-ads-alerts",
                        "message_retention_duration": "259200s"
                    }
                },
                "subscriptions": {
                    "optimization_worker": {
                        "name": "meta-ads-optimization-sub",
                        "topic": "meta-ads-optimization",
                        "ack_deadline_seconds": 600
                    }
                }
            },
            "cloud_scheduler": {
                "jobs": {
                    "daily_optimization": {
                        "name": "meta-ads-daily-optimization",
                        "schedule": "0 6 * * *",
                        "time_zone": "UTC",
                        "target": {
                            "pubsub_target": {
                                "topic_name": "projects/${GCP_PROJECT_ID}/topics/meta-ads-optimization",
                                "data": "eyJ0eXBlIjogImRhaWx5X29wdGltaXphdGlvbiJ9"
                            }
                        }
                    },
                    "hourly_monitoring": {
                        "name": "meta-ads-hourly-monitoring",
                        "schedule": "0 * * * *",
                        "time_zone": "UTC",
                        "target": {
                            "http_target": {
                                "uri": "https://meta-ads-api-${GCP_PROJECT_ID}.cloudfunctions.net/monitoring-check",
                                "http_method": "POST"
                            }
                        }
                    }
                }
            },
            "monitoring": {
                "notification_channels": {
                    "email_alerts": {
                        "type": "email",
                        "labels": {
                            "email_address": "${ALERT_EMAIL}"
                        }
                    },
                    "slack_alerts": {
                        "type": "slack",
                        "labels": {
                            "channel_name": "#meta-ads-alerts",
                            "url": "${SLACK_WEBHOOK_URL}"
                        }
                    }
                },
                "alert_policies": {
                    "high_error_rate": {
                        "display_name": "Meta Ads High Error Rate",
                        "conditions": [
                            {
                                "display_name": "Error rate > 5%",
                                "condition_threshold": {
                                    "filter": "resource.type=\"cloud_run_revision\"",
                                    "comparison": "COMPARISON_GREATER_THAN",
                                    "threshold_value": 0.05,
                                    "duration": "300s"
                                }
                            }
                        ]
                    },
                    "database_connection_issues": {
                        "display_name": "Database Connection Issues",
                        "conditions": [
                            {
                                "display_name": "DB connection failures > 10",
                                "condition_threshold": {
                                    "filter": "resource.type=\"cloudsql_database\"",
                                    "comparison": "COMPARISON_GREATER_THAN",
                                    "threshold_value": 10,
                                    "duration": "300s"
                                }
                            }
                        ]
                    }
                }
            },
            "security": {
                "firewall_rules": {
                    "allow_meta_ads_api": {
                        "name": "allow-meta-ads-api",
                        "direction": "INGRESS",
                        "priority": 1000,
                        "source_ranges": ["0.0.0.0/0"],
                        "target_tags": ["meta-ads-api"],
                        "allowed": [
                            {"IPProtocol": "tcp", "ports": ["80", "443", "8000"]}
                        ]
                    },
                    "allow_internal_ml": {
                        "name": "allow-internal-ml",
                        "direction": "INGRESS",
                        "priority": 1000,
                        "source_tags": ["meta-ads-api"],
                        "target_tags": ["meta-ads-ml"],
                        "allowed": [
                            {"IPProtocol": "tcp", "ports": ["8080", "9000"]}
                        ]
                    }
                },
                "iam": {
                    "service_accounts": {
                        "meta_ads_api": {
                            "account_id": "meta-ads-api-sa",
                            "display_name": "Meta Ads API Service Account",
                            "roles": [
                                "roles/cloudsql.client",
                                "roles/storage.objectAdmin",
                                "roles/pubsub.publisher",
                                "roles/monitoring.metricWriter"
                            ]
                        },
                        "meta_ads_ml": {
                            "account_id": "meta-ads-ml-sa", 
                            "display_name": "Meta Ads ML Service Account",
                            "roles": [
                                "roles/storage.objectAdmin",
                                "roles/ml.developer",
                                "roles/monitoring.metricWriter"
                            ]
                        }
                    }
                }
            },
            "networking": {
                "vpc": {
                    "name": "meta-ads-vpc",
                    "subnet": {
                        "name": "meta-ads-subnet",
                        "ip_cidr_range": "10.0.0.0/24",
                        "region": "${GCP_REGION}"
                    }
                },
                "load_balancer": {
                    "name": "meta-ads-lb",
                    "backend_service": "meta-ads-api",
                    "health_check": {
                        "path": "/system/health",
                        "port": 8000,
                        "check_interval_sec": 30,
                        "timeout_sec": 10
                    },
                    "ssl_certificate": {
                        "name": "meta-ads-ssl-cert",
                        "domains": ["${META_ADS_DOMAIN}"]
                    }
                }
            }
        }
        
        return config
    
    def create_terraform_main(self) -> str:
        """Create Terraform main configuration file"""
        
        terraform_config = '''
# Meta Ads Google Cloud Infrastructure
# Terraform configuration for complete GCP deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.0"
    }
  }
  
  backend "gcs" {
    bucket = "${var.project_id}-terraform-state"
    prefix = "meta-ads"
  }
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "meta_app_id" {
  description = "Meta App ID"
  type        = string
  sensitive   = true
}

variable "meta_app_secret" {
  description = "Meta App Secret"
  type        = string
  sensitive   = true
}

variable "meta_access_token" {
  description = "Meta Access Token"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "pubsub.googleapis.com",
    "scheduler.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  
  service = each.key
  
  disable_dependent_services = true
}

# VPC Network
resource "google_compute_network" "meta_ads_vpc" {
  name                    = "meta-ads-vpc"
  auto_create_subnetworks = false
  
  depends_on = [google_project_service.required_apis]
}

resource "google_compute_subnetwork" "meta_ads_subnet" {
  name          = "meta-ads-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.meta_ads_vpc.id
}

# Cloud SQL Instance
resource "google_sql_database_instance" "meta_ads_db" {
  name             = "meta-ads-db"
  database_version = "POSTGRES_14"
  region          = var.region
  
  deletion_protection = false
  
  settings {
    tier = "db-custom-2-7680"
    
    backup_configuration {
      enabled    = true
      start_time = "02:00"
    }
    
    maintenance_window {
      day          = 7
      hour         = 2
      update_track = "stable"
    }
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.meta_ads_vpc.id
    }
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_sql_database" "meta_ads_database" {
  name     = "meta_ads"
  instance = google_sql_database_instance.meta_ads_db.name
}

resource "google_sql_user" "meta_ads_user" {
  name     = "meta_ads_user"
  instance = google_sql_database_instance.meta_ads_db.name
  password = var.db_password
}

# Cloud Storage Buckets
resource "google_storage_bucket" "meta_ads_data" {
  name     = "${var.project_id}-meta-ads-data"
  location = var.region
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
  
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "meta_ads_models" {
  name     = "${var.project_id}-meta-ads-models"
  location = var.region
  
  versioning {
    enabled = true
  }
}

# Service Accounts
resource "google_service_account" "meta_ads_api_sa" {
  account_id   = "meta-ads-api-sa"
  display_name = "Meta Ads API Service Account"
}

resource "google_service_account" "meta_ads_ml_sa" {
  account_id   = "meta-ads-ml-sa"
  display_name = "Meta Ads ML Service Account"
}

# IAM Bindings
resource "google_project_iam_member" "meta_ads_api_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/storage.objectAdmin",
    "roles/pubsub.publisher",
    "roles/monitoring.metricWriter"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.meta_ads_api_sa.email}"
}

# Pub/Sub Topics
resource "google_pubsub_topic" "meta_ads_optimization" {
  name = "meta-ads-optimization"
  
  message_retention_duration = "604800s"
}

resource "google_pubsub_subscription" "meta_ads_optimization_sub" {
  name  = "meta-ads-optimization-sub"
  topic = google_pubsub_topic.meta_ads_optimization.name
  
  ack_deadline_seconds = 600
}

# Secret Manager Secrets
resource "google_secret_manager_secret" "meta_credentials" {
  secret_id = "meta-ads-credentials"
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "meta_credentials" {
  secret = google_secret_manager_secret.meta_credentials.id
  
  secret_data = jsonencode({
    meta_app_id      = var.meta_app_id
    meta_app_secret  = var.meta_app_secret
    meta_access_token = var.meta_access_token
  })
}

# Cloud Run Service
resource "google_cloud_run_service" "meta_ads_api" {
  name     = "meta-ads-api"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "autoscaling.knative.dev/minScale" = "1"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.meta_ads_db.connection_name
      }
    }
    
    spec {
      service_account_name = google_service_account.meta_ads_api_sa.email
      
      containers {
        image = "gcr.io/${var.project_id}/meta-ads-api:latest"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "DUMMY_MODE"
          value = "false"
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgresql://meta_ads_user:${var.db_password}@/${google_sql_database.meta_ads_database.name}?host=/cloudsql/${google_sql_database_instance.meta_ads_db.connection_name}"
        }
        
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.meta_ads_data.name
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Run IAM
resource "google_cloud_run_service_iam_member" "meta_ads_api_invoker" {
  service  = google_cloud_run_service.meta_ads_api.name
  location = google_cloud_run_service.meta_ads_api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Firewall Rules
resource "google_compute_firewall" "allow_meta_ads_api" {
  name    = "allow-meta-ads-api"
  network = google_compute_network.meta_ads_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8000"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["meta-ads-api"]
}

# Outputs
output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.meta_ads_api.status[0].url
}

output "database_connection_name" {
  description = "Database connection name"
  value       = google_sql_database_instance.meta_ads_db.connection_name
}

output "storage_bucket_data" {
  description = "Data storage bucket name"
  value       = google_storage_bucket.meta_ads_data.name
}
'''
        
        return terraform_config
    
    def create_dockerfile(self) -> str:
        """Create Dockerfile for Meta Ads API"""
        
        dockerfile = '''
# Meta Ads API Dockerfile for Google Cloud Run
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell  appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/system/health || exit 1

# Run the application
CMD ["python", "-m", "ml_core.api_gateway", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        return dockerfile
    
    def create_cloudbuild_yaml(self) -> str:
        """Create Cloud Build configuration"""
        
        cloudbuild = '''
# Cloud Build configuration for Meta Ads API
steps:
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA',
      '-t', 'gcr.io/$PROJECT_ID/meta-ads-api:latest',
      '.'
    ]
  
  # Push the image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/meta-ads-api:latest']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: [
      'run', 'deploy', 'meta-ads-api',
      '--image', 'gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA',
      '--platform', 'managed',
      '--region', 'us-central1',
      '--allow-unauthenticated',
      '--set-env-vars', 'DUMMY_MODE=false',
      '--memory', '2Gi',
      '--cpu', '2',
      '--max-instances', '10',
      '--min-instances', '1',
      '--port', '8000'
    ]

# Store images in Container Registry
images:
  - 'gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/meta-ads-api:latest'

# Build options
options:
  machineType: 'E2_HIGHCPU_8'
  substitution_option: 'ALLOW_LOOSE'

# Timeout
timeout: '1200s'
'''
        
        return cloudbuild
    
    def create_deployment_scripts(self) -> Dict[str, str]:
        """Create deployment scripts for GCP"""
        
        scripts = {}
        
        # Setup script
        scripts['setup_gcp.sh'] = '''#!

# Meta Ads GCP Setup Script
set -e

echo "🚀 Meta Ads Google Cloud Setup"
echo "=============================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ terraform not found. Please install Terraform"
    exit 1
fi

# Set variables
PROJECT_ID=${GCP_PROJECT_ID:-""}
REGION=${GCP_REGION:-"us-central1"}
ZONE=${GCP_ZONE:-"us-central1-a"}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ GCP_PROJECT_ID environment variable not set"
    exit 1
fi

echo "📋 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "📍 Zone: $ZONE"

# Set current project
gcloud config set project $PROJECT_ID

# Enable billing (if needed)
echo "💳 Checking billing..."
gcloud billing projects link $PROJECT_ID --billing-account=${GCP_BILLING_ACCOUNT} || true

# Create Terraform state bucket
echo "📦 Creating Terraform state bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-terraform-state || true
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Initialize Terraform
echo "🔧 Initializing Terraform..."
cd gcp/terraform
terraform init

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="zone=$ZONE"

echo ""
echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Review the Terraform plan above"
echo "2. Set Meta API credentials:"
echo "   export META_APP_ID=your_app_id"
echo "   export META_APP_SECRET=your_app_secret"
echo "   export META_ACCESS_TOKEN=your_access_token"
echo "   export DB_PASSWORD=your_db_password"
echo "3. Run: terraform apply"
echo "4. Build and deploy: python scripts/cross_platform_runner.py"
'''

        # Deploy script  
        scripts['deploy.sh'] = '''#!

# Meta Ads Deployment Script
set -e

echo "🚀 Deploying Meta Ads to Google Cloud"
echo "===================================="

# Check required environment variables
required_vars=("GCP_PROJECT_ID" "META_APP_ID" "META_APP_SECRET" "META_ACCESS_TOKEN" "DB_PASSWORD")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    fi
done

PROJECT_ID=$GCP_PROJECT_ID
REGION=${GCP_REGION:-"us-central1"}

echo "📋 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"

# Apply Terraform configuration
echo "🏗️ Deploying infrastructure..."
cd gcp/terraform
terraform apply -var="project_id=$PROJECT_ID" \
                -var="region=$REGION" \
                -var="meta_app_id=$META_APP_ID" \
                -var="meta_app_secret=$META_APP_SECRET" \
                -var="meta_access_token=$META_ACCESS_TOKEN" \
                -var="db_password=$DB_PASSWORD" \
                -auto-approve

cd ../..

# Build and deploy application
echo "🐳 Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/meta-ads-api .

echo "☁️ Deploying to Cloud Run..."
gcloud run deploy meta-ads-api \
    --image gcr.io/$PROJECT_ID/meta-ads-api \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars DUMMY_MODE=false \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8000

# Get service URL
SERVICE_URL=$(gcloud run services describe meta-ads-api --region=$REGION --format="value(status.url)")

echo ""
echo "🎉 Deployment completed!"
echo "📡 Service URL: $SERVICE_URL"
echo "📊 Health check: $SERVICE_URL/system/health"
echo "📚 API docs: $SERVICE_URL/docs"
'''

        # Monitoring setup
        scripts['setup_monitoring.sh'] = '''#!

# Meta Ads Monitoring Setup
set -e

echo "📊 Setting up Meta Ads monitoring..."

PROJECT_ID=$GCP_PROJECT_ID
REGION=${GCP_REGION:-"us-central1"}

# Create notification channels
echo "📧 Creating notification channels..."

# Email notification
gcloud alpha monitoring channels create \
    --display-name="Meta Ads Email Alerts" \
    --type=email \
    --channel-labels=email_address=${ALERT_EMAIL} \
    --project=$PROJECT_ID

# Slack notification (if configured)
if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    gcloud alpha monitoring channels create \
        --display-name="Meta Ads Slack Alerts" \
        --type=slack \
        --channel-labels=url=${SLACK_WEBHOOK_URL} \
        --project=$PROJECT_ID
fi

# Create alert policies
echo "🚨 Creating alert policies..."

# High error rate alert
cat > alert_policy_error_rate.yaml << EOF
displayName: "Meta Ads High Error Rate"
conditions:
  - displayName: "Error rate > 5%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" resource.label.service_name="meta-ads-api"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.05
      duration: 300s
alertStrategy:
  autoClose: 86400s
notificationChannels:
  - $(gcloud alpha monitoring channels list --filter="displayName:'Meta Ads Email Alerts'" --format="value(name)")
EOF

gcloud alpha monitoring policies create --policy-from-file=alert_policy_error_rate.yaml

echo "✅ Monitoring setup completed!"
'''

        return scripts
    
    def save_all_configs(self) -> Dict[str, str]:
        """Save all GCP configuration files"""
        
        files_created = {}
        
        # Create GCP directory structure
        gcp_dir = self.config_dir / "gcp"
        terraform_dir = gcp_dir / "terraform"
        scripts_dir = gcp_dir / "scripts"
        
        for directory in [gcp_dir, terraform_dir, scripts_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Save main configuration
        config = self.create_gcp_deployment_config()
        config_file = gcp_dir / "meta_ads_gcp_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        files_created['config'] = str(config_file)
        
        # Save Terraform configuration
        terraform_config = self.create_terraform_main()
        terraform_file = terraform_dir / "main.tf"
        with open(terraform_file, 'w') as f:
            f.write(terraform_config)
        files_created['terraform'] = str(terraform_file)
        
        # Save Dockerfile
        dockerfile_content = self.create_dockerfile()
        dockerfile = Path(__file__).parent.parent.parent / "Dockerfile.gcp"
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)
        files_created['dockerfile'] = str(dockerfile)
        
        # Save Cloud Build configuration
        cloudbuild_content = self.create_cloudbuild_yaml()
        cloudbuild_file = Path(__file__).parent.parent.parent / "cloudbuild.yaml"
        with open(cloudbuild_file, 'w') as f:
            f.write(cloudbuild_content)
        files_created['cloudbuild'] = str(cloudbuild_file)
        
        # Save deployment scripts
        scripts = self.create_deployment_scripts()
        for script_name, script_content in scripts.items():
            script_file = scripts_dir / script_name
            with open(script_file, 'w') as f:
                f.write(script_content)
            # Make executable
            os.chmod(script_file, 0o755)
            files_created[script_name] = str(script_file)
        
        # Create environment template
        env_template = self.create_gcp_env_template()
        env_file = gcp_dir / "gcp_production.env.template"
        with open(env_file, 'w') as f:
            f.write(env_template)
        files_created['env_template'] = str(env_file)
        
        return files_created
    
    def create_gcp_env_template(self) -> str:
        """Create GCP environment variables template"""
        
        env_template = '''
# Meta Ads Google Cloud Production Environment
# Copy to .env and fill in your actual values

# ============================================
# Google Cloud Platform Configuration
# ============================================

# GCP Project ID
GCP_PROJECT_ID=your-gcp-project-id

# GCP Region and Zone
GCP_REGION=us-central1
GCP_ZONE=us-central1-a

# GCP Service Account (optional)
GCP_SERVICE_ACCOUNT=meta-ads-api-sa@your-gcp-project-id.iam.gserviceaccount.com

# GCP Billing Account (for setup)
GCP_BILLING_ACCOUNT=your-billing-account-id

# ============================================
# Meta Business API Configuration
# ============================================

# Facebook App ID (from Facebook Developers)
META_APP_ID=your_facebook_app_id_here

# Facebook App Secret (keep secure!)
META_APP_SECRET=your_facebook_app_secret_here

# Long-lived User Access Token (refresh regularly)
META_ACCESS_TOKEN=your_long_lived_access_token_here

# Ad Account ID (without 'act_' prefix)
META_AD_ACCOUNT_ID=1234567890

# Facebook Page ID
META_PAGE_ID=0987654321

# Meta Pixel ID
META_PIXEL_ID=your_pixel_id_here

# Webhook Verify Token (create a random secure string)
META_WEBHOOK_VERIFY_TOKEN=your_secure_webhook_token_here

# ============================================
# Database Configuration
# ============================================

# Database password for Cloud SQL
DB_PASSWORD=your_secure_database_password

# ============================================
# Application Settings
# ============================================

# Disable dummy mode for production
DUMMY_MODE=false

# Enable Meta Ads module
ENABLE_META_ADS=true

# ============================================
# Monitoring & Alerts
# ============================================

# Email for alerts
ALERT_EMAIL=admin@yourcompany.com

# Slack webhook for alerts (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# ============================================
# Domain & SSL
# ============================================

# Custom domain for the API (optional)
META_ADS_DOMAIN=meta-ads-api.yourcompany.com

# ============================================
# Performance Settings
# ============================================

# API Rate limiting
API_RATE_LIMIT=1000
API_BURST_LIMIT=100

# Worker Configuration
MAX_WORKERS=10
WORKER_MEMORY=2Gi
WORKER_CPU=2
'''
        
        return env_template

# Factory function
def create_meta_ads_gcp_config() -> MetaAdsGCPConfig:
    """Create Meta Ads GCP configuration manager"""
    return MetaAdsGCPConfig()

if __name__ == "__main__":
    # Generate all GCP configuration files
    config_manager = create_meta_ads_gcp_config()
    
    print("☁️ Creating Meta Ads Google Cloud configuration...")
    
    files_created = config_manager.save_all_configs()
    
    print(f"""
🎯 Meta Ads Google Cloud Setup Files Created:

📋 Main Configuration: {files_created['config']}
🏗️ Terraform Config: {files_created['terraform']}
🐳 Dockerfile: {files_created['dockerfile']}
⚙️ Cloud Build: {files_created['cloudbuild']}
🔧 Environment Template: {files_created['env_template']}

🚀 Deployment Scripts:
- Setup: {files_created['setup_gcp.sh']}
- Deploy: {files_created['deploy.sh']}
- Monitoring: {files_created['setup_monitoring.sh']}

Next steps for GCP deployment:
1. Copy environment template to .env and fill in your values
2. Install Google Cloud SDK and Terraform
3. Run: bash config/gcp/scripts/setup_gcp.sh
4. Run: bash config/gcp/scripts/deploy.sh

💡 This will deploy Meta Ads system to Google Cloud with:
- Cloud Run for API hosting
- Cloud SQL for database
- Cloud Storage for data/models
- Cloud Functions for webhooks
- Pub/Sub for async processing
- Monitoring and alerting
""")