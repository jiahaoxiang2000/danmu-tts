# Danmu TTS Server Makefile
# Basic server management functions

# Configuration
PROJECT_NAME = danmu-tts
PYTHON = python3
VENV_DIR = .venv
PID_FILE = logs/tts_server.pid
LOG_FILE = logs/tts_server.log

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m

# Default target
.DEFAULT_GOAL := help

# Check if virtual environment exists
.check-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Virtual environment not found!$(NC)"; \
		echo "Run 'make setup' first to install dependencies"; \
		exit 1; \
	fi

# Setup target
.PHONY: setup
setup: ## Install dependencies and setup environment
	@echo "$(BLUE)Setting up Danmu TTS Server...$(NC)"
	./setup.sh

# Server management targets
.PHONY: start
start: .check-venv ## Start the server in background
	@echo "$(BLUE)Starting TTS Server...$(NC)"
	./start_server.sh start

.PHONY: stop
stop: ## Stop the server
	@echo "$(BLUE)Stopping TTS Server...$(NC)"
	./start_server.sh stop

.PHONY: restart
restart: ## Restart the server
	@echo "$(BLUE)Restarting TTS Server...$(NC)"
	./start_server.sh restart

.PHONY: status
status: ## Show server status
	@./start_server.sh status

# Log management
.PHONY: logs
logs: ## Show server logs (real-time)
	@if [ -f "$(LOG_FILE)" ]; then \
		echo "$(BLUE)Showing logs (Ctrl+C to exit):$(NC)"; \
		tail -f $(LOG_FILE); \
	else \
		echo "$(RED)Log file not found: $(LOG_FILE)$(NC)"; \
	fi

.PHONY: logs-tail
logs-tail: ## Show last 50 lines of logs
	@if [ -f "$(LOG_FILE)" ]; then \
		echo "$(BLUE)Last 50 lines of logs:$(NC)"; \
		tail -50 $(LOG_FILE); \
	else \
		echo "$(RED)Log file not found: $(LOG_FILE)$(NC)"; \
	fi

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)Danmu TTS Server - Basic Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  $(GREEN)setup$(NC)           Install dependencies and setup environment"
	@echo "  $(GREEN)update$(NC)          Update dependencies"
	@echo ""
	@echo "$(YELLOW)Server Management:$(NC)"
	@echo "  $(GREEN)start$(NC)           Start the server in background"
	@echo "  $(GREEN)stop$(NC)            Stop the server"
	@echo "  $(GREEN)restart$(NC)         Restart the server"
	@echo "  $(GREEN)status$(NC)          Show server status"
	@echo "  $(GREEN)dev$(NC)             Run server in development mode (foreground)"
	@echo ""
	@echo "$(YELLOW)Logs:$(NC)"
	@echo "  $(GREEN)logs$(NC)            Show server logs (real-time)"
	@echo "  $(GREEN)logs-tail$(NC)       Show last 50 lines of logs"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make setup          # Initial setup"
	@echo "  make start          # Start server in background"
	@echo "  make dev            # Start server in development mode"
	@echo "  make logs           # Follow server logs"
	@echo "  make status         # Check server status"
	@echo "  make restart        # Restart server"
