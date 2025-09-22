# Infrastructure automation for Online Learning MLOps Platform

CLUSTER_NAME = ml-cluster

.PHONY: cluster-up cluster-down apply again argo-e2e

# Cluster management
cluster-up:
	k3d cluster create $(CLUSTER_NAME) \
		--port "8000:8000@loadbalancer" \
		--port "8001:8001@loadbalancer" \
		--port "8002:8002@loadbalancer" \
		--port "8003:8003@loadbalancer" \
		--port "2746:2746@loadbalancer" \
		--port "3000:3000@loadbalancer" \
		--port "9090:9090@loadbalancer" \
		--port "3100:3100@loadbalancer"

cluster-down:
	k3d cluster delete $(CLUSTER_NAME)

# Deploy all services
apply:
	kubectl apply -k infra/k8s/

# Start CronWorkflow
argo-e2e:
	kubectl apply -f infra/workflows/v1/online-learning-pipeline-v1.yaml