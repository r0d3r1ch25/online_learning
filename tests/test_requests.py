import pytest
from fastapi.testclient import TestClient
from ml_api.service import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"

def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "model_version" in data

def test_train():
    payload = {
        "series_id": "store_123_sales",
        "observations": [
            {"timestamp": "2025-08-26", "value": 125},
            {"timestamp": "2025-08-27", "value": 130}
        ]
    }
    response = client.post("/train", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_predict():
    payload = {
        "series_id": "store_123_sales",
        "horizon": 3
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert len(data["forecast"]) == 3

def test_predict_learn():
    payload = {"series_id": "store_123_sales", "y_real": 135}
    response = client.post("/predict_learn", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data

def test_feedback():
    payload = {
        "series_id": "store_123_sales",
        "ground_truth": [{"timestamp": "2025-08-28", "value": 140}]
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
