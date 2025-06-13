"""Base TTS backend interface"""

from abc import ABC, abstractmethod
from typing import List, Optional, AsyncGenerator
from ..models import VoiceInfo


class BaseTTSBackend(ABC):
    """Base class for all TTS backends"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.current_load = 0.0
        self.queue_size = 0

    @abstractmethod
    async def initialize(self):
        """Initialize the backend"""
        pass

    @abstractmethod
    async def generate_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Generate speech audio from text"""
        pass

    @abstractmethod
    async def get_voices(self) -> List[VoiceInfo]:
        """Get available voices"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if backend is available"""
        pass

    async def stream_speech(
        self, text: str, voice: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream speech generation (default implementation)"""
        audio_data = await self.generate_speech(text, voice)
        # Simple chunking for streaming
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i : i + chunk_size]

    async def cleanup(self):
        """Clean up resources"""
        pass
