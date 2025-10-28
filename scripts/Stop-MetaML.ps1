# 🧠 Meta ML System - Stop Script for Windows
# Detiene todos los servicios del sistema Meta ML

Write-Host "🛑 DETENIENDO SISTEMA META ML..." -ForegroundColor Red
Write-Host "==================================" -ForegroundColor Red

# Función para detener servicio
function Stop-Service {
    param([string]$ServiceName)
    
    $pidFile = "logs\$ServiceName.pid"
    
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "🛑 Deteniendo $ServiceName (PID: $pid)..." -ForegroundColor Yellow
                Stop-Process -Id $pid -Force
                
                # Esperar a que termine
                $count = 0
                while ((Get-Process -Id $pid -ErrorAction SilentlyContinue) -and ($count -lt 10)) {
                    Start-Sleep -Seconds 1
                    $count++
                }
                
                Remove-Item -Path $pidFile -Force
                Write-Host "✅ $ServiceName detenido" -ForegroundColor Green
            } else {
                Write-Host "⚠️ $ServiceName no estaba corriendo" -ForegroundColor Yellow
                Remove-Item -Path $pidFile -Force
            }
        } catch {
            Write-Host "⚠️ Error deteniendo $ServiceName: $($_.Exception.Message)" -ForegroundColor Yellow
            Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue
        }
    } else {
        Write-Host "⚠️ No se encontró PID file para $ServiceName" -ForegroundColor Yellow
    }
}

# Detener servicios
Stop-Service -ServiceName "meta-ml-api"
Stop-Service -ServiceName "meta-ml-dashboard"

# Limpiar procesos huérfanos
Write-Host ""
Write-Host "🧹 Limpiando procesos..." -ForegroundColor Yellow

# Matar procesos Python relacionados con Meta ML
try {
    Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*sistema_meta_ml*" } | Stop-Process -Force
    Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*dashboard_meta_ml*" } | Stop-Process -Force
    Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*uvicorn*8006*" } | Stop-Process -Force  
    Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.CommandLine -like "*streamlit*8501*" } | Stop-Process -Force
} catch {
    # Ignorar errores si no hay procesos
}

# Verificar que los puertos estén libres
Write-Host ""
Write-Host "🔍 Verificando puertos..." -ForegroundColor Yellow

# Puerto 8006
$port8006 = Get-NetTCPConnection -LocalPort 8006 -ErrorAction SilentlyContinue
if ($port8006) {
    Write-Host "⚠️ Puerto 8006 aún ocupado" -ForegroundColor Yellow
    try {
        $process8006 = Get-Process -Id $port8006.OwningProcess -ErrorAction SilentlyContinue
        if ($process8006) {
            Stop-Process -Id $process8006.Id -Force
        }
    } catch {
        # Ignorar errores
    }
} else {
    Write-Host "✅ Puerto 8006 libre" -ForegroundColor Green
}

# Puerto 8501
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue  
if ($port8501) {
    Write-Host "⚠️ Puerto 8501 aún ocupado" -ForegroundColor Yellow
    try {
        $process8501 = Get-Process -Id $port8501.OwningProcess -ErrorAction SilentlyContinue
        if ($process8501) {
            Stop-Process -Id $process8501.Id -Force
        }
    } catch {
        # Ignorar errores
    }
} else {
    Write-Host "✅ Puerto 8501 libre" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ SISTEMA META ML DETENIDO COMPLETAMENTE" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para reiniciar:" -ForegroundColor Gray
Write-Host "  .\scripts\Start-MetaML.ps1" -ForegroundColor Gray