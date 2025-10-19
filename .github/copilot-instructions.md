# AI Agent Instructions

This document provides key information to help AI coding agents effectively work with this TikTok viral ML system codebase.

## System Architecture Overview

This is a sophisticated ML-powered TikTok automation system with several key components:

1. **ML Core** (`ml_core/`)
   - FastAPI service with endpoints for screenshot analysis, anomaly detection, and content optimization
   - Custom YOLOv8 models for visual analysis
   - Automated retraining pipeline for continuous model improvement

2. **Device Farm** (`device_farm/`)
   - Controls 10 physical devices via ADB/Appium
   - ML-driven action patterns for authentic engagement
   - Continuous monitoring for anomalies/shadowbans

3. **GoLogin Automation** (`gologin_automation/`)
   - Manages 30 browser profiles for web automation
   - ML-guided browsing patterns
   - Integrated anomaly detection

4. **Orchestration** (`orchestration/`)
   - n8n workflows coordinate all system components
   - ML-based decision engine for engagement
   - Cross-engagement scheduling

## Key Workflows

### Development Environment

1. **Initial Setup**
```bash
# Set up core components
./scripts/setup/setup_ml_environment.sh
./scripts/setup/setup_gologin.sh
./scripts/setup/setup_n8n.sh
./scripts/setup/setup_database.sh
```

2. **ML Development**
- Model training notebooks in `notebooks/training/`
- Automated retraining via `ml_core/training/auto_retrain.py`
- Model checkpoints stored in `data/models/`

3. **Testing**
```bash
# Run test suites
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

## Project Conventions

1. **ML Model Management**
- Production models in `data/models/production/`
- Checkpoints in `data/models/checkpoints/`
- Model configs in `config/ml/*.yaml`

2. **Configuration**
- Environment variables in `config/secrets/.env`
- Account configs in `config/accounts/*.json`
- ML configs in `config/ml/*.yaml`

3. **Monitoring**
- Grafana dashboards in `monitoring/dashboards/grafana/`
- Alert configs in `config/automation/alert_thresholds.json`
- Metrics tracked in `database/models/metric.py`

## Integration Points

1. **ML API** (`ml_core/api/`)
- Screenshot Analysis: `POST /analyze_screenshot`
- Anomaly Detection: `POST /detect_anomaly`
- Posting Time Prediction: `POST /predict_posting_time`
- Affinity Calculation: `POST /calculate_affinity`

2. **n8n Webhooks** (`orchestration/n8n_workflows/`)
- Main orchestrator: `main_orchestrator.json`
- ML decision engine: `ml_decision_engine.json`
- Device/GoLogin triggers: `device_farm_trigger.json`, `gologin_trigger.json`

3. **Database Models** (`database/models/`)
- Account state tracking
- ML predictions logging
- Metrics aggregation

## Critical Files

- `ml_core/api/main.py` - Core ML service entrypoint
- `device_farm/controllers/device_manager.py` - Device orchestration
- `orchestration/n8n_workflows/main_orchestrator.json` - System coordination
- `monitoring/health/account_health.py` - Account monitoring
- `config/ml/model_config.yaml` - ML configuration

## Common Patterns

1. **ML-Driven Actions**
```python
# Pattern found in device_farm/actions/ml_driven_actions.py
async def execute_ml_guided_action(session, context):
    prediction = await ml_client.predict_next_action(context)
    await human_patterns.apply_delay(prediction.confidence)
    return await tiktok_actions.execute(prediction.action)
```

2. **Anomaly Detection**
```python
# Pattern found in monitoring/health/shadowban_detector.py
async def check_account_health(account_id):
    screenshots = await screenshot_monitor.get_recent()
    predictions = await ml_client.detect_anomaly(screenshots)
    if predictions.is_shadowbanned:
        await alert_manager.raise_alert(account_id, "shadowban")
```

---

This is a living document that should be updated as:
1. New ML models or features are added
2. System architecture evolves
3. Integration points change
4. Monitoring patterns are refined