#!/usr/bin/env python3
"""
Integration tests for Feature Service API endpoints.
Tests the complete feature extraction workflow with multiple observations.
"""

import requests
import json
import pytest

class TestFeatureServiceIntegration:
    """Integration tests for feature service API"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = "http://localhost:8001"
        
    def _check_service_available(self):
        """Check if service is available, skip test if not"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def test_complete_feature_extraction_workflow(self):
        """Test complete workflow with multiple observations"""
        if not self._check_service_available():
            pytest.skip("Feature service not available - skipping integration test")
            
        # Test with sequential observations
        observations = [100.0, 105.0, 110.0, 115.0, 120.0]
        series_id = "test_workflow"
        
        for i, value in enumerate(observations):
            response = requests.post(f"{self.base_url}/add", json={
                "series_id": series_id,
                "value": value
            })
            
            assert response.status_code == 200
            result = response.json()
            
            # Verify response structure
            assert "features" in result
            assert "target" in result
            assert "available_lags" in result
            assert result["target"] == value
            assert result["available_lags"] == i  # Should match number of previous observations
            
            # Verify model-ready format
            features = result["features"]
            assert len(features) == 12  # Always 12 features (in_1 to in_12)
            
            # Check lag pattern
            if i > 0:
                assert features["in_1"] == observations[i-1]  # Most recent previous
            if i > 1:
                assert features["in_2"] == observations[i-2]  # Second most recent
    
    def test_model_ready_format_verification(self):
        """Test that features are in correct model-ready format"""
        if not self._check_service_available():
            pytest.skip("Feature service not available - skipping integration test")
            
        series_id = "format_test"
        
        # Add enough observations to test all lags
        for i in range(15):
            value = 100.0 + i * 5
            response = requests.post(f"{self.base_url}/add", json={
                "series_id": series_id,
                "value": value
            })
            
            result = response.json()
            features = result["features"]
            
            # Verify all 12 features exist
            for j in range(1, 13):
                assert f"in_{j}" in features
            
            # For the last observation, verify lag pattern
            if i >= 12:
                expected_lags = [100.0 + (i-k) * 5 for k in range(1, 13)]
                actual_lags = [features[f"in_{k}"] for k in range(1, 13)]
                assert actual_lags == expected_lags
    
    def test_multiple_series_independence(self):
        """Test that multiple series maintain independent state"""
        if not self._check_service_available():
            pytest.skip("Feature service not available - skipping integration test")
            
        # Add observations to first series
        for value in [10, 20, 30]:
            requests.post(f"{self.base_url}/add", json={
                "series_id": "series_1",
                "value": value
            })
        
        # Add observations to second series
        for value in [100, 200, 300]:
            requests.post(f"{self.base_url}/add", json={
                "series_id": "series_2", 
                "value": value
            })
        
        # Verify series independence
        response1 = requests.post(f"{self.base_url}/add", json={
            "series_id": "series_1",
            "value": 40
        })
        
        response2 = requests.post(f"{self.base_url}/add", json={
            "series_id": "series_2",
            "value": 400
        })
        
        result1 = response1.json()
        result2 = response2.json()
        
        # Series 1 should have lags from its own observations
        assert result1["features"]["in_1"] == 30
        assert result1["features"]["in_2"] == 20
        
        # Series 2 should have lags from its own observations
        assert result2["features"]["in_1"] == 300
        assert result2["features"]["in_2"] == 200

if __name__ == "__main__":
    # Can be run directly for manual testing
    test = TestFeatureServiceIntegration()
    test.setup_method()
    test.test_complete_feature_extraction_workflow()
    test.test_model_ready_format_verification()
    test.test_multiple_series_independence()
    print("All integration tests passed!")