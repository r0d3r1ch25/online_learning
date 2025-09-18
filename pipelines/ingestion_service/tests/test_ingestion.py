import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "total_observations" in data

def test_reset_stream():
    """Test stream reset functionality"""
    response = client.post("/reset")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "total_observations" in data

def test_get_next_observation():
    """Test getting next observation"""
    # Reset first
    client.post("/reset")
    
    # Get first observation
    response = client.get("/next")
    assert response.status_code == 200
    data = response.json()
    
    assert "observation_id" in data
    assert "input" in data
    assert "target" in data
    assert "remaining" in data
    assert data["observation_id"] == 1

def test_stream_exhaustion():
    """Test that stream returns 204 when exhausted"""
    # Reset stream
    client.post("/reset")
    
    # Get status to know total observations
    status_response = client.get("/status")
    total_obs = status_response.json()["total_observations"]
    
    # Consume all observations
    for i in range(total_obs):
        response = client.get("/next")
        assert response.status_code == 200
    
    # Next call should return 204
    response = client.get("/next")
    assert response.status_code == 204

def test_status_endpoint():
    """Test status endpoint"""
    client.post("/reset")
    
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    
    assert "current_index" in data
    assert "total_observations" in data
    assert "remaining" in data
    assert "completed" in data