# Online Learning MLOps Platform

A production-style MLOps stack for near real-time time-series forecasting. The platform streams observations, engineers features with Redis-backed state, trains multiple River-based online models, and orchestrates the end-to-end workflow with Argo Workflows on Kubernetes. It packages microservices, infrastructure, observability, and automation so the system can be deployed, monitored, and iterated like a production environment.

## Key Capabilities
- Real-time ingestion of 744 monthly observations plus live cryptocurrency prices via integrated Coinbase API.
- Feature service that materialises configurable lag features backed by Redis with automatic in-memory failover.
- Four independent online regression services (Linear, Ridge, KNN, AMF) exposing prediction, online learning, and detailed rolling metrics.
- Argo CronWorkflow that orchestrates ingestion → feature extraction → multi-model training in parallel using an asyncio job container.
- Kubernetes-native deployment with dedicated namespaces, resource requests/limits, k3d bootstrap automation, and manifests managed through Kustomize overlays.
- Full observability stack (Prometheus, Grafana, Loki, Promtail) and GitHub Actions CI/CD pipelines that test, build, and publish non-root Docker images for every workload.

## System Topology

```
                         +-----------------------------+
                         |     Argo CronWorkflow       |
                         | infra/workflows/v1/...yaml  |
                         +-------------+---------------+
                                       |
                                       v
+-------------------+      +-------------------------+        +-------------------------------------------+
| Ingestion Service | ---> | Feature Service + Redis | -----> | Model Services (Linear/Bagging/KNN/AMF)   |
| FastAPI :8002     |      | FastAPI :8001           |        | FastAPI (ClusterIP :8010-:8013 → container :8000)  |
| /next (CSV data)  |      |                         |        |                                           |
| /next/{crypto}    |      |                         |        |                                           |
+-------------------+      +-------------------------+        +-------------------------------------------+
          ^                           |                                        |
          |                           |                                        |
          |                           v                                        v
          |                    Redis feature cache                Prometheus scrapes /metrics endpoints
          |                  (ml-services namespace)                      Grafana visualises metrics
          |
          +---- Coinbase API (live crypto prices)

Observability namespace runs Prometheus, Grafana, Loki, and Promtail. Argo components live in the argo namespace, and all ML services plus Redis reside in ml-services.
```

## Repository Layout

```
.
├── Makefile                           # k3d bootstrap, kustomize apply, cron workflow helper
├── README.md                          # Project documentation (this file)
├── .github/workflows/                 # GitHub Actions for every workload
│   ├── coinbase_ci.yml
│   ├── e2e_job_ci.yml
│   ├── features_ci.yml
│   ├── ingestion.yml
│   └── model_ci.yml
├── infra/
│   ├── k8s/
│   │   ├── argo/                     # Argo controller + server manifests
│   │   ├── ml-services/              # Deployments & services for Redis + microservices
│   │   └── monitoring/               # Prometheus, Grafana, Loki, Promtail manifests
│   ├── workflows/
│   │   └── v1/ml-pipeline-v1.yaml    # CronWorkflow (every minute) running the end-to-end job
│   └── kustomization.yaml            # Root Kustomize entrypoint
├── jobs/
│   └── e2e_job/
│       ├── pipeline.py               # Async orchestration hitting all services
│       ├── Dockerfile                # Non-root job image
│       └── tests/                    # Lightweight unit tests for job code
├── pipelines/

│   ├── feature_service/              # Lag feature computation + Redis integration
│   ├── ingestion_service/            # Dataset streaming API
│   └── model_service/                # Online ML API (replicated for each model type)
└── util/Model_Metrics_Dashboard.json # Grafana dashboard for model metrics
```

## Microservices

### Ingestion Service (`pipelines/ingestion_service`, LoadBalancer :8002)
- Streams `data.csv` (744 monthly observations) one record at a time with stateful iteration and reset.
- FastAPI application exposing `GET /next`, `GET /next/{crypto}`, `POST /reset`, `GET /status`, and `GET /health`.
- Dynamic crypto endpoint: `GET /next/BTC`, `GET /next/XRP`, etc. fetch live prices from Coinbase API in standard format.
- Backed by Pandas for CSV management and aiohttp for external API calls.
- Tested with `pytest` via `TestClient` (`pipelines/ingestion_service/tests/test_ingestion.py`).
- Container image: `r0d3r1ch25/ml-ingestion:latest` built automatically by GitHub Actions.

