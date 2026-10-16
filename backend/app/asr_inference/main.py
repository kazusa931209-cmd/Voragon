"""
Voragon ASR inference service (P7-003+).

Run locally:
    cd backend && ASR_BACKEND=mock pip install -e ".[dev]" && python -m app.asr_inference.main
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request

from app.asr.base import ASREngine, create_asr_engine
from app.config import get_settings
from app.observability.logging_config import configure_logging

SERVICE_NAME = "voragon-asr-inference"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_settings = get_settings()
    configure_logging(app_settings)
    logger = logging.getLogger(__name__)
    asr_engine = create_asr_engine(app_settings)
    logger.info(
        "Warming up ASR backend=%s model=%s device=%s",
        app_settings.asr_backend,
        app_settings.asr_model,
        app_settings.asr_device,
    )
    await asr_engine.warmup()
    app.state.asr_engine = asr_engine
    yield


app = FastAPI(title="Voragon ASR Inference", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health(request: Request) -> dict[str, object]:
    """Health for Kubernetes probes and operator smoke tests."""
    asr_engine: ASREngine = request.app.state.asr_engine
    asr_health = await asr_engine.health()
    return {
        "status": "healthy" if asr_health.ready else "degraded",
        "service": SERVICE_NAME,
        "asr": {
            "ready": asr_health.ready,
            "backend": asr_health.backend,
            "model": asr_health.model,
            "device": get_settings().asr_device,
        },
    }


def main() -> None:
    settings = get_settings()
    configure_logging(settings)
    uvicorn.run(
        "app.asr_inference.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
