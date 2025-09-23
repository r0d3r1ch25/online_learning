import pytest
from unittest.mock import patch
from feature_manager import LagFeatureManager

def test_lag_feature_manager_init():
    """Test LagFeatureManager initialization."""
    with patch('redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Redis unavailable")
        manager = LagFeatureManager()  # Uses N_LAGS from environment
        assert manager.max_lags == 10  # Set in CI workflow
        assert len(manager.series_buffers) == 0
        assert manager.use_redis == False

def test_add_observation():
    """Test adding observations to series."""
    with patch('redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Redis unavailable")
        manager = LagFeatureManager()  # Uses N_LAGS from environment
    
    manager.add_observation("test_series", 100.0)
    manager.add_observation("test_series", 105.0)
    
    assert "test_series" in manager.series_buffers
    assert len(manager.series_buffers["test_series"]) == 2

def test_extract_features():
    """Test extracting model-ready features."""
    with patch('redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Redis unavailable")
        manager = LagFeatureManager()  # Uses N_LAGS from environment
    
    # Add some observations
    values = [100, 105, 110]
    for value in values:
        manager.add_observation("test_series", value)
    
    # Extract features with new value (115.0 becomes target, not feature)
    features = manager.extract_features("test_series", 115.0)
    
    # Should return in_1 to in_10 format (N_LAGS=10 in CI)
    assert "in_1" in features
    assert "in_2" in features
    assert "in_10" in features
    
    # in_1 should be the most recent PREVIOUS observation (110.0)
    assert features["in_1"] == 110.0
    assert features["in_2"] == 105.0
    assert features["in_3"] == 100.0
    
    # Missing lags should be 0.0
    assert features["in_4"] == 0.0
    assert features["in_10"] == 0.0

def test_extract_features_empty_series():
    """Test extracting features for new series."""
    with patch('redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Redis unavailable")
        manager = LagFeatureManager()  # Uses N_LAGS from environment
    
    # Extract features for new series (no previous observations)
    features = manager.extract_features("new_series", 50.0)
    
    # Should have in_1 to in_10 (N_LAGS=10 in CI)
    assert len(features) == 10
    
    # All lags should be 0.0 since no previous observations
    for i in range(1, 11):
        assert features[f"in_{i}"] == 0.0

def test_max_lags_limit():
    """Test that buffer respects max_lags limit."""
    with patch('redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Redis unavailable")
        manager = LagFeatureManager()  # Uses N_LAGS from environment
    
    # Add more observations than max_lags (15 > 10)
    for i in range(15):
        manager.add_observation("test_series", i)
    
    # Buffer should only keep last 10 values (N_LAGS=10 in CI)
    assert len(manager.series_buffers["test_series"]) == 10

def test_get_series_info():
    """Test getting series information."""
    with patch('redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Redis unavailable")
        manager = LagFeatureManager()  # Uses N_LAGS from environment
    
    manager.add_observation("series1", 100)
    manager.add_observation("series1", 105)
    manager.add_observation("series2", 200)
    
    info = manager.get_series_info()
    
    assert "series1" in info
    assert "series2" in info
    assert info["series1"]["length"] == 2
    assert info["series1"]["latest_value"] == 105
    assert info["series2"]["length"] == 1
    assert info["series2"]["latest_value"] == 200