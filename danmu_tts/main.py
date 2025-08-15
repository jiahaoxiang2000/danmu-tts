"""Main FastAPI application for Danmu TTS Server."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import config
from .manager import tts_manager




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