import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 1200
HEIGHT = 800

# Create the clock and set frame rate
clock = pygame.time.Clock()
FRAME_RATE = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (100, 149, 237)
BROWN = (139, 69, 19)
MENU_BG = (50, 50, 50, 200)  # Semi-transparent background

# Grid settings
GRID_SIZE = 20
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

# Add this at the start of the file, after imports
def load_image(path, size=None):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading image {path}: {e}")
        # Create a colored surface as fallback
        surface = pygame.Surface(size if size else (GRID_SIZE, GRID_SIZE))
        surface.fill(GRAY)  # Use gray as fallback color
        return surface

def play_music(path, loops=-1):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Music file not found: {path}")
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.3)  # Lower the music volume to 30%
        pygame.mixer.music.play(loops)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error playing music {path}: {e}")

def load_sound(path):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Sound file not found: {path}")
        sound = pygame.mixer.Sound(path)
        sound.set_volume(0.8)  # Set sound effects to 80% volume
        return sound
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading sound {path}: {e}")
        return None

def load_sprite_sheet(path, frame_count, frame_width, frame_height):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Sprite sheet not found: {path}")
        sheet = pygame.image.load(path)
        frames = []
        sheet_width = sheet.get_width()
        frames_per_row = sheet_width // frame_width
        
        print(f"Sheet dimensions: {sheet.get_width()}x{sheet.get_height()}")
        print(f"Frames per row: {frames_per_row}")
        
        for i in range(frame_count):
            # Calculate position in sprite sheet
            row = i // frames_per_row
            col = i % frames_per_row
            
            # Create frame surface with transparency
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            
            # Calculate exact pixel coordinates in the sprite sheet
            x = col * frame_width
            y = row * frame_height
            
            print(f"Loading frame {i} from position ({x}, {y})")
            
            # Copy the correct area from the sprite sheet
            frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
            frames.append(frame)
        return frames
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading sprite sheet {path}: {e}")
        return None

# Modify the asset loading code to use the new functions
rock_tile = load_image('tiles/rock_tile.png', (GRID_SIZE, GRID_SIZE))
dungeon_tile1 = load_image('tiles/dungeon_tile1.png', (GRID_SIZE, GRID_SIZE))
dungeon_tile2 = load_image('tiles/dungeon_tile2.png', (GRID_SIZE, GRID_SIZE))
chest_tile = load_image('tiles/chest_tile.png', (GRID_SIZE, GRID_SIZE))
stairs_tile = load_image('tiles/stairs_tile.png', (GRID_SIZE, GRID_SIZE))

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeons of Eldoria")

COMBAT_SPRITE_SIZE = 100  # 40 * 2.5 = 100 pixels

# Add this before the Player class
player_sprites = load_sprite_sheet('characters/sprite_sheets/player.png', 96, 16, 16)  # Total frames in sheet

# Add fallback for player sprites if loading fails
if player_sprites is None:
    # Create basic colored sprites as fallback
    player_sprites = []
    for _ in range(96):  # Create 48 frames
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        surface.fill(BLUE)  # Use blue as fallback color
        player_sprites.append(surface)
    print("Using fallback blue sprites - could not load player sprite sheet")

# Add after player sprite loading
enemy_sprites = load_sprite_sheet('characters/sprite_sheets/enemies.png', 96, 16, 16)  # Total frames in sheet

# Add fallback for enemy sprites if loading fails
if enemy_sprites is None:
    enemy_sprites = []
    for _ in range(96):
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        surface.fill(RED)
        enemy_sprites.append(surface)
    print("Using fallback red sprites - could not load enemy sprite sheet")

# Add before Player class
class Skill:
    def __init__(self, name, damage, cost, target_type='single', effect_type='damage'):
        self.name = name
        self.damage = damage
        self.cost = cost
        self.target_type = target_type  # 'single', 'all'
        self.effect_type = effect_type  # 'damage', 'heal', 'buff'

