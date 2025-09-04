#!/bin/bash

# Crystal Quest Game Launcher
# Simple script to run the game - use build.sh for full build system

echo "Crystal Quest - Game Launcher"
echo "============================="
echo "Note: For full build system features, use ./build.sh"
echo ""

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "game_env" ]; then
    echo "Virtual environment not found."
    echo "Please run one of the following to set up the game:"
    echo "  ./build.sh setup    (recommended)"
    echo "  make setup          (if you have make)"
    echo "  python3 build.py setup"
    exit 1
fi

echo "Activating virtual environment..."
source game_env/bin/activate

echo "Starting Crystal Quest..."
python main.py

echo "Game ended."
