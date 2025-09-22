# Online Learning MLOps Platform

A complete MLOps platform for online learning experiments with real-time model training, feature extraction, and workflow orchestration using Kubernetes and Argo Workflows.

## Architecture Overview

The platform consists of multiple microservices deployed on a k3d Kubernetes cluster:

- **Ingestion Service** (Port 8002): Streams time series data observations one at a time
- **Feature Service** (Port 8001): Calculates lag features and outputs model-ready format  
- **Model Services**: Multiple online ML models with real-time training and prediction
  - **Linear Regression** (Port 8010)
  - **Ridge Regression** (Port 8011) 
  - **Neural Network** (Port 8012)
- **Coinbase Service** (Port 8003): Cryptocurrency data streaming

## Project Structure

```
online_learning/
├── .github/workflows/          # CI/CD pipelines
│   ├── ingestion.yml          # Ingestion service CI/CD
│   ├── features_ci.yml        # Feature service CI/CD
│   ├── model_ci.yml           # Model service CI/CD
│   └── e2e_job_ci.yml         # E2E job CI/CD
├── pipelines/                 # Microservices
│   ├── ingestion_service/     # Time series data streaming
│   │   ├── tests/            # Unit tests
│   │   │   └── test_ingestion.py
│   │   ├── __init__.py       # Python package init
│   │   ├── data.csv          # Sample dataset (1949-1960 monthly data)
│   │   ├── service.py        # Core ingestion logic
│   │   ├── main.py           # FastAPI application
│   │   ├── Dockerfile        # Non-root container image
│   │   ├── README.md         # Service documentation
│   │   └── requirements.txt  # Python dependencies
│   ├── feature_service/       # Feature extraction
│   │   ├── tests/            # Unit tests
│   │   │   ├── test_api.py
│   │   │   ├── test_features.py
│   │   │   └── test_integration.py
│   │   ├── __init__.py       # Python package init
│   │   ├── feature_manager.py # Time series feature engineering
│   │   ├── service.py        # FastAPI service
│   │   ├── main.py           # Application entry point
│   │   ├── Dockerfile        # Non-root container image
│   │   ├── README.md         # Service documentation
│   │   └── requirements.txt  # Python dependencies
│   ├── model_service/         # Online ML models
│   │   ├── tests/            # Unit tests
│   │   │   ├── test_integration.py
│   │   │   └── test_requests.py
│   │   ├── __init__.py       # Python package init
│   │   ├── model_manager.py   # Online learning algorithms
│   │   ├── metrics_manager.py # Performance tracking
│   │   ├── service.py        # FastAPI service
│   │   ├── main.py           # Application entry point
│   │   ├── Dockerfile        # Non-root container image
│   │   ├── README.md         # Service documentation
│   │   └── requirements.txt  # Python dependencies
│   └── coinbase_service/      # Cryptocurrency data streaming
│       ├── __init__.py       # Python package init
│       ├── service.py        # Coinbase API integration
│       ├── main.py           # FastAPI application
│       ├── Dockerfile        # Non-root container image
│       └── requirements.txt  # Python dependencies
├── jobs/                      # Job containers
│   └── e2e_job/              # End-to-end pipeline job
│       ├── tests/            # Unit tests
│       │   ├── requirements.txt
│       │   └── test_pipeline.py
│       ├── Dockerfile        # Non-root container image
│       ├── pipeline.py       # Pipeline orchestration logic
│       ├── README.md         # Job documentation
│       └── requirements.txt  # Job dependencies
├── infra/                     # Infrastructure as Code
│   ├── k8s/                  # Kubernetes manifests
│   │   ├── ml-services/      # ML microservices deployment
│   │   │   ├── deployments/  # Deployment manifests
│   │   │   ├── services/     # Service manifests
│   │   │   ├── kustomization.yaml
│   │   │   └── namespace.yaml
│   │   ├── argo/             # Argo Workflows setup
│   │   │   ├── kustomization.yaml
│   │   │   ├── namespace.yaml
│   │   │   └── quick-start-minimal.yaml
│   │   ├── monitoring/       # Observability stack
│   │   │   ├── configmaps/   # Grafana, Prometheus, Promtail configs
│   │   │   ├── deployments/  # Monitoring service deployments
│   │   │   ├── services/     # Service manifests
│   │   │   ├── kustomization.yaml
│   │   │   ├── namespace.yaml
│   │   │   └── rbac.yaml
│   │   └── kustomization.yaml # Root kustomization
│   ├── workflows/            # Argo workflow definitions
│   │   ├── v0/               # CronWorkflow (inline script)
│   │   │   └── online-learning-pipeline.yaml
│   │   └── v1/               # CronWorkflow (baked image)
│   │       └── online-learning-pipeline-v1.yaml
│   └── test_pipeline.sh      # Manual pipeline testing script
├── .gitignore                # Git ignore rules
├── Makefile                  # Infrastructure automation
└── README.md                 # This file
```

