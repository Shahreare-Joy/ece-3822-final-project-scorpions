"""
subcharacter.py - Playable character classes for Game 4

Game 4 uses the newer Character base from character.py, which already provides
inventory, combat, animation, and multiplayer support. These subclasses only
define each archetype's stats plus the sprite assets they should load.
"""

from __future__ import annotations

import pygame
<<<<<<< HEAD
=======
from settings import *
from character import Character as BaseCharacter
>>>>>>> feature/chat-system

from character import Character
from sprite_loader import SpriteLoader


class Game4Character(Character):
    """Shared setup for Game 4's playable characters."""

<<<<<<< HEAD
    SPRITE_KEY = ""
    DISPLAY_NAME = "Unknown"
    DESCRIPTION = "A mysterious character."
    MAX_HP = 100
    ATTACK = 10
    DEFENSE = 5
    SPEED = 5

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)

        self.character_name = self.DISPLAY_NAME
        self.max_hp = self.MAX_HP
        self.hp = self.MAX_HP
        self.attack = self.ATTACK
        self.defense = self.DEFENSE
        self.speed = self.SPEED

        self._load_game4_assets()

    def _load_game4_assets(self):
        """Load the correct sprite set for this class and seed the first frame."""
        self.animations = SpriteLoader.load_character_sprites(self.SPRITE_KEY)

        for direction in ("up", "down", "left", "right"):
            frames = self.animations.get(direction) or []
            if not frames:
                fallback = pygame.Surface((64, 64))
                fallback.fill((255, 0, 255))
                frames = [fallback]
                self.animations[direction] = frames

            idle_key = f"{direction}_idle"
            if idle_key not in self.animations or not self.animations[idle_key]:
                self.animations[idle_key] = frames.copy()

        self.status = "down"
        self.image = self.animations["down"][0]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    @classmethod
    def get_display_name(cls):
        return cls.DISPLAY_NAME

    @classmethod
    def get_description(cls):
        return cls.DESCRIPTION

    @classmethod
    def get_preview_image(cls):
        return f"../../graphics/characters/{cls.SPRITE_KEY}.png"


class BambooVanguard(Game4Character):
    SPRITE_KEY = "bamboovanguard"
    DISPLAY_NAME = "Bamboo Vanguard"
    DESCRIPTION = "A sturdy vanguard with high defense and healing abilities."
    MAX_HP = 70
    ATTACK = 50
    DEFENSE = 100
    SPEED = 50
=======
class BambooVanguard(BaseCharacter):
    def __init__(self, pos, groups, obstacle_sprites, name="Player", is_local=False, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id or name, is_local=is_local)
        self.is_local = is_local
        self.player_name = name or str(player_id or "Player")
        self.name = self.player_name

        self.character_name = "Bamboo Vanguard"
        self.sprite_name = "bamboovanguard"
        self.hp = 70 
        self.max_hp = 70
        self.attack = 50
        self.defense = 100
        self.speed = 5
        self.import_player_assets()
>>>>>>> feature/chat-system

    def special_ability(self):
        self.heal(self.max_hp // 10)

<<<<<<< HEAD

class SilkbladeDuelist(Game4Character):
    SPRITE_KEY = "silkbladeduelist"
    DISPLAY_NAME = "Silkblade Duelist"
    DESCRIPTION = "A swift and agile duelist with high attack power."
    MAX_HP = 70
    ATTACK = 100
    DEFENSE = 40
    SPEED = 80

    def special_ability(self):
        self.dodge_chance = 1.0


class Monk(Game4Character):
    SPRITE_KEY = "monk"
    DISPLAY_NAME = "Monk"
    DESCRIPTION = "A monk who meditates and gains spiritual insight."
    MAX_HP = 100
    ATTACK = 50
    DEFENSE = 75
    SPEED = 40

    def special_ability(self):
        self.defense += 10
=======
    @staticmethod
    def get_display_name():
        return "Bamboo Vanguard"
         
    @staticmethod
    def get_description():
        return "A sturdy vanguard with high defense and healing abilities."
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/bamboovanguard.png'


class SilkbladeDuelist(BaseCharacter):
    def __init__(self, pos, groups, obstacle_sprites, name="Player", is_local=False, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id or name, is_local=is_local)
        self.is_local = is_local
        self.player_name = name or str(player_id or "Player")
        self.name = self.player_name

        self.character_name = "Silkblade Duelist"
        self.sprite_name = "silkbladeduelist"
        self.hp = 70    
        self.max_hp = 70
        self.attack = 100
        self.defense = 40
        self.speed = 7
        self.import_player_assets()

    def special_ability(self):
        self.dodge_chance = 1.0  

    @staticmethod
    def get_display_name():
        return "Silkblade Duelist"

    @staticmethod
    def get_description():
        return "A swift and agile duelist with high attack power."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/silkbladeduelist.png'


class Monk(BaseCharacter):
    def __init__(self, pos, groups, obstacle_sprites, name="Player", is_local=False, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id or name, is_local=is_local)
        self.is_local = is_local
        self.player_name = name or str(player_id or "Player")
        self.name = self.player_name

        self.character_name = "Monk"
        self.sprite_name = "monk"
        self.hp = 100    
        self.max_hp = 100
        self.attack = 50
        self.defense = 75
        self.speed = 4
        self.import_player_assets()

    def special_ability(self):
        self.defense += 10

    @staticmethod
    def get_display_name():
        return "Monk"
    
    @staticmethod
    def get_description():
        return "A monk who meditates and gains spiritual insight."
    
    @staticmethod
    def get_preview_image():
        return  '../../graphics/characters/monk.png'
    

class WanderingTraveler(BaseCharacter):
    def __init__(self, pos, groups, obstacle_sprites, name="Player", is_local=False, player_id=None):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id or name, is_local=is_local)
        self.is_local = is_local
        self.player_name = name or str(player_id or "Player")
        self.name = self.player_name

        self.character_name = "Wandering Traveler"
        self.sprite_name = "wanderingtraveler"
        self.hp = 70
        self.max_hp = 70
        self.attack = 70
        self.defense = 70
        self.speed = 6
        self.import_player_assets()

    def special_ability(self):
        self.all_stats_boost = True 
    
    @staticmethod
    def get_display_name():
        return "Wandering Traveler"
    
    @staticmethod
    def get_description():
        return "A wandering traveler with balanced stats and a mysterious past."
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/wanderingtraveler.png'


# ============================================
# CHARACTER REGISTRY (Auto-discovery)
# ============================================

def get_all_character_classes():
    """Return list of all character classes"""
    return [BambooVanguard, SilkbladeDuelist, Monk, WanderingTraveler]
>>>>>>> feature/chat-system
