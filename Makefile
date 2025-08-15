.PHONY: start stop restart status install dev clean help

PID_FILE = danmu_tts.pid
LOG_FILE = danmu_tts.log

help:
	@echo "Danmu TTS Server Management"
	@echo "=========================="
	@echo "Available commands:"
	@echo "  make start     - Start the danmu_tts server"
	@echo "  make stop      - Stop the danmu_tts server"
	@echo "  make restart   - Restart the danmu_tts server"
	@echo "  make status    - Check server status"
	@echo "  make install   - Install dependencies"
	@echo "  make dev       - Install development dependencies"
	@echo "  make clean     - Clean up temporary files"
	@echo "  make help      - Show this help message"

install:
	@echo "Installing dependencies..."
	uv sync --no-dev

dev:
	@echo "Installing development dependencies..."
	uv sync

start:
	@echo "Starting danmu_tts server..."
	@if [ -f $(PID_FILE) ]; then \
		echo "Server is already running (PID: $$(cat $(PID_FILE)))"; \
		exit 1; \
	fi
	@nohup python -m danmu_tts.main > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE)
	@echo "Server started (PID: $$(cat $(PID_FILE)))"
	@echo "Logs: tail -f $(LOG_FILE)"

stop:
	@echo "Stopping danmu_tts server..."
	@if [ ! -f $(PID_FILE) ]; then \
		echo "Server is not running (no PID file found)"; \
		exit 1; \
	fi
	@PID=$$(cat $(PID_FILE)); \
	if kill -0 $$PID 2>/dev/null; then \
		kill $$PID && echo "Server stopped (PID: $$PID)"; \
	else \
		echo "Server process not found (PID: $$PID was stale)"; \
	fi
	@rm -f $(PID_FILE)

restart: stop
	@sleep 2
	@$(MAKE) start

status:
	@if [ -f $(PID_FILE) ]; then \
		PID=$$(cat $(PID_FILE)); \
		if kill -0 $$PID 2>/dev/null; then \
			echo "Server is running (PID: $$PID)"; \
		else \
			echo "Server is not running (stale PID file found)"; \
			rm -f $(PID_FILE); \
		fi \
	else \
		echo "Server is not running"; \
	fi

clean:
	@echo "Cleaning up temporary files..."
	@rm -f $(PID_FILE) $(LOG_FILE)
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete"