from typing import Dict, List, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class LagFeatureManager:
    """Manages lag feature computation for time series data."""
    
    def __init__(self, max_lags: int = 12):
        self.max_lags = max_lags
        self.series_buffers: Dict[str, deque] = {}
    
    def add_observation(self, series_id: str, value: float) -> None:
        """Add new observation to series buffer."""
        if series_id not in self.series_buffers:
            self.series_buffers[series_id] = deque(maxlen=self.max_lags)
        
        self.series_buffers[series_id].append(value)
        logger.info(f"Added observation {value} to series {series_id}")
    
    def extract_features(self, series_id: str, current_value: float) -> Dict[str, float]:
        """Extract lag features from previous observations, then add current value."""
        # Get buffer for this series (before adding current observation)
        buffer = self.series_buffers.get(series_id, deque())
        
        # Create model-ready features from previous observations
        features = {}
        
        # Fill features with lag values (in_1 = most recent previous, etc.)
        for i in range(1, self.max_lags + 1):
            if len(buffer) >= i:
                # in_1 is the most recent previous observation
                features[f"in_{i}"] = buffer[-i]
            else:
                # Fill missing lags with 0.0
                features[f"in_{i}"] = 0.0
        
        # Now add current observation to buffer for next time
        self.add_observation(series_id, current_value)
        
        return features
    
    def get_series_info(self) -> Dict[str, Dict]:
        """Get information about all series."""
        info = {}
        for series_id, buffer in self.series_buffers.items():
            info[series_id] = {
                "length": len(buffer),
                "latest_value": buffer[-1] if buffer else None,
                "available_lags": min(len(buffer), self.max_lags)
            }
        return info