# TikTok ML System v4 - Artist Campaign Launch Script  
# Specialized deployment for music artist campaign management

param(
    [string]$ArtistName = "",
    [string]$CampaignName = "",
    [switch]$MinimalSetup = $false
)

# Colors for enhanced user experience
$Colors = @{
    Header = [ConsoleColor]::Cyan
    Success = [ConsoleColor]::Green
    Warning = [ConsoleColor]::Yellow
    Error = [ConsoleColor]::Red
    Info = [ConsoleColor]::Blue
    Prompt = [ConsoleColor]::Magenta
    Artist = [ConsoleColor]::Yellow
}

function Write-ColorText($Text, $Color = $Colors.Info) {
    Write-Host $Text -ForegroundColor $Color
}

function Write-ArtistHeader($Text) {
    Write-Host ""
    Write-ColorText "🎵═══════════════════════════════════════════════════════════════════🎵" $Colors.Header
    Write-ColorText "    $Text" $Colors.Header
    Write-ColorText "🎵═══════════════════════════════════════════════════════════════════🎵" $Colors.Header
    Write-Host ""
}

function Read-ArtistInput($Prompt, $Default = "", $Required = $false, $Secret = $false) {
    do {
        if ($Default) {
            Write-ColorText "🎤 $Prompt [$Default]: " $Colors.Prompt -NoNewline
        } else {
            Write-ColorText "🎤 $Prompt" $Colors.Prompt -NoNewline
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
            Write-ColorText "⚠️  Este campo es requerido para la campaña." $Colors.Warning
        }
    } while ($Required -and [string]::IsNullOrWhiteSpace($input))
    
    return $input
}

function Get-CampaignInfo {
    Write-ArtistHeader "INFORMACIÓN DE LA CAMPAÑA MUSICAL"
    
    $campaign = @{}
    
    if ([string]::IsNullOrWhiteSpace($ArtistName)) {
        $campaign.ArtistName = Read-ArtistInput "Nombre del Artista" "" $true
    } else {
        $campaign.ArtistName = $ArtistName
        Write-ColorText "🎤 Artista: $($campaign.ArtistName)" $Colors.Artist
    }
    
    if ([string]::IsNullOrWhiteSpace($CampaignName)) {
        $campaign.CampaignName = Read-ArtistInput "Nombre de la Campaña/Lanzamiento" "" $true
    } else {
        $campaign.CampaignName = $CampaignName  
        Write-ColorText "🚀 Campaña: $($campaign.CampaignName)" $Colors.Artist
    }
    
    Write-ColorText "`n📋 Selecciona el alcance de tu campaña:" $Colors.Info
    Write-ColorText "1. 🎯 SETUP MÍNIMO - Solo analytics básicos (Supabase)" $Colors.Info
    Write-ColorText "2. 🚀 CAMPAÑA ESTÁNDAR - Analytics + Meta Ads + Streaming platforms" $Colors.Info  
    Write-ColorText "3. 🔥 CAMPAÑA COMPLETA - Todo + Automation + Landing pages" $Colors.Info
    
    $scope = Read-ArtistInput "Alcance de campaña [1-3]" "2" $true
    
    switch ($scope) {
        "1" { 
            $campaign.Scope = "minimal"
            Write-ColorText "🎯 Setup mínimo seleccionado - Solo Supabase para analytics" $Colors.Info
        }
        "2" { 
            $campaign.Scope = "standard"
            Write-ColorText "🚀 Campaña estándar - Analytics completos + Meta Ads + Streaming" $Colors.Info
        }
        "3" { 
            $campaign.Scope = "complete"
            Write-ColorText "🔥 Campaña completa - Automatización total" $Colors.Info
        }
        default { $campaign.Scope = "standard" }
    }
    
    return $campaign
}

