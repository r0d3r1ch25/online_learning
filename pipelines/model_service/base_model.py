from abc import ABC, abstractmethod
from typing import Dict

class BaseModel(ABC):
    """Abstract base class for all ML models"""
    
    @abstractmethod
    def learn_one(self, features: Dict[str, float], target: float) -> None:
        """Train model with single observation"""
        pass
    
    @abstractmethod
    def predict_one(self, features: Dict[str, float]) -> float:
        """Predict single value from features"""
        pass
    
    @abstractmethod
    def predict_learn(self, features: Dict[str, float], target: float) -> float:
        """Predict then learn from target"""
        pass
    
    @abstractmethod
    def predict_many(self, features: Dict[str, float], steps: int = 5):
        """Predict multiple steps ahead recursively"""
        pass