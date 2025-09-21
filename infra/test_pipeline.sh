#!/bin/bash

INGESTION_URL="http://localhost:8002"
FEATURE_URL="http://localhost:8001"
MODEL_URL="http://localhost:8000"
SERIES_ID="pipeline_test"

echo "=== Testing Complete ML Pipeline ==="

# Reset ingestion stream
curl -s -X POST "$INGESTION_URL/reset"

# Process 144 observations with predict_learn
for i in $(seq 1 144); do
    echo "Processing observation $i/144 (predict_learn)"
    
    # Pipeline: Ingestion -> Feature -> Model (Predict & Learn)
    curl -s "$INGESTION_URL/next" \
    | jq '{series_id: "pipeline_test", value: .target}' \
    | curl -s -X POST \
        -H "Content-Type: application/json" \
        --data-binary @- \
        "$FEATURE_URL/add" \
    | jq '{features: .features, target: .target}' \
    | curl -s -X POST \
        -H "Content-Type: application/json" \
        --data-binary @- \
        "$MODEL_URL/predict_learn"
    
    echo "Sleeping 60 seconds..."
    sleep 60
done

echo "Pipeline complete - check Prometheus metrics"