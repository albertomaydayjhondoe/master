#!/usr/bin/env pwsh
# Device Farm v5 + TikTok ML v4 Integrated Deployment Script
# Interactive PowerShell deployment for the unified system

param(
    [Parameter(HelpMessage="Deployment mode: dev, staging, or production")]
    [ValidateSet("dev", "staging", "production")]
    [string]$Mode = "dev",
    
    [Parameter(HelpMessage="Skip environment checks")]
    [switch]$SkipChecks,
    
    [Parameter(HelpMessage="Force rebuild of all containers")]
    [switch]$Rebuild,
    
    [Parameter(HelpMessage="Start only specific services (comma-separated)")]
    [string]$Services
)

# Color functions for better output
function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success($Message) { Write-ColorOutput Green "✅ $Message" }
function Write-Warning($Message) { Write-ColorOutput Yellow "⚠️  $Message" }
function Write-Error($Message) { Write-ColorOutput Red "❌ $Message" }
function Write-Info($Message) { Write-ColorOutput Cyan "ℹ️  $Message" }

# Header
Clear-Host
Write-ColorOutput Magenta @"
╔══════════════════════════════════════════════════════════════════╗
║                  DEVICE FARM V5 + TIKTOK ML V4                  ║
║                     INTEGRATED DEPLOYMENT                        ║
║                        Version 1.0.0                            ║
╚══════════════════════════════════════════════════════════════════╝
"@

Write-Info "Starting integrated system deployment in $Mode mode..."

# Configuration
$config = @{
    dev = @{
        compose_file = "docker-compose.integrated.yml"
        env_file = ".env.dev"
        services = @("device-farm-v5", "ml-api", "supabase", "redis", "grafana")
    }
    staging = @{
        compose_file = "docker-compose.integrated.yml"
        env_file = ".env.staging"
        services = @("device-farm-v5", "ml-api", "supabase", "redis", "grafana", "n8n", "analytics-processor")
    }
    production = @{
        compose_file = "docker-compose.integrated.yml"
        env_file = ".env.production"
        services = @("device-farm-v5", "ml-api", "supabase", "redis", "grafana", "n8n", "analytics-processor", "alert-manager", "api-gateway", "prometheus")
    }
}

$currentConfig = $config[$Mode]

# Environment check function
function Test-Environment {
    Write-Info "Checking system requirements..."
    
    $checks = @()
    
    # Docker
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        $dockerVersion = docker --version
        $checks += @{ Name = "Docker"; Status = "✅"; Version = $dockerVersion }
    } else {
        $checks += @{ Name = "Docker"; Status = "❌"; Version = "Not installed" }
        return $false
    }
    
    # Docker Compose
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        $composeVersion = docker-compose --version
        $checks += @{ Name = "Docker Compose"; Status = "✅"; Version = $composeVersion }
    } else {
        $checks += @{ Name = "Docker Compose"; Status = "❌"; Version = "Not installed" }
        return $false
    }
    
    # ADB
    if (Get-Command adb -ErrorAction SilentlyContinue) {
        $adbVersion = adb version
        $checks += @{ Name = "ADB"; Status = "✅"; Version = "Available" }
    } else {
        $checks += @{ Name = "ADB"; Status = "⚠️"; Version = "Not in PATH (optional)" }
    }
    
    # USB devices (Android devices)
    try {
        $adbDevices = adb devices 2>$null | Select-String "device$" | Measure-Object
        $deviceCount = $adbDevices.Count
        $checks += @{ Name = "Android Devices"; Status = if($deviceCount -gt 0) {"✅"} else {"⚠️"}; Version = "$deviceCount connected" }
    } catch {
        $checks += @{ Name = "Android Devices"; Status = "⚠️"; Version = "Cannot check (ADB not available)" }
    }
    
    # Display results
    Write-Info "System Requirements Check:"
    $checks | ForEach-Object {
        Write-Host "  $($_.Status) $($_.Name): $($_.Version)"
    }
    
    $failedChecks = ($checks | Where-Object { $_.Status -eq "❌" }).Count
    if ($failedChecks -gt 0) {
        Write-Error "System requirements not met. Please install missing components."
        return $false
    }
    
    return $true
}

