# 🚀 Sistema ML Artístico Unificado

## ¿Qué incluye?
- **API ML (FastAPI/Uvicorn):** Predicciones, recomendaciones y análisis avanzados para campañas artísticas.
- **Dashboard interactivo (Streamlit):** Interfaz web moderna para chat, visualización y administración, accesible desde cualquier navegador.
- **Device Farm & Meta Ads:** Automatización multiplataforma y gestión de campañas.
- **YOLOv8 listo para inferencia:** Usa yolov8m.pt sin necesidad de COCO, pero preparado para entrenar cuando quieras.
- **Descarga automática de COCO:** El dataset se descarga solo durante el build (puedes desactivarlo si lo prefieres).
- **Cross-platform:** Imagen Docker compatible con Linux amd64 y arm64, lista para Railway, cloud o tu propio servidor.
- **Despliegue CI/CD:** Push a GitHub → build multi-arquitectura → imagen en Docker Hub → despliegue automático en Railway.

## ¿Cómo lo presumes?
- “Mi sistema ML artístico tiene API, dashboard web y automatización, todo en una sola imagen Docker, multiplataforma y con CI/CD real.”
- “El dashboard Streamlit es 100% interactivo y personalizable, ¡y lo puedes ver en producción en Railway!”
- “¿Quieres entrenar con COCO? Solo tienes que activar una línea, y el sistema se adapta solo.”

## Comandos de uso rápido

```bash
# Build local (requiere Docker y recursos)
docker build -f docker/Dockerfile.unified-railway -t agora90/artista-dashboard:latest .

# Push manual a Docker Hub
docker push agora90/artista-dashboard:latest

# Despliegue en Railway: usa la imagen agora90/artista-dashboard:latest
```

## Acceso
- Dashboard: `https://<tu-proyecto>.up.railway.app`
- API Swagger: `https://<tu-proyecto>.up.railway.app/docs`

---

¡Listo para presumir y desplegar donde quieras!
