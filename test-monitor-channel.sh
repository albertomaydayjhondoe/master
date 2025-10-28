#!/bin/bash

# ═══════════════════════════════════════════════════════════
# 🧪 TEST: Monitor-Channel Mode
# ═══════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   🧪 Testing Monitor-Channel Mode                     ║"
echo "║   Sistema de Auto-Viralización de Canal              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════
# TEST 1: Monitor con Auto-Launch ENABLED
# ═══════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Monitor con Auto-Launch ENABLED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuración:"
echo "  - Canal: UC_TEST_CHANNEL_123"
echo "  - Auto-launch: ON"
echo "  - Threshold: 0.70"
echo "  - Max campañas/día: 2"
echo "  - Budget: \$50/video"
echo "  - Check interval: 6h"
echo ""
echo "Ejecutando..."
echo ""

python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_TEST_CHANNEL_123" \
  --auto-launch \
  --virality-threshold 0.70 \
  --max-campaigns-per-day 2 \
  --paid-budget 50.0 \
  --check-interval 6

echo ""
echo "✅ TEST 1 COMPLETADO"
echo ""

# ═══════════════════════════════════════════════════════════
# TEST 2: Monitor con Auto-Launch DISABLED (solo notifica)
# ═══════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Monitor con Auto-Launch DISABLED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuración:"
echo "  - Canal: UC_TEST_CHANNEL_456"
echo "  - Auto-launch: OFF (solo notifica)"
echo "  - Threshold: 0.65"
echo "  - Max campañas/día: 3"
echo ""
echo "Ejecutando..."
echo ""

python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_TEST_CHANNEL_456" \
  --virality-threshold 0.65 \
  --max-campaigns-per-day 3 \
  --paid-budget 30.0 \
  --check-interval 4

echo ""
echo "✅ TEST 2 COMPLETADO"
echo ""

# ═══════════════════════════════════════════════════════════
# TEST 3: Launch Individual (para comparar)
# ═══════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Launch Individual (comparación)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuración:"
echo "  - Video: test_video.mp4"
echo "  - Campaña: Test Single 2025"
echo "  - Artista: Test Artist"
echo "  - Budget: \$50"
echo ""
echo "Ejecutando..."
echo ""

python unified_system_v3.py \
  --mode launch \
  --video "/data/videos/test_video.mp4" \
  --campaign-name "Test Single 2025" \
  --artist-name "Test Artist" \
  --genre "Trap" \
  --paid-budget 50.0

echo ""
echo "✅ TEST 3 COMPLETADO"
echo ""

# ═══════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   ✅ TODOS LOS TESTS COMPLETADOS                      ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "Resultados:"
echo "  ✅ TEST 1: Monitor auto-launch"
echo "  ✅ TEST 2: Monitor solo notificación"
echo "  ✅ TEST 3: Launch individual"
echo ""
echo "Próximos pasos:"
echo "  1. Revisa logs: logs/unified_system_v3.log"
echo "  2. Verifica analytics: http://localhost:8501"
echo "  3. Monitorea Grafana: http://localhost:3000"
echo ""
echo "Documentación:"
echo "  - docs/MONITOR_CHANNEL_MODE.md"
echo "  - QUICKSTART_GUIDE.md"
echo ""
