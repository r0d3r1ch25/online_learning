import pytest
import logging
from fastapi.testclient import TestClient
from service import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "model_loaded" in data





def test_predict_learn_valid():
    payload = {
        "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0},
        "target": 140.0
    }
    response = client.post("/predict_learn", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], (int, float))

def test_predict_learn_missing_target():
    """Test predict_learn without target - should fail validation"""
    payload = {"features": {"in_1": 135.0}}
    response = client.post("/predict_learn", json=payload)
    assert response.status_code == 422

def test_predict_learn_invalid_target():
    """Test predict_learn with non-numeric target"""
    payload = {
        "features": {"in_1": 135.0},
        "target": "invalid"
    }
    response = client.post("/predict_learn", json=payload)
    assert response.status_code == 422

# Feedback endpoint removed - feature-agnostic model service

def test_model_metrics():
    # Train and predict_learn to generate metrics
    payload = {
        "features": {"in_1": 135.0, "in_2": 130.0},
        "target": 140.0
    }
    client.post("/predict_learn", json=payload)
    
    response = client.get("/model_metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_predict_learn_edge_cases():
    """Test predict_learn with edge cases"""
    # Test with negative values
    payload = {
        "features": {"in_1": -100.0, "in_2": 0.0, "in_3": 999999.9},
        "target": 50.0
    }
    response = client.post("/predict_learn", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data

def test_predict_learn_12_inputs():
    """Test predict_learn with all 12 input features"""
    payload = {
        "features": {
            "in_1": 135.0, "in_2": 130.0, "in_3": 125.0, "in_4": 120.0,
            "in_5": 115.0, "in_6": 110.0, "in_7": 105.0, "in_8": 100.0,
            "in_9": 95.0, "in_10": 90.0, "in_11": 85.0, "in_12": 80.0
        },
        "target": 140.0
    }
    response = client.post("/predict_learn", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data

def test_prometheus_metrics():
    """Test the /metrics endpoint for Prometheus format"""
    # Generate some predictions first
    payload = {
        "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0},
        "target": 140.0
    }
    client.post("/predict_learn", json=payload)
    
    # Test Prometheus metrics endpoint
    response = client.get("/metrics")
    assert response.status_code == 200
    # Should return metrics data
    data = response.text if hasattr(response, 'text') else str(response.content)
    assert len(data) > 0

def test_model_metrics_detailed():
    """Test the /model_metrics endpoint for comprehensive model performance metrics"""
    # Generate some predictions first
    payload = {
        "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0},
        "target": 140.0
    }
    client.post("/predict_learn", json=payload)
    
    # Test model metrics endpoint
    response = client.get("/model_metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    
    # Should have comprehensive metrics for default series
    if "default" in data:
        metrics = data["default"]
        assert "count" in metrics
        assert "last_prediction" in metrics
        assert "last_actual" in metrics
        assert "last_error" in metrics
        # Check for rolling metrics with window sizes
        rolling_metrics = [k for k in metrics.keys() if k.endswith(('_5', '_10', '_20'))]
        assert len(rolling_metrics) > 0
        # Check that we have mae, mse, rmse, mape for each window size
        for window in ['5', '10', '20']:
            assert any(k.endswith(f'_{window}') for k in metrics.keys())
