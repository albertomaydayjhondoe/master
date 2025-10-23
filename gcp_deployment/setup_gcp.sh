#!/bin/bash

# Meta Ads GCP Setup Script
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
ZONE="${3:-us-central1-a}"

# Print banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║              Meta Ads GCP Setup Script                    ║
║                                                          ║
║  This script will set up the complete Google Cloud       ║
║  infrastructure for the Meta Ads automation system       ║
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

# Check if project ID is provided
if [ -z "$PROJECT_ID" ]; then
    print_error "Usage: $0 <PROJECT_ID> [REGION] [ZONE]"
    print_error "Example: $0 my-meta-ads-project us-central1 us-central1-a"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first."
    print_error "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install it first."
    print_error "Visit: https://learn.hashicorp.com/tutorials/terraform/install-cli"
    exit 1
fi

print_status "Starting Meta Ads GCP setup for project: $PROJECT_ID"
print_status "Region: $REGION, Zone: $ZONE"

# Set the project
print_status "Setting active project..."
gcloud config set project "$PROJECT_ID"

# Enable billing (user needs to do this manually)
print_warning "Please ensure billing is enabled for project $PROJECT_ID"
print_warning "Visit: https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"

# Check if project exists
if ! gcloud projects describe "$PROJECT_ID" &>/dev/null; then
    print_error "Project $PROJECT_ID does not exist or you don't have access to it."
    exit 1
fi

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com \
    pubsub.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudtrace.googleapis.com \
    secretmanager.googleapis.com \
    cloudscheduler.googleapis.com \
    servicenetworking.googleapis.com \
    containerregistry.googleapis.com

print_status "APIs enabled successfully!"

# Set up authentication for Terraform
print_status "Setting up Terraform authentication..."
if [ ! -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
    gcloud auth application-default login
fi

# Initialize Terraform
print_status "Initializing Terraform..."
cd "$(dirname "$0")"
terraform init

# Create terraform.tfvars file
print_status "Creating Terraform variables file..."
cat > terraform.tfvars << EOF
project_id  = "$PROJECT_ID"
region      = "$REGION"
zone        = "$ZONE"
environment = "prod"
EOF

# Plan Terraform deployment
print_status "Planning Terraform deployment..."
terraform plan -var-file="terraform.tfvars"

# Ask for confirmation
echo ""
print_warning "Ready to deploy infrastructure to Google Cloud Platform."
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Deploying infrastructure..."
    terraform apply -var-file="terraform.tfvars" -auto-approve
else
    print_warning "Deployment cancelled."
    exit 0
fi

# Get Terraform outputs
print_status "Retrieving deployment information..."
API_URL=$(terraform output -raw api_url 2>/dev/null || echo "Not deployed yet")
DB_CONNECTION=$(terraform output -raw database_connection_name 2>/dev/null || echo "Not created yet")
STORAGE_BUCKET=$(terraform output -raw storage_bucket_name 2>/dev/null || echo "Not created yet")
SERVICE_ACCOUNT=$(terraform output -raw service_account_email 2>/dev/null || echo "Not created yet")

# Set up secrets
print_status "Setting up Secret Manager secrets..."

# Create database URL secret
DB_URL="postgresql://meta_ads_user:$(terraform output -raw db_password 2>/dev/null || echo 'CHANGE_ME')@/$PROJECT_ID:$REGION:meta-ads-db-prod/meta_ads"
echo -n "$DB_URL" | gcloud secrets versions add database-url --data-file=-

# Create placeholder for Meta API secrets
echo -n '{"app_id":"","app_secret":"","access_token":"","ad_account_id":"","business_id":"","pixel_id":""}' | \
    gcloud secrets versions add meta-api-secrets --data-file=-

print_warning "Please update the meta-api-secrets in Secret Manager with your actual Meta API credentials:"
print_warning "gcloud secrets versions add meta-api-secrets --data-file=path-to-your-secrets.json"

# Create .env file from template
print_status "Creating environment configuration file..."
if [ ! -f ".env" ]; then
    cp .env.template .env
    
    # Replace placeholders in .env file
    sed -i.bak "s/your-gcp-project-id/$PROJECT_ID/g" .env
    sed -i.bak "s/your-project/$PROJECT_ID/g" .env
    sed -i.bak "s/us-central1/$REGION/g" .env
    
    rm .env.bak 2>/dev/null || true
    
    print_status "Environment file created: .env"
    print_warning "Please edit .env file and add your Meta API credentials"
fi

# Set up Cloud Build trigger (optional)
print_status "Setting up Cloud Build trigger..."
cat > cloudbuild-trigger.json << EOF
{
  "name": "meta-ads-deploy-trigger",
  "description": "Deploy Meta Ads on code changes",
  "trigger": {
    "branch": {
      "name": "main"
    }
  },
  "build": {
    "source": {
      "repoSource": {
        "projectId": "$PROJECT_ID",
        "repoName": "meta-ads-repo"
      }
    },
    "steps": [
      {
        "name": "gcr.io/cloud-builders/gcloud",
        "entrypoint": "bash",
        "args": ["-c", "gcp_deployment/deploy.sh"]
      }
    ]
  }
}
EOF

# Print deployment summary
print_status "Deployment completed successfully! 🎉"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗"
echo -e "║                     DEPLOYMENT SUMMARY                          ║"
echo -e "╠══════════════════════════════════════════════════════════════════╣"
echo -e "║ Project ID:       $PROJECT_ID"
echo -e "║ Region:           $REGION"
echo -e "║ API URL:          $API_URL"
echo -e "║ Database:         $DB_CONNECTION"
echo -e "║ Storage Bucket:   $STORAGE_BUCKET"
echo -e "║ Service Account:  $SERVICE_ACCOUNT"
echo -e "╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_warning "NEXT STEPS:"
echo "1. Update .env file with your Meta API credentials"
echo "2. Update Secret Manager with actual API keys:"
echo "   gcloud secrets versions add meta-api-secrets --data-file=secrets.json"
echo "3. Build and deploy the application:"
echo "   ./deploy.sh"
echo "4. Set up monitoring:"
echo "   ./setup_monitoring.sh"
echo ""

print_status "Setup complete! Your Meta Ads infrastructure is ready on Google Cloud Platform."