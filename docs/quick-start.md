# Quick Start Guide

Get the Danmu TTS Server running in just a few minutes with this quick start guide.

## Prerequisites

- Linux system (Ubuntu 20.04+ recommended)
- Python 3.8+
- 8GB+ RAM
- Internet connection for cloud TTS services

## 1. Installation

### Option A: One-Command Setup

```bash
curl -sSL https://raw.githubusercontent.com/your-repo/danmu-tts/main/setup.sh | bash
```

### Option B: Manual Setup

```bash
# Clone repository
git clone <your-repo-url>
cd danmu-tts

# Run setup script
./setup.sh

# Start server
./start_server.sh
```

## 2. Verify Installation

Once the server starts, you should see:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Starting TTS Server...
INFO:     TTS Server started successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 3. Test the API

### REST API Test

```bash
# Simple TTS request
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，欢迎使用弹幕TTS服务器！",
    "voice": "zh-CN-XiaoxiaoNeural"
  }'
```

### Web Interface Test

Open your browser and navigate to: `http://localhost:8000`

You should see a simple web interface where you can:

- Enter text to convert to speech
- Select different voices
- Choose TTS backends
- Play generated audio

## 4. Basic Usage Examples

### Example 1: Generate Speech Audio

```python
import requests
import base64
import io
from pydub import AudioSegment
from pydub.playback import play

# TTS request
response = requests.post("http://localhost:8000/tts", json={
    "text": "欢迎来到直播间！",
    "voice": "zh-CN-XiaoxiaoNeural",
    "backend": "edge"
})

if response.status_code == 200:
    data = response.json()
    audio_data = base64.b64decode(data["audio_data"])

    # Play audio
    audio = AudioSegment.from_wav(io.BytesIO(audio_data))
    play(audio)
```

### Example 2: WebSocket Connection

```python
import asyncio
import websocket
import json

async def websocket_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send TTS request
        request = {
            "text": "实时语音合成测试",
            "voice": "zh-CN-XiaoxiaoNeural"
        }
        await websocket.send(json.dumps(request))

        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received audio data: {len(data['audio_data'])} bytes")

asyncio.run(websocket_client())
```

### Example 3: Stream Audio

```python
import requests

# Stream audio response
response = requests.get("http://localhost:8000/stream", params={
    "text": "这是一个流式音频测试",
    "voice": "zh-CN-XiaoxiaoNeural"
}, stream=True)

# Save to file
with open("output.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
```

## 5. Available Voices

### List Available Voices

```bash
curl "http://localhost:8000/voices"
```

### Common Chinese Voices (EdgeTTS)

- `zh-CN-XiaoxiaoNeural` - Female, standard Chinese
- `zh-CN-YunxiNeural` - Male, standard Chinese
- `zh-CN-YunyangNeural` - Male, news style
- `zh-CN-XiaochenNeural` - Female, cheerful
- `zh-CN-XiaohanNeural` - Female, gentle

## 6. Configuration

### Basic Configuration

Edit `config.yaml` to customize:

```yaml
server:
  host: "0.0.0.0"
  port: 8000

tts:
  primary_backend: "edge" # Fast and reliable
  fallback_backends: ["piper"]

  backends:
    edge:
      enabled: true
      default_voice: "zh-CN-XiaoxiaoNeural"
```

### Enable GPU Acceleration (Optional)

```yaml
tts:
  backends:
    xtts:
      enabled: true
      device: "cuda" # Use GPU
```

## 7. Integration Examples

### Danmu (Bullet Comments) Processing

```python
# Example for live streaming danmu processing
import asyncio
import websockets
import json

class DanmuTTS:
    def __init__(self):
        self.tts_url = "ws://localhost:8000/ws"

    async def process_danmu(self, username, message):
        # Filter and prepare text
        tts_text = f"{username}说：{message}"

        async with websockets.connect(self.tts_url) as websocket:
            request = {
                "text": tts_text,
                "voice": "zh-CN-XiaoxiaoNeural",
                "quality": "medium"
            }
            await websocket.send(json.dumps(request))
            response = await websocket.recv()

            # Process audio response
            data = json.loads(response)
            return data["audio_data"]

# Usage
danmu_tts = DanmuTTS()
audio = await danmu_tts.process_danmu("用户123", "主播好帅！")
```

### OBS Integration

For OBS Studio integration, you can use the audio stream endpoint:

```
http://localhost:8000/stream?text=你的文本&voice=zh-CN-XiaoxiaoNeural
```

## 8. Performance Tips

### For Better Performance

1. **Enable caching**:

   ```yaml
   cache:
     enabled: true
     max_size: 1000
   ```

2. **Use GPU acceleration**:

   ```yaml
   tts:
     backends:
       xtts:
         device: "cuda"
   ```

3. **Adjust audio quality**:
   ```yaml
   audio:
     quality: "medium" # Use "low" for faster processing
   ```

## 9. Common Issues

### Server Won't Start

```bash
# Check if port is in use
sudo lsof -i :8000

# Check logs
tail -f logs/app.log
```

### Audio Quality Issues

- Try different voices with `/voices` endpoint
- Adjust audio quality in config.yaml
- Use higher quality backends (XTTS > EdgeTTS > Piper)

### Performance Issues

- Enable GPU acceleration
- Reduce audio quality for faster processing
- Increase cache size

## 10. Next Steps

Now that you have the server running:

1. **Read the API documentation**: [REST API Reference](api/rest-api.md)
2. **Explore backend options**: [Backend Engines](../README.md#backend-engines)
3. **Optimize performance**: [Performance Tuning](advanced/performance.md)
4. **Deploy to production**: [Production Setup](deployment/production.md)

## Support

If you encounter issues:

- Check the [troubleshooting guide](development/debugging.md)
- Review logs in `logs/app.log`
- Run environment check: `python check_env.py`
- Open an issue on GitHub with detailed error information
