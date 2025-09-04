#!/bin/bash
# Crystal Quest Build Script
set -e
VENV_DIR="game_env"

get_python() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        echo "Error: Python not found" >&2
        exit 1
    fi
}

clean() {
    echo "Cleaning build artifacts..."
    find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true
    [ "$1" = "all" ] && rm -rf "$VENV_DIR" 2>/dev/null
    echo "Cleaned"
}

setup() {
    echo "Setting up Crystal Quest..."
    PYTHON_CMD=$(get_python)
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        $PYTHON_CMD -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"
    echo "Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo "Setup complete"
}

play() {
    [ ! -d "$VENV_DIR" ] && { echo "Setting up Crystal Quest..."; setup; }
    source "$VENV_DIR/bin/activate"
    $(get_python) main.py
}

run() {
    [ ! -d "$VENV_DIR" ] && { echo "Setting up Crystal Quest..."; setup; }
    source "$VENV_DIR/bin/activate"
    echo "Starting Crystal Quest..."
    $(get_python) main.py
}

package() {
    [ ! -d "$VENV_DIR" ] && { echo "Run setup first"; exit 1; }
    echo "Packaging Crystal Quest..."
    source "$VENV_DIR/bin/activate"
    pip show pyinstaller &>/dev/null || { echo "Installing PyInstaller..."; pip install pyinstaller -q; }
    echo "Creating executable..."
    pyinstaller --onefile --windowed --name crystal-quest --add-data "game:game" --clean main.py
    echo "Executable created in dist/"
}

test() {
    [ ! -d "$VENV_DIR" ] && { echo "Run setup first"; exit 1; }
    echo "Running tests..."
    source "$VENV_DIR/bin/activate"
    $(get_python) -c "import game, pygame; from game.constants import *; from game.player import Player; from game.entities import *; print('All tests passed')"
}
case "${1:-play}" in
    clean) clean "$2" ;;
    setup) setup ;;
    run) run ;;
    play) play ;;
    package) package ;;
    test) test ;;
    help) echo "Usage: $0 {setup|clean|run|play|package|test|help}" ;;
    *) echo "Unknown command: $1. Use 'help' for usage."; exit 1 ;;
esac
