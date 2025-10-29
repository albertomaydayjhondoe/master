# Meta System V3.6 - ML Core & Meta Ads Optimizer (Rama promocion)

## Despliegue Railway
- El API de ML Core se despliega automáticamente en Railway usando FastAPI.
- Comando de inicio: `python -m ml_core.api.main`
- Healthcheck: `/health`
- Configuración en `railway.json`.

## Endpoints principales
- `/api/v1/meta_ads/optimize` (POST):
  - Optimización matemática de presupuesto y rentabilidad para campañas Meta Ads.
  - Input: métricas de campaña, parámetros de presupuesto, métricas ML preentrenadas.
  - Output: recomendaciones de gasto, early stop, asignación bayesiana, penalización por varianza, etc.

## Pipeline ML
- Código en `ml_core/optimizers/meta_ads_budget_optimizer.py`.
- Entrenamiento y validación continua soportados.
- Listo para integración con datasets COCO y Ultralytics.

## Tests automáticos
- Ubicación: `tests/unit/test_meta_ads_optimizer.py`
- Validan lógica matemática, endpoint y pipeline ML.
- Ejecutar con: `python -m pytest tests/unit/test_meta_ads_optimizer.py`

## Integración n8n y Meta Ads
- El endpoint está conectado al workflow orquestador vía webhook.
- Respuestas del optimizador pueden ser usadas para ajustar campañas en tiempo real.

## Notas de desarrollo
- El repo está en la rama `promocion` para pruebas y despliegue seguro.
- El archivo `__init__.py` está limpio para permitir entrenamiento real y uso de Ultralytics.
- El mandato matemático está documentado en `ml_core/mandatos/mandato_optimizacion_presupuesto.txt`.

## Variables de entorno recomendadas
- `API_KEY`: clave de API para proteger endpoints.
- `DUMMY_MODE`: debe estar en `false` para producción/entrenamiento real.
- `PORT`: puerto de despliegue (por defecto 8000).

## Entrenamiento con COCO/Ultralytics
- Preparar dataset COCO en la ruta esperada por Ultralytics.
- Entrenar modelos YOLOv8 con: `yolo task=detect mode=train model=yolov8n.pt data=path/to/coco.yaml epochs=100`.
- Integrar modelos entrenados en el pipeline ML para análisis audiovisual y optimización de campañas.

## Log de evolución (recursivo)
- 2025-10-29: Refactorización completa del pipeline ML y optimizador de Meta Ads en rama `promocion`.
- 2025-10-29: Integración de endpoint `/api/v1/meta_ads/optimize` con validación continua y tests automáticos.
- 2025-10-29: Conexión directa con workflows n8n y triggers webhook para automatización de campañas.
- 2025-10-29: Despliegue Railway listo para producción, healthcheck y variables de entorno documentadas.
- 2025-10-29: Eliminación de dummies y entorno preparado para entrenamiento real con COCO y Ultralytics.
- 2025-10-29: Mandato matemático de optimización documentado y versionado.
- 2025-10-29: Añadida sección de evolución y roadmap al README.
- 2025-10-29: Log de evolución recursivo implementado para trazabilidad total.

## Evolución y Roadmap

### Hitos alcanzados
- Refactorización completa del pipeline ML y optimizador de Meta Ads en rama `promocion`.
- Integración de endpoint `/api/v1/meta_ads/optimize` con validación continua y tests automáticos.
- Conexión directa con workflows n8n y triggers webhook para automatización de campañas.
- Despliegue Railway listo para producción, healthcheck y variables de entorno documentadas.
- Eliminación de dummies y entorno preparado para entrenamiento real con COCO y Ultralytics.
- Mandato matemático de optimización documentado y versionado.

### Próximos pasos sugeridos
- [ ] Integrar feedback real de campañas Meta Ads y YouTube para auto-retraining.
- [ ] Añadir dashboards avanzados de métricas y evolución de KPIs (Streamlit, Grafana).
- [ ] Implementar auto-retraining programado y logging de performance por versión de modelo.
- [ ] Desarrollar endpoints de análisis de outliers y alertas automáticas por desviación de métricas.
- [ ] Mejorar la integración con Spotify for Artists y reporting cross-plataforma.
- [ ] Documentar casos de uso reales y ejemplos de payloads para cada endpoint.
- [ ] Añadir tests de integración E2E y validación de outputs en workflows reales.

---

Para dudas o despliegues adicionales, revisar este README y los archivos de configuración del repo.
