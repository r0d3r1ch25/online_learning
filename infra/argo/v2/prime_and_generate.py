
import requests
import pandas as pd
import time
import logging
import os
import json
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FEATURE_SERVICE_URL = "http://fti-features-service.fti.svc.cluster.local:8001"
SERIES_ID = "air_passengers"
NUM_LAGS = 5

INPUT_DATA_PATH = "/tmp/data.csv"
OUTPUT_FEATURES_PATH = "/tmp/features.json"

def add_observation(series_id, value):
    try:
        requests.post(f"{FEATURE_SERVICE_URL}/add_observation", json={"series_id": series_id, "value": value}).raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error adding observation: {e}")
        return False

def get_features(series_id, num_lags):
    try:
        response = requests.post(f"{FEATURE_SERVICE_URL}/features", json={"series_id": series_id, "num_lags": num_lags})
        if response.status_code == 404:
            return None # Not enough history yet, this is expected
        response.raise_for_status()
        return response.json().get("features", {})
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting features: {e}")
        return None

def main():
    logging.info("--- V2: Starting Prime and Generate Features Step ---")
    
    if not os.path.exists(INPUT_DATA_PATH):
        logging.error(f"Input data file not found at {INPUT_DATA_PATH}")
        sys.exit(1)

    data = pd.read_csv(INPUT_DATA_PATH)
    logging.info(f"Loaded {len(data)} records.")

    all_feature_records = []
    for index, row in data.iterrows():
        y_value = float(row['target'])
        timestamp = row['input']
        logging.info(f"Processing {timestamp}...")

        # First, add the observation to build history
        if not add_observation(SERIES_ID, y_value):
            sys.exit(1)

        # Then, get the features for the current state
        features = get_features(SERIES_ID, NUM_LAGS)
        
        if features:
            record = {
                "features": features,
                "y_real": y_value,
                "timestamp": timestamp
            }
            all_feature_records.append(record)
        else:
            logging.warning("Not enough history to generate features. Skipping record.")

    logging.info(f"Successfully generated feature sets for {len(all_feature_records)} records.")
    with open(OUTPUT_FEATURES_PATH, 'w') as f:
        json.dump(all_feature_records, f)
    
    logging.info(f"Saved features to {OUTPUT_FEATURES_PATH}")
    logging.info("--- V2: Prime and Generate Features Step Finished ---")

if __name__ == "__main__":
    main()
