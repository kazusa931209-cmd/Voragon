from __future__ import annotations

import base64
import binascii

from fastapi import APIRouter, HTTPException, Request

from app.asr.api_models import AsrInferenceRequest, AsrInferenceResponse
from app.asr.base import ASREngine, ASRInferenceError, ASRModelUnavailableError

router = APIRouter(prefix="/v1/inference", tags=["inference"])


@router.post("/asr", response_model=AsrInferenceResponse)
async def inference_asr(body: AsrInferenceRequest, request: Request) -> AsrInferenceResponse:
    """Run partial or final transcription for remote realtime-backend callers (P7-006)."""
    asr_engine: ASREngine = request.app.state.asr_engine
    try:
        audio = base64.b64decode(body.audio_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid audio_base64") from exc

    try:
        if body.kind == "partial":
            result = await asr_engine.transcribe_partial(audio, body.segment_id, body.language)
        else:
            result = await asr_engine.transcribe_final(audio, body.segment_id, body.language)
    except ASRModelUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ASRInferenceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return AsrInferenceResponse(
        text=result.text,
        language=result.language,
        confidence=result.confidence,
    )
