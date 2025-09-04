import pygame
import random
import math
from game.constants import *

class Enemy:
    def __init__(self, x, y, enemy_type="walker"):
        self.x = x
        self.y = y
        self.start_x = x  # Store original position
        self.start_y = y  # Store original position
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        self.vel_x = ENEMY_SPEED
        self.vel_y = 0
        self.type = enemy_type
        self.alive = True
        self.animation_timer = 0
        
        # Type-specific properties
        if enemy_type == "walker":
            self.color = RED
            self.patrol_distance = 100
        elif enemy_type == "jumper":
            self.color = ORANGE
            self.jump_timer = 0
            self.jump_cooldown = 2.0
        elif enemy_type == "flyer":
            self.color = PURPLE
            self.float_amplitude = 30
            self.float_speed = 2.0
    
    def update(self, dt, platforms, player):
        if not self.alive:
            return
        
        self.animation_timer += dt
        
        if self.type == "walker":
            self.update_walker(dt, platforms)
        elif self.type == "jumper":
            self.update_jumper(dt, platforms, player)
        elif self.type == "flyer":
            self.update_flyer(dt, player)
        
        # Apply gravity for non-flying enemies
        if self.type != "flyer":
            self.vel_y += GRAVITY * dt
            self.y += self.vel_y * dt
            
            # Handle platform collisions
            self.handle_collisions(platforms)
        
        # Remove if fallen off screen
        if self.y > SCREEN_HEIGHT + 100:
            self.alive = False
    
    def update_walker(self, dt, platforms):
        # Simple patrol behavior
        self.x += self.vel_x * dt
        
        # Turn around at patrol boundaries
        if abs(self.x - self.start_x) > self.patrol_distance:
            self.vel_x *= -1
        
        # Turn around at platform edges
        future_x = self.x + self.vel_x * dt * 2
        standing_on_platform = False
        
        for platform in platforms:
            # Check if enemy will still be on a platform
            if (platform.top <= self.y + self.height <= platform.top + 10 and
                platform.left <= future_x + self.width//2 <= platform.right):
                standing_on_platform = True
                break
        
        if not standing_on_platform:
            self.vel_x *= -1
    
    def update_jumper(self, dt, platforms, player):
        # Jump towards player occasionally
        self.jump_timer += dt
        
        if self.jump_timer >= self.jump_cooldown and self.vel_y == 0:
            # Calculate direction to player
            dx = player.x - self.x
            if abs(dx) < 200:  # Only jump if player is nearby
                self.vel_x = ENEMY_SPEED * (1 if dx > 0 else -1)
                self.vel_y = -PLAYER_JUMP_SPEED * 0.7
                self.jump_timer = 0
        
        self.x += self.vel_x * dt
        self.vel_x *= 0.95  # Air resistance
    
    def update_flyer(self, dt, player):
        # Float up and down
        self.y = self.start_y + math.sin(self.animation_timer * self.float_speed) * self.float_amplitude
        
        # Move towards player horizontally
        dx = player.x - self.x
        if abs(dx) > 10:
            self.vel_x = ENEMY_SPEED * 0.5 * (1 if dx > 0 else -1)
            self.x += self.vel_x * dt
    
    def handle_collisions(self, platforms):
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            if enemy_rect.colliderect(platform):
                if self.vel_y > 0:  # Falling down
                    self.y = platform.top - self.height
                    self.vel_y = 0
                elif self.vel_y < 0:  # Jumping up
                    self.y = platform.bottom
                    self.vel_y = 0
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def render(self, screen):
        if not self.alive:
            return
        
        # Draw shadow directly without surface
        shadow_rect = pygame.Rect(self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET, self.width, self.height)
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect)
        
        # Draw enemy body with gradient
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Create gradient effect
        top_color = tuple(int(min(255, c + 30)) for c in self.color)
        bottom_color = tuple(int(max(0, c - 30)) for c in self.color)
        
        # Top half
        top_rect = pygame.Rect(self.x, self.y, self.width, self.height//2)
        pygame.draw.rect(screen, top_color, top_rect)
        
        # Bottom half
        bottom_rect = pygame.Rect(self.x, self.y + self.height//2, self.width, self.height//2)
        pygame.draw.rect(screen, bottom_color, bottom_rect)
        
        # Border
        pygame.draw.rect(screen, WHITE, enemy_rect, 2)
        
        # Draw type-specific features
        if self.type == "walker":
            # Draw legs with animation
            leg_offset = int(math.sin(self.animation_timer * 6) * 2)
            leg_width = 4
            leg_height = 8
            left_leg = pygame.Rect(self.x + 4, self.y + self.height + leg_offset, 
                                 leg_width, leg_height)
            right_leg = pygame.Rect(self.x + self.width - 8, self.y + self.height - leg_offset, 
                                  leg_width, leg_height)
            pygame.draw.rect(screen, self.color, left_leg)
            pygame.draw.rect(screen, self.color, right_leg)
            pygame.draw.rect(screen, WHITE, left_leg, 1)
            pygame.draw.rect(screen, WHITE, right_leg, 1)
        
        elif self.type == "jumper":
            # Draw animated spring
            spring_compression = max(0, -self.vel_y / 200)  # Compress when jumping
            spring_height = 8 - int(spring_compression * 4)
            spring_points = []
            for i in range(6):
                x = self.x + (i * self.width // 5)
                y = self.y + self.height + (spring_height if i % 2 else 0)
                spring_points.append((x, y))
            if len(spring_points) > 1:
                pygame.draw.lines(screen, WHITE, False, spring_points, 3)
                pygame.draw.lines(screen, self.color, False, spring_points, 1)
        
        elif self.type == "flyer":
            # Draw animated wings
            wing_flap = math.sin(self.animation_timer * 10) * 3
            wing_size = 8
            
            # Left wing
            left_wing = [(self.x - wing_size, self.y + wing_size + wing_flap),
                        (self.x, self.y + 4),
                        (self.x, self.y + wing_size + 2)]
            pygame.draw.polygon(screen, LIGHT_BLUE, left_wing)
            pygame.draw.polygon(screen, WHITE, left_wing, 2)
            
            # Right wing
            right_wing = [(self.x + self.width, self.y + 4),
                         (self.x + self.width + wing_size, self.y + wing_size + wing_flap),
                         (self.x + self.width, self.y + wing_size + 2)]
            pygame.draw.polygon(screen, LIGHT_BLUE, right_wing)
            pygame.draw.polygon(screen, WHITE, right_wing, 2)
        
        # Draw eyes with animation
        eye_size = 4
        blink = int(self.animation_timer * 3) % 60 < 3  # Blink occasionally
        
        if not blink:
            left_eye_pos = (self.x + 6, self.y + 6)
            right_eye_pos = (self.x + self.width - 10, self.y + 6)
            
            pygame.draw.circle(screen, WHITE, left_eye_pos, eye_size//2)
            pygame.draw.circle(screen, WHITE, right_eye_pos, eye_size//2)
            pygame.draw.circle(screen, RED, left_eye_pos, eye_size//4)
            pygame.draw.circle(screen, RED, right_eye_pos, eye_size//4)
        else:
            # Draw closed eyes (lines)
            pygame.draw.line(screen, WHITE, (self.x + 4, self.y + 6), (self.x + 8, self.y + 6), 2)
            pygame.draw.line(screen, WHITE, (self.x + self.width - 12, self.y + 6), 
                           (self.x + self.width - 8, self.y + 6), 2)


class Crystal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CRYSTAL_SIZE
        self.height = CRYSTAL_SIZE
        self.collected = False
        self.animation_timer = 0
        self.float_offset = 0
    
    def update(self, dt):
        self.animation_timer += dt
        self.float_offset = math.sin(self.animation_timer * 3) * 5
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.float_offset, self.width, self.height)
    
    def render(self, screen):
        if self.collected:
            return
        
        # Draw crystal with floating animation and glow effect
        y_pos = self.y + self.float_offset
        center_x = self.x + self.width // 2
        center_y = y_pos + self.height // 2
        
        # Draw glow effect
        glow_radius = self.width + int(math.sin(self.animation_timer * 4) * 4)
        # Draw glow directly without surface
        pygame.draw.circle(screen, (50, 150, 200), (center_x, center_y), glow_radius)
        
        # Draw crystal shadow directly
        shadow_points = [
            (center_x + SHADOW_OFFSET, y_pos + SHADOW_OFFSET),  # Top
            (self.x + self.width + SHADOW_OFFSET, center_y + SHADOW_OFFSET),  # Right
            (center_x + SHADOW_OFFSET, y_pos + self.height + SHADOW_OFFSET),  # Bottom
            (self.x + SHADOW_OFFSET, center_y + SHADOW_OFFSET)  # Left
        ]
        pygame.draw.polygon(screen, (20, 20, 20), shadow_points)
        
        # Draw main crystal diamond with gradient
        points = [
            (center_x, y_pos),  # Top
            (self.x + self.width, center_y),  # Right
            (center_x, y_pos + self.height),  # Bottom
            (self.x, center_y)  # Left
        ]
        
        # Draw filled crystal with gradient effect
        pygame.draw.polygon(screen, CYAN, points)
        
        # Draw inner diamond (lighter)
        inner_size = 0.6
        inner_points = [
            (center_x, y_pos + self.height * (1 - inner_size) / 2),
            (self.x + self.width * (1 + inner_size) / 2, center_y),
            (center_x, y_pos + self.height * (1 + inner_size) / 2),
            (self.x + self.width * (1 - inner_size) / 2, center_y)
        ]
        pygame.draw.polygon(screen, CRYSTAL_BLUE, inner_points)
        
        # Draw highlight
        highlight_points = [
            (center_x, y_pos + 2),
            (self.x + self.width - 2, center_y),
            (center_x, y_pos + 4),
            (self.x + 2, center_y)
        ]
        pygame.draw.polygon(screen, WHITE, highlight_points)
        
        # Draw border
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Draw sparkle effects
        sparkle_count = 3
        for i in range(sparkle_count):
            angle = (self.animation_timer * 2 + i * 2.1) % (2 * math.pi)
            sparkle_dist = self.width // 2 + 8
            sparkle_x = center_x + math.cos(angle) * sparkle_dist
            sparkle_y = center_y + math.sin(angle) * sparkle_dist
            sparkle_size = 2 + int(math.sin(self.animation_timer * 5 + i) * 1)
            pygame.draw.circle(screen, WHITE, (int(sparkle_x), int(sparkle_y)), sparkle_size)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = COIN_SIZE
        self.height = COIN_SIZE
        self.collected = False
        self.animation_timer = 0
        self.rotation = 0
    
    def update(self, dt):
        self.animation_timer += dt
        self.rotation += dt * 180  # Rotate 180 degrees per second
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def render(self, screen):
        if self.collected:
            return
        
        # Draw spinning coin with 3D effect
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Calculate spinning effect
        width_factor = abs(math.cos(math.radians(self.rotation)))
        coin_width = max(3, int(self.width * width_factor))
        
        # Draw shadow that rotates with the coin
        shadow_width = max(3, int(self.width * width_factor))
        shadow_center_x = center_x + SHADOW_OFFSET
        shadow_center_y = center_y + SHADOW_OFFSET
        shadow_rect = pygame.Rect(shadow_center_x - shadow_width//2, shadow_center_y - self.height//2, 
                                shadow_width, self.height)
        pygame.draw.ellipse(screen, (20, 20, 20), shadow_rect)
        
        # Draw outer ring (bronze/copper color)
        outer_rect = pygame.Rect(center_x - coin_width//2, self.y, coin_width, self.height)
        pygame.draw.ellipse(screen, BRONZE, outer_rect)
        
        # Draw inner coin (gold)
        inner_width = max(2, coin_width - 4)
        inner_height = self.height - 4
        inner_rect = pygame.Rect(center_x - inner_width//2, self.y + 2, inner_width, inner_height)
        pygame.draw.ellipse(screen, GOLDEN_YELLOW, inner_rect)
        
        # Draw highlight when coin is facing forward
        if width_factor > 0.7:
            highlight_width = max(1, inner_width - 4)
            highlight_height = inner_height - 4
            highlight_rect = pygame.Rect(center_x - highlight_width//2, self.y + 4, 
                                       highlight_width, highlight_height)
            pygame.draw.ellipse(screen, WHITE, highlight_rect)
        
        # Draw border
        pygame.draw.ellipse(screen, WHITE, outer_rect, 2)
        
        # Draw coin value symbol ($) when facing forward
        if width_factor > 0.8:
            font_size = max(8, int(self.height * 0.6))
            # Simple $ symbol using lines
            symbol_x = center_x
            symbol_y = center_y
            pygame.draw.line(screen, BRONZE, 
                           (symbol_x, symbol_y - 4), (symbol_x, symbol_y + 4), 2)
            pygame.draw.arc(screen, BRONZE, 
                          pygame.Rect(symbol_x - 3, symbol_y - 3, 6, 3), 
                          0, math.pi, 2)
            pygame.draw.arc(screen, BRONZE, 
                          pygame.Rect(symbol_x - 3, symbol_y, 6, 3), 
                          math.pi, 2 * math.pi, 2)


class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.width = POWERUP_SIZE
        self.height = POWERUP_SIZE
        self.type = powerup_type
        self.collected = False
        self.animation_timer = 0
        
        # Type-specific properties
        if powerup_type == "double_jump":
            self.color = GREEN
            self.symbol = "2"
        elif powerup_type == "speed_boost":
            self.color = YELLOW
            self.symbol = ">"
        elif powerup_type == "shield":
            self.color = CYAN
            self.symbol = "S"
    
    def update(self, dt):
        self.animation_timer += dt
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def render(self, screen):
        if self.collected:
            return
        
        # Calculate pulsing animation
        pulse = 1 + 0.3 * math.sin(self.animation_timer * 4)
        glow_pulse = 1 + 0.5 * math.sin(self.animation_timer * 6)
        size = int(self.width * pulse)
        offset = (self.width - size) // 2
        
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Draw glow effect directly
        glow_radius = int(self.width * glow_pulse)
        glow_color = tuple(int(min(255, c + 50)) for c in self.color)
        pygame.draw.circle(screen, glow_color, (center_x, center_y), glow_radius)
        
        # Draw shadow directly
        shadow_rect = pygame.Rect(self.x + offset + SHADOW_OFFSET, 
                                 self.y + offset + SHADOW_OFFSET, size, size)
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect)
        
        # Draw main powerup body with gradient
        powerup_rect = pygame.Rect(self.x + offset, self.y + offset, size, size)
        
        # Gradient effect
        top_color = tuple(int(min(255, c + 40)) for c in self.color)
        bottom_color = tuple(int(max(0, c - 20)) for c in self.color)
        
        # Top half
        top_rect = pygame.Rect(self.x + offset, self.y + offset, size, size//2)
        pygame.draw.rect(screen, top_color, top_rect)
        
        # Bottom half
        bottom_rect = pygame.Rect(self.x + offset, self.y + offset + size//2, size, size//2)
        pygame.draw.rect(screen, bottom_color, bottom_rect)
        
        # Draw border
        pygame.draw.rect(screen, WHITE, powerup_rect, 3)
        
        # Draw inner border
        inner_rect = pygame.Rect(self.x + offset + 3, self.y + offset + 3, 
                               size - 6, size - 6)
        pygame.draw.rect(screen, tuple(int(max(0, c - 30)) for c in self.color), inner_rect, 1)
        
        # Draw symbols with better graphics
        symbol_center_x = self.x + self.width // 2
        symbol_center_y = self.y + self.height // 2
        symbol_size = size // 3
        
        if self.type == "double_jump":
            # Draw stylized up arrows with trails
            arrow_width = symbol_size
            arrow_height = symbol_size // 2
            
            # First arrow (higher)
            arrow1_points = [
                (symbol_center_x, symbol_center_y - arrow_height),
                (symbol_center_x - arrow_width//2, symbol_center_y - arrow_height//2),
                (symbol_center_x + arrow_width//2, symbol_center_y - arrow_height//2)
            ]
            pygame.draw.polygon(screen, WHITE, arrow1_points)
            
            # Second arrow (lower)
            arrow2_points = [
                (symbol_center_x, symbol_center_y),
                (symbol_center_x - arrow_width//2, symbol_center_y + arrow_height//2),
                (symbol_center_x + arrow_width//2, symbol_center_y + arrow_height//2)
            ]
            pygame.draw.polygon(screen, WHITE, arrow2_points)
            
        elif self.type == "speed_boost":
            # Draw lightning bolt
            lightning_points = [
                (symbol_center_x - symbol_size//2, symbol_center_y - symbol_size//2),
                (symbol_center_x, symbol_center_y - symbol_size//4),
                (symbol_center_x - symbol_size//4, symbol_center_y),
                (symbol_center_x + symbol_size//2, symbol_center_y + symbol_size//2),
                (symbol_center_x, symbol_center_y + symbol_size//4),
                (symbol_center_x + symbol_size//4, symbol_center_y)
            ]
            pygame.draw.polygon(screen, WHITE, lightning_points)
            pygame.draw.polygon(screen, YELLOW, lightning_points, 2)
            
        elif self.type == "shield":
            # Draw shield with cross pattern
            shield_points = [
                (symbol_center_x, symbol_center_y - symbol_size//2),
                (symbol_center_x - symbol_size//3, symbol_center_y - symbol_size//4),
                (symbol_center_x - symbol_size//3, symbol_center_y + symbol_size//4),
                (symbol_center_x, symbol_center_y + symbol_size//2),
                (symbol_center_x + symbol_size//3, symbol_center_y + symbol_size//4),
                (symbol_center_x + symbol_size//3, symbol_center_y - symbol_size//4)
            ]
            pygame.draw.polygon(screen, WHITE, shield_points)
            
            # Draw cross on shield
            cross_size = symbol_size // 4
            pygame.draw.line(screen, CYAN,
                           (symbol_center_x - cross_size, symbol_center_y),
                           (symbol_center_x + cross_size, symbol_center_y), 3)
            pygame.draw.line(screen, CYAN,
                           (symbol_center_x, symbol_center_y - cross_size),
                           (symbol_center_x, symbol_center_y + cross_size), 3)
        
        # Draw rotating sparkles around powerup
        sparkle_count = 4
        sparkle_distance = size // 2 + 8
        for i in range(sparkle_count):
            angle = (self.animation_timer * 3 + i * 1.57) % (2 * math.pi)  # 1.57 ≈ π/2
            sparkle_x = center_x + math.cos(angle) * sparkle_distance
            sparkle_y = center_y + math.sin(angle) * sparkle_distance
            sparkle_size = 2 + int(math.sin(self.animation_timer * 8 + i) * 1)
            pygame.draw.circle(screen, WHITE, (int(sparkle_x), int(sparkle_y)), sparkle_size)
