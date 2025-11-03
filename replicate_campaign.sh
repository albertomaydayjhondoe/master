#!/bin/bash

# 🎵 REPLICADOR DE CAMPAÑAS - DISCOGRÁFICA ML SYSTEM
# ==================================================
# Script para replicar el molde base en campañas específicas

echo "🎵 REPLICADOR DE CAMPAÑAS MUSICALES"
echo "==================================="
echo ""

# Configuración
MOLDE_BASE="discografica-ml-system"
TEMPLATE_REPO="https://github.com/albertomaydayjhondoe/discografica-ml-system.git"

# Función para crear nueva campaña
create_campaign_repo() {
    local campaign_name="$1"
    local genre="$2"
    local artist="$3"
    
    echo "🚀 Creando campaña: $campaign_name"
    echo "📋 Género: $genre"
    echo "🎤 Artista: $artist"
    echo ""
    
    # Crear directorio de campaña
    if [[ -d "$campaign_name" ]]; then
        echo "⚠️  Directorio $campaign_name ya existe"
        read -p "¿Sobrescribir? (y/N): " confirm
        if [[ $confirm != "y" && $confirm != "Y" ]]; then
            echo "❌ Operación cancelada"
            return 1
        fi
        rm -rf "$campaign_name"
    fi
    
    # Clonar molde base
    echo "📥 Clonando molde base..."
    git clone "$TEMPLATE_REPO" "$campaign_name"
    cd "$campaign_name"
    
    # Limpiar historia git
    rm -rf .git
    git init
    
    # Personalizar para la campaña
    echo "🎨 Personalizando campaña..."
    
    # Actualizar README principal
    sed -i "s/DISCOGRÁFICA ML SYSTEM - UNIVERSAL TEMPLATE/CAMPAÑA $campaign_name - $genre/g" README.md
    sed -i "s/Molde universal/Campaña específica para $artist/g" README.md
    
    # Crear configuración específica de campaña
    cat > "campaign_config.json" << EOF
{
    "campaign_name": "$campaign_name",
    "genre": "$genre",
    "artist": "$artist",
    "created_at": "$(date -Iseconds)",
    "status": "initialized",
    "molde_version": "1.0.0"
}
EOF
    
    # Crear script de inicio personalizado
    cat > "start_campaign.sh" << EOF
#!/bin/bash
echo "🎵 LANZANDO CAMPAÑA: $campaign_name"
echo "🎤 Artista: $artist"
echo "🎼 Género: $genre"
echo ""

# Configurar variables específicas
export CAMPAIGN_NAME="$campaign_name"
export ARTIST_NAME="$artist"
export MUSIC_GENRE="$genre"

# Ejecutar inicio general
./start_discografica_ml.sh
EOF
    
    chmod +x "start_campaign.sh"
    
    # Configurar git para nueva campaña
    git add .
    git commit -m "🎵 CAMPAÑA INICIAL: $campaign_name

🎤 Artista: $artist
🎼 Género: $genre
📅 Fecha: $(date -Iseconds)

Campaña generada desde molde universal discográfica-ml-system
Lista para configuración de tokens y lanzamiento."
    
    echo ""
    echo "✅ CAMPAÑA CREADA EXITOSAMENTE"
    echo "================================"
    echo "📁 Directorio: $campaign_name/"
    echo "🎵 Archivo: campaign_config.json"
    echo "🚀 Launcher: start_campaign.sh"
    echo ""
    echo "📋 PRÓXIMOS PASOS:"
    echo "1. cd $campaign_name"
    echo "2. ./setup_production_tokens.sh"
    echo "3. python config_artist_generator.py"
    echo "4. ./start_campaign.sh"
    echo ""
    echo "🎵 ¡CAMPAÑA LISTA PARA CONFIGURAR! 🚀"
    
    cd ..
}

# Función interactiva
interactive_campaign_creation() {
    echo "🎯 CREACIÓN INTERACTIVA DE CAMPAÑA"
    echo "=================================="
    echo ""
    
    # Solicitar datos de campaña
    read -p "📝 Nombre de la campaña: " campaign_name
    if [[ -z "$campaign_name" ]]; then
        echo "❌ Nombre de campaña requerido"
        return 1
    fi
    
    # Mostrar géneros disponibles
    echo ""
    echo "🎼 Géneros disponibles:"
    echo "1. trap"
    echo "2. reggaeton"
    echo "3. pop"
    echo "4. rock"
    echo "5. bachata"
    echo "6. electronic"
    echo "7. salsa"
    echo "8. jazz"
    
    read -p "🎯 Selecciona género (1-8): " genre_num
    
    case $genre_num in
        1) genre="trap" ;;
        2) genre="reggaeton" ;;
        3) genre="pop" ;;  
        4) genre="rock" ;;
        5) genre="bachata" ;;
        6) genre="electronic" ;;
        7) genre="salsa" ;;
        8) genre="jazz" ;;
        *) 
            echo "❌ Selección inválida"
            return 1 
        ;;
    esac
    
    read -p "🎤 Nombre del artista: " artist_name
    if [[ -z "$artist_name" ]]; then
        echo "❌ Nombre del artista requerido"
        return 1
    fi
    
    # Crear campaña
    create_campaign_repo "$campaign_name" "$genre" "$artist_name"
}

# Función para mostrar ayuda
show_help() {
    echo "🎵 REPLICADOR DE CAMPAÑAS - AYUDA"
    echo "================================"
    echo ""
    echo "USAGE:"
    echo "  $0 [comando] [argumentos]"
    echo ""
    echo "COMANDOS:"
    echo "  interactive    - Modo interactivo para crear campaña"
    echo "  create <name> <genre> <artist> - Crear campaña directamente"
    echo "  list-genres    - Mostrar géneros disponibles"
    echo "  help           - Mostrar esta ayuda"
    echo ""
    echo "EJEMPLOS:"
    echo "  $0 interactive"
    echo "  $0 create campaña-trap-2024 trap \"MC Trapero\""
    echo "  $0 list-genres"
    echo ""
}

# Función para listar géneros
list_genres() {
    echo "🎼 GÉNEROS DISPONIBLES EN EL MOLDE"
    echo "=================================="
    echo ""
    echo "1. 🎤 trap        - Música urbana con beats pesados"
    echo "2. 🎵 reggaeton   - Música latina con ritmo pegajoso"  
    echo "3. 🎶 pop         - Música popular mainstream"
    echo "4. 🎸 rock        - Música rock con instrumentos en vivo"
    echo "5. 💕 bachata     - Música romántica latina"
    echo "6. 🎧 electronic  - Música electrónica para festivales"
    echo "7. 💃 salsa       - Música latina bailable tradicional"
    echo "8. 🎷 jazz        - Música sofisticada con improvisación"
    echo ""
}

# Procesamiento de argumentos
case "${1:-interactive}" in
    "interactive")
        interactive_campaign_creation
        ;;
    "create")
        if [[ $# -lt 4 ]]; then
            echo "❌ Uso: $0 create <nombre> <género> <artista>"
            exit 1
        fi
        create_campaign_repo "$2" "$3" "$4"
        ;;
    "list-genres")
        list_genres
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Comando desconocido: $1"
        show_help
        exit 1
        ;;
esac