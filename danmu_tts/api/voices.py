"""Voice management endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from ..models.responses import VoiceInfo
from ..main import tts_manager

router = APIRouter(prefix="/voices", tags=["voices"])


@router.get("/", response_model=List[VoiceInfo])
async def get_voices(backend: Optional[str] = Query(None, description="Filter by backend")):
    """Get all available voices, optionally filtered by backend."""
    try:
        all_voices = []
        
        # If backend specified, get voices from that backend only
        if backend:
            if backend not in tts_manager.backends:
                raise HTTPException(status_code=404, detail=f"Backend '{backend}' not found")
            
            tts_backend = tts_manager.backends[backend]
            if not tts_backend.available:
                raise HTTPException(status_code=503, detail=f"Backend '{backend}' is not available")
            
            voices = await tts_backend.get_voices()
            all_voices.extend(voices)
        else:
            # Get voices from all available backends
            for tts_backend in tts_manager.backends.values():
                if tts_backend.available:
                    voices = await tts_backend.get_voices()
                    all_voices.extend(voices)
        
        # Convert Voice objects to VoiceInfo response models
        voice_info_list = []
        for voice in all_voices:
            voice_info = VoiceInfo(
                id=voice.id,
                name=voice.name,
                language=voice.language,
                gender=voice.gender,
                backend=voice.backend,
                quality=voice.quality
            )
            voice_info_list.append(voice_info)
        
        return voice_info_list
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")