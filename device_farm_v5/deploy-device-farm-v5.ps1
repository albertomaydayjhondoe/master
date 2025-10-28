# Device Farm v5 - Interactive Deployment Script
# Automated deployment with step-by-step guidance

param(
    [switch]$Development = $false,
    [switch]$Production = $false,
    [switch]$QuickStart = $false,
    [string]$ConfigFile = "",
    [switch]$SkipDependencyCheck = $false
)

# Colors for better UX
$Colors = @{
    Header = [ConsoleColor]::Cyan
    Success = [ConsoleColor]::Green
    Warning = [ConsoleColor]::Yellow
    Error = [ConsoleColor]::Red
    Info = [ConsoleColor]::Blue
    Prompt = [ConsoleColor]::Magenta
}

function Write-ColorText($Text, $Color = $Colors.Info) {
    Write-Host $Text -ForegroundColor $Color
}

function Write-DeviceFarmHeader($Text) {
    Write-Host ""
    Write-ColorText "🤖═══════════════════════════════════════════════════════════════════🤖" $Colors.Header
    Write-ColorText "    $Text" $Colors.Header
    Write-ColorText "🤖═══════════════════════════════════════════════════════════════════🤖" $Colors.Header
    Write-Host ""
}

function Read-UserInput($Prompt, $Default = "", $Required = $false, $Secret = $false) {
    do {
        if ($Default) {
            Write-ColorText "🤖 $Prompt [$Default]: " $Colors.Prompt -NoNewline
        } else {
            Write-ColorText "🤖 $Prompt" $Colors.Prompt -NoNewline
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
            Write-ColorText "⚠️  Este campo es requerido." $Colors.Warning
        }
    } while ($Required -and [string]::IsNullOrWhiteSpace($input))
    
    return $input
}

function Test-Prerequisites {
    Write-DeviceFarmHeader "VERIFICACIÓN DE PREREQUISITOS"
    
    $allGood = $true
    
    # Docker check
    Write-ColorText "🐳 Verificando Docker..." $Colors.Info
    try {
        docker --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Docker instalado correctamente" $Colors.Success
        } else {
            Write-ColorText "❌ Docker no está funcionando" $Colors.Error
            $allGood = $false
        }
    } catch {
        Write-ColorText "❌ Docker no está instalado" $Colors.Error
        $allGood = $false
    }
    
    # Docker Compose check
    Write-ColorText "🐳 Verificando Docker Compose..." $Colors.Info
    try {
        docker-compose --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Docker Compose disponible" $Colors.Success
        } else {
            Write-ColorText "❌ Docker Compose no disponible" $Colors.Error
            $allGood = $false
        }
    } catch {
        Write-ColorText "❌ Docker Compose no está instalado" $Colors.Error
        $allGood = $false
    }
    
    # ADB check
    Write-ColorText "📱 Verificando ADB..." $Colors.Info
    try {
        adb version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ ADB disponible" $Colors.Success
        } else {
            Write-ColorText "⚠️  ADB no disponible - se instalará en container" $Colors.Warning
        }
    } catch {
        Write-ColorText "⚠️  ADB no encontrado - se instalará en container" $Colors.Warning
    }
    
    # USB devices check
    Write-ColorText "📱 Verificando dispositivos USB..." $Colors.Info
    try {
        $devices = adb devices 2>$null
        if ($devices -and $devices.Contains("device")) {
            Write-ColorText "✅ Dispositivos Android detectados" $Colors.Success
        } else {
            Write-ColorText "⚠️  No se detectaron dispositivos Android (conectar después)" $Colors.Warning
        }
    } catch {
        Write-ColorText "⚠️  No se pueden verificar dispositivos" $Colors.Warning
    }
    
    # Node.js check (for Appium)
    Write-ColorText "🚀 Verificando Node.js..." $Colors.Info
    try {
        node --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Node.js disponible" $Colors.Success
        } else {
            Write-ColorText "⚠️  Node.js no disponible - se instalará en container" $Colors.Warning
        }
    } catch {
        Write-ColorText "⚠️  Node.js no encontrado - se instalará en container" $Colors.Warning
    }
    
    return $allGood
}

