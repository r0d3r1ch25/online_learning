"""
Data Ingestion Service

Provides streaming access to CSV data one observation at a time.
Maintains state to track current position in the dataset.
"""

import pandas as pd
import os
from typing import Dict, Any, Optional

class DataIngestionService:
    """Service class for managing CSV data streaming"""
    
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or os.path.join(os.path.dirname(__file__), "data.csv")
        self.data: Optional[pd.DataFrame] = None
        self.current_index = 0
        self.load_data()
    
    def load_data(self) -> None:
        """Load CSV data from file"""
        self.data = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.data)} observations from {self.csv_path}")
    
    def get_next_observation(self) -> Optional[Dict[str, Any]]:
        """
        Get the next observation from the dataset.
        Returns None if no more data available.
        """
        if self.current_index >= len(self.data):
            return None
        
        observation = self.data.iloc[self.current_index]
        
        response = {
            "observation_id": self.current_index + 1,
            "input": observation["input"],
            "target": observation["target"],
            "remaining": len(self.data) - self.current_index - 1
        }
        
        self.current_index += 1
        return response
    
    def reset_stream(self) -> Dict[str, Any]:
        """Reset the stream to start from the beginning"""
        self.current_index = 0
        return {
            "message": "Stream reset to beginning",
            "total_observations": len(self.data)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current stream status"""
        return {
            "current_index": self.current_index,
            "total_observations": len(self.data),
            "remaining": len(self.data) - self.current_index,
            "completed": self.current_index >= len(self.data)
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "status": "healthy",
            "total_observations": len(self.data)
        }