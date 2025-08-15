# Changelog

All notable changes to the Danmu TTS Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-15

### Added

- **Complete MVP implementation of Danmu TTS Server with Edge TTS backend**
- Full FastAPI application with comprehensive REST API endpoints
- Edge TTS backend integration for high-quality text-to-speech synthesis
- Configuration system with environment variables support
- Modular architecture with separate API, backends, models, and utils packages
- TTS synthesis endpoint (`/tts/`) for converting text to speech with base64 encoded audio response
- Real-time audio streaming endpoint (`/tts/stream`) for live audio streaming
- Voice management endpoints for listing and getting available voices
- Backend management endpoints for checking backend status and capabilities
- Health check endpoints for service monitoring
- Comprehensive request/response models with proper validation
- Audio utilities for format conversion and metadata extraction
- Error handling with custom exceptions
- CORS middleware configuration for cross-origin requests
- Application lifespan management with proper startup/shutdown procedures
- Complete dependency configuration in pyproject.toml
- REST API test suite for endpoint validation
- Project restructure from `src/` to root-level `danmu_tts/` package

### Changed

- Moved from `src/` directory structure to root-level `danmu_tts/` package
- Updated pyproject.toml to reflect new package structure and dependencies
- Updated .gitignore to remove models/ exclusion for better project organization

### Technical Details

- FastAPI 0.104.0+ with uvicorn server
- Edge TTS 6.1.0+ for text-to-speech synthesis
- Pydantic 2.5.0+ for data validation
- Async/await pattern throughout for optimal performance
- Streaming audio support for real-time applications
- Multiple audio format support (MP3, WAV, OGG)
- Configurable quality settings and sample rates
- Backend abstraction layer for future TTS engine integrations
