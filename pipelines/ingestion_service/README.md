# Data Ingestion Service

A streaming service that serves time series CSV data one observation at a time via REST API for online learning workflows.

## Overview

The ingestion service streams monthly time series data (1949-1960) with date inputs and integer targets. It maintains state to track current position and provides stream management capabilities.

## Features

- **Sequential Data Streaming**: Returns observations one by one from CSV data
- **Time Series Data**: Date strings (YYYY-MM) as input, integer values as targets  
- **Stream Management**: Reset stream to beginning, check status
- **Proper HTTP Status Codes**: 200 for data, 204 when stream is exhausted
- **Health Monitoring**: Health check endpoint for Kubernetes orchestration

## API Endpoints

### `GET /next`
Returns the next observation from the dataset.
- **200**: Returns observation data
- **204**: No more data available (stream exhausted)

**Response Format:**
```json
{
  "observation_id": 1,
  "input": "1949-01", 
  "target": 112,
  "remaining": 143
}
```

### `POST /reset`
Resets the stream to start from the beginning.
- **200**: Stream reset successfully

### `GET /status`
Returns current stream status.
- **200**: Current index, total observations, remaining count, completion status

### `GET /health`
Health check endpoint for Kubernetes probes.
- **200**: Service is healthy with total observation count

## Dataset

Sample time series data with 144 monthly observations from 1949-1960:
- **Input**: Date strings in YYYY-MM format
- **Target**: Integer values representing time series measurements

## Usage Example

```bash
# Get next observation
curl http://localhost:8002/next
# Returns: {"observation_id": 1, "input": "1949-01", "target": 112, "remaining": 143}

# Reset stream
curl -X POST http://localhost:8002/reset

# Check status
curl http://localhost:8002/status
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
docker build -t ml-ingestion .
docker run -p 8002:8002 ml-ingestion
```

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-ingestion:latest`
- **Kubernetes Port**: 8002
- **LoadBalancer**: Accessible at `http://<your-ip>:8002`
- **CI/CD**: Automated build/push on changes to `pipelines/ingestion_service/**`