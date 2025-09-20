import pytest
import logging
from fastapi.testclient import TestClient
from service import app, FORECAST_HORIZON

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "model_loaded" in data

def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "forecast_horizon" in data
    assert "max_features" in data
    assert "stateless" in data
    assert data["stateless"] == True
    assert data["forecast_horizon"] == FORECAST_HORIZON

def test_train_valid_features():
    payload = {
        "features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0},
        "target": 130.0
    }
    response = client.post("/train", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "successfully" in data["message"]

def test_train_missing_features():
    """Test training with incomplete features - should use imputation"""
    payload = {
        "features": {"in_1": 125.0},  # Missing in_2, in_3, etc.
        "target": 130.0
    }
    response = client.post("/train", json=payload)
    assert response.status_code == 200

def test_train_unknown_features(caplog):
    """Test training with unknown feature names - should warn"""
    with caplog.at_level(logging.WARNING):
        payload = {
            "features": {"in_1": 125.0, "unknown_feature": 999.0, "lag_1": 100.0},
            "target": 130.0
        }
        response = client.post("/train", json=payload)
        assert response.status_code == 200
        assert "Unknown input feature: unknown_feature" in caplog.text
        assert "Unknown input feature: lag_1" in caplog.text

def test_train_invalid_payload():
    """Test training with invalid payload structure"""
    payload = {"invalid": "data"}
    response = client.post("/train", json=payload)
    assert response.status_code == 422  # Validation error

def test_predict_valid_features():
    # Train first
    train_payload = {
        "features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0},
        "target": 130.0
    }
    client.post("/train", json=train_payload)
    
    # Then predict
    payload = {"features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0}}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert len(data["forecast"]) == FORECAST_HORIZON
    for item in data["forecast"]:
        assert "value" in item
        assert isinstance(item["value"], (int, float))

def test_predict_empty_features():
    """Test prediction with empty features - should use imputation"""
    payload = {"features": {}}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["forecast"]) == FORECAST_HORIZON

def test_predict_unknown_features(caplog):
    """Test prediction with unknown features - should warn and ignore"""
    with caplog.at_level(logging.WARNING):
        payload = {
            "features": {"in_1": 130.0, "bad_feature": 999.0, "lag_5": 100.0}
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        assert "Unknown input feature: bad_feature" in caplog.text
        assert "Unknown input feature: lag_5" in caplog.text

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

def test_feedback():
    payload = {"message": "test feedback"}
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

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

def test_feature_validation_edge_cases():
    """Test edge cases in feature validation"""
    # Test with negative values
    payload = {
        "features": {"in_1": -100.0, "in_2": 0.0, "in_3": 999999.9},
        "target": 50.0
    }
    response = client.post("/train", json=payload)
    assert response.status_code == 200
    
    # Test prediction with same extreme values
    pred_payload = {"features": {"in_1": -100.0, "in_2": 0.0, "in_3": 999999.9}}
    response = client.post("/predict", json=pred_payload)
    assert response.status_code == 200

def test_full_12_inputs():
    """Test using all 12 input features"""
    # Train with all 12 inputs
    train_payload = {
        "features": {
            "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
            "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
            "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
        },
        "target": 130.0
    }
    response = client.post("/train", json=train_payload)
    assert response.status_code == 200
    
    # Predict with all 12 inputs
    pred_payload = {
        "features": {
            "in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 115.0,
            "in_5": 110.0, "in_6": 105.0, "in_7": 100.0, "in_8": 95.0,
            "in_9": 90.0, "in_10": 85.0, "in_11": 80.0, "in_12": 75.0
        }
    }
    response = client.post("/predict", json=pred_payload)
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert len(data["forecast"]) == FORECAST_HORIZON
    
    # Predict and learn with all 12 inputs
    pred_learn_payload = {
        "features": {
            "in_1": 135.0, "in_2": 130.0, "in_3": 125.0, "in_4": 120.0,
            "in_5": 115.0, "in_6": 110.0, "in_7": 105.0, "in_8": 100.0,
            "in_9": 95.0, "in_10": 90.0, "in_11": 85.0, "in_12": 80.0
        },
        "target": 140.0
    }
    response = client.post("/predict_learn", json=pred_learn_payload)
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
        assert "mae" in metrics
        assert "mse" in metrics
        assert "rmse" in metrics
        assert "count" in metrics
        assert "last_prediction" in metrics
        assert "last_actual" in metrics
        assert "last_error" in metrics
        assert isinstance(metrics["mae"], (int, float))
        assert isinstance(metrics["mse"], (int, float))
        assert isinstance(metrics["rmse"], (int, float))
