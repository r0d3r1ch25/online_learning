#!/usr/bin/env python3

import requests
import json
import sys

API_URL = "http://localhost:8001"

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
    print("=== Testing Feature Service API ===")
    
    # 1. Health Check
    test_endpoint("1. Health Check", "GET", "/health")
    
    # 2. Service Info
    test_endpoint("2. Service Info", "GET", "/info")
    
    # 3. Extract features with first value
    test_endpoint("3. Extract Features (First Value)", "POST", "/extract", {
        "series_id": "test_series",
        "value": 100.0
    })
    
    # 4. Extract features with second value
    test_endpoint("4. Extract Features (Second Value)", "POST", "/extract", {
        "series_id": "test_series", 
        "value": 105.0
    })
    
    # 5. Extract features with third value
    test_endpoint("5. Extract Features (Third Value)", "POST", "/extract", {
        "series_id": "test_series",
        "value": 110.0
    })
    
    # 6. Extract features with fourth value (should show lag pattern)
    result = test_endpoint("6. Extract Features (Fourth Value - Show Lags)", "POST", "/extract", {
        "series_id": "test_series",
        "value": 115.0
    })
    
    # 7. Verify model-ready format
    if result and "features" in result:
        features = result["features"]
        print(f"\nModel-Ready Features Verification:")
        print(f"in_1 (most recent): {features.get('in_1')}")
        print(f"in_2 (lag_2): {features.get('in_2')}")
        print(f"in_3 (lag_3): {features.get('in_3')}")
        print(f"in_4 (lag_4): {features.get('in_4')}")
        print(f"Available lags: {result.get('available_lags')}")
    
    # 8. Test different series
    test_endpoint("8. Extract Features (Different Series)", "POST", "/extract", {
        "series_id": "another_series",
        "value": 200.0
    })
    
    # 9. Get series info
    test_endpoint("9. Get Series Info", "GET", "/series/test_series")
    
    # 10. Service info (final)
    test_endpoint("10. Service Info (Final)", "GET", "/info")
    
    # 11. Test with more values to fill all 12 lags
    print("\n11. Testing All 12 Lags:")
    values = [120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175]
    for i, value in enumerate(values, 5):
        result = test_endpoint(f"  Extract {i}", "POST", "/extract", {
            "series_id": "full_series",
            "value": value
        })
        if i == len(values) + 4:  # Last iteration
            if result and "features" in result:
                print(f"\nAll 12 Features Filled:")
                for j in range(1, 13):
                    print(f"  in_{j}: {result['features'].get(f'in_{j}')}")
    
    print("\n=== Feature Service Test Complete ===")
    print("Features are now in model-ready format (in_1 to in_12)")
    print("Ready for direct input to model service")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
        print(f"Using API URL: {API_URL}")
    
    main()