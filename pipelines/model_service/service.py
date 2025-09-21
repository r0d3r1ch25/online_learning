# ml_api/service.py

import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from model_manager import ModelManager
from metrics_manager import MetricsManager
from river import stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Online ML API")

# Configuration - hardcoded for simplicity
FORECAST_HORIZON = 1
NUM_FEATURES = 12

# Models and simple imputation
mean_imputer = stats.Mean()
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
        "model_name": f"River {model_manager.model_name.replace('_', ' ').title()}",
        "model_version": "0.22.0",
        "forecast_horizon": 1,
        "max_features": 12,
        "regression_model": True,
        "available_models": ["linear_regression", "ridge_regression", "lasso_regression", "decision_tree", "bagging_regressor"]
    }

@app.post("/train")
def train(request: TrainRequest):
    """Train model with target and generate metrics"""
    try:
        validated_features = _validate_features(request.features)
        
        # Make prediction before training for metrics
        try:
            pred = model_manager.predict(validated_features)
            metrics_manager.add("default", request.target, pred)
        except:
            # First few observations may not have enough data for prediction
            pass
            
        # Train model
        model_manager.train(validated_features, request.target)
        return {"message": "Model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict(request: PredictRequest):
    """Predict multiple steps ahead using HoltWinters forecasting"""
    try:
        # Validate features (not used by HoltWinters but kept for compatibility)
        validated_features = _validate_features(request.features)
        
        # Get multi-step forecast from HoltWinters
        forecast_values = model_manager.predict_multi_step(validated_features)
        forecast = [{"value": val} for val in forecast_values]
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _validate_features(features: Dict[str, float]) -> Dict[str, float]:
    """Validate features and warn about unknown inputs"""
    expected_inputs = {f"in_{i}" for i in range(1, 13)}  # in_1 to in_12
    validated = {}
    
    # Check for unknown inputs
    for key in features:
        if key not in expected_inputs:
            logging.warning(f"Unknown input feature: {key}")
        else:
            validated[key] = features[key]
    
    # Simple mean imputation for missing features
    # Update mean with available values
    for value in validated.values():
        mean_imputer.update(value)
    
    # Fill missing features with current mean or 0.0 if no data
    mean_value = mean_imputer.get() if mean_imputer.n > 0 else 0.0
    
    for i in range(1, 13):  # in_1 to in_12
        input_key = f"in_{i}"
        if input_key not in validated:
            validated[input_key] = mean_value
    
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