## Infrastructure Components

### Kubernetes Namespaces

#### ml-services
- **ingestion-service**: Data streaming API (Port 8002)
- **feature-service**: Time series feature extraction API (Port 8001)
- **model-service**: Linear regression model API (Port 8010)
- **model-service-ridge**: Ridge regression model API (Port 8011)
- **model-service-neural**: Neural network model API (Port 8012)
- **coinbase-service**: Cryptocurrency data streaming API (Port 8003)


#### argo
- **argo-server**: Workflow management UI (Port 2746)
- **workflow-controller**: Workflow execution engine

#### monitoring
- **grafana**: Log visualization dashboard with Loki and Prometheus data sources (Port 3000)
- **loki**: Log aggregation backend (Port 3100)
- **promtail**: Log collection agent (DaemonSet)
- **prometheus**: Metrics collection and monitoring with ML model metrics (Port 9090)

## Quick Start

### 1. Cluster Setup

```bash
# Create k3d cluster with LoadBalancer support
make cluster-up

# Deploy all services
make apply
```

### 2. Service Endpoints

Once deployed, access services via LoadBalancer:

- **Feature Service**: `http://<your-ip>:8001` - Feature extraction
- **Ingestion Service**: `http://<your-ip>:8002` - Data streaming
- **Coinbase Service**: `http://<your-ip>:8003` - Crypto data streaming
- **Linear Model**: `http://<your-ip>:8010` - Linear regression ML
- **Ridge Model**: `http://<your-ip>:8011` - Ridge regression ML
- **Neural Model**: `http://<your-ip>:8012` - Neural network ML
- **Argo Server**: `https://<your-ip>:2746` - Workflow management
- **Grafana**: `http://<your-ip>:3000` - Monitoring (admin/admin)
- **Prometheus**: `http://<your-ip>:9090` - Metrics collection and monitoring
- **Loki**: `http://<your-ip>:3100` - Log aggregation API

### 3. Run Online Learning Pipeline

```bash
# Start v1 workflow (linear model only, every minute)
make argo-e2e

# Start v2 workflow (all 3 models, every minute)
kubectl apply -f infra/workflows/v2/online-learning-pipeline-v2.yaml

# Monitor workflows
argo list -n argo

# Stop workflows
kubectl delete cronworkflow online-learning-cron-v1 -n argo
kubectl delete cronworkflow online-learning-cron-v2 -n argo

# Monitor in Argo UI
open https://<your-ip>:2746
```

## API Usage

### Ingestion Service API

```bash
# Get next observation (date + value)
curl http://<your-ip>:8002/next
# Returns: {"observation_id": 1, "input": "1949-01", "target": 112, "remaining": 143}

# Reset stream to beginning
curl -X POST http://<your-ip>:8002/reset

# Check stream status
curl http://<your-ip>:8002/status

# Health check
curl http://<your-ip>:8002/health
```

### Feature Service API

