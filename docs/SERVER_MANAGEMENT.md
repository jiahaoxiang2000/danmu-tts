# Server Management Guide

This guide covers the comprehensive server management tools available for the Danmu TTS Server.

## Overview

The Danmu TTS Server provides multiple ways to manage the server lifecycle:

1. **Makefile** - High-level commands for common tasks
2. **start_server.sh** - Direct server management script
3. **process_manager.sh** - Advanced process monitoring and management
4. **Systemd service** - System-level service management (optional)

## Quick Start

```bash
# Initial setup
make setup

# Start server in background
make start

# Check status
make status

# View logs
make logs

# Stop server
make stop
```

## Management Scripts

### Makefile Commands

The Makefile provides the most convenient way to manage the server:

```bash
# Setup and Installation
make setup          # Install dependencies and setup environment
make install         # Alias for setup
make update          # Update dependencies

# Server Management
make start           # Start server in background
make stop            # Stop the server
make restart         # Restart the server
make status          # Show server status
make dev             # Run server in development mode (foreground)
make run             # Alias for dev

# Monitoring and Debugging
make logs            # Show server logs (real-time)
make logs-error      # Show error logs
make logs-tail       # Show last 50 lines of logs
make ps              # Show server process information

# Testing
make test            # Run tests
make test-api        # Test API endpoints
make test-tts        # Test TTS functionality

# Code Quality
make lint            # Run code linting
make format          # Format code with black
make type-check      # Run type checking

# Maintenance
make clean           # Clean cache and temporary files
make clean-logs      # Clean log files
make clean-cache     # Clean TTS cache
make clean-all       # Clean everything
make reset           # Complete reset (stop server, remove venv, clean all)

# Information
make info            # Show system information
make help            # Show all available commands
```

### start_server.sh

Direct server management script with background support:

```bash
# Start server in background
./start_server.sh start

# Stop server
./start_server.sh stop

# Restart server
./start_server.sh restart

# Check server status
./start_server.sh status

# Run in foreground (development)
./start_server.sh foreground

# Show help
./start_server.sh help
```

**Features:**

- Background process management with PID tracking
- Graceful shutdown with fallback to force kill
- System checks and GPU detection
- Colored output and status reporting
- Log file management

### process_manager.sh

Advanced process monitoring and management:

```bash
# Show detailed process information
./process_manager.sh info

# Monitor server in real-time
./process_manager.sh monitor

# Perform comprehensive health check
./process_manager.sh health

# Start auto-restart daemon
./process_manager.sh auto-restart

# Show performance statistics
./process_manager.sh performance
```

**Features:**

- Real-time process monitoring
- Memory usage tracking with thresholds
- Automatic restart on crashes or high memory usage
- Network connection monitoring
- Performance statistics collection
- Health checks with HTTP endpoint testing

## File Locations

```
logs/
├── tts_server.log       # Main server logs
├── tts_server_error.log # Error logs
└── tts_server.pid       # Process ID file

cache/                   # TTS audio cache
models/                  # TTS model files
.venv/                   # Python virtual environment
```

## Background Operation

### Starting in Background

```bash
# Method 1: Using Makefile (recommended)
make start

# Method 2: Using start_server.sh directly
./start_server.sh start

# Method 3: Manual (not recommended)
nohup python app.py > logs/tts_server.log 2> logs/tts_server_error.log &
```

### Checking Status

```bash
# Quick status check
make status

# Detailed process information
./process_manager.sh info

# Real-time monitoring
./process_manager.sh monitor
```

### Viewing Logs

```bash
# Follow logs in real-time
make logs

# Show recent logs
make logs-tail

# Show error logs
make logs-error
```

### Stopping the Server

```bash
# Graceful shutdown
make stop

# Force stop if needed
./start_server.sh stop
```

## Auto-Restart Daemon

The process manager can run an auto-restart daemon that:

- Monitors the server process
- Automatically restarts if it crashes
- Restarts if memory usage exceeds threshold
- Provides continuous monitoring

```bash
# Start auto-restart daemon
./process_manager.sh auto-restart

# Or use nohup to run in background
nohup ./process_manager.sh auto-restart > logs/auto_restart.log 2>&1 &
```

## Systemd Service (Production)

