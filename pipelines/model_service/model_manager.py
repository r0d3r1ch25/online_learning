# model_manager.py

from river import linear_model, preprocessing
import collections

class ModelManager:
    def __init__(self):
        self.model = preprocessing.StandardScaler() | linear_model.LinearRegression()
        self.series_data = collections.defaultdict(list)  # Store history per series
        self.step = 0

    def _create_features(self, series_id, value=None):
        """Create feature vector with lags and current value"""
        history = self.series_data[series_id]
        features = {'step': self.step}
        
        # Add lag features
        for i in range(1, min(4, len(history) + 1)):  # Up to 3 lags
            if i <= len(history):
                features[f'lag_{i}'] = history[-i]
            else:
                features[f'lag_{i}'] = 0.0
        
        # Add current value if provided (for training)
        if value is not None:
            features['current'] = value
            
        return features

    def train(self, series_id, value):
        # Create features before adding to history
        x = self._create_features(series_id, value)
        y = value
        
        # Train model
        self.model.learn_one(x, y)
        
        # Update history
        self.series_data[series_id].append(value)
        if len(self.series_data[series_id]) > 10:  # Keep last 10 values
            self.series_data[series_id].pop(0)
        
        self.step += 1

    def predict(self, series_id):
        x = self._create_features(series_id)
        return self.model.predict_one(x)

    def predict_learn(self, series_id, y_real):
        # Predict first
        x = self._create_features(series_id)
        pred = self.model.predict_one(x)
        
        # Then learn with real value
        x_learn = self._create_features(series_id, y_real)
        self.model.learn_one(x_learn, y_real)
        
        # Update history
        self.series_data[series_id].append(y_real)
        if len(self.series_data[series_id]) > 10:
            self.series_data[series_id].pop(0)
        
        self.step += 1
        return pred