import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.config import settings
from src.tts_manager import TTSManager
from src.models import TTSRequest, TTSResponse, VoiceInfo
from src.websocket_manager import WebSocketManager
from src.utils import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global managers
tts_manager = None
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global tts_manager

    # Startup
    logger.info("Starting TTS Server...")
    tts_manager = TTSManager()
    await tts_manager.initialize()
    logger.info("TTS Server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down TTS Server...")
    if tts_manager:
        await tts_manager.cleanup()
    logger.info("TTS Server shut down")


# Create FastAPI app
app = FastAPI(
    title="Danmu TTS Server",
    description="High-performance TTS server for live streaming",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount web interface
app.mount("/web", StaticFiles(directory="web"), name="web")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Danmu TTS Server is running"}


@app.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """Generate TTS audio from text"""
    try:
        logger.info(f"TTS request: {request.text[:50]}...")

        # Generate audio
        audio_data, metadata = await tts_manager.generate_speech(
            text=request.text,
            voice=request.voice,
            backend=request.backend,
            quality=request.quality,
        )

        return TTSResponse(
            audio_data=audio_data,
            metadata=metadata,
            cached=metadata.get("cached", False),
        )

    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tts/stream")
async def stream_tts(text: str, voice: str = None, backend: str = None):
    """Stream TTS audio"""
    try:

        async def generate_audio_stream():
            async for chunk in tts_manager.stream_speech(text, voice, backend):
                yield chunk

        return StreamingResponse(
            generate_audio_stream(),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=tts_audio.wav"},
        )
    except Exception as e:
        logger.error(f"TTS streaming failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voices", response_model=list[VoiceInfo])
async def get_voices(backend: str = None):
    """Get available voices"""
    try:
        voices = await tts_manager.get_available_voices(backend)
        return voices
    except Exception as e:
        logger.error(f"Failed to get voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/backends")
async def get_backends():
    """Get available TTS backends"""
    return await tts_manager.get_backend_status()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time TTS"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Receive text from client
            data = await websocket.receive_json()

            if data.get("type") == "tts":
                # Generate TTS
                text = data.get("text", "")
                voice = data.get("voice")
                backend = data.get("backend")

                try:
                    # Stream audio chunks
                    async for chunk in tts_manager.stream_speech(text, voice, backend):
                        await websocket.send_bytes(chunk)

                    # Send completion signal
                    await websocket.send_json({"type": "complete"})

                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        websocket_manager.disconnect(websocket)


@app.get("/stats")
async def get_stats():
    """Get server statistics"""
    return await tts_manager.get_stats()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.debug,
        log_level="info",
    )
