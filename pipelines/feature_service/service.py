from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import logging
from feature_manager import LagFeatureManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Feature Service", version="1.0.0")

# Global feature manager
feature_manager = LagFeatureManager(max_lags=12)

class ExtractRequest(BaseModel):
    series_id: str = "default"
    value: float

class ExtractResponse(BaseModel):
    series_id: str
    features: Dict[str, float]
    available_lags: int

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "feature_service"}

@app.get("/info")
async def get_info():
    """Get service and series information."""
    return {
        "service": "feature_service",
        "max_lags": feature_manager.max_lags,
        "output_format": "model_ready_in_1_to_in_12",
        "series_info": feature_manager.get_series_info()
    }

@app.post("/add", response_model=ExtractResponse)
async def add_observation(request: ExtractRequest):
    """Add observation and extract lag features, return model-ready format."""
    try:
        # Extract features in model-ready format (in_1 to in_12)
        features = feature_manager.extract_features(request.series_id, request.value)
        
        # Get available lags count
        buffer = feature_manager.series_buffers.get(request.series_id)
        available_lags = len(buffer) if buffer else 0
        
        return ExtractResponse(
            series_id=request.series_id,
            features=features,
            available_lags=min(available_lags, feature_manager.max_lags)
        )
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/series/{series_id}")
async def get_series_info(series_id: str):
    """Get information about a specific series."""
    series_info = feature_manager.get_series_info()
    
    if series_id not in series_info:
        raise HTTPException(
            status_code=404, 
            detail=f"Series {series_id} not found"
        )
    
    return {
        "series_id": series_id,
        **series_info[series_id]
    }