"""
character.py - Character classes for the game

Students create 4 unique character classes, each with:
- Different stats (hp, attack, defense, speed)
- Unique special ability
- Character sprite image

Author: Kevin Le
Date: 1/23/2026
Lab: Lab 2 - Character Classes
"""

import pygame
from settings import *
from character import Character as BaseCharacter

class Character(pygame.sprite.Sprite):
    """Base Character class - all characters inherit from this"""
    
    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)

        # Stats (override in subclasses)
        self.character_name = "Unknown"
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.speed = 5

        # Sanitize inputs
        self.__sanitize_inputs()
        
        # DO NOT EDIT
        self.image = pygame.Surface((64, 64))
        self.image.fill((255, 0, 255))  # Magenta placeholder
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        # Movement
        self.direction = pygame.math.Vector2()
        self.obstacle_sprites = obstacle_sprites
        
    def input(self):
        """Handle player input"""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0
    
    def move(self, speed):
        """Move the character"""
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center
    
    def collision(self, direction):
        """Handle collision with obstacles"""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom
    
    def update(self):
        """Update character each frame"""
        self.input()
        self.move(self.speed)

    def take_damage(self, amount):
        """Reduce HP when taking damage, accounting for defense"""
        actually_damage = max(amount - self.defense, 0)
        self.hp -= actually_damage
        if self.hp < 0:
            self.hp = 0
        return actually_damage

    def heal(self, amount):
        """Increase HP when healing"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        """Check if character is alive"""
        return self.hp > 0  

    def _validate_stats(self):
        """Ensure stats are within valid ranges"""
        self.hp = max(0, min(self.hp, self.max_hp))
        self.attack = max(0, self.attack)
        self.defense = max(0, self.defense)
        self.speed = max(1, self.speed)  

    def __sanitize_inputs(self):
        """Sanitize input values for stats"""
        self._validate_stats()
        
    def special_ability(self):
        """Special ability - override in subclasses"""
        pass
    
    @staticmethod
    def get_display_name():
        """Return character name for display"""
        return "Unknown"
    
    @staticmethod
    def get_description():
        """Return character description"""
        return "A mysterious character"
    
    @staticmethod
    def get_preview_image():
        """Return path to character preview image"""
        return '../graphics/test/player.png'


# ============================================
# IMPLEMENTED CHARACTER CLASSES 
# ============================================

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

    def special_ability(self):
        self.heal(self.max_hp // 10)

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
