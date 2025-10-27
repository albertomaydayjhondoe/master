# TikTok ML System v4 - Interactive Production Deployment Script
# Complete deployment with user input and validation

param(
    [string]$Mode = "interactive"
)

# Colors for enhanced user experience
$Colors = @{
    Header = [ConsoleColor]::Cyan
    Success = [ConsoleColor]::Green
    Warning = [ConsoleColor]::Yellow
    Error = [ConsoleColor]::Red
    Info = [ConsoleColor]::Blue
    Prompt = [ConsoleColor]::Magenta
    Input = [ConsoleColor]::White
}

function Write-ColorText($Text, $Color = $Colors.Info) {
    Write-Host $Text -ForegroundColor $Color
}

function Write-Header($Text) {
    Write-Host ""
    Write-ColorText "╔══════════════════════════════════════════════════════════════════════╗" $Colors.Header
    Write-ColorText "║ $(($Text -replace '.', ' ') -replace '^(.{68}).*', '$1').PadRight(68) ║" $Colors.Header
    Write-ColorText "╚══════════════════════════════════════════════════════════════════════╝" $Colors.Header
    Write-Host ""
}

function Read-UserInput($Prompt, $Default = "", $Required = $false, $Secret = $false) {
    do {
        if ($Default) {
            Write-ColorText "$Prompt [$Default]: " $Colors.Prompt -NoNewline
        } else {
            Write-ColorText "$Prompt" $Colors.Prompt -NoNewline
            if ($Required) {
                Write-ColorText " (REQUERIDO): " $Colors.Warning -NoNewline
            } else {
                Write-ColorText ": " $Colors.Prompt -NoNewline
            }
        }
        
        if ($Secret) {
            $input = Read-Host -AsSecureString
            $input = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($input))
        } else {
            $input = Read-Host
        }
        
        if ([string]::IsNullOrWhiteSpace($input)) {
            $input = $Default
        }
        
        if ($Required -and [string]::IsNullOrWhiteSpace($input)) {
            Write-ColorText "⚠️  Este campo es requerido. Por favor ingresa un valor." $Colors.Warning
        }
    } while ($Required -and [string]::IsNullOrWhiteSpace($input))
    
    return $input
}

function Test-Prerequisites {
    Write-Header "VERIFICACIÓN DE PREREQUISITOS"
    
    $checks = @()
    
    # Check Docker
    Write-ColorText "🔍 Verificando Docker..." $Colors.Info
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-ColorText "✅ Docker encontrado: $dockerVersion" $Colors.Success
            $checks += @{Name = "Docker"; Status = $true}
        } else {
            throw "Docker no encontrado"
        }
    } catch {
        Write-ColorText "❌ Docker no está instalado o no está en PATH" $Colors.Error
        $checks += @{Name = "Docker"; Status = $false}
    }
    
    # Check Docker Compose
    Write-ColorText "🔍 Verificando Docker Compose..." $Colors.Info
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($composeVersion) {
            Write-ColorText "✅ Docker Compose encontrado: $composeVersion" $Colors.Success
            $checks += @{Name = "Docker Compose"; Status = $true}
        } else {
            throw "Docker Compose no encontrado"
        }
    } catch {
        Write-ColorText "❌ Docker Compose no está instalado" $Colors.Error
        $checks += @{Name = "Docker Compose"; Status = $false}
    }
    
    # Check Git
    Write-ColorText "🔍 Verificando Git..." $Colors.Info
    try {
        $gitVersion = git --version 2>$null
        if ($gitVersion) {
            Write-ColorText "✅ Git encontrado: $gitVersion" $Colors.Success
            $checks += @{Name = "Git"; Status = $true}
        } else {
            throw "Git no encontrado"
        }
    } catch {
        Write-ColorText "⚠️  Git no encontrado (opcional para deployment)" $Colors.Warning
        $checks += @{Name = "Git"; Status = $false}
    }
    
    # Check required files
    $requiredFiles = @(
        "Dockerfile.v4",
        "docker-compose.v4.yml", 
        "requirements.txt",
        "ml_core\api\main_v4.py",
        ".env.example"
    )
    
    Write-ColorText "🔍 Verificando archivos requeridos..." $Colors.Info
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-ColorText "✅ $file" $Colors.Success
        } else {
            Write-ColorText "❌ $file - ARCHIVO FALTANTE" $Colors.Error
            $checks += @{Name = $file; Status = $false}
        }
    }
    
    $failedChecks = $checks | Where-Object { -not $_.Status }
    if ($failedChecks.Count -gt 0) {
        Write-ColorText "❌ Prerequisitos faltantes. Por favor instala los componentes faltantes." $Colors.Error
        return $false
    }
    
    Write-ColorText "🎉 Todos los prerequisitos verificados correctamente!" $Colors.Success
    return $true
}

