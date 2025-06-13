# EdgeTTS Backend

EdgeTTS is Microsoft's cloud-based text-to-speech service that provides high-quality voices with minimal latency. It's the recommended primary backend for most use cases due to its reliability and speed.

## Overview

- **Type**: Cloud-based TTS service
- **Quality**: High (Neural voices)
- **Speed**: Very fast (typically < 1 second)
- **Cost**: Free (with usage limits)
- **Languages**: 100+ languages and variants
- **Voices**: 400+ neural voices

## Features

### Advantages

- **Fast processing**: Sub-second response times
- **High quality**: Neural voice synthesis
- **No local resources**: No GPU/CPU intensive processing
- **Large voice selection**: Hundreds of voices available
- **Reliable**: Backed by Microsoft's infrastructure
- **Free to use**: No API keys required

### Limitations

- **Internet dependency**: Requires stable internet connection
- **Rate limits**: Microsoft may impose usage limits
- **Privacy**: Text is processed on Microsoft servers
- **Limited customization**: Cannot adjust fine-grained voice parameters

## Configuration

### Basic Configuration

```yaml
tts:
  backends:
    edge:
      enabled: true
      default_voice: "zh-CN-XiaoxiaoNeural"
      rate: "+0%"
      volume: "+0%"
      pitch: "+0Hz"
```

### Advanced Configuration

```yaml
tts:
  backends:
    edge:
      enabled: true

      # Voice settings
      default_voice: "zh-CN-XiaoxiaoNeural"
      fallback_voices: ["zh-CN-YunxiNeural", "zh-CN-YunyangNeural"]

      # Speech parameters
      rate: "+0%" # -50% to +200%
      volume: "+0%" # -50% to +200%
      pitch: "+0Hz" # ±50Hz

      # Quality settings
      output_format: "audio-24khz-48kbitrate-mono-mp3"

      # Network settings
      timeout: 10 # Request timeout in seconds
      max_retries: 3 # Number of retry attempts
      retry_delay: 1 # Delay between retries

      # Connection settings
      max_connections: 10 # Maximum concurrent connections
      connection_pool_size: 5 # Connection pool size

      # Proxy settings (if needed)
      proxy: null # HTTP proxy URL
      proxy_auth: null # Proxy authentication
```

## Available Voices

### Chinese Voices

#### Standard Chinese (zh-CN)

- **zh-CN-XiaoxiaoNeural** - Female, standard Chinese, friendly
- **zh-CN-YunxiNeural** - Male, standard Chinese, calm
- **zh-CN-YunyangNeural** - Male, news broadcaster style
- **zh-CN-XiaochenNeural** - Female, cheerful and energetic
- **zh-CN-XiaohanNeural** - Female, gentle and warm
- **zh-CN-XiaomengNeural** - Female, cute and childlike
- **zh-CN-XiaomoNeural** - Female, sweet and pleasant
- **zh-CN-XiaoxuanNeural** - Female, literary and elegant
- **zh-CN-XiaoruiNeural** - Female, confident and professional
- **zh-CN-XiaoyanNeural** - Female, storytelling style

#### Regional Variants

- **zh-HK-HiuGaaiNeural** - Female, Hong Kong Cantonese
- **zh-HK-WanLungNeural** - Male, Hong Kong Cantonese
- **zh-TW-HsiaoChenNeural** - Female, Taiwan Mandarin
- **zh-TW-HsiaoYuNeural** - Female, Taiwan Mandarin

### English Voices

#### US English (en-US)

- **en-US-AriaNeural** - Female, conversational
- **en-US-JennyNeural** - Female, customer service
- **en-US-GuyNeural** - Male, conversational
- **en-US-DavisNeural** - Male, professional

#### Other English Variants

- **en-GB-SoniaNeural** - Female, British English
- **en-AU-NatashaNeural** - Female, Australian English
- **en-CA-ClaraNeural** - Female, Canadian English

### Other Languages

