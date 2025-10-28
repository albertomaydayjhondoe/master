# 🧠 Meta ML System - Start Script for Windows
# Lanza el sistema completo de Meta ML para optimización España-LATAM

Write-Host "🧠 INICIANDO SISTEMA META ML..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Instala Python 3.11+" -ForegroundColor Red
    exit 1
}

# Crear entorno virtual si no existe
if (-not (Test-Path "venv_meta_ml")) {
    Write-Host "📦 Creando entorno virtual Meta ML..." -ForegroundColor Yellow
    python -m venv venv_meta_ml
}

# Activar entorno virtual
Write-Host "⚡ Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv_meta_ml\Scripts\Activate.ps1"

# Instalar dependencias
Write-Host "📥 Instalando dependencias ML..." -ForegroundColor Yellow
pip install -q -r requirements.txt
pip install -q -r requirements-ml.txt

# Dependencias específicas Meta ML
pip install -q "scikit-learn>=1.3.0" "pandas>=2.0.0" "numpy>=1.24.0" "joblib>=1.3.0"
pip install -q "plotly>=5.15.0" "streamlit>=1.25.0" "asyncpg>=0.28.0"

# Setup inicial del sistema
Write-Host "🔧 Configurando sistema Meta ML..." -ForegroundColor Yellow
python scripts/setup_meta_ml.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Setup Meta ML completado" -ForegroundColor Green
} else {
    Write-Host "❌ Error en setup Meta ML" -ForegroundColor Red
    exit 1
}

# Crear directorio de logs
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Función para lanzar servicios
function Launch-Service {
    param(
        [string]$ServiceName,
        [string]$Command,
        [int]$Port
    )
    
    Write-Host "🚀 Lanzando $ServiceName en puerto $Port..." -ForegroundColor Cyan
    
    $logFile = "logs\$ServiceName.log"
    $pidFile = "logs\$ServiceName.pid"
    
    # Lanzar proceso en background
    $process = Start-Process -FilePath "powershell" -ArgumentList "-Command", $Command -WindowStyle Hidden -PassThru -RedirectStandardOutput $logFile -RedirectStandardError $logFile
    
    # Guardar PID
    $process.Id | Out-File -FilePath $pidFile
    
    # Verificar que esté corriendo
    Start-Sleep -Seconds 3
    if ($process -and !$process.HasExited) {
        Write-Host "✅ $ServiceName iniciado correctamente (PID: $($process.Id))" -ForegroundColor Green
    } else {
        Write-Host "❌ Error iniciando $ServiceName" -ForegroundColor Red
    }
}

# 1. Lanzar API Meta ML
Write-Host ""
Write-Host "🤖 LANZANDO API META ML..." -ForegroundColor Magenta
Launch-Service -ServiceName "meta-ml-api" -Command "python -m uvicorn ml_core.sistema_meta_ml:app --host 0.0.0.0 --port 8006" -Port 8006

# 2. Lanzar Dashboard Meta ML  
Write-Host ""
Write-Host "📊 LANZANDO DASHBOARD META ML..." -ForegroundColor Magenta
Launch-Service -ServiceName "meta-ml-dashboard" -Command "streamlit run dashboard_meta_ml.py --server.port 8501 --server.headless true" -Port 8501

# 3. Verificar servicios
Write-Host ""
Write-Host "🔍 VERIFICANDO SERVICIOS..." -ForegroundColor Yellow

Start-Sleep -Seconds 8

# Health check API
try {
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8006/health" -UseBasicParsing -TimeoutSec 10
    if ($apiResponse.StatusCode -eq 200) {
        Write-Host "✅ API Meta ML: http://localhost:8006 - ACTIVO" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ API Meta ML: ERROR" -ForegroundColor Red
}

# Health check Dashboard
try {
    $dashResponse = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 10
    if ($dashResponse.StatusCode -eq 200) {
        Write-Host "✅ Dashboard Meta ML: http://localhost:8501 - ACTIVO" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Dashboard Meta ML: ERROR" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 SISTEMA META ML INICIADO" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host "🤖 API ML: http://localhost:8006" -ForegroundColor Cyan
Write-Host "📊 Dashboard: http://localhost:8501" -ForegroundColor Cyan
Write-Host "📋 Logs: .\logs\" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 READY FOR €400 META ADS CAMPAIGNS!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para detener:" -ForegroundColor Gray
Write-Host "  .\scripts\Stop-MetaML.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Para monitorear:" -ForegroundColor Gray
Write-Host "  Get-Content -Path .\logs\meta-ml-api.log -Wait" -ForegroundColor Gray
Write-Host "  Get-Content -Path .\logs\meta-ml-dashboard.log -Wait" -ForegroundColor Gray