function Get-DeploymentConfiguration {
    Write-Header "CONFIGURACIÓN DE DEPLOYMENT"
    
    $config = @{}
    
    # Deployment type
    Write-ColorText "📋 Selecciona el tipo de deployment:" $Colors.Info
    Write-ColorText "1. 🐳 Docker Local (Desarrollo/Testing)" $Colors.Input
    Write-ColorText "2. 🚀 Railway Cloud (Producción)" $Colors.Input
    Write-ColorText "3. ☁️  Docker Compose Completo (Producción Local)" $Colors.Input
    
    $deployType = Read-UserInput "Tipo de deployment [1-3]" "1" $true
    
    switch ($deployType) {
        "1" { $config.DeployType = "docker-local" }
        "2" { $config.DeployType = "railway" }
        "3" { $config.DeployType = "docker-compose" }
        default { $config.DeployType = "docker-local" }
    }
    
    # Production mode
    $prodMode = Read-UserInput "🔧 Modo producción (true/false)" "true"
    $config.ProductionMode = $prodMode.ToLower() -eq "true"
    
    if ($config.ProductionMode) {
        Write-ColorText "⚠️  MODO PRODUCCIÓN activado - Se requieren credenciales reales" $Colors.Warning
    } else {
        Write-ColorText "🧪 MODO DESARROLLO activado - Se usarán valores dummy" $Colors.Info
    }
    
    return $config
}

