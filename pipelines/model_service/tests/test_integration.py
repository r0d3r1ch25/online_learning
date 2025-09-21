#!/usr/bin/env python3
"""
Integration tests for Model Service API endpoints.
Tests comprehensive model functionality including edge cases and monitoring integration.
"""

import requests
import json
import pytest

class TestModelServiceIntegration:
    """Integration tests for model service API"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = "http://localhost:8000"
    
    def test_complete_training_workflow(self):
        """Test complete training workflow with multiple observations"""
        # Train with progressive complexity
        training_data = [
            ({"in_1": 125.0, "in_2": 120.0, "in_3": 115.0}, 130.0),
            ({"in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 118.0}, 135.0),
            ({"in_1": 135.0, "in_2": 130.0, "in_3": 125.0, "in_4": 122.0}, 140.0)
        ]
        
        for features, target in training_data:
            response = requests.post(f"{self.base_url}/train", json={
                "features": features,
                "target": target
            })
            assert response.status_code == 200
            result = response.json()
            assert "successfully" in result["message"]
    
    def test_prediction_workflow(self):
        """Test prediction workflow after training"""
        # Train first
        requests.post(f"{self.base_url}/train", json={
            "features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0},
            "target": 130.0
        })
        
        # Test prediction
        response = requests.post(f"{self.base_url}/predict", json={
            "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0}
        })
        
        assert response.status_code == 200
        result = response.json()
        assert "forecast" in result
        assert len(result["forecast"]) == 1  # Single-step prediction
        assert "value" in result["forecast"][0]
    
    def test_predict_learn_workflow(self):
        """Test predict_learn workflow (online learning)"""
        response = requests.post(f"{self.base_url}/predict_learn", json={
            "features": {"in_1": 140.0, "in_2": 135.0, "in_3": 130.0},
            "target": 145.0
        })
        
        assert response.status_code == 200
        result = response.json()
        assert "prediction" in result
        assert isinstance(result["prediction"], (int, float))
    
    def test_all_12_inputs(self):
        """Test model with all 12 input features"""
        all_features = {
            f"in_{i}": 125.0 - i * 5 for i in range(1, 13)
        }
        
        # Train with all 12 inputs
        response = requests.post(f"{self.base_url}/train", json={
            "features": all_features,
            "target": 130.0
        })
        assert response.status_code == 200
        
        # Predict with all 12 inputs
        response = requests.post(f"{self.base_url}/predict", json={
            "features": all_features
        })
        assert response.status_code == 200
        result = response.json()
        assert len(result["forecast"]) == 1
    
    def test_input_validation(self):
        """Test input validation with unknown features"""
        # This should work but log warnings
        response = requests.post(f"{self.base_url}/train", json={
            "features": {
                "in_1": 100.0,
                "unknown_feature": 999.0,  # Should be ignored
                "lag_1": 200.0  # Should be ignored
            },
            "target": 150.0
        })
        assert response.status_code == 200
    
    def test_edge_cases(self):
        """Test edge cases with extreme values"""
        # Test with extreme values
        response = requests.post(f"{self.base_url}/train", json={
            "features": {"in_1": -1000.0, "in_2": 0.0, "in_3": 999999.9},
            "target": 50.0
        })
        assert response.status_code == 200
        
        # Test with empty features
        response = requests.post(f"{self.base_url}/predict", json={
            "features": {}
        })
        assert response.status_code == 200
    
    def test_metrics_endpoints(self):
        """Test metrics endpoints"""
        # Generate some predictions first
        requests.post(f"{self.base_url}/predict_learn", json={
            "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0},
            "target": 140.0
        })
        
        # Test model metrics
        response = requests.get(f"{self.base_url}/model_metrics")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, dict)
        
        # Test Prometheus metrics
        response = requests.get(f"{self.base_url}/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
    
    def test_feedback_endpoint(self):
        """Test feedback endpoint"""
        response = requests.post(f"{self.base_url}/feedback", json={
            "message": "Model performing well with new features"
        })
        assert response.status_code == 200
        result = response.json()
        assert "message" in result

if __name__ == "__main__":
    # Can be run directly for manual testing
    test = TestModelServiceIntegration()
    test.setup_method()
    test.test_complete_training_workflow()
    test.test_prediction_workflow()
    test.test_predict_learn_workflow()
    test.test_all_12_inputs()
    test.test_input_validation()
    test.test_edge_cases()
    test.test_metrics_endpoints()
    test.test_feedback_endpoint()
    print("All integration tests passed!")