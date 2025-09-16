#!/bin/bash

API_URL="http://localhost:30090"

echo "=== Testing Feature Service API ==="

echo "1. Health Check:"
curl -s "$API_URL/health" | jq

echo -e "\n2. Service Info:"
curl -s "$API_URL/info" | jq

echo -e "\n3. Add Observations:"
curl -s -X POST "$API_URL/add_observation" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "value": 100}' | jq

curl -s -X POST "$API_URL/add_observation" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "value": 105}' | jq

curl -s -X POST "$API_URL/add_observation" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "value": 110}' | jq

echo -e "\n4. Get Features (POST):"
curl -s -X POST "$API_URL/features" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "num_lags": 3}' | jq

echo -e "\n5. Get Features (GET):"
curl -s "$API_URL/features/test_series?num_lags=2" | jq

echo -e "\n6. Add More Observations:"
for value in 115 120 125; do
  curl -s -X POST "$API_URL/add_observation" \
    -H "Content-Type: application/json" \
    -d "{\"series_id\": \"test_series\", \"value\": $value}" | jq
done

echo -e "\n7. Final Features:"
curl -s -X POST "$API_URL/features" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "test_series", "num_lags": 5}' | jq

echo -e "\n8. Service Info (Final):"
curl -s "$API_URL/info" | jq

echo -e "\n=== Feature Service Test Complete ==="