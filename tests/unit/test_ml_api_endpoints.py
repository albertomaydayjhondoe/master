import io
from fastapi.testclient import TestClient
from ml_core.api.main import app


client = TestClient(app)


def test_analyze_screenshot_endpoint():
    # Prepare a small dummy file
    files = {"file": ("img.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")}
    headers = {"X-API-Key": "dummy_development_key"}
    resp = client.post("/api/v1/analyze_screenshot", files=files, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "detected_elements" in data
    assert isinstance(data["detected_elements"], list)


def test_detect_anomaly_endpoint():
    payload = {"account_id": "dummy_account_1", "recent_actions": []}
    headers = {"X-API-Key": "dummy_development_key"}
    resp = client.post("/api/v1/detect_anomaly", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "anomaly_detected" in data


def test_predict_posting_time_endpoint():
    payload = {"account_id": "dummy_account_1"}
    headers = {"X-API-Key": "dummy_development_key"}
    resp = client.post("/api/v1/predict_posting_time", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "best_times" in data


def test_calculate_affinity_endpoint():
    payload = {"account_ids": ["a1", "a2", "a3"]}
    headers = {"X-API-Key": "dummy_development_key"}
    resp = client.post("/api/v1/calculate_affinity", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "affinity_scores" in data
