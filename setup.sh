#!/bin/bash

# Advanced setup script for Danmu TTS Server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check system requirements
check_system() {
    print_header "🔍 Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Python $PYTHON_VERSION found"
        
        # Check if version is compatible (3.9-3.11)
        if [[ $(echo "$PYTHON_VERSION 3.9" | awk '{print ($1 >= $2)}') == 1 ]] && \
           [[ $(echo "$PYTHON_VERSION 3.12" | awk '{print ($1 < $2)}') == 1 ]]; then
            print_status "Python version is compatible"
        else
            print_warning "Python $PYTHON_VERSION may not be fully compatible. Recommended: 3.9-3.11"
        fi
    else
        print_error "Python 3 not found. Please install Python 3.9-3.11"
        exit 1
    fi
    
    # Check GPU
    if command -v nvidia-smi &> /dev/null; then
        print_status "NVIDIA GPU detected"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | while read gpu; do
            print_status "  GPU: $gpu"
        done
    else
        print_warning "No NVIDIA GPU detected. GPU acceleration will be disabled."
    fi
    
    # Check disk space
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [[ $AVAILABLE_SPACE -gt 10485760 ]]; then  # 10GB in KB
        print_status "Sufficient disk space available"
    else
        print_warning "Low disk space. At least 10GB recommended."
    fi
}

# Install UV if not present
install_uv() {
    print_header "📦 Setting up UV package manager..."
    
    if command -v uv &> /dev/null; then
        print_status "UV already installed: $(uv --version)"
    else
        print_status "Installing UV..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        
        if command -v uv &> /dev/null; then
            print_status "UV installed successfully: $(uv --version)"
        else
            print_error "Failed to install UV"
            exit 1
        fi
    fi
}

# Setup virtual environment
setup_venv() {
    print_header "🐍 Setting up Python virtual environment..."
    
    # Determine Python version to use
    PYTHON_VERSION=${1:-"3.11"}
    
    if [ -d ".venv" ]; then
        print_status "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf .venv
            print_status "Removed existing virtual environment"
        else
            return 0
        fi
    fi
    
    print_status "Creating virtual environment with Python $PYTHON_VERSION..."
    if uv venv --python $PYTHON_VERSION; then
        print_status "Virtual environment created successfully"
    else
        print_warning "Failed to create venv with Python $PYTHON_VERSION, trying system Python..."
        uv venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    print_status "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_header "📚 Installing dependencies..."
    
    # Install base dependencies
    print_status "Installing base dependencies..."
    uv pip install -e .
    
    # Ask about optional features
    echo
    print_header "Optional features:"
    
    # GPU support
    if command -v nvidia-smi &> /dev/null; then
        read -p "Install GPU acceleration support? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            print_status "Installing GPU dependencies..."
            uv pip install -e .[gpu]
            
            # Install PyTorch with CUDA
            print_status "Installing PyTorch with CUDA support..."
            uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
        fi
    fi
    
    # Cloud TTS
    read -p "Install cloud TTS services (Azure, OpenAI)? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing cloud TTS dependencies..."
        uv pip install -e .[cloud]
    fi
    
    # Redis cache
    read -p "Install Redis cache support? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing Redis dependencies..."
        uv pip install -e .[cache]
    fi
    
    # Development tools
    read -p "Install development tools? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing development dependencies..."
        uv pip install -e .[dev]
    fi
}

# Create directories and configuration
setup_directories() {
    print_header "📁 Setting up directories..."
    
    mkdir -p logs cache models/piper models/xtts models/speakers
    print_status "Created necessary directories"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# GPU Settings
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Optional API Keys (uncomment and fill in if using cloud services)
# AZURE_SPEECH_KEY=your_azure_key_here
# AZURE_SPEECH_REGION=your_region_here
# OPENAI_API_KEY=your_openai_key_here

# Redis Settings (if using Redis cache)
# REDIS_URL=redis://localhost:6379/0
EOF
        print_status ".env file created"
    fi
}

# Test installation
test_installation() {
    print_header "🧪 Testing installation..."
    
    # Test Python imports
    python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import fastapi
    print('✅ FastAPI imported successfully')
except ImportError as e:
    print(f'❌ FastAPI import failed: {e}')

try:
    import torch
    if torch.cuda.is_available():
        print(f'✅ PyTorch with CUDA: {torch.cuda.get_device_name(0)}')
        print(f'   CUDA version: {torch.version.cuda}')
        print(f'   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    else:
        print('⚠️  PyTorch without CUDA (CPU mode)')
except ImportError:
    print('❌ PyTorch not installed')

try:
    import edge_tts
    print('✅ Edge TTS available')
except ImportError:
    print('❌ Edge TTS not available')

try:
    from TTS.api import TTS
    print('✅ XTTS available')
except ImportError:
    print('❌ XTTS not available')
"
}

# Main installation flow
main() {
    print_header "🚀 Danmu TTS Server Setup"
    echo "This script will set up the TTS server with UV package manager"
    echo
    
    # Parse command line arguments
    PYTHON_VERSION="3.11"
    SKIP_CHECKS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --python)
                PYTHON_VERSION="$2"
                shift 2
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --python VERSION    Specify Python version (default: 3.11)"
                echo "  --skip-checks      Skip system requirement checks"
                echo "  --help             Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    if [ "$SKIP_CHECKS" != true ]; then
        check_system
    fi
    
    install_uv
    setup_venv "$PYTHON_VERSION"
    install_dependencies
    setup_directories
    test_installation
    
    print_header "🎉 Setup complete!"
    echo
    print_status "To start the server:"
    echo "  source .venv/bin/activate"
    echo "  python app.py"
    echo
    print_status "Or use the startup script:"
    echo "  ./start_server.sh"
    echo
    print_status "Web interface will be available at: http://localhost:8000/web/"
    print_status "API documentation at: http://localhost:8000/docs"
}

# Run main function
main "$@"
