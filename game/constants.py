# Game Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors - Enhanced palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (70, 130, 255)
YELLOW = (255, 220, 50)
PURPLE = (180, 50, 180)
ORANGE = (255, 140, 50)
CYAN = (50, 220, 255)
PINK = (255, 150, 200)
GRAY = (128, 128, 128)
DARK_GRAY = (45, 45, 55)
LIGHT_BLUE = (150, 200, 255)

# Enhanced color palette
DEEP_BLUE = (25, 40, 80)
NIGHT_BLUE = (15, 25, 50)
FOREST_GREEN = (34, 80, 34)
CRYSTAL_BLUE = (100, 200, 255)
LAVA_RED = (255, 80, 40)
GOLDEN_YELLOW = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

# Platform colors by level theme
PLATFORM_COLORS = {
    0: WHITE,  # Tutorial - clean white
    1: LIGHT_BLUE,  # Sky level - light blue
    2: LAVA_RED,  # Cave level - red/orange
    3: CRYSTAL_BLUE,  # Crystal level - cyan/blue
    4: GOLDEN_YELLOW  # Final level - gold
}

# Background gradients by level
BACKGROUND_GRADIENTS = {
    0: [(120, 180, 255), (200, 230, 255)],  # Tutorial - light sky
    1: [(100, 50, 150), (150, 100, 200)],  # Sky - purple gradient
    2: [(150, 50, 50), (100, 30, 30)],     # Cave - red/dark
    3: [(50, 150, 100), (30, 100, 80)],    # Crystal - green
    4: [(100, 100, 50), (150, 150, 100)]   # Final - gold/brown
}

# Player constants
PLAYER_SPEED = 300
PLAYER_JUMP_SPEED = 600
GRAVITY = 1500
PLAYER_SIZE = 32

# Enemy constants
ENEMY_SPEED = 100
ENEMY_SIZE = 28

# Platform constants
PLATFORM_THICKNESS = 20

# Collectibles
CRYSTAL_SIZE = 20
COIN_SIZE = 16

# Power-ups
POWERUP_SIZE = 28
POWERUP_DURATION = 10.0  # seconds

# Game mechanics
MAX_LIVES = 3
LEVEL_TIME_LIMIT = 180  # 3 minutes per level

# Visual effects
PARTICLE_COUNT = 50
SHADOW_OFFSET = 2
BORDER_WIDTH = 3

# Sounds (we'll use simple tones)
JUMP_SOUND_FREQ = 400
COLLECT_SOUND_FREQ = 800
DAMAGE_SOUND_FREQ = 200
POWERUP_SOUND_FREQ = 1000
