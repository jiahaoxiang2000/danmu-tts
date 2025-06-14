#!/bin/bash

# TTS Server Management Script
# Usage: ./start_server.sh [start|stop|restart|status|foreground]

# Configuration
SERVER_NAME="danmu-tts"
PID_FILE="logs/tts_server.pid"
LOG_FILE="logs/tts_server.log"
ERROR_LOG="logs/tts_server_error.log"

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

# Check if virtual environment exists
check_venv() {
    if [ ! -d ".venv" ]; then
        print_error "Virtual environment not found!"
        echo "Please run setup.sh first to install dependencies:"
        echo "  ./setup.sh"
        exit 1
    fi
}

# Check if server is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            # PID file exists but process is dead, clean up
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Get server status
get_status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        print_status "TTS Server is running (PID: $PID)"
        
        # Show basic process info
        if command -v ps &> /dev/null; then
            ps -p "$PID" -o pid,ppid,cmd,%cpu,%mem,etime 2>/dev/null || true
        fi
        
        # Show log tail if available
        if [ -f "$LOG_FILE" ]; then
            echo ""
            print_header "Recent logs (last 5 lines):"
            tail -5 "$LOG_FILE" 2>/dev/null || true
        fi
        
        return 0
    else
        print_warning "TTS Server is not running"
        return 1
    fi
}

# Start server in background
start_server() {
    if is_running; then
        print_warning "TTS Server is already running"
        get_status
        return 0
    fi

    print_header "🚀 Starting Danmu TTS Server..."
    
    check_venv
    
    # Ensure directories exist
    mkdir -p logs cache models/piper models/xtts
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # System checks
    print_status "Performing system checks..."
    
    # Check GPU availability
    python -c "
import torch
if torch.cuda.is_available():
    print('✅ CUDA available: ' + torch.cuda.get_device_name(0))
    print(f'   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('⚠️  CUDA not available, using CPU mode')
" 2>/dev/null || print_warning "Could not check GPU status"

    print_status "Python version: $(python --version)"
    print_status "Working directory: $(pwd)"
    
    # Start the server in background
    print_status "Starting TTS server in background..."
    nohup python app.py > "$LOG_FILE" 2> "$ERROR_LOG" &
    SERVER_PID=$!
    
    # Save PID
    echo $SERVER_PID > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if is_running; then
        print_status "TTS Server started successfully (PID: $SERVER_PID)"
        print_status "Logs: $LOG_FILE"
        print_status "Error logs: $ERROR_LOG"
        print_status "Use './start_server.sh status' to check server status"
        print_status "Use './start_server.sh stop' to stop the server"
    else
        print_error "Failed to start TTS Server"
        if [ -f "$ERROR_LOG" ]; then
            print_error "Error log:"
            cat "$ERROR_LOG"
        fi
        return 1
    fi
}

# Stop server
stop_server() {
    if ! is_running; then
        print_warning "TTS Server is not running"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    print_status "Stopping TTS Server (PID: $PID)..."
    
    # Try graceful shutdown first
    kill -TERM "$PID" 2>/dev/null
    
    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if kill -0 "$PID" 2>/dev/null; then
        print_warning "Graceful shutdown failed, forcing termination..."
        kill -KILL "$PID" 2>/dev/null
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ! kill -0 "$PID" 2>/dev/null; then
        print_status "TTS Server stopped successfully"
    else
        print_error "Failed to stop TTS Server"
        return 1
    fi
}

# Restart server
restart_server() {
    print_header "🔄 Restarting TTS Server..."
    stop_server
    sleep 2
    start_server
}

# Run server in foreground (for development)
run_foreground() {
    if is_running; then
        print_warning "TTS Server is already running in background"
        print_status "Stop it first with: ./start_server.sh stop"
        return 1
    fi
    
    print_header "🚀 Starting Danmu TTS Server (foreground mode)..."
    
    check_venv
    
    # Ensure directories exist
    mkdir -p logs cache models/piper models/xtts
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # System checks
    print_status "Performing system checks..."
    
    # Check GPU availability
    python -c "
import torch
if torch.cuda.is_available():
    print('✅ CUDA available: ' + torch.cuda.get_device_name(0))
    print(f'   Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('⚠️  CUDA not available, using CPU mode')
" 2>/dev/null || print_warning "Could not check GPU status"

    print_status "Python version: $(python --version)"
    print_status "Working directory: $(pwd)"
    
    # Start the server in foreground
    print_status "Starting TTS server..."
    python app.py
}

# Show help
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start the server in background"
    echo "  stop        Stop the server"
    echo "  restart     Restart the server"
    echo "  status      Show server status"
    echo "  foreground  Run server in foreground (development mode)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start server in background"
    echo "  $0 stop       # Stop server"
    echo "  $0 restart    # Restart server"
    echo "  $0 status     # Check if server is running"
    echo ""
}

# Main script logic
case "${1:-start}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        get_status
        ;;
    foreground|fg|dev)
        run_foreground
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
