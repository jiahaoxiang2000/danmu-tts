# UV Setup Guide for Danmu TTS Server

## Why UV?

[UV](https://github.com/astral-sh/uv) is a extremely fast Python package installer and resolver, written in Rust. It's 10-100x faster than pip and provides better dependency resolution.

### Benefits for this project:

- **Speed**: Install all dependencies in seconds instead of minutes
- **Better dependency resolution**: Handles complex ML/AI package conflicts better
- **Python version management**: Automatically handles Python versions
- **Lock files**: Ensures reproducible builds
- **Memory efficiency**: Lower memory usage, important for GPU servers

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Download and run the setup script
./setup.sh

# Or with specific Python version
./setup.sh --python 3.10
```

### Option 2: Manual UV Setup

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Create virtual environment with Python 3.11
uv venv --python 3.11

# Activate environment
source .venv/bin/activate

# Install dependencies
uv pip install -e .[all]

# For GPU support (RTX 4090)
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Python Version Compatibility

| Python Version | Status          | Notes                         |
| -------------- | --------------- | ----------------------------- |
| 3.9            | ✅ Supported    | Minimum version               |
| 3.10           | ✅ Recommended  | Best performance              |
| 3.11           | ✅ Recommended  | Latest features               |
| 3.12           | ⚠️ Experimental | Some packages may have issues |

## Installation Profiles

### Basic Installation

```bash
uv pip install -e .
```

Includes: FastAPI, Edge TTS, basic audio processing

### GPU Acceleration (For RTX 4090)

```bash
uv pip install -e .[gpu]
```

Adds: PyTorch, TTS library, CUDA support

### Cloud Services

```bash
uv pip install -e .[cloud]
```

Adds: Azure Cognitive Services, OpenAI TTS

### Redis Caching

```bash
uv pip install -e .[cache]
```

Adds: Redis client for distributed caching

### Development Tools

```bash
uv pip install -e .[dev]
```

Adds: Testing, linting, formatting tools

### Everything

```bash
uv pip install -e .[all]
```

Installs all optional dependencies

## Performance Comparison

| Package Manager | Installation Time | Memory Usage | Dependency Resolution |
| --------------- | ----------------- | ------------ | --------------------- |
| pip             | 2-5 minutes       | High         | Basic                 |
| pip-tools       | 3-7 minutes       | High         | Good                  |
| poetry          | 1-3 minutes       | Medium       | Good                  |
| **uv**          | **10-30 seconds** | **Low**      | **Excellent**         |

## CUDA Setup for RTX 4090

### Check CUDA Compatibility

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA version
nvcc --version
```

### Install CUDA-enabled PyTorch

```bash
# For CUDA 11.8 (most compatible)
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1 (if you have newer drivers)
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Verify GPU Setup

```bash
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"
```

## Common Issues and Solutions

### Issue: UV not found after installation

```bash
# Solution: Source the cargo environment
source $HOME/.cargo/env

# Or add to your shell profile
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: Python version not found

```bash
# Install Python via system package manager
sudo apt update && sudo apt install python3.11 python3.11-venv

# Or use pyenv
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

### Issue: CUDA out of memory

```bash
# Reduce GPU memory fraction in config.yaml
performance:
  gpu:
    memory_fraction: 0.5  # Use only 50% of GPU memory
```

### Issue: Package conflicts

```bash
# UV handles this automatically, but if issues persist:
uv pip install --force-reinstall -e .[all]
```

## Lock Files and Reproducibility

UV automatically generates lock files for reproducible builds:

```bash
# Generate lock file
uv pip freeze > requirements.lock

# Install from lock file on production
uv pip install -r requirements.lock
```

## Docker with UV

Updated Dockerfile for UV:

```dockerfile
FROM python:3.11-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml .
COPY . .

# Install dependencies with UV
RUN uv pip install --system -e .[all]

EXPOSE 8000
CMD ["python", "app.py"]
```

## Migration from pip

If you have an existing pip-based setup:

```bash
# Backup current environment
pip freeze > old-requirements.txt

# Remove old venv
rm -rf venv/

# Setup with UV
./setup.sh

# Compare installations
uv pip list > new-requirements.txt
diff old-requirements.txt new-requirements.txt
```

## Performance Tuning

For maximum performance with UV:

```bash
# Use UV's parallel installation
export UV_CONCURRENT_DOWNLOADS=10

# Use faster index
export UV_INDEX_URL=https://pypi.org/simple/

# Enable UV cache
export UV_CACHE_DIR=~/.cache/uv
```

## Troubleshooting Commands

```bash
# Check UV version
uv --version

# Verify Python installation
uv python list

# Check package tree
uv pip tree

# Validate environment
uv pip check

# Clear cache if needed
uv cache clean
```
