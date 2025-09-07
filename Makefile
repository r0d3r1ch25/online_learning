# Variables
IMAGE_NAME = r0d3r1ch25/fti_predict_learn
TAG = latest
DOCKERFILE = Dockerfile

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  build    - Build Docker image"
	@echo "  push     - Push Docker image to registry"
	@echo "  test     - Run pytest"
	@echo "  run      - Run container locally"
	@echo "  clean    - Remove local Docker image"
	@echo "  all      - Build, test, and push"

# Build Docker image
.PHONY: build
build:
	docker build -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE) .

# Push Docker image
.PHONY: push
push:
	docker push $(IMAGE_NAME):$(TAG)

# Run tests
.PHONY: test
test:
	python3 -m pytest tests/ -v

# Run container locally
.PHONY: run
run:
	docker run -p 8000:8000 $(IMAGE_NAME):$(TAG)

# Clean up local image
.PHONY: clean
clean:
	docker rmi $(IMAGE_NAME):$(TAG) || true

# Build, test, and push
.PHONY: all
all: build test push
	@echo "Build, test, and push completed successfully!"

# Install dependencies
.PHONY: install
install:
	python3 -m pip install -r requirements.txt

# Run development server
.PHONY: dev
dev:
	python main.py