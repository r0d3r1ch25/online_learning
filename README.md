# Online Learning API

A FastAPI-based online machine learning service using River for real-time model training and prediction.

## Features

- **Online Learning**: Train models incrementally with new data
- **Real-time Predictions**: Get predictions with automatic model updates
- **Feature Engineering**: Automated lag feature extraction for time series
- **Metrics Tracking**: Monitor model performance over time
- **Health Monitoring**: Built-in health checks and service info
- **Docker Support**: Containerized deployment ready
- **Argo Workflows**: ML pipeline orchestration and automation

## Services

### Model Service (Port 8000)
- `GET /health` - Service health check
- `GET /info` - Model and service information
- `GET /metrics` - Performance metrics
- `POST /train` - Train model with new observations
- `POST /predict` - Get predictions for time series
- `POST /predict_learn` - Predict and learn from real values
- `POST /feedback` - Submit feedback for model improvement

### Feature Service (Port 8001)
- `GET /health` - Service health check
- `GET /info` - Service information and series status
- `POST /add_observation` - Add new observation to time series
- `POST /features` - Get lag features for a series
- `GET /features/{series_id}` - Get lag features (GET endpoint)

## Quick Start

### Local Development

1. Install and test the application:
```bash
cd app/model_service
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
python main.py
```

2. Build Docker image:
```bash
cd app/model_service
docker build -t fti-predict-learn .
```

### Kubernetes Deployment

#### Prerequisites
- k3d or any Kubernetes cluster
- kubectl configured

#### Deployment Steps

1. Create k3d cluster:
```bash
make cluster-up
```

2. Deploy ML API:
```bash
make apply
```

3. Deploy Argo Workflows (optional):
```bash
make argo
```

4. Test the deployment:
```bash
make test-api
```

5. Access services:
```bash
# Model Service
http://localhost:30080

# Feature Service
http://localhost:30090

# Argo Workflows UI (if deployed)
http://localhost:2746
```

6. Clean up:
```bash
make clean
make cluster-down
```

## Project Structure

```
online_learning/
├── .github/
│   └── workflows/
│       ├── features_ci.yml      # Feature service CI/CD
│       └── predict_learn_ci.yml # Model service CI/CD
├── app/                     # Application code (future GitOps repo)
│   ├── model_service/
│   │   ├── __init__.py
│   │   ├── metrics_manager.py   # Performance metrics tracking
│   │   ├── model_manager.py     # Model lifecycle management
│   │   ├── service.py          # FastAPI application
│   │   ├── main.py            # Application entry point
│   │   ├── Dockerfile         # Container configuration
│   │   ├── requirements.txt   # Python dependencies
│   │   ├── README.md          # App documentation
│   │   └── tests/
│   │       └── test_requests.py # API integration tests
│   └── feature_service/
│       ├── __init__.py
│       ├── feature_manager.py   # Lag feature computation
│       ├── service.py          # FastAPI feature service
│       ├── main.py            # Feature service entry point
│       ├── Dockerfile         # Feature service container
│       ├── requirements.txt   # Feature service dependencies
│       ├── README.md          # Feature service documentation
│       └── tests/
│           └── test_features.py # Feature service tests
├── infra/                   # Infrastructure code (future GitOps repo)
│   ├── argo/
│   │   ├── hello-world.yaml     # Simple Argo workflow example
│   │   └── quick-start-minimal.yaml # Argo Workflows installation
│   ├── k8s/
│   │   ├── deployments/
│   │   │   ├── model-service.yaml     # Model service deployment
│   │   │   └── feature-service.yaml   # Feature service deployment
│   │   ├── services/
│   │   │   ├── model-service.yaml     # Model service (port 30080)
│   │   │   └── feature-service.yaml   # Feature service (port 30090)
│   │   ├── namespace.yaml         # FTI namespace
│   │   └── kustomization.yaml     # Kustomize configuration
│   └── test_api.sh          # API testing script
├── .gitignore              # Git ignore patterns
├── Makefile                # Infrastructure automation
└── README.md               # Main project documentation
```

## API Usage Examples

### Using the test script:
```bash
cd infra
./test_api.sh
```

### Manual API calls:

#### Train the model:
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "store_123_sales",
    "observations": [
      {"timestamp": "2025-08-24", "value": 110},
      {"timestamp": "2025-08-25", "value": 120}
    ]
  }'
```

#### Get predictions:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "store_123_sales",
    "horizon": 3
  }'
```

#### Predict and learn:
```bash
curl -X POST "http://localhost:8000/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "store_123_sales",
    "y_real": 135
  }'
```

## Infrastructure Components

### Kubernetes Manifests (`infra/k8s/`)
- `deployments/` - Service deployment configurations
- `services/` - Service definitions with NodePort access
- `kustomization.yaml` - Kustomize configuration for organized deployment

### Argo Workflows (`infra/argo/`)
- `hello-world.yaml` - Simple workflow example
- `quick-start-minimal.yaml` - Complete Argo installation manifest

### Testing
- `test_api.sh` - Comprehensive API testing script

## GitOps Structure

The repository is organized for future GitOps separation:

- **`app/`** - Application code, CI/CD, and development tools
  - Will become a separate repository for application development
  - Contains GitHub Actions for testing and building Docker images
  - Includes model service code and documentation

- **`infra/`** - Infrastructure manifests and deployment automation
  - Will become a separate repository for infrastructure management
  - Contains Kubernetes manifests and Argo Workflows
  - Includes deployment scripts and testing tools

## CI/CD

The project includes separate GitHub Actions workflows:
- `predict_learn_ci.yml` - Model service CI/CD
- `features_ci.yml` - Feature service CI/CD

Each workflow includes:
- Automated testing with pytest
- Docker image building and pushing to Docker Hub
- Triggered on push to main branch (only when respective service files change)

## Argo Workflows

The project includes Argo Workflows integration:
- `infra/argo/hello-world.yaml` - Simple workflow example
- `infra/argo/quick-start-minimal.yaml` - Complete Argo installation manifest
- Deploy with `cd infra && make argo` command

## Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `API_BASE_URL`: Base URL for tests (default: http://127.0.0.1:8000)

## Dependencies

- FastAPI 0.116.1 - Web framework
- Uvicorn 0.35.0 - ASGI server
- River 0.22.0 - Online machine learning
- Pydantic 2.11.7 - Data validation
- NumPy 2.3.2 - Numerical computing
- Pytest 8.3.4 - Testing framework

## License

MIT License