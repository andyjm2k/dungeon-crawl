import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# Grid settings
GRID_SIZE = 20
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fantasy Dungeon Crawler")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([GRID_SIZE-2, GRID_SIZE-2])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE + 1
        self.rect.y = y * GRID_SIZE + 1
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.level = 1

    def move(self, dx, dy):
        self.rect.x += dx * GRID_SIZE
        self.rect.y += dy * GRID_SIZE

# Updated Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__()
        self.image = pygame.Surface([GRID_SIZE - 2, GRID_SIZE - 2])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE + 1
        self.rect.y = y * GRID_SIZE + 1
        self.health = 30 + (level * 10)
        self.attack = 5 + (level * 2)
        self.speed = 0.5  # Reduced movement speed
        self.vision_range = 5 * GRID_SIZE  # How far the enemy can "see"
        self.move_cooldown = 0
        self.move_delay = 60  # Frames to wait before moving again

    def move_towards_player(self, player, walls):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # Calculate direction vector
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        dist = math.hypot(dx, dy)

        if dist <= self.vision_range:
            # Normalize direction
            if dist != 0:
                dx, dy = dx / dist, dy / dist

            # Move enemy
            new_x = self.rect.x + dx * self.speed * GRID_SIZE
            new_y = self.rect.y + dy * self.speed * GRID_SIZE

            # Check for collisions with walls
            temp_rect = self.rect.copy()
            temp_rect.x = new_x
            temp_rect.y = new_y

            if not pygame.sprite.spritecollide(self, walls, False, pygame.sprite.collide_rect_ratio(0.8)):
                self.rect.x = new_x
                self.rect.y = new_y
                self.move_cooldown = self.move_delay

# Item class
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.image = pygame.Surface([GRID_SIZE-2, GRID_SIZE-2])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE + 1
        self.rect.y = y * GRID_SIZE + 1
        self.type = item_type

# Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([GRID_SIZE, GRID_SIZE])
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE

# Stairs class
class Stairs(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([GRID_SIZE-2, GRID_SIZE-2])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE + 1
        self.rect.y = y * GRID_SIZE + 1

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
items = pygame.sprite.Group()
walls = pygame.sprite.Group()

# Create player and stairs
player = None
stairs = None

# Dungeon generation
def generate_dungeon(level):
    global player, stairs
    all_sprites.empty()
    enemies.empty()
    items.empty()
    walls.empty()

    # Create grid
    grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]

    # Create rooms
    rooms = []
    for _ in range(7 + level):  # Increase number of rooms based on level
        room_width = random.randint(5, 8)
        room_height = random.randint(5, 8)
        x = random.randint(1, COLS - room_width - 1)
        y = random.randint(1, ROWS - room_height - 1)

        # Check for overlap with existing rooms
        overlaps = any(
            x < r[0] + r[2] and x + room_width > r[0] and
            y < r[1] + r[3] and y + room_height > r[1]
            for r in rooms
        )

        if not overlaps:
            # Carve out room
            for i in range(y, y + room_height):
                for j in range(x, x + room_width):
                    grid[i][j] = 0

            rooms.append((x, y, room_width, room_height))

    # Connect rooms
    for i in range(len(rooms) - 1):
        start_x, start_y = rooms[i][0] + rooms[i][2] // 2, rooms[i][1] + rooms[i][3] // 2
        end_x, end_y = rooms[i+1][0] + rooms[i+1][2] // 2, rooms[i+1][1] + rooms[i+1][3] // 2

        # Create L-shaped corridors
        if random.choice([True, False]):
            # Horizontal then vertical
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                grid[start_y][x] = 0
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                grid[y][end_x] = 0
        else:
            # Vertical then horizontal
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                grid[y][start_x] = 0
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                grid[end_y][x] = 0

    # Add some random corridors
    for _ in range(3 + level):
        x1, y1 = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        x2, y2 = random.randint(1, COLS-2), random.randint(1, ROWS-2)
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y1][x] = 0
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x2] = 0

    # Create wall sprites
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == 1:
                wall = Wall(x, y)
                walls.add(wall)
                all_sprites.add(wall)

    # Place player in first room
    player_x, player_y = rooms[0][0] + 1, rooms[0][1] + 1
    player = Player(player_x, player_y)
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

# Game loop
running = True
clock = pygame.time.Clock()
FRAME_RATE = 120  # Reduced frame rate

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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

            # Store the player's current position
            old_x, old_y = player.rect.x, player.rect.y

            # Move the player
            player.move(dx, dy)

            # Check for collisions with walls
            wall_hits = pygame.sprite.spritecollide(player, walls, False)
            if wall_hits:
                # If there's a collision, move the player back
                player.rect.x, player.rect.y = old_x, old_y

    # Move enemies towards the player
    for enemy in enemies:
        enemy.move_towards_player(player, walls)

    # Check for collisions with enemies
    enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
    for enemy in enemy_hits:
        player.health -= enemy.attack
        enemy.health -= player.attack
        if enemy.health <= 0:
            enemy.kill()
        if player.health <= 0:
            running = False  # Game over

    # Check for collisions with items
    item_hits = pygame.sprite.spritecollide(player, items, True)
    for item in item_hits:
        if item.type == 'health_potion':
            player.health = min(player.max_health, player.health + 20)
        elif item.type == 'strength_potion':
            player.attack += 5

    # Check for collision with stairs
    if pygame.sprite.collide_rect(player, stairs):
        player.level += 1
        player.health = player.max_health  # Heal player between levels
        generate_dungeon(player.level)

    # Draw everything
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw player stats
    font = pygame.font.Font(None, 36)
    health_text = font.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
    screen.blit(health_text, (10, 10))
    attack_text = font.render(f"Attack: {player.attack}", True, WHITE)
    screen.blit(attack_text, (10, 50))
    level_text = font.render(f"Level: {player.level}", True, WHITE)
    screen.blit(level_text, (10, 90))

    pygame.display.flip()
    clock.tick(FRAME_RATE)

pygame.quit()
