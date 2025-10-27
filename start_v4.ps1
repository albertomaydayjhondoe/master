# TikTok ML System v4 - Windows PowerShell Deployment Script
# Automated setup and deployment for Windows users

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "deploy", "stop", "restart", "logs", "status", "build", "help")]
    [string]$Command = "start"
)

# Colors for output
$Red = [ConsoleColor]::Red
$Green = [ConsoleColor]::Green  
$Yellow = [ConsoleColor]::Yellow
$Blue = [ConsoleColor]::Blue
$White = [ConsoleColor]::White

function Write-ColorOutput($Message, $Color = $White) {
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info($Message) {
    Write-ColorOutput "[INFO] $Message" $Blue
}

function Write-Success($Message) {
    Write-ColorOutput "[SUCCESS] $Message" $Green
}

function Write-Warning($Message) {
    Write-ColorOutput "[WARNING] $Message" $Yellow
}

function Write-Error($Message) {
    Write-ColorOutput "[ERROR] $Message" $Red
}

# Logo
Write-ColorOutput @"
╔══════════════════════════════════════════════════════════════╗
║                    TikTok ML System v4                       ║
║              Production Deployment Script                    ║
║                                                              ║
║  🧠 n8n + 🤖 Ultralytics + 📊 Meta Ads + 📈 Supabase      ║
╚══════════════════════════════════════════════════════════════╝
"@ $Blue

# Check dependencies
function Test-Dependencies {
    Write-Info "Checking dependencies..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version 2>$null
        if (-not $dockerVersion) {
            throw "Docker not found"
        }
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version 2>$null
        if (-not $composeVersion) {
            throw "Docker Compose not found"
        }
    }
    catch {
        Write-Error "Docker Compose is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    Write-Success "All dependencies found"
}

# Setup environment
function Initialize-Environment {
    Write-Info "Setting up environment..."
    
    # Create .env from example if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Info "Creating .env from .env.example..."
        Copy-Item ".env.example" ".env"
        Write-Warning "Please edit .env file with your actual credentials before continuing"
        
        # Open .env file for editing
        try {
            notepad.exe ".env"
        }
        catch {
            Write-Warning "Could not open notepad. Please edit .env file manually."
        }
        
        Write-Host ""
        $response = Read-Host "Have you configured the .env file with your credentials? (y/N)"
        if ($response -notmatch '^[Yy]$') {
            Write-Error "Please configure the .env file and run this script again"
            exit 1
        }
    }
    else {
        Write-Success ".env file already exists"
    }
    
    # Create necessary directories
    Write-Info "Creating directories..."
    $directories = @("data\models", "logs", "uploads")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Environment setup complete"
}

# Validate configuration
function Test-Configuration {
    Write-Info "Validating configuration..."
    
    if (-not (Test-Path ".env")) {
        Write-Error ".env file not found"
        exit 1
    }
    
    # Read .env file and check required variables
    $envContent = Get-Content ".env" | Where-Object { $_ -match "^[^#].*=" }
    $envVars = @{}
    
    foreach ($line in $envContent) {
        if ($line -match "^([^=]+)=(.*)$") {
            $envVars[$matches[1]] = $matches[2]
        }
    }
    
    $requiredVars = @("API_SECRET_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY")
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if (-not $envVars.ContainsKey($var) -or [string]::IsNullOrEmpty($envVars[$var])) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Error "Missing required environment variables:"
        foreach ($var in $missingVars) {
            Write-Host "  - $var" -ForegroundColor Red
        }
        exit 1
    }
    
    Write-Success "Configuration validation passed"
}

# Build Docker image
function Build-DockerImage {
    Write-Info "Building Docker image..."
    
    $buildResult = docker build -f Dockerfile.v4 -t tiktok-ml-v4:latest .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    }
    else {
        Write-Error "Failed to build Docker image"
        exit 1
    }
}

# Deploy with Docker Compose
function Start-DockerServices {
    Write-Info "Deploying with Docker Compose..."
    
    # Stop any existing services
    docker-compose -f docker-compose.v4.yml down | Out-Null
    
    # Start services
    docker-compose -f docker-compose.v4.yml up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services deployed successfully"
    }
    else {
        Write-Error "Failed to deploy services"
        exit 1
    }
}