- **ja-JP-NanamiNeural** - Japanese female
- **ko-KR-SunHiNeural** - Korean female
- **fr-FR-DeniseNeural** - French female
- **de-DE-KatjaNeural** - German female
- **es-ES-ElviraNeural** - Spanish female

## Voice Parameters

### Rate Control

Controls speaking speed:

```yaml
rate: "+20%"    # 20% faster
rate: "-30%"    # 30% slower
rate: "+0%"     # Normal speed
```

Range: -50% to +200%

### Volume Control

Controls voice volume:

```yaml
volume: "+10%"  # 10% louder
volume: "-20%"  # 20% quieter
volume: "+0%"   # Normal volume
```

Range: -50% to +200%

### Pitch Control

Controls voice pitch:

```yaml
pitch: "+5Hz"   # 5Hz higher
pitch: "-10Hz"  # 10Hz lower
pitch: "+0Hz"   # Normal pitch
```

Range: ±50Hz

## Output Formats

EdgeTTS supports multiple audio formats:

```yaml
output_format: "audio-24khz-48kbitrate-mono-mp3"    # Default
output_format: "audio-24khz-96kbitrate-mono-mp3"    # Higher quality MP3
output_format: "audio-48khz-192kbitrate-mono-mp3"   # Highest quality MP3
output_format: "riff-24khz-16bit-mono-pcm"          # WAV format
output_format: "audio-24khz-16bit-mono-opus"        # Opus format
```

## Usage Examples

### Basic Usage

```python
import asyncio
from src.backends.edge_tts import EdgeTTSBackend

async def example():
    backend = EdgeTTSBackend()
    await backend.initialize()

    # Simple synthesis
    audio_data = await backend.synthesize(
        text="你好，欢迎使用EdgeTTS！",
        voice="zh-CN-XiaoxiaoNeural"
    )

    # Save audio
    with open("output.mp3", "wb") as f:
        f.write(audio_data)

asyncio.run(example())
```

### Advanced Usage with Parameters

```python
async def advanced_example():
    backend = EdgeTTSBackend()
    await backend.initialize()

    # Synthesis with custom parameters
    audio_data = await backend.synthesize(
        text="这是一个高级的语音合成示例",
        voice="zh-CN-XiaoxiaoNeural",
        rate="+20%",
        volume="+10%",
        pitch="+5Hz"
    )

    return audio_data
```

### Voice Selection

```python
async def voice_example():
    backend = EdgeTTSBackend()

    # Get available voices
    voices = await backend.get_voices()
    chinese_voices = [v for v in voices if v.language.startswith('zh')]

    print("Available Chinese voices:")
    for voice in chinese_voices:
        print(f"- {voice.id}: {voice.name} ({voice.gender})")

    # Use specific voice
    audio = await backend.synthesize(
        text="测试语音",
        voice="zh-CN-YunxiNeural"  # Male voice
    )
```

## Performance Optimization

### Connection Pooling

```yaml
edge:
  # Use connection pooling for better performance
  max_connections: 10
  connection_pool_size: 5
  keep_alive: true
```

### Caching Strategy

```python
class OptimizedEdgeTTS:
    def __init__(self):
        self.cache = {}

    async def synthesize_cached(self, text, voice):
        cache_key = f"{voice}:{hash(text)}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        audio_data = await self.backend.synthesize(text, voice)
        self.cache[cache_key] = audio_data
        return audio_data
```

### Batch Processing

```python
async def batch_synthesize(texts, voice="zh-CN-XiaoxiaoNeural"):
    backend = EdgeTTSBackend()
    tasks = []

    for text in texts:
        task = backend.synthesize(text, voice)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

## Error Handling

### Common Errors

1. **Network connectivity issues**
2. **Rate limiting**
3. **Invalid voice parameters**
4. **Service unavailability**

### Error Handling Example

```python
async def robust_synthesis(text, voice):
    backend = EdgeTTSBackend()
    max_retries = 3

    for attempt in range(max_retries):
        try:
            return await backend.synthesize(text, voice)
        except NetworkError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except InvalidVoiceError:
            # Try fallback voice
            voice = "zh-CN-XiaoxiaoNeural"
            continue
