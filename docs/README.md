# Danmu TTS Server Documentation

Welcome to the Danmu TTS Server documentation! This is a high-performance Text-to-Speech server designed for live streaming applications with multiple backend options.

## Quick Navigation

### Getting Started

- [Installation Guide](installation.md) - Complete setup instructions
- [Quick Start](quick-start.md) - Get up and running in minutes
- [Configuration](configuration.md) - Server and backend configuration

### API Documentation

- [REST API Reference](api/rest-api.md) - HTTP endpoints documentation
- [WebSocket API](api/websocket-api.md) - Real-time communication
- [Response Formats](api/response-formats.md) - Data structures and formats

### Backend Engines

- [EdgeTTS](backends/edge-tts.md) - Fast, free, cloud-based TTS
- [XTTS](backends/xtts.md) - High-quality, GPU-accelerated TTS
- [Piper TTS](backends/piper-tts.md) - Local, lightweight TTS
- [Azure TTS](backends/azure-tts.md) - Microsoft Azure Cognitive Services
- [OpenAI TTS](backends/openai-tts.md) - OpenAI's text-to-speech API

### Advanced Features

- [Caching System](advanced/caching.md) - Audio caching for performance
- [GPU Acceleration](advanced/gpu-acceleration.md) - CUDA optimization
- [Performance Tuning](advanced/performance.md) - Optimization guidelines
- [Load Balancing](advanced/load-balancing.md) - Multiple backend management

### Development

- [Architecture](development/architecture.md) - System design overview
- [Contributing](development/contributing.md) - How to contribute
- [Testing](development/testing.md) - Testing guidelines
- [Debugging](development/debugging.md) - Troubleshooting guide

### Deployment

- [Docker Deployment](deployment/docker.md) - Containerized deployment
- [Production Setup](deployment/production.md) - Production considerations
- [Monitoring](deployment/monitoring.md) - Health checks and metrics

### Integration

- [Live Streaming](integration/streaming.md) - Integration with streaming platforms
- [Danmu Processing](integration/danmu.md) - Bullet comment handling
- [Client Examples](integration/examples.md) - Sample implementations

## Project Overview

The Danmu TTS Server is designed to provide real-time text-to-speech conversion for live streaming applications, particularly for processing "danmu" (bullet comments) from viewers. It features:

- **Multiple TTS Backends**: Choose the best engine for your needs
- **High Performance**: GPU acceleration and intelligent caching
- **Real-time Processing**: WebSocket support for instant responses
- **Easy Integration**: RESTful API and comprehensive documentation
- **Production Ready**: Docker support and monitoring capabilities

## Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: This documentation is continuously updated
- **Community**: Join our discussions for help and updates

---

_Last updated: June 2025_
