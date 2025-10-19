## Pruebas locales rápidas (modo dummy)

Estos son los pasos exactos que usé en desarrollo para ejecutar la API FastAPI en modo dummy y correr los tests unitarios.

1) Crear y activar un virtualenv (Linux / bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Actualizar pip e instalar dependencias de desarrollo

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

3) Ejecutar la API FastAPI (modo dummy por defecto)

```bash
export DUMMY_MODE=true
uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8080 --reload
```

La app quedará accesible en `http://localhost:8080`.

4) Correr tests unitarios (desde la raíz del repo)

```bash
# Si pyproject tiene addopts que interfieren, usar un pytest.ini temporal
printf "[pytest]\n" > /tmp/pytest.ini
PYTHONPATH=. pytest -c /tmp/pytest.ini -q
```

5) Opcional: ejecutar con docker-compose (sin GPU)

```bash
cd docker
docker compose -f docker-compose.no-gpu.yml up --build
```

Notas:
- Para salir del modo dummy y probar integraciones reales, implementar/adaptar las factories en `ml_core/models/factory.py` o establecer las variables env `YOLO_SCREENSHOT_IMPL`, `ADB_CONTROLLER_IMPL`, etc., apuntando a implementaciones de producción.