For production deployments, you can install the server as a systemd service:

### Installation

```bash
# Copy service file (adjust paths if needed)
sudo cp danmu-tts.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable danmu-tts
```

### Management

```bash
# Start service
sudo systemctl start danmu-tts

# Stop service
sudo systemctl stop danmu-tts

# Restart service
sudo systemctl restart danmu-tts

# Check status
sudo systemctl status danmu-tts

# View logs
sudo journalctl -u danmu-tts -f
```

### Benefits of Systemd Service

- Automatic startup on system boot
- Automatic restart on failure
- Resource limiting and security features
- Centralized logging with journald
- Integration with system monitoring tools

## Performance Monitoring

### Real-time Monitoring

```bash
# Monitor CPU, memory, and network usage
./process_manager.sh monitor

# Show performance statistics
./process_manager.sh performance
```

### Health Checks

```bash
# Comprehensive health check
./process_manager.sh health

# API endpoint testing
make test-api

# TTS functionality testing
make test-tts
```

### Log Analysis

```bash
# View recent logs
make logs-tail

# Check for errors
make logs-error

# Monitor logs in real-time
make logs
```

## Troubleshooting

### Server Won't Start

1. Check if virtual environment exists:

   ```bash
   ls -la .venv/
   ```

2. If missing, run setup:

   ```bash
   make setup
   ```

3. Check for port conflicts:

   ```bash
   netstat -tlnp | grep :8000
   ```

4. Check error logs:
   ```bash
   make logs-error
   ```

### Server Crashes or High Memory Usage

1. Check system resources:

   ```bash
   ./process_manager.sh info
   ```

2. Monitor performance:

   ```bash
   ./process_manager.sh monitor
   ```

3. Use auto-restart daemon:
   ```bash
   ./process_manager.sh auto-restart
   ```

### Can't Stop Server

1. Try graceful stop:

   ```bash
   make stop
   ```

2. If that fails, force stop:

   ```bash
   ./start_server.sh stop
   ```

3. Manual cleanup if needed:

   ```bash
   # Find and kill process
   ps aux | grep python | grep app.py
   kill -9 <PID>

   # Remove PID file
   rm -f logs/tts_server.pid
   ```

### Permission Issues

1. Make scripts executable:

   ```bash
   chmod +x start_server.sh process_manager.sh setup.sh
   ```

2. Check file ownership:
   ```bash
   ls -la *.sh
   ```

## Configuration

### Environment Variables

The server can be configured using environment variables:

```bash
# Set in your shell profile or systemd service
export TTS_HOST=0.0.0.0
export TTS_PORT=8000
export TTS_DEBUG=false
```

### Configuration Files

- `config.yaml` - Main server configuration
- `uv.toml` - Python package management
- `pyproject.toml` - Project metadata

### Log Levels

Configure logging in `config.yaml`:

```yaml
logging:
  level: INFO # DEBUG, INFO, WARNING, ERROR
  file: logs/tts_server.log
```

## Best Practices

### Development

- Use `make dev` for development mode
- Monitor logs with `make logs`
- Use `make test-api` to verify changes

### Production

- Use systemd service for production
- Enable auto-restart daemon
- Monitor resource usage regularly
- Set up log rotation for large deployments

### Maintenance

- Regular cleanup with `make clean`
- Update dependencies with `make update`
- Monitor cache size and clean if needed
- Back up configuration files

## Integration Examples

### Docker

If using Docker, you can still use these management tools:

```bash
# Build image
docker build -t danmu-tts .

# Run with volume mounts
docker run -d \
  --name danmu-tts \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/cache:/app/cache \
  danmu-tts

# Use docker logs
docker logs -f danmu-tts
```

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy TTS Server
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server "cd /path/to/danmu-tts && git pull"
          ssh user@server "cd /path/to/danmu-tts && make restart"
          ssh user@server "cd /path/to/danmu-tts && make test-api"
```

### Monitoring with External Tools

```bash
# Prometheus metrics endpoint (if implemented)
curl http://localhost:8000/metrics

# Health check for external monitoring
curl http://localhost:8000/health

# Status for uptime monitoring
make status
```

This comprehensive management system provides everything needed to deploy, monitor, and maintain the Danmu TTS Server in both development and production environments.
