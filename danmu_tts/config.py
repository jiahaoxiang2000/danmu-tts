"""Configuration management for Danmu TTS Server."""

import os
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server configuration settings."""
    
    host: str = Field(default="0.0.0.0", description="Server host address")
    port: int = Field(default=8000, description="Server port")
    log_level: str = Field(default="info", description="Logging level")
    max_text_length: int = Field(default=1000, description="Maximum text length for TTS")


class AudioConfig(BaseModel):
    """Audio output configuration."""
    
    default_format: str = Field(default="wav", description="Default audio format")
    default_sample_rate: int = Field(default=22050, description="Default sample rate")
    default_quality: str = Field(default="medium", description="Default audio quality")
    supported_formats: List[str] = Field(default=["wav"], description="Supported audio formats")
    quality_levels: List[str] = Field(default=["low", "medium", "high"], description="Available quality levels")


class EdgeTTSConfig(BaseModel):
    """Edge TTS backend configuration."""
    
    enabled: bool = Field(default=True, description="Enable Edge TTS backend")
    default_voice: str = Field(default="zh-CN-XiaoxiaoNeural", description="Default voice for Edge TTS")
    rate: str = Field(default="+0%", description="Speech rate adjustment")
    volume: str = Field(default="+0%", description="Volume adjustment")
    pitch: str = Field(default="+0Hz", description="Pitch adjustment")


class Config(BaseModel):
    """Main configuration class."""
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    edge_tts: EdgeTTSConfig = Field(default_factory=EdgeTTSConfig)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            server=ServerConfig(
                host=os.getenv("DANMU_TTS_HOST", "0.0.0.0"),
                port=int(os.getenv("DANMU_TTS_PORT", "8000")),
                log_level=os.getenv("DANMU_TTS_LOG_LEVEL", "info"),
                max_text_length=int(os.getenv("DANMU_TTS_MAX_TEXT_LENGTH", "1000")),
            ),
            audio=AudioConfig(
                default_format=os.getenv("DANMU_TTS_DEFAULT_FORMAT", "wav"),
                default_sample_rate=int(os.getenv("DANMU_TTS_DEFAULT_SAMPLE_RATE", "22050")),
                default_quality=os.getenv("DANMU_TTS_DEFAULT_QUALITY", "medium"),
            ),
            edge_tts=EdgeTTSConfig(
                enabled=os.getenv("DANMU_TTS_EDGE_ENABLED", "true").lower() == "true",
                default_voice=os.getenv("DANMU_TTS_EDGE_DEFAULT_VOICE", "zh-CN-XiaoxiaoNeural"),
                rate=os.getenv("DANMU_TTS_EDGE_RATE", "+0%"),
                volume=os.getenv("DANMU_TTS_EDGE_VOLUME", "+0%"),
                pitch=os.getenv("DANMU_TTS_EDGE_PITCH", "+0Hz"),
            )
        )


config = Config.from_env()