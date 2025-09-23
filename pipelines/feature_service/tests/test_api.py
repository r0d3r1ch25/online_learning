import pytest
from fastapi.testclient import TestClient
from service import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "feature_service"

def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "feature_service"
    assert data["max_lags"] == 10  # N_LAGS=10 in CI environment
    assert data["output_format"] == "model_ready_in_1_to_in_10"


def test_add_observation():
    payload = {
        "series_id": "test_series",
        "value": 100.0
    }
    response = client.post("/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["series_id"] == "test_series"
    assert "features" in data
    assert "target" in data
    assert "available_lags" in data
    
    # Check model-ready format - first observation has no previous lags
    features = data["features"]
    assert "in_1" in features
    assert "in_10" in features
    assert features["in_1"] == 0.0  # No previous observations
    assert data["target"] == 100.0  # Current observation as target
    assert len(features) == 10

def test_add_multiple_observations():
    series_id = "multi_test"
    values = [100.0, 105.0, 110.0, 115.0]
    
    for i, value in enumerate(values):
        payload = {
            "series_id": series_id,
            "value": value
        }
        response = client.post("/add", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check lag pattern - features are PREVIOUS observations
        features = data["features"]
        
        if i == 0:
            # First observation - no previous lags
            assert features["in_1"] == 0.0
        else:
            # in_1 should be the most recent previous observation
            assert features["in_1"] == values[i-1]
            
        if i > 1:
            assert features["in_2"] == values[i-2]
        if i > 2:
            assert features["in_3"] == values[i-3]



def test_invalid_payload():
    # Missing required fields
    response = client.post("/add", json={"invalid": "data"})
    assert response.status_code == 422

def test_negative_values():
    payload = {
        "series_id": "negative_test",
        "value": -50.0
    }
    response = client.post("/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["features"]["in_1"] == 0.0  # No previous observations
    assert data["target"] == -50.0  # Current observation as target

def test_zero_values():
    payload = {
        "series_id": "zero_test", 
        "value": 0.0
    }
    response = client.post("/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["features"]["in_1"] == 0.0  # No previous observations
    assert data["target"] == 0.0  # Current observation as target

def test_large_values():
    payload = {
        "series_id": "large_test",
        "value": 999999.99
    }
    response = client.post("/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["features"]["in_1"] == 0.0  # No previous observations
    assert data["target"] == 999999.99  # Current observation as target

def test_default_series_id():
    payload = {
        "value": 150.0
    }
    response = client.post("/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["series_id"] == "default"

def test_feature_format_consistency():
    """Test that all features follow in_1 to in_N_LAGS format (N_LAGS=10 in CI)"""
    payload = {
        "series_id": "format_test",
        "value": 300.0
    }
    response = client.post("/add", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    features = data["features"]
    # Should have exactly 10 features (N_LAGS=10 in CI environment)
    assert len(features) == 10
    
    # Should have in_1 through in_10
    for i in range(1, 11):
        assert f"in_{i}" in features
        assert isinstance(features[f"in_{i}"], (int, float))