```

## Integration Examples

### Danmu Processing

```python
class DanmuEdgeTTS:
    def __init__(self):
        self.backend = EdgeTTSBackend()
        self.voice_rotation = [
            "zh-CN-XiaoxiaoNeural",
            "zh-CN-YunxiNeural",
            "zh-CN-XiaochenNeural"
        ]
        self.current_voice = 0

    async def process_danmu(self, username, message):
        # Rotate voices for variety
        voice = self.voice_rotation[self.current_voice]
        self.current_voice = (self.current_voice + 1) % len(self.voice_rotation)

        # Format text
        tts_text = f"{username}说：{message}"

        # Synthesize with EdgeTTS
        try:
            audio_data = await self.backend.synthesize(
                text=tts_text,
                voice=voice,
                rate="+10%"  # Slightly faster for live streaming
            )
            return audio_data
        except Exception as e:
            print(f"EdgeTTS failed: {e}")
            return None
```

### Real-time Streaming

```python
import asyncio
from asyncio import Queue

class StreamingEdgeTTS:
    def __init__(self):
        self.backend = EdgeTTSBackend()
        self.request_queue = Queue()
        self.is_processing = False

    async def start_processing(self):
        self.is_processing = True
        while self.is_processing:
            try:
                request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=1.0
                )
                await self._process_request(request)
            except asyncio.TimeoutError:
                continue

    async def _process_request(self, request):
        text, voice, callback = request
        try:
            audio_data = await self.backend.synthesize(text, voice)
            await callback(audio_data)
        except Exception as e:
            await callback(None, error=str(e))

    async def synthesize_async(self, text, voice, callback):
        await self.request_queue.put((text, voice, callback))
```

## Monitoring and Debugging

### Performance Metrics

```python
import time
from collections import defaultdict

class EdgeTTSMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)

    async def monitored_synthesize(self, text, voice):
        start_time = time.time()

        try:
            audio_data = await self.backend.synthesize(text, voice)
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
            audio_data = None

        duration = time.time() - start_time

        self.metrics['requests'].append({
            'timestamp': start_time,
            'duration': duration,
            'success': success,
            'error': error,
            'text_length': len(text),
            'voice': voice
        })

        return audio_data

    def get_stats(self):
        requests = self.metrics['requests']
        if not requests:
            return {}

        successful = [r for r in requests if r['success']]

        return {
            'total_requests': len(requests),
            'successful_requests': len(successful),
            'success_rate': len(successful) / len(requests),
            'average_duration': sum(r['duration'] for r in successful) / len(successful) if successful else 0,
            'requests_per_minute': len([r for r in requests if time.time() - r['timestamp'] < 60])
        }
```

## Troubleshooting

### Common Issues

1. **Connection timeouts**

   - Check internet connectivity
   - Increase timeout values
   - Use retry logic

2. **Audio quality issues**

   - Try different output formats
   - Adjust voice parameters
   - Check for network packet loss

3. **Rate limiting**

   - Implement request throttling
   - Use multiple IP addresses if needed
   - Monitor usage patterns

4. **Voice not available**
   - Check voice ID spelling
   - Use voice list endpoint to verify
   - Implement fallback voices

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger('edge_tts').setLevel(logging.DEBUG)

# Test connectivity
async def test_edge_connectivity():
    backend = EdgeTTSBackend()

    try:
        # Simple test
        audio = await backend.synthesize("test", "zh-CN-XiaoxiaoNeural")
        print("EdgeTTS is working correctly")
        return True
    except Exception as e:
        print(f"EdgeTTS test failed: {e}")
        return False
```

## Best Practices

1. **Use appropriate voices** for your content language
2. **Implement caching** for frequently used phrases
3. **Handle errors gracefully** with fallback options
4. **Monitor usage** to avoid rate limits
5. **Use connection pooling** for better performance
6. **Test voice quality** before production deployment
7. **Implement request throttling** for high-volume usage
