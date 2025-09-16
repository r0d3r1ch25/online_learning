import os
import signal
import uvicorn
from service import app

def signal_handler(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000")))