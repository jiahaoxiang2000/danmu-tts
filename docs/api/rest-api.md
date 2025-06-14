# REST API Reference

The Danmu TTS Server provides a comprehensive REST API for text-to-speech conversion and system management.

## Server Management

The server includes comprehensive management tools for background operation, monitoring, and automation.

### Quick Start

```bash
# Setup (first time)
make setup

# Start server in background
make start

# Check server status
make status

# View logs
make logs

# Stop server
make stop

# Restart server
make restart
```

### Background Operation

The server can run in background mode with automatic process management:

```bash
# Start in background
./start_server.sh start

# Start in foreground (development)
./start_server.sh foreground

# Check status
./start_server.sh status

# Stop server
./start_server.sh stop

# Restart server
./start_server.sh restart
```

### Process Management

Advanced process monitoring and management:

```bash
# Show detailed process information
./process_manager.sh info

# Monitor server in real-time
./process_manager.sh monitor

# Perform health check
./process_manager.sh health

# Start auto-restart daemon
./process_manager.sh auto-restart

# Show performance statistics
./process_manager.sh performance
```

### Makefile Commands

Complete project management through Makefile:

| Command          | Description                                |
| ---------------- | ------------------------------------------ |
| `make setup`     | Install dependencies and setup environment |
| `make start`     | Start server in background                 |
| `make stop`      | Stop the server                            |
| `make restart`   | Restart the server                         |
| `make status`    | Show server status                         |
| `make dev`       | Run server in development mode             |
| `make logs`      | Show server logs (real-time)               |
| `make logs-tail` | Show last 50 lines of logs                 |
| `make test-api`  | Test API endpoints                         |
| `make test-tts`  | Test TTS functionality                     |
| `make clean`     | Clean cache and temporary files            |
| `make info`      | Show system information                    |

### Systemd Service (Optional)

For production deployment, you can install the server as a systemd service:

```bash
# Copy service file
sudo cp danmu-tts.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable danmu-tts

# Start service
sudo systemctl start danmu-tts

# Check status
sudo systemctl status danmu-tts
```

## Base URL

```
http://localhost:8000
```

## Content Type

All requests should use JSON content type:

```http
Content-Type: application/json
```

## Endpoints

### Health Check

#### GET /

Basic health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "message": "Danmu TTS Server is running"
}
```

**Status Codes:**

- `200`: Success - Server is running

**Example:**

```bash
curl "http://localhost:8000/"
```

### Text-to-Speech

#### POST /tts

Convert text to speech audio.

**Request Body:**

```json
{
  "text": "你好，欢迎使用弹幕TTS服务器！",
  "voice": "zh-CN-XiaoxiaoNeural",
  "backend": "edge",
  "quality": "medium",
  "format": "wav",
  "sample_rate": 22050
}
```

**Parameters:**

- `text` (string, required): Text to convert to speech
- `voice` (string, optional): Voice ID to use
- `backend` (string, optional): TTS backend ("edge", "xtts", "piper")
- `quality` (string, optional): Audio quality ("low", "medium", "high")
- `format` (string, optional): Audio format ("wav")
- `sample_rate` (integer, optional): Audio sample rate

**Response:**

```json
{
  "audio_data": "UklGRiQAAABXQVZF...",
  "metadata": {
    "backend": "edge",
    "voice": "zh-CN-XiaoxiaoNeural",
    "duration": 2.34,
    "sample_rate": 22050,
    "format": "wav",
    "size_bytes": 103456
  },
  "cached": false
}
```

**Status Codes:**

- `200`: Success
- `400`: Bad request (invalid parameters)
- `422`: Validation error
- `500`: Server error
- `503`: Service unavailable (all backends failed)

**Example:**

```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "voice": "zh-CN-XiaoxiaoNeural",
    "backend": "edge"
  }'
