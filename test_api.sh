#!/bin/bash

API_URL="http://100.114.152.108:30080"

echo "=== Testing Online Learning API ==="

echo "1. Health Check:"
curl -s "$API_URL/health" | jq

echo -e "\n2. Initial Metrics:"
curl -s "$API_URL/metrics" | jq

echo -e "\n3. Train Model with Initial Data:"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "test_series",
    "observations": [
      {"timestamp": "2025-01-20", "value": 100},
      {"timestamp": "2025-01-21", "value": 110}
    ]
  }' | jq

echo -e "\n4. First Prediction:"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "horizon": 1}' | jq

echo -e "\n5. Predict and Learn (Model Updates):"
curl -s -X POST "$API_URL/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "y_real": 120}' | jq

echo -e "\n6. Second Prediction (Should be Different):"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "horizon": 1}' | jq

echo -e "\n7. Another Predict and Learn:"
curl -s -X POST "$API_URL/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "y_real": 130}' | jq

echo -e "\n8. Final Prediction (Model Learned):"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "horizon": 1}' | jq

echo -e "\n9. Final Metrics:"
curl -s "$API_URL/metrics" | jq

echo -e "\n=== Model Learning Test Complete ==="
