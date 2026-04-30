"""
subcharacter.py - Playable character classes for Game 4

Game 4 uses the newer Character base from character.py, which already provides
inventory, combat, animation, and multiplayer support. These subclasses only
define each archetype's stats plus the sprite assets they should load.
"""

from __future__ import annotations

import pygame

from character import Character
from sprite_loader import SpriteLoader


class Game4Character(Character):
    """Shared setup for Game 4's playable characters."""

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

    def special_ability(self):
        self.heal(self.max_hp // 10)


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