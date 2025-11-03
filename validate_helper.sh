#!/bin/bash

# 🎯 TikTok Viral ML System - Helper Script Validador Multi-Ramas
# ================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_colored() {
    echo -e "${1}${2}${NC}"
}

# Header
print_colored $PURPLE "🎯 TikTok Viral ML System - Validador Multi-Ramas Helper"
print_colored $PURPLE "========================================================="

# Ayuda
show_help() {
    print_colored $WHITE "\n🔧 COMANDOS DISPONIBLES:"
    echo ""
    print_colored $CYAN "📋 VALIDACIÓN BÁSICA:"
    echo "  ./validate_multibranch.py                    # Valida rama actual"
    echo "  ./validate_multibranch.py --branch tele      # Valida rama específica"
    echo "  ./validate_multibranch.py --dummy-mode       # Validación en modo dummy"
    echo ""
    print_colored $CYAN "🔄 VALIDACIÓN MÚLTIPLE:"
    echo "  ./validate_multibranch.py --all-branches     # Valida todas las ramas"
    echo "  ./validate_multibranch.py --compare          # Compara todas las ramas"
    echo "  ./validate_multibranch.py --compare --dummy-mode  # Comparación en dummy"
    echo ""
    print_colored $CYAN "🔧 AUTO-REPARACIÓN:"
    echo "  ./validate_multibranch.py --fix              # Auto-instala dependencias"
    echo "  ./validate_multibranch.py --branch tele --fix     # Repara rama específica"
    echo ""
    print_colored $CYAN "💾 REPORTES:"
    echo "  ./validate_multibranch.py --save report.json      # Guarda reporte en JSON"
    echo "  ./validate_multibranch.py --compare --save full_report.json"
    echo ""
    print_colored $CYAN "🎭 MODO SILENCIOSO:"
    echo "  ./validate_multibranch.py --quiet            # Solo resultados finales"
    echo ""
}

# Menu interactivo
show_menu() {
    print_colored $WHITE "\n🎯 SELECCIONA UNA OPCIÓN:"
    echo ""
    echo "1) 🎭 Validar rama actual (modo dummy - rápido)"
    echo "2) 🔍 Validar rama actual (modo producción - completo)"
    echo "3) 🔄 Comparar todas las ramas (modo dummy)"
    echo "4) 📊 Comparar todas las ramas (modo producción)"
    echo "5) 🔧 Auto-reparar rama actual"
    echo "6) 📋 Validar rama específica"
    echo "7) 💾 Generar reporte completo"
    echo "8) 📚 Ver ayuda completa"
    echo "9) ❌ Salir"
    echo ""
    print_colored $YELLOW "Elige una opción (1-9): "
}

# Función para detectar rama actual
get_current_branch() {
    git branch --show-current 2>/dev/null || echo "unknown"
}

# Función para validar rama específica
validate_specific_branch() {
    print_colored $CYAN "\n🌿 RAMAS DISPONIBLES:"
    echo "1) main (ML completo + Device Farm)"
    echo "2) meta (Meta Ads + GoLogin)"
    echo "3) tele (Telegram + Social Media)"
    echo "4) dummy (Testing mode)"
    echo ""
    print_colored $YELLOW "Selecciona rama (1-4): "
    read -r branch_choice
    
    case $branch_choice in
        1) selected_branch="main" ;;
        2) selected_branch="meta" ;;
        3) selected_branch="tele" ;;
        4) selected_branch="dummy" ;;
        *) 
            print_colored $RED "❌ Opción inválida"
            return 1
            ;;
    esac
    
    print_colored $BLUE "\n🔍 Validando rama: $selected_branch"
    python validate_multibranch.py --branch "$selected_branch"
}

# Loop principal
main_loop() {
    current_branch=$(get_current_branch)
    print_colored $BLUE "🌿 Rama actual: $current_branch"
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                print_colored $BLUE "\n🎭 Validando rama actual en modo dummy..."
                python validate_multibranch.py --dummy-mode
                ;;
            2)
                print_colored $BLUE "\n🔍 Validando rama actual en modo producción..."
                python validate_multibranch.py
                ;;
            3)
                print_colored $BLUE "\n🔄 Comparando todas las ramas (modo dummy)..."
                python validate_multibranch.py --compare --dummy-mode
                ;;
            4)
                print_colored $BLUE "\n📊 Comparando todas las ramas (modo producción)..."
                python validate_multibranch.py --compare
                ;;
            5)
                print_colored $BLUE "\n🔧 Auto-reparando rama actual..."
                python validate_multibranch.py --fix
                ;;
            6)
                validate_specific_branch
                ;;
            7)
                timestamp=$(date +"%Y%m%d_%H%M%S")
                report_file="validation_report_$timestamp.json"
                print_colored $BLUE "\n💾 Generando reporte completo..."
                python validate_multibranch.py --compare --save "$report_file"
                print_colored $GREEN "✅ Reporte guardado en: $report_file"
                ;;
            8)
                show_help
                ;;
            9)
                print_colored $GREEN "\n👋 ¡Hasta luego!"
                exit 0
                ;;
            *)
                print_colored $RED "❌ Opción inválida. Intenta de nuevo."
                ;;
        esac
        
        print_colored $YELLOW "\n⏎ Presiona Enter para continuar..."
        read -r
    done
}

# Verificar si el script de validación existe
if [ ! -f "validate_multibranch.py" ]; then
    print_colored $RED "❌ Error: validate_multibranch.py no encontrado"
    print_colored $YELLOW "   Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar argumentos de línea de comandos
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
elif [ "$1" = "--quick-dummy" ]; then
    print_colored $BLUE "🎭 Validación rápida en modo dummy..."
    python validate_multibranch.py --dummy-mode
    exit $?
elif [ "$1" = "--quick-compare" ]; then
    print_colored $BLUE "📊 Comparación rápida en modo dummy..."
    python validate_multibranch.py --compare --dummy-mode
    exit $?
elif [ "$1" = "--quick-fix" ]; then
    print_colored $BLUE "🔧 Auto-reparación rápida..."
    python validate_multibranch.py --fix --dummy-mode
    exit $?
fi

# Ejecutar menu interactivo si no hay argumentos
main_loop