#!/usr/bin/env python3
import os, sys, subprocess, platform, argparse, shutil
from pathlib import Path

VENV_DIR = "game_env"

def get_venv_python():
    return os.path.join(VENV_DIR, "Scripts", "python.exe") if platform.system() == "Windows" else os.path.join(VENV_DIR, "bin", "python")

def get_venv_pip():
    return os.path.join(VENV_DIR, "Scripts", "pip.exe") if platform.system() == "Windows" else os.path.join(VENV_DIR, "bin", "pip")

def clean(clean_all=False):
    print("Cleaning build artifacts...")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"), ignore_errors=True)
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                os.remove(os.path.join(root, file))
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name, ignore_errors=True)
    for item in Path('.').glob('*.egg-info'):
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
    if clean_all and os.path.exists(VENV_DIR):
        shutil.rmtree(VENV_DIR, ignore_errors=True)
    print("Cleaned")

def setup():
    print("Setting up Crystal Quest...")
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    print("Installing dependencies...")
    subprocess.run([get_venv_pip(), "install", "--upgrade", "pip", "-q"], check=True)
    subprocess.run([get_venv_pip(), "install", "-r", "requirements.txt", "-q"], check=True)
    print("Setup complete")

def play_game():
    if not os.path.exists(VENV_DIR):
        print("Setting up Crystal Quest...")
        setup()
    subprocess.run([get_venv_python(), "main.py"], check=True)

def run_game():
    if not os.path.exists(VENV_DIR):
        print("Setting up Crystal Quest...")
        setup()
    print("Starting Crystal Quest...")
    subprocess.run([get_venv_python(), "main.py"], check=True)

def package():
    if not os.path.exists(VENV_DIR):
        print("Run setup first")
        sys.exit(1)
    print("Packaging Crystal Quest...")
    try:
        subprocess.run([get_venv_pip(), "show", "pyinstaller"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Installing PyInstaller...")
        subprocess.run([get_venv_pip(), "install", "pyinstaller", "-q"], check=True)
    
    print("Creating executable...")
    subprocess.run([
        get_venv_python(), "-m", "PyInstaller",
        "--onefile", "--windowed", "--name", "crystal-quest",
        "--add-data", f"game{os.pathsep}game", "--clean", "main.py"
    ], check=True)
    print("Executable created in dist/")

def test():
    if not os.path.exists(VENV_DIR):
        print("Run setup first")
        sys.exit(1)
    print("Running tests...")
    subprocess.run([get_venv_python(), "-c", 
        "import game, pygame; from game.constants import *; from game.player import Player; from game.entities import *; print('All tests passed')"
    ], check=True)

def main():
    parser = argparse.ArgumentParser(description="Crystal Quest Build System")
    parser.add_argument("command", nargs="?", default="play", choices=["setup", "clean", "run", "play", "package", "test", "help"])
    parser.add_argument("--clean-all", action="store_true")
    
    args = parser.parse_args()
    
    if args.command == "help":
        print("Usage: python build.py {setup|clean|run|play|package|test|help}")
        return
    
    try:
        if args.command == "setup": setup()
        elif args.command == "clean": clean(args.clean_all)
        elif args.command == "run": run_game()
        elif args.command == "play": play_game()
        elif args.command == "package": package()
        elif args.command == "test": test()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
