#!/bin/bash
# 🎵 VALIDADOR DE TOKENS - DISCOGRÁFICA ML
# ========================================
# Script para validar que los tokens configurados funcionan correctamente

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

ENV_FILE=".env"

echo -e "${PURPLE}🔍 VALIDADOR DE TOKENS - DISCOGRÁFICA ML${NC}"
echo -e "${PURPLE}=======================================${NC}"
echo ""

# Verificar que existe archivo de configuración
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ No se encontró archivo .env${NC}"
    echo -e "${YELLOW}   Ejecuta primero: ./setup_production_tokens.sh${NC}"
    exit 1
fi

# Cargar variables de entorno
source "$ENV_FILE"

echo -e "${BLUE}📋 Validando tokens configurados...${NC}"
echo ""

# Función para validar token
validate_token() {
    local token_name="$1"
    local token_value="$2"
    local validation_command="$3"
    
    echo -n "   🔍 ${token_name}: "
    
    if [ -z "$token_value" ]; then
        echo -e "${RED}❌ No configurado${NC}"
        return 1
    fi
    
    if [ ! -z "$validation_command" ]; then
        if eval "$validation_command" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Válido${NC}"
            return 0
        else
            echo -e "${RED}❌ Token inválido o sin acceso${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Configurado (no validado)${NC}"
        return 0
    fi
}

# Contadores
total_tokens=0
valid_tokens=0

# 1. META ADS VALIDATION
echo -e "${PURPLE}🎯 META ADS TOKENS${NC}"
((total_tokens++))
if validate_token "META_ACCESS_TOKEN" "$META_ACCESS_TOKEN" "curl -s 'https://graph.facebook.com/me?access_token=$META_ACCESS_TOKEN' | grep -q 'id'"; then
    ((valid_tokens++))
fi

((total_tokens++))
if validate_token "META_APP_ID" "$META_APP_ID" "[ ${#META_APP_ID} -ge 15 ]"; then
    ((valid_tokens++))
fi

((total_tokens++))
if validate_token "META_APP_SECRET" "$META_APP_SECRET" "[ ${#META_APP_SECRET} -eq 32 ]"; then
    ((valid_tokens++))
fi

echo ""

# 2. YOUTUBE VALIDATION
echo -e "${PURPLE}📺 YOUTUBE TOKENS${NC}"
((total_tokens++))
if validate_token "YOUTUBE_CLIENT_ID" "$YOUTUBE_CLIENT_ID" "echo '$YOUTUBE_CLIENT_ID' | grep -q 'googleusercontent.com'"; then
    ((valid_tokens++))
fi

((total_tokens++))
if validate_token "YOUTUBE_CLIENT_SECRET" "$YOUTUBE_CLIENT_SECRET" "echo '$YOUTUBE_CLIENT_SECRET' | grep -q '^GOCSPX-'"; then
    ((valid_tokens++))
fi

((total_tokens++))
if validate_token "YOUTUBE_REFRESH_TOKEN" "$YOUTUBE_REFRESH_TOKEN" "echo '$YOUTUBE_REFRESH_TOKEN' | grep -q '^1//'"; then
    ((valid_tokens++))
fi

echo ""

# 3. TELEGRAM VALIDATION
echo -e "${PURPLE}💬 TELEGRAM TOKENS${NC}"
((total_tokens++))
if validate_token "TELEGRAM_BOT_TOKEN" "$TELEGRAM_BOT_TOKEN" "curl -s 'https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe' | grep -q '\"ok\":true'"; then
    ((valid_tokens++))
fi

((total_tokens++))
if validate_token "TELEGRAM_API_ID" "$TELEGRAM_API_ID" "[ ${#TELEGRAM_API_ID} -ge 7 ]"; then
    ((valid_tokens++))
fi

((total_tokens++))
if validate_token "TELEGRAM_API_HASH" "$TELEGRAM_API_HASH" "[ ${#TELEGRAM_API_HASH} -eq 32 ]"; then
    ((valid_tokens++))
fi

echo ""

# 4. SISTEMA VALIDATION
echo -e "${PURPLE}⚙️  CONFIGURACIÓN SISTEMA${NC}"
echo -n "   🔍 DUMMY_MODE: "
if [ "$DUMMY_MODE" = "false" ]; then
    echo -e "${GREEN}✅ Producción activada${NC}"
    ((valid_tokens++))
else
    echo -e "${YELLOW}⚠️  Modo dummy activo${NC}"
fi
((total_tokens++))

echo -n "   🔍 ULTRALYTICS: "
if python3 -c "from ultralytics import YOLO; print('OK')" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Modelos disponibles${NC}"
    ((valid_tokens++))
else
    echo -e "${RED}❌ Ultralytics no disponible${NC}"
fi
((total_tokens++))

echo -n "   🔍 LONGCAT-VIDEO: "
if python3 -c "from ml_core.video_generation import create_video_generator; print('OK')" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Generador de video disponible${NC}"
    ((valid_tokens++))
else
    echo -e "${RED}❌ LongCat-Video no disponible${NC}"
fi
((total_tokens++))

echo -n "   🔍 PYTORCH: "
if python3 -c "import torch; print('CUDA:', torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
    echo -e "${GREEN}✅ GPU aceleración disponible${NC}"
    ((valid_tokens++))
elif python3 -c "import torch; print('OK')" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Solo CPU (generación lenta)${NC}"
    ((valid_tokens++))
else
    echo -e "${RED}❌ PyTorch no disponible${NC}"
fi
((total_tokens++))

echo ""

# RESUMEN FINAL
echo -e "${PURPLE}📊 RESUMEN DE VALIDACIÓN${NC}"
echo -e "${PURPLE}========================${NC}"
echo -e "${BLUE}   Tokens válidos: ${valid_tokens}/${total_tokens}${NC}"

percentage=$((valid_tokens * 100 / total_tokens))
echo -e "${BLUE}   Porcentaje: ${percentage}%${NC}"

if [ $percentage -ge 90 ]; then
    echo -e "${GREEN}🎉 SISTEMA LISTO PARA PRODUCCIÓN${NC}"
    echo ""
    echo -e "${GREEN}✅ Puedes iniciar campañas virales:${NC}"
    echo -e "${BLUE}   ./start_trap_production.py${NC}"
elif [ $percentage -ge 70 ]; then
    echo -e "${YELLOW}⚠️  SISTEMA PARCIALMENTE LISTO${NC}"
    echo ""
    echo -e "${YELLOW}   Algunas funcionalidades pueden no estar disponibles${NC}"
    echo -e "${BLUE}   Revisa los tokens marcados como inválidos${NC}"
else
    echo -e "${RED}❌ SISTEMA NO LISTO PARA PRODUCCIÓN${NC}"
    echo ""
    echo -e "${RED}   Demasiados tokens inválidos o faltantes${NC}"
    echo -e "${BLUE}   Ejecuta: ./setup_production_tokens.sh${NC}"
fi

echo ""
echo -e "${BLUE}📋 Para ver logs detallados:${NC}"
echo -e "${BLUE}   tail -f logs/*.log${NC}"
echo ""