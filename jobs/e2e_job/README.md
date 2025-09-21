# E2E Job

End-to-end pipeline job for Argo Workflows that orchestrates the complete ML pipeline.

## Overview

This job runs the complete online learning pipeline:
1. Fetches observations from ingestion service
2. Extracts features from feature service  
3. Performs model prediction and learning
4. Retrieves updated model metrics

## Features

- **Lightweight**: Based on `python:3.11-alpine`
- **Minimal dependencies**: Only `requests` library
- **Proper error handling**: HTTP status codes and timeouts
- **Real-time logging**: Timestamped logs with flush
- **Service integration**: Connects to all ML services

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

## Configuration

- **Service URLs**: Hardcoded for Kubernetes service discovery
- **Timeouts**: 10 seconds for all HTTP requests
- **Series ID**: `argo_e2e_pipeline` for identification

## Testing

Comprehensive unit tests with mocked service dependencies:

```bash
# Run tests locally
cd jobs/e2e_job
PYTHONPATH=. pytest tests/ -v
```

### Test Coverage
- **Pipeline flow**: Complete workflow testing
- **Error handling**: HTTP errors and stream exhaustion
- **Feature logging**: Verbose output verification
- **Service mocking**: No actual services required
- **CI/CD integration**: Tests run before image build

## Docker Image

- **Registry**: `r0d3r1ch25/ml-e2e-job:latest`
- **Security**: Runs as non-root user `appuser` for enhanced security
- **Platform**: `linux/arm64` (macOS k3d compatible)
- **Base**: `python:3.11-alpine` (lightweight)
- **Size**: ~50MB
- **CI/CD**: Automated test + build on changes to `jobs/e2e_job/**`