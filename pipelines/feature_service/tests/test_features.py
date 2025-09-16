import pytest
from feature_manager import LagFeatureManager

def test_lag_feature_manager_init():
    """Test LagFeatureManager initialization."""
    manager = LagFeatureManager(max_lags=5)
    assert manager.max_lags == 5
    assert len(manager.series_buffers) == 0

def test_add_observation():
    """Test adding observations to series."""
    manager = LagFeatureManager(max_lags=3)
    
    manager.add_observation("test_series", 100.0)
    manager.add_observation("test_series", 105.0)
    
    assert "test_series" in manager.series_buffers
    assert len(manager.series_buffers["test_series"]) == 2

def test_get_lag_features():
    """Test getting lag features."""
    manager = LagFeatureManager(max_lags=5)
    
    # Add observations
    values = [100, 105, 110, 115, 120]
    for value in values:
        manager.add_observation("test_series", value)
    
    # Get features
    features = manager.get_lag_features("test_series", num_lags=3)
    
    assert "lag_1" in features
    assert "lag_2" in features
    assert "lag_3" in features
    assert features["lag_1"] == 120  # Latest value
    assert features["lag_2"] == 115
    assert features["lag_3"] == 110

def test_get_lag_features_empty_series():
    """Test getting features for non-existent series."""
    manager = LagFeatureManager()
    features = manager.get_lag_features("nonexistent")
    assert features == {}

def test_max_lags_limit():
    """Test that buffer respects max_lags limit."""
    manager = LagFeatureManager(max_lags=3)
    
    # Add more observations than max_lags
    for i in range(5):
        manager.add_observation("test_series", i)
    
    # Buffer should only keep last 3 values
    assert len(manager.series_buffers["test_series"]) == 3
    
    features = manager.get_lag_features("test_series")
    assert len(features) == 3
    assert features["lag_1"] == 4  # Latest value

def test_get_series_info():
    """Test getting series information."""
    manager = LagFeatureManager(max_lags=5)
    
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