# Danmu TTS Server

A high-performance Text-to-Speech server designed for live streaming with multiple backend options to balance quality and speed.

## Features

- **Multiple TTS Backends**:

  - EdgeTTS (Fast, Free, Good Quality)
  - XTTS (High Quality, GPU Accelerated)
  - Piper TTS (Local, Fast)
  - Azure/OpenAI TTS (Cloud, High Quality)

- **Performance Optimization**:

  - GPU acceleration support (CUDA for RTX 4090)
  - Audio caching system
  - Queue management for concurrent requests
  - Automatic backend selection based on load

- **Live Streaming Integration**:

  - WebSocket support for real-time communication
  - RESTful API for easy integration
  - Audio streaming capabilities
  - Danmu (bullet comment) processing

- **Production-Ready Server Management**:
  - Background process management with PID tracking
  - Comprehensive Makefile for all operations
  - Advanced monitoring and health checks
  - Auto-restart daemon for high availability
  - Systemd service support for production deployment
  - Real-time performance monitoring

## Quick Start

### Simple Setup and Start

```bash
# Setup (first time only)
make setup

# Start server in background
make start

# Check server status
make status

# View logs
make logs

# Stop server
make stop
```

### Option 1: Automated Setup with UV (Recommended)

```bash
# Run the automated setup script
./setup.sh

# Start the server in background
./start_server.sh start

# Check server status
./start_server.sh status
```

### Option 2: Using Makefile (Recommended for Development)

```bash
# Install dependencies and setup environment
make setup

# Start server in development mode (foreground)
make dev

# Or start in background
make start

# Test the API
make test-api
```

### Option 3: Manual Setup with UV

```bash
# Install UV (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Create virtual environment with Python 3.11
uv venv --python 3.11
source .venv/bin/activate

# Install all dependencies (10x faster than pip)
uv pip install -e .[all]

# For RTX 4090 GPU support
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Start the server
python app.py
```

### Option 4: Traditional pip Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Web Interface

Access the beautiful web interface at: **http://localhost:8000/web/**

Features:

- Real-time TTS testing
- Voice selection and backend switching
- Performance monitoring
- Audio playback and download

## API Endpoints

- `POST /tts` - Generate TTS audio
- `GET /voices` - List available voices
- `WebSocket /ws` - Real-time TTS streaming

## Configuration

Edit `config.yaml` to customize:

- TTS backend preferences
- GPU settings
- Audio quality settings
- Cache configuration