function Get-ApiCredentials($ProductionMode) {
    Write-Header "CONFIGURACIÓN DE CREDENCIALES API"
    
    $creds = @{}
    
    if ($ProductionMode) {
        Write-ColorText "🔐 Configurando credenciales para PRODUCCIÓN" $Colors.Warning
        Write-ColorText "⚠️  Todas las credenciales son requeridas en modo producción" $Colors.Warning
        Write-Host ""
        
        # Core API
        $creds.API_SECRET_KEY = Read-UserInput "🔑 API Secret Key (min 32 caracteres)" "" $true $true
        $creds.JWT_SECRET = Read-UserInput "🔑 JWT Secret (min 32 caracteres)" "" $true $true
        
        # Supabase
        Write-ColorText "`n📊 SUPABASE CONFIGURATION (Requerido para métricas)" $Colors.Info
        $creds.SUPABASE_URL = Read-UserInput "🔗 Supabase URL" "" $true
        $creds.SUPABASE_ANON_KEY = Read-UserInput "🔑 Supabase Anon Key" "" $true $true
        $creds.SUPABASE_SERVICE_KEY = Read-UserInput "🔑 Supabase Service Key" "" $true $true
        
        # Meta Ads
        Write-ColorText "`n🎯 META ADS CONFIGURATION" $Colors.Info
        $includeMeta = Read-UserInput "¿Configurar Meta Ads? (y/n)" "y"
        if ($includeMeta.ToLower() -eq "y") {
            $creds.META_APP_ID = Read-UserInput "📱 Meta App ID" "" $true
            $creds.META_APP_SECRET = Read-UserInput "🔐 Meta App Secret" "" $true $true
            $creds.META_ACCESS_TOKEN = Read-UserInput "🎫 Meta Access Token (long-lived)" "" $true $true
            $creds.META_PIXEL_ID = Read-UserInput "📊 Meta Pixel ID" "" $false
        }
        
        # YouTube
        Write-ColorText "`n🎥 YOUTUBE CONFIGURATION" $Colors.Info
        $includeYoutube = Read-UserInput "¿Configurar YouTube API? (y/n)" "y"
        if ($includeYoutube.ToLower() -eq "y") {
            $creds.YOUTUBE_API_KEY = Read-UserInput "🔑 YouTube API Key" "" $true $true
            $channelIds = Read-UserInput "📺 Channel IDs (separados por coma)" ""
            $creds.YOUTUBE_CHANNEL_IDS = $channelIds
        }
        
        # Spotify
        Write-ColorText "`n🎵 SPOTIFY CONFIGURATION" $Colors.Info
        $includeSpotify = Read-UserInput "¿Configurar Spotify API? (y/n)" "y"
        if ($includeSpotify.ToLower() -eq "y") {
            $creds.SPOTIFY_CLIENT_ID = Read-UserInput "🎼 Spotify Client ID" "" $true
            $creds.SPOTIFY_CLIENT_SECRET = Read-UserInput "🔐 Spotify Client Secret" "" $true $true
            $artistIds = Read-UserInput "🎤 Artist IDs (separados por coma)" ""
            $creds.SPOTIFY_ARTIST_IDS = $artistIds
            $playlistIds = Read-UserInput "📋 Playlist IDs (separados por coma)" ""
            $creds.SPOTIFY_PLAYLIST_IDS = $playlistIds
        }
        
        # Landing Pages
        Write-ColorText "`n🌐 LANDING PAGE CONFIGURATION" $Colors.Info
        $includeLanding = Read-UserInput "¿Configurar Landing Pages? (y/n)" "y"
        if ($includeLanding.ToLower() -eq "y") {
            $landingUrls = Read-UserInput "🌐 Landing Page URLs (separadas por coma)" ""
            $creds.LANDING_PAGE_URLS = $landingUrls
        }
        
        # n8n
        Write-ColorText "`n🔄 N8N CONFIGURATION" $Colors.Info
        $includeN8n = Read-UserInput "¿Configurar n8n? (y/n)" "y"
        if ($includeN8n.ToLower() -eq "y") {
            $creds.N8N_WEBHOOK_BASE_URL = Read-UserInput "🔗 n8n Webhook Base URL" ""
            $creds.N8N_API_KEY = Read-UserInput "🔑 n8n API Key" "" $false $true
        }
        
    } else {
        Write-ColorText "🧪 Modo desarrollo - usando valores dummy" $Colors.Info
        $creds = @{
            API_SECRET_KEY = "dummy-secret-key-development-only-32chars"
            JWT_SECRET = "dummy-jwt-secret-development-only-32chars"
            SUPABASE_URL = "https://dummy-project.supabase.co"
            SUPABASE_ANON_KEY = "dummy-anon-key"
            SUPABASE_SERVICE_KEY = "dummy-service-key"
            META_APP_ID = "dummy-meta-app-id"
            META_APP_SECRET = "dummy-meta-secret"
            META_ACCESS_TOKEN = "dummy-access-token"
            YOUTUBE_API_KEY = "dummy-youtube-key"
            SPOTIFY_CLIENT_ID = "dummy-spotify-client"
            SPOTIFY_CLIENT_SECRET = "dummy-spotify-secret"
        }
    }
    
    return $creds
}

