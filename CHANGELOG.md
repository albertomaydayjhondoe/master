# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-19

### Added

### [0.1.1] - 2025-10-19

### Added
- ML Core dummy implementation with FastAPI
	- Screenshot analysis endpoint with simulated responses
	- Anomaly detection with random patterns
	- Posting time predictor with realistic dummy data
	- Affinity calculator with simulated engagement metrics
- Basic API security with dummy key authentication
- CORS middleware configuration

### [0.1.2] - 2025-10-19

### Added
- Model integration stubs under `ml_core/models/`:
	- `YoloScreenshotDetector` (dummy)
	- `YoloVideoDetector` (dummy)
	- `AffinityModel` (dummy)
	- `AnomalyDetector` (dummy)
- Updated `screenshot_analysis` endpoint to use the `YoloScreenshotDetector` wrapper

### [0.1.3] - 2025-10-19

### Added
- Device Farm dummy controllers under `device_farm/controllers/`:
	- `adb_controller.py` (simulated device actions)
	- `device_manager.py` (orchestration shim)
- Unit test for device manager in `tests/unit/test_device_manager.py`

### [0.1.4] - 2025-10-19

### Added
- `config/app_settings.py` - central switch for `DUMMY_MODE`
- Factories:
	- `ml_core/models/factory.py` (model implementation factory)
	- `device_farm/controllers/factory.py` (ADB controller factory)
- `screenshot_analysis` and `device_manager` updated to use factories so the
	repo runs fully in dummy mode by default. To exit dummy mode implement the
	production branches in the factories and set `DUMMY_MODE=false`.

### [0.1.5] - 2025-10-19

### Added
- n8n workflow stubs under `orchestration/n8n_workflows/`:
	- `main_orchestrator.json`
	- `device_farm_trigger.json`
	- `ml_decision_engine.json`
- `orchestration/scripts/workflow_validator.py` to validate workflow JSON
- Unit tests for the validator in `tests/unit/test_workflow_validator.py`

### [0.1.6] - 2025-10-19

### Added
- `scripts/import_by_path.py` - helper to import classes via dotted path
- `scripts/scaffold_prod_factories.py` - scaffolding to generate production factory templates
- Factories updated to support dotted-path overrides via environment variables
	(e.g. `YOLO_SCREENSHOT_IMPL`, `ADB_CONTROLLER_IMPL`) so migrating out of
	dummy mode can be done by implementing classes and setting env vars.