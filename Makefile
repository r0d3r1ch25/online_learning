# Variables
CLUSTER_NAME = fti-predict-cluster

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  cluster-up    - Create k3d cluster"
	@echo "  cluster-down  - Delete k3d cluster"
	@echo "  k8s-apply     - Apply Kubernetes manifests"
	@echo "  k8s-delete    - Delete Kubernetes resources"

# Create k3d cluster
.PHONY: cluster-up
cluster-up:
	k3d cluster create $(CLUSTER_NAME) --port "30080:30080@server:0"

# Delete k3d cluster
.PHONY: cluster-down
cluster-down:
	k3d cluster delete $(CLUSTER_NAME)

# Apply Kubernetes manifests
.PHONY: k8s-apply
k8s-apply:
	kubectl apply -f k8s/

# Delete Kubernetes resources
.PHONY: k8s-delete
k8s-delete:
	kubectl delete -f k8s/