# Crystal Quest

A 2D platformer game built with Python and Pygame. Collect crystals, avoid enemies, and complete 5 challenging levels.

## Quick Start

**Unix/Linux/macOS:** `./build.sh play`  
**Windows:** `build.bat play`  
**Cross-platform:** `python3 build.py play`

## Controls

- **Movement:** Arrow Keys or WASD
- **Jump:** Spacebar, Up Arrow, or W
- **Pause:** ESC or P

## Commands

| Command | Description |
|---------|-------------|
| `play` | Quick play (default) |
| `run` | Run with output |
| `setup` | Install dependencies |
| `clean` | Clean build files |
| `package` | Create executable |
| `test` | Run tests |

## Manual Install

```bash
python3 -m venv game_env
source game_env/bin/activate  # Windows: game_env\Scripts\activate
pip install -r requirements.txt
python main.py
```

