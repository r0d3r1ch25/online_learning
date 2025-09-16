# Variables
CLUSTER_NAME = fti-predict-cluster
ARGO_WORKFLOWS_VERSION = "v3.5.5"

# Create k3d cluster
.PHONY: cluster-up
cluster-up:
	k3d cluster create $(CLUSTER_NAME) --port "30080:30080@server:0" --port "30090:30090@server:0"

# Delete k3d cluster
.PHONY: cluster-down
cluster-down:
	k3d cluster delete $(CLUSTER_NAME)

# Apply Kubernetes manifests
.PHONY: apply
apply:
	kubectl apply -k infra/k8s/

# Deploy Argo Workflows
.PHONY: argo
argo:
	kubectl create namespace argo || true
	kubectl apply -n argo -f "https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/quick-start-minimal.yaml"

# Test API
.PHONY: test-api
test-api:
	cd infra && ./test_api.sh

# Clean up deployments
.PHONY: clean
clean:
	kubectl delete -k infra/k8s/ || true