### Feature Service (`pipelines/feature_service`, LoadBalancer :8001)
- Wraps `LagFeatureManager`, which uses Redis lists for persistent lag storage with automatic fallback to in-memory deques when Redis is unavailable.
- Produces `in_1 ... in_N` features where `N` is controlled by `N_LAGS` (deployment sets 15; CI/test suite pins 10 via environment variables).
- Endpoints: `GET /health`, `GET /info`, `POST /add` returning model-ready feature vectors and `available_lags` metadata per series.
- Extensive unit tests (`tests/test_api.py`, `tests/test_features.py`) and integration tests (`tests/test_integration.py`) that validate multiple series behaviour, lag ordering, and resilience when Redis is offline.
- Container image: `r0d3r1ch25/ml-features:latest`.

### Model Services (`pipelines/model_service`, ClusterIP :8010-:8013 → container :8000)
- Plugin-based architecture supporting multiple ML libraries with `BaseModel` interface and library-specific wrappers.
- Currently hosts four River ML models: linear regression, KNN regressor, AMF regressor, and bagging regressor (3 ridge models).
- Exposes `POST /predict_learn`, `POST /predict_many` (5-step recursive forecast), `GET /model_metrics`, and `GET /metrics` (Prometheus format) plus standard `GET /health`.
- `MetricsManager` maintains rolling MAE/MSE/RMSE/MAPE windows (5/10/20) and last prediction diagnostics per logical series.
- Services are ClusterIP by design; access externally with `kubectl port-forward -n ml-services svc/model-linear 8010:8010` (and similar for bagging/knn/amfr).
- Comprehensive tests in `tests/test_requests.py` covering predict_learn functionality, edge cases, validation errors, and Prometheus formatting.
- Container image: `r0d3r1ch25/ml-model:latest` reused across all four deployments with different `MODEL_NAME` environment variables.



## Online Pipeline & Orchestration
- `jobs/e2e_job/pipeline.py` is an asyncio-driven orchestrator that fetches an observation, requests features, and fans out `predict_learn` calls across all four model services (Linear, Bagging, KNN, AMFR) concurrently. It logs structured progress, emits durations per model, and surfaces prediction errors inline.
- Container image `r0d3r1ch25/ml-e2e-job:latest` backs the CronWorkflow defined in `infra/argo/workflows/v1/ml-pipeline-v1.yaml`.
- CronWorkflow schedule: `* * * * *` (every minute) with `concurrencyPolicy: Forbid`, `successfulJobsHistoryLimit: 20`, and `failedJobsHistoryLimit: 5`. Adjust the cadence in the workflow manifest before applying if you do not need per-minute executions.
- Workflow runs under the `argo` namespace; use the Argo CLI or UI to observe lineage, restart runs, or inspect pod logs.

## Infrastructure & Deployment Model
- Lightweight Kubernetes provided by `k3d`. `make cluster-up` provisions a cluster with LoadBalancer ports for FastAPI services, Argo UI (2746), Grafana (3000), Prometheus (9090), and Loki (3100).
- Deployments and services managed with Kustomize overlays at `infra/k8s`. Namespaces:
  - `ml-services`: ingestion, feature, model microservices plus Redis.
  - `argo`: workflow-controller and Argo server (using upstream quick start manifest).
  - `monitoring`: Prometheus, Grafana, Loki, Promtail with cross-namespace scraping configuration.
- Every deployment defines resource requests/limits, liveness/readiness probes, environment-driven configuration (e.g., `N_LAGS`, `MODEL_NAME`), and non-root security contexts.
- Redis deployment (`infra/k8s/ml-services/deployments/redis-deployment.yaml`) offers persistence for lag buffers within the cluster lifetime; feature service automatically degrades gracefully if Redis is unreachable.
- `Makefile` helpers:
  - `make cluster-up`: create the k3d cluster.
  - `make apply`: `kubectl apply -k infra/k8s/` (installs Argo, monitoring stack, and all services).
  - `make cron`: apply the CronWorkflow from `infra/workflows/v1/ml-pipeline-v1.yaml`.
  - `make cluster-down`: delete the k3d cluster.

