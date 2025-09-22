from fastapi import FastAPI, HTTPException
from .service import CoinbaseService

app = FastAPI()
coinbase_service = CoinbaseService()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/next")
async def get_next():
    try:
        return coinbase_service.get_current_rate()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))