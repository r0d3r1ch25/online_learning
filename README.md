# Online Learning MLOps Platform

A complete MLOps platform for online learning experiments with real-time model training, feature extraction, and workflow orchestration using Kubernetes and Argo Workflows.

## Architecture Overview

The platform consists of three main microservices deployed on a k3d Kubernetes cluster:

- **Ingestion Service** (Port 8002): Streams time series data observations one at a time
- **Feature Service** (Port 8001): Calculates lag features and outputs model-ready format  
- **Model Service** (Port 8000): Performs online machine learning with real-time training and prediction

## Project Structure

```
online_learning/
├── .github/workflows/          # CI/CD pipelines
│   ├── ingestion.yml          # Ingestion service CI/CD
│   ├── features_ci.yml        # Feature service CI/CD
│   └── model_ci.yml           # Model service CI/CD
├── pipelines/                 # Microservices
│   ├── ingestion_service/     # Time series data streaming
│   │   ├── data.csv          # Sample dataset (1949-1960 monthly data)
│   │   ├── service.py        # Core ingestion logic
│   │   ├── main.py           # FastAPI application
│   │   ├── README.md         # Service documentation
│   │   └── tests/            # Unit tests
│   ├── feature_service/       # Feature extraction
│   │   ├── feature_manager.py # Time series feature engineering
│   │   ├── service.py        # FastAPI service
│   │   ├── README.md         # Service documentation
│   │   └── tests/            # Unit tests
│   └── model_service/         # Online ML models
│       ├── model_manager.py   # Online learning algorithms
│       ├── metrics_manager.py # Performance tracking
│       ├── service.py        # FastAPI service
│       ├── README.md         # Service documentation
│       └── tests/            # Unit tests
├── infra/                     # Infrastructure as Code
│   ├── k8s/                  # Kubernetes manifests
│   │   ├── ml-services/      # ML microservices deployment
│   │   ├── argo/             # Argo Workflows setup
│   │   ├── feast/            # Feature store infrastructure
│   │   └── monitoring/       # Observability stack
│   └── workflows/            # Argo workflow definitions
│       └── v1/               # Online learning pipeline v1
└── Makefile                  # Infrastructure automation
```

## Infrastructure Components

### Kubernetes Namespaces

#### ml-services
- **ingestion-service**: Data streaming API (Port 8002)
- **feature-service**: Time series feature extraction API (Port 8001)
- **model-service**: Online ML training and prediction API (Port 8000)

#### feast
- **feast-server**: Feature store API server (Port 6566)
- **redis**: In-memory feature store (Port 6379)
- **minio**: S3-compatible object storage (Ports 9000/9001)

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

- **Model Service**: `http://<your-ip>:8000` - ML training/prediction
- **Feature Service**: `http://<your-ip>:8001` - Feature extraction
- **Ingestion Service**: `http://<your-ip>:8002` - Data streaming
- **Feast Server**: `http://<your-ip>:6566` - Feature store API
- **MinIO Console**: `http://<your-ip>:9001` - Storage dashboard (admin/password)
- **Argo Server**: `https://<your-ip>:2746` - Workflow management
- **Grafana**: `http://<your-ip>:3000` - Monitoring (admin/admin)
- **Prometheus**: `http://<your-ip>:9090` - Metrics collection and monitoring
- **Loki**: `http://<your-ip>:3100` - Log aggregation API

### 3. Run Online Learning Pipeline

```bash
# Submit workflow to Argo
argo submit -n argo infra/workflows/v1/online-learning-pipeline.yaml

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
```

### Feature Service API

```bash
# Add observation and extract lag features
curl -X POST http://<your-ip>:8001/add \
  -H "Content-Type: application/json" \
  -d '{"series_id": "default", "value": 125.0}'
# Returns: {"features": {"in_1": 120.0, "in_2": 115.0, ...}, "target": 125.0, "available_lags": 2}
```

### Model Service API

**Stateless online ML service supporting up to 12 input features (in_1 to in_12) with build-time configuration.**

