"""TTS Manager for handling TTS backends."""

import time
from typing import Dict

from fastapi import HTTPException

from .backends.base import TTSBackend
from .backends.edge_tts import EdgeTTSBackend
from .config import config


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


# Global TTS manager instance
tts_manager = TTSManager()