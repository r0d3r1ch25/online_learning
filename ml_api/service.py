# ml_api/service.py

import logging
from fastapi import FastAPI
from ml_api.model_manager import ModelManager
from ml_api.metrics_manager import MetricsManager

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Online ML API")

# -------------------------
# Dependency Injection placeholders
# -------------------------
# Right now simple initialization; can be replaced with real DI later
model_manager = ModelManager()
metrics_manager = MetricsManager()

# -------------------------
# ENDPOINTS
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_manager.model is not None}

@app.get("/info")
def info():
    return {
        "model_name": "River LinearRegression",
        "model_version": "0.22.0",
        "forecast_horizon_days": 1,
        "required_history_points": 1,
        "required_features": ["x"],
        "optional_exogenous_features": []
    }

@app.post("/train")
def train(data: dict):
    series_id = data["series_id"]
    for obs in data["observations"]:
        model_manager.train(series_id, obs["value"])
    return {"message": f"Model trained with {len(data['observations'])} observations"}

@app.post("/predict")
def predict(data: dict):
    series_id = data["series_id"]
    horizon = data.get("horizon", 1)
    forecast = []
    for _ in range(horizon):
        pred = model_manager.predict(series_id)
        forecast.append({"value": pred})
    return {"forecast": forecast}

@app.post("/predict_learn")
def predict_learn(data: dict):
    series_id = data["series_id"]
    y_real = data["y_real"]
    pred = model_manager.predict_learn(series_id, y_real)
    metrics_manager.add(series_id, y_real, pred)
    return {"prediction": pred}

@app.post("/feedback")
def feedback(data: dict):
    # Here you could save feedback to DB or Redis
    return {"message": "Feedback received successfully"}

@app.get("/metrics")
def metrics():
    # Prometheus-ready endpoint
    return metrics_manager.get_metrics()
