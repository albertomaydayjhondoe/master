# Meta Ads GCP Terraform Configuration
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
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
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

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudscheduler.googleapis.com"
  ])

  service = each.key
  project = var.project_id

  disable_dependent_services = false
  disable_on_destroy         = false
}

# VPC Network
resource "google_compute_network" "meta_ads_network" {
  name                    = "meta-ads-network"
  auto_create_subnetworks = false
  project                 = var.project_id
}

# Subnet
resource "google_compute_subnetwork" "meta_ads_subnet" {
  name          = "meta-ads-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.meta_ads_network.id
  project       = var.project_id

  private_ip_google_access = true
}

# Cloud SQL Instance
resource "google_sql_database_instance" "meta_ads_db" {
  name             = "meta-ads-db-${var.environment}"
  database_version = "POSTGRES_14"
  region          = var.region
  project         = var.project_id

  settings {
    tier                        = "db-f1-micro"
    disk_type                  = "PD_SSD"
    disk_size                  = 20
    disk_autoresize           = true
    disk_autoresize_limit     = 100
    availability_type         = "ZONAL"
    deletion_protection_enabled = false

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.meta_ads_network.id
      require_ssl     = true
    }

    database_flags {
      name  = "log_statement"
      value = "all"
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_networking_connection.private_vpc_connection
  ]

  deletion_protection = false
}

# Private VPC connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "meta-ads-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.meta_ads_network.id
  project       = var.project_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.meta_ads_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Cloud SQL Database
resource "google_sql_database" "meta_ads_database" {
  name     = "meta_ads"
  instance = google_sql_database_instance.meta_ads_db.name
  project  = var.project_id
}

# Cloud SQL User
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "google_sql_user" "meta_ads_user" {
  name     = "meta_ads_user"
  instance = google_sql_database_instance.meta_ads_db.name
  password = random_password.db_password.result
  project  = var.project_id
}

# Cloud Storage Buckets
resource "google_storage_bucket" "meta_ads_storage" {
  name          = "${var.project_id}-meta-ads-storage"
  location      = var.region
  project       = var.project_id
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "meta_ads_models" {
  name          = "${var.project_id}-meta-ads-models"
  location      = var.region
  project       = var.project_id
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Pub/Sub Topics
resource "google_pubsub_topic" "meta_ads_events" {
  name    = "meta-ads-events"
  project = var.project_id

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_subscription" "meta_ads_events_sub" {
  name  = "meta-ads-events-subscription"
  topic = google_pubsub_topic.meta_ads_events.name
  project = var.project_id

  message_retention_duration = "1200s"
  retain_acked_messages      = true

  expiration_policy {
    ttl = "300000.5s"
  }
}

# Secret Manager Secrets
resource "google_secret_manager_secret" "meta_api_secrets" {
  secret_id = "meta-api-secrets"
  project   = var.project_id

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"
  project   = var.project_id

  replication {
    automatic = true
  }

  depends_on = [google_project_service.required_apis]
}

# Service Account for Cloud Run
resource "google_service_account" "meta_ads_service_account" {
  account_id   = "meta-ads-service"
  display_name = "Meta Ads Service Account"
  description  = "Service account for Meta Ads Cloud Run services"
  project      = var.project_id
}

# IAM roles for service account
resource "google_project_iam_member" "service_account_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/storage.objectAdmin",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/secretmanager.secretAccessor",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent"
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.meta_ads_service_account.email}"
}

# Cloud Run Service
resource "google_cloud_run_service" "meta_ads_api" {
  name     = "meta-ads-api"
  location = var.region
  project  = var.project_id

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"        = "10"
        "autoscaling.knative.dev/minScale"        = "1"
        "run.googleapis.com/cloudsql-instances"   = google_sql_database_instance.meta_ads_db.connection_name
        "run.googleapis.com/execution-environment" = "gen2"
      }
    }

    spec {
      container_concurrency = 100
      timeout_seconds      = 300
      service_account_name = google_service_account.meta_ads_service_account.email

      containers {
        image = "gcr.io/${var.project_id}/meta-ads-api:latest"

        ports {
          container_port = 8000
        }

        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
          requests = {
            cpu    = "1"
            memory = "1Gi"
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.database_url.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "META_API_SECRETS"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.meta_api_secrets.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "PUBSUB_TOPIC"
          value = google_pubsub_topic.meta_ads_events.name
        }

        env {
          name  = "STORAGE_BUCKET"
          value = google_storage_bucket.meta_ads_storage.name
        }

        env {
          name  = "MODELS_BUCKET"
          value = google_storage_bucket.meta_ads_models.name
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.meta_ads_service_account
  ]
}

# Cloud Run IAM
resource "google_cloud_run_service_iam_binding" "meta_ads_api_public" {
  location = google_cloud_run_service.meta_ads_api.location
  project  = google_cloud_run_service.meta_ads_api.project
  service  = google_cloud_run_service.meta_ads_api.name
  role     = "roles/run.invoker"

  members = [
    "allUsers",
  ]
}

# Cloud Scheduler Jobs for ML tasks
resource "google_cloud_scheduler_job" "model_retraining" {
  name      = "meta-ads-model-retraining"
  project   = var.project_id
  region    = var.region
  schedule  = "0 2 * * *" # Daily at 2 AM

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.meta_ads_api.status[0].url}/ml/retrain"
    
    oidc_token {
      service_account_email = google_service_account.meta_ads_service_account.email
    }
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_scheduler_job" "campaign_optimization" {
  name      = "meta-ads-campaign-optimization"
  project   = var.project_id
  region    = var.region
  schedule  = "0 */4 * * *" # Every 4 hours

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.meta_ads_api.status[0].url}/campaigns/optimize-all"
    
    oidc_token {
      service_account_email = google_service_account.meta_ads_service_account.email
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Outputs
output "api_url" {
  description = "URL of the deployed Meta Ads API"
  value       = google_cloud_run_service.meta_ads_api.status[0].url
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.meta_ads_db.connection_name
}

output "storage_bucket_name" {
  description = "Main storage bucket name"
  value       = google_storage_bucket.meta_ads_storage.name
}

output "models_bucket_name" {
  description = "Models storage bucket name"
  value       = google_storage_bucket.meta_ads_models.name
}

output "pubsub_topic_name" {
  description = "Pub/Sub topic name"
  value       = google_pubsub_topic.meta_ads_events.name
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.meta_ads_service_account.email
}