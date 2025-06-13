#!/bin/bash

# TTS Server Startup Script

echo "🚀 Starting Danmu TTS Server..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup.sh first to install dependencies:"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Ensure directories exist
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
