# Dungeons of Eldoria

A classic turn-based dungeon crawler RPG built with Pygame, featuring procedurally generated dungeons, tactical combat, and character progression.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Game Features](#game-features)
- [Game Systems](#game-systems)
- [Technical Implementation](#technical-implementation)
- [Assets](#assets)
- [Controls](#controls)
- [Development](#development)

## Overview

Dungeons of Eldoria is a grid-based dungeon crawler with turn-based combat. Lead your party of adventurers through increasingly difficult dungeon levels, battle monsters, collect items, and find the stairs to the next level. The game features procedurally generated dungeons, ensuring each playthrough offers a unique experience.

## Installation

### Requirements
- Python 3.6 or higher
- Pygame library

### Setup
1. Clone this repository
2. Install the required dependencies:
   ```
   pip install pygame
   ```
3. Run the game:
   ```
   python dungeon-crawler-game.py
   ```

## How to Play

1. **Start a New Game**: From the main menu, select "New Game" to begin your adventure.
2. **Exploration**: Navigate through the dungeon using the arrow keys. Explore rooms, avoid or engage enemies, and collect items.
3. **Combat**: When you collide with an enemy, combat begins. Take turns attacking, using skills, defending, or attempting to flee.
4. **Level Progression**: Find the stairs to descend to the next level. Each level becomes progressively more difficult.
5. **Game Over**: If your player character dies, the game ends. You can choose to restart or quit.

## Game Features

### Procedural Dungeon Generation
- Unique dungeon layout for each level and playthrough
- Intelligently connected rooms with corridors using A* pathfinding
- Increasing difficulty with deeper levels

### Party System
- Lead a party of 4 characters (Player + 3 companions)
- Each character has unique abilities:
  - **Player**: Balanced stats with basic attack and skills
  - **Warrior**: High health and physical damage
  - **Mage**: Powerful AOE (area of effect) spells
  - **Healer**: Healing abilities for party members

### Combat System
- Turn-based combat with initiative order
- Multiple action options:
  - **Attack**: Basic attack against a single enemy
  - **Skills**: Special abilities that cost mana
  - **Defend**: Reduce incoming damage
  - **Run**: Attempt to flee combat
- Visual combat feedback with animations and sound effects
- Health and mana management

### Items and Progression
- Collect potions and items throughout the dungeon
- Health potions, strength potions, and speed potions
- Character leveling increases stats and combat effectiveness

### Immersive Visuals and Audio
- Character sprite animations for movement
- Dynamic battle effects with animated blood splatter
- Background music for exploration and combat
- Sound effects for all actions

### Fog of War
- Limited visibility radius around the player
- Encourages exploration and adds tension to gameplay

## Game Systems

### Combat Mechanics
- **Initiative System**: Turn order is determined by initiative rolls
- **Targeting System**: Select enemies to attack or use skills on
- **Damage Calculation**: Accounts for attack power and defense bonuses
- **AOE Effects**: Some skills affect all enemies
- **Healing**: Restore health to party members

### Character Classes
- **Player**: Balanced stats, versatile skills
- **Warrior**: High health (120), moderate attack (12), physical area damage
- **Mage**: Low health (80), high attack (15), powerful magic damage
- **Healer**: Medium health (90), low attack (8), healing abilities

### Enemy System
- Multiple enemy types (Goblin, Skeleton, Orc, Troll)
- Enemies scale in difficulty with dungeon level
- Enemies follow and pursue the player when in line of sight

### Level Progression
- Increasing enemy count and strength with each level
- Health is restored between levels
- Mana is partially regenerated between levels

## Technical Implementation

### Core Technologies
- **Pygame**: Game framework for rendering and input handling
- **Python**: Core game logic and systems

### Key Components
- **Grid-Based Movement**: Characters move along a discrete grid
- **A* Pathfinding**: Used for dungeon generation and enemy movement
- **Sprite Animation**: Direction-based character animations
- **Collision Detection**: Prevents moving through walls and handles combat initiation
- **Audio Management**: Background music and sound effects with volume control
- **Menu System**: Start screen and game over screen
- **Combat UI**: Initiative display, action selection, and targeting

## Assets

### Graphics
- Character sprites with directional animations
- Enemy sprites
- Dungeon tileset (floors and walls)
- Combat effects (blood splatter animation)
- UI elements

### Audio
- Background music for menus, exploration, and combat
- Sound effects:
  - Attacks
  - Taking damage
  - Enemy death
  - Character death
  - Skills
  - Defense

## Controls

### Exploration Mode
- **Arrow Keys**: Move the player character
- **Esc**: Quit game

### Combat Mode
- **Up/Down Arrows**: Navigate menu options or targets
- **Enter/Return**: Select action or confirm
- **Esc**: Back/Cancel (in submenus)

## Development

This project was developed using Python and Pygame to create a classic RPG experience. The code is organized to separate core game systems:
- Dungeon generation
- Character and enemy mechanics
- Combat system
- UI rendering
- Audio management

Future enhancements could include:
- Additional character classes
- More enemy types
- Equipment system
- Save/load functionality
- Boss encounters
- Quest system

---

Enjoy your adventure in the Dungeons of Eldoria! 
