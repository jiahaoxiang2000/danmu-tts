#!/bin/bash

# Advanced Process Management Script for Danmu TTS Server
# This script provides additional process management features

# Configuration
PROJECT_DIR="/home/xjh/py/danmu-tts"
PID_FILE="$PROJECT_DIR/logs/tts_server.pid"
LOG_FILE="$PROJECT_DIR/logs/tts_server.log"
ERROR_LOG="$PROJECT_DIR/logs/tts_server_error.log"
MONITOR_INTERVAL=5
MAX_MEMORY_MB=2048  # Kill process if it uses more than this amount of memory

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}$1${NC}"; }

# Check if server is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Get process info
get_process_info() {
    if ! is_running; then
        print_error "Server is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    print_header "Process Information (PID: $PID)"
    
    # Basic process info
    ps -p "$PID" -o pid,ppid,cmd,%cpu,%mem,vsz,rss,etime,lstart 2>/dev/null
    
    echo ""
    print_header "Memory Usage"
    ps -p "$PID" -o pid,vsz,rss,pmem --no-headers | while read pid vsz rss pmem; do
        vsz_mb=$((vsz / 1024))
        rss_mb=$((rss / 1024))
        echo "  Virtual Memory: ${vsz_mb} MB"
        echo "  Resident Memory: ${rss_mb} MB"
        echo "  Memory Percentage: ${pmem}%"
        
        if [ "$rss_mb" -gt "$MAX_MEMORY_MB" ]; then
            print_warning "Memory usage is high (${rss_mb} MB > ${MAX_MEMORY_MB} MB)"
        fi
    done
    
    echo ""
    print_header "Network Connections"
    if command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep "$PID" || echo "  No network connections found"
    elif command -v ss &> /dev/null; then
        ss -tlnp | grep "$PID" || echo "  No network connections found"
    else
        echo "  Network tools not available"
    fi
    
    echo ""
    print_header "Open Files"
    if command -v lsof &> /dev/null; then
        lsof -p "$PID" 2>/dev/null | wc -l | xargs echo "  Open file descriptors:"
    else
        ls /proc/"$PID"/fd 2>/dev/null | wc -l | xargs echo "  Open file descriptors:"
    fi
}

# Monitor server health
monitor_server() {
    if ! is_running; then
        print_error "Server is not running"
        return 1
    fi
    
    print_header "Monitoring server (Ctrl+C to stop)..."
    
    while true; do
        if ! is_running; then
            print_error "Server stopped unexpectedly!"
            break
        fi
        
        PID=$(cat "$PID_FILE")
        
        # Get current stats
        STATS=$(ps -p "$PID" -o %cpu,%mem,vsz,rss --no-headers 2>/dev/null)
        if [ -n "$STATS" ]; then
            read cpu mem vsz rss <<< "$STATS"
            rss_mb=$((rss / 1024))
            vsz_mb=$((vsz / 1024))
            
            timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            echo "[$timestamp] CPU: ${cpu}% | Memory: ${mem}% (${rss_mb}MB) | Virtual: ${vsz_mb}MB"
            
            # Check memory threshold
            if [ "$rss_mb" -gt "$MAX_MEMORY_MB" ]; then
                print_warning "Memory usage exceeded threshold (${rss_mb}MB > ${MAX_MEMORY_MB}MB)"
                print_warning "Consider restarting the server"
            fi
            
            # Check if CPU usage is too high
            cpu_int=${cpu%.*}
            if [ "$cpu_int" -gt 90 ]; then
                print_warning "High CPU usage detected: ${cpu}%"
            fi
        else
            print_error "Could not get process stats"
            break
        fi
        
        sleep "$MONITOR_INTERVAL"
    done
}

