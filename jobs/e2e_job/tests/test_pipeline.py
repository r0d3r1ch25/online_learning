#!/usr/bin/env python3
"""
Unit tests for E2E pipeline job.
Tests pipeline logic without requiring actual services.
"""

import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import log, main

class TestPipeline:
    """Unit tests for pipeline functions"""
    
    def test_log_function(self, capsys):
        """Test log function outputs correctly"""
        log("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert captured.out.endswith("Test message\n")
    
    @patch('pipeline.requests.get')
    @patch('pipeline.requests.post')
    def test_successful_pipeline(self, mock_post, mock_get):
        """Test successful pipeline execution"""
        # Mock ingestion service response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'target': 125.0,
            'observation_id': 1,
            'remaining': 143
        }
        
        # Mock feature service response
        feature_response = Mock()
        feature_response.status_code = 200
        feature_response.json.return_value = {
            'features': {'in_1': 120.0, 'in_2': 115.0},
            'target': 125.0,
            'available_lags': 2
        }
        
        # Mock model service responses
        model_response = Mock()
        model_response.status_code = 200
        model_response.json.return_value = {'prediction': 123.5}
        
        metrics_response = Mock()
        metrics_response.status_code = 200
        metrics_response.json.return_value = {
            'default': {'mae': 2.5, 'rmse': 3.2, 'count': 10}
        }
        
        # Configure mock responses in order
        mock_post.side_effect = [feature_response, model_response]
        mock_get.side_effect = [
            mock_get.return_value,  # ingestion call
            metrics_response        # metrics call
        ]
        
        # Run pipeline
        main()
        
        # Verify calls were made
        assert mock_get.call_count == 2
        assert mock_post.call_count == 2
    
    @patch('pipeline.requests.get')
    def test_stream_exhausted(self, mock_get):
        """Test pipeline handles stream exhaustion correctly"""
        mock_get.return_value.status_code = 204
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0  # Normal exit
    
    @patch('pipeline.requests.get')
    def test_http_error_handling(self, mock_get):
        """Test pipeline handles HTTP errors correctly"""
        mock_get.side_effect = Exception("Connection failed")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1  # Error exit
    
    @patch('pipeline.requests.get')
    @patch('pipeline.requests.post')
    def test_feature_logging(self, mock_post, mock_get, capsys):
        """Test feature logging shows all features"""
        # Mock responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'target': 125.0,
            'observation_id': 1,
            'remaining': 143
        }
        
        feature_response = Mock()
        feature_response.status_code = 200
        feature_response.json.return_value = {
            'features': {
                'in_1': 120.0, 'in_2': 115.0, 'in_3': 110.0,
                'in_4': 105.0, 'in_5': 100.0
            },
            'target': 125.0,
            'available_lags': 5
        }
        
        model_response = Mock()
        model_response.status_code = 200
        model_response.json.return_value = {'prediction': 123.5}
        
        metrics_response = Mock()
        metrics_response.status_code = 200
        metrics_response.json.return_value = {
            'default': {'mae': 2.5, 'rmse': 3.2, 'count': 10}
        }
        
        mock_post.side_effect = [feature_response, model_response]
        mock_get.side_effect = [
            mock_get.return_value,
            metrics_response
        ]
        
        main()
        
        captured = capsys.readouterr()
        # Check that all features are logged
        assert "in_1: 120.0" in captured.out
        assert "in_2: 115.0" in captured.out
        assert "in_5: 100.0" in captured.out

if __name__ == "__main__":
    pytest.main([__file__])