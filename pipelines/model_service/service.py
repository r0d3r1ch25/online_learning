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
FORECAST_HORIZON = 1

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
        "model_name": f"River {model_manager.model_name.replace('_', ' ').title()}",
        "model_version": "0.22.0",
        "forecast_horizon": FORECAST_HORIZON,
        "feature_agnostic": True,
        "regression_model": True,
        "available_models": ["linear_regression", "ridge_regression", "lasso_regression", "decision_tree", "bagging_regressor"]
    }

@app.post("/train")
def train(request: TrainRequest):
    """Train model with target and generate metrics"""
    try:
        # Make prediction before training for metrics
        try:
            pred = model_manager.predict(request.features)
            metrics_manager.add("default", request.target, pred)
        except:
            # First few observations may not have enough data for prediction
            pass
            
        # Train model
        model_manager.train(request.features, request.target)
        return {"message": "Model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict(request: PredictRequest):
    """Predict using regression model"""
    try:
        # Get forecast from regression model
        forecast_values = model_manager.predict_multi_step(request.features)
        forecast = [{"value": val} for val in forecast_values]
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_learn")
def predict_learn(request: PredictLearnRequest):
    """Predict then learn from target"""
    try:
        pred = model_manager.predict_learn(request.features, request.target)
        metrics_manager.add("default", request.target, pred)
        return {"prediction": pred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model_metrics")
def model_metrics():
    """Get comprehensive model performance metrics and statistics"""
    metrics_data = metrics_manager.get_metrics()
    
    # Add River model information
    model_info = {
        "model_type": str(type(model_manager.model).__name__),
        "model_name": model_manager.model_name,
        "model_str": str(model_manager.model),
        "model_params": getattr(model_manager.model, '_get_params', lambda: {})() if hasattr(model_manager.model, '_get_params') else {},
    }
    
    # Try to get more detailed info from River model
    try:
        if hasattr(model_manager.model, '__dict__'):
            model_dict = {k: str(v) for k, v in model_manager.model.__dict__.items() if not k.startswith('_')}
            model_info["model_attributes"] = model_dict
    except:
        pass
    
    # Add model info to response
    if isinstance(metrics_data, dict) and "message" not in metrics_data:
        metrics_data["model_info"] = model_info
    elif isinstance(metrics_data, dict) and "message" in metrics_data:
        return {"message": metrics_data["message"], "model_info": model_info}
    
    return metrics_data

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
        
        prometheus_output.append(f"# HELP ml_model_mape Mean Absolute Percentage Error")
        prometheus_output.append(f"# TYPE ml_model_mape gauge")
        prometheus_output.append(f'ml_model_mape{{series="{series_id}"}} {data.get("mape", 0)}')
        
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
