"""Custom exceptions for the Danmu TTS Server."""


class TTSError(Exception):
    """Base exception for TTS-related errors."""
    pass


class BackendError(TTSError):
    """Exception raised when a TTS backend encounters an error."""
    pass


class BackendNotAvailableError(BackendError):
    """Exception raised when a requested backend is not available."""
    pass


class VoiceNotFoundError(TTSError):
    """Exception raised when a requested voice is not found."""
    pass


class AudioProcessingError(TTSError):
    """Exception raised when audio processing fails."""
    pass


class TextTooLongError(TTSError):
    """Exception raised when input text exceeds maximum length."""
    pass


class InvalidParameterError(TTSError):
    """Exception raised when invalid parameters are provided."""
    pass