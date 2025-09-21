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

### Add Observation and Extract Features
```bash
POST /add
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
    "in_1": 120.0,
    "in_2": 115.0,
    "in_3": 110.0,
    "in_4": 0.0,
    ...
    "in_12": 0.0
  },
  "target": 125.0,
  "available_lags": 3
}
```

### Series Information
```bash
GET /series/{series_id}
```

## Feature Format

The service outputs features in model-ready format:
- `in_1`: Most recent previous observation (lag 1)
- `in_2`: Second most recent previous observation (lag 2)
- `in_3`: Third most recent previous observation (lag 3)
- ...
- `in_12`: Twelfth most recent previous observation (lag 12)

Missing lags are filled with `0.0`.

## Usage Examples

### Basic Usage
```python
import requests

# Add observation and extract features
response = requests.post("http://localhost:8001/add", json={
    "series_id": "my_series",
    "value": 150.0
})

features = response.json()["features"]
# features is ready for model service input
```

### Complete Workflow Example
```python
import requests

# Sequential observations to build lag features
observations = [100.0, 105.0, 110.0, 115.0, 120.0]
series_id = "time_series_1"

for i, value in enumerate(observations):
    response = requests.post("http://localhost:8001/add", json={
        "series_id": series_id,
        "value": value
    })
    
    result = response.json()
    print(f"Observation {i+1}: target={result['target']}, lags={result['available_lags']}")
    
    # Show lag pattern development
    if i >= 2:  # After 3rd observation
        features = result['features']
        print(f"  in_1 (most recent): {features['in_1']}")
        print(f"  in_2 (lag_2): {features['in_2']}")
        print(f"  in_3 (lag_3): {features['in_3']}")
```

### Integration with Model Service
```bash
# Complete pipeline: observation -> features -> model training
curl -s -X POST http://localhost:8001/add \
  -H "Content-Type: application/json" \
  -d '{"series_id": "pipeline", "value": 125.0}' | \
jq '{features: .features, target: .target}' | \
curl -s -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  --data-binary @-
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

# Test integration with model service
bash ../../infra/test_features_model.sh
```

## Configuration

- **Max Lags**: 12 (configurable in LagFeatureManager)
- **Port**: 8001
- **Output Format**: in_1 to in_12 (model-ready)
- **Memory**: Internal deque buffers

## Integration

### With Model Service
The feature service output is directly compatible with model service input:

```python
# Feature service output (model-ready)
response = {"features": {"in_1": 120.0, "in_2": 115.0, ...}, "target": 125.0}

# Model service input (direct use)
requests.post("http://model-service:8000/train", json={
    "features": response["features"],
    "target": response["target"]
})
```

### With Ingestion Service
Receives observations from ingestion service and processes them:

```python
# From ingestion service
observation = {"value": 125.0, "series_id": "default"}

# To feature service
requests.post("http://feature-service:8001/add", json=observation)
```

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-features:latest`
- **Security**: Runs as non-root user `appuser` for enhanced security
- **Kubernetes**: Deployed in `ml-services` namespace
- **Port**: 8001
- **Health Check**: `/health` endpoint
- **CI/CD**: Automated build/push on changes to `pipelines/feature_service/**`

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