function Create-EnvironmentFile($Credentials, $ProductionMode) {
    Write-Header "CREACIÓN ARCHIVO .ENV"
    
    Write-ColorText "📝 Creando archivo .env con configuraciones..." $Colors.Info
    
    $envContent = @"
# TikTok ML System v4 - Auto-Generated Configuration
# Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# Mode: $(if ($ProductionMode) { "PRODUCTION" } else { "DEVELOPMENT" })

# === SYSTEM CONFIGURATION ===
PRODUCTION_MODE=$($ProductionMode.ToString().ToLower())
DEBUG=$((-not $ProductionMode).ToString().ToLower())
LOG_LEVEL=INFO

# === CORE API CONFIGURATION ===
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_SECRET_KEY=$($Credentials.API_SECRET_KEY)
JWT_SECRET=$($Credentials.JWT_SECRET)

# === SUPABASE CONFIGURATION ===
SUPABASE_URL=$($Credentials.SUPABASE_URL)
SUPABASE_ANON_KEY=$($Credentials.SUPABASE_ANON_KEY)
SUPABASE_SERVICE_KEY=$($Credentials.SUPABASE_SERVICE_KEY)

# === META ADS CONFIGURATION ===
META_APP_ID=$($Credentials.META_APP_ID)
META_APP_SECRET=$($Credentials.META_APP_SECRET)
META_ACCESS_TOKEN=$($Credentials.META_ACCESS_TOKEN)
META_PIXEL_ID=$($Credentials.META_PIXEL_ID)

# === YOUTUBE API CONFIGURATION ===
YOUTUBE_API_KEY=$($Credentials.YOUTUBE_API_KEY)
YOUTUBE_CHANNEL_IDS=$($Credentials.YOUTUBE_CHANNEL_IDS)

# === SPOTIFY API CONFIGURATION ===
SPOTIFY_CLIENT_ID=$($Credentials.SPOTIFY_CLIENT_ID)
SPOTIFY_CLIENT_SECRET=$($Credentials.SPOTIFY_CLIENT_SECRET)
SPOTIFY_ARTIST_IDS=$($Credentials.SPOTIFY_ARTIST_IDS)
SPOTIFY_PLAYLIST_IDS=$($Credentials.SPOTIFY_PLAYLIST_IDS)

# === LANDING PAGE CONFIGURATION ===
LANDING_PAGE_URLS=$($Credentials.LANDING_PAGE_URLS)

# === ML CONFIGURATION ===
ULTRALYTICS_MODEL=yolov8n.pt
ML_MODEL_PATH=/app/data/models
MAX_UPLOAD_SIZE=52428800

# === N8N CONFIGURATION ===
N8N_WEBHOOK_BASE_URL=$($Credentials.N8N_WEBHOOK_BASE_URL)
N8N_API_KEY=$($Credentials.N8N_API_KEY)

# === DEPLOYMENT CONFIGURATION ===
PORT=8000
HEALTHCHECK_INTERVAL=30s
"@
    
    # Backup existing .env if it exists
    if (Test-Path ".env") {
        $backup = ".env.backup.$(Get-Date -Format "yyyyMMdd-HHmmss")"
        Copy-Item ".env" $backup
        Write-ColorText "💾 Backup de .env existente guardado como: $backup" $Colors.Warning
    }
    
    # Write new .env file
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-ColorText "✅ Archivo .env creado exitosamente" $Colors.Success
    
    # Set permissions (Windows)
    try {
        icacls ".env" /inheritance:r /grant:r "$env:USERNAME:(R,W)" /T 2>$null
        Write-ColorText "🔒 Permisos de .env configurados para seguridad" $Colors.Info
    } catch {
        Write-ColorText "⚠️  No se pudieron configurar permisos especiales para .env" $Colors.Warning
    }
}

function Start-DockerBuild($DeployType) {
    Write-Header "CONSTRUCCIÓN DE IMAGEN DOCKER"
    
    Write-ColorText "🔨 Construyendo imagen Docker v4..." $Colors.Info
    
    $buildArgs = @()
    if ($DeployType -eq "railway") {
        $buildArgs += "--platform", "linux/amd64"
    }
    
    $buildCommand = @("docker", "build") + $buildArgs + @("-f", "Dockerfile.v4", "-t", "tiktok-ml-v4:latest", ".")
    
    Write-ColorText "Ejecutando: $($buildCommand -join ' ')" $Colors.Info
    
    try {
        & $buildCommand[0] $buildCommand[1..($buildCommand.Length-1)]
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Imagen Docker construida exitosamente" $Colors.Success
            return $true
        } else {
            throw "Build failed with exit code $LASTEXITCODE"
        }
    } catch {
        Write-ColorText "❌ Error construyendo imagen Docker: $_" $Colors.Error
        return $false
    }
}

