
import requests
import logging
import os
import json
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_SERVICE_URL = "http://fti-predict-learn-service.fti.svc.cluster.local:8000"
SERIES_ID = "air_passengers"

INPUT_FEATURES_PATH = "/tmp/features.json"

def predict_and_learn(series_id, y_real, features, timestamp):
    try:
        payload = {
            "series_id": series_id,
            "y_real": y_real,
            "features": features
        }
        response = requests.post(f"{MODEL_SERVICE_URL}/predict_learn", json=payload)
        response.raise_for_status()
        prediction = response.json().get("prediction")
        logging.info(f"Timestamp: {timestamp}, Actual: {y_real}, Prediction: {prediction}")
        return prediction
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during predict_learn for {timestamp}: {e}")
        return None

def main():
    logging.info("--- V2: Starting Batch Predict and Learn Step ---")

    if not os.path.exists(INPUT_FEATURES_PATH):
        logging.error(f"Input features file not found at {INPUT_FEATURES_PATH}")
        sys.exit(1)

    with open(INPUT_FEATURES_PATH, 'r') as f:
        feature_records = json.load(f)
    
    logging.info(f"Loaded {len(feature_records)} feature records.")

    for record in feature_records:
        predict_and_learn(SERIES_ID, record['y_real'], record['features'], record['timestamp'])

    logging.info("--- V2: Batch Predict and Learn Step Finished ---")

if __name__ == "__main__":
    main()
