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

def test_extract_features():
    """Test extracting model-ready features."""
    manager = LagFeatureManager(max_lags=12)
    
    # Add some observations
    values = [100, 105, 110]
    for value in values:
        manager.add_observation("test_series", value)
    
    # Extract features with new value
    features = manager.extract_features("test_series", 115.0)
    
    # Should return in_1 to in_12 format
    assert "in_1" in features
    assert "in_2" in features
    assert "in_12" in features
    
    # in_1 should be the most recent (115.0)
    assert features["in_1"] == 115.0
    assert features["in_2"] == 110.0
    assert features["in_3"] == 105.0
    assert features["in_4"] == 100.0
    
    # Missing lags should be 0.0
    assert features["in_5"] == 0.0
    assert features["in_12"] == 0.0

def test_extract_features_empty_series():
    """Test extracting features for new series."""
    manager = LagFeatureManager(max_lags=12)
    
    # Extract features for new series
    features = manager.extract_features("new_series", 50.0)
    
    # Should have in_1 to in_12
    assert len(features) == 12
    assert features["in_1"] == 50.0
    
    # All other lags should be 0.0
    for i in range(2, 13):
        assert features[f"in_{i}"] == 0.0

def test_max_lags_limit():
    """Test that buffer respects max_lags limit."""
    manager = LagFeatureManager(max_lags=3)
    
    # Add more observations than max_lags
    for i in range(5):
        manager.add_observation("test_series", i)
    
    # Buffer should only keep last 3 values
    assert len(manager.series_buffers["test_series"]) == 3

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