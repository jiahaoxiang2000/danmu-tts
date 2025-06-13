# System Architecture

This document provides a comprehensive overview of the Danmu TTS Server architecture, including system design, component interactions, and data flow.

## Overview

The Danmu TTS Server is built as a modular, scalable system designed for real-time text-to-speech processing in live streaming environments. The architecture emphasizes performance, reliability, and extensibility.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │  REST Client    │    │ WebSocket Client │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   (FastAPI)     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ REST API    │      │ WebSocket   │      │ Static      │
│ Endpoints   │      │ Handler     │      │ Files       │
└─────────────┘      └─────────────┘      └─────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  TTS Manager    │
                    │  (Orchestrator) │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Backend     │      │ Cache       │      │ Queue       │
│ Manager     │      │ Manager     │      │ Manager     │
└─────────────┘      └─────────────┘      └─────────────┘
         │                       │                       │
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ EdgeTTS     │      │ Memory      │      │ Priority    │
│ XTTS        │      │ Redis       │      │ Round Robin │
│ Piper       │      │ File Cache  │      │ Load Balance│
│ Azure/OpenAI│      └─────────────┘      └─────────────┘
└─────────────┘
```

## Core Components

### 1. API Gateway (FastAPI Application)

**Location**: `app.py`

The main application server built with FastAPI, providing:

- HTTP REST API endpoints
- WebSocket connections
- Static file serving
- CORS handling
- Request/response middleware
- Health checks and monitoring

**Key Responsibilities**:

- Request routing and validation
- Authentication and rate limiting
- Error handling and logging
- API documentation generation
- WebSocket connection management

### 2. TTS Manager

**Location**: `src/tts_manager.py`

Central orchestrator that coordinates all TTS operations:

```python
class TTSManager:
    def __init__(self):
        self.backends = {}
        self.cache_manager = CacheManager()
        self.queue_manager = QueueManager()
        self.config = settings

    async def synthesize(self, request: TTSRequest) -> TTSResponse:
        # 1. Check cache first
        # 2. Select optimal backend
        # 3. Queue request if needed
        # 4. Process and return result
        # 5. Cache result for future use
```

**Key Responsibilities**:

- Backend selection and fallback
- Request routing and load balancing
- Cache integration
- Performance optimization
- Error handling and recovery

### 3. Backend Manager

**Location**: `src/backends/`

Manages multiple TTS backend implementations:

```
src/backends/
├── __init__.py          # Backend registry
├── base.py              # Abstract base class
├── edge_tts.py          # Microsoft EdgeTTS
├── xtts.py              # XTTS (GPU-accelerated)
├── piper_tts.py         # Piper TTS (local)
├── azure_tts.py         # Azure Cognitive Services
└── openai_tts.py        # OpenAI TTS API
```

**Backend Interface**:

```python
class BaseTTSBackend:
    async def initialize(self) -> None:
        """Initialize backend resources"""

    async def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        """Convert text to speech"""

    async def get_voices(self) -> List[VoiceInfo]:
        """Get available voices"""

    async def health_check(self) -> BackendStatus:
        """Check backend health"""

    async def cleanup(self) -> None:
        """Clean up resources"""
```

### 4. Cache Manager

**Location**: `src/cache_manager.py`

Intelligent caching system supporting multiple storage backends:

```python
class CacheManager:
    def __init__(self):
        self.backend = self._create_cache_backend()

    async def get(self, key: str) -> Optional[bytes]:
        """Retrieve cached audio"""

    async def set(self, key: str, data: bytes, ttl: int = None) -> None:
        """Store audio in cache"""

    def _generate_key(self, request: TTSRequest) -> str:
        """Generate unique cache key"""
