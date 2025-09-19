#!/bin/bash

API_URL="http://localhost:8000"

echo "=== Testing Stateless Model Service API ==="

echo "1. Health Check:"
curl -s "$API_URL/health" | jq

echo -e "\n2. Service Info:"
curl -s "$API_URL/info" | jq

echo -e "\n3. Train Model with Features:"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 125.0,
      "in_2": 120.0,
      "in_3": 115.0
    },
    "target": 130.0
  }' | jq

echo -e "\n4. Train with More Data:"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 130.0,
      "in_2": 125.0,
      "in_3": 120.0,
      "in_4": 118.0
    },
    "target": 135.0
  }' | jq

echo -e "\n5. Predict (Fixed Horizon):"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 135.0,
      "in_2": 130.0,
      "in_3": 125.0,
      "in_4": 122.0
    }
  }' | jq

echo -e "\n6. Predict with Missing Features (Should Fill with 0.0):"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 140.0,
      "in_3": 130.0
    }
  }' | jq

echo -e "\n7. Predict with Unknown Features (Should Warn and Ignore):"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 145.0,
      "in_2": 140.0,
      "unknown_feature": 999.0,
      "lag_1": 100.0
    }
  }' | jq

echo -e "\n8. Predict and Learn:"
curl -s -X POST "$API_URL/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 140.0,
      "in_2": 135.0,
      "in_3": 130.0
    },
    "target": 145.0
  }' | jq

echo -e "\n9. Another Predict and Learn:"
curl -s -X POST "$API_URL/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 145.0,
      "in_2": 140.0,
      "in_3": 135.0,
      "in_4": 132.0,
      "in_5": 128.0
    },
    "target": 150.0
  }' | jq

echo -e "\n10. Submit Feedback:"
curl -s -X POST "$API_URL/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Model performing well with new features"
  }' | jq

echo -e "\n11. Get Metrics:"
curl -s "$API_URL/metrics" | jq

echo -e "\n12. Test Edge Cases - Empty Features:"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {}
  }' | jq

echo -e "\n13. Test All 12 Inputs:"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
      "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
      "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
    },
    "target": 130.0
  }' | jq

echo -e "\n14. Predict with All 12 Inputs:"
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 115.0,
      "in_5": 110.0, "in_6": 105.0, "in_7": 100.0, "in_8": 95.0,
      "in_9": 90.0, "in_10": 85.0, "in_11": 80.0, "in_12": 75.0
    }
  }' | jq

echo -e "\n15. Get Model Performance Metrics:"
curl -s "$API_URL/metrics" | jq

echo -e "\n16. Test Edge Cases - Extreme Values:"
curl -s -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "in_1": -1000.0,
      "in_2": 0.0,
      "in_3": 999999.9
    },
    "target": 50.0
  }' | jq

echo -e "\n=== Stateless Model Service Test Complete ==="