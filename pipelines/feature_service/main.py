import uvicorn
import os

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    
    uvicorn.run(
        "service:app",
        host=host,
        port=port,
        reload=True
    )