```

**Cache Backends**:

- **Memory Cache**: Fast, limited by RAM
- **Redis Cache**: Shared across instances
- **File Cache**: Persistent, disk-based storage

### 5. WebSocket Manager

**Location**: `src/websocket_manager.py`

Handles real-time WebSocket connections:

```python
class WebSocketManager:
    def __init__(self):
        self.active_connections = set()
        self.connection_handlers = {}

    async def connect(self, websocket: WebSocket) -> str:
        """Accept new WebSocket connection"""

    async def disconnect(self, connection_id: str) -> None:
        """Handle connection disconnect"""

    async def handle_message(self, connection_id: str, message: dict) -> None:
        """Process incoming WebSocket message"""
```

## Data Flow

### 1. REST API Request Flow

```
Client Request
     ↓
FastAPI Router
     ↓
Request Validation
     ↓
TTS Manager
     ↓
Cache Check ─────→ Cache Hit? → Return Cached Audio
     ↓ (Cache Miss)
Backend Selection
     ↓
Queue Management
     ↓
TTS Processing
     ↓
Cache Storage
     ↓
Response Generation
     ↓
Client Response
```

### 2. WebSocket Message Flow

```
WebSocket Message
     ↓
Message Parsing
     ↓
Request Validation
     ↓
TTS Manager
     ↓
Async Processing
     ↓
Result Notification
     ↓
WebSocket Response
```

### 3. Backend Selection Algorithm

```python
async def select_backend(self, request: TTSRequest) -> TTSBackend:
    """
    Backend selection strategy:
    1. Use requested backend if specified and available
    2. Check primary backend availability and load
    3. Try fallback backends in order
    4. Consider queue sizes and processing times
    5. Return best available backend
    """

    if request.backend and self._is_backend_available(request.backend):
        return self.backends[request.backend]

    # Load balancing logic
    available_backends = [b for b in self.backends.values() if b.is_available()]

    if not available_backends:
        raise NoBackendsAvailableError()

    # Select based on load and performance
    return min(available_backends, key=lambda b: b.get_load_score())
```

## Configuration System

**Location**: `src/config.py`

Centralized configuration management using Pydantic:

```python
class Settings(BaseSettings):
    # Server settings
    server: ServerConfig

    # TTS backend settings
    tts: TTSConfig

    # Audio processing settings
    audio: AudioConfig

    # Cache configuration
    cache: CacheConfig

    # Performance tuning
    performance: PerformanceConfig

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

## Storage Architecture

### 1. Model Storage

```
models/
├── piper/
│   ├── zh_CN-huayan-medium.onnx
│   ├── zh_CN-huayan-medium.onnx.json
│   └── voices.json
├── xtts/
│   ├── model.pth
│   ├── config.json
│   ├── vocab.json
│   └── speakers.pth
└── reference_voices/
    ├── speaker_01.wav
    └── speaker_02.wav
```

### 2. Cache Storage

```
cache/
├── memory/          # In-memory cache (Redis/local)
├── file/           # File-based cache
│   ├── audio/
│   │   ├── edge/
│   │   ├── xtts/
│   │   └── piper/
│   └── metadata/
└── temp/           # Temporary processing files
```

### 3. Log Storage

```
logs/
├── app.log         # Main application logs
├── access.log      # HTTP access logs
├── error.log       # Error-specific logs
├── performance.log # Performance metrics
└── debug.log       # Debug information
```

## Performance Architecture

### 1. Async Processing

```python
# Concurrent request handling
async def handle_multiple_requests(requests: List[TTSRequest]):
    tasks = []
    for request in requests:
        task = asyncio.create_task(process_tts_request(request))
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 2. Connection Pooling

```python
# HTTP connection pooling for cloud services
class HTTPPoolManager:
    def __init__(self):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                keepalive_timeout=300
            )
        )
```

### 3. GPU Resource Management

```python
# GPU memory and compute management
class GPUResourceManager:
    def __init__(self):
        self.device_pool = []
        self.memory_tracker = {}

    async def allocate_gpu_memory(self, size: int) -> Optional[torch.device]:
        """Allocate GPU memory for TTS processing"""

    async def release_gpu_memory(self, device: torch.device) -> None:
        """Release allocated GPU memory"""
