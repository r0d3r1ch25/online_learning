# Infrastructure automation for Online Learning MLOps Platform

.PHONY: cluster-up cluster-down apply again argo-e2e coinbase-deploy

# Cluster management
cluster-up:
	k3d cluster create online-learning \
		--port "8000:8000@loadbalancer" \
		--port "8001:8001@loadbalancer" \
		--port "8002:8002@loadbalancer" \
		--port "8003:8003@loadbalancer" \
		--port "2746:2746@loadbalancer" \
		--port "3000:3000@loadbalancer" \
		--port "9090:9090@loadbalancer" \
		--port "3100:3100@loadbalancer"

cluster-down:
	k3d cluster delete online-learning

# Deploy all services
apply:
	kubectl apply -k infra/k8s/

# Deploy only coinbase service
coinbase-deploy:
	kubectl apply -f infra/k8s/ml-services/namespace.yaml
	kubectl apply -f infra/k8s/ml-services/deployments/coinbase-deployment.yaml
	kubectl apply -f infra/k8s/ml-services/services/coinbase-service.yaml

# Reset cluster with latest code
again: cluster-down cluster-up apply

# Start CronWorkflow
argo-e2e:
	kubectl apply -f infra/workflows/v1/online-learning-pipeline-v1.yaml