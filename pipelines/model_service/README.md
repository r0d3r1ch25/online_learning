# Model Service

FastAPI-based online machine learning service using River for real-time model training and prediction.

## Development

### Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Run tests:
```bash
PYTHONPATH=. pytest tests/ -v
```

### Docker Build

```bash
docker build -t fti-model .
docker run -p 8000:8000 fti-model
```

## API Endpoints

- `GET /health` - Service health check
- `GET /info` - Model and service information
- `GET /metrics` - Performance metrics
- `POST /train` - Train model with new observations
- `POST /predict` - Get predictions for time series
- `POST /predict_learn` - Predict and learn from real values
- `POST /feedback` - Submit feedback for model improvement

## Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)