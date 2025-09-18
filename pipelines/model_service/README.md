# Model Service

Online machine learning service using River for real-time model training and prediction with performance tracking.

## Overview

The model service provides online/incremental learning capabilities using River's LinearRegression. It supports real-time training, prediction, and performance metrics tracking for time series forecasting.

## Features

- **Online Learning**: Real-time model training with River LinearRegression
- **Prediction & Learning**: Combined predict-then-learn workflow
- **Performance Tracking**: Metrics collection and monitoring
- **Multi-Series Support**: Handle multiple time series with unique series IDs
- **Health Monitoring**: Kubernetes-ready health checks

## API Endpoints

### `GET /health`
Service health check for Kubernetes probes.
- **200**: Service status and model loaded state

### `GET /info`
Model and service information.
- **200**: Model details, version, requirements

**Response:**
```json
{
  "model_name": "River LinearRegression",
  "model_version": "0.22.0", 
  "forecast_horizon_days": 1,
  "required_history_points": 1,
  "required_features": ["x"],
  "optional_exogenous_features": []
}
```

### `POST /train`
Train model with new observations.

**Request:**
```json
{
  "series_id": "air_passengers",
  "observations": [
    {"value": 112},
    {"value": 118}
  ]
}
```

### `POST /predict`
Get predictions for time series.

**Request:**
```json
{
  "series_id": "air_passengers",
  "horizon": 1
}
```

### `POST /predict_learn`
Predict and learn from real values (online learning).

**Request:**
```json
{
  "series_id": "air_passengers", 
  "y_real": 125.0
}
```

**Response:**
```json
{
  "prediction": 123.5
}
```

### `POST /feedback`
Submit feedback for model improvement.
- **200**: Feedback received successfully

### `GET /metrics`
Performance metrics (Prometheus-ready endpoint).
- **200**: Model performance metrics by series

## Online Learning Workflow

1. **Predict**: Get prediction for next value
2. **Learn**: Update model with actual observed value
3. **Track**: Record prediction accuracy metrics
4. **Repeat**: Continue with next observation

## Components

- **ModelManager**: Handles River LinearRegression models per series
- **MetricsManager**: Tracks prediction accuracy and performance
- **FastAPI Service**: REST API endpoints for ML operations

## Usage Example

```bash
# Check service health
curl http://localhost:8000/health

# Get model info
curl http://localhost:8000/info

# Train model
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "sales", "observations": [{"value": 100}]}'

# Predict and learn
curl -X POST "http://localhost:8000/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "sales", "y_real": 105.0}'

# Get metrics
curl http://localhost:8000/metrics
```

## Development

### Run locally
```bash
pip install -r requirements.txt
python main.py
```

### Run tests
```bash
PYTHONPATH=. pytest tests/ -v
```

### Docker
```bash
docker build -t fti-model .
docker run -p 8000:8000 fti-model
```

## Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## Deployment

- **Docker Image**: `r0d3r1ch25/fti-model:latest`
- **Kubernetes Port**: 8000
- **LoadBalancer**: Accessible at `http://<your-ip>:8000`
- **CI/CD**: Automated build/push on changes to `pipelines/model_service/**`
- **Dependencies**: River for online learning, FastAPI for REST API