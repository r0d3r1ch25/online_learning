import os
from collections import defaultdict, deque
from river import metrics as river_metrics, utils

DEFAULT_WINDOW_SIZE = int(os.getenv("ROLLING_WINDOW_SIZE"))

class MetricsManager:
    def __init__(self, window_size=None):
        self.window_size = window_size or DEFAULT_WINDOW_SIZE
        self.series_metrics = defaultdict(lambda: {
            "mae": utils.Rolling(river_metrics.MAE(), window_size=self.window_size),
            "mse": utils.Rolling(river_metrics.MSE(), window_size=self.window_size),
            "rmse": utils.Rolling(river_metrics.RMSE(), window_size=self.window_size),
            "mape": utils.Rolling(river_metrics.MAPE(), window_size=self.window_size)
        })
        self.series_history = defaultdict(lambda: deque(maxlen=self.window_size))
        self.series_counts = defaultdict(int)

    def add(self, series_id, y_true, y_pred):
        y_true = float(y_true)
        y_pred = float(y_pred)
        abs_error = abs(y_true - y_pred)
        
        # Update rolling metrics
        for metric in self.series_metrics[series_id].values():
            metric.update(y_true, y_pred)
        
        # Store history for last_* values
        self.series_history[series_id].append((y_true, y_pred, abs_error))
        
        # Increment total count
        self.series_counts[series_id] += 1

    def get_metrics(self):
        """Returns comprehensive model performance metrics"""
        if not self.series_history:
            return {"message": "No predictions available yet"}
        
        metrics = {}
        for series_id in self.series_history:
            history = self.series_history[series_id]
            if not history:
                continue
            
            last_actual, last_pred, last_error = history[-1]
            
            metrics[series_id] = {
                'count': self.series_counts[series_id],
                'mae': round(self.series_metrics[series_id]["mae"].get() or 0.0, 4),
                'mse': round(self.series_metrics[series_id]["mse"].get() or 0.0, 4),
                'rmse': round(self.series_metrics[series_id]["rmse"].get() or 0.0, 4),
                'mape': round(self.series_metrics[series_id]["mape"].get() or 0.0, 4),
                'last_prediction': last_pred,
                'last_actual': last_actual,
                'last_error': last_error
            }
        
        return metrics
