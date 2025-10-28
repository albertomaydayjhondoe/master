#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# download-models.sh - Download YOLOv8 Models for ML Core
# ═══════════════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════"
echo "  🤖 DESCARGANDO MODELOS YOLOV8 - Ultralytics"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Create directory
mkdir -p data/models
cd data/models

# YOLOv8n (lightweight, 6.2 MB)
if [ ! -f yolov8n_screenshot.pt ]; then
    echo -e "${BLUE}Descargando YOLOv8n (6.2 MB)...${NC}"
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
    mv yolov8n.pt yolov8n_screenshot.pt
    echo -e "${GREEN}✅ yolov8n_screenshot.pt descargado${NC}"
else
    echo -e "${YELLOW}⏭️  yolov8n_screenshot.pt ya existe${NC}"
fi

# YOLOv8s (medium, 21.5 MB)
if [ ! -f yolov8s_video.pt ]; then
    echo -e "${BLUE}Descargando YOLOv8s (21.5 MB)...${NC}"
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
    mv yolov8s.pt yolov8s_video.pt
    echo -e "${GREEN}✅ yolov8s_video.pt descargado${NC}"
else
    echo -e "${YELLOW}⏭️  yolov8s_video.pt ya existe${NC}"
fi

# YOLOv8m (advanced, 49.7 MB)
if [ ! -f yolov8m_detection.pt ]; then
    echo -e "${BLUE}Descargando YOLOv8m (49.7 MB)...${NC}"
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
    mv yolov8m.pt yolov8m_detection.pt
    echo -e "${GREEN}✅ yolov8m_detection.pt descargado${NC}"
else
    echo -e "${YELLOW}⏭️  yolov8m_detection.pt ya existe${NC}"
fi

cd ../..

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ MODELOS YOLOV8 DESCARGADOS CORRECTAMENTE${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Modelos en: data/models/"
ls -lh data/models/*.pt
echo ""
