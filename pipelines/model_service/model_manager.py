

from river import linear_model, tree, ensemble, preprocessing, neighbors, forest
import os

class ModelManager:
    def __init__(self):
        self.forecast_horizon = 1  # Single-step prediction only
        model_name = os.getenv("MODEL_NAME", "linear_regression")
        
        # Available models: linear_regression, ridge_regression, knn_regressor, amf_regressor
        models = {
            "linear_regression": preprocessing.StandardScaler() | linear_model.LinearRegression(),
            "ridge_regression": preprocessing.StandardScaler() | linear_model.LinearRegression(l2=1.0),
            "knn_regressor": preprocessing.StandardScaler() | neighbors.KNNRegressor(n_neighbors=5),
            "amf_regressor": preprocessing.StandardScaler() | forest.AMFRegressor()
        }
        
        self.model = models.get(model_name, models["linear_regression"])
        self.model_name = model_name
        
    def train(self, features, target):
        """Train model with features and target"""
        self.model.learn_one(features, target)
        
    def predict(self, features):
        """Predict using features"""
        return self.model.predict_one(features)
        

        
    def predict_learn(self, features, target):
        """Predict then learn from target"""
        prediction = self.model.predict_one(features)
        self.model.learn_one(features, target)
        return prediction