# Model Service

Simple stateless online machine learning service using River for real-time model training and prediction with build-time configuration.

## Overview

The model service is a **simple, stateless ML service** that accepts pre-computed features (in_1 to in_12) and provides online learning capabilities. All parameters are set at Docker build time - no runtime configuration needed.

## ✅ **YES - You can use UP TO 12 INPUTS** (in_1 to in_12)

## Features

- **Simple & Stateless**: No memory, no lag computation - pure ML service
- **Build-Time Configuration**: Forecast horizon and feature count set when building image
- **12 Input Features**: Support for in_1, in_2, ..., in_12 input features
- **Input Validation**: Handles missing features, warns about unknown inputs
- **Robust Error Handling**: Bulletproof validation and edge case handling
- **Online Learning**: Real-time model training with River LinearRegression
- **Comprehensive Metrics**: MAE, MSE, RMSE tracking via single /metrics endpoint

## Configuration (Build Time Only)

### Docker Build Arguments
- `FORECAST_HORIZON`: Number of steps to forecast (default: 3)
- `NUM_FEATURES`: Maximum number of input features (default: 12)

**Important**: Parameters are fixed at build time. To change them, rebuild the image.

## API Endpoints

### `GET /health`
Service health check for Kubernetes probes.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### `GET /info`
Service configuration and model information.

**Response:**
```json
{
  "model_name": "River LinearRegression",
  "model_version": "0.22.0",
  "forecast_horizon": 3,
  "max_features": 12,
  "stateless": true,
  "memory_managed_externally": true
}
```

### `POST /train`
Train model with pre-computed features and target value.

**Request (3 inputs):**
```json
{
  "features": {
    "in_1": 125.0,
    "in_2": 120.0,
    "in_3": 115.0
  },
  "target": 130.0
}
```

**Request (All 12 inputs):**
```json
{
  "features": {
    "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
    "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
    "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
  },
  "target": 130.0
}
```

**Response:**
```json
{
  "message": "Model trained successfully"
}
```

**Validation:**
- Missing features automatically filled with 0.0
- Unknown feature names trigger warnings but don't fail
- Invalid payload structure returns 422 validation error

### `POST /predict`
Generate multi-step forecast using provided features (fixed horizon).

**Request (3 inputs):**
```json
{
  "features": {
    "in_1": 130.0,
    "in_2": 125.0,
    "in_3": 120.0
  }
}
```

**Request (All 12 inputs):**
```json
{
  "features": {
    "in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 115.0,
    "in_5": 110.0, "in_6": 105.0, "in_7": 100.0, "in_8": 95.0,
    "in_9": 90.0, "in_10": 85.0, "in_11": 80.0, "in_12": 75.0
  }
}
```

**Response:**
```json
{
  "forecast": [
    {"value": 135.2},
    {"value": 136.1},
    {"value": 137.0}
  ]
}
```

**Notes:**
- Horizon is fixed at build time (no horizon parameter needed)
- Returns exactly `FORECAST_HORIZON` predictions (default: 3)
- Uses same features for all forecast steps
- Missing features automatically filled with 0.0

### `POST /predict_learn`
Predict then immediately learn from actual target (online learning workflow).

**Request (3 inputs):**
```json
{
  "features": {
    "in_1": 135.0,
    "in_2": 130.0,
    "in_3": 125.0
  },
  "target": 140.0
}
```

**Request (All 12 inputs):**
```json
{
  "features": {
    "in_1": 135.0, "in_2": 130.0, "in_3": 125.0, "in_4": 120.0,
    "in_5": 115.0, "in_6": 110.0, "in_7": 105.0, "in_8": 100.0,
    "in_9": 95.0, "in_10": 90.0, "in_11": 85.0, "in_12": 80.0
  },
  "target": 140.0
}
```

**Response:**
```json
{
  "prediction": 138.5
}
```

**Online Learning Process:**
1. **Predict**: Make prediction using current model state
2. **Learn**: Update model with actual target value
3. **Track**: Record prediction accuracy for metrics
4. **Return**: Prediction made before learning

### `POST /feedback`
Submit feedback for model improvement and monitoring.

**Request:**
```json
{
  "message": "Model performing well with new feature set"
}
```

**Response:**
```json
{
  "message": "Feedback received successfully"
}
```

### `GET /metrics` ⭐ **SINGLE SOURCE OF TRUTH FOR MODEL PERFORMANCE**
Comprehensive model performance metrics showing exactly how well the model is performing.

**Response (No predictions yet):**
```json
{
  "message": "No predictions available yet"
}
```

**Response (With performance data):**
```json
{
  "default": {
    "count": 15,
    "mae": 2.3456,
    "mse": 7.8912,
    "rmse": 2.8091,
    "last_prediction": 142.3,
    "last_actual": 145.0,
    "last_error": 2.7
  }
}
```

**Metrics Explained:**
- **count**: Total number of predictions made (sample size)
- **mae**: Mean Absolute Error - average absolute difference between predictions and actual values (lower = better)
- **mse**: Mean Squared Error - average squared difference, penalizes larger errors more (lower = better)
- **rmse**: Root Mean Squared Error - square root of MSE, same units as target variable (lower = better)
- **last_prediction**: Most recent prediction value made by the model
- **last_actual**: Most recent actual target value observed
- **last_error**: Absolute error of the most recent prediction

