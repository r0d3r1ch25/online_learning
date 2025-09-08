# ml_api/model_manager.py

from river import linear_model, preprocessing

# -------------------------
# MODEL HOLDER (Ready for DI)
# -------------------------
class ModelManager:
    """
    Handles the online model.
    Ready for dependency injection or replacement later.
    You can swap River models or integrate with other frameworks.
    """
    def __init__(self):
        # Simple example: online linear regression with standardization
        self.model = preprocessing.StandardScaler() | linear_model.LinearRegression()
        self.history = []  # Stores predictions and real values for metrics
        self.series_last_value = {}  # Track last value per series_id

    def predict(self, series_id, x=None):
        """
        Predicts next value. In online learning, you might update after real observed value.
        x: optional features (exogenous)
        """
        # Here, a simple prediction using last known value
        last = self.series_last_value.get(series_id, 0)
        return last  # Simplified for demo

    def train(self, series_id, y):
        """
        Update the model with new observation (online learning)
        """
        # For simplicity, x=1 for River model
        self.model.learn_one({'x':1}, y)
        self.series_last_value[series_id] = y
        self.history.append({'series_id': series_id, 'y': y})

    def predict_learn(self, series_id, y_real):
        """
        Predicts first, then updates the model with y_real
        Returns the prediction made before seeing y_real
        """
        pred = self.predict(series_id)
        self.train(series_id, y_real)
        return pred
