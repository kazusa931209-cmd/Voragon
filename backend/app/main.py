"""
Voragon realtime backend.

Run locally:
    cd backend
    pip install -e ".[dev]"
    python -m app.main
"""

import logging

import uvicorn
from fastapi import FastAPI

from app.config import get_settings
from app.websocket.handler import router as websocket_router

settings = get_settings()

logging.basicConfig(level=settings.log_level.upper())

app = FastAPI(title="Voragon Realtime Backend", version="0.1.0")
app.include_router(websocket_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check for load balancers and local development."""
    return {"status": "healthy", "service": "voragon-realtime-backend"}


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
