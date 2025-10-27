# TikTok ML System v4 - Quick Launch Script
# Simplified deployment for rapid testing and development

param(
    [string]$Mode = "local",
    [switch]$Production = $false,
    [switch]$SkipBuild = $false,
    [string]$Port = "8000"
)

# Quick configuration
$config = @{
    Mode = $Mode
    Production = $Production.IsPresent
    Port = $Port
    SkipBuild = $SkipBuild.IsPresent
}

Write-Host "🚀 TikTok ML System v4 - Quick Launch" -ForegroundColor Cyan
Write-Host "Mode: $($config.Mode) | Production: $($config.Production) | Port: $($config.Port)" -ForegroundColor Yellow

# Create minimal .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating minimal .env file..." -ForegroundColor Blue
    
    $envContent = @"
# Quick Launch Configuration
PRODUCTION_MODE=$($config.Production.ToString().ToLower())
DEBUG=$((not $config.Production).ToString().ToLower())
API_HOST=0.0.0.0
API_PORT=$($config.Port)
API_SECRET_KEY=quick-launch-secret-key-for-development
JWT_SECRET=quick-launch-jwt-secret-for-development
SUPABASE_URL=https://dummy-project.supabase.co
SUPABASE_ANON_KEY=dummy-anon-key
SUPABASE_SERVICE_KEY=dummy-service-key
ULTRALYTICS_MODEL=yolov8n.pt
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env file created" -ForegroundColor Green
}

# Quick Docker build and run
try {
    if (-not $config.SkipBuild) {
        Write-Host "🔨 Building Docker image..." -ForegroundColor Blue
        docker build -f Dockerfile.v4 -t tiktok-ml-v4:quick .
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker build failed"
        }
        Write-Host "✅ Docker image built" -ForegroundColor Green
    }
    
    # Stop existing container
    Write-Host "🛑 Stopping existing container..." -ForegroundColor Blue
    docker stop tiktok-ml-v4-quick 2>$null
    docker rm tiktok-ml-v4-quick 2>$null
    
    # Run new container
    Write-Host "🏃 Starting container..." -ForegroundColor Blue
    docker run -d `
        --name tiktok-ml-v4-quick `
        -p "$($config.Port):8000" `
        --env-file .env `
        tiktok-ml-v4:quick
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Container started successfully" -ForegroundColor Green
        
        # Wait for health check
        Write-Host "🩺 Waiting for system to be ready..." -ForegroundColor Blue
        $attempts = 0
        $maxAttempts = 30
        
        do {
            Start-Sleep -Seconds 2
            $attempts++
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$($config.Port)/health" -TimeoutSec 5 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Host "🎉 System is ready!" -ForegroundColor Green
                    break
                }
            } catch {
                Write-Host "." -NoNewline -ForegroundColor Yellow
            }
        } while ($attempts -lt $maxAttempts)
        
        if ($attempts -eq $maxAttempts) {
            Write-Host "`n⚠️  System might not be fully ready, but container is running" -ForegroundColor Yellow
        }
        
        # Show quick access info
        Write-Host "`n🌐 Quick Access:" -ForegroundColor Cyan
        Write-Host "  • Main API: http://localhost:$($config.Port)/" -ForegroundColor White
        Write-Host "  • API Docs: http://localhost:$($config.Port)/docs" -ForegroundColor White
        Write-Host "  • Health: http://localhost:$($config.Port)/health" -ForegroundColor White
        
        Write-Host "`n🛠️  Quick Commands:" -ForegroundColor Cyan
        Write-Host "  • View logs: docker logs tiktok-ml-v4-quick -f" -ForegroundColor White
        Write-Host "  • Stop: docker stop tiktok-ml-v4-quick" -ForegroundColor White
        Write-Host "  • Restart: docker restart tiktok-ml-v4-quick" -ForegroundColor White
        
    } else {
        throw "Failed to start container"
    }
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "💡 Try running with -SkipBuild if image already exists" -ForegroundColor Yellow
}

Write-Host "`n🚀 Quick launch completed!" -ForegroundColor Green