from collections import defaultdict, deque
from river import metrics as river_metrics, utils

ROLLING_WINDOW_SIZES = [5, 10, 20]

class MetricsManager:
    def __init__(self):
        self.series_metrics = defaultdict(lambda: {
            f"{metric}_{size}": utils.Rolling(getattr(river_metrics, metric.upper())(), window_size=size)
            for metric in ["mae", "mse", "rmse", "mape"]
            for size in ROLLING_WINDOW_SIZES
        })
        self.series_history = defaultdict(lambda: deque(maxlen=max(ROLLING_WINDOW_SIZES)))
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
            
            series_metrics = {'count': self.series_counts[series_id]}
            
            # Add rolling metrics for each window size
            for metric_name, metric_obj in self.series_metrics[series_id].items():
                series_metrics[metric_name] = round(metric_obj.get() or 0.0, 4)
            
            # Add last prediction details
            series_metrics.update({
                'last_prediction': last_pred,
                'last_actual': last_actual,
                'last_error': last_error
            })
            
            metrics[series_id] = series_metrics
        
        return metrics