# Health check function
health_check() {
    print_header "Performing health check..."
    
    # Check if process is running
    if ! is_running; then
        print_error "Process is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    print_status "Process is running (PID: $PID)"
    
    # Check if server responds to HTTP requests
    if command -v curl &> /dev/null; then
        if curl -s --connect-timeout 5 http://localhost:8000/ > /dev/null; then
            print_status "HTTP endpoint is responsive"
        else
            print_error "HTTP endpoint is not responsive"
            return 1
        fi
    else
        print_warning "curl not available, skipping HTTP check"
    fi
    
    # Check log file for recent errors
    if [ -f "$ERROR_LOG" ]; then
        ERROR_COUNT=$(tail -100 "$ERROR_LOG" 2>/dev/null | grep -i error | wc -l)
        if [ "$ERROR_COUNT" -gt 0 ]; then
            print_warning "Found $ERROR_COUNT errors in recent logs"
        else
            print_status "No recent errors in logs"
        fi
    fi
    
    print_status "Health check completed"
    return 0
}

# Automatically restart server if it crashes
auto_restart() {
    print_header "Starting auto-restart daemon..."
    print_status "Monitoring interval: ${MONITOR_INTERVAL}s"
    print_status "Max memory threshold: ${MAX_MEMORY_MB}MB"
    
    while true; do
        if ! is_running; then
            print_warning "Server is not running, attempting to restart..."
            
            # Wait a moment before restart
            sleep 2
            
            # Use the main start script
            cd "$PROJECT_DIR"
            ./start_server.sh start
            
            if is_running; then
                print_status "Server restarted successfully"
            else
                print_error "Failed to restart server, waiting 30 seconds..."
                sleep 30
            fi
        else
            # Check memory usage
            PID=$(cat "$PID_FILE")
            RSS_KB=$(ps -p "$PID" -o rss --no-headers 2>/dev/null | tr -d ' ')
            if [ -n "$RSS_KB" ]; then
                RSS_MB=$((RSS_KB / 1024))
                if [ "$RSS_MB" -gt "$MAX_MEMORY_MB" ]; then
                    print_warning "Memory threshold exceeded (${RSS_MB}MB > ${MAX_MEMORY_MB}MB), restarting server..."
                    cd "$PROJECT_DIR"
                    ./start_server.sh restart
                fi
            fi
        fi
        
        sleep "$MONITOR_INTERVAL"
    done
}

# Performance stats
performance_stats() {
    if ! is_running; then
        print_error "Server is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    print_header "Performance Statistics (PID: $PID)"
    
    # CPU and memory over time
    echo "Collecting performance data (10 samples, 2s interval)..."
    echo ""
    echo "Time                CPU%   MEM%   RSS(MB)  VSZ(MB)"
    echo "================================================="
    
    for i in {1..10}; do
        STATS=$(ps -p "$PID" -o %cpu,%mem,rss,vsz --no-headers 2>/dev/null)
        if [ -n "$STATS" ]; then
            read cpu mem rss vsz <<< "$STATS"
            rss_mb=$((rss / 1024))
            vsz_mb=$((vsz / 1024))
            timestamp=$(date '+%H:%M:%S')
            printf "%-15s %-6s %-6s %-8s %-8s\n" "$timestamp" "$cpu" "$mem" "$rss_mb" "$vsz_mb"
        else
            print_error "Process no longer running"
            break
        fi
        sleep 2
    done
}

# Show help
show_help() {
    echo "Advanced Process Management for Danmu TTS Server"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  info          Show detailed process information"
    echo "  monitor       Monitor server in real-time"
    echo "  health        Perform health check"
    echo "  auto-restart  Start auto-restart daemon"
    echo "  performance   Show performance statistics"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 info           # Show process details"
    echo "  $0 monitor        # Monitor server performance"
    echo "  $0 health         # Check server health"
    echo "  $0 auto-restart   # Start auto-restart daemon"
    echo ""
}

# Main script logic
case "${1:-help}" in
    info)
        get_process_info
        ;;
    monitor)
        monitor_server
        ;;
    health)
        health_check
        ;;
    auto-restart|daemon)
        auto_restart
        ;;
    performance|perf)
        performance_stats
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
