import os
import requests
from datetime import datetime

class CoinbaseService:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "https://api.coinbase.com/v2/exchange-rates")
        self.target_currency = os.getenv("TARGET_CURRENCY", "XRP")
    
    def get_current_rate(self):
        response = requests.get(self.api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        rate = float(data["data"]["rates"][self.target_currency])
        
        return {
            "series_id": self.target_currency,
            "target": rate,
            "datetime": datetime.now().isoformat()
        }