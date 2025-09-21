# Variables
CLUSTER_NAME = ml-cluster
ARGO_WORKFLOWS_VERSION = "v3.5.5"

# Create k3d cluster with LoadBalancer support
.PHONY: cluster-up
cluster-up:
	k3d cluster create $(CLUSTER_NAME) \
		--port "0.0.0.0:8000:8000@loadbalancer" \
		--port "0.0.0.0:8001:8001@loadbalancer" \
		--port "0.0.0.0:8002:8002@loadbalancer" \
		--port "0.0.0.0:6566:6566@loadbalancer" \
		--port "0.0.0.0:9000:9000@loadbalancer" \
		--port "0.0.0.0:9001:9001@loadbalancer" \
		--port "0.0.0.0:2746:2746@loadbalancer" \
		--port "0.0.0.0:6379:6379@loadbalancer" \
		--port "0.0.0.0:3000:3000@loadbalancer" \
		--port "0.0.0.0:3100:3100@loadbalancer" \
		--port "0.0.0.0:9090:9090@loadbalancer" \
		--k3s-arg "--disable=traefik@server:*"

# Delete k3d cluster
.PHONY: cluster-down
cluster-down:
	k3d cluster delete $(CLUSTER_NAME)

# Apply Kubernetes manifests
.PHONY: apply
apply:
	kubectl apply -k infra/k8s/

# Start Argo CronWorkflow
.PHONY: argo-e2e
argo-e2e:
	kubectl apply -f infra/workflows/v1/online-learning-pipeline-v1.yaml -n argo && argo cron list -n argo

# Reset cluster with latest code
.PHONY: again
again:
	make cluster-down && git pull && make cluster-up && make apply
