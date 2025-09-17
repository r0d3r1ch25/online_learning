# online_learning

This is a repository for online learning experiments and MLOps pipeline orchestration using Argo Workflows.

## Project Structure

- `pipelines/feature_service`: Microservice for time series feature extraction.
- `pipelines/model_service`: Online machine learning service for real-time model training and prediction.
- `pipelines/ingestion_service`: Contains `data.csv`, a dummy data source for the pipelines.
- `infra/k8s`: Kubernetes manifests organized by namespace:
    - `ml-services/`: Feature and model services with kustomization
    - `argo/`: Argo Workflows with complete setup
    - `feast/`: Feast feature store with Redis, MinIO, and SQLite
    - `monitoring/`: Grafana, Loki, and Promtail for log monitoring
- `infra/argo`: Argo Workflows definitions for orchestrating ML pipelines.
    - `v1`: Contains the initial version of the online learning simulation workflow.

## Infrastructure Overview

The project uses a k3d Kubernetes cluster with 4 namespaces:

### ml-services
- **feature-service**: Time series feature extraction API
- **model-service**: Online ML model training and prediction

### feast
- **feast-server**: Feature store API server
- **redis**: In-memory feature store
- **minio**: S3-compatible object storage

### argo
- **argo-server**: Workflow management UI
- **workflow-controller**: Workflow execution engine
- Complete Argo Workflows installation

### monitoring
- **grafana**: Log visualization dashboard
- **loki**: Log aggregation backend
- **promtail**: Log collection agent (DaemonSet)

## Getting Started

### 1. Cluster Management (using k3d)

- **Create Cluster:**
  ```bash
  make cluster-up
  ```
  This command creates a k3d cluster with LoadBalancer support and port mappings for remote access.

- **Delete Cluster:**
  ```bash
  make cluster-down
  ```
  This command deletes the k3d cluster.

### Service Endpoints (Remote Access)

Once deployed, services are accessible via LoadBalancer on your machine's IP:

- **Model Service**: `http://<your-ip>:8000` - ML model training and prediction
- **Feature Service**: `http://<your-ip>:8001` - Time series feature extraction  
- **Feast Server**: `http://<your-ip>:6566` - Feature store API
- **MinIO Console**: `http://<your-ip>:9001` - Object storage dashboard (admin/password)
- **MinIO API**: `http://<your-ip>:9000` - S3-compatible storage API
- **Argo Server**: `https://<your-ip>:2746` - Workflow management UI
- **Redis**: `<your-ip>:6379` - In-memory data store
- **Grafana**: `http://<your-ip>:3000` - Log monitoring dashboard (admin/admin)

### 2. Deploying Services

- **Deploy All Services:**
  ```bash
  make apply
  ```
  Deploys all services across ml-services, argo, and feast namespaces.

- **Deploy Individual Namespaces:**
  ```bash
  make apply-ml          # ML services only
  make apply-argo        # Argo workflows only  
  make apply-feast       # Feast feature store only
  make apply-monitoring  # Monitoring stack only
  ```

### 3. Installing Argo Workflows

- **Deploy Argo Workflows:**
  ```bash
  make argo
  ```
  This command installs Argo Workflows into the `argo` Kubernetes namespace.

### 4. Running Workflows

- **Test Argo Installation (Hello World):**
  ```bash
  make argo-hello
  ```
  This runs a simple "hello world" workflow to verify your Argo setup.

- **Run V1 Online Learning Pipeline:**
  ```bash
  argo submit -n argo infra/argo/v1/online-learning-pipeline.yaml
  ```
  This workflow simulates an online learning process:
    - It adds observations to the `feature_service` one by one.
    - For each observation, it requests features from the `feature_service`.
    - It then uses these features and the actual value to perform a `predict_learn` operation on the `model_service`.

## Deployment Workflow

1. **Create Cluster**: `make cluster-up`
2. **Deploy All Services**: `make apply`
3. **Access Services**: Use `<your-ip>:port` from your local network
4. **Monitor Logs**: Access Grafana at `http://<your-ip>:3000`
5. **Run Workflows**: Use Argo UI at `https://<your-ip>:2746`

## Development Notes

- The `feature_service` and `model_service` are designed for online/incremental learning.
- The `v1` pipeline demonstrates a basic end-to-end online learning simulation.
- All services use LoadBalancer for remote network access.
- Promtail collects logs from all namespaces for centralized monitoring.
