# Online Learning API

A FastAPI-based online machine learning service using River for real-time model training and prediction.

## Features

- **Online Learning**: Train models incrementally with new data
- **Real-time Predictions**: Get predictions with automatic model updates
- **Metrics Tracking**: Monitor model performance over time
- **Health Monitoring**: Built-in health checks and service info
- **Docker Support**: Containerized deployment ready

## API Endpoints

- `GET /health` - Service health check
- `GET /info` - Model and service information
- `GET /metrics` - Performance metrics
- `POST /train` - Train model with new observations
- `POST /predict` - Get predictions for time series
- `POST /predict_learn` - Predict and learn from real values
- `POST /feedback` - Submit feedback for model improvement

## Quick Start

### Local Development

1. Install dependencies:
```bash
make install
```

2. Run the development server:
```bash
make dev
```

3. Run tests:
```bash
make test
```

### Docker

1. Build the image:
```bash
make build
```

2. Run locally:
```bash
make run
```

3. Push to registry:
```bash
make push
```

### Complete workflow:
```bash
make all  # Build, test, and push
```

## Project Structure

```
online_learning/
├── ml_api/
│   ├── __init__.py
│   ├── metrics_manager.py    # Performance metrics tracking
│   ├── model_manager.py      # Model lifecycle management
│   └── service.py           # FastAPI application
├── tests/
│   └── test_requests.py     # API integration tests
├── main.py                  # Application entry point
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── pytest.ini            # Test configuration
└── Makefile              # Build automation

```

## API Usage Examples

### Train the model:
```bash
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "store_123_sales",
    "observations": [
      {"timestamp": "2025-08-24", "value": 110},
      {"timestamp": "2025-08-25", "value": 120}
    ]
  }'
```

### Get predictions:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "store_123_sales",
    "horizon": 3
  }'
```

### Predict and learn:
```bash
curl -X POST "http://localhost:8000/predict_learn" \
  -H "Content-Type: application/json" \
  -d '{
    "series_id": "store_123_sales",
    "y_real": 135
  }'
```

## CI/CD

The project includes GitHub Actions workflow for:
- Automated testing with pytest
- Docker image building and pushing to Docker Hub
- Triggered on push to main branch

## Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `API_BASE_URL`: Base URL for tests (default: http://127.0.0.1:8000)

## Dependencies

- FastAPI 0.116.1 - Web framework
- Uvicorn 0.35.0 - ASGI server
- River 0.22.0 - Online machine learning
- Pydantic 2.11.7 - Data validation
- NumPy 2.3.2 - Numerical computing
- Pytest 8.3.4 - Testing framework

## License

MIT License