## Observability & Monitoring
- Prometheus configuration (`infra/k8s/monitoring/configmaps/prometheus-config.yaml`) scrapes each model service’s `/metrics` endpoint at 60s intervals and includes self-monitoring for Prometheus itself.
- Grafana (`infra/k8s/monitoring/deployments/grafana.yaml`) is pre-wired with Prometheus and Loki data sources. Import `util/Model_Metrics_Dashboard.json` to visualise per-model accuracy trends, error deltas, and request throughput.
- Loki + Promtail capture logs across namespaces; query by labels such as `{namespace="ml-services"}` or `{app=~"model-.*"}` for targeted debugging.
- Argo UI (accessible via `https://localhost:2746` when using port-forwarding) provides workflow-level visibility and log access for the job pods.

## Continuous Delivery
- GitHub Actions workflows are scoped per component using path filters:
  - `ingestion.yml`, `features_ci.yml`, `model_ci.yml`, `coinbase_ci.yml`, `e2e_job_ci.yml`.
- Each workflow checks out the repository, installs dependencies, runs `pytest`, builds Docker images, authenticates to Docker Hub, and publishes `r0d3r1ch25/ml-*` images.
- `pipelines/feature_service/tests/*` and `pipelines/model_service/tests/*` cover both service contracts and business logic, preventing regressions before images are pushed.
- Workflows target `linux/arm64` (adjust as required) and rely on `DOCKER_USERNAME`/`DOCKER_PASSWORD` secrets for registry access.

## Data & Feature Management
- Source dataset: `pipelines/ingestion_service/data.csv` (744 rows) representing monthly values with seasonality and trend; it drives deterministic replay for experimentation.
- Feature service persists lag sequences per `series_id` to Redis keys like `series:<id>:values`. The service always returns a dense feature vector with zero-filled gaps to maintain schema stability for downstream models.
- `available_lags` in the API response signals how many historical values were present prior to inserting the current observation, aiding feature completeness checks.
- Metrics API from model services returns per-series histories, enabling downstream reporting or drift monitoring outside Grafana.

## Testing & Quality Gates
- Unit and integration tests are available for every workload:
  - Ingestion: `pipelines/ingestion_service/tests/test_ingestion.py` exercises stream boundaries and HTTP responses.
  - Feature service: API, logic, and end-to-end tests with optional Redis mocking.
  - Model service: `tests/test_requests.py` validates training, prediction, error handling, metrics, and Prometheus output.
  - Coinbase service: smoke test for health endpoint.
  - E2E job: `jobs/e2e_job/tests/test_pipeline.py` covers logging and module imports.
- Tests run automatically in CI and can be executed locally with `pytest` commands from the repo root or service directories.

## Getting Started
1. **Prerequisites**: Docker, `k3d`, `kubectl`, and optionally the Argo CLI (`argo`) and `kubectl krew` plugins for observability. Ensure Docker Hub credentials exist if you need to rebuild images.
2. **Create a cluster**:
   ```bash
   make cluster-up
   ```
3. **Deploy the stack**:
   ```bash
   make apply
   kubectl get pods -A
   ```
4. **(Optional) Start scheduled runs**:
   ```bash
   make cron
   argo list -n argo
   ```
5. **Access services**:
   - Feature service: `http://localhost:8001/health`
   - Ingestion service: `http://localhost:8002/next` (CSV data) or `http://localhost:8002/next/BTC` (crypto)
   - Model services: `kubectl port-forward -n ml-services svc/model-linear 8010:8010` (and similar for bagging/knn/amfr)
   - Grafana: `http://localhost:3000` (default `admin/admin`)
   - Prometheus: `http://localhost:9090`
   - Loki API: `http://localhost:3100`
   - Argo UI: `https://localhost:2746` (accept the self-signed certificate)
6. **Tear down** when done:
   ```bash
   make cluster-down
   ```

## Operating the Platform
- **Trigger the pipeline manually**: Port-forward the model service of choice, then chain the ingestion → feature → model calls. Example:
  ```bash
  OBS=$(curl -s http://localhost:8002/next)
  FEAT=$(echo "$OBS" | jq '{series_id: "manual", value: .target}' | curl -sX POST -H "Content-Type: application/json" --data-binary @- http://localhost:8001/add)
  curl -sX POST -H "Content-Type: application/json" --data "{\"features\": $(echo "$FEAT" | jq '.features'), \"target\": $(echo "$FEAT" | jq '.target')}" http://localhost:8010/predict_learn
  ```