```bash
# Train model with features (3 inputs)
curl -X POST http://<your-ip>:8000/train \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0}, "target": 130.0}'

# Train with all 12 inputs
curl -X POST http://<your-ip>:8000/train \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
      "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
      "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
    },
    "target": 130.0
  }'

# Predict (fixed 3-step horizon, no horizon parameter needed)
curl -X POST http://<your-ip>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0}}'

# Online learning (predict then learn)
curl -X POST http://<your-ip>:8000/predict_learn \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 135.0, "in_2": 130.0}, "target": 140.0}'

# Get comprehensive model performance metrics (MAE, MSE, RMSE)
curl http://<your-ip>:8000/model_metrics

# Get Prometheus-compatible metrics for monitoring
curl http://<your-ip>:8000/metrics
```

**Key Features:**
- **Up to 12 Inputs**: in_1, in_2, ..., in_12 (missing features handled by imputation)
- **Build-Time Config**: FORECAST_HORIZON=3, NUM_FEATURES=12 (rebuild to change)
- **Input Validation**: Unknown features trigger warnings but don't fail
- **Performance Tracking**: /model_metrics endpoint with MAE, MSE, RMSE
- **Prometheus Ready**: /metrics endpoint for monitoring stack integration
- **Imputation**: Missing features handled by River StatImputer with Mean strategy
- **Stateless Design**: No memory management, features provided externally

## Development Commands

### Cluster Management
```bash
make cluster-up      # Create k3d cluster
make cluster-down    # Delete cluster
```

### Deployment
```bash
make apply           # Deploy all services
```

### Service Testing
```bash
# Test monitoring stack + model service (comprehensive)
python3 infra/test_model_api.py [url]

# Test feature service independently
python3 infra/test_features_api.py [url]

# Test feature + model service integration
bash infra/test_features_model.sh

# Test Argo installation
make argo-hello
```

### Grafana Monitoring
```bash
# Access Grafana with pre-configured data sources
open http://localhost:3000  # admin/admin
```

**Prometheus Queries (Metrics):**
- `ml_model_mae` - Mean Absolute Error
- `ml_model_rmse` - Root Mean Squared Error  
- `ml_model_predictions_total` - Total predictions count
- `ml_model_last_prediction` - Last prediction value

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
- Validates API endpoints

#### Ingestion Service (`pipelines/ingestion_service/**`)
- Runs pytest tests
- Builds and tests Docker container
- Pushes to Docker Hub: `r0d3r1ch25/ml-ingestion:latest`
- Validates API endpoints

#### Feature Service (`pipelines/feature_service/**`)
- Runs pytest tests  
- Builds Docker image
- Pushes to Docker Hub: `r0d3r1ch25/ml-features:latest`

#### Model Service (`pipelines/model_service/**`)
- Runs pytest tests
- Builds Docker image  
- Pushes to Docker Hub: `r0d3r1ch25/ml-model:latest`

## Data Flow

1. **Ingestion Service** streams time series observations (date, value pairs)
2. **Feature Service** calculates lag features and outputs model-ready format (in_1 to in_12)
3. **Model Service** performs online learning using model-ready features and targets
4. **Argo Workflows** orchestrate the end-to-end pipeline
5. **Monitoring Stack** tracks logs and metrics across all services

## Dataset

The platform uses a sample time series dataset (`data.csv`) with monthly observations from 1949-1960:
- **Input**: Date strings (YYYY-MM format)
- **Target**: Integer values representing time series measurements
- **Total**: 144 observations for online learning simulation

## Troubleshooting

### Feast Server Issues
If `feast-server` pod fails to start:
1. Check `initContainer` runs `feast apply` successfully
2. Verify `emptyDir` volume is writable
3. Ensure correct command: `feast serve`