```bash
# Health check
curl http://<your-ip>:8001/health

# Service information
curl http://<your-ip>:8001/info

# Add observation and extract lag features
curl -X POST http://<your-ip>:8001/add \
  -H "Content-Type: application/json" \
  -d '{"series_id": "default", "value": 125.0}'
# Returns: {"series_id": "default", "features": {"in_1": 120.0, "in_2": 115.0, ...}, "target": 125.0, "available_lags": 2}

# Get series information
curl http://<your-ip>:8001/series/default
```

### Coinbase Service API

```bash
# Health check
curl http://<your-ip>:8003/health

# Get current XRP rate (inverse of Coinbase rate)
curl http://<your-ip>:8003/next
# Returns: {"series_id": "XRP", "target": 2.84, "datetime": "2024-01-15T08:30:25-06:00"}
```

### Model Services API

**Three independent model services with feature-agnostic online ML:**

```bash
# Linear Regression Model (Port 8010)
curl http://<your-ip>:8010/health
curl http://<your-ip>:8010/info

# Ridge Regression Model (Port 8011)
curl http://<your-ip>:8011/health
curl http://<your-ip>:8011/info

# Neural Network Model (Port 8012)
curl http://<your-ip>:8012/health
curl http://<your-ip>:8012/info

# Train any model (example with linear model)
curl -X POST http://<your-ip>:8010/train \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 125.0, "in_2": 120.0}, "target": 130.0}'

# Predict (single-step horizon)
curl -X POST http://<your-ip>:8010/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 130.0, "in_2": 125.0}}'
# Returns: {"forecast": [{"value": 135.2}]}

# Online learning (predict then learn)
curl -X POST http://<your-ip>:8010/predict_learn \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 135.0, "in_2": 130.0}, "target": 140.0}'
# Returns: {"prediction": 138.7}

# Get model performance metrics (MAE, MSE, RMSE, MAPE)
curl http://<your-ip>:8010/model_metrics

# Get Prometheus-compatible metrics
curl http://<your-ip>:8010/metrics
```

**Available Models:**
- **Linear Regression**: Standard linear regression with StandardScaler
- **Ridge Regression**: L2 regularized linear regression
- **Neural Network**: MLP with 5 hidden neurons and ReLU activation

**Key Features:**
- **Feature Agnostic**: Accepts any number of input features dynamically
- **Configurable Lags**: N_LAGS environment variable controls feature service output (default: 12)
- **Single-Step Prediction**: FORECAST_HORIZON=1 (hardcoded)
- **Independent Scaling**: Each model can scale separately
- **Performance Tracking**: /model_metrics endpoint with MAE, MSE, RMSE, MAPE
- **Prometheus Ready**: /metrics endpoint with model labels for monitoring

## Development Commands

### Cluster Management
```bash
make cluster-up      # Create k3d cluster
make cluster-down    # Delete cluster
make again           # Reset cluster with latest code
```

### Deployment
```bash
make apply           # Deploy all services
```

### Service Testing
```bash
# Run unit tests for each service
pytest pipelines/ingestion_service/tests/ -v
pytest pipelines/feature_service/tests/ -v
pytest pipelines/model_service/tests/ -v

# Start CronWorkflow (runs every minute)
make argo-e2e

# Run unit tests for e2e job
cd jobs/e2e_job && PYTHONPATH=. pytest tests/ -v

# Manual pipeline testing
bash infra/test_pipeline.sh
```

### Pipeline Integration Examples
```bash
# Complete pipeline: Ingestion -> Features -> Model
# 1. Get observation from ingestion service
curl http://localhost:8002/next

# 2. Extract features (pipe ingestion output to feature service)
curl -s http://localhost:8002/next | \
  jq '{series_id: "manual_test", value: .target}' | \
  curl -s -X POST -H "Content-Type: application/json" \
    --data-binary @- http://localhost:8001/add

# 3. Train model (pipe feature output to model service)
curl -s http://localhost:8002/next | \
  jq '{series_id: "manual_test", value: .target}' | \
  curl -s -X POST -H "Content-Type: application/json" \
    --data-binary @- http://localhost:8001/add | \
  jq '{features: .features, target: .target}' | \
  curl -s -X POST -H "Content-Type: application/json" \
    --data-binary @- http://localhost:8000/predict_learn

# 4. Check model metrics
curl http://localhost:8000/model_metrics
```

