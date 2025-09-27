from collections import defaultdict, deque
import math

ROLLING_WINDOW_SIZES = [5, 10, 20]

class MetricsManager:
    def __init__(self):
        self.series_history = defaultdict(lambda: {
            size: deque(maxlen=size) for size in ROLLING_WINDOW_SIZES
        })
        self.series_counts = defaultdict(int)

    def add(self, series_id, y_true, y_pred):
        y_true = float(y_true)
        y_pred = float(y_pred)
        
        # Store in rolling windows
        for size in ROLLING_WINDOW_SIZES:
            self.series_history[series_id][size].append((y_true, y_pred))
        
        # Increment total count
        self.series_counts[series_id] += 1

    def _compute_metrics(self, data):
        """Compute MAE, MSE, RMSE, MAPE from (y_true, y_pred) pairs"""
        if not data:
            return {"mae": 0.0, "mse": 0.0, "rmse": 0.0, "mape": 0.0}
        
        errors = [abs(y_true - y_pred) for y_true, y_pred in data]
        squared_errors = [(y_true - y_pred) ** 2 for y_true, y_pred in data]
        
        mae = sum(errors) / len(errors)
        mse = sum(squared_errors) / len(squared_errors)
        rmse = math.sqrt(mse)
        
        # MAPE (avoid division by zero)
        mape_errors = [abs(y_true - y_pred) / abs(y_true) for y_true, y_pred in data if y_true != 0]
        mape = (sum(mape_errors) / len(mape_errors) * 100) if mape_errors else 0.0
        
        return {
            "mae": round(mae, 4),
            "mse": round(mse, 4), 
            "rmse": round(rmse, 4),
            "mape": round(mape, 4)
        }
    
    def get_metrics(self):
        """Returns comprehensive model performance metrics"""
        if not self.series_history:
            return {"message": "No predictions available yet"}
        
        metrics = {}
        for series_id in self.series_history:
            series_metrics = {'count': self.series_counts[series_id]}
            
            # Compute rolling metrics for each window size
            for size in ROLLING_WINDOW_SIZES:
                window_data = list(self.series_history[series_id][size])
                if window_data:
                    window_metrics = self._compute_metrics(window_data)
                    for metric_name, value in window_metrics.items():
                        series_metrics[f"{metric_name}_{size}"] = value
            
            # Add last prediction details from largest window
            largest_window = self.series_history[series_id][max(ROLLING_WINDOW_SIZES)]
            if largest_window:
                last_actual, last_pred = largest_window[-1]
                series_metrics.update({
                    'last_prediction': last_pred,
                    'last_actual': last_actual,
                    'last_error': abs(last_actual - last_pred)
                })
            
            metrics[series_id] = series_metrics
        
        return metrics
