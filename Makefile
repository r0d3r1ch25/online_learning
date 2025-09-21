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
.PHONY: argo-hello
argo-hello:
	kubectl apply -f infra/workflows/v0/online-learning-pipeline.yaml -n argo
	echo "CronWorkflow created - runs every 2 minutes"
	echo "Monitor with: argo list -n argo"
	echo "Stop with: kubectl delete cronworkflow online-learning-cron-v0 -n argo"

# Clean up deployments
.PHONY: clean
clean:
	kubectl delete -k infra/k8s/ || true

# Reset cluster with latest code
.PHONY: again
again:
	make cluster-down && git pull && make cluster-up && make apply
