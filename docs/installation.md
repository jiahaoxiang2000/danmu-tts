# Installation Guide

This guide covers the complete installation process for the Danmu TTS Server on Linux systems.

## System Requirements

### Minimum Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 10GB+ available space
- **CPU**: Multi-core processor recommended

### Recommended for GPU Acceleration

- **GPU**: NVIDIA RTX 4090 (24GB VRAM) or similar
- **CUDA**: Version 11.8 or higher
- **cuDNN**: Compatible version with CUDA

## Installation Methods

### Method 1: Automated Setup with UV (Recommended)

The fastest way to get started is using the automated setup script with UV package manager.

```bash
# Clone the repository
git clone <your-repo-url>
cd danmu-tts

# Run automated setup
./setup.sh

# Start the server
./start_server.sh
```

### Method 2: Manual Setup with UV

```bash
# Install UV (ultra-fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Create virtual environment with Python 3.11
uv venv --python 3.11
source .venv/bin/activate

# Install dependencies (10x faster than pip)
uv sync

# Create required directories
mkdir -p logs cache models/piper models/xtts

# Start the server
python app.py
```

### Method 3: Traditional pip Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p logs cache models/piper models/xtts

# Start the server
python app.py
```

## GPU Setup (Optional but Recommended)

### NVIDIA CUDA Installation

1. **Check GPU compatibility**:

```bash
nvidia-smi
```

2. **Install CUDA Toolkit**:

```bash
# Ubuntu/Debian
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda
```

3. **Install PyTorch with CUDA support**:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Verify GPU Installation

```bash
python check_env.py
```

This script will verify:

- CUDA availability
- GPU memory
- PyTorch GPU support
- TTS backend compatibility

## Model Download

### EdgeTTS

No additional models needed - uses Microsoft's cloud service.

### Piper TTS

```bash
# Download Chinese model
wget -O models/piper/zh_CN-huayan-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx
wget -O models/piper/zh_CN-huayan-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx.json
```

### XTTS

The model will be automatically downloaded on first use (about 2GB).

## Configuration

1. **Copy configuration template**:

```bash
cp config.yaml.example config.yaml
```

2. **Edit configuration**:

```bash
nano config.yaml
```

Key settings to review:

- Server host and port
- Enabled TTS backends
- GPU device selection
- Audio quality settings

## Verification

1. **Start the server**:

```bash
python app.py
```

2. **Test the API**:

```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "voice": "zh-CN-XiaoxiaoNeural"}'
```

3. **Access web interface**:
   Open `http://localhost:8000` in your browser.

## Troubleshooting

### Common Issues

1. **CUDA not found**:

   - Verify NVIDIA drivers: `nvidia-smi`
   - Check CUDA installation: `nvcc --version`
   - Reinstall PyTorch with correct CUDA version

2. **Memory errors**:

   - Reduce batch size in config.yaml
   - Use CPU-only mode for testing
   - Check available RAM and GPU memory

3. **Model download fails**:

   - Check internet connection
   - Verify disk space
   - Use manual download commands

4. **Permission errors**:
   ```bash
   sudo chown -R $USER:$USER /path/to/danmu-tts
   chmod +x setup.sh start_server.sh
   ```

### Log Analysis

Check logs for detailed error information:

```bash
tail -f logs/app.log
```

### Environment Check

Run the environment checker:

```bash
python check_env.py
```

## Next Steps

- [Quick Start Guide](quick-start.md) - Basic usage examples
- [Configuration](configuration.md) - Detailed configuration options
- [API Documentation](api/rest-api.md) - API reference
