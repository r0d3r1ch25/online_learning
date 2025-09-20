# ml_api/service.py

import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from model_manager import ModelManager
from metrics_manager import MetricsManager
from river import preprocessing, stats

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

# Models and imputation
imputer = preprocessing.StatImputer(('default', stats.Mean()))
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
    
    # Use imputation for missing features
    for i in range(1, NUM_FEATURES + 1):
        input_key = f"in_{i}"
        if input_key not in validated:
            validated[input_key] = None  # Will be imputed
    
    # Apply imputation
    imputed_features = imputer.transform_one(validated)
    
    return imputed_features

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

@app.get("/model_metrics")
def model_metrics():
    """Get comprehensive model performance metrics and statistics"""
    return metrics_manager.get_metrics()

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus-compatible metrics endpoint"""
    metrics_data = metrics_manager.get_metrics()
    
    if "message" in metrics_data:
        return "# No predictions available yet\n", {"Content-Type": "text/plain"}
    
    prometheus_output = []
    
    for series_id, data in metrics_data.items():
        # Model performance metrics
        prometheus_output.append(f"# HELP ml_model_mae Mean Absolute Error")
        prometheus_output.append(f"# TYPE ml_model_mae gauge")
        prometheus_output.append(f'ml_model_mae{{series="{series_id}"}} {data.get("mae", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_mse Mean Squared Error")
        prometheus_output.append(f"# TYPE ml_model_mse gauge")
        prometheus_output.append(f'ml_model_mse{{series="{series_id}"}} {data.get("mse", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_rmse Root Mean Squared Error")
        prometheus_output.append(f"# TYPE ml_model_rmse gauge")
        prometheus_output.append(f'ml_model_rmse{{series="{series_id}"}} {data.get("rmse", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_predictions_total Total number of predictions")
        prometheus_output.append(f"# TYPE ml_model_predictions_total counter")
        prometheus_output.append(f'ml_model_predictions_total{{series="{series_id}"}} {data.get("count", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_last_prediction Last prediction value")
        prometheus_output.append(f"# TYPE ml_model_last_prediction gauge")
        prometheus_output.append(f'ml_model_last_prediction{{series="{series_id}"}} {data.get("last_prediction", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_last_error Last prediction error")
        prometheus_output.append(f"# TYPE ml_model_last_error gauge")
        prometheus_output.append(f'ml_model_last_error{{series="{series_id}"}} {data.get("last_error", 0)}')
    
    from fastapi import Response
    return Response(content="\n".join(prometheus_output) + "\n", media_type="text/plain")