function Get-DeploymentConfiguration {
    Write-DeviceFarmHeader "CONFIGURACIÓN DE DEPLOYMENT"
    
    $config = @{}
    
    # Deployment type
    Write-ColorText "📋 Selecciona el tipo de deployment:" $Colors.Info
    Write-ColorText "1. 🔧 Desarrollo - Testing local con hot reload" $Colors.Info
    Write-ColorText "2. 🚀 Producción - Sistema completo optimizado" $Colors.Info
    Write-ColorText "3. ⚡ Quick Start - Deployment rápido con configuración mínima" $Colors.Info
    
    if ($Development) {
        $deployType = "1"
    } elseif ($Production) {
        $deployType = "2"
    } elseif ($QuickStart) {
        $deployType = "3"
    } else {
        $deployType = Read-UserInput "Tipo de deployment [1-3]" "1" $true
    }
    
    switch ($deployType) {
        "1" { 
            $config.DeploymentType = "development"
            Write-ColorText "🔧 Deployment de desarrollo seleccionado" $Colors.Info
        }
        "2" { 
            $config.DeploymentType = "production"
            Write-ColorText "🚀 Deployment de producción seleccionado" $Colors.Info
        }
        "3" { 
            $config.DeploymentType = "quickstart"
            Write-ColorText "⚡ Quick Start seleccionado" $Colors.Info
        }
        default { $config.DeploymentType = "development" }
    }
    
    # Device configuration
    Write-ColorText "`n📱 ¿Cuántos dispositivos Android planeas conectar?" $Colors.Info
    $config.ExpectedDevices = Read-UserInput "Número de dispositivos" "10"
    
    # Gologin configuration
    Write-ColorText "`n🔗 GOLOGIN API CONFIGURATION:" $Colors.Info
    Write-ColorText "   • Necesario para profiles de navegador y proxies" $Colors.Info
    Write-ColorText "   • Obtén tu token en: https://app.gologin.com/profile" $Colors.Info
    Write-Host ""
    
    $setupGologin = Read-UserInput "¿Configurar Gologin API? (y/n)" "y"
    if ($setupGologin.ToLower() -eq "y") {
        $config.GologinToken = Read-UserInput "Gologin API Token" "" $true $true
    } else {
        $config.GologinToken = "dummy-token-for-testing"
        Write-ColorText "⚠️  Usando token dummy - funcionalidad limitada" $Colors.Warning
    }
    
    # Dashboard configuration
    Write-ColorText "`n🎛️  DASHBOARD CONFIGURATION:" $Colors.Info
    $config.DashboardUsername = Read-UserInput "Dashboard Username" "admin"
    $config.DashboardPassword = Read-UserInput "Dashboard Password" "admin123" $false $true
    
    # Advanced configuration for production
    if ($config.DeploymentType -eq "production") {
        Write-ColorText "`n⚙️  CONFIGURACIÓN AVANZADA:" $Colors.Info
        
        $setupRedis = Read-UserInput "¿Configurar Redis externa? (y/n)" "n"
        if ($setupRedis.ToLower() -eq "y") {
            $config.RedisHost = Read-UserInput "Redis Host" "localhost"
            $config.RedisPort = Read-UserInput "Redis Port" "6379"
            $config.RedisPassword = Read-UserInput "Redis Password" "" $false $true
        }
        
        $setupMonitoring = Read-UserInput "¿Habilitar monitoreo (Prometheus/Grafana)? (y/n)" "n"
        $config.EnableMonitoring = $setupMonitoring.ToLower() -eq "y"
        
        $setupNginx = Read-UserInput "¿Usar Nginx como reverse proxy? (y/n)" "n"
        $config.EnableNginx = $setupNginx.ToLower() -eq "y"
    }
    
    return $config
}

