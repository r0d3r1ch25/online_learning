# Infrastructure automation for Online Learning MLOps Platform

CLUSTER_NAME = ml-cluster

.PHONY: cluster-up cluster-down apply cron

# Cluster management
cluster-up:
	k3d cluster create $(CLUSTER_NAME) \
		--port "8001:8001@loadbalancer" \
		--port "8002:8002@loadbalancer" \
		--port "8003:8003@loadbalancer" \
		--port "5432:5432@loadbalancer" \
		--port "2746:2746@loadbalancer" \
		--port "3000:3000@loadbalancer" \
		--port "9090:9090@loadbalancer" \
		--port "3100:3100@loadbalancer"

cluster-down:
	k3d cluster delete $(CLUSTER_NAME)

# Deploy all services
apply:
	kubectl apply -k infra/k8s/

# Start CronWorkflow (all 4 models in parallel)
cron:
	kubectl apply -f infra/k8s/argo/workflows/v1/ml-pipeline-v1.yaml