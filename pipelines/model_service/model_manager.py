

from river import linear_model, tree, ensemble, preprocessing, neighbors, forest, neural_net as nn
import os

class ModelManager:
    def __init__(self):
        self.forecast_horizon = 1  # Single-step prediction only
        model_name = os.getenv("MODEL_NAME", "linear_regression")
        
        # Available models: linear_regression, knn_regressor, amf_regressor, bagging_regressor
        models = {
            "linear_regression": preprocessing.StandardScaler() | linear_model.LinearRegression(),
            "knn_regressor": preprocessing.StandardScaler() | neighbors.KNNRegressor(n_neighbors=5),
            "amf_regressor": preprocessing.StandardScaler() | forest.AMFRegressor(),
            "bagging_regressor": preprocessing.StandardScaler() | ensemble.BaggingRegressor(
                model=linear_model.LinearRegression(l2=1.0),
                n_models=3
            )
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
        
    def predict_many(self, features, steps=5):
        """Predict multiple steps ahead recursively"""
        predictions = []
        current_features = features.copy()
        
        print(f"\n=== PREDICT_MANY: Starting {steps}-step prediction ===")
        print(f"Initial features: {current_features}")
        
        for step in range(steps):
            print(f"\n--- Step {step + 1} ---")
            print(f"Input features: {current_features}")
            
            pred = self.model.predict_one(current_features)
            predictions.append(pred)
            print(f"Prediction: {pred:.4f}")
            
            # Shift lag features for next prediction
            lag_keys = [k for k in current_features.keys() if k.startswith('in_')]
            lag_keys.sort(key=lambda x: int(x.split('_')[1]))
            print(f"Lag keys found: {lag_keys}")
            
            # Shift values: in_1 gets prediction, in_2 gets old in_1, etc.
            if lag_keys:
                old_features = current_features.copy()
                for i in range(len(lag_keys) - 1, 0, -1):
                    current_features[lag_keys[i]] = current_features[lag_keys[i-1]]
                current_features[lag_keys[0]] = pred
                print(f"Feature shift: {old_features} -> {current_features}")
            else:
                print("No lag features to shift")
                
        print(f"\n=== PREDICT_MANY: Complete. All predictions: {predictions} ===")
        return predictions