function Get-ArtistCredentials($Scope) {
    Write-ArtistHeader "CONFIGURACIÓN DE PLATAFORMAS MUSICALES"
    
    $creds = @{}
    
    # Supabase (SIEMPRE requerido)
    Write-ColorText "📊 SUPABASE - Analytics Database (REQUERIDO)" $Colors.Info
    Write-ColorText "   → Centraliza todas las métricas de tu campaña" $Colors.Info
    Write-ColorText "   → Tracking de streams, engagement, conversiones" $Colors.Info
    Write-ColorText "   → Dashboard personalizado para tu equipo" $Colors.Info
    Write-Host ""
    
    $setupSupabase = Read-ArtistInput "¿Ya tienes proyecto Supabase? (y/n)" "n"
    
    if ($setupSupabase.ToLower() -eq "n") {
        Write-ColorText "📋 CREAR PROYECTO SUPABASE:" $Colors.Warning
        Write-ColorText "   1. Ve a https://supabase.com" $Colors.Info
        Write-ColorText "   2. Crea cuenta gratuita" $Colors.Info  
        Write-ColorText "   3. Nuevo proyecto → Nombre: '$CampaignName Analytics'" $Colors.Info
        Write-ColorText "   4. Copia URL y Keys del dashboard" $Colors.Info
        Write-Host ""
        Read-ArtistInput "Presiona Enter cuando tengas el proyecto listo" ""
    }
    
    $creds.SUPABASE_URL = Read-ArtistInput "Supabase Project URL" "https://tu-proyecto.supabase.co" $true
    $creds.SUPABASE_ANON_KEY = Read-ArtistInput "Supabase Anon Key" "" $true $true
    $creds.SUPABASE_SERVICE_KEY = Read-ArtistInput "Supabase Service Key" "" $true $true
    
    # Configuraciones según scope
    if ($Scope -in @("standard", "complete")) {
        
        # Meta Ads para promoción
        Write-ColorText "`n🎯 META ADS - Promoción en Instagram/Facebook" $Colors.Info
        Write-ColorText "   → Campañas para video musical, streams, eventos" $Colors.Info
        Write-ColorText "   → Targeting de audiencia musical" $Colors.Info  
        Write-ColorText "   → Analytics de conversión" $Colors.Info
        
        $setupMeta = Read-ArtistInput "¿Configurar Meta Ads para promoción? (y/n)" "y"
        
        if ($setupMeta.ToLower() -eq "y") {
            Write-ColorText "📋 SETUP META ADS:" $Colors.Warning
            Write-ColorText "   1. Ve a https://developers.facebook.com" $Colors.Info
            Write-ColorText "   2. Crear App → Marketing API" $Colors.Info
            Write-ColorText "   3. Generar Access Token (long-lived)" $Colors.Info
            Write-Host ""
            
            $creds.META_APP_ID = Read-ArtistInput "Meta App ID" "" $true
            $creds.META_APP_SECRET = Read-ArtistInput "Meta App Secret" "" $true $true  
            $creds.META_ACCESS_TOKEN = Read-ArtistInput "Meta Access Token" "" $true $true
        }
        
        # Spotify Analytics
        Write-ColorText "`n🎵 SPOTIFY - Analytics de Streams y Playlists" $Colors.Info
        Write-ColorText "   → Tracking de streams en tiempo real" $Colors.Info
        Write-ColorText "   → Análisis de playlists y descubermiento" $Colors.Info
        Write-ColorText "   → Métricas de engagement de fans" $Colors.Info
        
        $setupSpotify = Read-ArtistInput "¿Configurar Spotify Analytics? (y/n)" "y"
        
        if ($setupSpotify.ToLower() -eq "y") {
            Write-ColorText "📋 SETUP SPOTIFY:" $Colors.Warning
            Write-ColorText "   1. Ve a https://developer.spotify.com" $Colors.Info
            Write-ColorText "   2. Crear App → Web API" $Colors.Info  
            Write-ColorText "   3. Buscar tus Artist IDs en Spotify" $Colors.Info
            Write-Host ""
            
            $creds.SPOTIFY_CLIENT_ID = Read-ArtistInput "Spotify Client ID" "" $true
            $creds.SPOTIFY_CLIENT_SECRET = Read-ArtistInput "Spotify Client Secret" "" $true $true
            
            $artistIds = Read-ArtistInput "Spotify Artist IDs (separados por coma)" ""
            if ($artistIds) {
                $creds.SPOTIFY_ARTIST_IDS = $artistIds
            }
        }
        
        # YouTube Analytics  
        Write-ColorText "`n🎥 YOUTUBE - Analytics de Videos Musicales" $Colors.Info
        Write-ColorText "   → Tracking de views, engagement, comentarios" $Colors.Info
        Write-ColorText "   → Analytics de performance de videos" $Colors.Info
        Write-ColorText "   → Métricas de crecimiento de canal" $Colors.Info
        
        $setupYoutube = Read-ArtistInput "¿Configurar YouTube Analytics? (y/n)" "y"
        
        if ($setupYoutube.ToLower() -eq "y") {
            Write-ColorText "📋 SETUP YOUTUBE:" $Colors.Warning  
            Write-ColorText "   1. Ve a https://console.cloud.google.com" $Colors.Info
            Write-ColorText "   2. Nuevo proyecto → YouTube Data API v3" $Colors.Info
            Write-ColorText "   3. Crear API Key" $Colors.Info
            Write-Host ""
            
            $creds.YOUTUBE_API_KEY = Read-ArtistInput "YouTube API Key" "" $true $true
            
            $channelIds = Read-ArtistInput "YouTube Channel IDs (separados por coma)" ""  
            if ($channelIds) {
                $creds.YOUTUBE_CHANNEL_IDS = $channelIds
            }
        }
    }
    
    if ($Scope -eq "complete") {
        # Landing Pages para campaign
        Write-ColorText "`n🌐 LANDING PAGES - Conversión de Fans" $Colors.Info
        Write-ColorText "   → Páginas de preventa, merchandise, eventos" $Colors.Info
        Write-ColorText "   → Tracking de conversiones" $Colors.Info
        Write-ColorText "   → Analytics de traffic sources" $Colors.Info
        
        $landingUrls = Read-ArtistInput "URLs de Landing Pages (separadas por coma)" ""
        if ($landingUrls) {
            $creds.LANDING_PAGE_URLS = $landingUrls
        }
        
        # n8n para automation
        Write-ColorText "`n🔄 N8N - Automatización de Campaña" $Colors.Info  
        Write-ColorText "   → Workflows automáticos" $Colors.Info
        Write-ColorText "   → Sincronización entre plataformas" $Colors.Info
        Write-ColorText "   → Alertas y notificaciones" $Colors.Info
        
        $setupN8n = Read-ArtistInput "¿Configurar automatización n8n? (y/n)" "n"
        
        if ($setupN8n.ToLower() -eq "y") {
            $creds.N8N_WEBHOOK_BASE_URL = Read-ArtistInput "n8n Webhook URL" ""
            $creds.N8N_API_KEY = Read-ArtistInput "n8n API Key" "" $false $true
        }
    }
    
    # Core API credentials
    $creds.API_SECRET_KEY = "artist-campaign-$($campaign.ArtistName.ToLower().Replace(' ', '-'))-$(Get-Random -Maximum 999999)"
    $creds.JWT_SECRET = "jwt-$($campaign.CampaignName.ToLower().Replace(' ', '-'))-$(Get-Random -Maximum 999999)"
    
    return $creds
}