function Create-EnvironmentFile($Config) {
    Write-ColorText "📝 Creando archivo de configuración..." $Colors.Info
    
    $envContent = @"
# Device Farm v5 - Environment Configuration
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# === GOLOGIN API ===
GOLOGIN_API_TOKEN=$($Config.GologinToken)

# === DASHBOARD SECURITY ===
DASHBOARD_SECRET_KEY=device-farm-v5-$(Get-Random -Maximum 999999)
DASHBOARD_USERNAME=$($Config.DashboardUsername)
DASHBOARD_PASSWORD=$($Config.DashboardPassword)

# === API SECURITY ===
API_SECRET_KEY=api-key-$(Get-Random -Maximum 999999)
JWT_SECRET_KEY=jwt-key-$(Get-Random -Maximum 999999)

# === DEPLOYMENT CONFIGURATION ===
ENVIRONMENT=$($Config.DeploymentType)
DEBUG=$($Config.DeploymentType -eq 'development')
LOG_LEVEL=$( if ($Config.DeploymentType -eq 'development') { 'DEBUG' } else { 'INFO' } )
EXPECTED_DEVICES=$($Config.ExpectedDevices)

# === REDIS CONFIGURATION ===
REDIS_HOST=$($Config.RedisHost ?? 'redis')
REDIS_PORT=$($Config.RedisPort ?? '6379')
REDIS_PASSWORD=$($Config.RedisPassword ?? 'devicefarm123')
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-ColorText "✅ Archivo .env creado" $Colors.Success
}

function Build-DeviceFarmImage($Config) {
    Write-ColorText "🔨 Construyendo imagen Docker..." $Colors.Info
    
    $imageName = "device-farm-v5:$($Config.DeploymentType)"
    
    try {
        docker build -t $imageName . --progress=plain
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Imagen Docker construida: $imageName" $Colors.Success
            return $true
        } else {
            Write-ColorText "❌ Error construyendo imagen Docker" $Colors.Error
            return $false
        }
    } catch {
        Write-ColorText "❌ Error construyendo imagen Docker: $_" $Colors.Error
        return $false
    }
}

function Deploy-System($Config) {
    Write-ColorText "🚀 Deployando Device Farm v5..." $Colors.Info
    
    try {
        switch ($Config.DeploymentType) {
            "development" {
                Write-ColorText "🔧 Iniciando en modo desarrollo..." $Colors.Info
                docker-compose -f docker-compose.dev.yml up -d
            }
            "production" {
                Write-ColorText "🚀 Iniciando en modo producción..." $Colors.Info
                
                $profiles = @()
                if ($Config.EnableMonitoring) { $profiles += "monitoring" }
                if ($Config.EnableNginx) { $profiles += "nginx" }
                
                if ($profiles.Count -gt 0) {
                    $profileArgs = "--profile " + ($profiles -join " --profile ")
                    Invoke-Expression "docker-compose $profileArgs up -d"
                } else {
                    docker-compose up -d
                }
            }
            "quickstart" {
                Write-ColorText "⚡ Quick Start deployment..." $Colors.Info
                docker-compose up -d device-farm redis
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✅ Sistema deployado exitosamente" $Colors.Success
            return $true
        } else {
            Write-ColorText "❌ Error en deployment" $Colors.Error
            return $false
        }
    } catch {
        Write-ColorText "❌ Error deployando sistema: $_" $Colors.Error
        return $false
    }
}

function Wait-ForServices($Config) {
    Write-ColorText "⏳ Esperando que los servicios estén listos..." $Colors.Info
    
    $maxWait = 120  # 2 minutes
    $waited = 0
    
    while ($waited -lt $maxWait) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-ColorText "✅ Servicios están listos!" $Colors.Success
                return $true
            }
        } catch {
            # Service not ready yet
        }
        
        Start-Sleep -Seconds 5
        $waited += 5
        Write-ColorText "." $Colors.Info -NoNewline
    }
    
    Write-ColorText "`n⚠️  Servicios tardan en estar listos, pero el deployment continuó" $Colors.Warning
    return $false
}

