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