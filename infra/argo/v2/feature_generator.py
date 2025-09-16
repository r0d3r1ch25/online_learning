
import requests
import pandas as pd
import time
import logging
import os
import json

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FEATURE_SERVICE_URL = "http://fti-features-service.fti.svc.cluster.local:8001"
SERIES_ID = "air_passengers"
NUM_LAGS = 5

# Input and output paths are provided by Argo
input_data_path = "/tmp/data.csv"
output_features_path = "/tmp/features.json"

# --- Helper Functions ---
def wait_for_service(url, service_name):
    max_retries = 12
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                logging.info(f"Service '{service_name}' is available.")
                return True
        except requests.exceptions.ConnectionError:
            logging.info(f"Waiting for service '{service_name}'... ({i+1}/{max_retries})")
            time.sleep(10)
    logging.error(f"Service '{service_name}' did not become available.")
    return False

def get_features(series_id, num_lags):
    try:
        response = requests.post(
            f"{FEATURE_SERVICE_URL}/features",
            json={"series_id": series_id, "num_lags": num_lags}
        )
        response.raise_for_status()
        return response.json().get("features", {})
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting features: {e}")
        return None

# --- Main Execution ---
def main():
    logging.info("--- Starting Feature Generation Step ---")

    if not wait_for_service(FEATURE_SERVICE_URL, "Feature Service"):
        sys.exit(1)

    if not os.path.exists(input_data_path):
        logging.error(f"Input data file not found at {input_data_path}")
        sys.exit(1)

    data = pd.read_csv(input_data_path)
    logging.info(f"Loaded {len(data)} records from {input_data_path}")

    all_features = []
    for index, row in data.iterrows():
        y_value = float(row['target'])
        timestamp = row['input']
        logging.info(f"Processing record {index+1}: Timestamp={timestamp}")

        features = get_features(SERIES_ID, NUM_LAGS)
        if features is not None:
            # Add the original target value to the feature set for the next step
            record = {
                "features": features,
                "y_real": y_value,
                "timestamp": timestamp
            }
            all_features.append(record)

    logging.info(f"Generated features for {len(all_features)} records.")
    with open(output_features_path, 'w') as f:
        json.dump(all_features, f)
    
    logging.info(f"Successfully saved features to {output_features_path}")
    logging.info("--- Feature Generation Step Finished ---")

if __name__ == "__main__":
    main()
