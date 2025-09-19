# model_manager.py

from river import linear_model, preprocessing
import os

class ModelManager:
    def __init__(self):
        self.model = preprocessing.StandardScaler() | linear_model.LinearRegression()
        self.num_features = int(os.getenv("NUM_FEATURES", "12"))
        
    def train(self, features, target):
        """Train model with provided features and target"""
        self.model.learn_one(features, target)
        
    def predict(self, features):
        """Predict using provided features"""
        return self.model.predict_one(features)
        
    def predict_learn(self, features, target):
        """Predict then learn from target"""
        prediction = self.model.predict_one(features)
        self.model.learn_one(features, target)
        return prediction