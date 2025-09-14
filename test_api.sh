#!/bin/bash

API_URL="http://100.114.152.108:30080"

echo "=== Testing Multi-Feature Online Learning API ==="

echo "1. Health Check:"
curl -s "$API_URL/health" | jq

echo -e "\n2. Initial Metrics:"
curl -s "$API_URL/metrics" | jq

echo -e "\n3. Train Model with Sequential Data (Building Lags):"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "multi_feature_test",
    "observations": [
      {"timestamp": "2025-01-20", "value": 100},
      {"timestamp": "2025-01-21", "value": 105},
      {"timestamp": "2025-01-22", "value": 110},
      {"timestamp": "2025-01-23", "value": 115}
    ]
  }' | jq

echo -e "\n4. First Prediction (With Lag Features):"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "multi_feature_test", "horizon": 1}' | jq

echo -e "\n5. Predict and Learn (Model Uses Lags):"
curl -s -X POST "$API_URL/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "multi_feature_test", "y_real": 120}' | jq

echo -e "\n6. Another Prediction (Lag Features Updated):"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "multi_feature_test", "horizon": 1}' | jq

echo -e "\n7. Test Different Series (Independent Features):"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "series_2",
    "observations": [
      {"timestamp": "2025-01-20", "value": 200},
      {"timestamp": "2025-01-21", "value": 210}
    ]
  }' | jq

echo -e "\n8. Predict for Series 2:"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "series_2", "horizon": 1}' | jq

echo -e "\n9. Final Metrics:"
curl -s "$API_URL/metrics" | jq

echo -e "\n=== Multi-Feature Model Test Complete ==="