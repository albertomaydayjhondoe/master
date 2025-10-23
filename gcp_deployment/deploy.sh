#!/bin/bash

# Meta Ads Deployment Script
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
BUILD_MODE="${3:-production}"

# Print banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║              Meta Ads Deployment Script                   ║
║                                                          ║
║  This script builds and deploys the Meta Ads API         ║
║  to Google Cloud Run                                     ║
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

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed."
    exit 1
fi

print_status "Starting deployment for project: $PROJECT_ID"
print_status "Region: $REGION"
print_status "Build mode: $BUILD_MODE"

# Change to project root
cd "$(dirname "$0")/.."

# Check if required files exist
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run from project root."
    exit 1
fi

# Create requirements-prod.txt if it doesn't exist
if [ ! -f "requirements-prod.txt" ]; then
    print_status "Creating production requirements file..."
    cat > requirements-prod.txt << EOF
google-cloud-storage==2.10.0
google-cloud-pubsub==2.18.4
google-cloud-secret-manager==2.17.0
google-cloud-monitoring==2.16.0
google-cloud-logging==3.8.0
psycopg2-binary==2.9.7
facebook-business==18.0.2
uvicorn[standard]==0.23.2
gunicorn==21.2.0
EOF
fi

# Set up Docker authentication for GCR
print_status "Configuring Docker authentication..."
gcloud auth configure-docker --quiet

# Get Git commit SHA for tagging
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
print_status "Using commit SHA: $COMMIT_SHA"

# Build the Docker image locally first (faster feedback)
print_status "Building Docker image locally..."
docker build \
    -f gcp_deployment/Dockerfile \
    -t "gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA" \
    -t "gcr.io/$PROJECT_ID/meta-ads-api:latest" \
    .

# Test the container locally
print_status "Testing container locally..."
CONTAINER_ID=$(docker run -d \
    -e DUMMY_MODE=true \
    -e DATABASE_URL=sqlite:///test.db \
    -p 8080:8000 \
    "gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA")

# Wait for container to start
sleep 5

# Test health endpoint
if curl -f -s "http://localhost:8080/health" > /dev/null; then
    print_status "Container health check passed ✓"
else
    print_error "Container health check failed ✗"
    docker logs "$CONTAINER_ID"
    docker stop "$CONTAINER_ID" || true
    exit 1
fi

# Stop test container
docker stop "$CONTAINER_ID" || true

# Push images to Google Container Registry
print_status "Pushing images to Google Container Registry..."
docker push "gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA"
docker push "gcr.io/$PROJECT_ID/meta-ads-api:latest"

# Use Cloud Build for deployment if available, otherwise deploy directly
if [ "$BUILD_MODE" = "cloudbuild" ]; then
    print_status "Deploying using Cloud Build..."
    
    # Submit to Cloud Build
    gcloud builds submit \
        --config=gcp_deployment/cloudbuild.yaml \
        --substitutions="_REGION=$REGION,_ENVIRONMENT=prod" \
        .
        
else
    print_status "Deploying directly to Cloud Run..."
    
    # Deploy to Cloud Run directly
    gcloud run deploy meta-ads-api \
        --image="gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --service-account="meta-ads-service@$PROJECT_ID.iam.gserviceaccount.com" \
        --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=prod" \
        --memory=2Gi \
        --cpu=2 \
        --concurrency=100 \
        --max-instances=10 \
        --min-instances=1 \
        --timeout=300 \
        --quiet
fi

# Get the service URL
SERVICE_URL=$(gcloud run services describe meta-ads-api --region="$REGION" --format="value(status.url)")

# Test the deployed service
print_status "Testing deployed service..."
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    print_status "Deployed service health check passed ✓"
else
    print_warning "Deployed service health check failed. Service may still be starting..."
fi

# Set up Cloud Scheduler jobs if they don't exist
print_status "Setting up scheduled jobs..."

# Model retraining job
if ! gcloud scheduler jobs describe meta-ads-model-retraining --location="$REGION" &>/dev/null; then
    gcloud scheduler jobs create http meta-ads-model-retraining \
        --location="$REGION" \
        --schedule="0 2 * * *" \
        --uri="$SERVICE_URL/ml/retrain" \
        --http-method=POST \
        --oidc-service-account-email="meta-ads-service@$PROJECT_ID.iam.gserviceaccount.com" \
        --quiet
fi

# Campaign optimization job
if ! gcloud scheduler jobs describe meta-ads-campaign-optimization --location="$REGION" &>/dev/null; then
    gcloud scheduler jobs create http meta-ads-campaign-optimization \
        --location="$REGION" \
        --schedule="0 */4 * * *" \
        --uri="$SERVICE_URL/campaigns/optimize-all" \
        --http-method=POST \
        --oidc-service-account-email="meta-ads-service@$PROJECT_ID.iam.gserviceaccount.com" \
        --quiet
fi

# Update Secret Manager with service URL if needed
gcloud secrets versions add api-service-url --data-file=<(echo -n "$SERVICE_URL") || \
gcloud secrets create api-service-url --data-file=<(echo -n "$SERVICE_URL")

# Clean up local Docker images to save space
print_status "Cleaning up local Docker images..."
docker image prune -f

# Print deployment summary
print_status "Deployment completed successfully! 🚀"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗"
echo -e "║                     DEPLOYMENT SUMMARY                          ║"
echo -e "╠══════════════════════════════════════════════════════════════════╣"
echo -e "║ Service URL:      $SERVICE_URL"
echo -e "║ Image:            gcr.io/$PROJECT_ID/meta-ads-api:$COMMIT_SHA"
echo -e "║ Region:           $REGION"
echo -e "║ Commit SHA:       $COMMIT_SHA"
echo -e "╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_status "API Endpoints:"
echo "  Health Check:     $SERVICE_URL/health"
echo "  API Docs:         $SERVICE_URL/docs"
echo "  Campaign Mgmt:    $SERVICE_URL/campaigns/"
echo "  ML Services:      $SERVICE_URL/ml/"
echo "  Monitoring:       $SERVICE_URL/monitoring/"
echo ""

print_warning "NEXT STEPS:"
echo "1. Test your API endpoints:"
echo "   curl $SERVICE_URL/health"
echo "2. Update your application secrets:"
echo "   gcloud secrets versions add meta-api-secrets --data-file=secrets.json"
echo "3. Monitor your deployment:"
echo "   gcloud run services list --region=$REGION"
echo "4. Check logs:"
echo "   gcloud logs tail meta-ads-api --region=$REGION"
echo ""

print_status "Meta Ads API deployed successfully to Google Cloud Run!"