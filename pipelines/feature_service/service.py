from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import os
from feature_manager import LagFeatureManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Feature Service", version="1.0.0")

# Global feature manager
feature_manager = LagFeatureManager(max_lags=12)

class ObservationRequest(BaseModel):
    series_id: str
    value: float

class FeaturesRequest(BaseModel):
    series_id: str
    num_lags: Optional[int] = None

class FeaturesResponse(BaseModel):
    series_id: str
    features: Dict[str, float]
    available_lags: int

@app.on_event("startup")
async def startup_event():
    """Load initial data on startup."""
    csv_path = "../ingestion_service/data.csv"
    if os.path.exists(csv_path):
        try:
            feature_manager.load_from_csv(csv_path, "air_passengers")
            logger.info("Loaded initial data from CSV")
        except Exception as e:
            logger.warning(f"Could not load initial data: {e}")

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
        "series_info": feature_manager.get_series_info()
    }

@app.post("/add_observation")
async def add_observation(request: ObservationRequest):
    """Add new observation to a time series."""
    try:
        feature_manager.add_observation(request.series_id, request.value)
        return {
            "status": "success",
            "series_id": request.series_id,
            "value": request.value,
            "message": "Observation added successfully"
        }
    except Exception as e:
        logger.error(f"Error adding observation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/features", response_model=FeaturesResponse)
async def get_features(request: FeaturesRequest):
    """Get lag features for a time series."""
    try:
        features = feature_manager.get_lag_features(request.series_id, request.num_lags)
        
        if not features:
            raise HTTPException(
                status_code=404, 
                detail=f"No features available for series {request.series_id}"
            )
        
        return FeaturesResponse(
            series_id=request.series_id,
            features=features,
            available_lags=len(features)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/features/{series_id}")
async def get_features_by_id(series_id: str, num_lags: Optional[int] = None):
    """Get lag features for a specific series (GET endpoint)."""
    request = FeaturesRequest(series_id=series_id, num_lags=num_lags)
    return await get_features(request)