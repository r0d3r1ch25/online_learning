# Feature Service

Time series feature extraction service that computes lag features for online machine learning.

## Features

- Computes lag features (up to 12 lags) for time series data
- Loads initial data from CSV files
- REST API for adding observations and retrieving features
- Designed for online/incremental learning workflows

## API Endpoints

- `GET /health` - Service health check
- `GET /info` - Service information and series status
- `POST /add_observation` - Add new observation to time series
- `POST /features` - Get lag features for a series
- `GET /features/{series_id}` - Get lag features (GET endpoint)

## Development

### Local Setup

```bash
pip install -r requirements.txt
python main.py
```

### Docker

```bash
docker build -t feature-service .
docker run -p 8001:8001 feature-service
```

### Testing

```bash
PYTHONPATH=. pytest tests/ -v
```

## Usage Example

```bash
# Add observation
curl -X POST "http://localhost:8001/add_observation" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "sales", "value": 150}'

# Get features
curl -X POST "http://localhost:8001/features" \
  -H "Content-Type: application/json" \
  -d '{"series_id": "sales", "num_lags": 5}'
```