- **Inspect workflow runs**: `argo get cron-v1 -n argo` or use the Argo UI to view DAGs, pod logs, and execution timelines.
- **Monitor metrics**: open Grafana and import `util/Model_Metrics_Dashboard.json`, or query Prometheus directly:
  - `ml_model_mae_10{model="ridge_regression"}`
  - `ml_model_predictions_total{series="default"}`
  - `ml_model_last_error{model="amf_regressor"}`
- **Review logs**: `kubectl logs -n ml-services deployment/model-linear`, or run a Loki query such as `{app="model-linear"} |= "ERROR"` in Grafana Explore.

## API Quick Reference

### Ingestion Service (`http://<host>:8002`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Returns service status and dataset size. |
| GET    | `/next`   | Streams next observation; returns 204 when the dataset is exhausted. |
| GET    | `/next/{crypto}` | Fetches live crypto price from Coinbase API (e.g., `/next/BTC`, `/next/XRP`). |
| POST   | `/reset`  | Resets stream cursor to the beginning of the dataset. |
| GET    | `/status` | Reports current index, remaining observations, and completion flag. |

### Feature Service (`http://<host>:8001`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Health probe for Kubernetes. |
| GET    | `/info`   | Reports service metadata including `max_lags` and output schema. |
| POST   | `/add`    | Accepts `{series_id, value}` and returns lag features, current target, and `available_lags`. |

### Model Services (port-forward to desired service)
| Service | Port-forward command | Notes |
|---------|----------------------|-------|
| Linear Regression | `kubectl port-forward -n ml-services svc/model-linear 8010:8010` | Access API at `http://localhost:8010`. |
| Bagging Regressor | `kubectl port-forward -n ml-services svc/model-bagging 8011:8011` | 3 ridge models ensemble. |
| KNN Regressor     | `kubectl port-forward -n ml-services svc/model-knn 8012:8012`    | k=5 neighbors. |
| AMF Regressor     | `kubectl port-forward -n ml-services svc/model-amfr 8013:8013`   | Adaptive model forest. |

Common endpoints once port-forwarded:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/health` | Quick readiness probe. |

| POST   | `/predict_learn` | Predicts then updates the model and rolling metrics in one call. |
| POST   | `/predict_many` | Returns 5-step recursive forecast with lag feature shifting. |
| GET    | `/model_metrics` | JSON summary containing counts, rolling metrics, last prediction, and model info. |
| GET    | `/metrics` | Prometheus-formatted gauges and counters ready for scraping. |



## Troubleshooting & Operations
- **Redis fallback**: Check feature-service logs for `REDIS CONNECTED` or `REDIS UNAVAILABLE` messages. Use `kubectl exec -n ml-services deployment/redis -- redis-cli LRANGE "series:default:values" 0 -1` to inspect stored lags.
- **External API rate limits**: Coinbase requests may fail if the remote API throttles traffic. The service surfaces HTTP 500 with the upstream error message; scale replicas or add caching as needed.
- **Workflow noise**: The CronWorkflow runs every minute by default. Disable with `kubectl delete cronworkflow cron-v1 -n argo` if you prefer manual triggers.
- **Certificate warnings**: The Argo server exposes HTTPS with self-signed certs. Use `--insecure-skip-tls-verify` flags or import the certificate for local trust during development.
- **Resource pressure**: Update resource requests/limits in `infra/k8s/ml-services/deployments/*.yaml` and re-apply. k3d defaults are conservative; adjust for heavier loads.

## Operational Backlog
To elevate the platform further, consider the following next steps:
- Introduce staged environments (dev/staging/prod) with image promotion policies and GitOps automation (e.g., Argo CD or Flux).
- Add model and feature registries, experiment tracking, and automated canary/champion-challenger promotion for new models.
- Implement data quality validation, point-in-time joins, and offline backfills to evolve the feature service toward a full feature store.
- Harden security: cluster network policies, secret management (e.g., External Secrets Operator), vulnerability scanning, and TLS termination across services.
- Expand testing depth with contract tests between services, load tests for the async pipeline, and chaos experiments for Redis/feature-store failure scenarios.

---

This documentation reflects the current production-style implementation and is intended to guide deployments, operations, and continued iteration of the Online Learning MLOps Platform.