### Service Connectivity
```bash
# Test service health
curl http://<your-ip>:8000/health  # Model service
curl http://<your-ip>:8001/health  # Feature service  
curl http://<your-ip>:8002/health  # Ingestion service
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
- **[Model Service](pipelines/model_service/README.md)**: Stateless online ML service with River LinearRegression
  - **Input Features**: Up to 12 generic inputs (in_1 to in_12) with automatic validation
  - **Forecast Horizon**: Fixed 3-step predictions (configurable at build time)
  - **Performance Metrics**: Comprehensive MAE, MSE, RMSE tracking via /model_metrics endpoint
  - **Prometheus Integration**: /metrics endpoint for monitoring stack integration
  - **Online Learning**: Real-time predict-then-learn workflow with metrics tracking
  - **Build-Time Config**: FORECAST_HORIZON and NUM_FEATURES set during Docker build
  - **Imputation**: Missing features handled by River StatImputer, unknown features warned but ignored

## Docker Images

All services are automatically built and pushed to Docker Hub:

- **ml-ingestion**: `r0d3r1ch25/ml-ingestion:latest` - Time series data streaming service
- **ml-features**: `r0d3r1ch25/ml-features:latest` - Feature extraction service  
- **ml-model**: `r0d3r1ch25/ml-model:latest` - Online ML training and prediction service

## Current Project Status

### ✅ Completed Components

**Microservices (All Deployed)**
- ✅ Ingestion Service: Streaming time series data (Port 8002)
- ✅ Feature Service: Lag feature extraction (Port 8001) 
- ✅ Model Service: Online ML with River (Port 8000)

**Infrastructure (Kubernetes Ready)**
- ✅ k3d cluster with LoadBalancer support
- ✅ 4 namespaces: ml-services, feast, argo, monitoring
- ✅ All services accessible via LoadBalancer
- ✅ Health checks and resource limits configured

**CI/CD Pipeline (Automated)**
- ✅ GitHub Actions for all 3 services
- ✅ Automated testing with pytest
- ✅ Docker build/push to Docker Hub
- ✅ Manual and path-based triggers

**Workflow Orchestration**
- ✅ Argo Workflows installed and configured
- ✅ Online learning pipeline v1 ready
- ✅ Workflow management UI accessible

**Monitoring & Observability**
- ✅ Grafana + Loki + Promtail + Prometheus stack
- ✅ Log aggregation from all services
- ✅ ML model metrics collection and monitoring
- ✅ Pre-configured data sources in Grafana
- ✅ Dashboard accessible via LoadBalancer

**Feature Store**
- ✅ Feast server with Redis + MinIO
- ✅ S3-compatible storage configured
- ✅ Feature store API accessible

### 🚀 Ready to Use

1. **Deploy**: `make cluster-up && make apply`
2. **Access**: All services available at `http://<your-ip>:port`
3. **Monitor**: Grafana at `http://<your-ip>:3000`
4. **Orchestrate**: Argo UI at `https://<your-ip>:2746`

## Technology Stack

- **Container Orchestration**: Kubernetes (k3d)
- **Workflow Engine**: Argo Workflows
- **API Framework**: FastAPI
- **Feature Store**: Feast + Redis + MinIO
- **Monitoring**: Grafana + Loki + Promtail + Prometheus
- **CI/CD**: GitHub Actions
- **Container Registry**: Docker Hub
- **Online Learning**: River (incremental ML algorithms)

## API Endpoints Reference

### Feature Service (Port 8001)

**Health Check**
```bash
curl http://<your-ip>:8001/health
```

**Service Information**
```bash
curl http://<your-ip>:8001/info
```

**Add Observation and Extract Features (Model-Ready Format)**
```bash
curl -X POST http://<your-ip>:8001/add \
  -H "Content-Type: application/json" \
  -d '{"series_id": "default", "value": 125.0}'
# Returns: {"features": {...}, "target": 125.0, "available_lags": N}
```

**Get Series Information**
```bash
curl http://<your-ip>:8001/series/default
```

### Model Service (Port 8000)

**Health Check**
```bash
curl http://<your-ip>:8000/health
```

**Service Information**
```bash
curl http://<your-ip>:8000/info
```

**Train Model**
```bash
curl -X POST http://<your-ip>:8000/train \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0}, "target": 130.0}'
```

**Predict (3-Step Horizon)**
```bash
curl -X POST http://<your-ip>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0}}'
```

**Online Learning (Predict then Learn)**
```bash
curl -X POST http://<your-ip>:8000/predict_learn \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 135.0, "in_2": 130.0}, "target": 140.0}'
```

**Get Model Performance Metrics**
```bash
curl http://<your-ip>:8000/model_metrics
```

**Get Prometheus Metrics**
```bash
curl http://<your-ip>:8000/metrics
```

**Submit Feedback**
```bash
curl -X POST http://<your-ip>:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"message": "Model performing well"}'
```