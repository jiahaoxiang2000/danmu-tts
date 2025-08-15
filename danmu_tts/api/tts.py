"""TTS endpoints for text-to-speech synthesis."""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from ..models.requests import TTSRequest, StreamTTSRequest
from ..models.responses import TTSResponse, AudioMetadata
from ..manager import tts_manager

router = APIRouter(prefix="/tts", tags=["tts"])


@router.post("/", response_model=TTSResponse)
async def synthesize_text(request: TTSRequest):
    """Convert text to speech and return base64 encoded audio."""
    try:
        # Get the appropriate backend
        if request.backend:
            backend = tts_manager.get_backend(request.backend)
        else:
            backend = tts_manager.get_default_backend()
        
        # Increment request counter
        tts_manager.total_requests += 1
        
        # Synthesize the text
        result = await backend.synthesize(
            text=request.text,
            voice=request.voice,
            quality=request.quality,
            format=request.format,
            sample_rate=request.sample_rate
        )
        
        # Convert TTSResult to API response format
        return TTSResponse(**result.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream")
async def stream_synthesize(
    text: str = Query(..., description="Text to convert to speech", min_length=1, max_length=1000),
    voice: Optional[str] = Query(None, description="Voice ID to use"),
    backend: Optional[str] = Query("edge", description="TTS backend to use")
):
    """Stream synthesized audio in real-time."""
    try:
        # Get the appropriate backend
        if backend:
            tts_backend = tts_manager.get_backend(backend)
        else:
            tts_backend = tts_manager.get_default_backend()
        
        # Increment request counter
        tts_manager.total_requests += 1
        
        # Create an async generator that yields audio chunks
        async def audio_generator():
            async for chunk in tts_backend.stream_synthesize(
                text=text,
                voice=voice,
                format="wav"
            ):
                yield chunk
        
        # Return streaming response
        return StreamingResponse(
            audio_generator(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=tts_audio.wav"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))