### Grafana Monitoring
```bash
# Access Grafana with pre-configured data sources
open http://localhost:3000  # admin/admin
```

**Prometheus Queries (Metrics):**
- `ml_model_mae{model="linear_regression"}` - Linear model MAE
- `ml_model_mae{model="ridge_regression"}` - Ridge model MAE
- `ml_model_mae{model="neural_network"}` - Neural model MAE
- `ml_model_rmse{model=~"linear_regression|ridge_regression|neural_network"}` - All models RMSE
- `ml_model_mape{model=~".*"}` - All models MAPE
- `ml_model_predictions_total` - Total predictions count by model

**Loki Queries (Logs):**
- `{app="model-service"}` - All model service logs
- `{app="model-service"} |= "WARNING"` - Warning logs only
- `{namespace="ml-services"}` - All ML services logs

## CI/CD Pipeline

### Automated Workflows

Each service has automated GitHub Actions that trigger on:
- **Push to main** with changes in service directory
- **Manual trigger** via GitHub Actions UI

#### Ingestion Service (`pipelines/ingestion_service/**`)
- Runs pytest tests
- Builds and tests Docker container
- Validates API endpoints with health check
- Pushes to Docker Hub: `r0d3r1ch25/ml-ingestion:latest`

#### Feature Service (`pipelines/feature_service/**`)
- Runs pytest tests with PYTHONPATH
- Builds Docker image
- Pushes to Docker Hub: `r0d3r1ch25/ml-features:latest`

#### Model Service (`pipelines/model_service/**`)
- Runs pytest tests
- Builds Docker image  
- Pushes to Docker Hub: `r0d3r1ch25/ml-model:latest`

#### E2E Job (`jobs/e2e_job/**`)
- Runs pytest tests with mocked services
- Builds Docker image
- Pushes to Docker Hub: `r0d3r1ch25/ml-e2e-job:latest`

## Data Flow

1. **Ingestion Service** streams time series observations (date, value pairs)
2. **Feature Service** calculates lag features and outputs model-ready format (in_1 to in_{N_LAGS})
3. **Model Service** performs feature-agnostic online learning with any features provided
4. **Argo CronWorkflow** orchestrates the end-to-end pipeline every minute
5. **Monitoring Stack** tracks logs and metrics across all services

## Configuration

### Feature Configuration
The number of lag features can be configured via environment variable:

```bash
# Change number of lag features (default: 12)
export N_LAGS=8  # Creates in_1 to in_8

# Feature service will generate: in_1, in_2, ..., in_8
# Model service automatically adapts to any number of features
```

### Model Configuration
Models are configured via environment variables in Kubernetes deployments:
- **Linear**: `MODEL_NAME=linear_regression`
- **Ridge**: `MODEL_NAME=ridge_regression` 
- **Neural**: `MODEL_NAME=neural_network`

## Dataset

The platform uses a sample time series dataset (`data.csv`) with monthly observations from 1949-1960:
- **Input**: Date strings (YYYY-MM format)
- **Target**: Integer values representing time series measurements
- **Total**: 144 observations for online learning simulation

## Troubleshooting

### Service Connectivity
```bash
# Test service health
curl http://<your-ip>:8001/health  # Feature service  
curl http://<your-ip>:8002/health  # Ingestion service
curl http://<your-ip>:8003/health  # Coinbase service
curl http://<your-ip>:8010/health  # Linear model
curl http://<your-ip>:8011/health  # Ridge model
curl http://<your-ip>:8012/health  # Neural model
```

### Logs and Monitoring
- **Grafana**: `http://<your-ip>:3000` (admin/admin) - Pre-configured with Loki and Prometheus data sources
- **Prometheus**: `http://<your-ip>:9090` - ML model metrics collection and monitoring
- **Loki**: Log aggregation from all services via Promtail
- **Argo Workflows**: `https://<your-ip>:2746` - Pipeline orchestration
- **Pod Logs**: `kubectl logs -n ml-services <pod-name>`