# Environment file setup
function Setup-EnvironmentFile {
    param([string]$EnvFile)
    
    Write-Info "Setting up environment file: $EnvFile"
    
    if (-not (Test-Path $EnvFile)) {
        Write-Warning "Environment file $EnvFile not found. Creating template..."
        
        $envTemplate = @"
# Device Farm v5 + TikTok ML v4 Integration Environment Variables

# ========== DATABASE CONFIGURATION ==========
POSTGRES_PASSWORD=secure_postgres_password_change_me
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# ========== API KEYS ==========
GOLOGIN_API_TOKEN=your_gologin_api_token_here
DEVICE_FARM_API_KEY=device_farm_secure_api_key_change_me
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET=your_jwt_secret_key_here

# ========== NOTIFICATION SERVICES ==========
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# ========== EMAIL CONFIGURATION ==========
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_USER=your_email@gmail.com
EMAIL_SMTP_PASSWORD=your_app_password_here

# ========== N8N CONFIGURATION ==========
N8N_USER=admin
N8N_PASSWORD=secure_n8n_password_change_me

# ========== GRAFANA CONFIGURATION ==========
GRAFANA_PASSWORD=secure_grafana_password_change_me

# ========== MODE CONFIGURATION ==========
DEPLOYMENT_MODE=$Mode
DUMMY_MODE=false
DEBUG=true
"@
        
        $envTemplate | Out-File -FilePath $EnvFile -Encoding UTF8
        
        Write-Warning "Template environment file created at $EnvFile"
        Write-Warning "Please edit the file and add your actual credentials before proceeding."
        
        $response = Read-Host "Do you want to edit the environment file now? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            if (Get-Command code -ErrorAction SilentlyContinue) {
                code $EnvFile
            } elseif (Get-Command notepad -ErrorAction SilentlyContinue) {
                notepad $EnvFile
            } else {
                Write-Info "Please edit $EnvFile manually and run the script again."
                exit 1
            }
            
            Read-Host "Press Enter when you've finished editing the environment file"
        }
    }
    
    # Validate required variables
    $envContent = Get-Content $EnvFile | Where-Object { $_ -match "^[^#].*=" }
    $requiredVars = @("SUPABASE_URL", "SUPABASE_KEY", "GOLOGIN_API_TOKEN", "POSTGRES_PASSWORD")
    
    $missingVars = @()
    foreach ($var in $requiredVars) {
        $found = $envContent | Where-Object { $_ -match "^$var=.+" }
        if (-not $found -or $found -match "your_.*_here") {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Error "Missing or incomplete environment variables: $($missingVars -join ', ')"
        Write-Info "Please edit $EnvFile and provide real values for these variables."
        return $false
    }
    
    Write-Success "Environment file validation passed"
    return $true
}

# Docker network setup
function Setup-DockerNetwork {
    Write-Info "Setting up Docker networks..."
    
    $networkExists = docker network ls --filter name=tiktok-ml-network --format "{{.Name}}" | Select-String "tiktok-ml-network"
    
    if (-not $networkExists) {
        Write-Info "Creating tiktok-ml-network..."
        docker network create tiktok-ml-network
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker network created successfully"
        } else {
            Write-Error "Failed to create Docker network"
            return $false
        }
    } else {
        Write-Success "Docker network already exists"
    }
    
    return $true
}

# Service management
function Start-IntegratedServices {
    param(
        [string]$ComposeFile,
        [string]$EnvFile,
        [string[]]$ServiceList,
        [bool]$RebuildContainers
    )
    
    Write-Info "Starting integrated services..."
    
    # Build arguments
    $composeArgs = @("--env-file", $EnvFile, "-f", $ComposeFile)
    
    if ($RebuildContainers) {
        Write-Info "Rebuilding containers..."
        $buildArgs = $composeArgs + @("build", "--no-cache")
        if ($ServiceList) {
            $buildArgs += $ServiceList
        }
        
        & docker-compose @buildArgs
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Container build failed"
            return $false
        }
    }
    
    # Start services
    $startArgs = $composeArgs + @("up", "-d")
    if ($ServiceList) {
        $startArgs += $ServiceList
    }
    
    Write-Info "Starting services: $($ServiceList -join ', ')"
    & docker-compose @startArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start services"
        return $false
    }
    
    Write-Success "Services started successfully"
    return $true
}

