# Configuration Guide

This guide covers all configuration options for the Danmu TTS Server.

## Configuration File

The main configuration file is `config.yaml` in the project root. All settings can be customized to fit your specific needs.

## Server Configuration

### Basic Server Settings

```yaml
server:
  host: "0.0.0.0" # Bind to all interfaces
  port: 8000 # Server port
  debug: false # Enable debug mode
  cors_origins: ["*"] # CORS allowed origins
  max_workers: 4 # Number of worker processes
```

### Advanced Server Settings

```yaml
server:
  # Request limits
  max_request_size: 10485760 # 10MB max request size
  timeout: 30 # Request timeout in seconds

  # SSL/TLS (for production)
  ssl_keyfile: null
  ssl_certfile: null

  # Logging
  log_level: "INFO" # DEBUG, INFO, WARNING, ERROR
  log_file: "logs/app.log" # Log file path
```

## TTS Backend Configuration

### Backend Selection Strategy

```yaml
tts:
  # Primary backend (first choice)
  primary_backend: "edge"

  # Fallback backends (in order of preference)
  fallback_backends: ["piper", "xtts"]

  # Automatic backend selection based on load
  auto_selection: true

  # Maximum concurrent requests per backend
  max_concurrent_requests: 5
```

### EdgeTTS Configuration

Fast, free, cloud-based TTS using Microsoft's service.

```yaml
tts:
  backends:
    edge:
      enabled: true
      default_voice: "zh-CN-XiaoxiaoNeural"

      # Voice parameters
      rate: "+0%" # Speech rate (-50% to +200%)
      volume: "+0%" # Volume (-50% to +200%)
      pitch: "+0Hz" # Pitch adjustment

      # Quality settings
      quality: "high" # low, medium, high

      # Request limits
      timeout: 10 # Request timeout
      max_retries: 3 # Retry attempts

      # Proxy settings (if needed)
      proxy: null # HTTP proxy URL
```

### Piper TTS Configuration

Local, lightweight TTS engine.

```yaml
tts:
  backends:
    piper:
      enabled: true
      model_path: "./models/piper"
      default_voice: "zh_CN-huayan-medium"

      # Model settings
      model_variants:
        - "zh_CN-huayan-medium"
        - "zh_CN-huayan-low"

      # Performance settings
      num_threads: 4 # CPU threads to use
      sentence_silence: 0.2 # Silence between sentences

      # Quality settings
      noise_scale: 0.667 # Voice variation
      noise_scale_w: 0.8 # Pronunciation variation
      length_scale: 1.0 # Speaking speed
```

### XTTS Configuration

High-quality, GPU-accelerated TTS.

```yaml
tts:
  backends:
    xtts:
      enabled: true
      model_path: "./models/xtts"

      # Hardware settings
      device: "cuda" # cuda, cpu, auto
      gpu_id: 0 # GPU device ID

      # Performance settings
      max_batch_size: 4 # Batch size for GPU
      enable_deepspeed: false # DeepSpeed optimization
      low_vram_mode: false # For GPUs with <8GB VRAM

      # Generation settings
      temperature: 0.7 # Creativity (0.0-1.0)
      repetition_penalty: 1.1 # Avoid repetition
      length_penalty: 1.0 # Sequence length preference

      # Voice cloning
      enable_voice_cloning: true
      reference_audio_path: "./reference_voices"

      # Quality settings
      sample_rate: 24000 # Audio sample rate
      gpt_batch_size: 1 # GPT model batch size
```

### Azure TTS Configuration

Microsoft Azure Cognitive Services TTS.

```yaml
tts:
  backends:
    azure:
      enabled: false
      subscription_key: "your-azure-key"
      region: "eastus"

      # Voice settings
      default_voice: "zh-CN-XiaoxiaoNeural"

      # Audio format
      audio_format: "riff-24khz-16bit-mono-pcm"

      # Request settings
      timeout: 30
      max_retries: 3
```

