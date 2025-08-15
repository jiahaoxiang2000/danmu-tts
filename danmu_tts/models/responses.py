"""Response models for the Danmu TTS API."""

from typing import List, Optional, Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""
    
    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Health status message")


class AudioMetadata(BaseModel):
    """Metadata for generated audio."""
    
    backend: str = Field(..., description="TTS backend used")
    voice: str = Field(..., description="Voice used for synthesis")
    duration: float = Field(..., description="Audio duration in seconds")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    format: str = Field(..., description="Audio format")
    size_bytes: int = Field(..., description="Audio data size in bytes")


class TTSResponse(BaseModel):
    """Response model for TTS synthesis."""
    
    audio_data: str = Field(..., description="Base64 encoded audio data")
    metadata: AudioMetadata = Field(..., description="Audio metadata")
    cached: bool = Field(False, description="Whether result was cached")


class VoiceInfo(BaseModel):
    """Information about a TTS voice."""
    
    id: str = Field(..., description="Voice identifier")
    name: str = Field(..., description="Human-readable voice name")
    language: str = Field(..., description="Language code (e.g., 'zh-CN')")
    gender: str = Field(..., description="Voice gender")
    backend: str = Field(..., description="TTS backend that provides this voice")
    quality: str = Field(..., description="Voice quality level")


class VoicesResponse(BaseModel):
    """Response model for voice listing."""
    
    voices: List[VoiceInfo] = Field(..., description="List of available voices")


class BackendInfo(BaseModel):
    """Information about a TTS backend."""
    
    name: str = Field(..., description="Backend name")
    enabled: bool = Field(..., description="Whether backend is enabled")
    available: bool = Field(..., description="Whether backend is available")
    load: float = Field(..., description="Current load factor (0.0-1.0)")
    queue_size: int = Field(..., description="Number of requests in queue")


class BackendsResponse(BaseModel):
    """Response model for backend listing."""
    
    backends: List[BackendInfo] = Field(..., description="List of available backends")


class GPUDevice(BaseModel):
    """Information about a GPU device."""
    
    id: int = Field(..., description="GPU device ID")
    name: str = Field(..., description="GPU device name")
    memory_total: str = Field(..., description="Total GPU memory")
    memory_used: str = Field(..., description="Used GPU memory")


class GPUUsage(BaseModel):
    """GPU usage information."""
    
    available: bool = Field(..., description="Whether GPU is available")
    devices: List[GPUDevice] = Field(..., description="List of GPU devices")


class StatsResponse(BaseModel):
    """Response model for server statistics."""
    
    uptime: float = Field(..., description="Server uptime in seconds")
    total_requests: int = Field(..., description="Total number of requests processed")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    active_connections: int = Field(..., description="Number of active connections")
    backend_status: List[BackendInfo] = Field(..., description="Status of all backends")
    gpu_usage: Optional[GPUUsage] = Field(None, description="GPU usage information")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error message")