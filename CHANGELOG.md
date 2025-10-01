# Changelog

All notable changes to the Danmu TTS Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Nix flake build system refactoring** - Migrated from custom Python package builds to uv2nix and pyproject-nix ecosystem for improved dependency management
  - Added pyproject-nix, uv2nix, and pyproject-build-systems as flake inputs
  - Replaced manual buildPythonPackage and buildPythonApplication with workspace-based virtual environments
  - Removed custom edge-tts package build in favor of uv.lock-based dependency resolution
  - Updated development shell to use dev virtual environment with proper dependencies
  - Improved reproducibility and alignment with Python packaging standards

### Added

- **Makefile for comprehensive server management** - Added complete Makefile with commands for server lifecycle management, dependency installation, and project maintenance
  - `make start` - Start the server in background with PID tracking and logging
  - `make stop` - Stop the server using saved PID with proper process validation
  - `make restart` - Stop and restart the server with appropriate delay
  - `make status` - Check if the server is running with PID validation
  - `make install` - Install production dependencies using uv
  - `make dev` - Install development dependencies using uv
  - `make clean` - Clean up temporary files, logs, and Python cache
  - `make help` - Display available commands and usage information

### Fixed

- **Circular import issue** - Resolved circular import between main.py and API modules by extracting TTSManager to dedicated manager.py module
  - Created new `danmu_tts/manager.py` containing TTSManager class and tts_manager instance
  - Updated `main.py` to import tts_manager from manager module instead of defining locally
  - Updated all API modules (tts.py, backends.py, voices.py) to import from `..manager` instead of `..main`
  - Eliminates circular dependency where main.py imported API modules while API modules imported from main.py

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
