# Grafana Query Examples

Access Grafana at `http://localhost:3000` (admin/admin)

## Prometheus Queries (Metrics)

### Model Performance Metrics

**Mean Absolute Error:**
```
ml_model_mae
```

**Mean Squared Error:**
```
ml_model_mse
```

**Root Mean Squared Error:**
```
ml_model_rmse
```

**Total Predictions Count:**
```
ml_model_predictions_total
```

**Last Prediction Value:**
```
ml_model_last_prediction
```

**Last Prediction Error:**
```
ml_model_last_error
```

### Time Series Queries

**MAE over time:**
```
ml_model_mae[5m]
```

**Rate of predictions per minute:**
```
rate(ml_model_predictions_total[1m]) * 60
```

**Average RMSE over 10 minutes:**
```
avg_over_time(ml_model_rmse[10m])
```

## Loki Queries (Logs)

### Basic Log Queries

**All model service logs:**
```
{app="model-service"}
```

**All logs from ml-services namespace:**
```
{namespace="ml-services"}
```

**Warning logs only:**
```
{app="model-service"} |= "WARNING"
```

**Unknown feature warnings:**
```
{app="model-service"} |= "Unknown input feature"
```

### Advanced Log Queries

**Logs from last 5 minutes:**
```
{app="model-service"} [5m]
```

**Error logs with line filtering:**
```
{app="model-service"} |= "ERROR" | json
```

**Count of warning logs:**
```
count_over_time({app="model-service"} |= "WARNING" [1h])
```

## How to Use in Grafana

### 1. Access Explore
- Go to `http://localhost:3000`
- Login: admin/admin
- Click "Explore" in left sidebar

### 2. Select Data Source
- **For Metrics**: Select "Prometheus" 
- **For Logs**: Select "Loki"

### 3. Enter Queries
- Copy any query from above
- Paste in query field
- Click "Run Query" or press Shift+Enter

### 4. Create Dashboards
- Click "+" → "Dashboard"
- Add panels with these queries
- Save dashboard for monitoring

## Common Issues

**No Loki Labels:**
- Check if Promtail is running: `kubectl get pods -n monitoring`
- Verify Loki service: `kubectl get svc -n monitoring`

**No Prometheus Metrics:**
- Check Prometheus targets: `http://localhost:9090/targets`
- Verify model service is generating metrics: `curl http://localhost:8000/metrics/prometheus`

**Empty Results:**
- Generate some data first: `python3 infra/test_model_api.py`
- Wait a few minutes for metrics to appear