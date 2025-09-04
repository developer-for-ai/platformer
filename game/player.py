import pygame
import math
from game.constants import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.lives = MAX_LIVES
        self.score = 0
        self.crystals_collected = 0
        self.invulnerable = False
        self.invulnerable_timer = 0
        
        # Power-ups
        self.has_double_jump = False
        self.double_jump_used = False
        self.has_speed_boost = False
        self.speed_boost_timer = 0
        self.has_shield = False
        self.shield_timer = 0
        
        # Animation
        self.color = BLUE
        self.animation_timer = 0
        
        # Jump input tracking
        self.jump_pressed = False
        
    def update(self, dt, platforms):
        from .effects import effects
        
        # Handle invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # Handle power-ups
        if self.has_speed_boost:
            self.speed_boost_timer -= dt
            # Add speed boost particles
            if self.speed_boost_timer > 0:
                effects.particle_system.create_sparkle(
                    self.x + self.width // 2, self.y + self.height // 2,
                    GOLDEN_YELLOW, count=2
                )
            if self.speed_boost_timer <= 0:
                self.has_speed_boost = False
        
        if self.has_shield:
            self.shield_timer -= dt
            # Add shield particles
            if self.shield_timer > 0:
                effects.particle_system.create_sparkle(
                    self.x + self.width // 2, self.y + self.height // 2,
                    CYAN, count=1
                )
            if self.shield_timer <= 0:
                self.has_shield = False
        
        # Physics
        keys = pygame.key.get_pressed()
        
        # Store old values for particle effects
        old_on_ground = self.on_ground
        old_vel_y = self.vel_y
        
        # Reset on_ground status (will be set to True if we land on a platform)
        self.on_ground = False
        
        # Horizontal movement
        speed_multiplier = 1.5 if self.has_speed_boost else 1.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED * speed_multiplier
            # Add movement dust when on ground
            if self.on_ground or old_on_ground:
                effects.particle_system.create_trail(
                    self.x + self.width // 2, self.y + self.height,
                    (180, 160, 120), direction_x=1
                )
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED * speed_multiplier
            # Add movement dust when on ground
            if self.on_ground or old_on_ground:
                effects.particle_system.create_trail(
                    self.x + self.width // 2, self.y + self.height,
                    (180, 160, 120), direction_x=-1
                )
        else:
            self.vel_x *= 0.8  # Friction
        
        # Jumping
        if self.jump_pressed:
            self.jump_pressed = False  # Reset jump press
            # Check if we're on ground by testing collision before jumping
            self.check_ground_collision(platforms)
            if self.on_ground:
                self.vel_y = -PLAYER_JUMP_SPEED
                self.on_ground = False
                self.double_jump_used = False
                # Add jump dust particles
                effects.particle_system.create_jump_dust(
                    self.x + self.width // 2, self.y + self.height
                )
            elif self.has_double_jump and not self.double_jump_used:
                self.vel_y = -PLAYER_JUMP_SPEED * 0.8
                self.double_jump_used = True
                # Add special double jump explosion
                effects.particle_system.create_explosion(
                    self.x + self.width // 2, self.y + self.height // 2,
                    GREEN, count=15
                )
        
        # Apply gravity
        self.vel_y += GRAVITY * dt
        
        # Store old position
        old_x = self.x
        old_y = self.y
        
        # Update horizontal position and check horizontal collisions
        self.x += self.vel_x * dt
        self.handle_horizontal_collisions(platforms, old_x)
        
        # Update vertical position and check vertical collisions
        self.y += self.vel_y * dt
        self.handle_vertical_collisions(platforms, old_y)
        
        # Check if we just landed hard
        if not old_on_ground and self.on_ground and old_vel_y > 300:
            # Add landing particles
            effects.particle_system.create_landing_dust(
                self.x + self.width // 2, self.y + self.height, self.width
            )
            # Add screen shake for hard landings
            if old_vel_y > 600:
                effects.start_screen_shake(3, 0.2)
        
        # Keep player on screen horizontally
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
        # Check if player fell off the bottom
        if self.y > SCREEN_HEIGHT:
            self.take_damage()
            self.respawn()
        
        # Animation
        self.animation_timer += dt
    
    def check_ground_collision(self, platforms):
        """Check if player is currently standing on ground"""
        player_rect = pygame.Rect(self.x, self.y + 1, self.width, self.height)  # Check 1 pixel below
        for platform in platforms:
            if player_rect.colliderect(platform):
                self.on_ground = True
                return
    
    def handle_horizontal_collisions(self, platforms, old_x):
        """Handle horizontal collisions separately"""
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            if player_rect.colliderect(platform):
                if self.vel_x > 0:  # Moving right
                    self.x = platform.left - self.width
                elif self.vel_x < 0:  # Moving left
                    self.x = platform.right
                self.vel_x = 0
    
    def handle_vertical_collisions(self, platforms, old_y):
        """Handle vertical collisions separately"""
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            if player_rect.colliderect(platform):
                if self.vel_y > 0:  # Falling down
                    self.y = platform.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Moving up (hitting ceiling)
                    self.y = platform.bottom
                    self.vel_y = 0
    

    def take_damage(self):
        if self.invulnerable or self.has_shield:
            return
        
        from .effects import effects
        
        self.lives -= 1
        self.invulnerable = True
        self.invulnerable_timer = 2.0  # 2 seconds of invulnerability
        
        # Create damage effects
        effects.particle_system.create_explosion(
            self.x + self.width // 2,
            self.y + self.height // 2,
            RED, count=20
        )
        effects.start_screen_shake(8, 0.4)
        
        # Play damage sound
        self.play_sound(DAMAGE_SOUND_FREQ, 200)
    
    def respawn(self):
        self.x = 50
        self.y = SCREEN_HEIGHT - 100  # Higher up so player doesn't fall through ground
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
    
    def collect_crystal(self):
        self.crystals_collected += 1
        self.score += 100
        self.play_sound(COLLECT_SOUND_FREQ, 100)
    
    def collect_coin(self):
        self.score += 10
        self.play_sound(COLLECT_SOUND_FREQ, 50)
    
    def collect_powerup(self, powerup_type):
        """Collect a powerup and activate its effect"""
        self.play_sound(POWERUP_SOUND_FREQ, 200)
        
        if powerup_type == "double_jump":
            self.has_double_jump = True
        elif powerup_type == "speed_boost":
            self.has_speed_boost = True
            self.speed_boost_timer = POWERUP_DURATION
        elif powerup_type == "shield":
            self.has_shield = True
            self.shield_timer = POWERUP_DURATION
    
    def play_sound(self, frequency, duration):
        # Simple tone generation
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            # We'll skip actual sound for simplicity
        except:
            pass
    
    def handle_key_press(self, key):
        """Handle key press events"""
        if key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
            self.jump_pressed = True
    
    def render(self, screen):
        from .effects import effects
        import math
        
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Draw simple shadow without multiple layers to avoid instability
        shadow_rect = pygame.Rect(self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET, 
                                self.width, self.height)
        pygame.draw.rect(screen, (20, 20, 30), shadow_rect)
        
        # Determine player color based on state with enhanced effects
        if self.invulnerable:
            # Enhanced flashing effect with smooth transitions
            flash_colors = [WHITE, GOLDEN_YELLOW, CYAN, PINK, LIGHT_BLUE]
            color_index = int(self.animation_timer * 6) % len(flash_colors)
            blend_factor = (self.animation_timer * 6) % 1
            current_color = flash_colors[color_index]
            next_color = flash_colors[(color_index + 1) % len(flash_colors)]
            
            # Blend between colors for smooth transition
            base_color = tuple(
                int(current_color[i] * (1 - blend_factor) + next_color[i] * blend_factor)
                for i in range(3)
            )
            
            # Add pulsing glow effect directly
            glow_radius = self.width + int(math.sin(self.animation_timer * 8) * 8)
            pygame.draw.circle(screen, base_color, 
                             (self.x + self.width//2, self.y + self.height//2), glow_radius)
        else:
            # Enhanced base color with subtle animation
            pulse = math.sin(self.animation_timer * 2) * 0.1 + 1
            base_color = tuple(min(255, max(0, int(c * pulse))) for c in BLUE)
        
        # Enhanced shield effect
        if self.has_shield:
            shield_radius = self.width//2 + 12
            shield_pulse = math.sin(self.animation_timer * 4) * 3
            
            # Multiple shield layers with different effects drawn directly
            for i in range(4):
                layer_radius = shield_radius - i * 3 + shield_pulse
                shield_alpha = 120 - i * 25
                shield_color = CYAN if i % 2 == 0 else LIGHT_BLUE
                
                # Draw shield circle directly
                pygame.draw.circle(screen, shield_color, 
                                 (self.x + self.width//2, self.y + self.height//2), 
                                 layer_radius, 3)
            
            # Shield sparkles
            for i in range(8):
                angle = (self.animation_timer * 2 + i * math.pi / 4) % (2 * math.pi)
                sparkle_x = self.x + self.width//2 + math.cos(angle) * shield_radius
                sparkle_y = self.y + self.height//2 + math.sin(angle) * shield_radius
                sparkle_size = 2 + int(math.sin(self.animation_timer * 6 + i) * 1)
                pygame.draw.circle(screen, WHITE, (int(sparkle_x), int(sparkle_y)), sparkle_size)
        
        # Enhanced speed trail effect
        if self.has_speed_boost:
            trail_length = 8
            for i in range(trail_length):
                trail_alpha = 200 - (i * 25)
                if trail_alpha > 0:
                    trail_offset_x = i * 6 * (-1 if self.vel_x >= 0 else 1)
                    trail_offset_y = math.sin(self.animation_timer * 8 + i * 0.5) * 2
                    
                    # Draw trail rectangle directly
                    trail_colors = [GOLDEN_YELLOW, ORANGE, RED]
                    color_index = min(i // 3, len(trail_colors) - 1)
                    trail_rect = pygame.Rect(self.x + trail_offset_x, self.y + trail_offset_y, 
                                           self.width, self.height)
                    pygame.draw.rect(screen, trail_colors[color_index], trail_rect)
        
        # Enhanced main player body with stable rendering
        # Simpler, more stable rendering
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Draw body with simple gradient (top and bottom half only)
        top_color = tuple(int(min(255, c + 40)) for c in base_color)
        bottom_color = tuple(int(max(0, c - 20)) for c in base_color)
        
        # Top half
        top_rect = pygame.Rect(self.x, self.y, self.width, self.height//2)
        pygame.draw.rect(screen, top_color, top_rect)
        
        # Bottom half
        bottom_rect = pygame.Rect(self.x, self.y + self.height//2, self.width, self.height//2)
        pygame.draw.rect(screen, bottom_color, bottom_rect)
        
        # Enhanced border with glow
        border_color = WHITE
        if self.invulnerable:
            border_color = base_color
        
        pygame.draw.rect(screen, border_color, body_rect, 3)
        
        # Add inner highlight
        highlight_rect = pygame.Rect(body_rect.x + 2, body_rect.y + 2, 
                                   body_rect.width - 4, body_rect.height - 4)
        highlight_color = tuple(int(min(255, c + 80)) for c in base_color)
        pygame.draw.rect(screen, highlight_color, highlight_rect, 1)
        
        # Enhanced face with expressions
        # Eyes with animation
        eye_size = 7
        blink = int(self.animation_timer * 2) % 120 < 3  # Occasional blinking
        
        left_eye_pos = (self.x + 6, self.y + 8)
        right_eye_pos = (self.x + self.width - 12, self.y + 8)
        
        if not blink:
            # Draw eyes with highlights
            pygame.draw.circle(screen, WHITE, left_eye_pos, eye_size//2)
            pygame.draw.circle(screen, WHITE, right_eye_pos, eye_size//2)
            
            # Pupils
            pupil_color = BLACK if not self.invulnerable else base_color
            pygame.draw.circle(screen, pupil_color, left_eye_pos, eye_size//4)
            pygame.draw.circle(screen, pupil_color, right_eye_pos, eye_size//4)
            
            # Eye highlights
            highlight_offset = 1
            pygame.draw.circle(screen, WHITE, 
                             (left_eye_pos[0] - highlight_offset, left_eye_pos[1] - highlight_offset), 1)
            pygame.draw.circle(screen, WHITE, 
                             (right_eye_pos[0] - highlight_offset, right_eye_pos[1] - highlight_offset), 1)
        else:
            # Closed eyes
            pygame.draw.line(screen, WHITE, 
                           (left_eye_pos[0] - 3, left_eye_pos[1]), 
                           (left_eye_pos[0] + 3, left_eye_pos[1]), 2)
            pygame.draw.line(screen, WHITE, 
                           (right_eye_pos[0] - 3, right_eye_pos[1]), 
                           (right_eye_pos[0] + 3, right_eye_pos[1]), 2)
        
        # Enhanced mouth with expressions
        mouth_center = (self.x + self.width//2, self.y + self.height - 8)
        
        if self.has_speed_boost or self.has_shield:
            # Happy expression
            mouth_rect = pygame.Rect(mouth_center[0] - 8, mouth_center[1] - 4, 16, 8)
            pygame.draw.arc(screen, WHITE, mouth_rect, 0, math.pi, 3)
        else:
            # Normal expression
            mouth_rect = pygame.Rect(mouth_center[0] - 6, mouth_center[1] - 3, 12, 6)
            pygame.draw.arc(screen, WHITE, mouth_rect, 0, math.pi, 2)
        
        # Enhanced double jump indicator
        if self.has_double_jump and not self.double_jump_used:
            indicator_y = self.y - 15
            indicator_bounce = math.sin(self.animation_timer * 5) * 3
            
            # Draw glowing orb directly
            pygame.draw.circle(screen, GREEN, 
                             (self.x + self.width//2, int(indicator_y + indicator_bounce)), 10)
            
            # Inner orb
            pygame.draw.circle(screen, GREEN, 
                             (self.x + self.width//2, int(indicator_y + indicator_bounce)), 4)
            pygame.draw.circle(screen, WHITE, 
                             (self.x + self.width//2, int(indicator_y + indicator_bounce)), 4, 2)
            
            # Sparkles around the orb
            for i in range(4):
                angle = self.animation_timer * 3 + i * math.pi / 2
                sparkle_x = self.x + self.width//2 + math.cos(angle) * 8
                sparkle_y = indicator_y + indicator_bounce + math.sin(angle) * 8
                pygame.draw.circle(screen, WHITE, (int(sparkle_x), int(sparkle_y)), 1)
