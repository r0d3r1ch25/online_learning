from typing import Dict, List, Optional
from collections import deque
import logging
import os
import redis

logger = logging.getLogger(__name__)

# Configuration - change this value to adjust number of lags
N_LAGS = int(os.getenv('N_LAGS', '12'))
REDIS_HOST = os.getenv('REDIS_HOST', 'redis.ml-services.svc.cluster.local')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

class LagFeatureManager:
    """Manages lag feature computation for time series data using Redis FIFO lists."""
    
    def __init__(self, max_lags: int = N_LAGS):
        self.max_lags = max_lags
        self.series_buffers: Dict[str, deque] = {}  # Fallback for Redis unavailable
        
        # Try to connect to Redis
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            self.redis_client.ping()
            self.use_redis = True
            logger.info(f"REDIS CONNECTED: Using Redis at {REDIS_HOST}:{REDIS_PORT} for persistent lag features")
        except Exception as e:
            logger.warning(f"REDIS UNAVAILABLE: Using in-memory storage (data will be lost on restart): {e}")
            self.redis_client = None
            self.use_redis = False
    
    def add_observation(self, series_id: str, value: float) -> None:
        """Add new observation to series buffer."""
        if self.use_redis:
            try:
                key = f"series:{series_id}:values"
                # Add to front of list (most recent first)
                self.redis_client.lpush(key, value)
                # Keep only max_lags items
                self.redis_client.ltrim(key, 0, self.max_lags - 1)
                logger.info(f"REDIS: Added observation {value} to series {series_id} (persistent storage)")
                return
            except Exception as e:
                logger.error(f"REDIS ERROR: Falling back to in-memory storage: {e}")
                self.use_redis = False
        
        # Fallback to in-memory storage
        if series_id not in self.series_buffers:
            self.series_buffers[series_id] = deque(maxlen=self.max_lags)
        
        self.series_buffers[series_id].append(value)
        logger.info(f"MEMORY: Added observation {value} to series {series_id} (temporary storage)")
    
    def extract_features(self, series_id: str, current_value: float) -> Dict[str, float]:
        """Extract lag features from previous observations, then add current value."""
        features = {}
        
        if self.use_redis:
            try:
                key = f"series:{series_id}:values"
                # Get all values from Redis list (most recent first)
                values = self.redis_client.lrange(key, 0, -1)
                values = [float(v) for v in values]  # Convert to float
                
                # Fill features with lag values (in_1 = most recent, etc.)
                for i in range(1, self.max_lags + 1):
                    if len(values) >= i:
                        features[f"in_{i}"] = values[i-1]  # Redis list is already newest first
                    else:
                        features[f"in_{i}"] = 0.0
            except Exception as e:
                logger.error(f"REDIS ERROR in extract_features: Falling back to memory: {e}")
                self.use_redis = False
        
        if not self.use_redis:
            # Fallback to in-memory storage
            buffer = self.series_buffers.get(series_id, deque())
            
            # Fill features with lag values (in_1 = most recent previous, etc.)
            for i in range(1, self.max_lags + 1):
                if len(buffer) >= i:
                    features[f"in_{i}"] = buffer[-i]
                else:
                    features[f"in_{i}"] = 0.0
        
        # Now add current observation to buffer for next time
        self.add_observation(series_id, current_value)
        
        return features
    
    def get_series_info(self) -> Dict[str, Dict]:
        """Get information about all series."""
        info = {}
        
        if self.use_redis:
            try:
                # Get all series keys from Redis
                keys = self.redis_client.keys("series:*:values")
                for key in keys:
                    series_id = key.split(":")[1]  # Extract series_id from key
                    values = self.redis_client.lrange(key, 0, -1)
                    info[series_id] = {
                        "length": len(values),
                        "latest_value": float(values[0]) if values else None,
                        "available_lags": min(len(values), self.max_lags),
                        "storage": "redis"
                    }
            except Exception as e:
                logger.error(f"Redis error in get_series_info: {e}")
        
        # Add in-memory series info
        for series_id, buffer in self.series_buffers.items():
            info[series_id] = {
                "length": len(buffer),
                "latest_value": buffer[-1] if buffer else None,
                "available_lags": min(len(buffer), self.max_lags),
                "storage": "memory"
            }
        
        return info