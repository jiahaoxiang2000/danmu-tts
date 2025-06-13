# REST API Reference

The Danmu TTS Server provides a comprehensive REST API for text-to-speech conversion and system management.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API supports optional API key authentication. If enabled in configuration:

```http
Authorization: Bearer your-api-key
```

## Content Type

All requests should use JSON content type:

```http
Content-Type: application/json
```

## Endpoints

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
- `backend` (string, optional): TTS backend ("edge", "xtts", "piper", "azure", "openai")
- `quality` (string, optional): Audio quality ("low", "medium", "high", "ultra")
- `format` (string, optional): Audio format ("wav", "mp3", "ogg")
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

#### GET /stream

Stream audio as it's generated (Server-Sent Events).

**Query Parameters:**

- `text` (string, required): Text to convert
- `voice` (string, optional): Voice ID
- `backend` (string, optional): TTS backend
- `quality` (string, optional): Audio quality
- `format` (string, optional): Audio format

**Response:**
Returns a stream of audio chunks as they're generated.

**Example:**

```bash
curl "http://localhost:8000/stream?text=Hello&voice=zh-CN-XiaoxiaoNeural" \
  --output audio.wav
```

### Voice Management

#### GET /voices

List all available voices across all backends.

**Query Parameters:**

- `backend` (string, optional): Filter by backend
- `language` (string, optional): Filter by language code
- `gender` (string, optional): Filter by gender ("male", "female")

**Response:**

```json
{
  "voices": [
    {
      "id": "zh-CN-XiaoxiaoNeural",
      "name": "Xiaoxiao (Neural)",
      "language": "zh-CN",
      "gender": "female",
      "backend": "edge",
      "quality": "high"
    },
    {
      "id": "zh_CN-huayan-medium",
      "name": "Huayan Medium",
      "language": "zh-CN",
      "gender": "female",
      "backend": "piper",
      "quality": "medium"
    }
  ],
  "total": 2
}
```

**Example:**

```bash
curl "http://localhost:8000/voices?language=zh-CN"
```

#### GET /voices/{backend}

Get voices for a specific backend.

**Path Parameters:**

- `backend` (string): Backend name

**Response:**
Same format as `/voices` but filtered by backend.

### Backend Management

#### GET /backends

List all available TTS backends and their status.

**Response:**

```json
{
  "backends": [
    {
      "name": "edge",
      "enabled": true,
      "status": "available",
      "version": "1.0",
      "capabilities": ["realtime", "multiple_voices"],
      "load": 0.2,
      "queue_size": 0
    },
    {
      "name": "xtts",
      "enabled": true,
      "status": "available",
      "version": "2.0",
      "capabilities": ["gpu_acceleration", "voice_cloning"],
      "load": 0.8,
      "queue_size": 3
    }
  ]
}
```

**Status Values:**

- `available`: Backend is ready to process requests
- `loading`: Backend is initializing
- `error`: Backend has encountered an error
- `disabled`: Backend is disabled in configuration

#### GET /backends/{backend}/status

Get detailed status for a specific backend.

**Path Parameters:**

- `backend` (string): Backend name

**Response:**

```json
{
  "name": "xtts",
  "enabled": true,
  "status": "available",
  "version": "2.0.1",
  "gpu_memory_used": "2.1 GB",
  "gpu_memory_total": "24 GB",
  "model_loaded": true,
  "queue_size": 2,
  "processing_time_avg": 1.2,
  "requests_processed": 1523,
  "errors": 3
}
```

### System Information

#### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-06-13T10:30:00Z",
  "version": "1.0.0",
  "uptime": 3600,
  "backends_available": 3,
  "memory_usage": "1.2 GB",
  "cpu_usage": 25.5
}
```

**Status Values:**

- `healthy`: All systems operational
- `degraded`: Some backends unavailable
- `unhealthy`: Critical errors

#### GET /info

Detailed system information.

**Response:**

```json
{
  "version": "1.0.0",
  "python_version": "3.11.0",
  "platform": "Linux-5.15.0-72-generic-x86_64",
  "gpu_available": true,
  "gpu_devices": [
    {
      "id": 0,
      "name": "NVIDIA RTX 4090",
      "memory_total": "24 GB",
      "memory_used": "2.1 GB"
    }
  ],
  "backends": {
    "edge": "available",
    "xtts": "available",
    "piper": "available"
  },
  "cache": {
    "enabled": true,
    "size": 156,
    "hit_rate": 0.85
  }
}
```

#### GET /metrics

System metrics in Prometheus format (if enabled).

**Response:**

```
# HELP tts_requests_total Total number of TTS requests
# TYPE tts_requests_total counter
tts_requests_total{backend="edge"} 1523
tts_requests_total{backend="xtts"} 456

