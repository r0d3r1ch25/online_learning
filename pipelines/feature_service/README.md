# Feature Service

Lag feature extraction service for time series data. Calculates lag features and outputs model-ready format for the model service.

## Overview

The Feature Service processes time series observations and extracts lag features in a format ready for consumption by the Model Service. It maintains internal buffers for each time series and outputs features as `in_1` to `in_12` format.

## Key Features

- **Lag Feature Calculation**: Computes up to 12 lag features from time series data
- **Model-Ready Output**: Returns features in `in_1` to `in_12` format for direct model input
- **Multiple Series Support**: Handles multiple independent time series
- **Stateful Processing**: Maintains internal buffers for lag calculation
- **Zero-Fill**: Missing lags are automatically filled with 0.0

## API Endpoints

### Health Check
```bash
GET /health
```

### Service Information
```bash
GET /info
```

### Extract Features
```bash
POST /extract
{
  "series_id": "default",
  "value": 125.0
}
```

**Response:**
```json
{
  "series_id": "default",
  "features": {
    "in_1": 125.0,
    "in_2": 120.0,
    "in_3": 115.0,
    "in_4": 0.0,
    ...
    "in_12": 0.0
  },
  "available_lags": 3
}
```

### Series Information
```bash
GET /series/{series_id}
```

## Feature Format

The service outputs features in model-ready format:
- `in_1`: Most recent value (current observation)
- `in_2`: Lag 1 (previous observation)
- `in_3`: Lag 2 (two observations ago)
- ...
- `in_12`: Lag 11 (eleven observations ago)

Missing lags are filled with `0.0`.

## Usage Example

```python
import requests

# Extract features from new observation
response = requests.post("http://localhost:8001/extract", json={
    "series_id": "my_series",
    "value": 150.0
})

features = response.json()["features"]
# features is ready for model service input
```

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
docker build -t ml-features .

# Run container
docker run -p 8001:8001 ml-features
```

### Test Deployed Service
```bash
# Test locally
python3 ../../infra/test_features_api.py

# Test deployed service
python3 ../../infra/test_features_api.py http://<your-ip>:8001
```

## Configuration

- **Max Lags**: 12 (configurable in LagFeatureManager)
- **Port**: 8001
- **Output Format**: in_1 to in_12 (model-ready)

## Integration

### With Model Service
The feature service output is directly compatible with model service input:

```python
# Feature service output
features = {"in_1": 125.0, "in_2": 120.0, ..., "in_12": 0.0}

# Model service input (ready to use)
requests.post("http://model-service:8000/train", json={
    "features": features,
    "target": 130.0
})
```

### With Ingestion Service
Receives observations from ingestion service and processes them:

```python
# From ingestion service
observation = {"value": 125.0, "series_id": "default"}

# To feature service
requests.post("http://feature-service:8001/extract", json=observation)
```

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-features:latest`
- **Kubernetes**: Deployed in `ml-services` namespace
- **Port**: 8001
- **Health Check**: `/health` endpoint

## Architecture

```
Input: Time Series Value
         ↓
    Lag Calculation
         ↓
   Model-Ready Features
         ↓
    Output: in_1 to in_12
```

The service maintains internal state for each time series to calculate lag features efficiently.