
import requests
import pandas as pd
import time
import logging
import os

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URLs for services running in Kubernetes
FEATURE_SERVICE_URL = "http://feature-service.default.svc.cluster.local:8001"
MODEL_SERVICE_URL = "http://model-service.default.svc.cluster.local:8000"
SERIES_ID = "air_passengers"
NUM_LAGS = 5

# Path to the data, assuming the script is run from the repo root
DATA_PATH = "pipelines/ingestion_service/data.csv"

# --- Helper Functions ---
def wait_for_service(url, service_name):
    """Polls a service's health check until it's available."""
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
    """Gets features from the feature service."""
    try:
        response = requests.post(
            f"{FEATURE_SERVICE_URL}/features",
            json={"series_id": series_id, "num_lags": num_lags}
        )
        response.raise_for_status()
        features = response.json().get("features", {})
        logging.info(f"Successfully retrieved {len(features)} features for {series_id}.")
        return features
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting features: {e}")
        return None

def predict_and_learn(series_id, y_real, features):
    """Calls the model service to get a prediction and then learn from the actual value."""
    try:
        # The model service doesn't currently accept features, but we pass them
        # in anticipation of a future update.
        payload = {
            "series_id": series_id,
            "y_real": y_real
        }
        response = requests.post(
            f"{MODEL_SERVICE_URL}/predict_learn",
            json=payload
        )
        response.raise_for_status()
        prediction = response.json().get("prediction")
        logging.info(f"Actual: {y_real}, Prediction: {prediction}")
        return prediction
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during predict_learn: {e}")
        return None

# --- Main Execution ---
def main():
    logging.info("--- Starting Online Learning Simulation Pipeline ---")

    # 1. Wait for services to be ready before starting the process
    if not wait_for_service(FEATURE_SERVICE_URL, "Feature Service"):
        return
    if not wait_for_service(MODEL_SERVICE_URL, "Model Service"):
        return

    # 2. Load the dataset
    if not os.path.exists(DATA_PATH):
        logging.error(f"Data file not found at '{DATA_PATH}'. Make sure the script is run from the repository root.")
        return
    
    data = pd.read_csv(DATA_PATH)
    logging.info(f"Loaded {len(data)} records from {DATA_PATH}")

    # 3. Iterate through the dataset to simulate online learning
    # The feature_service loads the entire dataset on startup.
    # We will iterate through the same data, get features for the *current* state of the world,
    # and then ask the model to predict and learn based on the actual value.
    for index, row in data.iterrows():
        y_value = float(row['target'])
        timestamp = row['input']
        logging.info(f"--- Processing Record {index+1}: Timestamp={timestamp} ---")

        # a. Get the latest features.
        # In this simulation, the feature service already has all historical data.
        features = get_features(SERIES_ID, NUM_LAGS)

        # b. Use the features and the actual value to get a prediction and update the model.
        if features is not None:
            predict_and_learn(SERIES_ID, y_value, features)

        # Add a small delay to make the log output readable
        time.sleep(1)

    logging.info("--- Online Learning Simulation Pipeline Finished ---")

if __name__ == "__main__":
    main()
