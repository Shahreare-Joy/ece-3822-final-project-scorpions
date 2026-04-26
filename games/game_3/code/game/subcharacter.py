"""
character.py - Character classes with inventory

Lab 3 Update: Characters now have inventories using ArrayList!
"""
"""
Author: [Mykai Wade]
Date: [2/11/26]
"""

import pygame
from character import Character

class Demolisher(Character):
    """Heavy-duty construction machine"""
    def __init__(self, pos, groups, obstacle_sprites, is_local=True, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, is_local=is_local, player_id=player_id)
        self.image = pygame.image.load('../../graphics/characters/demolisher.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        self.character_name = "Demolisher"

        # Stats from Lab 2
        self.hp = 120
        self.max_hp = 120
        self.attack = 15
        self.defense = 20
        self.speed = 5

       # self.import_player_assets(animate=False)

    @staticmethod
    def get_display_name():
        return "Demolisher"

    @staticmethod
    def get_description():
        return "Heavy construction machine. High HP and defense, low speed."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/demolisher.png'


class Runner(Character):
    """High-speed delivery machine"""
    def __init__(self, pos, groups, obstacle_sprites, is_local=True, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, is_local=is_local, player_id=player_id)
        self.image = pygame.image.load('../../graphics/characters/runner.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        self.character_name = "Runner"

        # Stats from Lab 2
        self.hp = 80
        self.max_hp = 80
        self.attack = 5
        self.defense = 10
        self.speed = 25

      # self.import_player_assets(animate=False)

    @staticmethod
    def get_display_name():
        return "Runner"

    @staticmethod
    def get_description():
        return "High-speed delivery machine. Very fast but fragile."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/runner.png'


class Officer(Character):
    """Law enforcement machine"""
    def __init__(self, pos, groups, obstacle_sprites, is_local=True, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, is_local=is_local, player_id=player_id)
        self.image = pygame.image.load('../../graphics/characters/officer.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        self.character_name = "Officer"

        # Stats from Lab 2
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 15
        self.speed = 15

      # self.import_player_assets(animate=False)

    @staticmethod
    def get_display_name():
        return "Officer"

    @staticmethod
    def get_description():
        return "Law enforcement machine. Balanced stats with stun ability."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/officer.png'


class Gardener(Character):
    """Agricultural maintenance machine"""
    def __init__(self, pos, groups, obstacle_sprites, is_local=True, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, is_local=is_local, player_id=player_id)
        self.image = pygame.image.load('../../graphics/characters/gardener.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        self.character_name = "Gardener"

        # Stats from Lab 2
        self.hp = 110
        self.max_hp = 110
        self.attack = 15
        self.defense = 10
        self.speed = 15

      # self.import_player_assets(animate=False)

    @staticmethod
    def get_display_name():
        return "Gardener"

    @staticmethod
    def get_description():
        return "Agricultural machine with solar charging. Self-healing ability."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/gardener.png'


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character':
            character_classes.append(cls)
    return character_classes
