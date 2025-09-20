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

# Add first observation to feature service and train model
echo "Step 1: Add observation 100.0"
FEATURES=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 100.0}" | jq -r '.features')

echo "Features from feature service: $FEATURES"

# Train model with these features
echo "Training model with features..."
curl -s -X POST "$MODEL_URL/train" \
  -H "Content-Type: application/json" \
  -d "{\"features\": $FEATURES, \"target\": 105.0}" | jq

# Add second observation
echo -e "\nStep 2: Add observation 105.0"
FEATURES=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 105.0}" | jq -r '.features')

echo "Features from feature service: $FEATURES"

# Train model
echo "Training model with features..."
curl -s -X POST "$MODEL_URL/train" \
  -H "Content-Type: application/json" \
  -d "{\"features\": $FEATURES, \"target\": 110.0}" | jq

# Add third observation and predict
echo -e "\nStep 3: Add observation 110.0 and predict"
FEATURES=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 110.0}" | jq -r '.features')

echo "Features from feature service: $FEATURES"

# Predict with these features
echo "Predicting with features..."
curl -s -X POST "$MODEL_URL/predict" \
  -H "Content-Type: application/json" \
  -d "{\"features\": $FEATURES}" | jq

# Add fourth observation and use predict_learn
echo -e "\nStep 4: Add observation 115.0 and predict_learn"
FEATURES=$(curl -s -X POST "$FEATURE_URL/add" \
  -H "Content-Type: application/json" \
  -d "{\"series_id\": \"$SERIES_ID\", \"value\": 115.0}" | jq -r '.features')

echo "Features from feature service: $FEATURES"

# Predict and learn
echo "Predict and learn with features..."
curl -s -X POST "$MODEL_URL/predict_learn" \
  -H "Content-Type: application/json" \
  -d "{\"features\": $FEATURES, \"target\": 120.0}" | jq

echo -e "\n4. Final Model Metrics:"
curl -s "$MODEL_URL/model_metrics" | jq

echo -e "\n5. Feature Service Series Info:"
curl -s "$FEATURE_URL/series/$SERIES_ID" | jq

echo -e "\n=== Integration Test Complete ==="
echo "Feature service successfully provides model-ready features to model service"