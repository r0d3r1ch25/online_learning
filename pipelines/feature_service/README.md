# Feature Service

Lag feature extraction service with Redis persistence for time series data. Calculates lag features and outputs model-ready format for the model service.

## Overview

The Feature Service processes time series observations and extracts lag features in a format ready for consumption by the Model Service. It maintains internal buffers for each time series and outputs features based on N_LAGS configuration.

## Key Features

- **Lag Feature Calculation**: Computes up to 15 lag features from time series data
- **Model-Ready Output**: Returns features in `in_1` to `in_15` format for direct model input
- **Multiple Series Support**: Handles multiple independent time series via series_id
- **Redis Persistence**: Uses Redis FIFO lists for persistent lag storage with automatic fallback
- **Zero-Fill**: Missing lags are automatically filled with 0.0
- **Configurable Lags**: N_LAGS environment variable (currently set to 15 in deployment YAML)

## API Endpoints

### `GET /health`
Health check endpoint for Kubernetes probes.

**Response:**
```json
{
  "status": "healthy",
  "service": "feature_service"
}
```

### `GET /info`
Service information including configuration and series data.

**Response:**
```json
{
  "service": "feature_service",
  "max_lags": 15,
  "output_format": "model_ready_in_1_to_in_15",
  "series_info": {}
}
```

### `POST /add`
Add observation and extract lag features in model-ready format.

**Request:**
```json
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
    "in_5": 0.0,
    "in_6": 0.0,
    "in_7": 0.0,
    "in_8": 0.0,
    "in_9": 0.0,
    "in_10": 0.0,
    "in_11": 0.0,
    "in_12": 0.0,
    "in_13": 0.0,
    "in_14": 0.0,
    "in_15": 0.0
  },
  "target": 125.0,
  "available_lags": 3
}
```

### `GET /series/{series_id}`
Get information about a specific series.

**Response:**
```json
{
  "series_id": "default",
  "length": 5,
  "latest_value": 125.0,
  "available_lags": 5
}
```

## Feature Format

The service outputs features in model-ready format:
- `in_1`: Most recent previous observation (lag 1)
- `in_2`: Second most recent previous observation (lag 2)
- `in_3`: Third most recent previous observation (lag 3)
- ...
- `in_{N_LAGS}`: N_LAGS most recent previous observation

Missing lags are filled with `0.0`.

## Implementation Details

### Core Components

- **`main.py`**: FastAPI application entry point
- **`service.py`**: FastAPI service with endpoint definitions
- **`feature_manager.py`**: `LagFeatureManager` class with core logic

### LagFeatureManager Class

- **`add_observation()`**: Adds value to series buffer (deque with maxlen)
- **`extract_features()`**: Extracts lag features then adds current observation


### Configuration

Environment variable:
- `N_LAGS`: Number of lag features (set in deployment YAML, current value: 15)

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

### Sequential Processing
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

## Testing

Comprehensive test coverage in `tests/`:

- **`test_api.py`**: API endpoint testing
- **`test_features.py`**: Feature extraction logic
- **`test_integration.py`**: Integration scenarios

Key test scenarios:
- Health and info endpoints
- Single and multiple observations
- Lag pattern validation
- Model-ready format verification
- Edge cases (negative, zero, large values)
- Series information retrieval

## Configuration

### Changing Number of Lags
```bash
# Change via environment variable
export N_LAGS=8  # Creates in_1 to in_8

# Or in Docker
docker run -e N_LAGS=8 r0d3r1ch25/ml-features:latest

# Or in Kubernetes
env:
- name: N_LAGS
  value: "8"
```

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
observation = {"target": 125.0}

# To feature service
requests.post("http://feature-service:8001/add", json={
    "series_id": "default",
    "value": observation["target"]
})
```

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-features:latest`
- **Security**: Runs as non-root user `appuser` for enhanced security
- **Kubernetes**: Deployed in `ml-services` namespace
- **Port**: 8001
- **Health Check**: `/health` endpoint
- **CI/CD**: Automated build/push on changes to `pipelines/feature_service/**`

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/features_ci.yml`):

1. **Test Phase**:
   - Python 3.11 setup
   - Install dependencies
   - Run pytest tests with PYTHONPATH

2. **Build & Push Phase**:
   - Docker Buildx setup
   - Login to Docker Hub
   - Build for linux/arm64 platform
   - Push to `r0d3r1ch25/ml-features:latest`

## Architecture

```
Input: Time Series Value
         ↓
    Lag Calculation (deque buffer)
         ↓
   Model-Ready Features
         ↓
    Output: in_1 to in_{N_LAGS}
```

The service maintains internal state for each time series to calculate lag features efficiently using Python's deque with maxlen for automatic buffer management.