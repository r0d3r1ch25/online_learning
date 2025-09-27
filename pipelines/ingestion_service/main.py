from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from service import DataIngestionService
import aiohttp
import asyncio

app = FastAPI(title="Data Ingestion Service", version="1.0.0")
ingestion_service = DataIngestionService()

@app.get("/health")
async def health():
    """Health check endpoint"""
    return ingestion_service.get_health()

@app.get("/next")
async def get_next_observation() -> Dict[str, Any]:
    """
    Get the next observation from the dataset.
    Returns 200 with data if available, 204 if no more data.
    """
    observation = ingestion_service.get_next_observation()
    
    if observation is None:
        # No more data available - return 204 No Content
        raise HTTPException(status_code=204, detail="No more observations available")
    
    return observation

@app.post("/reset")
async def reset_stream():
    """Reset the stream to start from the beginning"""
    return ingestion_service.reset_stream()

@app.get("/status")
async def get_status():
    """Get current stream status"""
    return ingestion_service.get_status()

@app.get("/next/{crypto}")
async def get_crypto_price(crypto: str) -> Dict[str, Any]:
    """Get current crypto price from Coinbase API in standard format"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coinbase.com/v2/prices/{crypto.upper()}-USD/spot"
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    price = float(data["data"]["amount"])
                    return {
                        "observation_id": f"{crypto.upper()}_live",
                        "input": crypto.upper(),
                        "target": price,
                        "remaining": "live"
                    }
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail=f"Crypto {crypto.upper()} not found on Coinbase")
                else:
                    raise HTTPException(status_code=response.status, detail=f"Coinbase API error: {response.status}")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=503, detail=f"Network error fetching {crypto.upper()}: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch {crypto.upper()} price: {str(e)}")