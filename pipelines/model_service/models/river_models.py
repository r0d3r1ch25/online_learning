from river import linear_model, ensemble, preprocessing, neighbors, forest
from base_model import BaseModel
from typing import Dict, List

class RiverModelWrapper(BaseModel):
    """Wrapper for River models to implement BaseModel interface"""
    
    def __init__(self, river_model, model_name: str):
        self.river_model = river_model
        self.model_name = model_name
    
    def learn_one(self, features: Dict[str, float], target: float) -> None:
        self.river_model.learn_one(features, target)
    
    def predict_one(self, features: Dict[str, float]) -> float:
        return self.river_model.predict_one(features)
    
    def predict_learn(self, features: Dict[str, float], target: float) -> float:
        """Predict then learn from target"""
        prediction = self.river_model.predict_one(features)
        self.river_model.learn_one(features, target)
        return prediction
    
    def predict_many(self, features: Dict[str, float], steps: int = 5) -> List[float]:
        """Predict multiple steps ahead recursively"""
        predictions = []
        current_features = features.copy()
        
        print(f"\n=== PREDICT_MANY: Starting {steps}-step prediction ===")
        print(f"Initial features: {current_features}")
        
        for step in range(steps):
            print(f"\n--- Step {step + 1} ---")
            print(f"Input features: {current_features}")
            
            pred = self.river_model.predict_one(current_features)
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

def get_river_models() -> Dict[str, BaseModel]:
    """Return all available River models"""
    return {
        "linear_regression": RiverModelWrapper(
            preprocessing.StandardScaler() | linear_model.LinearRegression(),
            "linear_regression"
        ),
        "knn_regressor": RiverModelWrapper(
            preprocessing.StandardScaler() | neighbors.KNNRegressor(n_neighbors=5),
            "knn_regressor"
        ),
        "amf_regressor": RiverModelWrapper(
            preprocessing.StandardScaler() | forest.AMFRegressor(),
            "amf_regressor"
        ),
        "bagging_regressor": RiverModelWrapper(
            preprocessing.StandardScaler() | ensemble.BaggingRegressor(
                model=linear_model.LinearRegression(l2=1.0),
                n_models=3
            ),
            "bagging_regressor"
        )
    }