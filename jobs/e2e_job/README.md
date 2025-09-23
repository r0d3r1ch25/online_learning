# E2E Job

End-to-end pipeline job for Argo Workflows that orchestrates the complete ML pipeline every 2 minutes with parallel model training.

## Overview

This job runs the complete online learning pipeline:
1. Fetches observations from ingestion service
2. Extracts features from feature service (15 lag features)
3. Performs parallel model prediction and learning (Linear, Ridge, KNN)
4. Retrieves updated model metrics from all models

## Features

- **Lightweight**: Based on `python:3.11-alpine`
- **Minimal dependencies**: Only `requests` library
- **Proper error handling**: HTTP status codes and timeouts
- **Real-time logging**: Timestamped logs with flush
- **Service integration**: Connects to all ML services via Kubernetes service discovery
- **Stream exhaustion handling**: Graceful exit when no more data available

## Implementation Details

### Core Components

- **`pipeline.py`**: Main pipeline orchestration logic
- **`Dockerfile`**: Alpine-based container image
- **`requirements.txt`**: Python dependencies (requests only)
- **`tests/`**: Unit tests with mocked services

### Pipeline Flow

1. **GET** `/next` from ingestion service
2. **POST** `/add` to feature service with observation value
3. **POST** `/predict_learn` to model service with features and target
4. **GET** `/model_metrics` from model service for updated performance

### Service URLs

Hardcoded for Kubernetes service discovery:
- `INGESTION_URL`: `http://ingestion-service.ml-services.svc.cluster.local:8002`
- `FEATURE_URL`: `http://feature-service.ml-services.svc.cluster.local:8001`
- `MODEL_URL`: `http://model-service.ml-services.svc.cluster.local:8000`

### Configuration

- **Timeout**: 10 seconds for all HTTP requests
- **Series ID**: `features_pipeline` for identification
- **Error Handling**: Proper exit codes for Argo Workflows

## Usage

### Local Development
```bash
# Run tests
PYTHONPATH=. pytest tests/ -v

# Build image
docker build -t ml-e2e-job .

# Run locally (requires services running)
docker run --network host ml-e2e-job
```

### Kubernetes Deployment
```bash
# Deploy CronWorkflow
kubectl apply -f ../../infra/workflows/v1/online-learning-pipeline-v1.yaml -n argo

# Monitor execution
argo list -n argo
argo logs -n argo -f online-learning-cron-v1-<timestamp>
```

## Pipeline Execution Example

### Successful Run Log Output
```
2024-01-15 10:30:00: === E2E PIPELINE START ===
2024-01-15 10:30:00: [1/4] SUCCESS: Observation 1: target=112, remaining=143
2024-01-15 10:30:00: [2/4] SUCCESS: Features extracted: 15 inputs, 0 lags available
2024-01-15 10:30:00:   Feature breakdown:
2024-01-15 10:30:00:     in_1: 0.0
2024-01-15 10:30:00:     in_2: 0.0
2024-01-15 10:30:00:     ...
2024-01-15 10:30:00:     in_15: 0.0
2024-01-15 10:30:00: [3/4] SUCCESS: Model prediction: 0.0000
2024-01-15 10:30:00:   Actual: 112 | Prediction: 0.0000 | Error: 112.0000
2024-01-15 10:30:00: [4/4] SUCCESS: Updated metrics: MAE=112.0000, RMSE=112.0000, Count=1
2024-01-15 10:30:00: === E2E PIPELINE COMPLETE: 2024-01-15 10:30:00 | Duration: 0.245s ===
```

### Stream Exhaustion
```
2024-01-15 10:35:00: INFO: No more observations available - stream exhausted
```

### Error Handling
```
2024-01-15 10:30:00: ERROR: HTTP request failed: Connection timeout
```

## Testing

Comprehensive unit tests in `tests/test_pipeline.py`:

### Test Coverage
- **Pipeline flow**: Complete workflow testing with mocked services
- **Error handling**: HTTP errors and connection failures
- **Stream exhaustion**: 204 status code handling
- **Feature logging**: Verbose output verification
- **Service mocking**: No actual services required for testing
- **CI/CD integration**: Tests run before image build

### Mock Responses
Tests use realistic mock responses that match actual service APIs:

```python
# Ingestion service mock
{"observation_id": 1, "input": "1949-01", "target": 112, "remaining": 143}

# Feature service mock
{"series_id": "argo_e2e_pipeline", "features": {"in_1": 0.0, ...}, "target": 112, "available_lags": 0}

# Model service mock
{"prediction": 0.0}

# Metrics mock
{"default": {"mae": 112.0, "rmse": 112.0, "count": 1}}
```

### Running Tests
```bash
cd jobs/e2e_job
PYTHONPATH=. pytest tests/ -v
```

## Docker Image

### Specifications
- **Registry**: `r0d3r1ch25/ml-e2e-job:latest`
- **Security**: Runs as non-root user `appuser` for enhanced security
- **Platform**: `linux/arm64` (macOS k3d compatible)
- **Base**: `python:3.11-alpine` (lightweight)
- **Size**: ~50MB
- **Dependencies**: Only `requests` library

### Dockerfile
```dockerfile
FROM python:3.11-alpine

# Create non-root user
RUN adduser -D -s /bin/sh appuser

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pipeline.py .

# Switch to non-root user
USER appuser

# Run pipeline
CMD ["python", "pipeline.py"]
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/e2e_job_ci.yml`):

1. **Test Phase**:
   - Python 3.11 setup
   - Install dependencies
   - Run pytest tests with PYTHONPATH

2. **Build & Push Phase**:
   - Docker Buildx setup
   - Login to Docker Hub
   - Build for linux/arm64 platform
   - Push to `r0d3r1ch25/ml-e2e-job:latest`

## Integration with Argo Workflows

### CronWorkflow Configuration
The job is designed to run as an Argo CronWorkflow:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: CronWorkflow
metadata:
  name: online-learning-cron-v1
  namespace: argo
spec:
  schedule: "*/2 * * * *"  # Every 2 minutes
  workflowSpec:
    templates:
    - name: e2e-pipeline
      container:
        image: r0d3r1ch25/ml-e2e-job:latest
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
```

### Workflow Management
```bash
# Start CronWorkflow
make argo-e2e

# Monitor workflows
argo list -n argo

# View logs
argo logs -n argo -f online-learning-cron-v1-<timestamp>

# Stop CronWorkflow
kubectl delete cronworkflow online-learning-cron-v1 -n argo
```

## Error Handling

The pipeline handles various error scenarios:

1. **HTTP Timeouts**: 10-second timeout for all requests
2. **Connection Errors**: Proper error logging and exit codes
3. **Stream Exhaustion**: Graceful exit with status code 0
4. **Service Unavailable**: Error logging and exit code 1
5. **Invalid Responses**: JSON parsing error handling

## Monitoring

The job integrates with the monitoring stack:

- **Logs**: Collected by Promtail and stored in Loki
- **Metrics**: Model metrics updated after each run
- **Grafana**: Pipeline execution logs visible in dashboards
- **Argo UI**: Workflow execution status and history

## Performance

Typical execution metrics:
- **Duration**: 200-500ms per pipeline run
- **Memory**: ~64MB peak usage
- **CPU**: Minimal usage (100m request)
- **Network**: 4 HTTP requests per execution

The lightweight design ensures efficient resource usage in Kubernetes environments.