function Show-DeploymentSummary($Config) {
    Write-DeviceFarmHeader "DEVICE FARM v5 DEPLOYADO EXITOSAMENTE"
    
    Write-ColorText "🎉 ¡Tu Device Farm está corriendo!" $Colors.Success
    Write-Host ""
    
    Write-ColorText "🌐 ACCESOS PRINCIPALES:" $Colors.Info
    Write-ColorText "   • 🎛️  Dashboard Principal: http://localhost:5000" $Colors.Success
    Write-ColorText "   • 📊 API Documentation: http://localhost:8000/docs" $Colors.Success
    Write-ColorText "   • 🤖 Appium Servers: http://localhost:4723-4733" $Colors.Success
    
    if ($Config.EnableMonitoring) {
        Write-ColorText "   • 📈 Prometheus: http://localhost:9090" $Colors.Success
        Write-ColorText "   • 📊 Grafana: http://localhost:3000" $Colors.Success
    }
    
    Write-Host ""
    
    Write-ColorText "📱 PRÓXIMOS PASOS:" $Colors.Info
    Write-ColorText "   1. 🔌 Conecta tus dispositivos Android via USB" $Colors.Success
    Write-ColorText "   2. 📱 Habilita 'Depuración USB' en cada dispositivo" $Colors.Success
    Write-ColorText "   3. 🎛️  Accede al dashboard en http://localhost:5000" $Colors.Success
    Write-ColorText "   4. 🔗 Configura perfiles Gologin si no lo hiciste" $Colors.Success
    Write-ColorText "   5. ⚡ ¡Empieza a automatizar!" $Colors.Success
    
    Write-Host ""
    
    Write-ColorText "📋 COMANDOS ÚTILES:" $Colors.Info
    Write-ColorText "   • Ver logs: docker-compose logs -f" $Colors.Success
    Write-ColorText "   • Detener: docker-compose down" $Colors.Success
    Write-ColorText "   • Reiniciar: docker-compose restart" $Colors.Success
    Write-ColorText "   • Estado: docker-compose ps" $Colors.Success
    
    Write-Host ""
    
    Write-ColorText "💡 CREDENCIALES:" $Colors.Info
    Write-ColorText "   • Dashboard: $($Config.DashboardUsername) / $($Config.DashboardPassword)" $Colors.Success
    Write-ColorText "   • Redis: devicefarm123" $Colors.Success
    
    Write-Host ""
    Write-ColorText "🤖 ¡DEVICE FARM v5 LISTO PARA AUTOMATIZACIÓN!" $Colors.Success
}

function Main {
    Clear-Host
    
    # Device Farm logo
    Write-ColorText @"
    🤖 ═══════════════════════════════════════════════════════════════ 🤖
                        DEVICE FARM v5 DEPLOYMENT SCRIPT
                      10x Android Devices + Gologin + Appium
    🤖 ═══════════════════════════════════════════════════════════════ 🤖
"@ $Colors.Header
    
    Write-ColorText "`n🚀 Sistema profesional para automatización de dispositivos Android" $Colors.Info
    Write-ColorText "📱 Soporte para 10 dispositivos físicos + Gologin API + Appium + Dashboard web" $Colors.Info
    Write-Host ""
    
    try {
        # Check prerequisites
        if (-not $SkipDependencyCheck) {
            $prereqsOk = Test-Prerequisites
            if (-not $prereqsOk) {
                Write-ColorText "❌ Prerequisitos no cumplidos. Instala Docker y Docker Compose primero." $Colors.Error
                Read-Host "Presiona Enter para salir..."
                return
            }
        }
        
        # Get deployment configuration
        $config = Get-DeploymentConfiguration
        
        # Create environment file
        Create-EnvironmentFile $config
        
        # Build Docker image
        $buildSuccess = Build-DeviceFarmImage $config
        if (-not $buildSuccess) {
            Write-ColorText "❌ Error construyendo imagen. Verifica Docker y conexión a internet." $Colors.Error
            Read-Host "Presiona Enter para salir..."
            return
        }
        
        # Deploy system
        $deploySuccess = Deploy-System $config
        if (-not $deploySuccess) {
            Write-ColorText "❌ Error en deployment. Verifica logs con: docker-compose logs" $Colors.Error
            Read-Host "Presiona Enter para salir..."
            return
        }
        
        # Wait for services
        Wait-ForServices $config
        
        # Show summary
        Show-DeploymentSummary $config
        
    } catch {
        Write-ColorText "❌ Error durante deployment: $_" $Colors.Error
    }
    
    Read-Host "`n🤖 Presiona Enter para continuar..."
}

# Execute main function
Main