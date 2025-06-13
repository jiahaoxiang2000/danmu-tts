#!/bin/bash

# Development mode startup script with hot reload

echo "🔧 Starting Danmu TTS Server in development mode..."

# Check if UV virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install development dependencies if not present
echo "Checking development dependencies..."
uv pip install -e .[dev] --quiet

# Create test directories
mkdir -p tests logs cache

# Set development environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export TTS_DEBUG=true
export TTS_LOG_LEVEL=DEBUG

# Start server with auto-reload
echo "Starting server with auto-reload..."
echo "🌐 Web interface: http://localhost:8000/web/"
echo "📚 API docs: http://localhost:8000/docs"
echo "🔄 Server will reload automatically on file changes"
echo ""

uvicorn app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir src \
    --reload-dir . \
    --log-level debug
