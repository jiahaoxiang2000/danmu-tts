# 安装和配置指南

## 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+)
- **Python**: 3.8+
- **GPU**: NVIDIA RTX 4090 (24GB VRAM)
- **RAM**: 16GB+ 推荐
- **存储**: 10GB+ 可用空间

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd danmu-tts
```

### 2. 自动安装 (推荐)

```bash
./start_server.sh
```

### 3. 手动安装

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建必要目录
mkdir -p logs cache models/piper models/xtts

# 启动服务器
python app.py
```

## GPU 环境配置

### NVIDIA CUDA 设置

```bash
# 检查 CUDA 版本
nvidia-smi

# 安装 CUDA (如果需要)
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run

# 设置环境变量
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
```

### PyTorch GPU 支持

```bash
# 安装支持 CUDA 的 PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# 验证 GPU 支持
python -c "import torch; print(torch.cuda.is_available())"
```

## TTS 后端配置

### 1. Edge TTS (默认启用)

无需额外配置，开箱即用。

### 2. Piper TTS

```bash
# 安装 Piper
pip install piper-tts

# 下载中文模型
mkdir -p models/piper
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx.json
```

### 3. XTTS (高质量)

```bash
# 安装 TTS 库
pip install TTS

# 下载 XTTS 模型 (自动)
# 模型将在首次使用时自动下载
```

## 配置文件调优

### 针对 RTX 4090 的推荐配置

编辑 `config.yaml`:

```yaml
# 高性能配置
performance:
  gpu:
    enabled: true
    device: "cuda:0"
    memory_fraction: 0.7 # 使用 70% GPU 内存

  cache:
    enabled: true
    max_size_mb: 2048 # 2GB 缓存
    ttl_seconds: 3600

  queue:
    max_concurrent: 8 # 并发处理 8 个请求

# TTS 后端优先级
tts:
  primary_backend: "edge"
  fallback_backends: ["piper", "xtts"]
```

### 成本优化配置

```yaml
# 省电配置
performance:
  gpu:
    memory_fraction: 0.4 # 降低 GPU 使用

tts:
  backends:
    xtts:
      enabled: true
      max_requests_per_hour: 30 # 限制高耗能请求
```

## 直播软件集成

### OBS Studio 集成

1. 安装 OBS WebSocket 插件
2. 使用以下脚本连接:

```python
# obs_tts.py
import asyncio
import websockets
import json

async def send_tts(text):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "type": "tts",
            "text": text,
            "voice": "zh-CN-XiaoxiaoNeural"
        }))

        # 处理音频流
        while True:
            message = await websocket.recv()
            if isinstance(message, bytes):
                # 播放音频块
                continue
            else:
                data = json.loads(message)
                if data.get("type") == "complete":
                    break

# 使用示例
asyncio.run(send_tts("新的弹幕: 主播你好！"))
```

### B 站弹幕监听

```python
# bilibili_listener.py
import asyncio
import aiohttp
import json

class BilibiliDanmuListener:
    def __init__(self, room_id, tts_server="ws://localhost:8000/ws"):
        self.room_id = room_id
        self.tts_server = tts_server

    async def connect_danmu(self):
        # 连接 B站弹幕 WebSocket
        # 实现弹幕监听逻辑
        pass

    async def send_to_tts(self, text):
        async with websockets.connect(self.tts_server) as ws:
            await ws.send(json.dumps({
                "type": "tts",
                "text": text[:100],  # 限制长度
                "backend": "edge"    # 使用快速后端
            }))
```

## 监控和维护

### 系统监控

```bash
# 安装监控工具
pip install psutil GPUtil

# 运行监控脚本
python -c "
import psutil
import GPUtil

# GPU 状态
gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f'GPU {gpu.id}: {gpu.temperature}°C, {gpu.memoryUtil:.1%} VRAM')

# 系统状态
print(f'CPU: {psutil.cpu_percent()}%')
print(f'RAM: {psutil.virtual_memory().percent}%')
"
```

### 日志监控

```bash
# 实时查看日志
tail -f logs/tts_server.log

# 搜索错误
grep ERROR logs/tts_server.log
```

## 性能基准测试

### 延迟测试

```bash
# 测试各后端延迟
python demo_client.py
```

预期结果:

- Edge TTS: 200-500ms
- Piper TTS: 100-300ms
- XTTS: 1-3 秒

### 压力测试

```bash
# 并发测试
pip install aiohttp
python -c "
import asyncio
import aiohttp
import time

async def test_concurrent():
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()

        for i in range(10):
            task = session.post('http://localhost:8000/tts',
                              json={'text': f'测试文本 {i}'})
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        print(f'10 个并发请求完成时间: {end_time - start_time:.2f} 秒')

asyncio.run(test_concurrent())
"
```

## 故障排除

### 常见问题

1. **CUDA 内存不足**

   ```bash
   # 降低 memory_fraction
   # config.yaml: memory_fraction: 0.5
   ```

2. **Edge TTS 连接失败**

   ```bash
   # 检查网络连接
   ping speech.platform.bing.com
   ```

3. **Piper 模型未找到**

   ```bash
   # 重新下载模型
   cd models/piper
   wget https://huggingface.co/rhasspy/piper-voices/...
   ```

4. **GPU 温度过高**
   ```bash
   # 设置风扇曲线
   nvidia-settings -a '[gpu:0]/GPUFanControlState=1'
   nvidia-settings -a '[fan:0]/GPUTargetFanSpeed=80'
   ```

### 性能优化提示

1. **使用 SSD**: 将缓存和模型存储在高速 SSD 上
2. **内存优化**: 增加系统 RAM 以支持更大缓存
3. **网络优化**: 使用有线连接以减少 Edge TTS 延迟
4. **散热优化**: 确保 GPU 有良好的散热

## API 文档

启动服务器后访问:

- Web 界面: http://localhost:8000/web/
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/

## 技术支持

遇到问题时:

1. 查看日志文件: `logs/tts_server.log`
2. 检查 GPU 状态: `nvidia-smi`
3. 验证依赖: `pip list`
4. 测试网络: `curl http://localhost:8000/`
