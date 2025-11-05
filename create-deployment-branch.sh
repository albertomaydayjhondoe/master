#!/bin/bash
# 🌿 Neural Forge - Branch Deployment Creator
# ==========================================
# Creates a deployment branch with all infrastructure

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🌿 Neural Forge - Deployment Branch Creator${NC}"
echo -e "${CYAN}===========================================${NC}"

# Configuration
DEPLOYMENT_BRANCH="deployment/hetzner-production"
BACKUP_BRANCH="backup/pre-deployment-$(date +%Y%m%d-%H%M%S)"
DEPLOYMENT_TAG="v3.0-deployment-$(date +%Y%m%d)"

# Function to check git status
check_git_status() {
    echo -e "\n${BLUE}🔍 Checking Git status...${NC}"
    
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo -e "${RED}❌ Not in a Git repository${NC}"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}⚠️  You have uncommitted changes${NC}"
        echo -e "${YELLOW}Do you want to commit them first? (y/N)${NC}"
        read -r COMMIT_CHANGES
        
        if [ "$COMMIT_CHANGES" = "y" ] || [ "$COMMIT_CHANGES" = "Y" ]; then
            echo "Enter commit message:"
            read -r COMMIT_MSG
            git add .
            git commit -m "$COMMIT_MSG"
            echo -e "${GREEN}✅ Changes committed${NC}"
        else
            echo -e "${YELLOW}⚠️  Proceeding with uncommitted changes${NC}"
        fi
    fi
    
    CURRENT_BRANCH=$(git branch --show-current)
    echo -e "${GREEN}✅ Current branch: $CURRENT_BRANCH${NC}"
}

# Create backup of current state
create_backup() {
    echo -e "\n${BLUE}💾 Creating backup branch...${NC}"
    
    git branch "$BACKUP_BRANCH"
    echo -e "${GREEN}✅ Backup created: $BACKUP_BRANCH${NC}"
}

# Prepare deployment files
prepare_deployment_files() {
    echo -e "\n${BLUE}📦 Preparing deployment package...${NC}"
    
    # List of essential deployment files
    DEPLOYMENT_FILES=(
        # Docker Infrastructure
        "docker-compose.yml"
        "docker-compose.prod.yml"
        "docker-compose.dev.yml"
        "Dockerfile.ml-core"
        "Dockerfile.production-controller"
        "Dockerfile.analytics-engine"
        "Dockerfile.meta-automation"
        "Makefile.docker"
        
        # Hetzner Deployment Scripts
        "deploy/hetzner/setup-vps.sh"
        "deploy/hetzner/install-docker.sh"
        "deploy/hetzner/deploy-services.sh"
        "deploy/hetzner/ssl-setup.sh"
        "deploy/hetzner/monitoring-setup.sh"
        
        # Operations Scripts
        "operations.sh"
        "scripts/health-check.sh"
        "scripts/service-manager.sh"
        "scripts/dev-setup.sh"
        
        # Configuration Templates
        ".env.production.template"
        "config/nginx/nginx.conf"
        "config/nginx/sites-available/neural-forge.conf"
        "config/prometheus/prometheus.yml"
        "config/grafana/dashboards/"
        
        # Documentation
        "docs/DEPLOYMENT_HETZNER_AIM_BY_AIM.md"
        "docs/QUICK_START_EXPRESS.md"
        "README.md"
        "PROMPT_RECTOR_REFINADO.md"
        
        # Core Application
        "ml_core/"
        "device_farm/"
        "gologin_automation/"
        "orchestration/"
        "monitoring/"
        "database/"
        "meta_automation/"
        
        # Requirements
        "requirements.txt"
        "requirements-ml.txt"
        "requirements-dev.txt"
        "pyproject.toml"
    )
    
    # Check which files exist
    echo "Checking deployment files..."
    MISSING_FILES=()
    EXISTING_FILES=()
    
    for file in "${DEPLOYMENT_FILES[@]}"; do
        if [ -e "$file" ]; then
            EXISTING_FILES+=("$file")
            echo -e "  ${GREEN}✅ $file${NC}"
        else
            MISSING_FILES+=("$file")
            echo -e "  ${YELLOW}⚠️  $file (missing)${NC}"
        fi
    done
    
    echo ""
    echo "Summary:"
    echo -e "  ${GREEN}Existing files: ${#EXISTING_FILES[@]}${NC}"
    echo -e "  ${YELLOW}Missing files: ${#MISSING_FILES[@]}${NC}"
    
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        echo -e "\n${YELLOW}⚠️  Some files are missing but deployment can proceed${NC}"
    fi
}

