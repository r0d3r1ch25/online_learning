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
MODEL_URL = "http://model-service.ml-services.svc.cluster.local:8000"

def log(message):
    """Log with timestamp and flush immediately"""
    print(f"{datetime.datetime.now()}: {message}", flush=True)

def main():
    log("=== E2E PIPELINE START ===")
    
    try:
        # Step 1: Get observation from ingestion service
        log("[1/4] Fetching observation from ingestion service...")
        response = requests.get(f"{INGESTION_URL}/next", timeout=10)
        
        if response.status_code == 204:
            log("INFO: No more observations available - stream exhausted")
            sys.exit(0)
        
        response.raise_for_status()
        observation = response.json()
        
        actual_value = observation['target']
        obs_id = observation.get('observation_id', 'N/A')
        remaining = observation.get('remaining', 'N/A')
        log(f"SUCCESS: Observation {obs_id}: target={actual_value}, remaining={remaining}")
        
        # Step 2: Extract features
        log("[2/4] Extracting features from feature service...")
        feature_payload = {"series_id": "argo_e2e_pipeline", "value": actual_value}
        response = requests.post(f"{FEATURE_URL}/add", json=feature_payload, timeout=10)
        response.raise_for_status()
        feature_result = response.json()
        
        features = feature_result['features']
        available_lags = feature_result.get('available_lags', 0)
        log(f"SUCCESS: Features extracted: {len(features)} inputs, {available_lags} lags available")
        
        # Show all features for debugging
        log(f"  All features: {features}")
        log("  Feature breakdown:")
        num_features = len([k for k in features.keys() if k.startswith('in_')])
        for i in range(1, num_features + 1):
            key = f"in_{i}"
            value = features.get(key, 0.0)
            log(f"    {key}: {value}")
        
        # Step 3: Model prediction and learning
        log("[3/4] Sending to model service (predict_learn)...")
        model_payload = {
            "features": features,
            "target": feature_result['target']
        }
        log(f"  Model input: features={len(features)} keys, target={feature_result['target']}")
        
        response = requests.post(f"{MODEL_URL}/predict_learn", json=model_payload, timeout=10)
        response.raise_for_status()
        model_result = response.json()
        
        prediction = model_result['prediction']
        error = actual_value - prediction
        log(f"SUCCESS: Model prediction: {prediction:.4f}")
        log(f"  Actual: {actual_value} | Prediction: {prediction:.4f} | Error: {error:.4f}")
        
        # Step 4: Get updated metrics
        log("[4/4] Fetching updated model metrics...")
        response = requests.get(f"{MODEL_URL}/model_metrics", timeout=10)
        response.raise_for_status()
        metrics = response.json()
        
        if 'default' in metrics:
            m = metrics['default']
            log(f"SUCCESS: Updated metrics: MAE={m.get('mae', 0):.4f}, RMSE={m.get('rmse', 0):.4f}, Count={m.get('count', 0)}")
        
        log("=== E2E PIPELINE COMPLETE ===")
        
    except requests.exceptions.RequestException as e:
        log(f"ERROR: HTTP request failed: {e}")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()