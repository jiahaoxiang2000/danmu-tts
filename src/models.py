"""Data models for TTS server"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import base64


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    backend: Optional[str] = None
    quality: Optional[str] = "medium"
    format: Optional[str] = "wav"
    sample_rate: Optional[int] = None


class TTSResponse(BaseModel):
    audio_data: str  # Base64 encoded audio
    metadata: Dict[str, Any]
    cached: bool = False


class VoiceInfo(BaseModel):
    id: str
    name: str
    language: str
    gender: str
    backend: str
    quality: str = "medium"


class BackendStatus(BaseModel):
    name: str
    enabled: bool
    available: bool
    load: float = 0.0
    queue_size: int = 0


class ServerStats(BaseModel):
    uptime: float
    total_requests: int
    cache_hit_rate: float
    active_connections: int
    backend_status: List[BackendStatus]
    gpu_usage: Optional[Dict[str, Any]] = None