## Service Documentation

Each microservice has detailed documentation in its respective directory:

- **[Ingestion Service](pipelines/ingestion_service/README.md)**: Time series data streaming API with sequential observation delivery
- **[Feature Service](pipelines/feature_service/README.md)**: Lag feature calculation with model-ready output format (in_1 to in_12)
- **[Model Service](pipelines/model_service/README.md)**: Feature-agnostic online ML service with multiple regression models
- **[E2E Job](jobs/e2e_job/README.md)**: End-to-end pipeline orchestration job for Argo Workflows

## Docker Images

All images use non-root users for security and are automatically built and pushed to Docker Hub:

- **ml-ingestion**: `r0d3r1ch25/ml-ingestion:latest` - Time series data streaming service
- **ml-features**: `r0d3r1ch25/ml-features:latest` - Feature extraction service  
- **ml-model**: `r0d3r1ch25/ml-model:latest` - Online ML service (used by all 3 model deployments)
- **ml-coinbase**: `r0d3r1ch25/ml-coinbase:latest` - Cryptocurrency data streaming service
- **ml-e2e-job**: `r0d3r1ch25/ml-e2e-job:latest` - End-to-end pipeline orchestration job

**Security Features:**
- All containers run as non-root user `appuser`
- Principle of least privilege applied
- Reduced attack surface for production deployments

## Technology Stack

- **Container Orchestration**: Kubernetes (k3d)
- **Workflow Engine**: Argo Workflows
- **API Framework**: FastAPI
- **Feature Store**: Feast + Redis + MinIO
- **Monitoring**: Grafana + Loki + Promtail + Prometheus
- **CI/CD**: GitHub Actions
- **Container Registry**: Docker Hub
- **Online Learning**: River (incremental ML algorithms)

## Dependencies

### Core Services
- **FastAPI**: Web framework for all services
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **River**: Online machine learning library
- **Pandas**: Data manipulation (ingestion service)
- **Requests**: HTTP client library

### Testing
- **Pytest**: Testing framework
- **HTTPx**: Async HTTP client for testing

### Infrastructure
- **k3d**: Lightweight Kubernetes distribution
- **Kustomize**: Kubernetes configuration management
- **Argo Workflows**: Workflow orchestration
- **Grafana Stack**: Monitoring and observability

## Current Project Status

### ✅ Completed Components

**Microservices (All Deployed)**
- ✅ Ingestion Service: Streaming time series data (Port 8002)
- ✅ Feature Service: Lag feature extraction (Port 8001) 
- ✅ Model Service: Online ML with River (Port 8000)

**Infrastructure (Kubernetes Ready)**
- ✅ k3d cluster with LoadBalancer support
- ✅ 3 namespaces: ml-services, argo, monitoring
- ✅ All services accessible via LoadBalancer
- ✅ Health checks and resource limits configured

**CI/CD Pipeline (Automated)**
- ✅ GitHub Actions for all services + e2e job
- ✅ Automated testing with pytest
- ✅ Docker build/push to Docker Hub
- ✅ Manual and path-based triggers

**Workflow Orchestration**
- ✅ Argo Workflows installed and configured
- ✅ CronWorkflow v1 with containerized job (runs every minute)
- ✅ Workflow management UI accessible
- ✅ Manual testing script available

**Monitoring & Observability**
- ✅ Grafana + Loki + Promtail + Prometheus stack
- ✅ Log aggregation from all services
- ✅ ML model metrics collection and monitoring
- ✅ Pre-configured data sources in Grafana
- ✅ Dashboard accessible via LoadBalancer



### 🚀 Ready to Use

1. **Deploy**: `make cluster-up && make apply`
2. **Access**: All services available at `http://<your-ip>:port`
3. **Monitor**: Grafana at `http://<your-ip>:3000`
4. **Orchestrate**: Argo UI at `https://<your-ip>:2746`
5. **Test**: `bash infra/test_pipeline.sh` for manual testing

## Complete API Reference