function Start-Deployment($DeployType) {
    Write-Header "INICIO DE DEPLOYMENT"
    
    switch ($DeployType) {
        "docker-local" {
            Write-ColorText "🐳 Iniciando deployment Docker local..." $Colors.Info
            
            # Stop existing container
            docker stop tiktok-ml-v4 2>$null
            docker rm tiktok-ml-v4 2>$null
            
            # Run new container
            $runCommand = @(
                "docker", "run", "-d",
                "--name", "tiktok-ml-v4",
                "-p", "8000:8000",
                "--env-file", ".env",
                "-v", "${PWD}/data:/app/data",
                "-v", "${PWD}/logs:/app/logs",
                "tiktok-ml-v4:latest"
            )
            
            Write-ColorText "Ejecutando: $($runCommand -join ' ')" $Colors.Info
            & $runCommand[0] $runCommand[1..($runCommand.Length-1)]
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✅ Container Docker iniciado exitosamente" $Colors.Success
                return $true
            } else {
                Write-ColorText "❌ Error iniciando container Docker" $Colors.Error
                return $false
            }
        }
        
        "docker-compose" {
            Write-ColorText "🐳 Iniciando deployment Docker Compose completo..." $Colors.Info
            
            docker-compose -f docker-compose.v4.yml down 2>$null
            docker-compose -f docker-compose.v4.yml up -d
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✅ Stack Docker Compose iniciado exitosamente" $Colors.Success
                return $true
            } else {
                Write-ColorText "❌ Error iniciando stack Docker Compose" $Colors.Error
                return $false
            }
        }
        
        "railway" {
            Write-ColorText "🚀 Preparando deployment Railway..." $Colors.Info
            
            # Check Railway CLI
            try {
                $railwayVersion = railway version 2>$null
                Write-ColorText "✅ Railway CLI encontrado: $railwayVersion" $Colors.Success
            } catch {
                Write-ColorText "❌ Railway CLI no encontrado. Instalando..." $Colors.Warning
                try {
                    npm install -g @railway/cli
                    Write-ColorText "✅ Railway CLI instalado" $Colors.Success
                } catch {
                    Write-ColorText "❌ Error instalando Railway CLI. Por favor instala manualmente." $Colors.Error
                    return $false
                }
            }
            
            # Railway login check
            try {
                railway whoami 2>$null
            } catch {
                Write-ColorText "🔑 Por favor inicia sesión en Railway..." $Colors.Info
                railway login
            }
            
            # Deploy to Railway
            Write-ColorText "🚀 Desplegando a Railway..." $Colors.Info
            railway up --detach
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorText "✅ Deployment a Railway completado exitosamente" $Colors.Success
                return $true
            } else {
                Write-ColorText "❌ Error en deployment Railway" $Colors.Error
                return $false
            }
        }
    }
    
    return $false
}

function Wait-ForHealthCheck($DeployType) {
    Write-Header "VERIFICACIÓN DE SALUD DEL SISTEMA"
    
    $baseUrl = switch ($DeployType) {
        "docker-local" { "http://localhost:8000" }
        "docker-compose" { "http://localhost:8000" }
        "railway" { 
            Write-ColorText "🔗 Obteniendo URL de Railway..." $Colors.Info
            $railwayUrl = railway status --json 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty deployments | Select-Object -First 1 -ExpandProperty url
            if ($railwayUrl) {
                Write-ColorText "🌐 URL Railway: $railwayUrl" $Colors.Info
                $railwayUrl
            } else {
                Write-ColorText "⚠️  No se pudo obtener URL de Railway automáticamente" $Colors.Warning
                Read-UserInput "🌐 Ingresa la URL de Railway manualmente" "https://your-app.railway.app"
            }
        }
    }
    
    Write-ColorText "🩺 Verificando salud del sistema en: $baseUrl" $Colors.Info
    
    $maxAttempts = 20
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            Write-ColorText "🔄 Intento $attempt/$maxAttempts - Verificando health endpoint..." $Colors.Info
            
            $response = Invoke-WebRequest -Uri "$baseUrl/health" -TimeoutSec 10 -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                $healthData = $response.Content | ConvertFrom-Json
                Write-ColorText "✅ Sistema saludable! Status: $($healthData.status)" $Colors.Success
                return @{
                    Success = $true
                    Url = $baseUrl
                    HealthData = $healthData
                }
            }
        } catch {
            Write-ColorText "⏳ Esperando que el sistema esté listo..." $Colors.Info
        }
        
        Start-Sleep -Seconds 15
        $attempt++
    }
    
    Write-ColorText "❌ El sistema no respondió después de $maxAttempts intentos" $Colors.Error
    return @{
        Success = $false
        Url = $baseUrl
    }
}