**Performance Interpretation:**
- **MAE < 5**: Excellent performance
- **MAE 5-10**: Good performance  
- **MAE 10-20**: Moderate performance
- **MAE > 20**: Poor performance (may need retraining)

## Input Features

### Feature Naming Convention
- **in_1** to **in_12**: Generic input features (12 maximum supported)
- **Flexible Usage**: Can represent lags, external variables, engineered features, or any numeric inputs
- **Validated Processing**: Unknown feature names trigger warnings but don't break the service

### Feature Handling & Validation
- **Missing Features**: Automatically filled with 0.0 (no errors thrown)
- **Unknown Features**: Logged as warnings, ignored in processing (service continues)
- **Edge Cases**: Handles negative values, zeros, and extreme numbers gracefully
- **Type Validation**: All features must be numeric (float/int)

### Input Examples
```json
// Minimal (3 features)
{"in_1": 125.0, "in_2": 120.0, "in_3": 115.0}

// Partial (missing features filled with 0.0)
{"in_1": 140.0, "in_5": 100.0, "in_12": 80.0}

// Full (all 12 features)
{
  "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
  "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
  "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
}

// With unknown features (warnings logged, unknowns ignored)
{"in_1": 145.0, "unknown_feature": 999.0, "lag_1": 100.0}
```

## Usage Examples

### Basic Training (3 inputs)
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0},
    "target": 130.0
  }'
```

### Training with All 12 Inputs
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
      "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
      "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
    },
    "target": 130.0
  }'
```

### Prediction (Fixed 3-Step Horizon)
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0}
  }'
```

### Prediction with All 12 Inputs
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 115.0,
      "in_5": 110.0, "in_6": 105.0, "in_7": 100.0, "in_8": 95.0,
      "in_9": 90.0, "in_10": 85.0, "in_11": 80.0, "in_12": 75.0
    }
  }'
```

### Online Learning Workflow
```bash
curl -X POST "http://localhost:8000/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0},
    "target": 140.0
  }'
```

### Check Model Performance
```bash
curl http://localhost:8000/metrics
```

### Edge Cases & Validation
```bash
# Missing features (automatically filled with 0.0)
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 140.0}}'

# Unknown features (warnings logged, ignored)
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 145.0,
      "unknown_feature": 999.0,
      "lag_1": 100.0
    }
  }'

# Extreme values (handled gracefully)
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {"in_1": -1000.0, "in_2": 0.0, "in_3": 999999.9},
    "target": 50.0
  }'
```

## Development

### Run Locally
```bash
pip install -r requirements.txt
python main.py
```

### Run Tests (Bulletproof Coverage)
```bash
PYTHONPATH=. pytest tests/ -v
```

**Test Coverage Includes:**
- Valid and invalid payloads
- Missing and unknown features
- Edge cases (negative, zero, extreme values)
- Warning validation with logging
- Error handling for malformed requests
- **Full 12 input features test**
- **Comprehensive metrics endpoint test**
- Online learning workflow validation

### Docker Build
```bash
# Default configuration (3 horizon, 12 features)
docker build -t fti-model .

# Custom configuration
docker build -t fti-model \
  --build-arg FORECAST_HORIZON=5 \
  --build-arg NUM_FEATURES=8 .
```

### Test Deployed Service
```bash
# Make script executable
chmod +x infra/test_model_api.sh

# Run comprehensive tests (includes 12 inputs and metrics examples)
./infra/test_model_api.sh
```

## Architecture

### 1. Simple Service ✅
- **Stateless Design**: No memory or state management
- **Pure ML Focus**: Only training and prediction logic
- **Minimal Implementation**: Essential functionality only

### 2. Build-Time Configuration ✅
- **No Runtime Environment Variables**: All parameters set at Docker build time
- **Immutable Configuration**: To change parameters, rebuild image
- **Kubernetes Clean**: No environment variables needed in deployment YAML

### 3. Fixed Horizon ✅
- **No Horizon Parameter**: Predict endpoint uses build-time horizon value
- **Consistent Output**: Always returns same number of predictions
- **Simplified API**: Fewer parameters to manage and validate

### 4. Bulletproof Tests ✅
- **Edge Cases**: Missing features, unknown inputs, extreme values
- **Validation Testing**: Warning detection, error handling
- **Comprehensive Coverage**: 17+ test scenarios covering all failure modes
- **12 Inputs Validation**: Full feature set testing

### 5. Generic Inputs ✅
- **in_1 to in_12**: Generic feature names (not domain-specific)
- **Flexible Usage**: Can represent any numeric features across projects
- **Robust Validation**: Input handling with warnings and auto-fill

### 6. Single Metrics Endpoint ✅
- **Unified /metrics**: Single source of truth for model performance
- **Comprehensive Data**: MAE, MSE, RMSE, count, and recent predictions
- **Real-time Updates**: Metrics update with each predict_learn call

## Deployment

- **Docker Image**: `r0d3r1ch25/fti-model:latest`
- **Kubernetes Port**: 8000
- **LoadBalancer Access**: `http://<your-ip>:8000`
- **CI/CD Pipeline**: Automated build/push on changes to `pipelines/model_service/**`
- **Configuration**: Build-time only (no runtime environment variables)

## Dependencies

- **River**: Online machine learning algorithms (LinearRegression + StandardScaler)
- **FastAPI**: REST API framework with automatic validation
- **Pydantic**: Request/response validation and serialization
- **Python Standard Library**: Math, logging, collections for metrics calculation