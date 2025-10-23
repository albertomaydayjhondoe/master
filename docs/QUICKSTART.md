# Quickstart Guide - TikTok Viral ML System

Esta guía rápida te ayudará a poner en marcha el sistema en menos de 15 minutos.

## Prerequisites

- Python 3.11 o superior
- Git
- 4GB RAM mínimo
- Sistema operativo: Linux, macOS, o Windows con WSL

## Paso 1: Clonar el Repositorio

```bash
git clone <repository-url>
cd master
```

## Paso 2: Crear Entorno Virtual

```bash
# Crear virtualenv
python3.11 -m venv .venv

# Activar virtualenv
source .venv/bin/activate  # Linux/Mac
# O en Windows:
# .venv\Scripts\activate
```

## Paso 3: Instalar Dependencias (Modo Dummy)

```bash
# Solo dependencias básicas para modo dummy
pip install -r requirements-dummy.txt

# Dependencias de desarrollo (testing, linting)
pip install -r requirements-dev.txt
```

**Nota**: En modo dummy NO necesitas instalar PyTorch ni dependencias pesadas de ML.

## Paso 4: Configurar Variables de Entorno

```bash
# Crear archivo .env (opcional en dummy mode)
cat > .env << 'EOF'
DUMMY_MODE=true
ML_API_KEY=dummy_development_key
EOF
```

## Paso 5: Iniciar el Servicio ML API

```bash
# Activar modo dummy (ya es el default)
export DUMMY_MODE=true

# Iniciar FastAPI con hot-reload
uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

## Paso 6: Verificar Instalación

Abre otro terminal y prueba el API:

```bash
# Health check
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"healthy"}

# Ver documentación interactiva
# Abre en tu navegador: http://localhost:8000/docs
```

## Paso 7: Probar Endpoints

### Screenshot Analysis (Dummy)

```bash
# Crear imagen de prueba (cualquier imagen PNG/JPG)
curl -X POST "http://localhost:8000/api/v1/analyze_screenshot" \
  -H "X-API-Key: dummy_development_key" \
  -F "file=@/path/to/image.png"
```

Respuesta (dummy mode):
```json
{
  "detected_elements": [
    {
      "type": "like_button",
      "confidence": 0.95,
      "coordinates": {"x": 100, "y": 200, "width": 50, "height": 50}
    }
  ],
  "processing_time": 0.15,
  "screen_state": "normal",
  "recommendation": "safe_to_interact"
}
```

### Anomaly Detection (Dummy)

```bash
curl -X POST "http://localhost:8000/api/v1/detect_anomaly" \
  -H "X-API-Key: dummy_development_key" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "test_account_001",
    "recent_actions": ["like", "follow", "comment"],
    "context": {"session_duration": 1800}
  }'
```

### Posting Time Prediction (Dummy)

```bash
curl -X POST "http://localhost:8000/api/v1/predict_posting_time" \
  -H "X-API-Key: dummy_development_key" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "test_account_001",
    "timezone": "Europe/Madrid"
  }'
```

### Affinity Calculation (Dummy)

```bash
curl -X POST "http://localhost:8000/api/v1/calculate_affinity" \
  -H "X-API-Key: dummy_development_key" \
  -H "Content-Type: application/json" \
  -d '{
    "account_ids": ["acc_1", "acc_2", "acc_3"],
    "context": {"content_type": "dance"}
  }'
```

## Paso 8: Usar el Cliente Python

Crea un archivo `test_client.py`:

```python
from examples.ml_client import MLClient
import asyncio

async def main():
    async with MLClient() as client:
        # Detectar anomalías
        result = await client.detect_anomaly(
            account_id="test_account",
            recent_actions=["like", "follow", "comment"]
        )
        print("Anomaly detection:", result)
        
        # Predicción de momento para publicar
        timing = await client.predict_posting_time(
            account_id="test_account",
            timezone="Europe/Madrid"
        )
        print("\nPosting time:", timing)

