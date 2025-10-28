#!/bin/bash
"""
Get Public URL for Streamlit Dashboard

Script para obtener la URL pública del dashboard de Streamlit en GitHub Codespaces
"""

echo "🌐 Dashboard URL Generator"
echo "========================="

# Verificar si Streamlit está ejecutándose
if ! pgrep -f "streamlit" > /dev/null; then
    echo "❌ Streamlit no está ejecutándose"
    echo "💡 Iniciando Streamlit..."
    cd /workspaces/master
    streamlit run scripts/documentation_dashboard.py --server.port=8501 &
    sleep 5
fi

echo "✅ Streamlit está ejecutándose en el puerto 8501"
echo ""

# Obtener información del Codespace
CODESPACE_NAME="${CODESPACE_NAME:-unknown}"
GITHUB_USER="${GITHUB_USER:-albertomaydayjhondoe}"

echo "📋 Información del Codespace:"
echo "• Nombre: ${CODESPACE_NAME}"
echo "• Usuario: ${GITHUB_USER}"
echo "• Puerto: 8501"
echo ""

echo "🔗 URLs de acceso:"
echo "• Local: http://localhost:8501"
echo "• Codespace: https://${CODESPACE_NAME}-8501.app.github.dev"
echo ""

echo "📱 Para hacer público el dashboard:"
echo "1. Abre la pestaña 'PORTS' en VS Code (parte inferior)"
echo "2. Encuentra el puerto 8501"
echo "3. Cambia 'Private' a 'Public' en la columna Visibility"
echo "4. Copia la URL generada"
echo ""

echo "🚀 Alternativa rápida:"
echo "• Presiona Ctrl+Shift+\` para abrir terminal"
echo "• Ejecuta: gh codespace ports --codespace=\$CODESPACE_NAME"
echo ""

# Intentar abrir automáticamente
echo "🌐 Intentando abrir dashboard..."
if command -v gh &> /dev/null; then
    echo "• GitHub CLI disponible - configurando port forwarding..."
    gh codespace ports visibility 8501:public || echo "ℹ️  Configura manualmente desde VS Code"
else
    echo "• Usa VS Code para configurar el port forwarding"
fi

echo ""
echo "✨ Dashboard Features:"
echo "• 🏠 Home: Métricas y overview del sistema"
echo "• 🔍 Search: Búsqueda inteligente en documentación" 
echo "• 📖 Browse: Navegación completa de documentos"
echo "• 📊 Analytics: Métricas de uso y trends"
echo "• ⚙️ Admin: Panel de administración del sistema"
echo ""
echo "🎉 ¡Disfruta explorando tu Documentation Dashboard!"