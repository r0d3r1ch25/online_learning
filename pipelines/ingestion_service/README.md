# Data Ingestion Service

A streaming service that serves time series CSV data one observation at a time via REST API for online learning workflows. Integrated with Argo CronWorkflow running every 2 minutes.

## Overview

The ingestion service streams monthly time series data (1949-1960) with date inputs and integer targets. It maintains state to track current position and provides stream management capabilities.

## Features

- **Sequential Data Streaming**: Returns observations one by one from CSV data
- **Time Series Data**: Date strings (YYYY-MM) as input, integer values as targets  
- **Stream Management**: Reset stream to beginning, check status
- **Proper HTTP Status Codes**: 200 for data, 204 when stream is exhausted
- **Health Monitoring**: Health check endpoint for Kubernetes orchestration

## API Endpoints

### `GET /health`
Health check endpoint for Kubernetes probes.
- **200**: Service is healthy with total observation count

**Response:**
```json
{
  "status": "healthy",
  "total_observations": 144
}
```

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

**Response:**
```json
{
  "message": "Stream reset to beginning",
  "total_observations": 144
}
```

### `GET /status`
Returns current stream status.
- **200**: Current index, total observations, remaining count, completion status

**Response:**
```json
{
  "current_index": 5,
  "total_observations": 144,
  "remaining": 139,
  "completed": false
}
```

## Dataset

Sample time series data with 144 monthly observations from 1949-1960:
- **Input**: Date strings in YYYY-MM format
- **Target**: Integer values representing time series measurements
- **File**: `data.csv` in service directory

## Usage Example

```bash
# Health check
curl http://localhost:8002/health

# Get next observation
curl http://localhost:8002/next
# Returns: {"observation_id": 1, "input": "1949-01", "target": 112, "remaining": 143}

# Reset stream
curl -X POST http://localhost:8002/reset

# Check status
curl http://localhost:8002/status
```

## Implementation Details

### Core Components

- **`main.py`**: FastAPI application with endpoint definitions
- **`service.py`**: `DataIngestionService` class with core logic
- **`data.csv`**: Time series dataset (144 observations)

### Service Class Methods

- `load_data()`: Loads CSV data using pandas
- `get_next_observation()`: Returns next observation or None if exhausted
- `reset_stream()`: Resets current index to 0
- `get_status()`: Returns current stream state
- `get_health()`: Returns health status

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

## Testing

Comprehensive test coverage in `tests/test_ingestion.py`:

- Health endpoint validation
- Stream reset functionality
- Sequential observation retrieval
- Stream exhaustion (204 status code)
- Status endpoint verification

## Deployment

- **Docker Image**: `r0d3r1ch25/ml-ingestion:latest`
- **Security**: Runs as non-root user `appuser` for enhanced security
- **Kubernetes Port**: 8002
- **LoadBalancer**: Accessible at `http://<your-ip>:8002`
- **CI/CD**: Automated build/push on changes to `pipelines/ingestion_service/**`

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ingestion.yml`):

1. **Test Phase**:
   - Python 3.11 setup
   - Install dependencies
   - Run pytest tests
   - Docker build test
   - Container health check

2. **Build & Push Phase**:
   - Docker Buildx setup
   - Login to Docker Hub
   - Build for linux/arm64 platform
   - Push to `r0d3r1ch25/ml-ingestion:latest`

## Integration

Works seamlessly with other services in the ML pipeline:

```bash
# Complete pipeline example
curl -s http://localhost:8002/next | \
  jq '{series_id: "pipeline_test", value: .target}' | \
  curl -s -X POST -H "Content-Type: application/json" \
    --data-binary @- http://localhost:8001/add
```

The ingestion service provides the data source for the feature extraction and model training pipeline, orchestrated by Argo Workflows every 2 minutes with parallel model training.