# Health check function
function Test-ServiceHealth {
    param([string[]]$ServiceList)
    
    Write-Info "Checking service health..."
    
    $healthChecks = @{
        "device-farm-v5" = "http://localhost:5000/api/status"
        "ml-api" = "http://localhost:8000/health"
        "grafana" = "http://localhost:3000/api/health"
        "n8n" = "http://localhost:5678/healthz"
    }
    
    Start-Sleep -Seconds 10  # Wait for services to start
    
    foreach ($service in $ServiceList) {
        if ($healthChecks.ContainsKey($service)) {
            $url = $healthChecks[$service]
            Write-Info "Checking $service at $url..."
            
            try {
                $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
                if ($response.StatusCode -eq 200) {
                    Write-Success "$service is healthy"
                } else {
                    Write-Warning "$service responded with status $($response.StatusCode)"
                }
            } catch {
                Write-Warning "$service health check failed: $($_.Exception.Message)"
            }
        } else {
            Write-Info "$service (no health check URL defined)"
        }
    }
}

# Main deployment flow
try {
    # Step 1: Environment checks
    if (-not $SkipChecks) {
        if (-not (Test-Environment)) {
            Write-Error "Environment checks failed. Use -SkipChecks to bypass."
            exit 1
        }
    }
    
    # Step 2: Environment file setup
    if (-not (Setup-EnvironmentFile $currentConfig.env_file)) {
        Write-Error "Environment file setup failed."
        exit 1
    }
    
    # Step 3: Docker network setup
    if (-not (Setup-DockerNetwork)) {
        Write-Error "Docker network setup failed."
        exit 1
    }
    
    # Step 4: Determine services to start
    $servicesToStart = if ($Services) {
        $Services.Split(',') | ForEach-Object { $_.Trim() }
    } else {
        $currentConfig.services
    }
    
    Write-Info "Services to deploy: $($servicesToStart -join ', ')"
    
    # Step 5: Start services
    if (-not (Start-IntegratedServices $currentConfig.compose_file $currentConfig.env_file $servicesToStart $Rebuild)) {
        Write-Error "Service deployment failed."
        exit 1
    }
    
    # Step 6: Health checks
    Test-ServiceHealth $servicesToStart
    
    # Step 7: Display service URLs
    Write-Success "Deployment completed successfully!"
    Write-Info ""
    Write-Info "🌐 Service URLs:"
    Write-Info "   • Device Farm v5 Dashboard: http://localhost:5000"
    Write-Info "   • ML API Documentation: http://localhost:8000/docs"
    Write-Info "   • Grafana Monitoring: http://localhost:3000"
    Write-Info "   • n8n Workflows: http://localhost:5678"
    Write-Info "   • Prometheus Metrics: http://localhost:9090"
    Write-Info ""
    Write-Info "📋 Management Commands:"
    Write-Info "   • View logs: docker-compose -f $($currentConfig.compose_file) logs -f [service-name]"
    Write-Info "   • Stop services: docker-compose -f $($currentConfig.compose_file) down"
    Write-Info "   • Restart service: docker-compose -f $($currentConfig.compose_file) restart [service-name]"
    Write-Info ""
    Write-Info "📱 Device Farm Commands:"
    Write-Info "   • Scan devices: curl http://localhost:5000/api/devices/scan -X POST"
    Write-Info "   • Sync profiles: curl http://localhost:5000/api/profiles/sync -X POST"
    Write-Info "   • Get status: curl http://localhost:5000/api/status"
    
    # Optional: Open browser
    $openBrowser = Read-Host "Do you want to open the Device Farm v5 Dashboard in your browser? (y/n)"
    if ($openBrowser -eq 'y' -or $openBrowser -eq 'Y') {
        Start-Process "http://localhost:5000"
    }
    
} catch {
    Write-Error "Deployment failed with error: $($_.Exception.Message)"
    exit 1
}

Write-Success "Integrated deployment script completed!"