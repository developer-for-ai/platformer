import pygame
import json
import random
import math
from game.constants import *
from game.entities import Enemy, Crystal, Coin, PowerUp

class Level:
    def __init__(self, level_data):
        self.platforms = []
        self.enemies = []
        self.crystals = []
        self.coins = []
        self.powerups = []
        self.background_color = level_data.get('background_color', BLACK)
        self.name = level_data.get('name', 'Unknown Level')
        self.time_limit = level_data.get('time_limit', LEVEL_TIME_LIMIT)
        self.crystals_required = level_data.get('crystals_required', 0)
        
        self.load_level(level_data)
    
    def load_level(self, level_data):
        # Load platforms
        for platform_data in level_data.get('platforms', []):
            platform = pygame.Rect(
                platform_data['x'],
                platform_data['y'],
                platform_data['width'],
                platform_data['height']
            )
            self.platforms.append(platform)
        
        # Load enemies
        for enemy_data in level_data.get('enemies', []):
            enemy = Enemy(
                enemy_data['x'],
                enemy_data['y'],
                enemy_data.get('type', 'walker')
            )
            self.enemies.append(enemy)
        
        # Load crystals
        for crystal_data in level_data.get('crystals', []):
            crystal = Crystal(crystal_data['x'], crystal_data['y'])
            self.crystals.append(crystal)
        
        # Load coins
        for coin_data in level_data.get('coins', []):
            coin = Coin(coin_data['x'], coin_data['y'])
            self.coins.append(coin)
        
        # Load powerups
        for powerup_data in level_data.get('powerups', []):
            powerup = PowerUp(
                powerup_data['x'],
                powerup_data['y'],
                powerup_data['type']
            )
            self.powerups.append(powerup)
    
    def update(self, dt, player):
        # Update enemies (don't remove dead ones so they can be reset)
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(dt, self.platforms, player)
        
        # Update collectibles
        for crystal in self.crystals:
            crystal.update(dt)
        
        for coin in self.coins:
            coin.update(dt)
        
        for powerup in self.powerups:
            powerup.update(dt)
        
        # Check collisions with player
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        
        # Enemy collisions
        for enemy in self.enemies:
            if player_rect.colliderect(enemy.get_rect()) and enemy.alive:
                player.take_damage()
                break
        
        # Crystal collisions
        for crystal in self.crystals:
            if not crystal.collected and player_rect.colliderect(crystal.get_rect()):
                from .effects import effects
                # Create collection effect
                effects.particle_system.create_explosion(
                    crystal.x + crystal.width // 2,
                    crystal.y + crystal.height // 2,
                    CRYSTAL_BLUE, count=15
                )
                effects.particle_system.create_sparkle(
                    crystal.x + crystal.width // 2,
                    crystal.y + crystal.height // 2,
                    WHITE, count=10
                )
                crystal.collected = True
                player.collect_crystal()
        
        # Coin collisions
        for coin in self.coins:
            if not coin.collected and player_rect.colliderect(coin.get_rect()):
                from .effects import effects
                # Create coin collection effect
                effects.particle_system.create_sparkle(
                    coin.x + coin.width // 2,
                    coin.y + coin.height // 2,
                    GOLDEN_YELLOW, count=8
                )
                coin.collected = True
                player.collect_coin()
        
        # Powerup collisions
        for powerup in self.powerups:
            if not powerup.collected and player_rect.colliderect(powerup.get_rect()):
                from .effects import effects
                # Create powerup collection effect
                powerup_colors = {
                    "double_jump": GREEN,
                    "speed_boost": GOLDEN_YELLOW,
                    "shield": CYAN
                }
                effect_color = powerup_colors.get(powerup.type, WHITE)
                effects.particle_system.create_explosion(
                    powerup.x + powerup.width // 2,
                    powerup.y + powerup.height // 2,
                    effect_color, count=20
                )
                powerup.collected = True
                player.collect_powerup(powerup.type)
    
    def is_complete(self, player):
        collected_crystals = sum(1 for crystal in self.crystals if crystal.collected)
        return collected_crystals >= self.crystals_required
    
    def render(self, screen):
        # Draw gradient background
        self.draw_gradient_background(screen)
        
        # Draw background decorations
        self.draw_background_decorations(screen)
        
        # Draw platforms with enhanced graphics
        self.draw_platforms(screen)
        
        # Draw entities
        for enemy in self.enemies:
            if enemy.alive:
                enemy.render(screen)
        
        for crystal in self.crystals:
            crystal.render(screen)
        
        for coin in self.coins:
            coin.render(screen)
        
        for powerup in self.powerups:
            powerup.render(screen)
    
    def draw_gradient_background(self, screen):
        """Draw a beautiful gradient background"""
        level_num = self.get_level_number()
        if level_num in BACKGROUND_GRADIENTS:
            top_color, bottom_color = BACKGROUND_GRADIENTS[level_num]
        else:
            top_color, bottom_color = BACKGROUND_GRADIENTS[0]
        
        # Draw gradient
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = tuple(
                int(top_color[i] * (1 - ratio) + bottom_color[i] * ratio)
                for i in range(3)
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    
    def draw_background_decorations(self, screen):
        """Draw decorative background elements"""
        level_num = self.get_level_number()
        
        if level_num == 0:  # Tutorial - clouds
            self.draw_clouds(screen)
        elif level_num == 1:  # Sky level - stars
            self.draw_stars(screen)
        elif level_num == 2:  # Cave - stalactites
            self.draw_cave_decorations(screen)
        elif level_num == 3:  # Crystal - crystals in background
            self.draw_crystal_decorations(screen)
        elif level_num == 4:  # Final - ancient ruins
            self.draw_ruin_decorations(screen)
    
    def draw_clouds(self, screen):
        """Draw simple cloud shapes"""
        cloud_positions = [(200, 100), (600, 150), (1000, 80), (400, 200)]
        for x, y in cloud_positions:
            # Simple cloud made of circles
            cloud_color = (255, 255, 255, 100)
            for i, (offset_x, offset_y, size) in enumerate([
                (0, 0, 30), (25, 5, 25), (50, 0, 30), (15, -15, 20), (35, -10, 18)
            ]):
                cloud_surface = pygame.Surface((size * 2, size * 2))
                cloud_surface.set_alpha(80)
                cloud_surface.fill((255, 255, 255))
                pygame.draw.circle(cloud_surface, (255, 255, 255), (size, size), size)
                screen.blit(cloud_surface, (x + offset_x - size, y + offset_y - size))
    
    def draw_stars(self, screen):
        """Draw twinkling stars"""
        import random
        random.seed(42)  # Consistent star positions
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            size = random.randint(1, 3)
            # Simple twinkling effect
            alpha = 100 + int(50 * math.sin(pygame.time.get_ticks() * 0.01 + x * 0.01))
            star_surface = pygame.Surface((size * 2, size * 2))
            star_surface.set_alpha(alpha)
            pygame.draw.circle(star_surface, WHITE, (size, size), size)
            screen.blit(star_surface, (x - size, y - size))
    
    def draw_cave_decorations(self, screen):
        """Draw cave stalactites and stalagmites"""
        # Stalactites from ceiling
        stalactite_positions = [(100, 0), (300, 0), (500, 0), (800, 0), (1000, 0)]
        for x, y in stalactite_positions:
            height = 40 + (x % 30)
            points = [(x, y), (x - 8, y), (x - 4, y + height), (x + 4, y + height), (x + 8, y)]
            pygame.draw.polygon(screen, GRAY, points)
            pygame.draw.polygon(screen, WHITE, points, 1)
    
    def draw_crystal_decorations(self, screen):
        """Draw background crystals"""
        crystal_positions = [(150, 300), (400, 200), (750, 400), (950, 250)]
        for x, y in crystal_positions:
            size = 15
            points = [(x, y), (x + size, y + size), (x, y + size * 2), (x - size, y + size)]
            pygame.draw.polygon(screen, CRYSTAL_BLUE, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
    
    def draw_ruin_decorations(self, screen):
        """Draw ancient ruin pillars"""
        pillar_positions = [(100, SCREEN_HEIGHT - 200), (900, SCREEN_HEIGHT - 180)]
        for x, y in pillar_positions:
            width, height = 40, 150
            # Pillar body
            pillar_rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(screen, GRAY, pillar_rect)
            # Pillar top
            top_rect = pygame.Rect(x - 5, y - 10, width + 10, 15)
            pygame.draw.rect(screen, LIGHT_BLUE, top_rect)
            pygame.draw.rect(screen, WHITE, pillar_rect, 2)
            pygame.draw.rect(screen, WHITE, top_rect, 2)
    
    def draw_platforms(self, screen):
        """Draw platforms with enhanced graphics"""
        level_num = self.get_level_number()
        platform_color = PLATFORM_COLORS.get(level_num, WHITE)
        
        for platform in self.platforms:
            # Draw platform shadow
            shadow_rect = pygame.Rect(platform.x + SHADOW_OFFSET, 
                                    platform.y + SHADOW_OFFSET,
                                    platform.width, platform.height)
            shadow_surface = pygame.Surface((platform.width, platform.height))
            shadow_surface.set_alpha(100)
            shadow_surface.fill((20, 20, 20))
            screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))
            
            # Draw main platform with gradient
            top_color = tuple(min(255, c + 30) for c in platform_color)
            bottom_color = tuple(max(0, c - 30) for c in platform_color)
            
            # Top part (lighter)
            top_rect = pygame.Rect(platform.x, platform.y, 
                                 platform.width, platform.height // 2)
            pygame.draw.rect(screen, top_color, top_rect)
            
            # Bottom part (darker)
            bottom_rect = pygame.Rect(platform.x, platform.y + platform.height // 2,
                                    platform.width, platform.height // 2)
            pygame.draw.rect(screen, bottom_color, bottom_rect)
            
            # Draw border
            pygame.draw.rect(screen, WHITE, platform, BORDER_WIDTH)
            
            # Draw platform texture/pattern
            if level_num == 1:  # Sky level - cloud pattern
                for i in range(0, platform.width, 20):
                    pygame.draw.circle(screen, (255, 255, 255, 50), 
                                     (platform.x + i + 10, platform.y + platform.height // 2), 8)
            elif level_num == 2:  # Cave level - rocky texture
                for i in range(0, platform.width, 15):
                    for j in range(0, platform.height, 8):
                        if (i + j) % 30 < 15:
                            dot_rect = pygame.Rect(platform.x + i, platform.y + j, 3, 3)
                            pygame.draw.rect(screen, DARK_GRAY, dot_rect)
            elif level_num == 3:  # Crystal level - crystal pattern
                for i in range(0, platform.width, 25):
                    crystal_x = platform.x + i + 12
                    crystal_y = platform.y + platform.height // 2
                    crystal_points = [(crystal_x, crystal_y - 3), (crystal_x + 3, crystal_y),
                                    (crystal_x, crystal_y + 3), (crystal_x - 3, crystal_y)]
                    pygame.draw.polygon(screen, CYAN, crystal_points)
    
    def get_level_number(self):
        """Get the current level number for theming"""
        # This is a simple way to determine level - you might want to store this explicitly
        if "Tutorial" in self.name:
            return 0
        elif "Skyward" in self.name:
            return 1
        elif "Monster" in self.name or "Cavern" in self.name:
            return 2
        elif "Crystal" in self.name or "Spire" in self.name:
            return 3
        elif "Fortress" in self.name:
            return 4
        return 0

    def reset_collectibles(self):
        """Reset all collectibles to their uncollected state"""
        for crystal in self.crystals:
            crystal.collected = False
        
        for coin in self.coins:
            coin.collected = False
        
        for powerup in self.powerups:
            powerup.collected = False
    
    def reset_enemies(self):
        """Reset all enemies to their starting positions and states"""
        for enemy in self.enemies:
            enemy.alive = True
            enemy.x = enemy.start_x
            enemy.y = enemy.start_y
            enemy.vel_y = 0
            enemy.animation_timer = 0
            
            # Reset type-specific properties
            if enemy.type == "walker":
                enemy.vel_x = ENEMY_SPEED if enemy.vel_x > 0 else -ENEMY_SPEED
            elif enemy.type == "jumper":
                enemy.vel_x = 0
                enemy.jump_timer = 0
            elif enemy.type == "flyer":
                enemy.vel_x = 0


class LevelManager:
    def __init__(self):
        self.current_level = 0
        self.levels = self.create_levels()
    
    def create_levels(self):
        """Create predefined levels"""
        levels = []
        
        # Level 1: Tutorial
        level1_data = {
            'name': 'Tutorial Valley',
            'background_color': (50, 100, 150),
            'crystals_required': 3,
            'platforms': [
                {'x': 0, 'y': SCREEN_HEIGHT - 20, 'width': SCREEN_WIDTH, 'height': 20},  # Ground
                {'x': 200, 'y': SCREEN_HEIGHT - 120, 'width': 150, 'height': 20},
                {'x': 450, 'y': SCREEN_HEIGHT - 200, 'width': 150, 'height': 20},
                {'x': 700, 'y': SCREEN_HEIGHT - 280, 'width': 150, 'height': 20},
                {'x': 950, 'y': SCREEN_HEIGHT - 150, 'width': 200, 'height': 20},
            ],
            'enemies': [
                {'x': 500, 'y': SCREEN_HEIGHT - 220, 'type': 'walker'},
            ],
            'crystals': [
                {'x': 250, 'y': SCREEN_HEIGHT - 160},
                {'x': 500, 'y': SCREEN_HEIGHT - 240},
                {'x': 1000, 'y': SCREEN_HEIGHT - 190},
            ],
            'coins': [
                {'x': 100, 'y': SCREEN_HEIGHT - 60},
                {'x': 300, 'y': SCREEN_HEIGHT - 160},
                {'x': 600, 'y': SCREEN_HEIGHT - 320},
                {'x': 800, 'y': SCREEN_HEIGHT - 60},
            ],
            'powerups': [
                {'x': 750, 'y': SCREEN_HEIGHT - 320, 'type': 'double_jump'},
            ]
        }
        levels.append(Level(level1_data))
        
        # Level 2: Jumping Challenge
        level2_data = {
            'name': 'Skyward Peaks',
            'background_color': (100, 50, 100),
            'crystals_required': 4,
            'platforms': [
                {'x': 0, 'y': SCREEN_HEIGHT - 20, 'width': 200, 'height': 20},
                {'x': 300, 'y': SCREEN_HEIGHT - 100, 'width': 120, 'height': 20},
                {'x': 500, 'y': SCREEN_HEIGHT - 180, 'width': 120, 'height': 20},
                {'x': 700, 'y': SCREEN_HEIGHT - 240, 'width': 120, 'height': 20},
                {'x': 900, 'y': SCREEN_HEIGHT - 320, 'width': 120, 'height': 20},
                {'x': 1050, 'y': SCREEN_HEIGHT - 200, 'width': 150, 'height': 20},  # Right side platform
                {'x': 850, 'y': SCREEN_HEIGHT - 400, 'width': 200, 'height': 20},  # High platform (reachable with double jump)
                {'x': 600, 'y': SCREEN_HEIGHT - 360, 'width': 150, 'height': 20},  # Step to high platform
                {'x': 400, 'y': SCREEN_HEIGHT - 320, 'width': 120, 'height': 20},  # Another step
                {'x': 200, 'y': SCREEN_HEIGHT - 280, 'width': 120, 'height': 20},  # Left side steps
                {'x': 50, 'y': SCREEN_HEIGHT - 200, 'width': 100, 'height': 20},   # Lower left platform
            ],
            'enemies': [
                {'x': 350, 'y': SCREEN_HEIGHT - 120, 'type': 'jumper'},
                {'x': 750, 'y': SCREEN_HEIGHT - 260, 'type': 'walker'},
                {'x': 450, 'y': SCREEN_HEIGHT - 340, 'type': 'flyer'},
            ],
            'crystals': [
                {'x': 350, 'y': SCREEN_HEIGHT - 140},
                {'x': 750, 'y': SCREEN_HEIGHT - 280},
                {'x': 950, 'y': SCREEN_HEIGHT - 360},
                {'x': 900, 'y': SCREEN_HEIGHT - 440},  # On the high platform
            ],
            'coins': [
                {'x': 550, 'y': SCREEN_HEIGHT - 220},
                {'x': 1100, 'y': SCREEN_HEIGHT - 240},
                {'x': 250, 'y': SCREEN_HEIGHT - 320},
                {'x': 650, 'y': SCREEN_HEIGHT - 400},
                {'x': 100, 'y': SCREEN_HEIGHT - 240},
            ],
            'powerups': [
                {'x': 250, 'y': SCREEN_HEIGHT - 320, 'type': 'double_jump'},  # Needed to reach high platform
                {'x': 950, 'y': SCREEN_HEIGHT - 440, 'type': 'speed_boost'},  # Reward on high platform
            ]
        }
        levels.append(Level(level2_data))
        
        # Level 3: Enemy Gauntlet
        level3_data = {
            'name': 'Monster Caverns',
            'background_color': (150, 50, 50),
            'crystals_required': 5,
            'platforms': [
                {'x': 0, 'y': SCREEN_HEIGHT - 20, 'width': SCREEN_WIDTH, 'height': 20},
                {'x': 150, 'y': SCREEN_HEIGHT - 100, 'width': 100, 'height': 20},
                {'x': 350, 'y': SCREEN_HEIGHT - 100, 'width': 100, 'height': 20},
                {'x': 550, 'y': SCREEN_HEIGHT - 100, 'width': 100, 'height': 20},
                {'x': 750, 'y': SCREEN_HEIGHT - 100, 'width': 100, 'height': 20},
                {'x': 950, 'y': SCREEN_HEIGHT - 100, 'width': 100, 'height': 20},
                {'x': 250, 'y': SCREEN_HEIGHT - 200, 'width': 200, 'height': 20},
                {'x': 650, 'y': SCREEN_HEIGHT - 200, 'width': 200, 'height': 20},
                {'x': 450, 'y': SCREEN_HEIGHT - 300, 'width': 150, 'height': 20},
                {'x': 200, 'y': SCREEN_HEIGHT - 400, 'width': 100, 'height': 20},
                {'x': 600, 'y': SCREEN_HEIGHT - 400, 'width': 100, 'height': 20},
            ],
            'enemies': [
                {'x': 200, 'y': SCREEN_HEIGHT - 120, 'type': 'walker'},
                {'x': 400, 'y': SCREEN_HEIGHT - 120, 'type': 'jumper'},
                {'x': 600, 'y': SCREEN_HEIGHT - 120, 'type': 'walker'},
                {'x': 800, 'y': SCREEN_HEIGHT - 120, 'type': 'jumper'},
                {'x': 300, 'y': SCREEN_HEIGHT - 150, 'type': 'flyer'},
                {'x': 700, 'y': SCREEN_HEIGHT - 150, 'type': 'flyer'},
                {'x': 500, 'y': SCREEN_HEIGHT - 320, 'type': 'walker'},
            ],
            'crystals': [
                {'x': 200, 'y': SCREEN_HEIGHT - 140},
                {'x': 500, 'y': SCREEN_HEIGHT - 340},
                {'x': 250, 'y': SCREEN_HEIGHT - 440},
                {'x': 650, 'y': SCREEN_HEIGHT - 440},
                {'x': 1050, 'y': SCREEN_HEIGHT - 60},
            ],
            'coins': [
                {'x': 400, 'y': SCREEN_HEIGHT - 140},
                {'x': 800, 'y': SCREEN_HEIGHT - 140},
                {'x': 350, 'y': SCREEN_HEIGHT - 240},
                {'x': 750, 'y': SCREEN_HEIGHT - 240},
                {'x': 500, 'y': SCREEN_HEIGHT - 340},
            ],
            'powerups': [
                {'x': 350, 'y': SCREEN_HEIGHT - 240, 'type': 'shield'},
                {'x': 500, 'y': SCREEN_HEIGHT - 340, 'type': 'speed_boost'},
                {'x': 250, 'y': SCREEN_HEIGHT - 440, 'type': 'double_jump'},
            ]
        }
        levels.append(Level(level3_data))
        
        # Level 4: Precision Platforming
        level4_data = {
            'name': 'Crystal Spires',
            'background_color': (50, 150, 100),
            'crystals_required': 6,
            'platforms': [
                {'x': 0, 'y': SCREEN_HEIGHT - 20, 'width': 100, 'height': 20},
                {'x': 200, 'y': SCREEN_HEIGHT - 80, 'width': 80, 'height': 20},
                {'x': 350, 'y': SCREEN_HEIGHT - 140, 'width': 60, 'height': 20},
                {'x': 480, 'y': SCREEN_HEIGHT - 200, 'width': 80, 'height': 20},
                {'x': 630, 'y': SCREEN_HEIGHT - 260, 'width': 60, 'height': 20},
                {'x': 750, 'y': SCREEN_HEIGHT - 320, 'width': 80, 'height': 20},
                {'x': 900, 'y': SCREEN_HEIGHT - 380, 'width': 60, 'height': 20},
                {'x': 1050, 'y': SCREEN_HEIGHT - 440, 'width': 100, 'height': 20},
                {'x': 850, 'y': SCREEN_HEIGHT - 500, 'width': 150, 'height': 20},
                {'x': 500, 'y': SCREEN_HEIGHT - 560, 'width': 200, 'height': 20},
                {'x': 200, 'y': SCREEN_HEIGHT - 620, 'width': 100, 'height': 20},
            ],
            'enemies': [
                {'x': 250, 'y': SCREEN_HEIGHT - 100, 'type': 'flyer'},
                {'x': 520, 'y': SCREEN_HEIGHT - 220, 'type': 'walker'},
                {'x': 780, 'y': SCREEN_HEIGHT - 340, 'type': 'jumper'},
                {'x': 600, 'y': SCREEN_HEIGHT - 400, 'type': 'flyer'},
                {'x': 900, 'y': SCREEN_HEIGHT - 520, 'type': 'walker'},
            ],
            'crystals': [
                {'x': 230, 'y': SCREEN_HEIGHT - 120},
                {'x': 380, 'y': SCREEN_HEIGHT - 180},
                {'x': 660, 'y': SCREEN_HEIGHT - 300},
                {'x': 930, 'y': SCREEN_HEIGHT - 420},
                {'x': 900, 'y': SCREEN_HEIGHT - 540},
                {'x': 250, 'y': SCREEN_HEIGHT - 660},
            ],
            'coins': [
                {'x': 50, 'y': SCREEN_HEIGHT - 60},
                {'x': 240, 'y': SCREEN_HEIGHT - 120},
                {'x': 390, 'y': SCREEN_HEIGHT - 180},
                {'x': 520, 'y': SCREEN_HEIGHT - 240},
                {'x': 670, 'y': SCREEN_HEIGHT - 300},
                {'x': 790, 'y': SCREEN_HEIGHT - 360},
                {'x': 940, 'y': SCREEN_HEIGHT - 420},
                {'x': 600, 'y': SCREEN_HEIGHT - 600},
            ],
            'powerups': [
                {'x': 240, 'y': SCREEN_HEIGHT - 120, 'type': 'double_jump'},
                {'x': 790, 'y': SCREEN_HEIGHT - 360, 'type': 'speed_boost'},
                {'x': 950, 'y': SCREEN_HEIGHT - 540, 'type': 'shield'},
            ]
        }
        levels.append(Level(level4_data))
        
        # Level 5: Final Challenge
        level5_data = {
            'name': 'The Crystal Fortress',
            'background_color': (100, 100, 50),
            'crystals_required': 8,
            'platforms': [
                {'x': 0, 'y': SCREEN_HEIGHT - 20, 'width': 150, 'height': 20},
                {'x': 250, 'y': SCREEN_HEIGHT - 80, 'width': 100, 'height': 20},
                {'x': 450, 'y': SCREEN_HEIGHT - 60, 'width': 100, 'height': 20},
                {'x': 650, 'y': SCREEN_HEIGHT - 120, 'width': 100, 'height': 20},
                {'x': 850, 'y': SCREEN_HEIGHT - 180, 'width': 100, 'height': 20},
                {'x': 1050, 'y': SCREEN_HEIGHT - 240, 'width': 150, 'height': 20},
                {'x': 900, 'y': SCREEN_HEIGHT - 320, 'width': 120, 'height': 20},
                {'x': 700, 'y': SCREEN_HEIGHT - 280, 'width': 100, 'height': 20},
                {'x': 500, 'y': SCREEN_HEIGHT - 240, 'width': 100, 'height': 20},
                {'x': 300, 'y': SCREEN_HEIGHT - 200, 'width': 100, 'height': 20},
                {'x': 100, 'y': SCREEN_HEIGHT - 160, 'width': 100, 'height': 20},
                {'x': 200, 'y': SCREEN_HEIGHT - 320, 'width': 150, 'height': 20},
                {'x': 450, 'y': SCREEN_HEIGHT - 400, 'width': 100, 'height': 20},
                {'x': 650, 'y': SCREEN_HEIGHT - 480, 'width': 100, 'height': 20},
                {'x': 850, 'y': SCREEN_HEIGHT - 560, 'width': 200, 'height': 20},
                {'x': 400, 'y': SCREEN_HEIGHT - 640, 'width': 400, 'height': 20},
            ],
            'enemies': [
                {'x': 300, 'y': SCREEN_HEIGHT - 100, 'type': 'walker'},
                {'x': 500, 'y': SCREEN_HEIGHT - 80, 'type': 'jumper'},
                {'x': 700, 'y': SCREEN_HEIGHT - 140, 'type': 'walker'},
                {'x': 900, 'y': SCREEN_HEIGHT - 200, 'type': 'jumper'},
                {'x': 350, 'y': SCREEN_HEIGHT - 150, 'type': 'flyer'},
                {'x': 550, 'y': SCREEN_HEIGHT - 200, 'type': 'flyer'},
                {'x': 750, 'y': SCREEN_HEIGHT - 250, 'type': 'flyer'},
                {'x': 950, 'y': SCREEN_HEIGHT - 340, 'type': 'walker'},
                {'x': 250, 'y': SCREEN_HEIGHT - 340, 'type': 'jumper'},
                {'x': 500, 'y': SCREEN_HEIGHT - 420, 'type': 'walker'},
                {'x': 700, 'y': SCREEN_HEIGHT - 500, 'type': 'jumper'},
            ],
            'crystals': [
                {'x': 300, 'y': SCREEN_HEIGHT - 120},
                {'x': 700, 'y': SCREEN_HEIGHT - 160},
                {'x': 1100, 'y': SCREEN_HEIGHT - 280},
                {'x': 350, 'y': SCREEN_HEIGHT - 240},
                {'x': 150, 'y': SCREEN_HEIGHT - 200},
                {'x': 500, 'y': SCREEN_HEIGHT - 280},
                {'x': 700, 'y': SCREEN_HEIGHT - 520},
                {'x': 600, 'y': SCREEN_HEIGHT - 680},
            ],
            'coins': [
                {'x': 75, 'y': SCREEN_HEIGHT - 60},
                {'x': 300, 'y': SCREEN_HEIGHT - 120},
                {'x': 500, 'y': SCREEN_HEIGHT - 100},
                {'x': 700, 'y': SCREEN_HEIGHT - 160},
                {'x': 900, 'y': SCREEN_HEIGHT - 220},
                {'x': 950, 'y': SCREEN_HEIGHT - 360},
                {'x': 750, 'y': SCREEN_HEIGHT - 320},
                {'x': 550, 'y': SCREEN_HEIGHT - 280},
                {'x': 275, 'y': SCREEN_HEIGHT - 360},
                {'x': 500, 'y': SCREEN_HEIGHT - 440},
                {'x': 700, 'y': SCREEN_HEIGHT - 520},
                {'x': 500, 'y': SCREEN_HEIGHT - 680},
                {'x': 700, 'y': SCREEN_HEIGHT - 680},
            ],
            'powerups': [
                {'x': 500, 'y': SCREEN_HEIGHT - 100, 'type': 'speed_boost'},
                {'x': 150, 'y': SCREEN_HEIGHT - 200, 'type': 'double_jump'},
                {'x': 950, 'y': SCREEN_HEIGHT - 360, 'type': 'shield'},
                {'x': 500, 'y': SCREEN_HEIGHT - 440, 'type': 'speed_boost'},
                {'x': 950, 'y': SCREEN_HEIGHT - 600, 'type': 'shield'},
            ]
        }
        levels.append(Level(level5_data))
        
        return levels
    
    def get_current_level(self):
        if self.current_level < len(self.levels):
            return self.levels[self.current_level]
        return None
    
    def next_level(self):
        self.current_level += 1
        return self.get_current_level()
    
    def has_more_levels(self):
        return self.current_level < len(self.levels)
    
    def get_total_levels(self):
        return len(self.levels)