# Create deployment branch
create_deployment_branch() {
    echo -e "\n${BLUE}🌿 Creating deployment branch...${NC}"
    
    # Check if branch already exists
    if git branch --list | grep -q "$DEPLOYMENT_BRANCH"; then
        echo -e "${YELLOW}⚠️  Branch $DEPLOYMENT_BRANCH already exists${NC}"
        echo -e "${YELLOW}Do you want to delete and recreate it? (y/N)${NC}"
        read -r RECREATE_BRANCH
        
        if [ "$RECREATE_BRANCH" = "y" ] || [ "$RECREATE_BRANCH" = "Y" ]; then
            git branch -D "$DEPLOYMENT_BRANCH"
            echo -e "${GREEN}✅ Old branch deleted${NC}"
        else
            echo -e "${RED}❌ Deployment cancelled${NC}"
            exit 1
        fi
    fi
    
    # Create and switch to deployment branch
    git checkout -b "$DEPLOYMENT_BRANCH"
    echo -e "${GREEN}✅ Created and switched to branch: $DEPLOYMENT_BRANCH${NC}"
}

# Optimize deployment branch
optimize_deployment_branch() {
    echo -e "\n${BLUE}⚡ Optimizing deployment branch...${NC}"
    
    # Create deployment-specific .gitignore
    cat > .gitignore.deployment << 'EOF'
# Development files (excluded from deployment)
*.pyc
__pycache__/
.pytest_cache/
.coverage
htmlcov/
.env.local
.env.dev

# IDE files
.vscode/settings.json
.idea/

# OS files
.DS_Store
Thumbs.db

# Logs (except structure)
logs/*.log
logs/*.json
!logs/.gitkeep

# Test files
tests/fixtures/temp/
tests/temp/

# Development databases
*.db
*.sqlite3

# Node modules (if any)
node_modules/

# Build artifacts
build/
dist/
*.egg-info/

# Backup files
*.bak
*.backup
EOF
    
    # Create deployment README
    cat > README_DEPLOYMENT.md << 'EOF'
# 🚀 Neural Forge - Production Deployment Package

## Quick Start

### 1. Clone this deployment branch:
```bash
git clone -b deployment/hetzner-production https://github.com/tu-usuario/neural-forge.git
cd neural-forge
```

### 2. Configure environment:
```bash
cp .env.production.template .env.production
nano .env.production  # Edit with your values
```

### 3. Deploy to Hetzner VPS:
```bash
# One-command deployment
make deploy-production

# Or step by step
./deploy/hetzner/setup-vps.sh
./deploy/hetzner/install-docker.sh
./deploy/hetzner/deploy-services.sh
./deploy/hetzner/ssl-setup.sh
./deploy/hetzner/monitoring-setup.sh
```

## Documentation

- 📖 **Complete Guide:** [docs/DEPLOYMENT_HETZNER_AIM_BY_AIM.md](docs/DEPLOYMENT_HETZNER_AIM_BY_AIM.md)
- ⚡ **Quick Start:** [docs/QUICK_START_EXPRESS.md](docs/QUICK_START_EXPRESS.md)
- 🔧 **Operations:** Use `./operations.sh help`

## Support

- 🆘 **Troubleshooting:** Check logs with `./operations.sh logs`
- 📊 **Monitoring:** Access Grafana at `https://your-domain.com/grafana`
- 🔍 **Health Check:** Run `./operations.sh health`

## Structure

This deployment package includes:
- 🐳 **Docker infrastructure** (9 services)
- 🏗️ **Hetzner deployment scripts** (5 automated scripts)
- 🔒 **SSL configuration** (Let's Encrypt automation)
- 📊 **Monitoring stack** (Prometheus + Grafana)
- 🔧 **Operations tools** (Management and health check scripts)

Version: Neural Forge v3.0 Production Ready
EOF
    
    # Set executable permissions for scripts
    find deploy/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    chmod +x operations.sh 2>/dev/null || true
    
    echo -e "${GREEN}✅ Deployment branch optimized${NC}"
}

# Create deployment package info
create_package_info() {
    echo -e "\n${BLUE}📋 Creating package information...${NC}"
    
    # Get current git info
    GIT_COMMIT=$(git rev-parse HEAD)
    GIT_BRANCH_SOURCE=$(git name-rev --name-only HEAD 2>/dev/null || echo "unknown")
    BUILD_DATE=$(date -Iseconds)
    
    # Create deployment info file
    cat > DEPLOYMENT_INFO.json << EOF
{
  "package_name": "Neural Forge Discográfica",
  "version": "3.0.0",
  "deployment_type": "production",
  "target_platform": "hetzner_vps",
  "build_info": {
    "build_date": "$BUILD_DATE",
    "git_commit": "$GIT_COMMIT",
    "source_branch": "$GIT_BRANCH_SOURCE",
    "deployment_branch": "$DEPLOYMENT_BRANCH"
  },
  "included_services": [
    "production-controller",
    "analytics-engine", 
    "ml-core",
    "n8n-workflows",
    "postgres-database",
    "redis-cache",
    "prometheus-monitoring",
    "grafana-dashboard",
    "nginx-proxy"
  ],
  "deployment_scripts": [
    "setup-vps.sh",
    "install-docker.sh", 
    "deploy-services.sh",
    "ssl-setup.sh",
    "monitoring-setup.sh"
  ],
  "quick_start": {
    "one_command": "make deploy-production",
    "documentation": "docs/QUICK_START_EXPRESS.md",
    "estimated_time": "15 minutes"
  },
  "requirements": {
    "vps_specs": "Hetzner CX33 (2 vCPU, 8GB RAM, 80GB SSD)",
    "monthly_cost": "€5.49",
    "domain_required": true,
    "ssl_auto_generated": true
  }
}
EOF
    
    echo -e "${GREEN}✅ Package info created${NC}"
}

# Create deployment tag
create_deployment_tag() {
    echo -e "\n${BLUE}🏷️  Creating deployment tag...${NC}"
    
    git add .
    git commit -m "🚀 Neural Forge v3.0 - Complete Deployment Package

Features included:
- Docker infrastructure (9 services)
- Hetzner deployment automation (5 scripts) 
- SSL automation with Let's Encrypt
- Prometheus + Grafana monitoring
- Complete operations toolkit
- Production-ready configuration

Deployment time: ~15 minutes
Target: Hetzner VPS (CX33 - €5.49/month)
SSL: Automatic with domain validation
"
    
    git tag -a "$DEPLOYMENT_TAG" -m "Neural Forge v3.0 - Production Deployment Package

Complete infrastructure for Hetzner VPS deployment:
✅ Docker containerization (9 services)
✅ Automated deployment scripts (5 scripts)
✅ SSL configuration (Let's Encrypt)
✅ Monitoring stack (Prometheus + Grafana)
✅ Operations toolkit (health, logs, management)
✅ Security hardening
✅ Backup automation

Ready for production deployment in 15 minutes.
"
    
    echo -e "${GREEN}✅ Tagged as: $DEPLOYMENT_TAG${NC}"
}

# Generate deployment summary
generate_summary() {
    echo -e "\n${CYAN}📊 Deployment Package Summary${NC}"
    echo "================================="
    
    echo -e "\n${BLUE}🌿 Branch Information:${NC}"
    echo "  • Deployment branch: $DEPLOYMENT_BRANCH"
    echo "  • Backup branch: $BACKUP_BRANCH"
    echo "  • Deployment tag: $DEPLOYMENT_TAG"
    
    echo -e "\n${BLUE}📦 Package Contents:${NC}"
    echo "  • Docker services: 9 containerized services"
    echo "  • Deployment scripts: 5 Hetzner automation scripts"
    echo "  • Operations tools: Health check, service management"
    echo "  • Monitoring: Prometheus + Grafana stack"
    echo "  • Security: SSL automation + firewall"
    echo "  • Documentation: Complete deployment guides"
    
    echo -e "\n${BLUE}🚀 Deployment Options:${NC}"
    echo "  • One-command: make deploy-production"
    echo "  • Manual: Execute scripts step by step"
    echo "  • Development: ./start-dev.sh for local testing"
    
    echo -e "\n${BLUE}💰 Cost Information:${NC}"
    echo "  • VPS: Hetzner CX33 - €5.49/month"
    echo "  • Domain: Required (your own)"
    echo "  • SSL: Free (Let's Encrypt)"
    echo "  • Total monthly: ~€6-10 (including domain)"
    
    echo -e "\n${BLUE}⏱️ Deployment Time:${NC}"
    echo "  • Automated: ~15 minutes"
    echo "  • Manual: ~30 minutes"
    echo "  • SSL setup: ~5 minutes"
    
    echo -e "\n${GREEN}📋 Next Steps:${NC}"
    echo "1. Push deployment branch to remote repository"
    echo "2. Clone deployment branch on target server"
    echo "3. Configure .env.production with real values"
    echo "4. Run deployment command"
    echo "5. Access system at https://your-domain.com"
    
    echo -e "\n${CYAN}Commands to push deployment:${NC}"
    echo "git push origin $DEPLOYMENT_BRANCH"
    echo "git push origin $DEPLOYMENT_TAG"
}

# Main execution
main() {
    echo -e "Starting deployment branch creation..."
    echo -e "Current working directory: $(pwd)"
    echo ""
    
    check_git_status
    create_backup
    prepare_deployment_files
    create_deployment_branch
    optimize_deployment_branch
    create_package_info
    create_deployment_tag
    generate_summary
    
    echo ""
    echo -e "${GREEN}🎉 Deployment branch created successfully!${NC}"
    echo ""
    echo -e "${YELLOW}💡 To push to remote repository:${NC}"
    echo "git push origin $DEPLOYMENT_BRANCH"
    echo "git push origin $DEPLOYMENT_TAG"
    echo ""
    echo -e "${YELLOW}💡 To deploy on server:${NC}"
    echo "git clone -b $DEPLOYMENT_BRANCH https://github.com/tu-usuario/neural-forge.git"
    echo "cd neural-forge && make deploy-production"
    echo ""
}

# Execute main function
main "$@"