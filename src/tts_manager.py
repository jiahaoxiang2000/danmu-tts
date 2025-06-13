"""TTS Manager - Coordinates multiple TTS backends"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from pathlib import Path

from .config import settings
from .models import VoiceInfo, BackendStatus, ServerStats
from .utils import generate_cache_key, audio_to_base64, check_gpu_availability
from .backends.edge_tts import EdgeTTSBackend
from .backends.piper_tts import PiperTTSBackend
from .backends.xtts import XTTSBackend
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


class TTSManager:
    """Main TTS manager that coordinates multiple backends"""

    def __init__(self):
        self.backends: Dict[str, Any] = {}
        self.cache_manager = CacheManager()
        self.stats = {
            "start_time": time.time(),
            "total_requests": 0,
            "cache_hits": 0,
            "backend_usage": {},
        }
        self.request_queue = asyncio.Queue()
        self.active_tasks = set()

    async def initialize(self):
        """Initialize all enabled TTS backends"""
        logger.info("Initializing TTS Manager...")

        # Initialize cache
        await self.cache_manager.initialize()

        # Initialize backends based on configuration
        backend_configs = settings.tts.backends

        # Edge TTS (always available, fast)
        if backend_configs.get("edge", {}).get("enabled", True):
            try:
                self.backends["edge"] = EdgeTTSBackend()
                await self.backends["edge"].initialize()
                logger.info("Edge TTS backend initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Edge TTS: {e}")

        # Piper TTS (local, fast)
        if backend_configs.get("piper", {}).get("enabled", False):
            try:
                self.backends["piper"] = PiperTTSBackend()
                await self.backends["piper"].initialize()
                logger.info("Piper TTS backend initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Piper TTS: {e}")

        # XTTS (high quality, GPU accelerated)
        if backend_configs.get("xtts", {}).get("enabled", False):
            try:
                gpu_info = check_gpu_availability()
                if gpu_info["available"]:
                    self.backends["xtts"] = XTTSBackend()
                    await self.backends["xtts"].initialize()
                    logger.info("XTTS backend initialized with GPU support")
                else:
                    logger.warning("XTTS requires GPU but none available")
            except Exception as e:
                logger.error(f"Failed to initialize XTTS: {e}")

        logger.info(
            f"TTS Manager initialized with backends: {list(self.backends.keys())}"
        )

    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        backend: Optional[str] = None,
        quality: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate speech from text"""
        self.stats["total_requests"] += 1

        # Generate cache key
        cache_key = generate_cache_key(
            text, voice or "default", backend or "auto", quality=quality
        )

        # Check cache first
        if settings.performance.cache.enabled:
            cached_audio = await self.cache_manager.get(cache_key)
            if cached_audio:
                self.stats["cache_hits"] += 1
                return cached_audio, {"cached": True, "backend": "cache"}

        # Select backend
        selected_backend = await self._select_backend(backend, quality)
        if not selected_backend:
            raise Exception("No available TTS backend")

        # Generate audio
        audio_data = await selected_backend.generate_speech(text, voice)

        # Convert to base64
        audio_b64 = audio_to_base64(audio_data)

        # Cache the result
        if settings.performance.cache.enabled:
            await self.cache_manager.set(cache_key, audio_b64)

        # Update stats
        backend_name = selected_backend.__class__.__name__
        self.stats["backend_usage"][backend_name] = (
            self.stats["backend_usage"].get(backend_name, 0) + 1
        )

        metadata = {
            "backend": backend_name,
            "voice": voice,
            "sample_rate": settings.audio.sample_rate,
            "format": settings.audio.format,
        }

        return audio_b64, metadata

    async def stream_speech(
        self, text: str, voice: Optional[str] = None, backend: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream speech generation"""
        selected_backend = await self._select_backend(backend)
        if not selected_backend:
            raise Exception("No available TTS backend")

        async for chunk in selected_backend.stream_speech(text, voice):
            yield chunk

    async def get_available_voices(
        self, backend: Optional[str] = None
    ) -> List[VoiceInfo]:
        """Get available voices from all or specific backend"""
        voices = []

        if backend and backend in self.backends:
            voices.extend(await self.backends[backend].get_voices())
        else:
            for backend_instance in self.backends.values():
                voices.extend(await backend_instance.get_voices())

        return voices

    async def get_backend_status(self) -> List[BackendStatus]:
        """Get status of all backends"""
        status_list = []

        for name, backend in self.backends.items():
            try:
                is_available = await backend.is_available()
                load = getattr(backend, "current_load", 0.0)
                queue_size = getattr(backend, "queue_size", 0)

                status_list.append(
                    BackendStatus(
                        name=name,
                        enabled=True,
                        available=is_available,
                        load=load,
                        queue_size=queue_size,
                    )
                )
            except Exception as e:
                logger.error(f"Failed to get status for backend {name}: {e}")
                status_list.append(
                    BackendStatus(name=name, enabled=True, available=False)
                )

        return status_list

    async def get_stats(self) -> ServerStats:
        """Get server statistics"""
        uptime = time.time() - self.stats["start_time"]
        cache_hit_rate = (
            self.stats["cache_hits"] / max(self.stats["total_requests"], 1)
        ) * 100

        return ServerStats(
            uptime=uptime,
            total_requests=self.stats["total_requests"],
            cache_hit_rate=cache_hit_rate,
            active_connections=0,  # Will be updated by WebSocket manager
            backend_status=await self.get_backend_status(),
            gpu_usage=check_gpu_availability(),
        )

    async def _select_backend(
        self, preferred: Optional[str] = None, quality: Optional[str] = None
    ):
        """Select the best available backend"""
        # If specific backend requested
        if preferred and preferred in self.backends:
            backend = self.backends[preferred]
            if await backend.is_available():
                return backend

        # Auto-select based on quality and availability
        priority_order = []

        if quality == "high":
            priority_order = ["xtts", "edge", "piper"]
        elif quality == "low" or quality == "fast":
            priority_order = ["edge", "piper", "xtts"]
        else:  # medium
            priority_order = [
                settings.tts.primary_backend
            ] + settings.tts.fallback_backends

        # Find first available backend
        for backend_name in priority_order:
            if backend_name in self.backends:
                backend = self.backends[backend_name]
                if await backend.is_available():
                    return backend

        return None

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up TTS Manager...")

        # Cancel active tasks
        for task in self.active_tasks:
            task.cancel()

        # Cleanup backends
        for backend in self.backends.values():
            if hasattr(backend, "cleanup"):
                await backend.cleanup()

        # Cleanup cache
        await self.cache_manager.cleanup()

        logger.info("TTS Manager cleanup complete")
