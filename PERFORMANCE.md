# Performance Optimization Guide

## GPU Memory Management

### NVIDIA RTX 4090 Optimization

Your RTX 4090 has 24GB VRAM, which is excellent for TTS. Here's how to optimize:

```yaml
# config.yaml optimizations
performance:
  gpu:
    enabled: true
    device: "cuda:0"
    memory_fraction: 0.7 # Use 70% of 24GB = ~17GB

  cache:
    enabled: true
    max_size_mb: 2048 # 2GB cache

  queue:
    max_concurrent: 8 # Process 8 requests simultaneously
```

### Backend Selection Strategy

1. **Edge TTS** (Fastest, Free)

   - Latency: ~200-500ms
   - Quality: Good
   - Cost: Free
   - Use for: Real-time chat, high volume

2. **Piper TTS** (Fast, Local)

   - Latency: ~100-300ms
   - Quality: Very Good
   - Cost: Local compute only
   - Use for: Medium quality, privacy

3. **XTTS** (Highest Quality)
   - Latency: ~1-3 seconds
   - Quality: Excellent
   - Cost: GPU compute
   - Use for: Special announcements, high-quality content

## Cost Optimization

### Electricity Cost Calculation (RTX 4090)

- Idle: ~30W
- Light load (Edge TTS): ~50W
- Heavy load (XTTS): ~400W

**Daily cost estimates (at $0.12/kWh):**

- Idle: $0.09/day
- Edge TTS only: $0.14/day
- Mixed usage: $0.50/day
- Heavy XTTS: $1.15/day

### Recommended Settings for Cost Control

```yaml
# Balanced performance/cost config
tts:
  primary_backend: "edge"
  fallback_backends: ["piper"]

  backends:
    xtts:
      enabled: true
      # Only use for special cases
      max_requests_per_hour: 50

performance:
  gpu:
    memory_fraction: 0.5 # Reduce power consumption

  cache:
    enabled: true
    max_size_mb: 1024 # Aggressive caching
    ttl_seconds: 7200 # Keep cache longer
```

## Live Streaming Integration

### For OBS Studio

```python
# obs_integration.py
import asyncio
import websockets
import json

async def connect_to_tts():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send danmu text
        await websocket.send(json.dumps({
            "type": "tts",
            "text": "观众弹幕内容",
            "voice": "zh-CN-XiaoxiaoNeural"
        }))

        # Receive audio and play
        while True:
            message = await websocket.recv()
            if isinstance(message, bytes):
                # Play audio chunk
                pass
```

### For StreamLabs

Add webhook endpoint to receive donations/follows and convert to speech.

## Monitoring and Alerts

### Set up monitoring for:

1. GPU temperature (keep under 80°C)
2. GPU memory usage
3. Request queue length
4. Cache hit rate
5. Response latency

### Example monitoring script:

```python
import psutil
import GPUtil

def check_system_health():
    # GPU stats
    gpus = GPUtil.getGPUs()
    gpu = gpus[0]

    if gpu.temperature > 80:
        print("⚠️ GPU temperature high:", gpu.temperature)

    if gpu.memoryUtil > 0.9:
        print("⚠️ GPU memory high:", gpu.memoryUtil)

    # CPU and RAM
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent

    print(f"💻 CPU: {cpu_percent}%, RAM: {memory_percent}%")
    print(f"🎮 GPU: {gpu.temperature}°C, VRAM: {gpu.memoryUtil:.1%}")
```

## Scaling Strategies

### Horizontal Scaling

- Run multiple TTS server instances
- Use load balancer (nginx)
- Distribute by backend type

### Vertical Scaling

- Increase concurrent requests
- Add more RAM for caching
- Use faster storage (NVMe SSD)

## Best Practices

1. **Cache Everything**: Enable aggressive caching for repeated content
2. **Smart Backend Selection**: Use Edge TTS for chat, XTTS for highlights
3. **Queue Management**: Set appropriate timeouts and limits
4. **Monitor Resources**: Keep GPU usage under 80%
5. **Batch Processing**: Group similar requests when possible
