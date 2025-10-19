# TikTok Viral ML System (Dummy Mode)

Este repositorio implementa una plataforma de automatización TikTok potenciada por
Modelos de Visión (YOLOv8) y reglas ML. Está pensada para desarrollo local y pruebas
mediante un "modo dummy" que emula hardware y servicios externos.

Este README explica cómo empezar rápido en modo dummy y cómo migrar a producción.

## Estado actual

- El repositorio corre en "dummy mode" por defecto (`DUMMY_MODE=true`).
- Contiene stubs para: ML (YOLO), Device Farm (ADB/Appium) y GoLogin (navegadores).
- `docker/` contiene una configuración `docker-compose.yml` orientada a pruebas locales.

## Requisitos

- Python 3.11+
- Docker & docker-compose (opcional para levantar todos los servicios)
- Git

## Quickstart (modo virtualenv)

1. Crear y activar un virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias (modo dummy):

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. Arrancar el servicio ML (FastAPI) localmente:

```bash
export DUMMY_MODE=true
uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000 --reload
```

4. Probar el endpoint de screenshot (ejemplo usando curl):

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze_screenshot" -H "X-API-Key: dummy_development_key" -F "file=@/path/to/sample.png"
```

## Quickstart (Docker Compose)

Nota: la configuración actual de `docker/docker-compose.yml` asume entornos de
prueba. Revisa `docker/.env.example` y copia como `.env` antes de arrancar.

```bash
cp docker/.env.example docker/.env
# Construir y levantar servicios
docker compose -f docker/docker-compose.yml up --build
```

## Cómo salir del modo dummy (pasos resumidos)

1. Implementa las ramas de producción en las fábricas:
	- `ml_core/models/factory.py`
	- `device_farm/controllers/factory.py`
	Alternativamente, puedes implementar una clase de producción y apuntar a ella
	con una variable de entorno (`YOLO_SCREENSHOT_IMPL`, `ADB_CONTROLLER_IMPL`,
	etc.). El helper `scripts/import_by_path.py` permite importar por ruta puntuada.
	Usa `scripts/scaffold_prod_factories.py` para generar plantillas de fábrica.
2. Provee pesos y configuración real en `config/ml/model_config.yaml`.
3. Asegura credenciales y variables de entorno necesarias (GoLogin, proxies, Appium).
4. Ejecuta los tests de integración y smoke tests.
5. Cambia `DUMMY_MODE=false` y reinicia los servicios.

## Estructura importante

- `ml_core/api/` - FastAPI app y endpoints
- `ml_core/models/` - surface para los modelos (stubs en dummy mode)
- `device_farm/controllers/` - ADB/Appium dummy y manager
- `gologin_automation/` - stubs para GoLogin (por implementar)
- `orchestration/n8n_workflows/` - workflows (stubs)
- `docker/` - compose y Dockerfiles

## Tests

Ejecuta tests unitarios (recomendado con `PYTHONPATH=.`):

```bash
PYTHONPATH=. pytest -q
```

Si quieres ejecutar un test puntual y evitar `pyproject` addopts:

```bash
printf "[pytest]\n" > /tmp/pytest.ini
PYTHONPATH=. pytest -c /tmp/pytest.ini -q tests/unit/test_device_manager.py
```

## Documentación y siguientes pasos

- `CHANGELOG.md` contiene el historial de cambios.
- Usa `.github/copilot-instructions.md` para orientación interna del agente.

Si quieres, puedo:
- Implementar la parte dummy de GoLogin (siguiente tarea),
- Añadir pruebas unitarias para los endpoints ML (requieres instalar `fastapi`/`httpx`),
- Crear workflows n8n dummy y validador.

¡Dime qué prefieres y continúo!
