"""Main FastAPI application for Danmu TTS Server."""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import config
from .backends.edge_tts import EdgeTTSBackend
from .backends.base import TTSBackend


class TTSManager:
    """Manager for TTS backends."""
    
    def __init__(self):
        self.backends: Dict[str, TTSBackend] = {}
        self.start_time = time.time()
        self.total_requests = 0
    
    async def initialize(self):
        """Initialize all TTS backends."""
        # Initialize Edge TTS backend
        if config.edge_tts.enabled:
            edge_backend = EdgeTTSBackend()
            await edge_backend.initialize()
            self.backends["edge"] = edge_backend
    
    async def cleanup(self):
        """Clean up all backends."""
        for backend in self.backends.values():
            await backend.cleanup()
    
    def get_backend(self, name: str) -> TTSBackend:
        """Get a backend by name."""
        if name not in self.backends:
            raise HTTPException(status_code=404, detail=f"Backend '{name}' not found")
        backend = self.backends[name]
        if not backend.available:
            raise HTTPException(status_code=503, detail=f"Backend '{name}' is not available")
        return backend
    
    def get_default_backend(self) -> TTSBackend:
        """Get the default backend (first available)."""
        for backend in self.backends.values():
            if backend.available:
                return backend
        raise HTTPException(status_code=503, detail="No backends available")
    
    @property
    def uptime(self) -> float:
        """Get server uptime in seconds."""
        return time.time() - self.start_time


# Global TTS manager
tts_manager = TTSManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    print("Initializing Danmu TTS Server...")
    await tts_manager.initialize()
    print("Server initialized successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down Danmu TTS Server...")
    await tts_manager.cleanup()
    print("Server shutdown complete.")


# Create FastAPI application
app = FastAPI(
    title="Danmu TTS Server",
    description="High-performance Text-to-Speech server for live streaming",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "message": "Danmu TTS Server is running"
    }


@app.get("/health")
async def health():
    """Health check endpoint (alias for /)."""
    return await health_check()


# Include API routers
from .api.tts import router as tts_router
from .api.voices import router as voices_router
from .api.backends import router as backends_router

app.include_router(tts_router)
app.include_router(voices_router)
app.include_router(backends_router)


def main():
    """Main entry point for the application."""
    uvicorn.run(
        "danmu_tts.main:app",
        host=config.server.host,
        port=config.server.port,
        log_level=config.server.log_level,
        reload=True  # Set to False in production
    )


if __name__ == "__main__":
    main()