```

## Security Architecture

### 1. Request Validation

```python
# Pydantic models for request validation
class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    voice: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9\-_]+$')
    backend: Optional[str] = Field(None, enum=['edge', 'xtts', 'piper'])
```

### 2. Rate Limiting

```python
# Rate limiting implementation
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)

    async def check_rate_limit(self, client_id: str) -> bool:
        """Check if client exceeds rate limit"""
```

### 3. Content Filtering

```python
# Content filtering for inappropriate text
class ContentFilter:
    def __init__(self):
        self.blocked_words = set()
        self.profanity_filter = ProfanityFilter()

    def is_content_safe(self, text: str) -> bool:
        """Check if text content is appropriate"""
```

## Monitoring and Observability

### 1. Health Checks

```python
# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": __version__
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed system health check"""
    return {
        "status": "healthy",
        "backends": await get_backend_status(),
        "cache": await get_cache_status(),
        "gpu": await get_gpu_status()
    }
```

### 2. Metrics Collection

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('tts_requests_total', 'Total TTS requests', ['backend', 'status'])
REQUEST_DURATION = Histogram('tts_request_duration_seconds', 'TTS request duration')
ACTIVE_CONNECTIONS = Gauge('tts_websocket_connections', 'Active WebSocket connections')
```

### 3. Logging Strategy

```python
# Structured logging
import structlog

logger = structlog.get_logger()

await logger.info(
    "TTS request processed",
    request_id=request_id,
    backend=backend_name,
    duration=processing_time,
    text_length=len(text),
    voice=voice_id,
    cached=was_cached
)
```

## Deployment Architecture

### 1. Docker Containerization

```dockerfile
# Multi-stage build for optimal image size
FROM python:3.11-slim as builder
# Build dependencies and models

FROM python:3.11-slim as runtime
# Runtime environment
COPY --from=builder /app /app
EXPOSE 8000
CMD ["python", "app.py"]
```

### 2. Horizontal Scaling

```yaml
# Docker Compose for scaling
version: "3.8"
services:
  tts-server:
    image: danmu-tts:latest
    ports:
      - "8000-8010:8000"
    environment:
      - BACKEND_MODE=worker
    deploy:
      replicas: 5

  load-balancer:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - tts-server
```

### 3. Resource Requirements

**Minimum Requirements**:

- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 10GB
- **Network**: 100Mbps

**Recommended for Production**:

- **CPU**: 16+ cores
- **RAM**: 32GB+
- **GPU**: NVIDIA RTX 4090 (24GB VRAM)
- **Storage**: 100GB+ SSD
- **Network**: 1Gbps+

## Extension Points

### 1. Custom TTS Backends

```python
# Custom backend implementation
class CustomTTSBackend(BaseTTSBackend):
    def __init__(self):
        super().__init__()
        self.name = "custom"

    async def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        # Custom TTS implementation
        pass
```

### 2. Custom Cache Backends

```python
# Custom cache implementation
class CustomCacheBackend(BaseCacheBackend):
    async def get(self, key: str) -> Optional[bytes]:
        # Custom cache retrieval
        pass

    async def set(self, key: str, data: bytes, ttl: int = None) -> None:
        # Custom cache storage
        pass
```

### 3. Plugin System

```python
# Plugin interface
class TTSPlugin:
    def __init__(self):
        self.name = ""
        self.version = ""

    async def pre_process(self, request: TTSRequest) -> TTSRequest:
        """Modify request before processing"""
        return request

    async def post_process(self, response: TTSResponse) -> TTSResponse:
        """Modify response after processing"""
        return response
```

This architecture provides a solid foundation for a scalable, maintainable, and extensible TTS service that can handle high-volume real-time processing while maintaining reliability and performance.
