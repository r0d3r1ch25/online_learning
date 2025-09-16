# online_learning

This is a repository for online learning experiments and MLOps pipeline orchestration using Argo Workflows.

## Project Structure

- `pipelines/feature_service`: Microservice for time series feature extraction.
- `pipelines/model_service`: Online machine learning service for real-time model training and prediction.
- `pipelines/ingestion_service`: Contains `data.csv`, a dummy data source for the pipelines.
- `infra/k8s`: Kubernetes manifests for deploying the feature and model services.
- `infra/argo`: Argo Workflows definitions for orchestrating ML pipelines.
    - `v1`: Contains the initial version of the online learning simulation workflow.

## Getting Started

### 1. Cluster Management (using k3d)

- **Create Cluster:**
  ```bash
  make cluster-up
  ```
  This command creates a k3d cluster with necessary port mappings.

- **Delete Cluster:**
  ```bash
  make cluster-down
  ```
  This command deletes the k3d cluster.

### 2. Deploying Services

- **Apply Kubernetes Manifests:**
  ```bash
  make apply
  ```
  This command deploys the `feature_service` and `model_service` to the `fti` Kubernetes namespace.

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

## Development Notes

- The `feature_service` and `model_service` are designed for online/incremental learning.
- The `v1` pipeline demonstrates a basic end-to-end online learning simulation.
