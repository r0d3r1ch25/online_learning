# ml_api/metrics_manager.py

import math
from collections import defaultdict

class MetricsManager:
    def __init__(self):
        self.predictions = defaultdict(list)

    def add(self, series_id, y_true, y_pred):
        self.predictions[series_id].append({
            'y_true': float(y_true), 
            'y_pred': float(y_pred),
            'error': abs(float(y_true) - float(y_pred))
        })

    def get_metrics(self):
        """Returns comprehensive model performance metrics"""
        if not self.predictions:
            return {"message": "No predictions available yet"}
        
        metrics = {}
        for series_id, preds in self.predictions.items():
            if not preds:
                continue
                
            errors = [p['error'] for p in preds]
            squared_errors = [(p['y_true'] - p['y_pred'])**2 for p in preds]
            
            mae = sum(errors) / len(errors)
            mse = sum(squared_errors) / len(squared_errors)
            rmse = math.sqrt(mse)
            
            metrics[series_id] = {
                'count': len(preds),
                'mae': round(mae, 4),
                'mse': round(mse, 4), 
                'rmse': round(rmse, 4),
                'last_prediction': preds[-1]['y_pred'],
                'last_actual': preds[-1]['y_true'],
                'last_error': preds[-1]['error']
            }
        
        return metrics
