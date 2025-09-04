#!/usr/bin/env python3
"""
Crystal Quest - A 2D Platformer Game
A challenging platformer with multiple levels, enemies, collectibles, and power-ups.
"""

import pygame
import sys
import json
from game.game_engine import GameEngine
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    """Main game entry point"""
    pygame.init()
    pygame.mixer.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Crystal Quest")
    clock = pygame.time.Clock()
    
    # Create game engine
    game = GameEngine(screen)
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game.handle_event(event):
                running = False  # Quit requested from game
        
        # Update game
        if not game.update(dt):
            running = False
        
        # Render game
        game.render()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