function Create-CampaignEnvironment($Campaign, $Credentials) {
    Write-ArtistHeader "CREACIÓN DE ENTORNO DE CAMPAÑA"
    
    Write-ColorText "📝 Creando configuración personalizada para $($Campaign.ArtistName)..." $Colors.Info
    
    $envContent = @"
# ========================================
# 🎵 CAMPAÑA MUSICAL - $($Campaign.ArtistName.ToUpper())
# 🚀 Lanzamiento: $($Campaign.CampaignName) 
# 📅 Generado: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# ========================================

# === INFORMACIÓN DE CAMPAÑA ===
ARTIST_NAME=$($Campaign.ArtistName)
CAMPAIGN_NAME=$($Campaign.CampaignName)
CAMPAIGN_SCOPE=$($Campaign.Scope)

# === CONFIGURACIÓN DEL SISTEMA ===
PRODUCTION_MODE=true
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=$($Credentials.API_SECRET_KEY)
JWT_SECRET=$($Credentials.JWT_SECRET)

# === SUPABASE - ANALYTICS DATABASE ===
SUPABASE_URL=$($Credentials.SUPABASE_URL)
SUPABASE_ANON_KEY=$($Credentials.SUPABASE_ANON_KEY)  
SUPABASE_SERVICE_KEY=$($Credentials.SUPABASE_SERVICE_KEY)

# === META ADS - PROMOCIÓN MUSICAL ===
META_APP_ID=$($Credentials.META_APP_ID)
META_APP_SECRET=$($Credentials.META_APP_SECRET)
META_ACCESS_TOKEN=$($Credentials.META_ACCESS_TOKEN)

# === SPOTIFY - STREAMING ANALYTICS ===
SPOTIFY_CLIENT_ID=$($Credentials.SPOTIFY_CLIENT_ID)
SPOTIFY_CLIENT_SECRET=$($Credentials.SPOTIFY_CLIENT_SECRET)
SPOTIFY_ARTIST_IDS=$($Credentials.SPOTIFY_ARTIST_IDS)

# === YOUTUBE - VIDEO ANALYTICS ===
YOUTUBE_API_KEY=$($Credentials.YOUTUBE_API_KEY)
YOUTUBE_CHANNEL_IDS=$($Credentials.YOUTUBE_CHANNEL_IDS)

# === LANDING PAGES - CONVERSIÓN ===
LANDING_PAGE_URLS=$($Credentials.LANDING_PAGE_URLS)

# === AUTOMATIZACIÓN ===
N8N_WEBHOOK_BASE_URL=$($Credentials.N8N_WEBHOOK_BASE_URL)
N8N_API_KEY=$($Credentials.N8N_API_KEY)

# === ML CONFIGURATION ===
ULTRALYTICS_MODEL=yolov8n.pt
ML_MODEL_PATH=/app/data/models
MAX_UPLOAD_SIZE=52428800

# === DEPLOYMENT ===
PORT=8000
HEALTHCHECK_INTERVAL=30s
"@
    
    # Backup existing .env
    if (Test-Path ".env") {
        $backup = ".env.backup.artist-campaign.$(Get-Date -Format "yyyyMMdd-HHmmss")"
        Copy-Item ".env" $backup
        Write-ColorText "💾 Backup guardado: $backup" $Colors.Warning
    }
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-ColorText "✅ Configuración de campaña creada" $Colors.Success
    
    # Create campaign folder for assets
    $campaignFolder = "campaigns\$($Campaign.ArtistName.Replace(' ', '_'))\$($Campaign.CampaignName.Replace(' ', '_'))"
    if (-not (Test-Path $campaignFolder)) {
        New-Item -ItemType Directory -Path $campaignFolder -Force | Out-Null
        Write-ColorText "📁 Folder de campaña creado: $campaignFolder" $Colors.Success
    }
}

