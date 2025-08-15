"""Request models for the Danmu TTS API."""

from typing import Optional

from pydantic import BaseModel, Field, validator


class TTSRequest(BaseModel):
    """Request model for text-to-speech synthesis."""
    
    text: str = Field(
        ...,
        description="Text to convert to speech",
        min_length=1,
        max_length=1000
    )
    voice: Optional[str] = Field(
        None,
        description="Voice ID to use for synthesis"
    )
    backend: Optional[str] = Field(
        None,
        description="TTS backend to use (e.g., 'edge', 'xtts', 'piper')"
    )
    quality: Optional[str] = Field(
        None,
        description="Audio quality level"
    )
    format: Optional[str] = Field(
        "wav",
        description="Audio format"
    )
    sample_rate: Optional[int] = Field(
        22050,
        description="Audio sample rate in Hz",
        ge=8000,
        le=48000
    )
    
    @validator("text")
    def validate_text(cls, v):
        """Validate text input."""
        if not v.strip():
            raise ValueError("Text cannot be empty or only whitespace")
        return v.strip()
    
    @validator("quality")
    def validate_quality(cls, v):
        """Validate quality parameter."""
        if v is not None and v not in ["low", "medium", "high"]:
            raise ValueError("Quality must be one of: low, medium, high")
        return v
    
    @validator("format")
    def validate_format(cls, v):
        """Validate audio format."""
        if v not in ["wav"]:  # Only wav supported in MVP
            raise ValueError("Format must be 'wav'")
        return v
    
    @validator("backend")
    def validate_backend(cls, v):
        """Validate backend parameter."""
        if v is not None and v not in ["edge"]:  # Only edge supported in MVP
            raise ValueError("Backend must be 'edge'")
        return v


class StreamTTSRequest(BaseModel):
    """Request model for streaming TTS synthesis."""
    
    text: str = Field(
        ...,
        description="Text to convert to speech",
        min_length=1,
        max_length=1000
    )
    voice: Optional[str] = Field(
        None,
        description="Voice ID to use for synthesis"
    )
    backend: Optional[str] = Field(
        "edge",
        description="TTS backend to use"
    )
    
    @validator("text")
    def validate_text(cls, v):
        """Validate text input."""
        if not v.strip():
            raise ValueError("Text cannot be empty or only whitespace")
        return v.strip()
    
    @validator("backend")
    def validate_backend(cls, v):
        """Validate backend parameter."""
        if v not in ["edge"]:  # Only edge supported in MVP
            raise ValueError("Backend must be 'edge'")
        return v