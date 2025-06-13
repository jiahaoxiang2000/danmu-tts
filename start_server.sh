#!/bin/bash

# TTS Server Startup Script with UV

echo "🚀 Starting Danmu TTS Server with UV..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with UV (Python 3.11)..."
    uv venv --python 3.11
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies with UV..."
uv pip install -e .[all]

# For CUDA support, install PyTorch with CUDA
echo "Installing PyTorch with CUDA support..."
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Create necessary directories
mkdir -p logs cache models/piper models/xtts

# Check GPU availability
echo "Checking GPU availability..."
python -c "
import torch
if torch.cuda.is_available():
    print(f'✅ CUDA available: {torch.cuda.get_device_name(0)}')
    print(f'   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('⚠️  CUDA not available, using CPU mode')
"

echo "📊 System information:"
echo "   Python version: $(python --version)"
echo "   UV version: $(uv --version)"
echo "   Working directory: $(pwd)"

# Start the server
echo "Starting TTS server..."
python app.py