function Test-Endpoints($BaseUrl) {
    Write-Header "PRUEBAS DE ENDPOINTS"
    
    $endpoints = @(
        @{Name = "Health Check"; Path = "/health"; Method = "GET"}
        @{Name = "Root Info"; Path = "/"; Method = "GET"}
        @{Name = "API Docs"; Path = "/docs"; Method = "GET"}
        @{Name = "OpenAPI Schema"; Path = "/openapi.json"; Method = "GET"}
    )
    
    $results = @()
    
    foreach ($endpoint in $endpoints) {
        Write-ColorText "🧪 Probando $($endpoint.Name): $($endpoint.Path)" $Colors.Info
        
        try {
            $response = Invoke-WebRequest -Uri "$BaseUrl$($endpoint.Path)" -Method $endpoint.Method -TimeoutSec 10 -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                Write-ColorText "✅ $($endpoint.Name) - OK ($($response.StatusCode))" $Colors.Success
                $results += @{
                    Name = $endpoint.Name
                    Status = "OK"
                    StatusCode = $response.StatusCode
                }
            } else {
                Write-ColorText "⚠️  $($endpoint.Name) - Unexpected status ($($response.StatusCode))" $Colors.Warning
                $results += @{
                    Name = $endpoint.Name
                    Status = "Warning"
                    StatusCode = $response.StatusCode
                }
            }
        } catch {
            Write-ColorText "❌ $($endpoint.Name) - Failed: $($_.Exception.Message)" $Colors.Error
            $results += @{
                Name = $endpoint.Name
                Status = "Failed"
                Error = $_.Exception.Message
            }
        }
    }
    
    return $results
}

function Show-DeploymentSummary($Config, $HealthResult, $EndpointResults) {
    Write-Header "RESUMEN DE DEPLOYMENT"
    
    Write-ColorText "🎉 DEPLOYMENT COMPLETADO!" $Colors.Success
    Write-Host ""
    
    # Configuration Summary
    Write-ColorText "📋 CONFIGURACIÓN:" $Colors.Info
    Write-ColorText "   • Tipo: $($Config.DeployType)" $Colors.Input
    Write-ColorText "   • Modo: $(if ($Config.ProductionMode) { "PRODUCTION" } else { "DEVELOPMENT" })" $Colors.Input
    Write-ColorText "   • URL Base: $($HealthResult.Url)" $Colors.Input
    Write-Host ""
    
    # Health Status
    Write-ColorText "🩺 ESTADO DEL SISTEMA:" $Colors.Info
    if ($HealthResult.Success) {
        Write-ColorText "   • ✅ Sistema OPERATIVO" $Colors.Success
        if ($HealthResult.HealthData.version) {
            Write-ColorText "   • 🔖 Versión: $($HealthResult.HealthData.version)" $Colors.Input
        }
    } else {
        Write-ColorText "   • ❌ Sistema NO RESPONDE" $Colors.Error
    }
    Write-Host ""
    
    # Endpoint Results
    Write-ColorText "🧪 RESULTADOS DE PRUEBAS:" $Colors.Info
    foreach ($result in $EndpointResults) {
        $icon = switch ($result.Status) {
            "OK" { "✅" }
            "Warning" { "⚠️ " }
            "Failed" { "❌" }
        }
        Write-ColorText "   • $icon $($result.Name): $($result.Status)" $Colors.Input
    }
    Write-Host ""
    
    # Quick Access URLs
    Write-ColorText "🌐 ENLACES RÁPIDOS:" $Colors.Info
    Write-ColorText "   • 🏠 Página Principal: $($HealthResult.Url)/" $Colors.Input
    Write-ColorText "   • 📖 Documentación API: $($HealthResult.Url)/docs" $Colors.Input
    Write-ColorText "   • 🩺 Health Check: $($HealthResult.Url)/health" $Colors.Input
    
    if ($Config.DeployType -eq "docker-compose") {
        Write-ColorText "   • 🔄 n8n Workflows: http://localhost:5678" $Colors.Input
        Write-ColorText "   • 📊 Traefik Dashboard: http://localhost:8080" $Colors.Input
    }
    Write-Host ""
    
    # Management Commands
    Write-ColorText "🛠️  COMANDOS DE GESTIÓN:" $Colors.Info
    switch ($Config.DeployType) {
        "docker-local" {
            Write-ColorText "   • Ver logs: docker logs tiktok-ml-v4 -f" $Colors.Input
            Write-ColorText "   • Parar: docker stop tiktok-ml-v4" $Colors.Input
            Write-ColorText "   • Reiniciar: docker restart tiktok-ml-v4" $Colors.Input
        }
        "docker-compose" {
            Write-ColorText "   • Ver logs: docker-compose -f docker-compose.v4.yml logs -f" $Colors.Input
            Write-ColorText "   • Parar: docker-compose -f docker-compose.v4.yml down" $Colors.Input
            Write-ColorText "   • Reiniciar: docker-compose -f docker-compose.v4.yml restart" $Colors.Input
        }
        "railway" {
            Write-ColorText "   • Ver logs: railway logs" $Colors.Input
            Write-ColorText "   • Estado: railway status" $Colors.Input
            Write-ColorText "   • Redeploy: railway up --detach" $Colors.Input
        }
    }
    Write-Host ""
    
    # Next Steps
    Write-ColorText "📋 PRÓXIMOS PASOS:" $Colors.Info
    Write-ColorText "   1. 🔧 Configurar workflows n8n (si aplica)" $Colors.Input
    Write-ColorText "   2. 🧪 Probar endpoints en /docs" $Colors.Input
    Write-ColorText "   3. 📊 Verificar métricas Supabase" $Colors.Input
    Write-ColorText "   4. 🎯 Configurar campañas Meta Ads" $Colors.Input
    Write-ColorText "   5. 🔒 Configurar SSL para producción" $Colors.Input
    Write-Host ""
    
    Write-ColorText "🚀 ¡TikTok ML System v4 desplegado exitosamente!" $Colors.Success
}