# Wait for services to be healthy
function Wait-ForServices {
    Write-Info "Waiting for services to be healthy..."
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "API is healthy"
                return
            }
        }
        catch {
            # Continue waiting
        }
        
        Write-Info "Attempt $attempt/$maxAttempts`: Waiting for API to be ready..."
        Start-Sleep -Seconds 10
        $attempt++
    }
    
    Write-Error "API failed to become healthy"
    exit 1
}

# Test API endpoints
function Test-ApiEndpoints {
    Write-Info "Testing API endpoints..."
    
    # Test health endpoint
    try {
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction Stop
        if ($healthResponse.StatusCode -eq 200) {
            Write-Success "Health endpoint working"
        }
    }
    catch {
        Write-Error "Health endpoint failed"
    }
    
    # Test API documentation
    try {
        $docsResponse = Invoke-WebRequest -Uri "http://localhost:8000/docs" -ErrorAction Stop
        if ($docsResponse.StatusCode -eq 200) {
            Write-Success "API documentation available at http://localhost:8000/docs"
        }
    }
    catch {
        Write-Warning "API documentation not accessible"
    }
}

# Display deployment info
function Show-DeploymentInfo {
    Write-Host ""
    Write-ColorOutput "╔══════════════════════════════════════════════════════════════╗" $Green
    Write-ColorOutput "║                   DEPLOYMENT SUCCESSFUL!                     ║" $Green
    Write-ColorOutput "╚══════════════════════════════════════════════════════════════╝" $Green
    Write-Host ""
    Write-ColorOutput "🌐 Service URLs:" $Blue
    Write-Host "  • Main API:        http://localhost:8000"
    Write-Host "  • API Docs:        http://localhost:8000/docs"
    Write-Host "  • Health Check:    http://localhost:8000/health"
    Write-Host "  • n8n Workflows:   http://localhost:5678"
    Write-Host ""
    Write-ColorOutput "📊 Management Commands:" $Blue
    Write-Host "  • View logs:       docker-compose -f docker-compose.v4.yml logs -f"
    Write-Host "  • Stop services:   docker-compose -f docker-compose.v4.yml down"
    Write-Host "  • Restart:         docker-compose -f docker-compose.v4.yml restart"
    Write-Host "  • Check status:    docker-compose -f docker-compose.v4.yml ps"
    Write-Host ""
    Write-ColorOutput "🔧 Configuration:" $Blue
    Write-Host "  • Edit config:     notepad .env"
    Write-Host "  • Reload:          docker-compose -f docker-compose.v4.yml up -d"
    Write-Host ""
    Write-ColorOutput "📋 Next Steps:" $Yellow
    Write-Host "  1. Configure n8n workflows at http://localhost:5678"
    Write-Host "  2. Test API endpoints at http://localhost:8000/docs"
    Write-Host "  3. Monitor logs for any issues"
    Write-Host "  4. Configure SSL/TLS for production use"
    Write-Host ""
}

# Main deployment function
function Start-Deployment {
    Write-Info "Starting TikTok ML System v4 deployment..."
    
    Test-Dependencies
    Initialize-Environment
    Test-Configuration
    Build-DockerImage
    Start-DockerServices
    Wait-ForServices
    Test-ApiEndpoints
    Show-DeploymentInfo
    
    Write-Success "Deployment completed successfully! 🚀"
}

# Handle commands
switch ($Command) {
    "start" {
        Start-Deployment
    }
    "deploy" {
        Start-Deployment
    }
    "stop" {
        Write-Info "Stopping services..."
        docker-compose -f docker-compose.v4.yml down
        Write-Success "Services stopped"
    }
    "restart" {
        Write-Info "Restarting services..."
        docker-compose -f docker-compose.v4.yml down
        docker-compose -f docker-compose.v4.yml up -d
        Write-Success "Services restarted"
    }
    "logs" {
        docker-compose -f docker-compose.v4.yml logs -f
    }
    "status" {
        docker-compose -f docker-compose.v4.yml ps
    }
    "build" {
        Build-DockerImage
    }
    "help" {
        Write-Host "TikTok ML System v4 - Deployment Script"
        Write-Host ""
        Write-Host "Usage: .\start_v4.ps1 [command]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  start, deploy    Full deployment (default)"
        Write-Host "  stop            Stop all services"
        Write-Host "  restart         Restart all services"
        Write-Host "  logs            Show live logs"
        Write-Host "  status          Show services status"
        Write-Host "  build           Build Docker image only"
        Write-Host "  help            Show this help"
        Write-Host ""
    }
}