# Model Service

Online ML model service with pluggable architecture supporting multiple ML libraries.

## Architecture

### Plugin-Based Design
- `BaseModel`: Abstract interface for all ML models
- `models/river_models.py`: River ML implementations
- `ModelManager`: Loads models from all available plugins
- Future: Easy to add sklearn, vowpal wabbit, etc.

### Current Models (River ML)
- `linear_regression`: StandardScaler + LinearRegression
- `knn_regressor`: StandardScaler + KNNRegressor (k=5)
- `amf_regressor`: StandardScaler + AMFRegressor
- `bagging_regressor`: StandardScaler + BaggingRegressor (3 ridge models)

## API Endpoints

### Active Endpoints
| Method | Endpoint | Description | Used By |
|--------|----------|-------------|---------|
| GET | `/health` | Health check | Kubernetes probes |

| POST | `/predict_learn` | Predict then train | E2E pipeline |
| POST | `/predict_many` | 5-step recursive forecast | Testing/validation |
| GET | `/model_metrics` | Detailed performance metrics | E2E pipeline |
| GET | `/metrics` | Prometheus format | Monitoring |

### Request/Response Examples

**Predict & Learn:**
```bash
curl -X POST http://localhost:8010/predict_learn \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 1.5, "in_2": 2.0}, "target": 2.1}'
# Response: {"prediction": 2.05}
```

**Multi-step Prediction:**
```bash
curl -X POST http://localhost:8010/predict_many \
  -H "Content-Type: application/json" \
  -d '{"features": {"in_1": 1.5, "in_2": 2.0, "in_3": 1.8}}'
# Response: {"forecast": [{"step": 1, "value": 2.1}, {"step": 2, "value": 2.0}, ...]}
```

## Configuration

Set model via environment variable:
```bash
MODEL_NAME=linear_regression  # Default
MODEL_NAME=knn_regressor
MODEL_NAME=amf_regressor
MODEL_NAME=bagging_regressor
```

## Testing

```bash
python3 -m pytest tests/ -v
```

All tests pass (10/10) covering:
- Health endpoint
- Predict_learn functionality
- Edge cases and validation
- Metrics endpoints
- Prometheus format

## Adding New ML Libraries

1. Create `models/new_library_models.py`
2. Implement `BaseModel` interface:
   ```python
   class NewLibraryWrapper(BaseModel):
       def learn_one(self, features, target): pass
       def predict_one(self, features): pass
       def predict_learn(self, features, target): pass
       def predict_many(self, features, steps=5): pass
   ```
3. Add to `model_manager.py`:
   ```python
   from models.new_library_models import get_new_library_models
   models.update(get_new_library_models())
   ```

## Dependencies

- `river`: Online ML library
- `fastapi`: Web framework
- `pydantic`: Data validation
- `pytest`: Testing

## Docker

Uses shared image `r0d3r1ch25/ml-model:latest` with different `MODEL_NAME` env vars per deployment.