### OpenAI TTS Configuration

OpenAI's text-to-speech API.

```yaml
tts:
  backends:
    openai:
      enabled: false
      api_key: "your-openai-key"
      model: "tts-1" # tts-1, tts-1-hd

      # Voice settings
      default_voice: "alloy" # alloy, echo, fable, onyx, nova, shimmer

      # Quality settings
      quality: "standard" # standard, hd
      speed: 1.0 # 0.25 to 4.0

      # Request settings
      timeout: 30
      max_chunk_size: 4096 # Max characters per request
```

## Audio Configuration

### Output Settings

```yaml
audio:
  # Default audio format
  sample_rate: 22050 # 16000, 22050, 44100, 48000
  format: "wav" # wav, mp3, ogg
  channels: 1 # 1 (mono), 2 (stereo)
  bit_depth: 16 # 16, 24, 32

  # Quality presets
  quality: "medium" # low, medium, high, ultra

  # Post-processing
  normalize_audio: true # Normalize volume levels
  remove_silence: false # Remove leading/trailing silence

  # Encoding settings
  mp3_bitrate: 128 # MP3 bitrate (kbps)
  ogg_quality: 5 # OGG quality (0-10)
```

### Quality Presets

```yaml
audio:
  quality_presets:
    low:
      sample_rate: 16000
      bit_depth: 16
      mp3_bitrate: 64
    medium:
      sample_rate: 22050
      bit_depth: 16
      mp3_bitrate: 128
    high:
      sample_rate: 44100
      bit_depth: 16
      mp3_bitrate: 192
    ultra:
      sample_rate: 48000
      bit_depth: 24
      mp3_bitrate: 320
```

## Caching Configuration

### Cache Settings

```yaml
cache:
  enabled: true

  # Cache backend
  backend: "memory" # memory, redis, file

  # Memory cache settings
  max_size: 1000 # Maximum cached items
  max_memory_mb: 512 # Max memory usage (MB)

  # File cache settings
  cache_dir: "./cache" # Cache directory
  max_file_size_mb: 50 # Max individual file size
  cleanup_interval: 3600 # Cleanup interval (seconds)

  # Redis cache settings
  redis_url: "redis://localhost:6379"
  redis_db: 0
  redis_prefix: "danmu_tts:"

  # Cache TTL (time to live)
  default_ttl: 86400 # 24 hours
  voice_ttl: 604800 # 7 days for voice samples
```

### Cache Strategies

```yaml
cache:
  # Cache key generation
  include_backend: true # Include backend in cache key
  include_voice: true # Include voice in cache key
  include_quality: true # Include quality in cache key

  # Cache behavior
  preload_common: true # Preload common phrases
  async_write: true # Asynchronous cache writes
  compression: true # Compress cached audio

  # Cache warming
  warmup_phrases: ["欢迎来到直播间", "感谢关注", "谢谢打赏"]
```

## Performance Configuration

### Resource Limits

```yaml
performance:
  # CPU settings
  max_cpu_cores: 4 # Maximum CPU cores to use
  cpu_affinity: null # CPU affinity (core numbers)

  # Memory settings
  max_memory_mb: 2048 # Maximum memory usage
  memory_pool_size: 256 # Memory pool size

  # GPU settings
  gpu_memory_fraction: 0.8 # GPU memory fraction
  allow_gpu_growth: true # Allow GPU memory growth

  # Request processing
  request_queue_size: 100 # Maximum queued requests
  batch_processing: true # Enable batch processing
  batch_timeout: 0.1 # Batch timeout (seconds)
```

### Optimization Settings

```yaml
performance:
  # Threading
  enable_threading: true
  thread_pool_size: 8

  # Async processing
  async_processing: true
  event_loop_policy: "uvloop" # uvloop, asyncio

  # Model optimization
  model_warmup: true # Warm up models on startup
  jit_compilation: true # JIT compile models
  half_precision: false # Use FP16 (if supported)
```

