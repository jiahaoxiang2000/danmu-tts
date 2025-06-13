# WebSocket API Reference

The Danmu TTS Server provides WebSocket support for real-time text-to-speech conversion, perfect for live streaming applications.

## Connection

### WebSocket Endpoint

```
ws://localhost:8000/ws
```

For secure connections:

```
wss://your-domain.com/ws
```

### Connection Example

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = function (event) {
  console.log("Connected to TTS WebSocket");
};

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

ws.onerror = function (error) {
  console.error("WebSocket error:", error);
};

ws.onclose = function (event) {
  console.log("WebSocket closed:", event.code, event.reason);
};
```

## Message Format

All WebSocket messages use JSON format.

### Request Message

```json
{
  "id": "unique-request-id",
  "type": "tts",
  "data": {
    "text": "你好，欢迎来到直播间！",
    "voice": "zh-CN-XiaoxiaoNeural",
    "backend": "edge",
    "quality": "medium",
    "format": "wav"
  }
}
```

### Response Message

```json
{
  "id": "unique-request-id",
  "type": "tts_response",
  "status": "success",
  "data": {
    "audio_data": "UklGRiQAAABXQVZF...",
    "metadata": {
      "backend": "edge",
      "voice": "zh-CN-XiaoxiaoNeural",
      "duration": 2.34,
      "sample_rate": 22050,
      "format": "wav"
    },
    "cached": false
  }
}
```

## Message Types

### TTS Request

Convert text to speech.

**Request:**

```json
{
  "id": "req_001",
  "type": "tts",
  "data": {
    "text": "Hello, world!",
    "voice": "zh-CN-XiaoxiaoNeural",
    "backend": "edge",
    "quality": "medium",
    "format": "wav",
    "sample_rate": 22050
  }
}
```

**Response:**

```json
{
  "id": "req_001",
  "type": "tts_response",
  "status": "success",
  "data": {
    "audio_data": "base64-encoded-audio",
    "metadata": {
      "duration": 1.5,
      "size_bytes": 66150
    }
  }
}
```

### Streaming TTS Request

For long texts, enable streaming to receive audio in chunks.

**Request:**

```json
{
  "id": "req_002",
  "type": "tts_stream",
  "data": {
    "text": "This is a very long text that will be processed in chunks...",
    "voice": "zh-CN-XiaoxiaoNeural",
    "chunk_size": 100
  }
}
```

**Response (multiple messages):**

```json
{
  "id": "req_002",
  "type": "tts_chunk",
  "status": "processing",
  "data": {
    "chunk_index": 0,
    "total_chunks": 3,
    "audio_data": "base64-chunk-1",
    "text_chunk": "This is a very long text that will be"
  }
}
```

```json
{
  "id": "req_002",
  "type": "tts_complete",
  "status": "success",
  "data": {
    "total_duration": 15.6,
    "chunks_sent": 3
  }
}
```

### Voice List Request

Get available voices.

**Request:**

```json
{
  "id": "req_003",
  "type": "get_voices",
  "data": {
    "backend": "edge",
    "language": "zh-CN"
  }
}
```

**Response:**

```json
{
  "id": "req_003",
  "type": "voices_response",
  "status": "success",
  "data": {
    "voices": [
      {
        "id": "zh-CN-XiaoxiaoNeural",
        "name": "Xiaoxiao",
        "language": "zh-CN",
        "gender": "female"
      }
    ]
  }
}
```

### Backend Status Request

Check backend availability and performance.

**Request:**

```json
{
  "id": "req_004",
  "type": "backend_status",
  "data": {
    "backend": "xtts"
  }
}
```

**Response:**

```json
{
  "id": "req_004",
  "type": "backend_status_response",
  "status": "success",
  "data": {
    "backend": "xtts",
    "available": true,
    "queue_size": 2,
    "average_processing_time": 1.8,
    "gpu_memory_usage": 0.45
  }
}
```

### Queue Status Request

Monitor processing queue.

**Request:**

```json
{
  "id": "req_005",
  "type": "queue_status"
}
```

**Response:**

```json
{
  "id": "req_005",
  "type": "queue_status_response",
  "status": "success",
  "data": {
    "total_queued": 5,
    "position": 2,
    "estimated_wait_time": 3.2,
    "queues": {
      "edge": { "size": 1, "processing": 1 },
      "xtts": { "size": 4, "processing": 1 }
    }
  }
}
```

### Cancel Request

Cancel a pending TTS request.

**Request:**

```json
{
  "id": "req_006",
  "type": "cancel",
  "data": {
    "request_id": "req_001"
  }
}
```

**Response:**

```json
{
  "id": "req_006",
  "type": "cancel_response",
  "status": "success",
  "data": {
    "cancelled": true,
    "request_id": "req_001"
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "id": "req_001",
  "type": "error",
  "status": "error",
  "error": {
    "code": "BACKEND_UNAVAILABLE",
    "message": "XTTS backend is currently unavailable",
    "details": {
      "backend": "xtts",
      "available_backends": ["edge", "piper"]
    }
  }
}
```

### Common Error Codes

- `INVALID_MESSAGE_FORMAT`: Invalid JSON or missing required fields
- `BACKEND_UNAVAILABLE`: Requested backend is not available
- `QUEUE_FULL`: Processing queue is at capacity
- `TEXT_TOO_LONG`: Text exceeds maximum length limit
- `VOICE_NOT_FOUND`: Specified voice is not available
- `RATE_LIMITED`: Too many requests from client
- `INTERNAL_ERROR`: Server-side processing error

## Connection Management

### Heartbeat

The server sends periodic heartbeat messages to keep the connection alive.

**Server Message:**

```json
{
  "type": "heartbeat",
  "timestamp": "2025-06-13T10:30:00Z"
}
```

**Client Response (optional):**

```json
{
  "type": "heartbeat_ack",
  "timestamp": "2025-06-13T10:30:00Z"
}
```

### Connection Limits

- **Maximum connections per IP**: 10
- **Maximum message rate**: 60 messages per minute
- **Maximum message size**: 1MB
- **Connection timeout**: 300 seconds (5 minutes) idle

### Reconnection Strategy

Implement exponential backoff for reconnections:

```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connect() {
  const ws = new WebSocket("ws://localhost:8000/ws");

  ws.onopen = function () {
    console.log("Connected");
    reconnectAttempts = 0;
  };

  ws.onclose = function (event) {
    if (reconnectAttempts < maxReconnectAttempts) {
      const delay = Math.pow(2, reconnectAttempts) * 1000;
      console.log(`Reconnecting in ${delay}ms...`);
      setTimeout(connect, delay);
      reconnectAttempts++;
    }
  };
}
```

## Client Examples

### Python Client

```python
import asyncio
import websockets
import json
import base64

class DanmuTTSWebSocketClient:
    def __init__(self, uri="ws://localhost:8000/ws"):
        self.uri = uri
        self.websocket = None
        self.request_id = 0

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print("Connected to TTS WebSocket")

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()

    def _generate_id(self):
        self.request_id += 1
        return f"req_{self.request_id}"

    async def synthesize(self, text, voice=None, backend=None):
        request = {
            "id": self._generate_id(),
            "type": "tts",
            "data": {
                "text": text,
                "voice": voice,
                "backend": backend
            }
        }

        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        return json.loads(response)

    async def get_voices(self, backend=None, language=None):
        request = {
            "id": self._generate_id(),
            "type": "get_voices",
            "data": {
                "backend": backend,
                "language": language
            }
        }

        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        return json.loads(response)

# Usage example
async def main():
    client = DanmuTTSWebSocketClient()
    await client.connect()

    try:
        # Get voices
        voices_response = await client.get_voices(language="zh-CN")
        print("Available voices:", voices_response["data"]["voices"])

        # Synthesize speech
        result = await client.synthesize(
            text="你好，这是WebSocket测试",
            voice="zh-CN-XiaoxiaoNeural",
            backend="edge"
        )

        if result["status"] == "success":
            audio_data = base64.b64decode(result["data"]["audio_data"])
            with open("output.wav", "wb") as f:
                f.write(audio_data)
            print("Audio saved to output.wav")

    finally:
        await client.disconnect()

asyncio.run(main())
```

### JavaScript Client

```javascript
class DanmuTTSWebSocketClient {
  constructor(uri = "ws://localhost:8000/ws") {
    this.uri = uri;
    this.ws = null;
    this.requestId = 0;
    this.pendingRequests = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.uri);

      this.ws.onopen = () => {
        console.log("Connected to TTS WebSocket");
        resolve();
      };

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this._handleMessage(message);
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        reject(error);
      };

      this.ws.onclose = (event) => {
        console.log("WebSocket closed:", event.code, event.reason);
      };
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }

  _generateId() {
    return `req_${++this.requestId}`;
  }

  _handleMessage(message) {
    if (message.type === "heartbeat") {
      // Respond to heartbeat
      this.ws.send(
        JSON.stringify({
          type: "heartbeat_ack",
          timestamp: message.timestamp,
        })
      );
      return;
    }

    const request = this.pendingRequests.get(message.id);
    if (request) {
      if (message.status === "success") {
        request.resolve(message);
      } else {
        request.reject(new Error(message.error?.message || "Request failed"));
      }
      this.pendingRequests.delete(message.id);
    }
  }

  async synthesize(text, options = {}) {
    const id = this._generateId();
    const request = {
      id,
      type: "tts",
      data: {
        text,
        ...options,
      },
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      this.ws.send(JSON.stringify(request));
    });
  }

  async getVoices(options = {}) {
    const id = this._generateId();
    const request = {
      id,
      type: "get_voices",
      data: options,
    };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      this.ws.send(JSON.stringify(request));
    });
  }
}

