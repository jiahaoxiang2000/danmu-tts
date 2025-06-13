"""Utilities for TTS server"""

import logging
import os
import base64
import hashlib
from pathlib import Path
from typing import Any, Dict
import numpy as np


def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "tts_server.log"),
            logging.StreamHandler(),
        ],
    )


def audio_to_base64(audio_data: bytes) -> str:
    """Convert audio bytes to base64 string"""
    return base64.b64encode(audio_data).decode("utf-8")


def base64_to_audio(b64_string: str) -> bytes:
    """Convert base64 string to audio bytes"""
    return base64.b64decode(b64_string)


def generate_cache_key(text: str, voice: str, backend: str, **kwargs) -> str:
    """Generate cache key for TTS request"""
    key_data = f"{text}_{voice}_{backend}_{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def normalize_audio(audio: np.ndarray, target_db: float = -20.0) -> np.ndarray:
    """Normalize audio to target dB level"""
    # Calculate current RMS
    rms = np.sqrt(np.mean(audio**2))
    if rms > 0:
        # Calculate target amplitude
        target_rms = 10 ** (target_db / 20)
        # Apply normalization
        audio = audio * (target_rms / rms)
    return audio


def check_gpu_availability() -> Dict[str, Any]:
    """Check GPU availability and memory"""
    try:
        import torch

        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            return {
                "available": True,
                "device_count": torch.cuda.device_count(),
                "current_device": device,
                "device_name": torch.cuda.get_device_name(device),
                "memory_allocated": torch.cuda.memory_allocated(device),
                "memory_cached": torch.cuda.memory_reserved(device),
                "memory_total": torch.cuda.get_device_properties(device).total_memory,
            }
    except ImportError:
        pass

    return {"available": False}


def ensure_directory(path: Path) -> None:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)
