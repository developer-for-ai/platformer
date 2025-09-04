# Visual Effects System for Crystal Quest
import pygame
import math
import random
from .constants import *

class Particle:
    def __init__(self, x, y, vel_x, vel_y, color, life, size=3, gravity=True):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.alpha = 255
    
    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        if self.gravity:
            self.vel_y += 500 * dt  # Gravity
        
        self.life -= dt
        self.alpha = int(255 * (self.life / self.max_life))
        return self.life > 0
    
    def render(self, screen):
        if self.life <= 0:
            return
        
        color_with_alpha = (*self.color[:3], max(0, self.alpha))
        particle_surface = pygame.Surface((self.size * 2, self.size * 2))
        particle_surface.set_alpha(self.alpha)
        particle_surface.fill(self.color)
        
        pygame.draw.circle(particle_surface, self.color, 
                         (self.size, self.size), self.size)
        screen.blit(particle_surface, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, vel_x, vel_y, color, life, size=3, gravity=True):
        self.particles.append(Particle(x, y, vel_x, vel_y, color, life, size, gravity))
    
    def create_explosion(self, x, y, color, count=10):
        """Create an explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            life = random.uniform(0.5, 1.5)
            size = random.randint(2, 5)
            self.add_particle(x, y, vel_x, vel_y, color, life, size)
    
    def create_sparkle(self, x, y, color, count=5):
        """Create sparkle effect"""
        for _ in range(count):
            vel_x = random.uniform(-30, 30)
            vel_y = random.uniform(-30, 30)
            life = random.uniform(0.3, 0.8)
            size = random.randint(1, 3)
            self.add_particle(x, y, vel_x, vel_y, color, life, size, gravity=False)
    
    def create_trail(self, x, y, color, direction_x=0):
        """Create a trail effect"""
        for _ in range(3):
            vel_x = random.uniform(-20, 20) + direction_x * -30
            vel_y = random.uniform(-10, 10)
            life = random.uniform(0.2, 0.5)
            size = random.randint(1, 2)
            self.add_particle(x, y, vel_x, vel_y, color, life, size, gravity=False)
    
    def create_jump_dust(self, x, y):
        """Create dust particles when jumping"""
        for _ in range(8):
            vel_x = random.uniform(-50, 50)
            vel_y = random.uniform(-20, 5)
            life = random.uniform(0.3, 0.6)
            size = random.randint(1, 3)
            dust_color = (200, 180, 140)  # Dusty brown
            self.add_particle(x, y, vel_x, vel_y, dust_color, life, size)
    
    def create_landing_dust(self, x, y, width):
        """Create dust particles when landing"""
        for _ in range(12):
            offset_x = random.uniform(-width//2, width//2)
            vel_x = random.uniform(-80, 80)
            vel_y = random.uniform(-30, -10)
            life = random.uniform(0.4, 0.8)
            size = random.randint(2, 4)
            dust_color = (180, 160, 120)
            self.add_particle(x + offset_x, y, vel_x, vel_y, dust_color, life, size)
    
    def update(self, dt):
        """Update all particles and remove dead ones"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
    
    def render(self, screen):
        """Render all particles"""
        for particle in self.particles:
            particle.render(screen)

class ScreenTransition:
    def __init__(self):
        self.active = False
        self.transition_type = "fade"
        self.duration = 1.0
        self.timer = 0.0
        self.direction = "out"  # "in" or "out"
        self.callback = None
    
    def start_fade_out(self, duration=1.0, callback=None):
        self.active = True
        self.transition_type = "fade"
        self.duration = duration
        self.timer = 0.0
        self.direction = "out"
        self.callback = callback
    
    def start_fade_in(self, duration=1.0, callback=None):
        self.active = True
        self.transition_type = "fade"
        self.duration = duration
        self.timer = 0.0
        self.direction = "in"
        self.callback = callback
    
    def start_wipe(self, duration=1.0, callback=None, direction="left"):
        self.active = True
        self.transition_type = "wipe"
        self.duration = duration
        self.timer = 0.0
        self.direction = direction
        self.callback = callback
    
    def update(self, dt):
        if not self.active:
            return False
        
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False
            if self.callback:
                self.callback()
            return True
        return False
    
    def render(self, screen):
        if not self.active:
            return
        
        progress = self.timer / self.duration
        
        if self.transition_type == "fade":
            if self.direction == "out":
                alpha = int(255 * progress)
            else:
                alpha = int(255 * (1 - progress))
            
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.set_alpha(alpha)
            fade_surface.fill(BLACK)
            screen.blit(fade_surface, (0, 0))
        
        elif self.transition_type == "wipe":
            if self.direction == "left":
                width = int(SCREEN_WIDTH * progress)
                pygame.draw.rect(screen, BLACK, (0, 0, width, SCREEN_HEIGHT))
            elif self.direction == "right":
                width = int(SCREEN_WIDTH * progress)
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - width, 0, width, SCREEN_HEIGHT))

class AnimatedText:
    def __init__(self, text, x, y, font, color, animation_type="bounce"):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.animation_type = animation_type
        self.timer = 0.0
        self.offset_y = 0
        self.scale = 1.0
        self.alpha = 255
    
    def update(self, dt):
        self.timer += dt
        
        if self.animation_type == "bounce":
            self.offset_y = math.sin(self.timer * 3) * 5
        elif self.animation_type == "pulse":
            self.scale = 1.0 + math.sin(self.timer * 4) * 0.1
        elif self.animation_type == "fade_in":
            self.alpha = min(255, int(255 * self.timer))
    
    def render(self, screen):
        # Create text surface
        text_surface = self.font.render(self.text, True, self.color)
        
        # Apply scaling if needed
        if self.scale != 1.0:
            new_width = int(text_surface.get_width() * self.scale)
            new_height = int(text_surface.get_height() * self.scale)
            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))
        
        # Apply alpha
        if self.alpha < 255:
            text_surface.set_alpha(self.alpha)
        
        # Calculate position
        rect = text_surface.get_rect(center=(self.x, self.y + self.offset_y))
        screen.blit(text_surface, rect)

class VisualEffects:
    """Centralized visual effects manager"""
    def __init__(self):
        self.particle_system = ParticleSystem()
        self.screen_transition = ScreenTransition()
        self.animated_texts = []
        self.screen_shake = 0.0
        self.screen_shake_duration = 0.0
    
    def add_animated_text(self, text, x, y, font, color, animation_type="bounce"):
        self.animated_texts.append(AnimatedText(text, x, y, font, color, animation_type))
    
    def start_screen_shake(self, intensity=10, duration=0.5):
        self.screen_shake = intensity
        self.screen_shake_duration = duration
    
    def get_screen_offset(self):
        if self.screen_shake > 0:
            offset_x = random.uniform(-self.screen_shake, self.screen_shake)
            offset_y = random.uniform(-self.screen_shake, self.screen_shake)
            return (int(offset_x), int(offset_y))
        return (0, 0)
    
    def clear(self):
        """Clear all effects"""
        self.particle_system.clear()
        self.animated_texts.clear()
        self.screen_shake = 0.0
        self.screen_shake_duration = 0.0
    
    def update(self, dt):
        self.particle_system.update(dt)
        self.screen_transition.update(dt)
        
        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= dt
            if self.screen_shake_duration <= 0:
                self.screen_shake = 0
        
        # Update animated texts
        for text in self.animated_texts:
            text.update(dt)
    
    def render(self, screen):
        self.particle_system.render(screen)
        
        for text in self.animated_texts:
            text.render(screen)
        
        self.screen_transition.render(screen)

# Global effects instance
effects = VisualEffects()
