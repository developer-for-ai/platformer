#!/usr/bin/env python3
"""
Test script for Crystal Quest build system
Verifies that all build components work correctly
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def test_build_system():
    """Test the build system components"""
    print("Testing Crystal Quest Build System")
    print("=" * 40)
    
    # Test if all build files exist
    required_files = [
        "build.sh",
        "build.bat", 
        "build.py",
        "Makefile",
        "setup.py",
        "build.cfg"
    ]
    
    print("\n1. Checking build files...")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
    
    # Test if game files exist
    game_files = [
        "main.py",
        "requirements.txt",
        "game/__init__.py",
        "game/constants.py",
        "game/player.py",
        "game/entities.py",
        "game/game_engine.py",
        "game/level.py",
        "game/effects.py"
    ]
    
    print("\n2. Checking game files...")
    for file in game_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
    
    # Test Python build script
    print("\n3. Testing Python build script...")
    try:
        result = subprocess.run([sys.executable, "build.py", "help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✓ Python build script works")
        else:
            print("  ✗ Python build script failed")
            print(f"    Error: {result.stderr}")
    except Exception as e:
        print(f"  ✗ Python build script error: {e}")
    
    # Test if scripts are executable (Unix-like systems)
    if platform.system() != "Windows":
        print("\n4. Checking script permissions...")
        executable_files = ["build.sh", "build.py", "run_game.sh"]
        for file in executable_files:
            if os.path.exists(file):
                if os.access(file, os.X_OK):
                    print(f"  ✓ {file} is executable")
                else:
                    print(f"  ✗ {file} is not executable")
                    print(f"    Fix with: chmod +x {file}")
    
    # Test requirements file
    print("\n5. Checking requirements...")
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().strip().split('\n')
            requirements = [req.strip() for req in requirements if req.strip()]
            print(f"  ✓ Found {len(requirements)} requirements:")
            for req in requirements:
                print(f"    - {req}")
    except Exception as e:
        print(f"  ✗ Error reading requirements.txt: {e}")
    
    print("\n6. Platform information...")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Python: {sys.version}")
    
    print("\n" + "=" * 40)
    print("Build system test completed!")
    print("\nTo get started:")
    print("  ./build.sh setup     (Unix/Linux/macOS)")
    print("  build.bat setup      (Windows)")
    print("  python build.py setup  (Cross-platform)")
    print("  make setup           (If you have make)")

if __name__ == "__main__":
    test_build_system()
