# Online Learning MLOps Platform

A complete MLOps platform for online learning experiments with real-time model training, feature extraction, and workflow orchestration using Kubernetes and Argo Workflows.

## Architecture Overview

The platform consists of three main microservices deployed on a k3d Kubernetes cluster:

- **Ingestion Service** (Port 8002): Streams time series data observations one at a time
- **Feature Service** (Port 8001): Extracts time series features from raw observations  
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
│   │   └── tests/            # Unit tests
│   ├── feature_service/       # Feature extraction
│   │   ├── feature_manager.py # Time series feature engineering
│   │   ├── service.py        # FastAPI service
│   │   └── tests/            # Unit tests
│   └── model_service/         # Online ML models
│       ├── model_manager.py   # Online learning algorithms
│       ├── metrics_manager.py # Performance tracking
│       ├── service.py        # FastAPI service
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
- **grafana**: Log visualization dashboard (Port 3000)
- **loki**: Log aggregation backend
- **promtail**: Log collection agent (DaemonSet)

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
# Extract features from observation
curl -X POST http://<your-ip>:8001/extract \
  -H "Content-Type: application/json" \
  -d '{"observation_id": 1, "input": "1949-01", "target": 112}'
```

### Model Service API

```bash
# Train and predict (online learning)
curl -X POST http://<your-ip>:8000/predict_learn \
  -H "Content-Type: application/json" \
  -d '{"features": {...}, "target": 112}'

# Get model metrics
curl http://<your-ip>:8000/metrics
```

## Development Commands

### Cluster Management
```bash
make cluster-up      # Create k3d cluster
make cluster-down    # Delete cluster
```

### Deployment
```bash
make apply           # Deploy all services
make apply-ml        # Deploy ML services only
make apply-argo      # Deploy Argo only
make apply-feast     # Deploy Feast only
make apply-monitoring # Deploy monitoring only
```

### Workflow Testing
```bash
make argo-hello      # Test Argo installation
```

## CI/CD Pipeline

### Automated Workflows

Each service has automated GitHub Actions that trigger on:
- **Push to main** with changes in service directory
- **Manual trigger** via GitHub Actions UI

#### Ingestion Service (`pipelines/ingestion_service/**`)
- Runs pytest tests
- Builds and tests Docker container
- Validates API endpoints

#### Feature Service (`pipelines/feature_service/**`)
- Runs pytest tests  
- Builds Docker image
- Pushes to Docker Hub: `r0d3r1ch25/fti_features:latest`

#### Model Service (`pipelines/model_service/**`)
- Runs pytest tests
- Builds Docker image  
- Pushes to Docker Hub: `r0d3r1ch25/fti_model:latest`

## Data Flow

1. **Ingestion Service** streams time series observations (date, value pairs)
2. **Feature Service** extracts time series features from raw observations
3. **Model Service** performs online learning using features and targets
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
- Access Grafana at `http://<your-ip>:3000`
- View Argo workflows at `https://<your-ip>:2746`
- Check pod logs: `kubectl logs -n ml-services <pod-name>`

## Technology Stack

- **Container Orchestration**: Kubernetes (k3d)
- **Workflow Engine**: Argo Workflows
- **API Framework**: FastAPI
- **Feature Store**: Feast + Redis + MinIO
- **Monitoring**: Grafana + Loki + Promtail
- **CI/CD**: GitHub Actions
- **Container Registry**: Docker Hub
- **Online Learning**: Incremental ML algorithms