function Show-CampaignSummary($Campaign, $BaseUrl) {
    Write-ArtistHeader "CAMPAÑA MUSICAL ACTIVADA"
    
    Write-ColorText "🎉 ¡Campaña '$($Campaign.CampaignName)' para $($Campaign.ArtistName) está ACTIVA!" $Colors.Success
    Write-Host ""
    
    Write-ColorText "🎯 DASHBOARD DE CAMPAÑA:" $Colors.Info
    Write-ColorText "   • 📊 Analytics Principal: $BaseUrl/analytics/comprehensive" $Colors.Artist
    Write-ColorText "   • 🎵 Métricas Spotify: $BaseUrl/analytics/spotify" $Colors.Artist  
    Write-ColorText "   • 🎥 Analytics YouTube: $BaseUrl/analytics/youtube" $Colors.Artist
    Write-ColorText "   • 📱 Rendimiento Meta Ads: $BaseUrl/analytics/meta-ads" $Colors.Artist
    Write-ColorText "   • 📋 API Documentation: $BaseUrl/docs" $Colors.Artist
    Write-Host ""
    
    Write-ColorText "🚀 PRÓXIMOS PASOS PARA LA CAMPAÑA:" $Colors.Info
    Write-ColorText "   1. 🎵 Configura tus playlists objetivo en Spotify" $Colors.Artist
    Write-ColorText "   2. 🎥 Sube tu video musical a YouTube" $Colors.Artist  
    Write-ColorText "   3. 🎯 Crea campañas Meta Ads para promoción" $Colors.Artist
    Write-ColorText "   4. 📊 Monitorea métricas en tiempo real" $Colors.Artist
    Write-ColorText "   5. 🔄 Ajusta estrategia basada en data" $Colors.Artist
    Write-Host ""
    
    Write-ColorText "💡 TIPS PARA MAXIMIZAR RESULTADOS:" $Colors.Info
    Write-ColorText "   • 📈 Revisa analytics cada 24h durante lanzamiento" $Colors.Artist
    Write-ColorText "   • 🎯 Ajusta targeting Meta Ads según performance" $Colors.Artist
    Write-ColorText "   • 🎵 Busca nuevas playlists para pitch" $Colors.Artist
    Write-ColorText "   • 📱 Engaging con comentarios = mejor algoritmo" $Colors.Artist
    Write-Host ""
    
    Write-ColorText "🎤 ¡ÉXITO EN TU LANZAMIENTO, $($Campaign.ArtistName.ToUpper())! 🚀" $Colors.Success
}

