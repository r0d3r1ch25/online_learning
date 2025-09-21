# Model Service

Online machine learning service with multiple regression models for real-time training and prediction.

## Overview

The model service provides online learning capabilities with support for multiple regression algorithms. It processes model-ready features from the feature service and performs real-time training and prediction with comprehensive metrics tracking.

## Features

- **Feature Agnostic**: Accepts any number of input features dynamically
- **Multiple Regression Models**: Linear, Ridge, Lasso, Decision Tree, Bagging Regressor
- **Easy Model Switching**: Via MODEL_NAME environment variable
- **Online Learning**: Real-time predict-then-learn workflow
- **Single-Step Prediction**: FORECAST_HORIZON=1 for simplified predictions
- **No Feature Validation**: River handles any feature set automatically
- **Performance Metrics**: MAE, MSE, RMSE tracking
- **Prometheus Integration**: Metrics endpoint for monitoring
- **River Integration**: Leverages River's adaptive capabilities

## Model Selection

Change the model by setting the MODEL_NAME environment variable:

```bash
# Available models:
export MODEL_NAME=linear_regression    # Default - Linear Regression with StandardScaler
export MODEL_NAME=ridge_regression     # Ridge Regression (L2 regularization)
export MODEL_NAME=lasso_regression     # Lasso Regression (L1 regularization)  
export MODEL_NAME=decision_tree        # Hoeffding Tree Regressor
export MODEL_NAME=bagging_regressor    # Bagging Regressor with Trees
```

## API Endpoints

### `POST /train`
Train the model with features and target value.
- Generates metrics by predicting before training
- Updates model with new observation

**Request:**
```json
{
  "features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0},
  "target": 130.0
}
```

### `POST /predict`
Make prediction using current model state.
- Returns single-step forecast
- Does not update model

**Request:**
```json
{
  "features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0}
}
```

**Response:**
```json
{
  "forecast": [{"value": 135.2}]
}
```

### `POST /predict_learn`
Predict then learn from actual value (online learning).
- Makes prediction first
- Updates model with actual value
- Generates metrics comparing prediction vs actual

**Request:**
```json
{
  "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0},
  "target": 140.0
}
```

**Response:**
```json
{
  "prediction": 138.7
}
```

### `GET /model_metrics`
Get comprehensive model performance metrics.

**Response:**
```json
{
  "default": {
    "mae": 2.45,
    "mse": 8.12,
    "rmse": 2.85,
    "count": 15,
    "last_prediction": 138.7,
    "last_actual": 140.0,
    "last_error": -1.3
  }
}
```

### `GET /metrics`
Prometheus-compatible metrics endpoint.

### `GET /info`
Service information including current model.

**Response:**
```json
{
  "model_name": "River Linear Regression",
  "model_version": "0.22.0",
  "forecast_horizon": 1,
  "feature_agnostic": true,
  "regression_model": true,
  "available_models": ["linear_regression", "ridge_regression", "lasso_regression", "decision_tree", "bagging_regressor"]
}
```

## Configuration

Environment variables:
- `MODEL_NAME`: Model type (default: "linear_regression")

Hardcoded values:
- `FORECAST_HORIZON`: 1 (single-step prediction)
- `NUM_FEATURES`: 12 (in_1 to in_12)

## Usage Examples

### Basic Training and Prediction
```bash
# Set model type
export MODEL_NAME=ridge_regression

# Train model
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 125.0, "in_2": 120.0}, "target": 130.0}'

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 130.0, "in_2": 125.0}}'

# Online learning (predict then learn)
curl -X POST http://localhost:8000/predict_learn \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 130.0, "in_2": 125.0}, "target": 135.0}'

# Check metrics
curl http://localhost:8000/model_metrics
```

### Complete Workflow with All 12 Features
```bash
# Train with all 12 input features
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
      "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
      "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
    },
    "target": 130.0
  }'

# Predict with all features
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 115.0,
      "in_5": 110.0, "in_6": 105.0, "in_7": 100.0, "in_8": 95.0,
      "in_9": 90.0, "in_10": 85.0, "in_11": 80.0, "in_12": 75.0
    }
  }'
```

### Monitoring and Metrics
```bash
# Get comprehensive model metrics
curl http://localhost:8000/model_metrics
# Returns: {"default": {"mae": 2.45, "mse": 8.12, "rmse": 2.85, "count": 15, ...}}

# Get Prometheus metrics
curl http://localhost:8000/metrics
# Returns: Prometheus format metrics for monitoring

```

### Feature Flexibility
```bash
# Works with any number of features
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 140.0, "in_3": 130.0, "custom_feature": 99.0}}'

# River adapts to any feature set
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"features": {"lag_1": 100.0, "trend": 0.5}, "target": 150.0}'
```

## Integration with Feature Service

The model service expects model-ready features from the feature service:

```bash
# Feature service output -> Model service input
{
  "features": {"in_1": 120.0, "in_2": 115.0, ...},  # Previous observations as lags
  "target": 125.0                                    # Current observation as target
}
```

## Development

### Run locally
```bash
pip install -r requirements.txt
python main.py
```

### Run tests
```bash
pytest tests/ -v
```

### Docker
```bash
docker build -t ml-model .
docker run -p 8000:8000 -e MODEL_NAME=ridge_regression ml-model
```

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-model:latest`
- **Security**: Runs as non-root user `appuser` for enhanced security
- **Kubernetes Port**: 8000
- **LoadBalancer**: Accessible at `http://<your-ip>:8000`
- **CI/CD**: Automated build/push on changes to `pipelines/model_service/**`