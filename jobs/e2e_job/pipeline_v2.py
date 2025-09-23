#!/usr/bin/env python3
"""
End-to-end ML pipeline v2 for Argo Workflows.
Runs ingestion -> features -> 3 models in parallel with asyncio.
"""

import asyncio
import aiohttp
import json
import datetime
import sys
import os

# Service URLs
INGESTION_URL = "http://ingestion-service.ml-services.svc.cluster.local:8002"
FEATURE_URL = "http://feature-service.ml-services.svc.cluster.local:8001"

MODEL_SERVICES = [
    {"name": "Linear", "url": "http://model-service-linear.ml-services.svc.cluster.local:8010"},
    {"name": "Ridge", "url": "http://model-service-ridge.ml-services.svc.cluster.local:8011"},
    {"name": "Neural", "url": "http://model-service-neural.ml-services.svc.cluster.local:8012"}
]

def log(message):
    """Log with timestamp and flush immediately"""
    print(f"{datetime.datetime.now()}: {message}", flush=True)

async def call_model_service(session, model_info, features, target):
    """Call a single model service for predict_learn and get metrics"""
    model_start = datetime.datetime.now()
    try:
        # Predict and learn
        async with session.post(
            f"{model_info['url']}/predict_learn",
            json={"features": features, "target": target},
            timeout=10
        ) as response:
            response.raise_for_status()
            predict_result = await response.json()
        
        # Get metrics
        async with session.get(f"{model_info['url']}/model_metrics", timeout=10) as response:
            response.raise_for_status()
            metrics = await response.json()
        
        model_end = datetime.datetime.now()
        model_duration = (model_end - model_start).total_seconds()
        
        return {
            "model": model_info["name"],
            "prediction": predict_result["prediction"],
            "metrics": metrics.get("default", {}),
            "duration": model_duration
        }
    except Exception as e:
        model_end = datetime.datetime.now()
        model_duration = (model_end - model_start).total_seconds()
        return {
            "model": model_info["name"],
            "error": str(e),
            "duration": model_duration
        }

async def main():
    start_time = datetime.datetime.now()
    
    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Get observation from ingestion service
            async with session.get(f"{INGESTION_URL}/next", timeout=10) as response:
                if response.status == 204:
                    log("INFO: No more observations available - stream exhausted")
                    sys.exit(0)
                response.raise_for_status()
                observation = await response.json()
                target = observation['target']
            
            # Step 2: Extract features
            async with session.post(
                f"{FEATURE_URL}/add",
                json={"series_id": "argo_e2e_pipeline_v2", "value": target},
                timeout=10
            ) as response:
                response.raise_for_status()
                feature_result = await response.json()
            
            # Step 3: Call all 3 models in parallel
            tasks = [
                call_model_service(session, model_info, feature_result['features'], feature_result['target'])
                for model_info in MODEL_SERVICES
            ]
            model_results = await asyncio.gather(*tasks)
        
        # All HTTP calls complete - now log everything
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log("=== E2E PIPELINE V2 START ===")
        log(f"[1/4] SUCCESS: Ingestion - {observation}")
        
        features = feature_result['features']
        log(f"[2/4] SUCCESS: Features extracted: {len(features)} inputs, {feature_result.get('available_lags', 0)} lags available")
        log("  Feature breakdown:")
        num_features = len([k for k in features.keys() if k.startswith('in_')])
        for i in range(1, num_features + 1):
            key = f"in_{i}"
            log(f"    {key}: {features.get(key, 0.0)}")
        
        log("[3/4] SUCCESS: Model predictions (parallel execution):")
        log("┌─────────┬─────────────┬─────────┬─────────┬─────────┬─────────┬───────┬─────────┐")
        log("│ Model   │ Prediction  │   MAE   │  RMSE   │  MAPE   │  Count  │ Error │  Time   │")
        log("├─────────┼─────────────┼─────────┼─────────┼─────────┼─────────┼───────┼─────────┤")
        
        for result in model_results:
            if "error" in result:
                log(f"│ {result['model']:<7} │ ERROR       │    -    │    -    │    -    │    -    │   -   │ {result['duration']:>6.3f}s │")
            else:
                pred = result["prediction"]
                error = target - pred
                m = result["metrics"]
                log(f"│ {result['model']:<7} │ {pred:>10.4f}  │ {m.get('mae', 0):>6.2f}  │ {m.get('rmse', 0):>6.2f}  │ {m.get('mape', 0):>6.2f}  │ {m.get('count', 0):>6}  │ {error:>5.2f} │ {result['duration']:>6.3f}s │")
        
        log("└─────────┴─────────────┴─────────┴─────────┴─────────┴─────────┴───────┴─────────┘")
        log(f"[4/4] SUCCESS: All models trained in parallel")
        log(f"=== E2E PIPELINE V2 COMPLETE: {end_time} | Duration: {duration:.3f}s ===")
        
    except Exception as e:
        log(f"ERROR: Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())