"""Configuration management for TTS server"""

import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = ["*"]


class BackendConfig(BaseModel):
    enabled: bool = True

    class Config:
        extra = "allow"


class TTSConfig(BaseModel):
    primary_backend: str = "edge"
    fallback_backends: List[str] = ["piper"]
    backends: Dict[str, Dict[str, Any]] = {}


class AudioConfig(BaseModel):
    sample_rate: int = 22050
    format: str = "wav"
    quality: str = "medium"
    normalize: bool = True


class GPUConfig(BaseModel):
    enabled: bool = True
    device: str = "cuda:0"
    memory_fraction: float = 0.6


class CacheConfig(BaseModel):
    enabled: bool = True
    type: str = "memory"
    max_size_mb: int = 500
    ttl_seconds: int = 3600


class QueueConfig(BaseModel):
    max_concurrent: int = 10
    timeout_seconds: int = 30
    priority_enabled: bool = True


class PerformanceConfig(BaseModel):
    gpu: GPUConfig = GPUConfig()
    cache: CacheConfig = CacheConfig()
    queue: QueueConfig = QueueConfig()


class StreamingConfig(BaseModel):
    buffer_size: int = 4096
    chunk_duration_ms: int = 100
    websocket_timeout: int = 60


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/tts_server.log"
    rotation: str = "1 day"
    retention: str = "7 days"


class Settings(BaseModel):
    server: ServerConfig = ServerConfig()
    tts: TTSConfig = TTSConfig()
    audio: AudioConfig = AudioConfig()
    performance: PerformanceConfig = PerformanceConfig()
    streaming: StreamingConfig = StreamingConfig()
    logging: LoggingConfig = LoggingConfig()


def load_config(config_path: str = "config.yaml") -> Settings:
    """Load configuration from YAML file"""
    config_file = Path(config_path)

    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        return Settings(**config_data)
    else:
        # Return default settings if no config file
        return Settings()


# Global settings instance
settings = load_config()
