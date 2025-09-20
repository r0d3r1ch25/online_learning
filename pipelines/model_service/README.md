# Model Service

Online machine learning service using River for real-time training and prediction with time series data.

## Overview

The Model Service provides stateless online machine learning capabilities using River's LinearRegression algorithm. It accepts model-ready features from the Feature Service and performs real-time training and prediction with comprehensive metrics tracking.

## Key Features

- **Online Learning**: Real-time model training with River LinearRegression
- **Stateless Design**: No internal memory management, features provided externally
- **Up to 12 Inputs**: Supports in_1 to in_12 feature format from Feature Service
- **Imputation**: Missing features handled by River StatImputer with Mean strategy
- **Fixed Horizon**: 3-step ahead predictions (configurable at build time)
- **Metrics Tracking**: Comprehensive MAE, MSE, RMSE performance monitoring
- **Prometheus Integration**: Built-in metrics endpoint for monitoring stack

## API Endpoints

### Health Check
```bash
GET /health
```

### Service Information
```bash
GET /info
```

### Train Model
```bash
POST /train
{
  "features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0},
  "target": 130.0
}
```

### Predict (3-Step Horizon)
```bash
POST /predict
{
  "features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0}
}
```

**Response:**
```json
{
  "forecast": [
    {"value": 135.2},
    {"value": 135.2},
    {"value": 135.2}
  ]
}
```

### Online Learning (Predict then Learn)
```bash
POST /predict_learn
{
  "features": {"in_1": 135.0, "in_2": 130.0},
  "target": 140.0
}
```

### Model Performance Metrics
```bash
GET /model_metrics
```

**Response:**
```json
{
  "default": {
    "count": 5,
    "mae": 2.45,
    "mse": 8.12,
    "rmse": 2.85,
    "last_prediction": 135.2,
    "last_actual": 140.0,
    "last_error": 4.8
  }
}
```

### Prometheus Metrics
```bash
GET /metrics
```

### Submit Feedback
```bash
POST /feedback
{
  "message": "Model performing well"
}
```

## Configuration

- **Forecast Horizon**: 3 steps (configurable via FORECAST_HORIZON env var)
- **Max Features**: 12 (configurable via NUM_FEATURES env var)
- **Port**: 8000
- **Imputation Strategy**: Mean imputation for missing features

## Input Validation

- **Expected Features**: in_1 to in_12 format from Feature Service
- **Missing Features**: Handled by River StatImputer with Mean strategy
- **Unknown Features**: Logged as warnings but ignored
- **Feature Range**: No restrictions, handles any numeric values

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python main.py

# Run tests
pytest tests/ -v
```

### Docker
```bash
# Build image
docker build -t ml-model .

# Run container
docker run -p 8000:8000 ml-model
```

### Test Deployed Service
```bash
# Test locally
python3 ../../infra/test_model_api.py

# Test deployed service
python3 ../../infra/test_model_api.py http://<your-ip>:8000

# Test integration with feature service
bash ../../infra/test_features_model.sh
```

## Integration

### With Feature Service
Receives model-ready features directly from Feature Service:

```python
# Feature service provides
features = {"in_1": 125.0, "in_2": 120.0, ..., "in_12": 0.0}

# Model service consumes directly
requests.post("http://model-service:8000/train", json={
    "features": features,
    "target": 130.0
})
```

### Monitoring Integration
- **Prometheus**: Scrapes `/metrics` endpoint every 30 seconds
- **Grafana**: Visualizes model performance metrics
- **Metrics Available**: MAE, MSE, RMSE, prediction count, last values

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-model:latest`
- **Kubernetes**: Deployed in `ml-services` namespace
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Resource Limits**: 512Mi memory, 500m CPU

## Performance Metrics

The service tracks comprehensive performance metrics:

- **MAE**: Mean Absolute Error
- **MSE**: Mean Squared Error
- **RMSE**: Root Mean Squared Error
- **Count**: Total number of predictions
- **Last Values**: Most recent prediction, actual, and error

## Architecture

```
Input: Model-Ready Features (in_1 to in_12)
         ↓
    Feature Imputation (River StatImputer)
         ↓
    Online Learning (River LinearRegression)
         ↓
    Prediction/Training + Metrics Tracking
         ↓
    Output: Predictions + Performance Metrics
```

The service is designed for high-throughput online learning scenarios with real-time feature processing and comprehensive monitoring capabilities.