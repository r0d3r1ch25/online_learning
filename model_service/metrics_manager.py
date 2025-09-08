# ml_api/metrics_manager.py

# Placeholder for metrics (ready for Prometheus integration)
class MetricsManager:
    def __init__(self):
        self.predictions = []

    def add(self, series_id, y_true, y_pred):
        self.predictions.append({'series_id': series_id, 'y_true': y_true, 'y_pred': y_pred})

    def get_metrics(self):
        """
        Returns example metrics.
        Later, integrate Prometheus counters or gauges here.
        """
        count = len(self.predictions)
        return {
            'predictions_count': count,
            'last_prediction': self.predictions[-1] if count > 0 else None
        }
