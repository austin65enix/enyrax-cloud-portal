from fastapi import FastAPI
from datetime import datetime, timezone
import socket

app = FastAPI(
    title="ENYRAX Cloud API",
    version="0.1.0",
)

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "enyrax-api",
        "host": socket.gethostname(),
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "modules": {
            "portal": "online",
            "soc": "static-demo",
            "serviceops": "static-demo",
            "projectops": "static-demo",
        }
    }
