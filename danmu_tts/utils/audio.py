"""Audio processing utilities."""

import wave
import io
from typing import Tuple, Optional


def get_audio_info(audio_data: bytes) -> Tuple[int, int, int]:
    """
    Get basic information about WAV audio data.
    
    Args:
        audio_data: Raw audio data in WAV format
        
    Returns:
        Tuple of (sample_rate, channels, frames)
    """
    try:
        with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            frames = wav_file.getnframes()
            return sample_rate, channels, frames
    except Exception as e:
        raise ValueError(f"Invalid WAV data: {e}")


def calculate_duration(audio_data: bytes) -> float:
    """
    Calculate duration of WAV audio data in seconds.
    
    Args:
        audio_data: Raw audio data in WAV format
        
    Returns:
        Duration in seconds
    """
    try:
        sample_rate, channels, frames = get_audio_info(audio_data)
        return frames / sample_rate
    except Exception as e:
        raise ValueError(f"Could not calculate duration: {e}")


def validate_audio_format(audio_data: bytes, expected_format: str = "wav") -> bool:
    """
    Validate that audio data matches expected format.
    
    Args:
        audio_data: Raw audio data
        expected_format: Expected audio format (currently only 'wav' supported)
        
    Returns:
        True if format is valid
    """
    if expected_format.lower() != "wav":
        return False
    
    try:
        # Check if it's valid WAV data by trying to parse it
        get_audio_info(audio_data)
        return True
    except:
        return False


def estimate_text_duration(text: str, words_per_second: float = 2.5) -> float:
    """
    Estimate audio duration based on text length.
    
    Args:
        text: Input text
        words_per_second: Average speaking rate
        
    Returns:
        Estimated duration in seconds
    """
    words = len(text.split())
    return max(0.5, words / words_per_second)  # Minimum 0.5 seconds