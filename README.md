# Crystal Quest

A 2D platformer game built with Python and Pygame. Navigate through 5 levels, collect crystals, avoid enemies, and reach the end of each stage.

## Quick Start

**Just want to play?** Run one of these commands:

- **Mac/Linux:** `./build.sh play`
- **Windows:** `build.bat play`  
- **Any platform:** `python3 build.py play`

The game will automatically install everything needed and start.

## Game Basics

**Goal:** Collect all crystals in each level and reach the exit before time runs out.

**Controls:**
- **Move:** Arrow keys or WASD
- **Jump:** Spacebar, Up arrow, or W
- **Pause:** ESC or P

**What to collect:**
- **Crystals:** Required to complete levels
- **Coins:** Extra points
- **Power-ups:** Green (double jump), Yellow (speed), Cyan (shield)

## Build Commands

All three build scripts support the same commands:

| Command | What it does |
|---------|-------------|
| `play` | Start the game (auto-setup if needed) |
| `run` | Start with detailed messages |
| `setup` | Install Python dependencies |
| `clean` | Remove temporary files |
| `package` | Create standalone executable |
| `test` | Check that everything works |
| `help` | Show command list |

**Examples:**
```bash
./build.sh setup     # First-time setup
./build.sh play      # Quick play
./build.sh package   # Create .exe file
```

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
python3 -m venv game_env
source game_env/bin/activate    # Windows: game_env\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.7 or newer
- That's it! Everything else installs automatically.

