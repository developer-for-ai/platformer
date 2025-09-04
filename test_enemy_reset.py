#!/usr/bin/env python3
"""
Simple test to verify enemy reset functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.level import LevelManager
from game.entities import Enemy
from game.constants import *

def test_enemy_reset():
    """Test that enemies reset properly when reset_enemies() is called"""
    print("Testing enemy reset functionality...")
    
    # Create a simple level with some enemies
    level_manager = LevelManager()
    current_level = level_manager.get_current_level()
    
    # Get initial enemy count and positions
    initial_count = len(current_level.enemies)
    print(f"Initial enemy count: {initial_count}")
    
    if initial_count == 0:
        print("No enemies in current level, test cannot proceed")
        return False
    
    # Store initial positions
    initial_positions = []
    for enemy in current_level.enemies:
        initial_positions.append((enemy.x, enemy.y, enemy.alive))
        print(f"Enemy at ({enemy.x}, {enemy.y}), alive: {enemy.alive}")
    
    # Kill some enemies and move others
    for i, enemy in enumerate(current_level.enemies):
        if i % 2 == 0:  # Kill every other enemy
            enemy.alive = False
            print(f"Killed enemy {i}")
        else:  # Move the others
            enemy.x += 100
            enemy.y += 50
            print(f"Moved enemy {i} to ({enemy.x}, {enemy.y})")
    
    print(f"After modifications:")
    for i, enemy in enumerate(current_level.enemies):
        print(f"Enemy {i} at ({enemy.x}, {enemy.y}), alive: {enemy.alive}")
    
    # Now reset enemies
    print("Resetting enemies...")
    current_level.reset_enemies()
    
    # Check if enemies are back to original state
    print("After reset:")
    success = True
    for i, (enemy, (orig_x, orig_y, orig_alive)) in enumerate(zip(current_level.enemies, initial_positions)):
        print(f"Enemy {i} at ({enemy.x}, {enemy.y}), alive: {enemy.alive}")
        if enemy.x != orig_x or enemy.y != orig_y or enemy.alive != orig_alive:
            print(f"ERROR: Enemy {i} not properly reset!")
            print(f"  Expected: ({orig_x}, {orig_y}), alive: {orig_alive}")
            print(f"  Got: ({enemy.x}, {enemy.y}), alive: {enemy.alive}")
            success = False
    
    if success:
        print("✓ All enemies reset correctly!")
        return True
    else:
        print("✗ Enemy reset failed!")
        return False

if __name__ == "__main__":
    try:
        success = test_enemy_reset()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
