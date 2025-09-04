import pygame
from game.constants import *
from game.player import Player
from game.level import LevelManager
from game.effects import effects

class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = "menu"  # menu, playing, paused, game_over, level_complete, game_complete
        self.player = Player(50, SCREEN_HEIGHT - 100)  # Start higher up
        self.level_manager = LevelManager()
        self.current_level = None
        self.level_timer = 0
        self.game_timer = 0
        
        # Menu selection
        self.menu_selection = 0
        self.menu_options = ["Start Game", "Instructions", "Quit"]
        
        # Pause menu
        self.pause_selection = 0
        self.pause_options = ["Resume", "Restart Level", "Main Menu"]
        
        # Game over options
        self.game_over_selection = 0
        self.game_over_options = ["Restart Game", "Main Menu", "Quit"]
        
        # Key states for menu navigation
        self.keys_pressed = set()
        
        self.load_level()
    
    def load_level(self):
        self.current_level = self.level_manager.get_current_level()
        if self.current_level:
            self.level_timer = self.current_level.time_limit
            self.player.respawn()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            
            if self.state == "menu":
                if not self.handle_menu_input(event.key):
                    return False  # Quit requested
            elif self.state == "instructions":
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
            elif self.state == "playing":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.state = "paused"
                else:
                    # Pass key press to player for jump handling
                    self.player.handle_key_press(event.key)
            elif self.state == "paused":
                if not self.handle_pause_input(event.key):
                    return False  # Quit requested
            elif self.state == "game_over":
                if not self.handle_game_over_input(event.key):
                    return False  # Quit requested
            elif self.state == "level_complete":
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.next_level()
            elif self.state == "game_complete":
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.restart_game()
        
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
        
        return True
    
    def handle_menu_input(self, key):
        if key == pygame.K_UP or key == pygame.K_w:
            self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.menu_selection == 0:  # Start Game
                self.start_game()
            elif self.menu_selection == 1:  # Instructions
                self.state = "instructions"
            elif self.menu_selection == 2:  # Quit
                return False
        return True
    
    def handle_pause_input(self, key):
        if key == pygame.K_UP or key == pygame.K_w:
            self.pause_selection = (self.pause_selection - 1) % len(self.pause_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.pause_selection = (self.pause_selection + 1) % len(self.pause_options)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.pause_selection == 0:  # Resume
                self.state = "playing"
            elif self.pause_selection == 1:  # Restart Level
                self.restart_level()
            elif self.pause_selection == 2:  # Main Menu
                self.state = "menu"
        elif key == pygame.K_ESCAPE:
            self.state = "playing"
        return True
    
    def handle_game_over_input(self, key):
        if key == pygame.K_UP or key == pygame.K_w:
            self.game_over_selection = (self.game_over_selection - 1) % len(self.game_over_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.game_over_selection = (self.game_over_selection + 1) % len(self.game_over_options)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.game_over_selection == 0:  # Restart Game
                self.restart_game()
            elif self.game_over_selection == 1:  # Main Menu
                self.state = "menu"
            elif self.game_over_selection == 2:  # Quit
                return False
        return True
    
    def start_game(self):
        self.state = "playing"
        self.restart_game()
    
    def restart_game(self):
        # Clear effects
        effects.clear()
        
        self.player = Player(50, SCREEN_HEIGHT - 100)  # Start higher up
        self.level_manager = LevelManager()
        self.game_timer = 0
        self.load_level()
        self.state = "playing"
    
    def restart_level(self):
        # Clear effects
        effects.clear()
        
        # Reset level collectibles and enemies FIRST
        if self.current_level:
            self.current_level.reset_collectibles()
            self.current_level.reset_enemies()
        
        # Reset player
        self.player.respawn()
        self.player.lives = MAX_LIVES
        
        # Reset player power-ups
        self.player.has_double_jump = False
        self.player.double_jump_used = False
        self.player.has_speed_boost = False
        self.player.speed_boost_timer = 0
        self.player.has_shield = False
        self.player.shield_timer = 0
        
        # Reset level timer
        if self.current_level:
            self.level_timer = self.current_level.time_limit
        
        self.state = "playing"
    
    def next_level(self):
        # Clear effects when transitioning to next level
        effects.clear()
        
        next_level = self.level_manager.next_level()
        if next_level:
            # Reset lives and power-ups for new level
            self.player.lives = MAX_LIVES
            self.player.has_double_jump = False
            self.player.double_jump_used = False
            self.player.has_speed_boost = False
            self.player.speed_boost_timer = 0
            self.player.has_shield = False
            self.player.shield_timer = 0
            
            self.load_level()
            self.state = "playing"
        else:
            self.state = "game_complete"
    
    def update(self, dt):
        # Update effects system
        effects.update(dt)
        
        if self.state == "playing":
            self.game_timer += dt
            self.level_timer -= dt
            
            # Update player
            self.player.update(dt, self.current_level.platforms)
            
            # Update level
            self.current_level.update(dt, self.player)
            
            # Check win condition
            if self.current_level.is_complete(self.player):
                self.state = "level_complete"
                # Add celebration particles
                effects.particle_system.create_explosion(
                    self.player.x + self.player.width // 2,
                    self.player.y + self.player.height // 2,
                    GOLDEN_YELLOW, count=30
                )
            
            # Check lose conditions
            if self.player.lives <= 0:
                self.state = "game_over"
            elif self.level_timer <= 0:
                self.player.take_damage()
                if self.player.lives <= 0:
                    self.state = "game_over"
                else:
                    self.level_timer = self.current_level.time_limit
        
        return True
    
    def render(self):
        # Apply screen shake if active
        offset_x, offset_y = effects.get_screen_offset()
        
        # Create a temporary surface for shake effect
        if offset_x != 0 or offset_y != 0:
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            render_target = temp_surface
        else:
            render_target = self.screen
        
        if self.state == "menu":
            self.render_menu_enhanced(render_target)
        elif self.state == "instructions":
            self.render_instructions_enhanced(render_target)
        elif self.state == "playing":
            self.render_game_enhanced(render_target)
        elif self.state == "paused":
            self.render_game_enhanced(render_target)
            self.render_pause_overlay(render_target)
        elif self.state == "game_over":
            self.render_game_over_enhanced(render_target)
        elif self.state == "level_complete":
            self.render_level_complete_enhanced(render_target)
        elif self.state == "game_complete":
            self.render_game_complete_enhanced(render_target)
        
        # Apply screen shake
        if offset_x != 0 or offset_y != 0:
            self.screen.fill(BLACK)
            self.screen.blit(temp_surface, (offset_x, offset_y))
        
        # Always render effects last
        effects.render(self.screen)
    
    def render_menu_enhanced(self, screen):
        # Enhanced gradient background
        for y in range(SCREEN_HEIGHT):
            color_factor = y / SCREEN_HEIGHT
            color = (
                int(DARK_GRAY[0] * (1 - color_factor) + DEEP_BLUE[0] * color_factor),
                int(DARK_GRAY[1] * (1 - color_factor) + DEEP_BLUE[1] * color_factor),
                int(DARK_GRAY[2] * (1 - color_factor) + DEEP_BLUE[2] * color_factor)
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Animated title with glow effect
        import math
        title_glow = int(50 + 30 * math.sin(pygame.time.get_ticks() * 0.003))
        
        # Draw title glow
        title_text = self.font.render("CRYSTAL QUEST", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        
        # Multiple glow layers
        for i in range(5):
            glow_surface = pygame.Surface((title_rect.width + i*10, title_rect.height + i*10))
            glow_surface.set_alpha(title_glow - i*10)
            glow_surface.fill(CYAN)
            glow_rect = glow_surface.get_rect(center=title_rect.center)
            screen.blit(glow_surface, glow_rect)
        
        # Main title
        screen.blit(title_text, title_rect)
        
        # Animated subtitle
        subtitle_pulse = math.sin(pygame.time.get_ticks() * 0.002) * 0.1 + 1
        subtitle_color = tuple(min(255, max(0, int(c * subtitle_pulse))) for c in WHITE)
        subtitle_text = self.small_font.render("A 2D Platformer Adventure", True, subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Enhanced menu options with animations
        for i, option in enumerate(self.menu_options):
            if i == self.menu_selection:
                # Selected option effects
                glow_intensity = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.01))
                option_color = GOLDEN_YELLOW
                
                # Draw selection glow
                option_text = self.font.render(option, True, option_color)
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, 300 + i * 60))
                
                glow_surface = pygame.Surface((option_rect.width + 40, option_rect.height + 20))
                glow_surface.set_alpha(glow_intensity)
                glow_surface.fill(GOLDEN_YELLOW)
                glow_rect = glow_surface.get_rect(center=option_rect.center)
                screen.blit(glow_surface, glow_rect)
                
                # Selection arrows
                arrow_bounce = math.sin(pygame.time.get_ticks() * 0.008) * 5
                left_arrow_pos = (option_rect.left - 30 + arrow_bounce, option_rect.centery)
                right_arrow_pos = (option_rect.right + 30 - arrow_bounce, option_rect.centery)
                
                arrow_points_left = [
                    (left_arrow_pos[0], left_arrow_pos[1]),
                    (left_arrow_pos[0] + 15, left_arrow_pos[1] - 8),
                    (left_arrow_pos[0] + 15, left_arrow_pos[1] + 8)
                ]
                arrow_points_right = [
                    (right_arrow_pos[0], right_arrow_pos[1]),
                    (right_arrow_pos[0] - 15, right_arrow_pos[1] - 8),
                    (right_arrow_pos[0] - 15, right_arrow_pos[1] + 8)
                ]
                
                pygame.draw.polygon(screen, GOLDEN_YELLOW, arrow_points_left)
                pygame.draw.polygon(screen, GOLDEN_YELLOW, arrow_points_right)
            else:
                option_color = WHITE
                option_text = self.font.render(option, True, option_color)
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, 300 + i * 60))
            
            screen.blit(option_text, option_rect)
        
        # Enhanced instructions with icons
        instruction_lines = [
            "🎮 Use ARROW KEYS or WASD to move",
            "⬆️ SPACE or UP to jump",
            "⏸️ ESC to pause",
            "💎 Collect crystals to complete levels!"
        ]
        
        for i, line in enumerate(instruction_lines):
            # Remove emoji for now since we don't have font support
            clean_line = line.replace("🎮 ", "").replace("⬆️ ", "").replace("⏸️ ", "").replace("💎 ", "")
            text_color = tuple(min(255, max(0, int(c * (0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.001 + i))))) for c in LIGHT_BLUE)
            text = self.small_font.render(clean_line, True, text_color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 550 + i * 30))
            screen.blit(text, text_rect)
        
        # Add floating particles in background
        import random
        random.seed(42)
        for i in range(20):
            x = (random.randint(0, SCREEN_WIDTH) + pygame.time.get_ticks() * 0.02 * (i % 3 + 1)) % SCREEN_WIDTH
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            alpha = 50 + int(30 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            
            # Draw particle directly without creating surface
            particle_color = (*CRYSTAL_BLUE, alpha)
            pygame.draw.circle(screen, CRYSTAL_BLUE, (int(x), int(y)), size)
    
    def render_menu(self, screen):
        # Fallback to enhanced version
        self.render_menu_enhanced(screen)
    
    def render_instructions(self):
        self.screen.fill(DARK_GRAY)
        
        title_text = self.font.render("INSTRUCTIONS", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        instructions = [
            "CONTROLS:",
            "- ARROW KEYS or WASD: Move left/right",
            "- SPACE or UP: Jump",
            "- ESC: Pause game",
            "",
            "GAMEPLAY:",
            "- Collect all crystals to complete each level",
            "- Avoid red enemies - they hurt you!",
            "- Collect yellow coins for points",
            "- Grab power-ups for special abilities:",
            "  * Green (2): Double Jump",
            "  * Yellow (>): Speed Boost",
            "  * Cyan (S): Shield Protection",
            "",
            "- You have 3 lives and a time limit per level",
            "- Complete 5 challenging levels to win!",
            "",
            "Press ESC to return to menu"
        ]
        
        for i, line in enumerate(instructions):
            if line.startswith("CONTROLS:") or line.startswith("GAMEPLAY:"):
                color = YELLOW
            elif line.startswith("  *"):
                color = GREEN
            else:
                color = WHITE
            
            text = self.small_font.render(line, True, color)
            self.screen.blit(text, (100, 120 + i * 25))
    
    def render_instructions_enhanced(self, screen):
        # Use the existing instructions method but with enhanced background
        self.render_instructions_with_screen(screen)
    
    def render_instructions_with_screen(self, screen):
        screen.fill(DARK_GRAY)
        
        title_text = self.font.render("INSTRUCTIONS", True, CYAN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        screen.blit(title_text, title_rect)
        
        instructions = [
            "CONTROLS:",
            "- ARROW KEYS or WASD: Move left/right",
            "- SPACE or UP: Jump",
            "- ESC: Pause game",
            "",
            "GAMEPLAY:",
            "- Collect all crystals to complete each level",
            "- Avoid red enemies - they hurt you!",
            "- Collect yellow coins for points",
            "- Grab power-ups for special abilities:",
            "  * Green (2): Double Jump",
            "  * Yellow (>): Speed Boost",
            "  * Cyan (S): Shield Protection",
            "",
            "- You have 3 lives and a time limit per level",
            "- Complete 5 challenging levels to win!",
            "",
            "Press ESC to return to menu"
        ]
        
        for i, line in enumerate(instructions):
            if line.startswith("CONTROLS:") or line.startswith("GAMEPLAY:"):
                color = YELLOW
            elif line.startswith("  *"):
                color = GREEN
            else:
                color = WHITE
            
            text = self.small_font.render(line, True, color)
            screen.blit(text, (100, 120 + i * 25))
    
    def render_game_enhanced(self, screen):
        # Render level first
        self.current_level.render(screen)
        
        # Render player
        self.player.render(screen)
        
        # Render enhanced UI
        self.render_ui_enhanced(screen)
    
    def render_game(self, screen):
        # Fallback to enhanced version
        self.render_game_enhanced(screen)
    
    def render_ui(self):
        # Create semi-transparent background for UI
        ui_surface = pygame.Surface((300, 120))
        ui_surface.set_alpha(180)
        ui_surface.fill((20, 20, 30))
        self.screen.blit(ui_surface, (5, 5))
        
        # Draw UI border
        ui_border = pygame.Rect(5, 5, 300, 120)
        pygame.draw.rect(self.screen, WHITE, ui_border, 2)
        
        # Lives with heart icons
        lives_text = self.small_font.render(f"Lives:", True, WHITE)
        self.screen.blit(lives_text, (15, 15))
        for i in range(self.player.lives):
            heart_x = 60 + i * 20
            heart_y = 18
            # Simple heart shape using circles and triangle
            pygame.draw.circle(self.screen, RED, (heart_x, heart_y), 6)
            pygame.draw.circle(self.screen, RED, (heart_x + 8, heart_y), 6)
            heart_bottom = [(heart_x - 6, heart_y + 3), (heart_x + 4, heart_y + 12), 
                           (heart_x + 14, heart_y + 3)]
            pygame.draw.polygon(self.screen, RED, heart_bottom)
        
        # Score with coin icon
        coin_icon_pos = (15, 40)
        pygame.draw.circle(self.screen, GOLDEN_YELLOW, coin_icon_pos, 8)
        pygame.draw.circle(self.screen, WHITE, coin_icon_pos, 8, 2)
        score_text = self.small_font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (35, 35))
        
        # Crystals with crystal icon
        crystal_icon_pos = (15, 65)
        crystal_points = [(crystal_icon_pos[0], crystal_icon_pos[1] - 6),
                         (crystal_icon_pos[0] + 6, crystal_icon_pos[1]),
                         (crystal_icon_pos[0], crystal_icon_pos[1] + 6),
                         (crystal_icon_pos[0] - 6, crystal_icon_pos[1])]
        pygame.draw.polygon(self.screen, CRYSTAL_BLUE, crystal_points)
        pygame.draw.polygon(self.screen, WHITE, crystal_points, 2)
        
        crystals_collected = sum(1 for crystal in self.current_level.crystals if crystal.collected)
        crystals_text = self.small_font.render(
            f"Crystals: {crystals_collected}/{self.current_level.crystals_required}", 
            True, CYAN
        )
        self.screen.blit(crystals_text, (35, 60))
        
        # Level info
        level_text = self.small_font.render(
            f"Level: {self.level_manager.current_level + 1}/{self.level_manager.get_total_levels()}", 
            True, WHITE
        )
        self.screen.blit(level_text, (15, 85))
        
        # Timer with enhanced styling
        timer_bg = pygame.Surface((120, 30))
        timer_bg.set_alpha(200)
        timer_bg.fill((30, 30, 40))
        self.screen.blit(timer_bg, (SCREEN_WIDTH - 130, 5))
        
        timer_border = pygame.Rect(SCREEN_WIDTH - 130, 5, 120, 30)
        pygame.draw.rect(self.screen, WHITE, timer_border, 2)
        
        time_left = int(self.level_timer)
        timer_color = RED if time_left < 30 else WHITE
        timer_text = self.small_font.render(f"Time: {time_left}", True, timer_color)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH - 70, 20))
        self.screen.blit(timer_text, timer_rect)
        
        # Level name with decorative background
        level_name_bg = pygame.Surface((200, 25))
        level_name_bg.set_alpha(180)
        level_name_bg.fill((40, 40, 60))
        self.screen.blit(level_name_bg, (SCREEN_WIDTH - 210, 40))
        
        level_name_border = pygame.Rect(SCREEN_WIDTH - 210, 40, 200, 25)
        pygame.draw.rect(self.screen, GOLDEN_YELLOW, level_name_border, 2)
        
        level_name_text = self.small_font.render(self.current_level.name, True, GOLDEN_YELLOW)
        level_name_rect = level_name_text.get_rect(center=(SCREEN_WIDTH - 110, 52))
        self.screen.blit(level_name_text, level_name_rect)
        
        # Power-up indicators with icons
        y_offset = 75
        if self.player.has_double_jump:
            powerup_bg = pygame.Surface((140, 22))
            powerup_bg.set_alpha(180)
            powerup_bg.fill((0, 60, 0))
            self.screen.blit(powerup_bg, (SCREEN_WIDTH - 150, y_offset))
            
            # Double jump icon
            icon_x = SCREEN_WIDTH - 145
            icon_y = y_offset + 11
            pygame.draw.polygon(self.screen, WHITE, [
                (icon_x, icon_y - 4), (icon_x - 3, icon_y - 1), (icon_x + 3, icon_y - 1)
            ])
            pygame.draw.polygon(self.screen, WHITE, [
                (icon_x, icon_y + 1), (icon_x - 3, icon_y + 4), (icon_x + 3, icon_y + 4)
            ])
            
            powerup_text = self.small_font.render("Double Jump", True, GREEN)
            self.screen.blit(powerup_text, (SCREEN_WIDTH - 135, y_offset + 5))
            y_offset += 25
        
        if self.player.has_speed_boost:
            time_left = int(self.player.speed_boost_timer)
            powerup_bg = pygame.Surface((160, 22))
            powerup_bg.set_alpha(180)
            powerup_bg.fill((60, 60, 0))
            self.screen.blit(powerup_bg, (SCREEN_WIDTH - 170, y_offset))
            
            # Speed boost icon (lightning)
            icon_x = SCREEN_WIDTH - 165
            icon_y = y_offset + 11
            lightning_points = [
                (icon_x - 3, icon_y - 4), (icon_x, icon_y - 1),
                (icon_x - 2, icon_y + 1), (icon_x + 3, icon_y + 4),
                (icon_x, icon_y + 1), (icon_x + 2, icon_y - 1)
            ]
            pygame.draw.polygon(self.screen, YELLOW, lightning_points)
            
            powerup_text = self.small_font.render(f"Speed Boost ({time_left}s)", True, YELLOW)
            self.screen.blit(powerup_text, (SCREEN_WIDTH - 155, y_offset + 5))
            y_offset += 25
        
        if self.player.has_shield:
            time_left = int(self.player.shield_timer)
            powerup_bg = pygame.Surface((140, 22))
            powerup_bg.set_alpha(180)
            powerup_bg.fill((0, 40, 60))
            self.screen.blit(powerup_bg, (SCREEN_WIDTH - 150, y_offset))
            
            # Shield icon
            icon_x = SCREEN_WIDTH - 145
            icon_y = y_offset + 11
            shield_points = [
                (icon_x, icon_y - 4), (icon_x - 3, icon_y - 1),
                (icon_x - 3, icon_y + 2), (icon_x, icon_y + 4),
                (icon_x + 3, icon_y + 2), (icon_x + 3, icon_y - 1)
            ]
            pygame.draw.polygon(self.screen, CYAN, shield_points)
            
            powerup_text = self.small_font.render(f"Shield ({time_left}s)", True, CYAN)
            self.screen.blit(powerup_text, (SCREEN_WIDTH - 135, y_offset + 5))
    
    def render_ui_enhanced(self, screen):
        import math
        
        # Create semi-transparent UI background panels
        ui_panel_left = pygame.Surface((250, 120))
        ui_panel_left.set_alpha(180)
        ui_panel_left.fill((20, 20, 40))
        screen.blit(ui_panel_left, (5, 5))
        
        ui_panel_right = pygame.Surface((200, 100))
        ui_panel_right.set_alpha(180)
        ui_panel_right.fill((20, 20, 40))
        screen.blit(ui_panel_right, (SCREEN_WIDTH - 205, 5))
        
        # Enhanced lives display with heart icons
        lives_y = 15
        for i in range(MAX_LIVES):
            heart_x = 15 + i * 25
            if i < self.player.lives:
                # Full heart
                heart_color = RED
                pulse = math.sin(pygame.time.get_ticks() * 0.008) * 0.1 + 1
                heart_size = int(8 * pulse)
            else:
                # Empty heart
                heart_color = GRAY
                heart_size = 8
            
            # Draw heart shape (simplified)
            pygame.draw.circle(screen, heart_color, (heart_x, lives_y), heart_size//2)
            pygame.draw.circle(screen, heart_color, (heart_x + heart_size//2, lives_y), heart_size//2)
            pygame.draw.polygon(screen, heart_color, [
                (heart_x - heart_size//2, lives_y),
                (heart_x + heart_size, lives_y),
                (heart_x + heart_size//4, lives_y + heart_size)
            ])
        
        lives_text = self.small_font.render(f"Lives", True, WHITE)
        screen.blit(lives_text, (15, lives_y + 15))
        
        # Enhanced score with coin icon
        score_text = self.small_font.render(f"Score: {self.player.score}", True, GOLDEN_YELLOW)
        screen.blit(score_text, (15, 45))
        
        # Enhanced crystals display with crystal icon
        crystals_collected = sum(1 for crystal in self.current_level.crystals if crystal.collected)
        crystals_text = self.small_font.render(
            f"Crystals: {crystals_collected}/{self.current_level.crystals_required}", 
            True, CRYSTAL_BLUE
        )
        screen.blit(crystals_text, (15, 70))
        
        # Draw mini crystal icons
        for i in range(self.current_level.crystals_required):
            crystal_x = 100 + i * 15
            crystal_y = 75
            crystal_color = CRYSTAL_BLUE if i < crystals_collected else GRAY
            
            # Draw diamond shape
            points = [
                (crystal_x, crystal_y - 4),
                (crystal_x + 4, crystal_y),
                (crystal_x, crystal_y + 4),
                (crystal_x - 4, crystal_y)
            ]
            pygame.draw.polygon(screen, crystal_color, points)
            if i < crystals_collected:
                pygame.draw.polygon(screen, WHITE, points, 1)
        
        # Level info
        level_text = self.small_font.render(
            f"Level: {self.level_manager.current_level + 1}/{self.level_manager.get_total_levels()}", 
            True, WHITE
        )
        screen.blit(level_text, (15, 95))
        
        # Enhanced timer with warning colors
        time_left = int(self.level_timer)
        if time_left <= 30:
            timer_color = RED
            timer_pulse = math.sin(pygame.time.get_ticks() * 0.02) * 0.3 + 0.7
            timer_color = tuple(min(255, max(0, int(c * timer_pulse))) for c in timer_color)
        elif time_left <= 60:
            timer_color = ORANGE
        else:
            timer_color = WHITE
        
        timer_text = self.small_font.render(f"Time: {time_left}", True, timer_color)
        timer_rect = timer_text.get_rect(topright=(SCREEN_WIDTH - 15, 15))
        screen.blit(timer_text, timer_rect)
        
        # Level name with style
        level_name_text = self.small_font.render(self.current_level.name, True, GOLDEN_YELLOW)
        level_name_rect = level_name_text.get_rect(topright=(SCREEN_WIDTH - 15, 40))
        screen.blit(level_name_text, level_name_rect)
        
        # Enhanced power-up indicators
        y_offset = 70
        if self.player.has_double_jump:
            powerup_bg = pygame.Surface((120, 20))
            powerup_bg.set_alpha(150)
            powerup_bg.fill(GREEN)
            screen.blit(powerup_bg, (SCREEN_WIDTH - 125, y_offset - 2))
            
            powerup_text = self.small_font.render("Double Jump", True, WHITE)
            powerup_rect = powerup_text.get_rect(topright=(SCREEN_WIDTH - 15, y_offset))
            screen.blit(powerup_text, powerup_rect)
            y_offset += 25
        
        if self.player.has_speed_boost:
            time_left = int(self.player.speed_boost_timer)
            
            powerup_bg = pygame.Surface((140, 20))
            powerup_bg.set_alpha(150)
            powerup_bg.fill(GOLDEN_YELLOW)
            screen.blit(powerup_bg, (SCREEN_WIDTH - 145, y_offset - 2))
            
            powerup_text = self.small_font.render(f"Speed Boost ({time_left}s)", True, BLACK)
            powerup_rect = powerup_text.get_rect(topright=(SCREEN_WIDTH - 15, y_offset))
            screen.blit(powerup_text, powerup_rect)
            y_offset += 25
        
        if self.player.has_shield:
            time_left = int(self.player.shield_timer)
            
            powerup_bg = pygame.Surface((110, 20))
            powerup_bg.set_alpha(150)
            powerup_bg.fill(CYAN)
            screen.blit(powerup_bg, (SCREEN_WIDTH - 115, y_offset - 2))
            
            powerup_text = self.small_font.render(f"Shield ({time_left}s)", True, BLACK)
            powerup_rect = powerup_text.get_rect(topright=(SCREEN_WIDTH - 15, y_offset))
            screen.blit(powerup_text, powerup_rect)
    
    def render_pause_overlay(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Pause menu
        pause_text = self.font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(pause_text, pause_rect)
        
        for i, option in enumerate(self.pause_options):
            color = YELLOW if i == self.pause_selection else WHITE
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, 350 + i * 60))
            screen.blit(option_text, option_rect)
    
    def render_game_over(self):
        self.screen.fill(RED)
        
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(game_over_text, game_over_rect)
        
        final_score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, 280))
        self.screen.blit(final_score_text, final_score_rect)
        
        for i, option in enumerate(self.game_over_options):
            color = YELLOW if i == self.game_over_selection else WHITE
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, 380 + i * 60))
            self.screen.blit(option_text, option_rect)
    
    def render_game_over_enhanced(self, screen):
        import math
        
        # Animated gradient background (red to dark red)
        for y in range(SCREEN_HEIGHT):
            color_factor = y / SCREEN_HEIGHT
            red_intensity = int(120 + 80 * math.sin(pygame.time.get_ticks() * 0.002 + y * 0.01))
            color = (
                red_intensity,
                int(20 * (1 - color_factor)),
                int(20 * (1 - color_factor))
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Pulsing skull/death particles
        for i in range(15):
            x = 100 + i * 80 + math.sin(pygame.time.get_ticks() * 0.003 + i) * 20
            y = 100 + math.sin(pygame.time.get_ticks() * 0.004 + i * 0.5) * 30
            size = 3 + int(2 * math.sin(pygame.time.get_ticks() * 0.005 + i))
            alpha = 100 + int(50 * math.sin(pygame.time.get_ticks() * 0.006 + i))
            
            # Draw particle directly without creating surface
            pygame.draw.circle(screen, (255, 100, 100), (int(x), int(y)), size)
        
        # Main title with dramatic effect
        title_pulse = math.sin(pygame.time.get_ticks() * 0.008) * 0.2 + 1
        title_shake_x = int(math.sin(pygame.time.get_ticks() * 0.02) * 3)
        title_shake_y = int(math.cos(pygame.time.get_ticks() * 0.025) * 2)
        
        # Title shadow/glow layers
        for i in range(5):
            shadow_offset = 8 - i
            shadow_alpha = 150 - i * 30
            shadow_color = (100 + i * 20, 0, 0)
            
            shadow_text = self.font.render("GAME OVER", True, shadow_color)
            shadow_rect = shadow_text.get_rect(center=(
                SCREEN_WIDTH//2 + title_shake_x + shadow_offset,
                200 + title_shake_y + shadow_offset
            ))
            
            shadow_surface = pygame.Surface(shadow_text.get_size())
            shadow_surface.set_alpha(shadow_alpha)
            shadow_surface.blit(shadow_text, (0, 0))
            screen.blit(shadow_surface, shadow_rect)
        
        # Main title
        title_color = tuple(min(255, max(0, int(c * title_pulse))) for c in (255, 50, 50))
        game_over_text = self.font.render("GAME OVER", True, title_color)
        game_over_rect = game_over_text.get_rect(center=(
            SCREEN_WIDTH//2 + title_shake_x, 
            200 + title_shake_y
        ))
        screen.blit(game_over_text, game_over_rect)
        
        # Animated subtitle
        subtitle_wave = math.sin(pygame.time.get_ticks() * 0.003) * 0.3 + 0.7
        subtitle_color = tuple(min(255, max(0, int(c * subtitle_wave))) for c in (255, 150, 150))
        subtitle_text = self.small_font.render("Your adventure ends here...", True, subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Score display with frame
        score_bg = pygame.Surface((300, 80))
        score_bg.set_alpha(180)
        score_bg.fill((60, 20, 20))
        screen.blit(score_bg, (SCREEN_WIDTH//2 - 150, 300))
        
        score_border = pygame.Rect(SCREEN_WIDTH//2 - 150, 300, 300, 80)
        pygame.draw.rect(screen, (255, 100, 100), score_border, 3)
        
        final_score_text = self.font.render(f"Final Score: {self.player.score}", True, GOLDEN_YELLOW)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, 340))
        screen.blit(final_score_text, final_score_rect)
        
        # Enhanced menu options
        for i, option in enumerate(self.game_over_options):
            option_y = 450 + i * 60
            
            if i == self.game_over_selection:
                # Selected option effects
                glow_intensity = int(80 + 40 * math.sin(pygame.time.get_ticks() * 0.01))
                
                # Selection background
                option_bg = pygame.Surface((250, 40))
                option_bg.set_alpha(glow_intensity)
                option_bg.fill((200, 50, 50))
                screen.blit(option_bg, (SCREEN_WIDTH//2 - 125, option_y - 15))
                
                # Selection border
                border_rect = pygame.Rect(SCREEN_WIDTH//2 - 125, option_y - 15, 250, 40)
                pygame.draw.rect(screen, GOLDEN_YELLOW, border_rect, 2)
                
                # Animated arrows
                arrow_bounce = math.sin(pygame.time.get_ticks() * 0.012) * 8
                left_arrow_x = SCREEN_WIDTH//2 - 140 - arrow_bounce
                right_arrow_x = SCREEN_WIDTH//2 + 140 + arrow_bounce
                
                # Draw arrow triangles
                pygame.draw.polygon(screen, GOLDEN_YELLOW, [
                    (left_arrow_x, option_y),
                    (left_arrow_x + 15, option_y - 8),
                    (left_arrow_x + 15, option_y + 8)
                ])
                pygame.draw.polygon(screen, GOLDEN_YELLOW, [
                    (right_arrow_x, option_y),
                    (right_arrow_x - 15, option_y - 8),
                    (right_arrow_x - 15, option_y + 8)
                ])
                
                option_color = GOLDEN_YELLOW
            else:
                option_color = (255, 180, 180)
            
            option_text = self.font.render(option, True, option_color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, option_y))
            screen.blit(option_text, option_rect)
    
    def render_level_complete(self):
        self.screen.fill(GREEN)
        
        complete_text = self.font.render("LEVEL COMPLETE!", True, WHITE)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(complete_text, complete_rect)
        
        crystals_collected = sum(1 for crystal in self.current_level.crystals if crystal.collected)
        stats_lines = [
            f"Crystals Collected: {crystals_collected}/{len(self.current_level.crystals)}",
            f"Time Remaining: {int(self.level_timer)}s",
            f"Score Earned: {self.player.score}",
            "",
            "Press SPACE to continue"
        ]
        
        for i, line in enumerate(stats_lines):
            text = self.small_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 350 + i * 30))
            self.screen.blit(text, text_rect)
    
    def render_level_complete_enhanced(self, screen):
        import math
        
        # Celebratory gradient background (green to gold)
        for y in range(SCREEN_HEIGHT):
            color_factor = y / SCREEN_HEIGHT
            green_pulse = 1 + 0.3 * math.sin(pygame.time.get_ticks() * 0.003)
            color = (
                min(255, max(0, int((50 + 100 * color_factor) * green_pulse))),
                min(255, max(0, int((200 - 50 * color_factor) * green_pulse))),
                min(255, max(0, int(50 * (1 - color_factor))))
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Celebration particles (stars and sparkles)
        for i in range(25):
            x = (100 + i * 40 + pygame.time.get_ticks() * 0.1 * (i % 3 + 1)) % SCREEN_WIDTH
            y = 50 + i * 20 + math.sin(pygame.time.get_ticks() * 0.005 + i) * 30
            
            # Star particles
            if i % 3 == 0:
                star_size = 4 + int(3 * math.sin(pygame.time.get_ticks() * 0.008 + i))
                star_alpha = 150 + int(100 * math.sin(pygame.time.get_ticks() * 0.006 + i))
                
                # Draw 5-pointed star
                star_points = []
                for j in range(10):
                    angle = j * math.pi / 5
                    radius = star_size if j % 2 == 0 else star_size // 2
                    star_x = x + radius * math.cos(angle)
                    star_y = y + radius * math.sin(angle)
                    star_points.append((star_x, star_y))
                
                star_surface = pygame.Surface((star_size * 4, star_size * 4))
                star_surface.set_alpha(star_alpha)
                pygame.draw.polygon(star_surface, GOLDEN_YELLOW, 
                                  [(p[0] - x + star_size * 2, p[1] - y + star_size * 2) for p in star_points])
                screen.blit(star_surface, (x - star_size * 2, y - star_size * 2))
            else:
                # Sparkle particles
                sparkle_size = 2 + int(2 * math.sin(pygame.time.get_ticks() * 0.01 + i))
                sparkle_alpha = 120 + int(80 * math.sin(pygame.time.get_ticks() * 0.007 + i))
                
                # Draw sparkle directly without creating surface
                pygame.draw.circle(screen, WHITE, (int(x), int(y)), sparkle_size)
        
        # Main title with celebration effect
        title_bounce = math.sin(pygame.time.get_ticks() * 0.006) * 10
        title_scale = 1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.004)
        
        # Title glow layers
        for i in range(6):
            glow_alpha = 100 - i * 15
            glow_size = i * 3
            glow_color = (100 + i * 25, 255 - i * 20, 50 + i * 10)
            
            glow_surface = pygame.Surface((400 + glow_size, 80 + glow_size))
            glow_surface.set_alpha(glow_alpha)
            glow_surface.fill(glow_color)
            glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH//2, 150 + title_bounce))
            screen.blit(glow_surface, glow_rect)
        
        # Main title
        complete_text = self.font.render("LEVEL COMPLETE!", True, WHITE)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, 150 + title_bounce))
        screen.blit(complete_text, complete_rect)
        
        # Victory message
        victory_pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.2 + 0.8
        victory_color = tuple(min(255, max(0, int(c * victory_pulse))) for c in GOLDEN_YELLOW)
        victory_text = self.small_font.render("🎉 Excellent work, Crystal Hunter! 🎉", True, victory_color)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        # Remove emoji for compatibility
        clean_victory = "Excellent work, Crystal Hunter!"
        victory_text = self.small_font.render(clean_victory, True, victory_color)
        screen.blit(victory_text, victory_rect)
        
        # Stats panel with fancy border
        panel_width = 400
        panel_height = 200
        panel_x = SCREEN_WIDTH//2 - panel_width//2
        panel_y = 280
        
        # Panel background with transparency
        panel_bg = pygame.Surface((panel_width, panel_height))
        panel_bg.set_alpha(200)
        panel_bg.fill((20, 60, 20))
        screen.blit(panel_bg, (panel_x, panel_y))
        
        # Animated border
        border_glow = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.008))
        border_color = (100, 255, 100, border_glow)
        pygame.draw.rect(screen, (100, 255, 100), 
                        pygame.Rect(panel_x, panel_y, panel_width, panel_height), 4)
        
        # Inner border decoration
        pygame.draw.rect(screen, GOLDEN_YELLOW, 
                        pygame.Rect(panel_x + 10, panel_y + 10, panel_width - 20, panel_height - 20), 2)
        
        # Statistics with icons and colors
        crystals_collected = sum(1 for crystal in self.current_level.crystals if crystal.collected)
        stats_data = [
            ("💎", f"Crystals: {crystals_collected}/{len(self.current_level.crystals)}", CRYSTAL_BLUE),
            ("⏱️", f"Time Bonus: {int(self.level_timer)}s", CYAN),
            ("🏆", f"Score: {self.player.score}", GOLDEN_YELLOW),
        ]
        
        for i, (icon, text, color) in enumerate(stats_data):
            # Remove emoji and use colored text
            clean_text = text.replace("💎 ", "").replace("⏱️ ", "").replace("🏆 ", "")
            stat_y = panel_y + 40 + i * 40
            
            # Icon - draw colored circle directly without background
            icon_color = color
            pygame.draw.circle(screen, icon_color, (panel_x + 30, stat_y), 8)
            pygame.draw.circle(screen, WHITE, (panel_x + 30, stat_y), 8, 2)
            
            # Stat text with animation
            text_pulse = 1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.006 + i)
            text_color = tuple(min(255, max(0, int(c * text_pulse))) for c in color)
            stat_text = self.small_font.render(clean_text, True, text_color)
            screen.blit(stat_text, (panel_x + 50, stat_y - 8))
        
        # Performance rating
        rating_y = panel_y + 160
        if crystals_collected == len(self.current_level.crystals) and self.level_timer > 60:
            rating = "*** PERFECT!"
            rating_color = GOLDEN_YELLOW
            star_count = 3
        elif crystals_collected == len(self.current_level.crystals):
            rating = "** GREAT!"
            rating_color = (255, 200, 100)
            star_count = 2
        else:
            rating = "* GOOD!"
            rating_color = (200, 200, 200)
            star_count = 1
        
        rating_pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.3 + 0.7
        rating_color = tuple(min(255, max(0, int(c * rating_pulse))) for c in rating_color)
        
        # Draw custom stars instead of using unicode
        star_y = rating_y
        star_start_x = SCREEN_WIDTH//2 - 60
        
        for i in range(star_count):
            star_x = star_start_x + i * 25
            # Draw 5-pointed star
            star_points = []
            for j in range(10):
                angle = j * math.pi / 5 - math.pi / 2  # Start from top
                radius = 8 if j % 2 == 0 else 4
                px = star_x + radius * math.cos(angle)
                py = star_y + radius * math.sin(angle)
                star_points.append((px, py))
            pygame.draw.polygon(screen, rating_color, star_points)
            pygame.draw.polygon(screen, WHITE, star_points, 1)
        
        # Draw rating text without stars
        rating_text_only = rating.replace("*", "").strip()
        rating_text = self.small_font.render(rating_text_only, True, rating_color)
        rating_rect = rating_text.get_rect(center=(SCREEN_WIDTH//2 + 40, rating_y))
        screen.blit(rating_text, rating_rect)
        
        # Continue instruction with animation
        continue_pulse = math.sin(pygame.time.get_ticks() * 0.008) * 0.4 + 0.6
        continue_color = tuple(min(255, max(0, int(c * continue_pulse))) for c in WHITE)
        continue_text = self.small_font.render("Press SPACE to continue your quest!", True, continue_color)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, 550))
        screen.blit(continue_text, continue_rect)
    
    def render_game_complete(self):
        self.screen.fill(PURPLE)
        
        complete_text = self.font.render("CONGRATULATIONS!", True, WHITE)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(complete_text, complete_rect)
        
        victory_text = self.font.render("You completed Crystal Quest!", True, YELLOW)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, 280))
        self.screen.blit(victory_text, victory_rect)
        
        stats_lines = [
            f"Final Score: {self.player.score}",
            f"Total Time: {int(self.game_timer)}s",
            "",
            "Thanks for playing!",
            "",
            "Press SPACE to play again"
        ]
        
        for i, line in enumerate(stats_lines):
            text = self.small_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 380 + i * 30))
            self.screen.blit(text, text_rect)
    
    def render_game_complete_enhanced(self, screen):
        import math
        
        # Epic victory gradient background (purple to gold)
        for y in range(SCREEN_HEIGHT):
            color_factor = y / SCREEN_HEIGHT
            time_factor = math.sin(pygame.time.get_ticks() * 0.002) * 0.3 + 0.7
            color = (
                min(255, max(0, int((150 + 105 * color_factor) * time_factor))),
                min(255, max(0, int((50 + 150 * color_factor) * time_factor))),
                min(255, max(0, int((180 - 130 * color_factor) * time_factor)))
            )
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Victory fireworks particles
        for i in range(30):
            explosion_time = (pygame.time.get_ticks() + i * 200) * 0.005
            x = 200 + (i % 8) * 120 + math.sin(explosion_time) * 50
            y = 100 + (i // 8) * 100 + math.cos(explosion_time * 1.5) * 30
            
            # Firework particles
            for j in range(8):
                angle = j * math.pi / 4 + explosion_time
                distance = 20 + 15 * math.sin(explosion_time * 2)
                px = x + distance * math.cos(angle)
                py = y + distance * math.sin(angle)
                
                particle_size = 3 + int(2 * math.sin(explosion_time * 3 + j))
                colors = [GOLDEN_YELLOW, WHITE, CYAN, PINK]
                particle_color = colors[j % len(colors)]
                
                particle_alpha = int(200 * (1 - (explosion_time % 2) / 2))
                if particle_alpha > 0:
                    # Draw particle directly without creating surface
                    pygame.draw.circle(screen, particle_color, (int(px), int(py)), particle_size)
        
        # Main title with epic scaling effect
        title_time = pygame.time.get_ticks() * 0.003
        title_scale = 1 + 0.2 * math.sin(title_time * 0.5)
        title_rainbow_shift = math.sin(title_time) * 50
        
        # Rainbow title effect
        rainbow_colors = [
            (255, int(100 + 155 * math.sin(title_time)), 100),
            (255, 200, int(100 + 155 * math.sin(title_time + 1))),
            (int(100 + 155 * math.sin(title_time + 2)), 255, 255),
        ]
        
        for i, color in enumerate(rainbow_colors):
            offset = i * 3
            title_text = self.font.render("CONGRATULATIONS!", True, color)
            title_rect = title_text.get_rect(center=(
                SCREEN_WIDTH//2 + offset, 
                120 + offset + int(10 * math.sin(title_time + i))
            ))
            screen.blit(title_text, title_rect)
        
        # Main title (white on top)
        title_text = self.font.render("CONGRATULATIONS!", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 120))
        screen.blit(title_text, title_rect)
        
        # Epic subtitle
        subtitle_glow = math.sin(pygame.time.get_ticks() * 0.006) * 0.3 + 0.7
        subtitle_color = tuple(min(255, max(0, int(c * subtitle_glow))) for c in GOLDEN_YELLOW)
        victory_text = self.font.render("You completed Crystal Quest!", True, subtitle_color)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        screen.blit(victory_text, victory_rect)
        
        # Master achievement banner
        banner_width = 500
        banner_height = 60
        banner_x = SCREEN_WIDTH//2 - banner_width//2
        banner_y = 220
        
        # Banner background with glow
        for i in range(5):
            glow_alpha = 100 - i * 15
            glow_expansion = i * 5
            glow_surface = pygame.Surface((banner_width + glow_expansion, banner_height + glow_expansion))
            glow_surface.set_alpha(glow_alpha)
            glow_surface.fill(GOLDEN_YELLOW)
            glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH//2, banner_y + banner_height//2))
            screen.blit(glow_surface, glow_rect)
        
        # Banner main background
        banner_bg = pygame.Surface((banner_width, banner_height))
        banner_bg.set_alpha(220)
        banner_bg.fill((80, 40, 100))
        screen.blit(banner_bg, (banner_x, banner_y))
        
        # Banner borders
        pygame.draw.rect(screen, GOLDEN_YELLOW, 
                        pygame.Rect(banner_x, banner_y, banner_width, banner_height), 4)
        pygame.draw.rect(screen, WHITE, 
                        pygame.Rect(banner_x + 5, banner_y + 5, banner_width - 10, banner_height - 10), 2)
        
        # Achievement text
        achievement_pulse = math.sin(pygame.time.get_ticks() * 0.008) * 0.2 + 0.8
        achievement_color = tuple(min(255, max(0, int(c * achievement_pulse))) for c in GOLDEN_YELLOW)
        achievement_text = self.small_font.render("🏆 CRYSTAL MASTER ACHIEVED! 🏆", True, achievement_color)
        achievement_rect = achievement_text.get_rect(center=(SCREEN_WIDTH//2, banner_y + banner_height//2))
        # Remove emoji for compatibility
        clean_achievement = "CRYSTAL MASTER ACHIEVED!"
        achievement_text = self.small_font.render(clean_achievement, True, achievement_color)
        screen.blit(achievement_text, achievement_rect)
        
        # Final stats panel
        stats_panel_width = 400
        stats_panel_height = 180
        stats_x = SCREEN_WIDTH//2 - stats_panel_width//2
        stats_y = 320
        
        # Stats background
        stats_bg = pygame.Surface((stats_panel_width, stats_panel_height))
        stats_bg.set_alpha(200)
        stats_bg.fill((40, 20, 60))
        screen.blit(stats_bg, (stats_x, stats_y))
        
        # Stats border with animation
        border_pulse = int(150 + 50 * math.sin(pygame.time.get_ticks() * 0.01))
        border_color = (border_pulse, 150, 255)
        pygame.draw.rect(screen, border_color, 
                        pygame.Rect(stats_x, stats_y, stats_panel_width, stats_panel_height), 3)
        
        # Final statistics
        total_time_minutes = int(self.game_timer // 60)
        total_time_seconds = int(self.game_timer % 60)
        
        final_stats = [
            f"Final Score: {self.player.score}",
            f"Total Time: {total_time_minutes}m {total_time_seconds}s",
            f"Levels Conquered: {self.level_manager.get_total_levels()}",
            "Status: LEGENDARY HERO!"
        ]
        
        stat_colors = [GOLDEN_YELLOW, CYAN, GREEN, PINK]
        
        for i, (stat, color) in enumerate(zip(final_stats, stat_colors)):
            stat_wave = math.sin(pygame.time.get_ticks() * 0.005 + i * 0.5) * 0.2 + 0.8
            final_color = tuple(min(255, max(0, int(c * stat_wave))) for c in color)
            stat_text = self.small_font.render(stat, True, final_color)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH//2, stats_y + 30 + i * 35))
            screen.blit(stat_text, stat_rect)
        
        # Thank you message
        thanks_y = 540
        thanks_pulse = math.sin(pygame.time.get_ticks() * 0.004) * 0.3 + 0.7
        thanks_color = tuple(min(255, max(0, int(c * thanks_pulse))) for c in WHITE)
        thanks_text = self.small_font.render("Thanks for playing Crystal Quest!", True, thanks_color)
        thanks_rect = thanks_text.get_rect(center=(SCREEN_WIDTH//2, thanks_y))
        screen.blit(thanks_text, thanks_rect)
        
        # Play again instruction
        play_again_pulse = math.sin(pygame.time.get_ticks() * 0.012) * 0.4 + 0.6
        play_again_color = tuple(min(255, max(0, int(c * play_again_pulse))) for c in GOLDEN_YELLOW)
        play_again_text = self.small_font.render("Press SPACE to embark on a new quest!", True, play_again_color)
        play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH//2, 580))
        screen.blit(play_again_text, play_again_rect)
