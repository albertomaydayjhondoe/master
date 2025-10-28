#!/bin/bash

# Meta Ads GCP Validation Script
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${2:-us-central1}"

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Print banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║            Meta Ads GCP Validation Script                ║
║                                                          ║
║  This script validates your GCP deployment setup         ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

if [ -z "$PROJECT_ID" ]; then
    print_error "No project ID found. Usage: $0 <PROJECT_ID> [REGION]"
    exit 1
fi

print_info "Validating Meta Ads deployment for project: $PROJECT_ID"
print_info "Region: $REGION"
echo ""

# Check gcloud authentication
print_info "Checking authentication..."
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    print_status "Authenticated as: $ACTIVE_ACCOUNT"
else
    print_error "Not authenticated with gcloud. Run: gcloud auth login"
    exit 1
fi

# Check project access
print_info "Checking project access..."
if gcloud projects describe "$PROJECT_ID" &>/dev/null; then
    print_status "Project $PROJECT_ID is accessible"
else
    print_error "Cannot access project $PROJECT_ID"
    exit 1
fi

# Check billing
print_info "Checking billing..."
if gcloud billing projects describe "$PROJECT_ID" --format="value(billingEnabled)" 2>/dev/null | grep -q "True"; then
    print_status "Billing is enabled"
else
    print_warning "Billing may not be enabled. Check: https://console.cloud.google.com/billing"
fi

# Check required APIs
print_info "Checking required APIs..."
REQUIRED_APIS=(
    "run.googleapis.com"
    "sqladmin.googleapis.com" 
    "storage.googleapis.com"
    "pubsub.googleapis.com"
    "secretmanager.googleapis.com"
    "monitoring.googleapis.com"
    "cloudbuild.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        print_status "API enabled: $api"
    else
        print_warning "API not enabled: $api"
    fi
done

# Check Terraform
print_info "Checking Terraform..."
if command -v terraform &> /dev/null; then
    TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version' 2>/dev/null || terraform version | head -1 | cut -d' ' -f2)
    print_status "Terraform installed: $TERRAFORM_VERSION"
else
    print_error "Terraform not installed"
fi

# Check Docker
print_info "Checking Docker..."
if command -v docker &> /dev/null; then
    if docker info &>/dev/null; then
        DOCKER_VERSION=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "unknown")
        print_status "Docker running: $DOCKER_VERSION"
    else
        print_warning "Docker installed but not running"
    fi
else
    print_error "Docker not installed"
fi

# Check if deployed
print_info "Checking deployed resources..."

# Cloud Run service
if gcloud run services describe meta-ads-api --region="$REGION" &>/dev/null; then
    SERVICE_URL=$(gcloud run services describe meta-ads-api --region="$REGION" --format="value(status.url)")
    print_status "Cloud Run service deployed: $SERVICE_URL"
    
    # Test health endpoint
    if curl -s -f "$SERVICE_URL/health" | grep -q "healthy"; then
        print_status "Health check passed"
    else
        print_warning "Health check failed or service not responding"
    fi
else
    print_warning "Cloud Run service not deployed"
fi

# Cloud SQL
if gcloud sql instances describe meta-ads-db-prod &>/dev/null; then
    DB_STATUS=$(gcloud sql instances describe meta-ads-db-prod --format="value(state)")
    print_status "Cloud SQL instance: $DB_STATUS"
else
    print_warning "Cloud SQL instance not found"
fi

# Storage buckets
if gsutil ls -b gs://"$PROJECT_ID"-meta-ads-storage &>/dev/null; then
    print_status "Storage bucket exists"
else
    print_warning "Storage bucket not found"
fi

# Secrets
if gcloud secrets describe meta-api-secrets &>/dev/null; then
    print_status "Meta API secrets configured"
else
    print_warning "Meta API secrets not configured"
fi

# Service account
if gcloud iam service-accounts describe meta-ads-service@"$PROJECT_ID".iam.gserviceaccount.com &>/dev/null; then
    print_status "Service account exists"
else
    print_warning "Service account not found"
fi

# Check environment file
print_info "Checking configuration files..."
if [ -f ".env" ]; then
    print_status ".env file exists"
    
    # Check for required variables
    if grep -q "META_APP_ID=" .env && grep -q "GCP_PROJECT_ID=" .env; then
        print_status "Required environment variables found"
    else
        print_warning "Some required variables may be missing in .env"
    fi
else
    print_warning ".env file not found. Copy from .env.template"
fi

# Check Terraform state
if [ -f "terraform.tfstate" ]; then
    print_status "Terraform state file exists"
else
    print_warning "Terraform state file not found - infrastructure may not be deployed"
fi

# Summary
echo ""
print_info "Validation Summary:"

# Check if everything is working
ALL_GOOD=true

# Critical checks
if ! command -v terraform &> /dev/null; then ALL_GOOD=false; fi
if ! command -v docker &> /dev/null; then ALL_GOOD=false; fi
if ! gcloud projects describe "$PROJECT_ID" &>/dev/null; then ALL_GOOD=false; fi

if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║  🎉 All critical components validated successfully!            ║
║                                                               ║
║  Your Meta Ads GCP deployment appears to be ready!           ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    if gcloud run services describe meta-ads-api --region="$REGION" &>/dev/null; then
        SERVICE_URL=$(gcloud run services describe meta-ads-api --region="$REGION" --format="value(status.url)")
        print_info "Next steps:"
        echo "  • Test API: curl $SERVICE_URL/health"
        echo "  • View docs: $SERVICE_URL/docs"
        echo "  • Monitor: https://console.cloud.google.com/monitoring"
    else
        print_info "Ready to deploy! Run: ./deploy.sh $PROJECT_ID"
    fi
else
    echo -e "${YELLOW}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║  ⚠️  Some issues found that need attention                     ║
║                                                               ║
║  Please check the warnings above before deploying            ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
fi

echo ""