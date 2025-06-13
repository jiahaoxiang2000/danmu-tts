# Docker deployment configuration with UV
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project configuration
COPY pyproject.toml .
COPY requirements.txt .

# Install Python dependencies with UV (much faster)
RUN uv pip install --system -e .[all]

# For GPU support, install PyTorch with CUDA
RUN uv pip install --system torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs cache models/piper models/xtts models/speakers

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start the application
CMD ["python", "app.py"]
