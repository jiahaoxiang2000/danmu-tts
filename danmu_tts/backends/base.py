"""Abstract base class for TTS backends."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncGenerator, Any
import io


class Voice:
    """Represents a TTS voice."""
    
    def __init__(
        self,
        id: str,
        name: str,
        language: str,
        gender: str,
        backend: str,
        quality: str = "medium"
    ):
        self.id = id
        self.name = name
        self.language = language
        self.gender = gender
        self.backend = backend
        self.quality = quality
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "gender": self.gender,
            "backend": self.backend,
            "quality": self.quality
        }


class TTSResult:
    """Result from TTS synthesis."""
    
    def __init__(
        self,
        audio_data: bytes,
        backend: str,
        voice: str,
        duration: float,
        sample_rate: int,
        format: str,
        cached: bool = False
    ):
        self.audio_data = audio_data
        self.backend = backend
        self.voice = voice
        self.duration = duration
        self.sample_rate = sample_rate
        self.format = format
        self.cached = cached
    
    @property
    def size_bytes(self) -> int:
        """Get the size of audio data in bytes."""
        return len(self.audio_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API response."""
        import base64
        return {
            "audio_data": base64.b64encode(self.audio_data).decode("utf-8"),
            "metadata": {
                "backend": self.backend,
                "voice": self.voice,
                "duration": self.duration,
                "sample_rate": self.sample_rate,
                "format": self.format,
                "size_bytes": self.size_bytes
            },
            "cached": self.cached
        }


class BackendStatus:
    """Status information for a TTS backend."""
    
    def __init__(
        self,
        name: str,
        enabled: bool,
        available: bool,
        load: float = 0.0,
        queue_size: int = 0
    ):
        self.name = name
        self.enabled = enabled
        self.available = available
        self.load = load
        self.queue_size = queue_size
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "available": self.available,
            "load": self.load,
            "queue_size": self.queue_size
        }


class TTSBackend(ABC):
    """Abstract base class for TTS backends."""
    
    def __init__(self, name: str):
        self.name = name
        self._enabled = True
        self._available = False
    
    @property
    def enabled(self) -> bool:
        """Whether the backend is enabled."""
        return self._enabled
    
    @property
    def available(self) -> bool:
        """Whether the backend is available for use."""
        return self._available
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend."""
        pass
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        quality: Optional[str] = None,
        format: str = "wav",
        sample_rate: int = 22050,
        **kwargs
    ) -> TTSResult:
        """Synthesize text to speech."""
        pass
    
    @abstractmethod
    async def stream_synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        quality: Optional[str] = None,
        format: str = "wav",
        sample_rate: int = 22050,
        **kwargs
    ) -> AsyncGenerator[bytes, None]:
        """Stream synthesized audio."""
        pass
    
    @abstractmethod
    async def get_voices(self) -> List[Voice]:
        """Get available voices for this backend."""
        pass
    
    @abstractmethod
    async def get_status(self) -> BackendStatus:
        """Get current backend status."""
        pass
    
    async def cleanup(self) -> None:
        """Clean up resources used by the backend."""
        pass