```

#### GET /tts/stream

Stream audio as it's generated.

**Query Parameters:**

- `text` (string, required): Text to convert
- `voice` (string, optional): Voice ID
- `backend` (string, optional): TTS backend

**Response:**
Returns audio stream with appropriate Content-Type headers.

**Headers:**

- `Content-Type: audio/wav`
- `Content-Disposition: attachment; filename=tts_audio.wav`

**Example:**

```bash
curl "http://localhost:8000/tts/stream?text=Hello&voice=zh-CN-XiaoxiaoNeural" \
  --output audio.wav
```

### Voice Management

#### GET /voices

List all available voices across all backends.

**Query Parameters:**

- `backend` (string, optional): Filter by backend

**Response:**

```json
[
  {
    "id": "zh-CN-XiaoxiaoNeural",
    "name": "Xiaoxiao (Neural)",
    "language": "zh-CN",
    "gender": "female",
    "backend": "edge",
    "quality": "medium"
  },
  {
    "id": "zh_CN-huayan-medium",
    "name": "Huayan Medium",
    "language": "zh-CN",
    "gender": "female",
    "backend": "piper",
    "quality": "medium"
  }
]
```

**Example:**

```bash
curl "http://localhost:8000/voices?backend=edge"
```

### Backend Management

#### GET /backends

List all available TTS backends and their status.

**Response:**

```json
[
  {
    "name": "edge",
    "enabled": true,
    "available": true,
    "load": 0.2,
    "queue_size": 0
  },
  {
    "name": "xtts",
    "enabled": true,
    "available": true,
    "load": 0.8,
    "queue_size": 3
  }
]
```

**Status Fields:**

- `enabled`: Backend is enabled in configuration
- `available`: Backend is ready to process requests
- `load`: Current load factor (0.0 to 1.0)
- `queue_size`: Number of requests in queue

### System Information

#### GET /stats

Get comprehensive server statistics.

**Response:**

```json
{
  "uptime": 3600.5,
  "total_requests": 1523,
  "cache_hit_rate": 85.2,
  "active_connections": 3,
  "backend_status": [
    {
      "name": "edge",
      "enabled": true,
      "available": true,
      "load": 0.2,
      "queue_size": 0
    }
  ],
  "gpu_usage": {
    "available": true,
    "devices": [
      {
        "id": 0,
        "name": "NVIDIA RTX 4090",
        "memory_total": "24 GB",
        "memory_used": "2.1 GB"
      }
    ]
  }
}
```

#### GET /health

Health check endpoint (alias for `/`).

**Response:**

```json
{
  "status": "ok",
  "message": "Danmu TTS Server is running"
}
```

## Error Handling

All API endpoints return errors in a consistent format using standard HTTP status codes and JSON responses:

```json
{
  "detail": "Voice 'invalid-voice' not found"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid parameters or malformed request
- `422`: Validation Error - Request validation failed
- `500`: Internal Server Error - Backend processing failed or server error
- `503`: Service Unavailable - All backends failed

### Status Codes by Endpoint

**POST /tts:**

- `200`: Success
- `422`: Validation error (invalid parameters)
- `500`: TTS generation failed

**GET /tts/stream:**

- `200`: Success
- `500`: TTS streaming failed

**GET /voices:**

- `200`: Success
- `500`: Failed to retrieve voices

**GET /backends:**

- `200`: Success
- `500`: Failed to get backend status

**GET /stats:**

- `200`: Success
- `500`: Failed to get server statistics

## OpenAPI Specification

The server provides automatic API documentation through FastAPI:

Interactive API documentation (Swagger UI):

```
http://localhost:8000/docs
```

Alternative documentation (ReDoc):

```
http://localhost:8000/redoc
```

Raw OpenAPI JSON specification:

```
http://localhost:8000/openapi.json
```

## SDK Examples

### Python

```python
import requests
import base64
from typing import Optional, List

class DanmuTTSClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def synthesize(self, text: str, voice: Optional[str] = None,
                  backend: Optional[str] = None, quality: Optional[str] = None):
        """Generate TTS audio from text"""
        response = requests.post(f"{self.base_url}/tts", json={
            "text": text,
            "voice": voice,
            "backend": backend,
            "quality": quality
        })
        response.raise_for_status()
        return response.json()

    def get_voices(self, backend: Optional[str] = None) -> List[dict]:
        """Get available voices"""
        params = {"backend": backend} if backend else {}
        response = requests.get(f"{self.base_url}/voices", params=params)
        response.raise_for_status()
        return response.json()

    def get_backends(self) -> List[dict]:
        """Get backend status"""
        response = requests.get(f"{self.base_url}/backends")
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> dict:
        """Get server statistics"""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    def stream_audio(self, text: str, voice: Optional[str] = None,
                    backend: Optional[str] = None, output_file: str = "output.wav"):
        """Stream TTS audio to file"""
        params = {"text": text}
        if voice:
            params["voice"] = voice
        if backend:
            params["backend"] = backend

        response = requests.get(f"{self.base_url}/tts/stream",
                              params=params, stream=True)
        response.raise_for_status()

        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

# Usage examples
client = DanmuTTSClient()

# Basic text-to-speech
result = client.synthesize("Hello, world!", voice="zh-CN-XiaoxiaoNeural")
audio_data = base64.b64decode(result["audio_data"])

# Get available voices
voices = client.get_voices(backend="edge")
print(f"Available voices: {len(voices)}")

# Stream audio to file
client.stream_audio("Hello streaming!", output_file="hello.wav")
```

### JavaScript

```javascript
class DanmuTTSClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async synthesize(text, options = {}) {
    const response = await fetch(`${this.baseUrl}/tts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        ...options,
      }),
    });

    if (!response.ok) {
      throw new Error(`TTS request failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async getVoices(backend = null) {
    const params = backend ? `?backend=${backend}` : "";
    const response = await fetch(`${this.baseUrl}/voices${params}`);

    if (!response.ok) {
      throw new Error(`Failed to get voices: ${response.statusText}`);
    }

    return await response.json();
  }

  async getBackends() {
    const response = await fetch(`${this.baseUrl}/backends`);

    if (!response.ok) {
      throw new Error(`Failed to get backends: ${response.statusText}`);
    }

    return await response.json();
  }

  async getStats() {
    const response = await fetch(`${this.baseUrl}/stats`);

    if (!response.ok) {
      throw new Error(`Failed to get stats: ${response.statusText}`);
    }

    return await response.json();
  }

  async streamAudio(text, options = {}) {
    const params = new URLSearchParams({ text });
    if (options.voice) params.append("voice", options.voice);
    if (options.backend) params.append("backend", options.backend);

    const response = await fetch(`${this.baseUrl}/tts/stream?${params}`);

    if (!response.ok) {
      throw new Error(`Stream request failed: ${response.statusText}`);
    }

    return response.blob();
  }
}

// Usage examples
const client = new DanmuTTSClient();

// Basic text-to-speech
try {
  const result = await client.synthesize("Hello, world!", {
    voice: "zh-CN-XiaoxiaoNeural",
    backend: "edge",
  });

  // Convert base64 to audio blob
  const audioData = atob(result.audio_data);
  const audioBlob = new Blob(
    [new Uint8Array([...audioData].map((c) => c.charCodeAt(0)))],
    { type: "audio/wav" }
  );

  // Play audio
  const audio = new Audio(URL.createObjectURL(audioBlob));
  audio.play();
} catch (error) {
  console.error("TTS failed:", error);
}

// Get available voices
const voices = await client.getVoices("edge");
console.log("Available voices:", voices);

// Stream audio
const audioBlob = await client.streamAudio("Hello streaming!");
const audio = new Audio(URL.createObjectURL(audioBlob));
audio.play();
```

### cURL Examples

```bash
# Basic TTS request
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界！",
    "voice": "zh-CN-XiaoxiaoNeural",
    "backend": "edge"
  }'

# Stream audio to file
curl "http://localhost:8000/tts/stream?text=Hello&voice=zh-CN-XiaoxiaoNeural" \
  --output audio.wav

# Get available voices
curl "http://localhost:8000/voices"

# Get backend status
curl "http://localhost:8000/backends"

# Get server statistics
curl "http://localhost:8000/stats"

# Health check
curl "http://localhost:8000/"
```
