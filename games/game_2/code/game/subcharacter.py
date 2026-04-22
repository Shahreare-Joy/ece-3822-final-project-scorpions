"""
subcharacter.py - Character classes

Different character types that players can choose from
"""

import pygame
from character import Character

class Character1(Character):
    """Cleric - Healing specialist"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Cleric"
        self.hp, self.max_hp = 120, 120
        self.attack, self.defense = 8, 7
        
        # Load image for remote players or as fallback
        try:
            self.image = pygame.image.load('../../graphics/characters/cleric/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        # Load animations for local player
        if is_local:
            self.import_player_assets(animate=True)
    
    @staticmethod
    def get_display_name():
        return "Cleric"
    
    @staticmethod
    def get_description():
        return "Healing specialist with high HP"
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/cleric/down/frame_000.png'


class Character2(Character):
    """Hobbit - Sneaky and fast"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Hobbit"
        self.hp, self.max_hp = 80, 80
        self.attack, self.defense = 12, 4
        self.speed = 6  # Faster than others
        
        try:
            self.image = pygame.image.load('../../graphics/characters/hobbit/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        if is_local:
            self.import_player_assets(animate=True)
    
    @staticmethod
    def get_display_name():
        return "Hobbit"
    
    @staticmethod
    def get_description():
        return "Fast and sneaky"
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/hobbit/down/frame_000.png'


class Character3(Character):
    """Thief - High attack, low defense"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Thief"
        self.hp, self.max_hp = 90, 90
        self.attack, self.defense = 15, 3
        
        try:
            self.image = pygame.image.load('../../graphics/characters/thief/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        if is_local:
            self.import_player_assets(animate=True)
    
    @staticmethod
    def get_display_name():
        return "Thief"
    
    @staticmethod
    def get_description():
        return "Glass cannon - high attack"
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/thief/down/frame_000.png'


class Character4(Character):
    """Wizard - Magical powerhouse"""
    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)
        self.character_name = "Wizard"
        self.hp, self.max_hp = 100, 100
        self.attack, self.defense = 10, 5
        
        try:
            self.image = pygame.image.load('../../graphics/characters/wizard/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass
            
        if is_local:
            self.import_player_assets(animate=True)
    
    @staticmethod
    def get_display_name():
        return "Wizard"
    
    @staticmethod
    def get_description():
        return "Balanced mage with special abilities"
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/wizard/down/frame_000.png'


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character' and cls.__name__.startswith('Character'):
            character_classes.append(cls)
    return character_classes
