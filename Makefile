# Crystal Quest Makefile
# Cross-platform build system for Crystal Quest

.PHONY: help setup clean run package test install dev-install

# Variables
PYTHON := python3
VENV_DIR := game_env
PROJECT_NAME := crystal-quest

# Default target
help:
	@echo "Crystal Quest Build System"
	@echo "=========================="
	@echo ""
	@echo "Available targets:"
	@echo "  help        Show this help message"
	@echo "  setup       Set up development environment"
	@echo "  clean       Clean build artifacts and cache files"
	@echo "  run         Run the game"
	@echo "  package     Create distributable executable"
	@echo "  test        Run basic tests"
	@echo "  install     Install the game system-wide"
	@echo "  dev-install Install in development mode"
	@echo ""
	@echo "Examples:"
	@echo "  make setup    # First time setup"
	@echo "  make run      # Run the game"
	@echo "  make package  # Create executable"
	@echo "  make clean    # Clean up"

# Check if we're on Windows
ifeq ($(OS),Windows_NT)
    PYTHON := python
    VENV_ACTIVATE := $(VENV_DIR)\Scripts\activate
    RM := del /Q
    RMDIR := rmdir /S /Q
else
    VENV_ACTIVATE := . $(VENV_DIR)/bin/activate
    RM := rm -f
    RMDIR := rm -rf
endif

# Setup development environment
setup:
	@echo "Setting up development environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_ACTIVATE) && pip install --upgrade pip
	$(VENV_ACTIVATE) && pip install -r requirements.txt
	@echo "Setup completed!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	$(RMDIR) build dist *.egg-info 2>/dev/null || true
	@echo "Cleanup completed!"

# Clean everything including virtual environment
clean-all: clean
	@echo "Removing virtual environment..."
	$(RMDIR) $(VENV_DIR) 2>/dev/null || true
	@echo "Full cleanup completed!"

# Run the game
run:
	@if [ ! -d "$(VENV_DIR)" ]; then echo "Virtual environment not found. Run 'make setup' first."; exit 1; fi
	$(VENV_ACTIVATE) && $(PYTHON) main.py

# Package for distribution
package:
	@if [ ! -d "$(VENV_DIR)" ]; then echo "Virtual environment not found. Run 'make setup' first."; exit 1; fi
	$(VENV_ACTIVATE) && pip install pyinstaller
	$(VENV_ACTIVATE) && pyinstaller --onefile --windowed \
		--name $(PROJECT_NAME) \
		--add-data "game:game" \
		--clean main.py
	@echo "Executable created in dist/ directory"

# Run basic tests
test:
	@if [ ! -d "$(VENV_DIR)" ]; then echo "Virtual environment not found. Run 'make setup' first."; exit 1; fi
	$(VENV_ACTIVATE) && $(PYTHON) -c "import game; print('All modules imported successfully')"
	$(VENV_ACTIVATE) && $(PYTHON) -c "import pygame; print('Pygame version:', pygame.version.ver)"
	@echo "Basic tests passed!"

# Install system-wide
install:
	pip install -r requirements.txt
	@echo "Dependencies installed system-wide"

# Install in development mode
dev-install: setup
	$(VENV_ACTIVATE) && pip install -e .
	@echo "Installed in development mode"

# Quick development cycle
dev: clean setup test run

# Show project status
status:
	@echo "Project Status:"
	@echo "==============="
	@echo "Virtual environment: $(if $(wildcard $(VENV_DIR)),EXISTS,NOT FOUND)"
	@echo "Python version: $(shell $(PYTHON) --version 2>&1)"
	@if [ -d "$(VENV_DIR)" ]; then echo "Installed packages:"; $(VENV_ACTIVATE) && pip list --format=columns; fi