# MAIN EXECUTION
function Main {
    Clear-Host
    
    # Artist campaign logo
    Write-ColorText @"
    🎵 ═════════════════════════════════════════════════════════════════ 🎵
                        TIKTOK ML ARTIST CAMPAIGN LAUNCHER
                      Specialized for Music Industry Success  
    🎵 ═════════════════════════════════════════════════════════════════ 🎵
"@ $Colors.Header
    
    Write-ColorText "`n🎤 Sistema especializado para lanzamientos musicales y campañas artísticas" $Colors.Info
    Write-ColorText "📊 Analytics integrados: Spotify + YouTube + Meta Ads + Landing Pages" $Colors.Info  
    Write-Host ""
    
    try {
        # Get campaign information
        $campaign = Get-CampaignInfo
        
        # Configure artist platforms
        $credentials = Get-ArtistCredentials $campaign.Scope
        
        # Create campaign environment  
        Create-CampaignEnvironment $campaign $credentials
        
        # Build and deploy (simplified for artist focus)
        Write-ColorText "🔨 Construyendo sistema de campaña..." $Colors.Info
        docker build -f Dockerfile.v4 -t "tiktok-ml-artist:$($campaign.ArtistName.ToLower().Replace(' ', '-'))" .
        
        Write-ColorText "🚀 Lanzando campaña..." $Colors.Info  
        docker run -d `
            --name "artist-campaign-$($campaign.ArtistName.ToLower().Replace(' ', '-'))" `
            -p "8000:8000" `
            --env-file .env `
            "tiktok-ml-artist:$($campaign.ArtistName.ToLower().Replace(' ', '-'))"
        
        # Wait for system
        Write-ColorText "⏳ Preparando dashboard de campaña..." $Colors.Info
        Start-Sleep -Seconds 30
        
        # Show campaign summary
        Show-CampaignSummary $campaign "http://localhost:8000"
        
    } catch {
        Write-ColorText "❌ Error en lanzamiento de campaña: $_" $Colors.Error
    }
    
    Read-Host "`n🎵 Presiona Enter para continuar..."
}

# Execute  
Main