# HELP tts_processing_time_seconds Time spent processing TTS requests
# TYPE tts_processing_time_seconds histogram
tts_processing_time_seconds_bucket{backend="edge",le="0.5"} 1200
tts_processing_time_seconds_bucket{backend="edge",le="1.0"} 1450
```

### Cache Management

#### GET /cache/stats

Get cache statistics.

**Response:**

```json
{
  "enabled": true,
  "backend": "memory",
  "size": 156,
  "max_size": 1000,
  "memory_usage": "45.2 MB",
  "hit_rate": 0.85,
  "miss_rate": 0.15,
  "total_requests": 2000,
  "cache_hits": 1700,
  "cache_misses": 300
}
```

#### DELETE /cache

Clear all cached audio.

**Response:**

```json
{
  "message": "Cache cleared successfully",
  "items_removed": 156
}
```

#### DELETE /cache/{key}

Remove a specific cache entry.

**Path Parameters:**

- `key` (string): Cache key to remove

**Response:**

```json
{
  "message": "Cache entry removed",
  "key": "edge:zh-CN-XiaoxiaoNeural:hello_world"
}
```

### Queue Management

#### GET /queue

Get current processing queue status.

**Response:**

```json
{
  "total_queued": 5,
  "queues": {
    "edge": {
      "size": 2,
      "processing": 1,
      "avg_wait_time": 0.5
    },
    "xtts": {
      "size": 3,
      "processing": 1,
      "avg_wait_time": 2.1
    }
  }
}
```

## Error Handling

All API endpoints return errors in a consistent format:

```json
{
  "error": {
    "code": "INVALID_VOICE",
    "message": "Voice 'invalid-voice' not found",
    "details": {
      "voice": "invalid-voice",
      "available_voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]
    }
  }
}
```

### Common Error Codes

- `INVALID_TEXT`: Text is empty or too long
- `INVALID_VOICE`: Voice ID not found
- `INVALID_BACKEND`: Backend not available
- `BACKEND_ERROR`: Backend processing failed
- `QUEUE_FULL`: Processing queue is full
- `RATE_LIMITED`: Rate limit exceeded
- `AUTHENTICATION_FAILED`: Invalid API key
- `VALIDATION_ERROR`: Request validation failed

## Rate Limiting

API endpoints are subject to rate limiting:

**Headers:**

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1623456789
```

## Pagination

For endpoints that return lists (like voices), pagination is supported:

**Query Parameters:**

- `page` (integer, default: 1): Page number
- `limit` (integer, default: 50): Items per page

**Response Headers:**

```http
X-Total-Count: 150
X-Page: 1
X-Per-Page: 50
X-Total-Pages: 3
```

## OpenAPI Specification

The complete API specification is available at:

```
http://localhost:8000/docs
```

Interactive API documentation (Swagger UI):

```
http://localhost:8000/redoc
```

Raw OpenAPI JSON:

```
http://localhost:8000/openapi.json
```

## SDK Examples

### Python

```python
import requests
import base64

class DanmuTTSClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def synthesize(self, text, voice=None, backend=None):
        response = requests.post(f"{self.base_url}/tts", json={
            "text": text,
            "voice": voice,
            "backend": backend
        })
        response.raise_for_status()
        return response.json()

    def get_voices(self, language=None):
        params = {"language": language} if language else {}
        response = requests.get(f"{self.base_url}/voices", params=params)
        return response.json()["voices"]

# Usage
client = DanmuTTSClient()
result = client.synthesize("Hello, world!", voice="zh-CN-XiaoxiaoNeural")
audio_data = base64.b64decode(result["audio_data"])
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

  async getVoices(language = null) {
    const params = language ? `?language=${language}` : "";
    const response = await fetch(`${this.baseUrl}/voices${params}`);
    const data = await response.json();
    return data.voices;
  }
}

// Usage
const client = new DanmuTTSClient();
const result = await client.synthesize("Hello, world!", {
  voice: "zh-CN-XiaoxiaoNeural",
  backend: "edge",
});
```
