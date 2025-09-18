# Data Ingestion Service

A simple streaming service that serves CSV data one observation at a time via REST API.

## Features

- **Sequential Data Streaming**: Returns observations one by one from CSV data
- **Stream Management**: Reset stream to beginning, check status
- **Proper HTTP Status Codes**: 200 for data, 204 when stream is exhausted
- **Health Monitoring**: Health check endpoint for container orchestration

## API Endpoints

### `GET /next`
Returns the next observation from the dataset.
- **200**: Returns observation data with `input`, `target`, `observation_id`, and `remaining` count
- **204**: No more data available (stream exhausted)

### `POST /reset`
Resets the stream to start from the beginning.
- **200**: Stream reset successfully

### `GET /status`
Returns current stream status.
- **200**: Current index, total observations, remaining count, completion status

### `GET /health`
Health check endpoint.
- **200**: Service is healthy with total observation count

## Usage Example

```python
import requests

# Get next observation
response = requests.get("http://localhost:8002/next")
if response.status_code == 200:
    data = response.json()
    print(f"Observation {data['observation_id']}: {data['input']} -> {data['target']}")
elif response.status_code == 204:
    print("No more data available")

# Reset stream
requests.post("http://localhost:8002/reset")
```

## Development

### Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002
```

### Run tests
```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Build Docker image
```bash
docker build -t fti-ingestion .
docker run -p 8002:8002 fti-ingestion
```