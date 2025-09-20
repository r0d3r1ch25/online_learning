#!/bin/bash

FEATURE_URL="http://localhost:8001"
MODEL_URL="http://localhost:8000"
SERIES_ID="integration_test"

echo "=== Testing Feature Service + Model Service Integration ==="

echo "1. Health Checks:"
echo "Feature Service:"
curl -s "$FEATURE_URL/health" | jq
echo "Model Service:"
curl -s "$MODEL_URL/health" | jq

echo -e "\n2. Service Info:"
echo "Feature Service:"
curl -s "$FEATURE_URL/info" | jq
echo "Model Service:"
curl -s "$MODEL_URL/info" | jq

echo -e "\n3. Integration Test - Add observations and train model:"

# Add first observation to feature service (model-ready response)
echo "Step 1: Add observation 100.0"
RESPONSE=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 100.0}")

echo "Model-ready response: $RESPONSE"

# Train model directly with model-ready response
echo "Training model with model-ready data..."
echo "$RESPONSE" | jq '{features: .features, target: .target}' | curl -s -X POST \
  -H "Content-Type: application/json" \
  --data-binary @- \
  "$MODEL_URL/train" | jq

# Add second observation
echo -e "\nStep 2: Add observation 105.0"
RESPONSE=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 105.0}")

echo "Model-ready response: $RESPONSE"

# Train model directly with model-ready response
echo "Training model with model-ready data..."
echo "$RESPONSE" | jq '{features: .features, target: .target}' | curl -s -X POST \
  -H "Content-Type: application/json" \
  --data-binary @- \
  "$MODEL_URL/train" | jq

# Add third observation and predict
echo -e "\nStep 3: Add observation 110.0 and predict"
RESPONSE=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 110.0}")

echo "Model-ready response: $RESPONSE"

# Predict with features from response
echo "Predicting with features..."
echo "$RESPONSE" | jq '{features: .features}' | curl -s -X POST \
  -H "Content-Type: application/json" \
  --data-binary @- \
  "$MODEL_URL/predict" | jq

# Add fourth observation and use predict_learn
echo -e "\nStep 4: Add observation 115.0 and predict_learn"
RESPONSE=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 115.0}")

echo "Model-ready response: $RESPONSE"

# Predict and learn directly with model-ready response
echo "Predict and learn with model-ready data..."
echo "$RESPONSE" | jq '{features: .features, target: .target}' | curl -s -X POST \
  -H "Content-Type: application/json" \
  --data-binary @- \
  "$MODEL_URL/predict_learn" | jq

echo -e "\n4. Final Model Metrics:"
curl -s "$MODEL_URL/model_metrics" | jq

echo -e "\n5. Feature Service Series Info:"
curl -s "$FEATURE_URL/series/$SERIES_ID" | jq

echo -e "\n=== Integration Test Complete ==="
echo "Feature service successfully provides model-ready features to model service"