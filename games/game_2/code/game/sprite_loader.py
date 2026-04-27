"""
sprite_loader.py - Unified sprite loading system for characters and enemies

Handles two sprite organization patterns:
1. Animated: graphics/characters/wizard/down/0.png, down/1.png, etc.
2. Static: graphics/characters/wizard.png (single image for all directions)

Author: [System - Lab 5]
Date: [Date]
"""

import pygame
import os

# Resolve graphics directory relative to this file, not the working directory
_GAME_DIR = os.path.dirname(os.path.abspath(__file__))
_GRAPHICS_DIR = os.path.join(_GAME_DIR, '..', '..', 'graphics')

class SpriteLoader:
    """Handles sprite loading for both characters and enemies with flexible organization."""

    CHARACTER_FRAME_SIZE = (96, 96)
    ENEMY_FRAME_SIZE = (80, 80)
    PREVIEW_SIZE = (128, 128)
    
    @staticmethod
    def load_character_sprites(character_name, base_path=None):
        if base_path is None:
            base_path = os.path.join(_GRAPHICS_DIR, 'characters')
        """
        Load sprites for a character.
        
        Args:
            character_name (str): Name of character (e.g., "wizard", "cleric")
            base_path (str): Base directory for character graphics
            
        Returns:
            dict: Animation dictionary with status keys and frame lists
        """
        return SpriteLoader._load_sprites(
            character_name,
            base_path,
            is_character=True,
            target_size=SpriteLoader.CHARACTER_FRAME_SIZE
        )
    
    @staticmethod
    def load_enemy_sprites(enemy_name, base_path=None):
        if base_path is None:
            base_path = os.path.join(_GRAPHICS_DIR, 'enemies')
        """
        Load sprites for an enemy.

        Args:
            enemy_name (str): Name of enemy (e.g., "forest_guard", "wandering_goblin")
            base_path (str): Base directory for enemy graphics

        Returns:
            dict: Animation dictionary with status keys and frame lists
        """
        return SpriteLoader._load_sprites(
            enemy_name,
            base_path,
            is_character=False,
            target_size=SpriteLoader.ENEMY_FRAME_SIZE
        )

    @staticmethod
    def load_npc_sprites(enemy_name, base_path=None):
        """Deprecated: use load_enemy_sprites instead."""
        if base_path is None:
            base_path = os.path.join(_GRAPHICS_DIR, 'enemies')
        return SpriteLoader._load_sprites(
            enemy_name,
            base_path,
            is_character=False,
            target_size=SpriteLoader.ENEMY_FRAME_SIZE
        )

    @staticmethod
    def load_preview_image(image_path, target_size=None):
        """Load and normalize a preview image for menus."""
        if target_size is None:
            target_size = SpriteLoader.PREVIEW_SIZE

        image = pygame.image.load(image_path).convert_alpha()
        return SpriteLoader._normalize_surface(image, target_size)

    @staticmethod
    def _load_sprites(name, base_path, is_character=True, target_size=None):
        """
        Internal method to load sprites with flexible organization.
        
        Args:
            name (str): Character/enemy name
            base_path (str): Base graphics directory
            is_character (bool): True for characters, False for enemies
            target_size (tuple[int, int]): Final normalized frame size
            
        Returns:
            dict: {status: [pygame.Surface, ...], ...}
        """
        name_lower = name.lower()
        animations = {}
        
        # Define all possible statuses
        statuses = ['up', 'down', 'left', 'right', 'up_idle', 'down_idle', 'left_idle', 'right_idle']
        
        # Check for animated sprites (subdirectory structure)
        character_dir = os.path.join(base_path, name_lower)
        
        print(f"  Checking for animated sprites at: {character_dir}")
        print(f"  Directory exists: {os.path.exists(character_dir)}")
        
        if os.path.exists(character_dir) and os.path.isdir(character_dir):
            # Animated sprites - load from subdirectories
            print(f"  Loading animated sprites for {name} from {character_dir}")
            animations = SpriteLoader._load_animated_sprites(character_dir, statuses, target_size)
            
            # Check if we actually loaded any frames
            total_frames = sum(len(frames) for frames in animations.values() if frames)
            print(f"  Total frames loaded: {total_frames}")
            
        else:
            # Static sprite - single image file
            static_path = os.path.join(base_path, f"{name_lower}.png")
            print(f"  Checking for static sprite at: {static_path}")
            print(f"  File exists: {os.path.exists(static_path)}")
            
            if os.path.exists(static_path):
                print(f"  Loading static sprite for {name} from {static_path}")
                animations = SpriteLoader._load_static_sprite(static_path, statuses, target_size)
            else:
                # No sprites found - create defaults
                print(f"  No sprites found for {name}, using default colored rectangles")
                animations = SpriteLoader._create_default_sprites(name, statuses, is_character)
        
        return animations
    
    @staticmethod
    def _load_animated_sprites(character_dir, statuses, target_size):
        """Load animated sprites from subdirectory structure."""
        animations = {}
        
        for status in statuses:
            animations[status] = []
            
            # Determine which directory to look in
            # idle statuses use the same sprites as movement statuses
            if '_idle' in status:
                direction = status.replace('_idle', '')  # 'up_idle' -> 'up'
            else:
                direction = status  # 'up' -> 'up'
            
            sprite_dir = os.path.join(character_dir, direction)
            
            if os.path.exists(sprite_dir) and os.path.isdir(sprite_dir):
                try:
                    # Get all PNG files and sort alphabetically
                    all_files = os.listdir(sprite_dir)
                    png_files = [f for f in all_files if f.lower().endswith('.png')]
                    png_files.sort()  # Simple alphabetical sort
                    
                    print(f"    Loading {direction}: found {len(png_files)} PNG files")
                    
                    # Load all PNG files
                    for png_file in png_files:
                        try:
                            image_path = os.path.join(sprite_dir, png_file)
                            image = pygame.image.load(image_path).convert_alpha()
                            image = SpriteLoader._normalize_surface(image, target_size)
                            animations[status].append(image)
                        except pygame.error as e:
                            print(f"      Error loading {image_path}: {e}")
                            
                except Exception as e:
                    print(f"    Error reading directory {sprite_dir}: {e}")
            
            # If no frames loaded, create a default
            if not animations[status]:
                default_sprite = SpriteLoader._create_single_default_sprite(direction)
                animations[status] = [default_sprite]
        
        return animations
    
    @staticmethod
    def _load_static_sprite(image_path, statuses, target_size):
        """Load single static sprite for all statuses."""
        animations = {}

        try:
            static_image = pygame.image.load(image_path).convert_alpha()
            static_image = SpriteLoader._normalize_surface(static_image, target_size)
            
            # Use the same image for all statuses
            for status in statuses:
                animations[status] = [static_image.copy()]
                
        except pygame.error as e:
            print(f"Error loading static sprite {image_path}: {e}")
            # Create defaults if loading fails
            for status in statuses:
                default_sprite = SpriteLoader._create_single_default_sprite('down')
                animations[status] = [default_sprite]
        
        return animations
    
    @staticmethod
    def _create_default_sprites(name, statuses, is_character=True):
        """Create default colored rectangle sprites."""
        animations = {}
        
        # Different default colors for characters vs enemies
        if is_character:
            # Character default colors (based on common RPG classes)
            colors = {
                'wizard': (100, 100, 200),
                'cleric': (200, 200, 100),
                'warrior': (200, 100, 100),
                'rogue': (100, 200, 100),
                'paladin': (200, 150, 100),
                'archer': (150, 200, 150),
            }
            default_color = colors.get(name.lower(), (150, 150, 150))
        else:
            # Enemy default colors
            colors = {
                'forest_guard': (0, 100, 0),
                'village_merchant': (100, 100, 200),
                'temple_priest': (200, 200, 200),
                'dungeon_scout': (150, 0, 0),
                'market_vendor': (200, 150, 0),
                'wandering_goblin': (80, 140, 60),
            }
            default_color = colors.get(name.lower(), (100, 100, 100))
        
        for status in statuses:
            direction = status.replace('_idle', '') if '_idle' in status else status
            sprite = SpriteLoader._create_single_default_sprite(direction, default_color)
            animations[status] = [sprite]
        
        return animations
    
    @staticmethod
    def _create_single_default_sprite(direction, color=(100, 100, 100)):
        """Create a single default sprite with directional indicator."""
        sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        sprite.fill(color)
        
        # Add directional arrow
        if direction == 'up':
            pygame.draw.polygon(sprite, (255, 255, 255), [(16, 5), (10, 15), (22, 15)])
        elif direction == 'down':
            pygame.draw.polygon(sprite, (255, 255, 255), [(16, 27), (10, 17), (22, 17)])
        elif direction == 'left':
            pygame.draw.polygon(sprite, (255, 255, 255), [(5, 16), (15, 10), (15, 22)])
        elif direction == 'right':
            pygame.draw.polygon(sprite, (255, 255, 255), [(27, 16), (17, 10), (17, 22)])
        
        # Add border
        pygame.draw.rect(sprite, (255, 255, 255), sprite.get_rect(), 2)

        return sprite

    @staticmethod
    def _normalize_surface(surface, target_size):
        """Crop transparent borders and fit the sprite into a consistent canvas."""
        if target_size is None:
            return surface

        bounds = surface.get_bounding_rect(min_alpha=1)
        if bounds.width == 0 or bounds.height == 0:
            trimmed = surface.copy()
        else:
            trimmed = surface.subsurface(bounds).copy()

        max_width, max_height = target_size
        scale = min(max_width / trimmed.get_width(), max_height / trimmed.get_height())
        scaled_size = (
            max(1, int(trimmed.get_width() * scale)),
            max(1, int(trimmed.get_height() * scale))
        )
        scaled = pygame.transform.scale(trimmed, scaled_size)

        canvas = pygame.Surface(target_size, pygame.SRCALPHA)
        dest = scaled.get_rect(center=(target_size[0] // 2, target_size[1] // 2))
        canvas.blit(scaled, dest)
        return canvas
    
    @staticmethod
    def _extract_number(filename):
        """Extract number from filename for sorting (0.png -> 0, 1.png -> 1, etc.)."""
        try:
            # Remove extension and convert to int
            return int(os.path.splitext(filename)[0])
        except ValueError:
            # If filename doesn't start with number, sort alphabetically
            return float('inf')
    
    @staticmethod
    def get_sprite_info(name, base_path):
        """Get information about available sprites for debugging."""
        name_lower = name.lower()
        character_dir = os.path.join(base_path, name_lower)
        static_path = os.path.join(base_path, f"{name_lower}.png")
        
        info = {
            'name': name,
            'type': 'none',
            'directories': [],
            'files': []
        }
        
        if os.path.exists(character_dir) and os.path.isdir(character_dir):
            info['type'] = 'animated'
            for item in os.listdir(character_dir):
                item_path = os.path.join(character_dir, item)
                if os.path.isdir(item_path):
                    png_count = len([f for f in os.listdir(item_path) if f.lower().endswith('.png')])
                    info['directories'].append(f"{item} ({png_count} frames)")
        elif os.path.exists(static_path):
            info['type'] = 'static'
            info['files'].append(f"{name_lower}.png")
        else:
            info['type'] = 'default'
        
        return info
