import os
from models.river_models import get_river_models
from base_model import BaseModel

class ModelManager:
    def __init__(self):
        model_name = os.getenv("MODEL_NAME", "linear_regression")
        
        # Get all available models
        models = {}
        models.update(get_river_models())
        # Future: models.update(get_sklearn_models())
        # Future: models.update(get_vowpal_models())
        
        self.model: BaseModel = models.get(model_name, models["linear_regression"])
        self.model_name = model_name
        
    def predict_learn(self, features, target):
        """Predict then learn from target"""
        return self.model.predict_learn(features, target)
        
    def predict_many(self, features, steps=5):
        """Predict multiple steps ahead recursively"""
        return self.model.predict_many(features, steps)