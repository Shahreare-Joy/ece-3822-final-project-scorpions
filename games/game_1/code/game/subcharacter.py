"""
subcharacter.py - Character classes

Different character types that players can choose from
"""

import pygame
from character import Character

class Sprinter(Character):
    """Skybound Sprinter - fast, evasive character."""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)
        
        # TODO: Set character image
        self.image = pygame.image.load('../../graphics/characters/sprinter.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (55, 55))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        # TODO: Set stats
        self.character_name = "Skybound Sprinter"
        self.max_hp = 100
        self.hp = 80
        self.attack = 10
        self.defense = 5
        self.speed = 15

        #self._Character__validate_stats()
        self._dash_cooldown = 0  # Cooldown timer for special ability
    
    def special_ability(self):
        """Wind Dash: dash a short distance with cooldown."""
        if self._dash_cooldown > 0:
            return False

        dash_distance = 30
        dash_dir = self.direction.normalize() if self.direction.magnitude() != 0 else pygame.math.Vector2(1, 0)

        self.hitbox.x += int(dash_dir.x * dash_distance)
        self.hitbox.y += int(dash_dir.y * dash_distance)
        self.rect.center = self.hitbox.center

        self._dash_cooldown = 60  # 1 second cooldown at 60 FPS
        return True

    def update(self):
        super().update()
        if self._dash_cooldown > 0:
            self._dash_cooldown -= 1
    
    @staticmethod
    def get_display_name():
        return "Skybound Sprinter"
    
    @staticmethod
    def get_description():
        return "A swift character excelling in speed and evasion."
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/sprinter.png'


class Bruiser(Character):
    """ Ironclad Bruiser - tanky, high-defense character."""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)
        
        self.image = pygame.image.load('../../graphics/characters/bruiser.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (55, 55))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        self.character_name = "Ironclad Bruiser"
        self.max_hp = 100
        self.hp = 90
        self.attack = 15
        self.defense = 20
        self.speed = 5

        #self._Character__validate_stats()

        self._push_strength = 15  # Amount to push enemies back


    def special_ability(self):
        """Shield Bash: temporarily increase defense and push back enemies."""
        return self._push_strength
    
    @staticmethod
    def get_display_name():
        return "Ironclad Bruiser"
    
    @staticmethod
    def get_description():
        return "A sturdy character excelling in defense and resilience."
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/bruiser.png'
    

class Trickster(Character):
    """ Arcane Trickster - balanced stats with magical abilities."""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id=player_id, is_local=is_local)
        
        self.image = pygame.image.load('../../graphics/characters/trickster.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (55, 55))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        self.character_name = "Arcane Trickster"
        self.max_hp = 100
        self.hp = 70
        self.attack = 10
        self.defense = 10
        self.speed = 10

        #self._Character__validate_stats()
        self._illusion_timer = 0  # Timer for special ability duration

    
    def special_ability(self):
        """ Reality Twist: activate visual illusions to confuse enemies."""
        self._illusion_timer = 300  # Illusions last for 5 seconds at 60 FPS
        return True
    
    @staticmethod
    def get_display_name():
        return "Arcane Trickster"
    
    @staticmethod
    def get_description():
        return "A versatile character excelling in magic and trickery."
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/trickster.png'
    
class Guardian(Character):
    """Verdant Guardian - defensive protector with shield."""

    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(pos, groups, obstacle_sprites)
        
        self.image = pygame.image.load('../../graphics/characters/guardian.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (55, 55))
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)
        
        self.character_name = "Verdant Guardian"
        self.max_hp = 100
        self.hp = 85
        self.attack = 12
        self.defense = 15
        self.speed = 7
        #self._Character__validate_stats()
        self._shield_active = False  # Shield status

    def special_ability(self):
        """Nature's Shield: absorb one hit."""
        self._shield_active = True
        return True
    
    @staticmethod
    def get_display_name():
        return "Verdant Guardian"
    
    @staticmethod
    def get_description():
        return "A protective character excelling in defense and support."
    
    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/guardian.png'


def get_all_character_classes():
    """Return all character subclasses"""
    return Character.__subclasses__()
    return character_classes

#def get_all_character_classes():
#    """Auto-discover all character classes"""
#    character_classes = []
#    for cls in Character.__subclasses__():
#        if cls.__name__ != 'Character' and cls.__name__.startswith('Character'):
#            character_classes.append(cls)
#    return character_classes