// Usage example
async function main() {
  const client = new DanmuTTSWebSocketClient();

  try {
    await client.connect();

    // Get available voices
    const voicesResponse = await client.getVoices({ language: "zh-CN" });
    console.log("Available voices:", voicesResponse.data.voices);

    // Synthesize speech
    const result = await client.synthesize("你好，世界！", {
      voice: "zh-CN-XiaoxiaoNeural",
      backend: "edge",
    });

    // Create audio element and play
    const audioData = result.data.audio_data;
    const audioBlob = new Blob(
      [Uint8Array.from(atob(audioData), (c) => c.charCodeAt(0))],
      { type: "audio/wav" }
    );

    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
  } catch (error) {
    console.error("Error:", error);
  } finally {
    client.disconnect();
  }
}

main();
```

### Real-time Danmu Processing

```javascript
class DanmuProcessor {
  constructor() {
    this.ttsClient = new DanmuTTSWebSocketClient();
    this.audioQueue = [];
    this.isPlaying = false;
  }

  async initialize() {
    await this.ttsClient.connect();
  }

  async processDanmu(username, message) {
    // Filter inappropriate content
    if (this._isFiltered(message)) {
      return;
    }

    // Format message for TTS
    const ttsText = `${username}说：${message}`;

    try {
      const result = await this.ttsClient.synthesize(ttsText, {
        voice: "zh-CN-XiaoxiaoNeural",
        backend: "edge",
        quality: "medium",
      });

      if (result.status === "success") {
        this._queueAudio(result.data.audio_data);
      }
    } catch (error) {
      console.error("TTS processing failed:", error);
    }
  }