## Security Configuration

### Authentication

```yaml
security:
  # API key authentication
  require_api_key: false
  api_keys: [] # List of valid API keys

  # Rate limiting
  rate_limiting:
    enabled: true
    requests_per_minute: 60
    requests_per_hour: 1000

  # Request validation
  max_text_length: 1000 # Maximum text length
  allowed_languages: ["zh", "en"] # Allowed languages

  # Content filtering
  content_filter:
    enabled: true
    blocked_words: [] # List of blocked words
    profanity_filter: true # Enable profanity filtering
```

### Network Security

```yaml
security:
  # CORS settings
  cors:
    allow_origins: ["*"]
    allow_methods: ["GET", "POST"]
    allow_headers: ["*"]

  # Request size limits
  max_request_size: 10485760 # 10MB
  max_file_upload: 5242880 # 5MB

  # SSL/TLS
  ssl:
    enabled: false
    cert_file: null
    key_file: null
    ca_file: null
```

## Monitoring Configuration

### Logging

```yaml
monitoring:
  logging:
    level: "INFO" # DEBUG, INFO, WARNING, ERROR
    format: "detailed" # simple, detailed, json

    # Log files
    app_log: "logs/app.log"
    access_log: "logs/access.log"
    error_log: "logs/error.log"

    # Log rotation
    max_size_mb: 100
    backup_count: 5

    # Structured logging
    structured: true
    include_request_id: true
```

### Metrics

```yaml
monitoring:
  metrics:
    enabled: true

    # Prometheus metrics
    prometheus:
      enabled: false
      port: 9090
      path: "/metrics"

    # Performance metrics
    track_performance: true
    track_usage: true
    track_errors: true

    # Export settings
    export_interval: 60 # seconds
    export_format: "json" # json, csv, prometheus
```

## Environment Variables

You can override configuration values using environment variables:

```bash
# Server settings
export DANMU_TTS_HOST="0.0.0.0"
export DANMU_TTS_PORT="8000"
export DANMU_TTS_DEBUG="false"

# TTS settings
export DANMU_TTS_PRIMARY_BACKEND="edge"
export DANMU_TTS_ENABLE_CACHE="true"

# GPU settings
export DANMU_TTS_CUDA_DEVICE="0"
export DANMU_TTS_ENABLE_GPU="true"

# API keys
export AZURE_SUBSCRIPTION_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

## Configuration Validation

Use the configuration validator to check your settings:

```bash
python -m src.config --validate
```

This will:

- Check syntax and structure
- Validate backend availability
- Test API keys and connections
- Verify model paths and files
- Check resource requirements

## Example Configurations

### Development Configuration

```yaml
server:
  host: "127.0.0.1"
  port: 8000
  debug: true

tts:
  primary_backend: "edge"
  backends:
    edge:
      enabled: true
    piper:
      enabled: false
    xtts:
      enabled: false

cache:
  enabled: false

performance:
  max_cpu_cores: 2
```

### Production Configuration

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  debug: false
  max_workers: 8

tts:
  primary_backend: "edge"
  fallback_backends: ["xtts", "piper"]
  auto_selection: true

cache:
  enabled: true
  backend: "redis"
  max_size: 5000

performance:
  max_cpu_cores: 16
  max_memory_mb: 8192
  gpu_memory_fraction: 0.9

security:
  rate_limiting:
    enabled: true
    requests_per_minute: 100
```

### High-Performance Configuration

```yaml
server:
  max_workers: 16

tts:
  backends:
    xtts:
      enabled: true
      device: "cuda"
      max_batch_size: 8
      enable_deepspeed: true

cache:
  enabled: true
  backend: "redis"
  max_size: 10000
  async_write: true

performance:
  batch_processing: true
  jit_compilation: true
  half_precision: true
```
