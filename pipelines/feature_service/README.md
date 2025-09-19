# Feature Service

Time series feature extraction service that computes lag features for online machine learning workflows.

## Overview

The feature service extracts lag features from time series observations, supporting up to 12 lags. It loads initial data from CSV and provides REST API for adding observations and retrieving features for online learning.

## Features

- **Lag Feature Extraction**: Computes lag features (up to 12 lags) for time series data
- **Initial Data Loading**: Loads air passenger data from CSV on startup
- **Series Management**: Handles multiple time series with unique series IDs
- **REST API**: Add observations and retrieve features via HTTP endpoints
- **Online Learning Ready**: Designed for incremental/online ML workflows

## API Endpoints

### `GET /health`
Service health check for Kubernetes probes.
- **200**: Service is healthy

### `GET /info`
Service information and series status.
- **200**: Max lags, series information

### `POST /add_observation`
Add new observation to a time series.

**Request:**
```json
{
  "series_id": "air_passengers",
  "value": 150.0
}
```

### `POST /features`
Get lag features for a time series.

**Request:**
```json
{
  "series_id": "air_passengers", 
  "num_lags": 5
}
```

**Response:**
```json
{
  "series_id": "air_passengers",
  "features": {
    "lag_1": 145.0,
    "lag_2": 140.0,
    "lag_3": 135.0
  },
  "available_lags": 3
}
```

### `GET /features/{series_id}`
Get lag features for a specific series (GET endpoint).
- Query parameter: `num_lags` (optional)

## Feature Engineering

The service computes lag features using the `LagFeatureManager`:
- **Max Lags**: 12 historical values
- **Feature Names**: `lag_1`, `lag_2`, ..., `lag_n`
- **Series Support**: Multiple independent time series

## Usage Example

```bash
# Add observation
curl -X POST "http://localhost:8001/add_observation" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "sales", "value": 150}'

# Get features
curl -X POST "http://localhost:8001/features" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "sales", "num_lags": 5}'

# Get service info
curl http://localhost:8001/info
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
docker build -t ml-features .
docker run -p 8001:8001 fti-features
```

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-features:latest`
- **Kubernetes Port**: 8001
- **LoadBalancer**: Accessible at `http://<your-ip>:8001`
- **CI/CD**: Automated build/push on changes to `pipelines/feature_service/**`
- **Initial Data**: Loads air passenger data from `../ingestion_service/data.csv` on startup