  _isFiltered(message) {
    // Implement content filtering logic
    const blockedWords = ["spam", "inappropriate"];
    return blockedWords.some((word) => message.includes(word));
  }

  _queueAudio(audioData) {
    this.audioQueue.push(audioData);
    if (!this.isPlaying) {
      this._playNext();
    }
  }

  _playNext() {
    if (this.audioQueue.length === 0) {
      this.isPlaying = false;
      return;
    }

    this.isPlaying = true;
    const audioData = this.audioQueue.shift();

    // Create and play audio
    const audioBlob = new Blob(
      [Uint8Array.from(atob(audioData), (c) => c.charCodeAt(0))],
      { type: "audio/wav" }
    );

    const audio = new Audio(URL.createObjectURL(audioBlob));
    audio.onended = () => this._playNext();
    audio.play();
  }
}

// Usage in live streaming application
const danmuProcessor = new DanmuProcessor();
await danmuProcessor.initialize();

// Process incoming danmu messages
danmuProcessor.processDanmu("用户123", "主播好棒！");
danmuProcessor.processDanmu("观众456", "来个才艺表演吧");
```

## Best Practices

1. **Request ID Management**: Always use unique request IDs to match responses
2. **Error Handling**: Implement proper error handling for all message types
3. **Connection Management**: Use heartbeat and reconnection logic
4. **Rate Limiting**: Respect server rate limits to avoid disconnection
5. **Resource Cleanup**: Properly close connections and clean up audio resources
6. **Content Filtering**: Filter inappropriate content before TTS processing
7. **Queue Management**: Implement audio queue for smooth playback experience