if __name__ == "__main__":
    asyncio.run(main())
```

Ejecutar:
```bash
python test_client.py
```

## Paso 9: Ejecutar Tests (Opcional)

```bash
# Tests unitarios
PYTHONPATH=. pytest tests/unit/ -v

# Tests con coverage
PYTHONPATH=. pytest --cov=ml_core --cov=device_farm tests/unit/
```

## Paso 10: Explorar Documentación

### Documentación Interactiva
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Documentación del Proyecto
- `README.md` - Descripción general
- `SOCIAL_MEDIA_AUDIT.md` - Auditoría de referencias a redes sociales
- `SECURITY.md` - Políticas de seguridad
- `docs/api_integration.md` - Guía de integración del API
- `docs/PRODUCTION_MIGRATION.md` - Migración a producción
- `docs/MAINTENANCE.md` - Guía de mantenimiento

## Troubleshooting Común

### Problema: "Module not found"
```bash
# Asegurarse de estar en el virtualenv
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements-dummy.txt
```

### Problema: "Port already in use"
```bash
# Cambiar puerto
uvicorn ml_core.api.main:app --port 8001

# O matar proceso en puerto 8000
# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Problema: "Import errors en tests"
```bash
# Usar PYTHONPATH
PYTHONPATH=. pytest tests/unit/
```

## Próximos Pasos

### Para Desarrollo
1. ✅ Explorar código en `ml_core/` y `device_farm/`
2. ✅ Modificar respuestas dummy para simular escenarios
3. ✅ Añadir tests para nuevas features
4. ✅ Leer `.github/copilot-instructions.md` para arquitectura

### Para Testing
1. ✅ Probar todos los endpoints con diferentes inputs
2. ✅ Validar respuestas del API
3. ✅ Simular flujos de trabajo completos
4. ✅ Experimentar con el cliente Python

### Para Producción
1. ⚠️ Leer `docs/PRODUCTION_MIGRATION.md` **completo**
2. ⚠️ Obtener hardware necesario (GPU, dispositivos)
3. ⚠️ Entrenar modelos ML con datos reales
4. ⚠️ Configurar credenciales y servicios externos
5. ⚠️ Implementar factories de producción
6. ⚠️ Seguir checklist de seguridad en `SECURITY.md`

## Docker Compose (Alternativa)

Si prefieres usar Docker:

```bash
# Copiar ejemplo de .env
cp docker/.env.example docker/.env

# Iniciar servicios
docker compose -f docker/docker-compose.yml up -d

# Ver logs
docker compose logs -f

# Detener
docker compose down
```

**Nota**: Docker Compose incluye PostgreSQL, Grafana y n8n adicionales.

## Comandos Útiles

```bash
# Ver rutas y estructura
tree -L 3 -I '__pycache__|.git|.venv'

# Buscar TODOs en código
grep -r "TODO\|FIXME" --include="*.py" .

# Verificar sintaxis Python
python -m py_compile ml_core/api/main.py

# Formato de código (si tienes black instalado)
black ml_core/ device_farm/

# Type checking (si tienes mypy instalado)
mypy ml_core/
```

## Ayuda y Soporte

- **Issues**: Abre un issue en GitHub con detalles del problema
- **Documentación**: Consulta archivos en `/docs`
- **Ejemplos**: Revisa `/examples` para código de referencia
- **Tests**: Mira `/tests` para ver cómo usar cada componente

## Resumen de Comandos

```bash
# Setup inicial
git clone <repo>
cd master
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dummy.txt

# Iniciar servidor
export DUMMY_MODE=true
uvicorn ml_core.api.main:app --reload

# En otro terminal - test rápido
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Abrir en navegador
```

---

¡Listo! El sistema está corriendo en modo dummy y puedes empezar a desarrollar. 🚀

Para migrar a producción, consulta `docs/PRODUCTION_MIGRATION.md`.
