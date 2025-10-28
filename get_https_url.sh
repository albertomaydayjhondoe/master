#!/bin/bash
# Script para obtener la URL HTTPS del dashboard en GitHub Codespaces

echo "🔍 Obteniendo URL HTTPS del dashboard..."
echo ""

# Intentar obtener el nombre del codespace
if [ -n "$CODESPACE_NAME" ]; then
    HTTPS_URL="https://${CODESPACE_NAME}-8501.app.github.dev"
    echo "✅ URL HTTPS del Dashboard:"
    echo "   $HTTPS_URL"
    echo ""
    echo "🌐 También disponible en:"
    echo "   http://localhost:8501 (local)"
    echo ""
    echo "📋 Copia esta URL para acceder desde cualquier navegador:"
    echo "   $HTTPS_URL"
else
    echo "⚠️  Variable CODESPACE_NAME no encontrada"
    echo "   Usa el panel PORTS de VS Code para obtener la URL"
    echo ""
    echo "🌐 URL Local disponible:"
    echo "   http://localhost:8501"
fi

echo ""
echo "💡 Para ver el panel de puertos en VS Code:"
echo "   1. Presiona Ctrl+Shift+` para abrir terminal"
echo "   2. Haz clic en la pestaña 'PORTS'"
echo "   3. Busca el puerto 8501"
echo "   4. La URL HTTPS aparecerá en 'Forwarded Address'"
