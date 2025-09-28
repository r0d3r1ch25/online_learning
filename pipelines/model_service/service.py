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

app = FastAPI(title="Online-ML")



# Models
model_manager = ModelManager()
metrics_manager = MetricsManager()

class PredictRequest(BaseModel):
    features: Dict[str, float]

class PredictLearnRequest(BaseModel):
    features: Dict[str, float]
    target: float

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_manager.model is not None}





@app.post("/predict_learn")
def predict_learn(request: PredictLearnRequest):
    """Predict then learn from target"""
    try:
        pred = model_manager.predict_learn(request.features, request.target)
        metrics_manager.add("default", request.target, pred)
        return {"prediction": pred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_many")
def predict_many(request: PredictRequest):
    """Predict 5 steps ahead recursively"""
    try:
        predictions = model_manager.predict_many(request.features, steps=5)
        forecast = [{"step": i+1, "value": round(pred, 6)} for i, pred in enumerate(predictions)]
        
        # Track predict_many usage in metrics
        metrics_manager.add_predict_many("default", [pred for pred in predictions])
        
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model_metrics")
def model_metrics():
    """Get comprehensive model performance metrics and statistics"""
    metrics_data = metrics_manager.get_metrics()
    
    # Add River model information
    try:
        model_info = {
            "model_type": str(type(model_manager.model).__name__),
            "model_name": model_manager.model_name,
            "model_str": str(model_manager.model)[:200],
        }
        
        # Try to get model attributes safely
        try:
            if hasattr(model_manager.model, '__dict__'):
                safe_attrs = {}
                for k, v in model_manager.model.__dict__.items():
                    if not k.startswith('_'):
                        try:
                            safe_attrs[k] = str(v)[:100]
                        except:
                            safe_attrs[k] = str(type(v).__name__)
                model_info["model_attributes"] = safe_attrs
        except:
            model_info["model_attributes"] = {}
            
    except Exception as e:
        model_info = {
            "model_name": model_manager.model_name,
            "error": "Could not extract model info"
        }
    
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
        # Rolling metrics for each window size
        for metric_name, value in data.items():
            if metric_name.endswith(('_5', '_10', '_20')):
                base_metric = metric_name.rsplit('_', 1)[0]
                window_size = metric_name.rsplit('_', 1)[1]
                prometheus_output.append(f"# HELP ml_model_{metric_name} {base_metric.upper()} over {window_size} predictions")
                prometheus_output.append(f"# TYPE ml_model_{metric_name} gauge")
                prometheus_output.append(f'ml_model_{metric_name}{{series="{series_id}",model="{model_manager.model_name}"}} {value}')
        
        prometheus_output.append(f"# HELP ml_model_predictions_total Total number of model learning operations")
        prometheus_output.append(f"# TYPE ml_model_predictions_total counter")
        prometheus_output.append(f'ml_model_predictions_total{{series="{series_id}",model="{model_manager.model_name}"}} {data.get("count", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_last_prediction Last prediction value")
        prometheus_output.append(f"# TYPE ml_model_last_prediction gauge")
        prometheus_output.append(f'ml_model_last_prediction{{series="{series_id}",model="{model_manager.model_name}"}} {data.get("last_prediction", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_last_actual Last actual value")
        prometheus_output.append(f"# TYPE ml_model_last_actual gauge")
        prometheus_output.append(f'ml_model_last_actual{{series="{series_id}",model="{model_manager.model_name}"}} {data.get("last_actual", 0)}')
        
        prometheus_output.append(f"# HELP ml_model_last_error Last prediction error")
        prometheus_output.append(f"# TYPE ml_model_last_error gauge")
        prometheus_output.append(f'ml_model_last_error{{series="{series_id}",model="{model_manager.model_name}"}} {data.get("last_error", 0)}')
        
        # Forecast metrics - all 5 steps as comma-separated values
        if "forecast" in data:
            forecast_values = ",".join([str(val) for val in data["forecast"]])
            prometheus_output.append(f"# HELP ml_model_forecast_steps 5-step forecast values (comma-separated)")
            prometheus_output.append(f"# TYPE ml_model_forecast_steps gauge")
            prometheus_output.append(f'ml_model_forecast_steps{{series="{series_id}",model="{model_manager.model_name}",values="{forecast_values}"}} 1')
    
    from fastapi import Response
    return Response(content="\n".join(prometheus_output) + "\n", media_type="text/plain")