### Ingestion Service (Port 8002)

#### `GET /health`
Health check endpoint for Kubernetes probes.
```bash
curl http://<your-ip>:8002/health
# Returns: {"status": "healthy", "total_observations": 144}
```

#### `GET /next`
Get the next observation from the dataset.
```bash
curl http://<your-ip>:8002/next
# Returns: {"observation_id": 1, "input": "1949-01", "target": 112, "remaining": 143}
# Returns 204 when stream is exhausted
```

#### `POST /reset`
Reset the stream to start from the beginning.
```bash
curl -X POST http://<your-ip>:8002/reset
# Returns: {"message": "Stream reset to beginning", "total_observations": 144}
```

#### `GET /status`
Get current stream status.
```bash
curl http://<your-ip>:8002/status
# Returns: {"current_index": 5, "total_observations": 144, "remaining": 139, "completed": false}
```

### Feature Service (Port 8001)

#### `GET /health`
Health check endpoint for Kubernetes probes.
```bash
curl http://<your-ip>:8001/health
# Returns: {"status": "healthy", "service": "feature_service"}
```

#### `GET /info`
Get service and series information.
```bash
curl http://<your-ip>:8001/info
# Returns: {"service": "feature_service", "max_lags": 12, "output_format": "model_ready_in_1_to_in_12", "series_info": {}}
```

#### `POST /add`
Add observation and extract lag features in model-ready format.
```bash
curl -X POST http://<your-ip>:8001/add \
  -H "Content-Type: application/json" \
  -d '{"series_id": "default", "value": 125.0}'
# Returns: {"series_id": "default", "features": {"in_1": 120.0, "in_2": 115.0, ...}, "target": 125.0, "available_lags": 2}
```

#### `GET /series/{series_id}`
Get information about a specific series.
```bash
curl http://<your-ip>:8001/series/default
# Returns: {"series_id": "default", "length": 5, "latest_value": 125.0, "available_lags": 5}
# Returns 404 if series not found
```

### Model Service (Port 8000)

#### `GET /health`
Health check endpoint for Kubernetes probes.
```bash
curl http://<your-ip>:8000/health
# Returns: {"status": "ok", "model_loaded": true}
```

#### `GET /info`
Get service information including current model configuration.
```bash
curl http://<your-ip>:8000/info
# Returns: {"model_name": "River Linear Regression", "model_version": "0.22.0", "forecast_horizon": 1, "feature_agnostic": true, "regression_model": true, "available_models": ["linear_regression", "ridge_regression", "lasso_regression", "decision_tree", "bagging_regressor"]}
```

#### `POST /train`
Train the model with features and target value.
```bash
curl -X POST http://<your-ip>:8000/train \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0}, "target": 130.0}'
# Returns: {"message": "Model trained successfully"}
```

#### `POST /predict`
Make prediction using current model state (single-step forecast).
```bash
curl -X POST http://<your-ip>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0}}'
# Returns: {"forecast": [{"value": 135.2}]}
```

#### `POST /predict_learn`
Predict then learn from actual value (online learning).
```bash
curl -X POST http://<your-ip>:8000/predict_learn \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0}, "target": 140.0}'
# Returns: {"prediction": 138.7}
```

#### `GET /model_metrics`
Get comprehensive model performance metrics.
```bash
curl http://<your-ip>:8000/model_metrics
# Returns: {"default": {"count": 15, "mae": 2.45, "mse": 8.12, "rmse": 2.85, "last_prediction": 138.7, "last_actual": 140.0, "last_error": 1.3}}
```

#### `GET /metrics`
Prometheus-compatible metrics endpoint.
```bash
curl http://<your-ip>:8000/metrics
# Returns: Prometheus format metrics (text/plain)
# Example:
# ml_model_mae{series="default"} 2.45
# ml_model_mse{series="default"} 8.12
# ml_model_rmse{series="default"} 2.85
# ml_model_predictions_total{series="default"} 15
# ml_model_last_prediction{series="default"} 138.7
# ml_model_last_error{series="default"} 1.3
```