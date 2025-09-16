import pandas as pd
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
    
    def get_lag_features(self, series_id: str, num_lags: int = None) -> Dict[str, float]:
        """Get lag features for a series."""
        if num_lags is None:
            num_lags = self.max_lags
        
        num_lags = min(num_lags, self.max_lags)
        
        if series_id not in self.series_buffers:
            return {}
        
        buffer = self.series_buffers[series_id]
        features = {}
        
        for i in range(1, min(num_lags + 1, len(buffer) + 1)):
            if len(buffer) >= i:
                features[f"lag_{i}"] = buffer[-i]
        
        return features
    
    def load_from_csv(self, csv_path: str, series_id: str = "default") -> None:
        """Load historical data from CSV to build initial lag features."""
        try:
            df = pd.read_csv(csv_path)
            
            # Assume CSV has 'target' column for the time series values
            if 'target' in df.columns:
                values = df['target'].tolist()
            elif 'value' in df.columns:
                values = df['value'].tolist()
            else:
                # Use the second column if no standard names
                values = df.iloc[:, 1].tolist()
            
            # Add observations to build lag features
            for value in values:
                self.add_observation(series_id, float(value))
            
            logger.info(f"Loaded {len(values)} observations for series {series_id}")
            
        except Exception as e:
            logger.error(f"Error loading CSV {csv_path}: {e}")
            raise
    
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