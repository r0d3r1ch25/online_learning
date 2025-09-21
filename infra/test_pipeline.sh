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
    
    # Get observation
    OBSERVATION=$(curl -s "$INGESTION_URL/next")
    ACTUAL_VALUE=$(echo "$OBSERVATION" | jq -r '.target')
    echo "Actual value: $ACTUAL_VALUE"
    
    # Get features and predict_learn
    RESULT=$(echo "$OBSERVATION" \
    | jq '{series_id: "pipeline_test", value: .target}' \
    | curl -s -X POST \
        -H "Content-Type: application/json" \
        --data-binary @- \
        "$FEATURE_URL/add" \
    | jq '{features: .features, target: .target}' \
    | curl -s -X POST \
        -H "Content-Type: application/json" \
        --data-binary @- \
        "$MODEL_URL/predict_learn")
    
    PREDICTION=$(echo "$RESULT" | jq -r '.prediction')
    echo "Prediction: $PREDICTION"
    echo "Actual: $ACTUAL_VALUE | Prediction: $PREDICTION"
    
    echo ""
    echo "Waiting 60 seconds..."
    sleep 60
done

echo "Pipeline complete - check Prometheus metrics"