# MAIN EXECUTION
function Main {
    Clear-Host
    
    # Logo and welcome
    Write-ColorText @"
    ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗    ███╗   ███╗██╗         
    ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝    ████╗ ████║██║         
       ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝     ██╔████╔██║██║         
       ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗     ██║╚██╔╝██║██║         
       ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗    ██║ ╚═╝ ██║███████╗    
       ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═╝     ╚═╝╚══════╝    
                                                                              
                        SISTEMA v4 - DEPLOYMENT INTERACTIVO
"@ $Colors.Header
    
    Write-ColorText "🚀 Bienvenido al deployment interactivo del TikTok ML System v4" $Colors.Info
    Write-ColorText "📋 Este script te guiará paso a paso para desplegar el sistema completo" $Colors.Info
    Write-Host ""
    
    try {
        # Step 1: Prerequisites
        if (-not (Test-Prerequisites)) {
            Write-ColorText "❌ No se pueden cumplir los prerequisitos. Deployment cancelado." $Colors.Error
            return
        }
        
        # Step 2: Configuration
        $config = Get-DeploymentConfiguration
        
        # Step 3: Credentials
        $credentials = Get-ApiCredentials $config.ProductionMode
        
        # Step 4: Environment file
        Create-EnvironmentFile $credentials $config.ProductionMode
        
        # Step 5: Docker build
        if (-not (Start-DockerBuild $config.DeployType)) {
            Write-ColorText "❌ Error en construcción Docker. Deployment cancelado." $Colors.Error
            return
        }
        
        # Step 6: Deployment
        if (-not (Start-Deployment $config.DeployType)) {
            Write-ColorText "❌ Error en deployment. Proceso cancelado." $Colors.Error
            return
        }
        
        # Step 7: Health check
        $healthResult = Wait-ForHealthCheck $config.DeployType
        
        # Step 8: Endpoint testing
        $endpointResults = @()
        if ($healthResult.Success) {
            $endpointResults = Test-Endpoints $healthResult.Url
        }
        
        # Step 9: Summary
        Show-DeploymentSummary $config $healthResult $endpointResults
        
    } catch {
        Write-ColorText "❌ Error durante el deployment: $($_.Exception.Message)" $Colors.Error
        Write-ColorText "📋 Stack trace: $($_.ScriptStackTrace)" $Colors.Error
    }
    
    Write-ColorText "`n⏸️  Presiona cualquier tecla para continuar..." $Colors.Info
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Execute main function
Main