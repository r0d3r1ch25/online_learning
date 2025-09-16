import pytest
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")

def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "feature_service"

def test_service_info():
    """Test service info endpoint."""
    response = requests.get(f"{API_BASE_URL}/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "feature_service"
    assert data["max_lags"] == 12

def test_add_observation_and_get_features():
    """Test adding observations and getting features."""
    series_id = "test_series"
    
    # Add some observations
    for i, value in enumerate([100, 105, 110, 115, 120], 1):
        response = requests.post(
            f"{API_BASE_URL}/add_observation",
            json={"series_id": series_id, "value": value}
        )
        assert response.status_code == 200
    
    # Get features
    response = requests.post(
        f"{API_BASE_URL}/features",
        json={"series_id": series_id, "num_lags": 3}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["series_id"] == series_id
    assert "features" in data
    assert "lag_1" in data["features"]
    assert data["features"]["lag_1"] == 120  # Latest value

def test_get_features_by_id():
    """Test GET endpoint for features."""
    series_id = "test_series_2"
    
    # Add observation
    requests.post(
        f"{API_BASE_URL}/add_observation",
        json={"series_id": series_id, "value": 200}
    )
    
    # Get features via GET
    response = requests.get(f"{API_BASE_URL}/features/{series_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["series_id"] == series_id