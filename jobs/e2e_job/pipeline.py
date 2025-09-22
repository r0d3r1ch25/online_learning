#!/usr/bin/env python3
"""
End-to-end ML pipeline for Argo Workflows.
Runs ingestion -> features -> model prediction/learning workflow.
"""

import requests
import json
import datetime
import sys
import os

# Service URLs
INGESTION_URL = "http://ingestion-service.ml-services.svc.cluster.local:8002"
FEATURE_URL = "http://feature-service.ml-services.svc.cluster.local:8001"
MODEL_URL = "http://model-service-linear.ml-services.svc.cluster.local:8000"

def log(message):
    """Log with timestamp and flush immediately"""
    print(f"{datetime.datetime.now()}: {message}", flush=True)

def main():
    start_time = datetime.datetime.now()
    
    try:
        # Step 1: Get observation from ingestion service
        response = requests.get(f"{INGESTION_URL}/next", timeout=10)
        
        if response.status_code == 204:
            log("INFO: No more observations available - stream exhausted")
            sys.exit(0)
        
        response.raise_for_status()
        observation = response.json()
        target = observation['target']
        
        # Step 2: Extract features
        response = requests.post(f"{FEATURE_URL}/add", json={"series_id": "argo_e2e_pipeline", "value": target}, timeout=10)
        response.raise_for_status()
        feature_result = response.json()
        
        # Step 3: Model prediction and learning
        response = requests.post(f"{MODEL_URL}/predict_learn", json={"features": feature_result['features'], "target": feature_result['target']}, timeout=10)
        response.raise_for_status()
        model_result = response.json()
        
        # Step 4: Get updated metrics
        response = requests.get(f"{MODEL_URL}/model_metrics", timeout=10)
        response.raise_for_status()
        metrics = response.json()
        
        # All HTTP calls complete - now log everything
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log("=== E2E PIPELINE START ===")
        log(f"[1/4] SUCCESS: Observation {observation.get('observation_id', 'N/A')}: target={target}, remaining={observation.get('remaining', 'N/A')}")
        
        features = feature_result['features']
        log(f"[2/4] SUCCESS: Features extracted: {len(features)} inputs, {feature_result.get('available_lags', 0)} lags available")
        log("  Feature breakdown:")
        num_features = len([k for k in features.keys() if k.startswith('in_')])
        for i in range(1, num_features + 1):
            key = f"in_{i}"
            log(f"    {key}: {features.get(key, 0.0)}")
        
        prediction = model_result['prediction']
        error = target - prediction
        log(f"[3/4] SUCCESS: Model prediction: {prediction:.4f}")
        log(f"  Actual: {target} | Prediction: {prediction:.4f} | Error: {error:.4f}")
        
        if 'default' in metrics:
            m = metrics['default']
            log(f"[4/4] SUCCESS: Updated metrics: MAE={m.get('mae', 0):.4f}, RMSE={m.get('rmse', 0):.4f}, Count={m.get('count', 0)}")
        
        log(f"=== E2E PIPELINE COMPLETE: {end_time} | Duration: {duration:.3f}s ===")
        
    except requests.exceptions.RequestException as e:
        log(f"ERROR: HTTP request failed: {e}")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()