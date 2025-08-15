"""Edge TTS backend implementation."""

import asyncio
import io
import wave
from typing import List, Optional, AsyncGenerator

import edge_tts

from .base import TTSBackend, TTSResult, Voice, BackendStatus
from ..config import config


class EdgeTTSBackend(TTSBackend):
    """Edge TTS backend implementation using Microsoft Edge Text-to-Speech."""
    
    def __init__(self):
        super().__init__("edge")
        self._voices_cache: Optional[List[Voice]] = None
        self._voices_cache_timestamp = 0
        self._cache_ttl = 3600  # 1 hour cache for voices
    
    async def initialize(self) -> None:
        """Initialize the Edge TTS backend."""
        try:
            # Test basic functionality by fetching voices
            await self._fetch_voices()
            self._available = True
        except Exception as e:
            print(f"Failed to initialize Edge TTS backend: {e}")
            self._available = False
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        quality: Optional[str] = None,
        format: str = "wav",
        sample_rate: int = 22050,
        **kwargs
    ) -> TTSResult:
        """Synthesize text to speech using Edge TTS."""
        if not self._available:
            raise RuntimeError("Edge TTS backend is not available")
        
        # Use default voice if none specified
        if voice is None:
            voice = config.edge_tts.default_voice
        
        # Create Edge TTS communication object
        tts = edge_tts.Communicate(
            text,
            voice,
            rate=config.edge_tts.rate,
            volume=config.edge_tts.volume,
            pitch=config.edge_tts.pitch
        )
        
        # Generate audio data
        audio_data = b""
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if not audio_data:
            raise RuntimeError("No audio data generated")
        
        # Calculate duration (rough estimate based on typical speech rate)
        # This is an approximation - Edge TTS doesn't provide exact duration
        words = len(text.split())
        duration = words / 2.5  # Assume ~2.5 words per second
        
        return TTSResult(
            audio_data=audio_data,
            backend=self.name,
            voice=voice,
            duration=duration,
            sample_rate=sample_rate,
            format=format,
            cached=False
        )
    
    async def stream_synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        quality: Optional[str] = None,
        format: str = "wav",
        sample_rate: int = 22050,
        **kwargs
    ) -> AsyncGenerator[bytes, None]:
        """Stream synthesized audio from Edge TTS."""
        if not self._available:
            raise RuntimeError("Edge TTS backend is not available")
        
        # Use default voice if none specified
        if voice is None:
            voice = config.edge_tts.default_voice
        
        # Create Edge TTS communication object
        tts = edge_tts.Communicate(
            text,
            voice,
            rate=config.edge_tts.rate,
            volume=config.edge_tts.volume,
            pitch=config.edge_tts.pitch
        )
        
        # Stream audio chunks
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    
    async def _fetch_voices(self) -> List[Voice]:
        """Fetch available voices from Edge TTS."""
        import time
        
        current_time = time.time()
        
        # Return cached voices if still valid
        if (self._voices_cache is not None and 
            current_time - self._voices_cache_timestamp < self._cache_ttl):
            return self._voices_cache
        
        # Fetch voices from Edge TTS
        edge_voices = await edge_tts.list_voices()
        
        voices = []
        for voice_info in edge_voices:
            voice = Voice(
                id=voice_info["ShortName"],
                name=voice_info["FriendlyName"],
                language=voice_info["Locale"],
                gender=voice_info["Gender"].lower(),
                backend=self.name,
                quality="medium"  # Edge TTS provides consistent medium quality
            )
            voices.append(voice)
        
        # Cache the results
        self._voices_cache = voices
        self._voices_cache_timestamp = current_time
        
        return voices
    
    async def get_voices(self) -> List[Voice]:
        """Get available voices for Edge TTS."""
        return await self._fetch_voices()
    
    async def get_status(self) -> BackendStatus:
        """Get current Edge TTS backend status."""
        return BackendStatus(
            name=self.name,
            enabled=self.enabled and config.edge_tts.enabled,
            available=self.available,
            load=0.0,  # Edge TTS doesn't provide load information
            queue_size=0  # Edge TTS doesn't have a queue
        )