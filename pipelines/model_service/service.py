# ml_api/service.py

import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from model_manager import ModelManager
from metrics_manager import MetricsManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Online ML API")

# Configuration
FORECAST_HORIZON = int(os.getenv("FORECAST_HORIZON", "3"))
NUM_FEATURES = int(os.getenv("NUM_FEATURES", "12"))

# Models
model_manager = ModelManager()
metrics_manager = MetricsManager()

class TrainRequest(BaseModel):
    features: Dict[str, float]
    target: float

class PredictRequest(BaseModel):
    features: Dict[str, float]

class PredictLearnRequest(BaseModel):
    features: Dict[str, float]
    target: float

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_manager.model is not None}

@app.get("/info")
def info():
    return {
        "model_name": "River LinearRegression",
        "model_version": "0.22.0",
        "forecast_horizon": FORECAST_HORIZON,
        "max_features": NUM_FEATURES,
        "stateless": True,
        "memory_managed_externally": True
    }

@app.post("/train")
def train(request: TrainRequest):
    """Train model with features and target"""
    try:
        validated_features = _validate_features(request.features)
        model_manager.train(validated_features, request.target)
        return {"message": "Model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict(request: PredictRequest):
    """Predict multiple steps ahead using same features"""
    try:
        # Validate and clean features
        validated_features = _validate_features(request.features)
        
        forecast = []
        for _ in range(FORECAST_HORIZON):
            pred = model_manager.predict(validated_features)
            forecast.append({"value": pred})
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _validate_features(features: Dict[str, float]) -> Dict[str, float]:
    """Validate features and warn about unknown inputs"""
    expected_inputs = {f"in_{i}" for i in range(1, NUM_FEATURES + 1)}
    validated = {}
    
    # Check for unknown inputs
    for key in features:
        if key not in expected_inputs:
            logging.warning(f"Unknown input feature: {key}")
        else:
            validated[key] = features[key]
    
    # Fill missing inputs with 0.0
    for i in range(1, NUM_FEATURES + 1):
        input_key = f"in_{i}"
        if input_key not in validated:
            validated[input_key] = 0.0
    
    return validated

@app.post("/predict_learn")
def predict_learn(request: PredictLearnRequest):
    """Predict then learn from target"""
    try:
        validated_features = _validate_features(request.features)
        pred = model_manager.predict_learn(validated_features, request.target)
        metrics_manager.add("default", request.target, pred)
        return {"prediction": pred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
def feedback(data: dict):
    return {"message": "Feedback received successfully"}

@app.get("/metrics")
def metrics():
    """Get comprehensive model performance metrics and statistics"""
    return metrics_manager.get_metrics()
