
import requests
import logging
import os
import json
import sys

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_SERVICE_URL = "http://fti-predict-learn-service.fti.svc.cluster.local:8000"
SERIES_ID = "air_passengers"

# Input path is provided by Argo
input_features_path = "/tmp/features.json"

# --- Helper Functions ---
def predict_and_learn(series_id, y_real, features):
    try:
        payload = {
            "series_id": series_id,
            "y_real": y_real,
            "features": features
        }
        response = requests.post(
            f"{MODEL_SERVICE_URL}/predict_learn",
            json=payload
        )
        response.raise_for_status()
        prediction = response.json().get("prediction")
        logging.info(f"Timestamp: {features.get('timestamp')}, Actual: {y_real}, Prediction: {prediction}")
        return prediction
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during predict_learn: {e}")
        return None

# --- Main Execution ---
def main():
    logging.info("--- Starting Predict and Learn Step ---")

    if not os.path.exists(input_features_path):
        logging.error(f"Input features file not found at {input_features_path}")
        sys.exit(1)

    with open(input_features_path, 'r') as f:
        feature_records = json.load(f)
    
    logging.info(f"Loaded {len(feature_records)} records from {input_features_path}")

    for record in feature_records:
        predict_and_learn(SERIES_ID, record['y_real'], record['features'])

    logging.info("--- Predict and Learn Step Finished ---")

if __name__ == "__main__":
    main()