# Player class (now after Skill class)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load the directional sprites with animation frames and scale them to fill the grid
        # With 12 frames per row, 3 frames per direction:
        # Row 0 (frames 0-11): Down = frames 0,1,2
        # Row 1 (frames 12-23): Left = frames 12,13,14
        # Row 2 (frames 24-35): Right = frames 24,25,26
        # Row 3 (frames 36-47): Up = frames 36,37,38
        self.sprites = {
            'down': [pygame.transform.scale(player_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in [0, 1, 2]],
            'left': [pygame.transform.scale(player_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in [12, 13, 14]],
            'right': [pygame.transform.scale(player_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in [24, 25, 26]],
            'up': [pygame.transform.scale(player_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in [36, 37, 38]]
        }
        
        # Print sprite information for debugging
        print("Loaded sprite dimensions:")
        for direction, frames in self.sprites.items():
            for i, frame in enumerate(frames):
                print(f"{direction} frame {i}: {frame.get_width()}x{frame.get_height()}")
        self.direction = 'down'  # Default direction
        self.current_frame = 0  # Current frame index (0-2) for each direction
        
        # Set initial sprite
        self.image = self.sprites[self.direction][0]
        self.rect = self.image.get_rect()
        # Position exactly on grid without the +1 offset
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE
        
        # Rest of the initialization
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.level = 1
        self.is_alive = True
        self.name = "Player"
        self.mana = 100
        self.max_mana = 100
        self.defense_bonus = 1
        self.speed = 1.0
        self.skills = [
            Skill("Power Attack", 15, 20),
            Skill("Multi Strike", 10, 25, target_type='all')
        ]
        self.combat_sprite = pygame.image.load('characters/hero.png')
        self.combat_sprite = pygame.transform.scale(self.combat_sprite, (COMBAT_SPRITE_SIZE, COMBAT_SPRITE_SIZE))

    def move(self, dx, dy):
        if dx == 0 and dy == 0:
            return
            
        # Update direction based on movement
        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'
        elif dy > 0:
            self.direction = 'down'
        elif dy < 0:
            self.direction = 'up'
        
        # Calculate new position
        new_x = self.rect.x + dx * GRID_SIZE
        new_y = self.rect.y + dy * GRID_SIZE
        
        # Create a slightly smaller rect for collision testing with walls
        test_rect = pygame.Rect(new_x + 2, new_y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
        
        # Only update position if there's no wall collision
        colliding = any(wall.rect.colliderect(test_rect) for wall in walls)
        if not colliding:
            self.rect.x = new_x
            self.rect.y = new_y
            # Update animation frame only when actually moving to new grid position
            self.current_frame = (self.current_frame + 1) % 3
            self.image = self.sprites[self.direction][self.current_frame]

# Updated Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__()
        # Load the directional sprites with animation frames
        self.sprites = {
            'down': [pygame.transform.scale(enemy_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in range(54, 57)],
            'left': [pygame.transform.scale(enemy_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in range(66, 69)],
            'right': [pygame.transform.scale(enemy_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in range(78, 81)],
            'up': [pygame.transform.scale(enemy_sprites[i], (GRID_SIZE, GRID_SIZE)) for i in range(90, 93)]
        }
        self.direction = 'down'  # Default direction
        self.current_frame = 0  # Current frame index (0-2)
        
        # Set initial sprite
        self.image = self.sprites[self.direction][0]
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE
        
        self.level = level
        self.health = 30 + (level * 10)
        self.attack = 5 + (level * 2)
        self.speed = 1.0
        self.vision_range = 8 * GRID_SIZE
        self.move_cooldown = 0
        self.move_delay = 30
        self.is_alive = True

    def move_towards_player(self, player, walls):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # Calculate direction to player
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        
        # Only move if within vision range
        dist = math.hypot(dx, dy)
        if dist > self.vision_range:
            return
        
        # Determine primary direction (horizontal or vertical)
        if abs(dx) > abs(dy):
            # Move horizontally
            dx = 1 if dx > 0 else -1
            dy = 0
        else:
            # Move vertically
            dx = 0
            dy = 1 if dy > 0 else -1

        # Update direction based on movement
        if dx > 0:
            self.direction = 'right'
        elif dx < 0:
            self.direction = 'left'
        elif dy > 0:
            self.direction = 'down'
        elif dy < 0:
            self.direction = 'up'

        # Calculate new position
        new_x = self.rect.x + dx * GRID_SIZE
        new_y = self.rect.y + dy * GRID_SIZE

        # Create collision rect for testing
        test_rect = pygame.Rect(new_x + 2, new_y + 2, GRID_SIZE - 4, GRID_SIZE - 4)

        # Check collisions with walls and other enemies
        wall_collision = any(wall.rect.colliderect(test_rect) for wall in walls)
        enemy_collision = any(enemy.rect.colliderect(test_rect) for enemy in enemies if enemy != self)

        # Only move if there are no collisions with walls or other enemies
        # Note: We don't check player collision here to allow battle initiation
        if not (wall_collision or enemy_collision):
            self.rect.x = new_x
            self.rect.y = new_y
            # Update animation frame only when actually moving
            self.current_frame = (self.current_frame + 1) % 3
            self.image = self.sprites[self.direction][self.current_frame]
            self.move_cooldown = self.move_delay

# Item class
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.image = chest_tile  # Use chest_tile instead of yellow surface
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE + 1
        self.rect.y = y * GRID_SIZE + 1
        self.type = item_type

# Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = rock_tile  # Use rock_tile instead of a grey surface
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE

# Stairs class
class Stairs(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = stairs_tile  # Use stairs_tile instead of green surface
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE + 1
        self.rect.y = y * GRID_SIZE + 1

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
items = pygame.sprite.Group()
walls = pygame.sprite.Group()

# Create player, party members, and stairs
player = None
party_members = []  # Initialize as empty list
stairs = None
floor_pattern = None

# Define the PartyMember class before using it
class PartyMember(pygame.sprite.Sprite):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.mana = 100
        self.max_mana = 100
        self.defense_bonus = 1
        self.speed = 1.0  # Add speed attribute
        self.skills = []
        
        if role == 'Warrior':
            self.health = 120
            self.max_health = 120
            self.attack = 12
            self.color = RED
            self.skills = [
                Skill("Slash All", 8, 20, target_type='all'),
                Skill("Power Strike", 20, 15)
            ]
        elif role == 'Mage':
            self.health = 80
            self.max_health = 80
            self.attack = 15
            self.color = LIGHT_BLUE
            self.skills = [
                Skill("Fireball", 25, 20),
                Skill("Lightning Storm", 15, 30, target_type='all')
            ]
        elif role == 'Healer':
            self.health = 90
            self.max_health = 90
            self.attack = 8
            self.color = GREEN
            self.skills = [
                Skill("Heal", 30, 20, effect_type='heal'),
                Skill("Group Heal", 15, 35, target_type='all', effect_type='heal')
            ]
        self.is_alive = True
        self.name = role
        # Load combat sprite
        self.combat_sprite = pygame.image.load(f'characters/{role.lower()}.png')
        self.combat_sprite = pygame.transform.scale(self.combat_sprite, (COMBAT_SPRITE_SIZE, COMBAT_SPRITE_SIZE))

# Ensure the PartyMember class is defined before this function
def generate_dungeon(level):
    global player, party_members, stairs, floor_pattern
    all_sprites.empty()
    enemies.empty()
    items.empty()
    walls.empty()
    
    # Initialize player and party members if they don't exist
    if player is None:
        player = Player(0, 0)
        party_members = [
            PartyMember('Warrior'),
            PartyMember('Mage'),
            PartyMember('Healer')
        ]
    
    # Reset defense bonus and regenerate some mana for all characters
    player.defense_bonus = 1
    player.mana = min(player.max_mana, player.mana + 50)  # Regenerate 50 mana between levels
    for member in party_members:
        member.defense_bonus = 1
        member.mana = min(member.max_mana, member.mana + 50)  # Regenerate 50 mana between levels
    
    # Create grid
    grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    
    # Create floor tile pattern
    floor_pattern = [[random.choice([dungeon_tile1, dungeon_tile2]) for _ in range(COLS)] for _ in range(ROWS)]

    # Create rooms with more structure
    rooms = []
    max_attempts = 50
    target_rooms = 5 + level  # Base number of rooms
    min_room_size = 5
    max_room_size = 8

    # Divide the dungeon into sectors to ensure better distribution
    sectors_h = 3
    sectors_v = 3
    sector_w = (COLS - 2) // sectors_h
    sector_h = (ROWS - 2) // sectors_v

    # Try to place rooms in each sector
    for sy in range(sectors_v):
        for sx in range(sectors_h):
            attempts = 0
            while attempts < max_attempts and len(rooms) < target_rooms:
                room_width = random.randint(min_room_size, max_room_size)
                room_height = random.randint(min_room_size, max_room_size)
                
                # Calculate bounds for this sector
                min_x = 1 + sx * sector_w
                max_x = min_x + sector_w - room_width - 1
                min_y = 1 + sy * sector_h
                max_y = min_y + sector_h - room_height - 1
                
                # Ensure we stay within grid bounds
                max_x = min(max_x, COLS - room_width - 1)
                max_y = min(max_y, ROWS - room_height - 1)
                
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)

                # Add padding around rooms
                overlaps = any(
                    x - 1 < r[0] + r[2] + 1 and x + room_width + 1 > r[0] and
                    y - 1 < r[1] + r[3] + 1 and y + room_height + 1 > r[1]
                    for r in rooms
                )

                if not overlaps:
                    # Carve out room
                    for i in range(y, y + room_height):
                        for j in range(x, x + room_width):
                            grid[i][j] = 0
                    rooms.append((x, y, room_width, room_height))
                    break
                attempts += 1

    # Connect rooms using A* pathfinding
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def get_neighbors(pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if 0 < new_x < COLS-1 and 0 < new_y < ROWS-1:
                neighbors.append((new_x, new_y))
        return neighbors

    def create_corridor(start, end):
        open_set = [(0, start)]
        came_from = {start: None}
        g_score = {start: 0}
        f_score = {start: manhattan_distance(start, end)}
        
        while open_set:
            current = min(open_set, key=lambda x: x[0])[1]
            if current == end:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            
            open_set = [(f, pos) for f, pos in open_set if pos != current]
            
            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + manhattan_distance(neighbor, end)
                    open_set.append((f_score[neighbor], neighbor))
        
        return None

    # Connect rooms in a more structured way
    for i in range(len(rooms) - 1):
        room1 = rooms[i]
        room2 = rooms[i + 1]
        
        # Get center points of rooms
        start_x = room1[0] + room1[2] // 2
        start_y = room1[1] + room1[3] // 2
        end_x = room2[0] + room2[2] // 2
        end_y = room2[1] + room2[3] // 2
        
        # Create corridor between rooms
        path = create_corridor((start_x, start_y), (end_x, end_y))
        if path:
            for x, y in path:
                grid[y][x] = 0
                # Add some width to corridors
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 < nx < COLS-1 and 0 < ny < ROWS-1:
                        grid[ny][nx] = 0

    # Create wall sprites
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == 1:
                wall = Wall(x, y)
                walls.add(wall)
                all_sprites.add(wall)

    # Place player in first room
    player_x, player_y = rooms[0][0] + 1, rooms[0][1] + 1
    if player is None:  # Only create new player if one doesn't exist
        player = Player(player_x, player_y)
        party_members = [
            PartyMember('Warrior'),
            PartyMember('Mage'),
            PartyMember('Healer')
        ]
    else:  # Otherwise just update position
        player.rect.x = player_x * GRID_SIZE + 1
        player.rect.y = player_y * GRID_SIZE + 1
    all_sprites.add(player)

    # Place stairs in last room
    stairs_x, stairs_y = rooms[-1][0] + rooms[-1][2] - 2, rooms[-1][1] + rooms[-1][3] - 2
    stairs = Stairs(stairs_x, stairs_y)
    all_sprites.add(stairs)

    # Add enemies and items to rooms
    for room in rooms[1:-1]:  # Skip first and last room
        x, y, w, h = room
        for _ in range(random.randint(1, 3 + level // 2)):
            enemy_x, enemy_y = random.randint(x+1, x+w-2), random.randint(y+1, y+h-2)
            enemy = Enemy(enemy_x, enemy_y, level)
            enemies.add(enemy)
            all_sprites.add(enemy)

        if random.random() < 0.7:  # 70% chance for an item
            item_x, item_y = random.randint(x+1, x+w-2), random.randint(y+1, y+h-2)
            item_type = random.choice(['health_potion', 'strength_potion', 'speed_potion'])
            item = Item(item_x, item_y, item_type)
            items.add(item)
            all_sprites.add(item)

    # Add some obstacles in corridors
    for _ in range(10 + level * 2):
        x, y = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        if grid[y][x] == 0 and not any(sprite.rect.collidepoint(x*GRID_SIZE, y*GRID_SIZE) for sprite in all_sprites):
            wall = Wall(x, y)
            walls.add(wall)
            all_sprites.add(wall)

# Generate initial dungeon
generate_dungeon(1)

# Add new functions for menus
def draw_text_centered(text, font_size, y_position, color=WHITE):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH/2, y_position))
    screen.blit(text_surface, text_rect)

def draw_button(text, y_position, selected=False):
    button_width = 200
    button_height = 50
    button_x = WIDTH/2 - button_width/2
    button_rect = pygame.Rect(button_x, y_position, button_width, button_height)
    
    pygame.draw.rect(screen, LIGHT_BLUE if selected else DARK_GRAY, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)
    
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH/2, y_position + button_height/2))
    screen.blit(text_surface, text_rect)
    
    return button_rect

def show_launch_menu():
    # Load and play menu music
    play_music('music/Shadows of the Abyss.mp3')
    
    # Load and scale background image
    background = load_image('background/start_menu.png', (WIDTH, HEIGHT))
    
    selected_option = 0
    menu_options = ["New Game", "Quit"]
    
    while True:
        # Draw background instead of filling with black
        screen.blit(background, (0, 0))
        
        # Add a semi-transparent overlay to make text more readable
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)  # 128 is half transparent
        screen.blit(overlay, (0, 0))
        
        draw_text_centered("Dungeons of Eldoria", 64, HEIGHT/4)
        
        button_rects = []
        for i, option in enumerate(menu_options):
            button_rect = draw_button(option, HEIGHT/2 + i*70, selected_option == i)
            button_rects.append(button_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    pygame.mixer.music.stop()
                    if selected_option == 0:
                        return "new_game"
                    else:
                        return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        pygame.mixer.music.stop()
                        if i == 0:
                            return "new_game"
                        else:
                            return "quit"

def show_game_over_menu():
    selected_option = 0
    menu_options = ["Restart", "Quit"]
    
    while True:
        screen.fill(BLACK)
        draw_text_centered("Game Over!", 64, HEIGHT/4)
        draw_text_centered(f"You reached level {player.level}", 48, HEIGHT/3)
        
        button_rects = []
        for i, option in enumerate(menu_options):
            button_rect = draw_button(option, HEIGHT/2 + i*70, selected_option == i)
            button_rects.append(button_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return "restart"
                    else:
                        return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        if i == 0:
                            return "restart"
                        else:
                            return "quit"

# Add new classes for combat
class CombatEnemy:
    def __init__(self, level):
        self.health = 30 + (level * 10)
        self.max_health = self.health
        self.attack = 5 + (level * 2)
        # Randomly choose enemy type and set corresponding sprite
        self.name = random.choice(['Goblin', 'Skeleton', 'Orc', 'Troll'])
        self.sprite = pygame.image.load(f'enemies/{self.name.lower()}.png')
        self.sprite = pygame.transform.scale(self.sprite, (COMBAT_SPRITE_SIZE, COMBAT_SPRITE_SIZE))  # Scale to desired size
        self.is_alive = True

# Add this new class after the Player class
class PartyMember(pygame.sprite.Sprite):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.mana = 100
        self.max_mana = 100
        self.defense_bonus = 1
        self.speed = 1.0  # Add speed attribute
        self.skills = []
        
        if role == 'Warrior':
            self.health = 120
            self.max_health = 120
            self.attack = 12
            self.color = RED
            self.skills = [
                Skill("Slash All", 8, 20, target_type='all'),
                Skill("Power Strike", 20, 15)
            ]
        elif role == 'Mage':
            self.health = 80
            self.max_health = 80
            self.attack = 15
            self.color = LIGHT_BLUE
            self.skills = [
                Skill("Fireball", 25, 20),
                Skill("Lightning Storm", 15, 30, target_type='all')
            ]
        elif role == 'Healer':
            self.health = 90
            self.max_health = 90
            self.attack = 8
            self.color = GREEN
            self.skills = [
                Skill("Heal", 30, 20, effect_type='heal'),
                Skill("Group Heal", 15, 35, target_type='all', effect_type='heal')
            ]
        self.is_alive = True
        self.name = role
        # Load combat sprite
        self.combat_sprite = pygame.image.load(f'characters/{role.lower()}.png')
        self.combat_sprite = pygame.transform.scale(self.combat_sprite, (COMBAT_SPRITE_SIZE, COMBAT_SPRITE_SIZE))

# Modify CombatSystem class
class CombatSystem:
    def __init__(self, player, party_members, dungeon_enemy):
        # Load and play battle music
        play_music('music/Eternal Quest.mp3')
        
        # Load sound effects
        self.sounds = {
            'attack': load_sound('sounds/Sword Slash (Rpg).wav'),
            'enemy_damaged': load_sound('sounds/Monster Growl 2.wav'),
            'character_damaged': load_sound('sounds/Rage up.wav'),
            'enemy_died': load_sound('sounds/Monster death (Rpg).wav'),
            'character_died': load_sound('sounds/Gladiator Buff.wav'),
            'defend': load_sound('sounds/Armor break.wav'),
            'skill': load_sound('sounds/Magical Sting 2.wav')
        }
        
        self.player = player
        self.party_members = party_members
        self.party = [player] + self.party_members
        self.enemy_count = random.randint(1, 4)
        self.enemies = [CombatEnemy(dungeon_enemy.level) for _ in range(self.enemy_count)]
        
        # Initialize turn tracking variables
        self.current_turn_index = 0
        self.selected_enemy = 0
        self.selected_action = 0
        self.selected_party_member = 0
        self.actions = ['Attack', 'Skills', 'Defend', 'Run']
        self.message = ''
        self.combat_over = False
        self.player_won = False
        
        # Load battle background
        try:
            self.background = load_image('background/battleground.png', (WIDTH, HEIGHT))
        except:
            # Create a fallback background if image loading fails
            self.background = pygame.Surface((WIDTH, HEIGHT))
            self.background.fill(BLACK)
        
        self.in_skills_menu = False
        self.selected_skill = 0
        self.selected_target = 0
        self.targeting_mode = False
        
        # Load blood splatter animation
        self.blood_frames = load_sprite_sheet('effects/blood - left 1.png', 16, 512, 512)
        self.current_frame = 0
        self.animation_speed = 2  # Frames to skip before showing next animation frame
        self.frame_counter = 0
        
        # Initialize combat after all variables are set
        self.combatants = []
        self.init_combat()

    def roll_initiative(self, combatant):
        # Base initiative on a d20 roll (1-20)
        base_roll = random.randint(1, 20)
        
        # Add modifiers based on character type
        if isinstance(combatant, Player):
            modifier = 2  # Player gets a small bonus
        elif isinstance(combatant, PartyMember):
            if combatant.role == 'Mage':
                modifier = 3  # Mages are quick
            elif combatant.role == 'Warrior':
                modifier = 1  # Warriors are average
            elif combatant.role == 'Healer':
                modifier = 2  # Healers are moderately quick
        else:  # Enemy
            modifier = 0  # Enemies get no bonus
            
        return base_roll + modifier

    def init_combat(self):
        # Create list of all combatants with their initiative rolls
        all_combatants = []
        
        # Add party members
        for member in self.party:
            all_combatants.append({
                'combatant': member,
                'initiative': self.roll_initiative(member),
                'is_enemy': False
            })
        
        # Add enemies
        for enemy in self.enemies:
            all_combatants.append({
                'combatant': enemy,
                'initiative': self.roll_initiative(enemy),
                'is_enemy': True
            })
        
        # Sort by initiative (highest first)
        all_combatants.sort(key=lambda x: x['initiative'], reverse=True)
        self.combatants = all_combatants
        
        # If first turn is enemy's, process it immediately
        if self.combatants[0]['is_enemy']:
            pygame.time.wait(1000)  # Give player time to see initiative order
            self.process_enemy_turn(self.combatants[0]['combatant'])

    def next_turn(self):
        # Reset defense bonus of current character before moving to next turn
        current_character = self.combatants[self.current_turn_index]['combatant']
        current_character.defense_bonus = 1
        
        self.current_turn_index = (self.current_turn_index + 1) % len(self.combatants)
        self.selected_action = 0
        self.selected_enemy = 0
        
        # Skip dead combatants
        while not self.combatants[self.current_turn_index]['combatant'].is_alive:
            self.current_turn_index = (self.current_turn_index + 1) % len(self.combatants)
        
        # Process enemy turn immediately if it's an enemy
        if self.combatants[self.current_turn_index]['is_enemy']:
            self.process_enemy_turn(self.combatants[self.current_turn_index]['combatant'])

    def process_enemy_turn(self, enemy):
        if enemy.is_alive:
            living_party = [member for member in self.party if member.is_alive]
            if not living_party:
                self.combat_over = True
                return
            
            target = random.choice(living_party)
            damage = enemy.attack // (target.defense_bonus if hasattr(target, 'defense_bonus') else 1)
            
            # Show enemy's intent to attack
            self.message = f'{enemy.name} is targeting {target.name}...'
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(1000)
            
            # Play attack sound
            self.play_sound('attack')
            self.message = f'{enemy.name} attacks {target.name}!'
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(250)  # Shorter wait before animation
            
            # Get target's sprite rect for animation
            target_rect = None
            for i, member in enumerate(self.party):
                if member == target:
                    member_x = WIDTH//4 + (i * 150)
                    member_y = HEIGHT*3//4
                    target_rect = member.combat_sprite.get_rect(center=(member_x, member_y))
                    break
            
            # Play hit animation
            if target_rect:
                self.play_hit_animation(target_rect)
            
            # Play damage sound and show damage message
            self.play_sound('character_damaged')
            target.health = max(0, target.health - damage)
            self.message = f'{enemy.name} deals {damage} damage to {target.name}!'
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(1000)
            
            if target.health <= 0:
                self.play_sound('character_died')
                target.is_alive = False
                self.message = f'{target.name} was defeated!'
                self.draw(screen)
                pygame.display.flip()
                pygame.time.wait(1000)
                
                if not any(member.is_alive for member in self.party):
                    self.combat_over = True
                    return
        
        self.next_turn()

    def handle_input(self, event):
        current_combatant = self.combatants[self.current_turn_index]
        if current_combatant['is_enemy'] or not current_combatant['combatant'].is_alive:
            return

        if event.type == pygame.KEYDOWN:
            if self.in_skills_menu:
                self.handle_skills_input(event)
            else:
                self.handle_main_menu_input(event)

    def handle_main_menu_input(self, event):
        if event.key == pygame.K_UP:
            if self.selected_action >= 0:
                self.selected_action = (self.selected_action - 1) % len(self.actions)
            else:
                self.selected_enemy = (self.selected_enemy - 1) % len([e for e in self.enemies if e.is_alive])
        elif event.key == pygame.K_DOWN:
            if self.selected_action >= 0:
                self.selected_action = (self.selected_action + 1) % len(self.actions)
            else:
                self.selected_enemy = (self.selected_enemy + 1) % len([e for e in self.enemies if e.is_alive])
        elif event.key == pygame.K_RETURN:
            if self.selected_action >= 0:
                self.execute_action()
            else:
                self.execute_attack()
        elif event.key == pygame.K_ESCAPE and self.selected_action < 0:
            self.selected_action = 0

    def handle_skills_input(self, event):
        current_character = self.combatants[self.current_turn_index]['combatant']
        selected_skill = current_character.skills[self.selected_skill]
        
        if self.targeting_mode:
            if event.key == pygame.K_UP:
                self.selected_enemy = (self.selected_enemy - 1) % len([e for e in self.enemies if e.is_alive])
            elif event.key == pygame.K_DOWN:
                self.selected_enemy = (self.selected_enemy + 1) % len([e for e in self.enemies if e.is_alive])
            elif event.key == pygame.K_RETURN:
                self.execute_skill()
            elif event.key == pygame.K_ESCAPE:
                self.targeting_mode = False
        else:
            if event.key == pygame.K_UP:
                self.selected_skill = (self.selected_skill - 1) % len(current_character.skills)
            elif event.key == pygame.K_DOWN:
                self.selected_skill = (self.selected_skill + 1) % len(current_character.skills)
            elif event.key == pygame.K_RETURN:
                if selected_skill.effect_type == 'damage' and selected_skill.target_type == 'single':
                    self.targeting_mode = True
                    self.selected_enemy = 0
                else:
                    self.execute_skill()
            elif event.key == pygame.K_ESCAPE:
                self.in_skills_menu = False
                self.selected_action = 1  # Return to 'Skills' option

    def execute_action(self):
        action = self.actions[self.selected_action]
        current_character = self.combatants[self.current_turn_index]['combatant']
        
        if action == 'Attack':
            self.selected_action = -1  # Switch to enemy selection mode
        elif action == 'Skills':
            self.in_skills_menu = True
            self.selected_skill = 0
        elif action == 'Defend':
            self.play_sound('defend')
            current_character.defense_bonus = 2
            self.message = f'{current_character.name} is defending!'
            self.next_turn()
        elif action == 'Run':
            run_chance = random.random()
            if run_chance > 0.5:
                self.combat_over = True
                self.message = 'Successfully fled!'
            else:
                self.message = 'Failed to run away!'
                self.next_turn()

    def execute_attack(self):
        current_character = self.combatants[self.current_turn_index]['combatant']
        alive_enemies = [e for e in self.enemies if e.is_alive]
        if self.selected_enemy < len(alive_enemies):
            target = alive_enemies[self.selected_enemy]
            
            # Play attack sound
            self.play_sound('attack')
            damage = current_character.attack
            self.draw(screen)
            pygame.display.flip()
            pygame.time.wait(250)  # Shorter wait before animation
            
            # Get target's sprite rect for animation
            enemy_x = WIDTH // 2 + (self.selected_enemy - len(alive_enemies)/2) * 150
            enemy_y = HEIGHT // 3
            target_rect = target.sprite.get_rect(center=(enemy_x, enemy_y))
            
            # Play hit animation
            self.play_hit_animation(target_rect)
            
            # Play enemy damaged sound and apply damage
            self.play_sound('enemy_damaged')
            target.health -= damage
            self.message = f'{current_character.name} deals {damage} damage!'
            
            # Check if enemy died
            if target.health <= 0:
                self.play_sound('enemy_died')
                target.is_alive = False
                self.message = f'{target.name} was defeated!'
            
            # Check if all enemies are defeated
            if not any(e.is_alive for e in self.enemies):
                self.combat_over = True
                self.player_won = True
                pygame.mixer.music.stop()  # Stop battle music when combat ends
                return
            
            self.next_turn()

    def execute_skill(self):
        current_character = self.combatants[self.current_turn_index]['combatant']
        selected_skill = current_character.skills[self.selected_skill]
        
        if current_character.mana < selected_skill.cost:
            self.message = "Not enough mana!"
            return

        # Play skill sound
        self.play_sound('skill')
        current_character.mana -= selected_skill.cost

        if selected_skill.effect_type == 'damage':
            if selected_skill.target_type == 'all':
                total_damage = 0
                alive_enemies = [e for e in self.enemies if e.is_alive]
                
                # Play skill sound first
                self.play_sound('skill')
                pygame.time.wait(250)  # Wait before animations
                
                # Animate and damage each enemy
                for i, enemy in enumerate(alive_enemies):
                    enemy_x = WIDTH // 2 + (i - len(alive_enemies)/2) * 150
                    enemy_y = HEIGHT // 3
                    target_rect = enemy.sprite.get_rect(center=(enemy_x, enemy_y))
                    
                    self.play_hit_animation(target_rect)
                    self.play_sound('enemy_damaged')
                    
                    enemy.health -= selected_skill.damage
                    total_damage += selected_skill.damage
                    if enemy.health <= 0:
                        self.play_sound('enemy_died')
                        enemy.is_alive = False
                
                self.message = f'{current_character.name} deals {total_damage} total damage!'
                
                if not any(e.is_alive for e in self.enemies):
                    self.combat_over = True
                    self.player_won = True
                    pygame.mixer.music.stop()
                    return
            else:
                alive_enemies = [e for e in self.enemies if e.is_alive]
                if self.selected_enemy < len(alive_enemies):
                    target = alive_enemies[self.selected_enemy]
                    self.play_sound('enemy_damaged')
                    target.health -= selected_skill.damage
                    self.message = f'{current_character.name} deals {selected_skill.damage} damage!'
                    if target.health <= 0:
                        self.play_sound('enemy_died')
                        target.is_alive = False
                        self.message = f'{target.name} was defeated!'
                    
                    if not any(e.is_alive for e in self.enemies):
                        self.combat_over = True
                        self.player_won = True
                        pygame.mixer.music.stop()
                        return

        elif selected_skill.effect_type == 'heal':
            if selected_skill.target_type == 'all':
                for member in self.party:
                    if member.is_alive:
                        member.health = min(member.max_health, member.health + selected_skill.damage)
                self.message = f'{current_character.name} heals the party!'
            else:
                target = self.party[self.selected_target]
                target.health = min(target.max_health, target.health + selected_skill.damage)
                self.message = f'{current_character.name} heals {target.name}!'

        self.in_skills_menu = False
        self.next_turn()

    def play_sound(self, sound_key):
        if sound_key in self.sounds and self.sounds[sound_key]:
            self.sounds[sound_key].play()
            pygame.time.wait(100)  # Small delay to ensure sound starts playing

    def draw(self, screen):
        # Draw battle background instead of solid color
        screen.blit(self.background, (0, 0))
        
        # Draw turn order on the left side
        turn_list_x = 20
        turn_list_y = 20
        turn_spacing = 30
        
        # Draw turn order background with some transparency
        turn_list_width = 200
        turn_list_height = len(self.combatants) * turn_spacing + 20
        turn_order_surface = pygame.Surface((turn_list_width, turn_list_height))
        turn_order_surface.fill(MENU_BG[:3])  # Use RGB values from MENU_BG
        turn_order_surface.set_alpha(200)  # Make it slightly transparent
        screen.blit(turn_order_surface, (turn_list_x, turn_list_y))
        pygame.draw.rect(screen, WHITE, (turn_list_x, turn_list_y, turn_list_width, turn_list_height), 2)
        
        # Draw each combatant in turn order
        font = pygame.font.Font(None, 28)
        for i, combatant_data in enumerate(self.combatants):
            combatant = combatant_data['combatant']
            if not combatant.is_alive:
                continue
            
            text_y = turn_list_y + 20 + (i * turn_spacing)
            
            # Highlight current turn
            if i == self.current_turn_index:
                pygame.draw.rect(screen, (100, 100, 100), 
                               (turn_list_x + 5, text_y - 15, turn_list_width - 10, turn_spacing),
                               border_radius=5)
                color = YELLOW
            else:
                color = WHITE
            
            # Show initiative roll next to name
            text = f"{combatant.name} ({combatant_data['initiative']})"
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(midleft=(turn_list_x + 20, text_y))
            screen.blit(text_surface, text_rect)
        
        # Draw enemies
        alive_enemies = [e for e in self.enemies if e.is_alive]
        for i, enemy in enumerate(alive_enemies):
            enemy_x = WIDTH // 2 + (i - len(alive_enemies)/2) * 150  # Increased spacing
            enemy_y = HEIGHT // 3
            
            # Draw enemy sprite
            sprite_rect = enemy.sprite.get_rect()
            sprite_rect.center = (enemy_x, enemy_y)
            screen.blit(enemy.sprite, sprite_rect)
            
            # Draw enemy health bar
            health_width = 100 * (enemy.health / enemy.max_health)  # Wider health bar
            pygame.draw.rect(screen, RED, (enemy_x-50, enemy_y-60, health_width, 8))  # Adjusted position and size
            
            # Draw selection indicator
            if self.selected_action == -1 and i == self.selected_enemy:
                pygame.draw.rect(screen, YELLOW, (sprite_rect.x-5, sprite_rect.y-5, 
                                                sprite_rect.width+10, sprite_rect.height+10), 2)

        # Draw party members
        for i, member in enumerate(self.party):
            if member.is_alive:
                member_x = WIDTH//4 + (i * 150)  # Increased spacing
                member_y = HEIGHT*3//4
                
                # Draw character sprite
                sprite_rect = member.combat_sprite.get_rect()
                sprite_rect.center = (member_x, member_y)
                screen.blit(member.combat_sprite, sprite_rect)
                
                # Draw health bar
                health_width = 100 * (member.health / member.max_health)
                pygame.draw.rect(screen, GREEN, (member_x-50, member_y+60, health_width, 8))
                
                # Draw active character indicator
                current_combatant = self.combatants[self.current_turn_index]['combatant']
                if current_combatant == member and not self.combatants[self.current_turn_index]['is_enemy']:
                    pygame.draw.rect(screen, YELLOW, (sprite_rect.x-5, sprite_rect.y-5, 
                                                    sprite_rect.width+10, sprite_rect.height+10), 2)

        # Draw mana bar for party members
        for i, member in enumerate(self.party):
            if member.is_alive:
                member_x = WIDTH//4 + (i * 150)
                member_y = HEIGHT*3//4
                
                # Draw mana bar below health bar
                mana_width = 100 * (member.mana / member.max_mana)
                pygame.draw.rect(screen, BLUE, (member_x-50, member_y+70, mana_width, 8))

        # Draw either the main action menu or the skills menu, but not both
        if self.selected_action >= 0 and not self.combatants[self.current_turn_index]['is_enemy']:
            menu_x = WIDTH - 220
            menu_y = 20
            
            if self.in_skills_menu:
                current_character = self.combatants[self.current_turn_index]['combatant']
                menu_width = 250
                menu_height = len(current_character.skills) * 30 + 20
                
                # Adjust menu_x to match left padding
                menu_x = WIDTH - menu_width - turn_list_x  # This ensures same padding as left side
                
                pygame.draw.rect(screen, MENU_BG, (menu_x, menu_y, menu_width, menu_height))
                pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
                
                for i, skill in enumerate(current_character.skills):
                    color = YELLOW if i == self.selected_skill else WHITE
                    if current_character.mana < skill.cost:
                        color = DARK_GRAY
                    
                    text_y = menu_y + 20 + i * 30
                    font = pygame.font.Font(None, 28)
                    text = f"{skill.name} ({skill.cost} MP)"
                    if self.targeting_mode and i == self.selected_skill:
                        text += " - Select Target"
                    text_surface = font.render(text, True, color)
                    text_rect = text_surface.get_rect(midleft=(menu_x + 20, text_y))
                    screen.blit(text_surface, text_rect)

                # Draw enemy selection indicator if in targeting mode
                if self.targeting_mode:
                    alive_enemies = [e for e in self.enemies if e.is_alive]
                    if self.selected_enemy < len(alive_enemies):
                        target = alive_enemies[self.selected_enemy]
                        pygame.draw.rect(screen, YELLOW, 
                                       target.sprite.get_rect(center=(
                                           WIDTH // 2 + (self.selected_enemy - len(alive_enemies)/2) * 150,
                                           HEIGHT // 3
                                       )), 2)
            else:
                # Draw main action menu
                menu_width = 200
                menu_height = len(self.actions) * 40 + 20
                menu_x = WIDTH - menu_width - turn_list_x  # Match padding for consistency
                
                pygame.draw.rect(screen, MENU_BG, (menu_x, menu_y, menu_width, menu_height))
                pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)
                
                for i, action in enumerate(self.actions):
                    color = YELLOW if i == self.selected_action else WHITE
                    text_y = menu_y + 20 + i * 40
                    font = pygame.font.Font(None, 36)
                    text_surface = font.render(action, True, color)
                    text_rect = text_surface.get_rect(midleft=(menu_x + 20, text_y))
                    screen.blit(text_surface, text_rect)

        # Draw message
        if self.message:
            draw_text_centered(self.message, 36, HEIGHT//2, WHITE)

    def play_hit_animation(self, target_rect):
        if not self.blood_frames:
            return
            
        # Calculate position to center blood splatter on target
        animation_size = (256, 256)  # Doubled from 128x128 to 256x256
        
        for frame in range(len(self.blood_frames)):
            # Scale current frame
            scaled_frame = pygame.transform.scale(self.blood_frames[frame], animation_size)
            
            # Position frame centered on target's center, but offset to the right
            # Start 50 pixels right and move left as animation progresses
            offset_x = 50 * (1 - frame / len(self.blood_frames))  # Gradually reduces from 50 to 0
            frame_x = target_rect.centerx - animation_size[0] // 2 + offset_x
            frame_y = target_rect.centery - animation_size[1] // 2
            
            # Draw current game state
            self.draw(screen)
            
            # Draw blood frame on top
            screen.blit(scaled_frame, (frame_x, frame_y))
            
            # Update display
            pygame.display.flip()
            
            # Control animation speed
            pygame.time.wait(60)  # 60ms delay between frames for slower animation

# Replace the main game loop with this structure
running = True
while running:
    # Show launch menu
    menu_choice = show_launch_menu()
    if menu_choice == "quit":
        running = False
        continue
    
    # Start new game
    generate_dungeon(1)
    player.health = player.max_health  # Reset health
    player.level = 1  # Reset level
    player.attack = 10  # Reset attack to initial value
    game_running = True
    
    # Game loop
    while game_running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                running = False
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1

                # Move the player
                player.move(dx, dy)

        # Move enemies towards the player
        for enemy in enemies:
            enemy.move_towards_player(player, walls)

        # Check for collisions with enemies
        enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
        if enemy_hits:
            combat = CombatSystem(player, party_members, enemy_hits[0])
            in_combat = True
            
            while in_combat and running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        in_combat = False
                    combat.handle_input(event)

                combat.draw(screen)
                pygame.display.flip()
                clock.tick(FRAME_RATE)

                if combat.combat_over:
                    in_combat = False
                    if player.health <= 0:
                        menu_choice = show_game_over_menu()
                        if menu_choice == "restart":
                            generate_dungeon(1)
                            player.health = player.max_health
                            player.level = 1
                            player.attack = 10
                            continue
                        else:
                            game_running = False
                            running = False
                            continue
                    else:
                        for enemy in enemy_hits:
                            enemy.kill()
                        # Restart dungeon music after combat
                        play_music('music/Shadows of the Abyss.mp3')

        # Check for collisions with items
        item_hits = pygame.sprite.spritecollide(player, items, True)
        for item in item_hits:
            if item.type == 'health_potion':
                player.health = min(player.max_health, player.health + 20)
            elif item.type == 'strength_potion':
                player.attack += 5
            elif item.type == 'speed_potion':
                player.speed += 0.2  # 20% speed boost

        # Check for collision with stairs
        if pygame.sprite.collide_rect(player, stairs):
            current_level = player.level  # Store current level
            player.level += 1  # Explicitly increment level
            print(f"Level up! Now at level {player.level}")  # Debug print
            player.health = player.max_health  # Heal player between levels
            generate_dungeon(player.level)  # Generate dungeon with new level

        # Draw everything
        screen.fill(BLACK)
        
        # Draw floor tiles using the pre-generated pattern
        for y in range(ROWS):
            for x in range(COLS):
                screen.blit(floor_pattern[y][x], (x * GRID_SIZE, y * GRID_SIZE))
        
        all_sprites.draw(screen)

        # Create fog of war effect
        fog_surface = pygame.Surface((WIDTH, HEIGHT))
        fog_surface.fill((0, 0, 0))  # Fill with black
        
        # Create a circle mask
        vision_radius = 5 * GRID_SIZE  # 10 grid points radius
        pygame.draw.circle(fog_surface, (255, 255, 255), 
                         (player.rect.centerx, player.rect.centery), 
                         vision_radius)
        
        # Use the circle as an alpha mask
        fog_surface.set_colorkey((255, 255, 255))
        fog_surface.set_alpha(255)  # Adjust visibility of fog (0-255)
        
        # Draw the fog
        screen.blit(fog_surface, (0, 0))

        pygame.display.flip()
        clock.tick(FRAME_RATE)

    # Cleanup
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass
    
    pygame.quit()
