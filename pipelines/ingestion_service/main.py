from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from service import DataIngestionService

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