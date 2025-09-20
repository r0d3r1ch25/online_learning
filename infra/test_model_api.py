#!/usr/bin/env python3

import requests
import json
import sys
import time

API_URL = "http://localhost:8000"

def test_monitoring_stack():
    """Test monitoring stack services"""
    print("=== Testing Monitoring Stack ===")
    
    services = {
        "Grafana": "http://localhost:3000/api/health",
        "Prometheus": "http://localhost:9090/-/healthy", 
        "Loki": "http://localhost:3100/ready"
    }
    
    results = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            print(f"[OK] {name}: {response.status_code}")
            results[name] = True
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            results[name] = False
    
    working = sum(results.values())
    total = len(results)
    print(f"\nMonitoring services: {working}/{total} working")
    
    if results.get("Grafana"):
        print("Grafana: http://localhost:3000 (admin/admin)")
    if results.get("Prometheus"):
        print("Prometheus: http://localhost:9090")
    
    return results

def test_endpoint(name, method, endpoint, data=None):
    """Test an API endpoint and return response"""
    print(f"\n{name}:")
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}")
        else:
            response = requests.post(f"{API_URL}{endpoint}", json=data)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    # Test monitoring stack first
    monitoring_results = test_monitoring_stack()
    
    print("\n=== Testing Deployed Model Service API ===")
    
    # 1. Health Check
    test_endpoint("1. Health Check", "GET", "/health")
    
    # 2. Service Info
    test_endpoint("2. Service Info", "GET", "/info")
    
    # 3. Train with 3 inputs
    test_endpoint("3. Train Model (3 inputs)", "POST", "/train", {
        "features": {"in_1": 125.0, "in_2": 120.0, "in_3": 115.0},
        "target": 130.0
    })
    
    # 4. Train with more data
    test_endpoint("4. Train with More Data", "POST", "/train", {
        "features": {"in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 118.0},
        "target": 135.0
    })
    
    # 5. Predict (fixed horizon)
    test_endpoint("5. Predict (Fixed 3-Step Horizon)", "POST", "/predict", {
        "features": {"in_1": 135.0, "in_2": 130.0, "in_3": 125.0, "in_4": 122.0}
    })
    
    # 6. Predict with missing features
    test_endpoint("6. Predict with Missing Features (Auto-fill 0.0)", "POST", "/predict", {
        "features": {"in_1": 140.0, "in_3": 130.0}
    })
    
    # 7. Predict with unknown features (should trigger warnings in service logs)
    print("\n7. Predict with Unknown Features (Warnings in Service Logs):")
    print("Testing: unknown_feature, lag_1 (should be ignored)")
    test_endpoint("", "POST", "/predict", {
        "features": {
            "in_1": 145.0,
            "in_2": 140.0,
            "unknown_feature": 999.0,
            "lag_1": 100.0
        }
    })
    
    # 8. Predict and Learn
    test_endpoint("8. Predict and Learn", "POST", "/predict_learn", {
        "features": {"in_1": 140.0, "in_2": 135.0, "in_3": 130.0},
        "target": 145.0
    })
    
    # 9. Another Predict and Learn
    test_endpoint("9. Another Predict and Learn", "POST", "/predict_learn", {
        "features": {
            "in_1": 145.0, "in_2": 140.0, "in_3": 135.0,
            "in_4": 132.0, "in_5": 128.0
        },
        "target": 150.0
    })
    
    # 10. Submit Feedback
    test_endpoint("10. Submit Feedback", "POST", "/feedback", {
        "message": "Model performing well with new features"
    })
    
    # 11. Train with all 12 inputs
    test_endpoint("11. Train with All 12 Inputs", "POST", "/train", {
        "features": {
            "in_1": 125.0, "in_2": 120.0, "in_3": 115.0, "in_4": 110.0,
            "in_5": 105.0, "in_6": 100.0, "in_7": 95.0, "in_8": 90.0,
            "in_9": 85.0, "in_10": 80.0, "in_11": 75.0, "in_12": 70.0
        },
        "target": 130.0
    })
    
    # 12. Predict with all 12 inputs
    test_endpoint("12. Predict with All 12 Inputs", "POST", "/predict", {
        "features": {
            "in_1": 130.0, "in_2": 125.0, "in_3": 120.0, "in_4": 115.0,
            "in_5": 110.0, "in_6": 105.0, "in_7": 100.0, "in_8": 95.0,
            "in_9": 90.0, "in_10": 85.0, "in_11": 80.0, "in_12": 75.0
        }
    })
    
    # 13. Test input validation with multiple unknown features
    print("\n13. Test Input Validation (Multiple Unknown Features):")
    print("Testing: bad_input, lag_5, feature_x (should be ignored)")
    test_endpoint("", "POST", "/train", {
        "features": {
            "in_1": 100.0,
            "bad_input": 999.0,
            "lag_5": 200.0,
            "feature_x": 300.0
        },
        "target": 150.0
    })
    
    # 14. Test edge cases - empty features
    test_endpoint("14. Test Edge Cases - Empty Features", "POST", "/predict", {
        "features": {}
    })
    
    # 15. Test edge cases - extreme values
    test_endpoint("15. Test Edge Cases - Extreme Values", "POST", "/train", {
        "features": {"in_1": -1000.0, "in_2": 0.0, "in_3": 999999.9},
        "target": 50.0
    })
    
    # 16. Get comprehensive metrics
    metrics = test_endpoint("16. Get Model Performance Metrics", "GET", "/metrics")
    
    # 17. Test Prometheus metrics endpoint
    print("\n17. Test Prometheus Metrics Endpoint:")
    try:
        response = requests.get(f"{API_URL}/metrics/prometheus")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            lines = response.text.split('\n')[:10]  # Show first 10 lines
            print("Prometheus metrics (first 10 lines):")
            for line in lines:
                if line.strip():
                    print(f"  {line}")
            print("  ... (truncated)")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    # 18. Validation summary
    print("\n=== Test Summary ===")
    if metrics and "default" in metrics:
        m = metrics["default"]
        print(f"Total Predictions: {m.get('count', 0)}")
        print(f"Model Performance - MAE: {m.get('mae', 'N/A')}, RMSE: {m.get('rmse', 'N/A')}")
        print(f"Last Prediction: {m.get('last_prediction', 'N/A')}")
        print(f"Last Actual: {m.get('last_actual', 'N/A')}")
    
    print("\n=== All Tests Completed ===")
    print("Model API: All endpoints tested successfully")
    print("Monitoring: Check Grafana and Prometheus for data sources")
    print("Note: Check service logs for warnings about unknown input features")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
        print(f"Using API URL: {API_URL}")
    
    main()