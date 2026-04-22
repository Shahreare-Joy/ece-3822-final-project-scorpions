"""
subcharacter.py - Character classes

Different character types that players can choose from
"""

import pygame
from character import Character


class Character1(Character):
    """Street Car - Balanced with temporary speed boost"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)

        self.character_name = "street_car"
        self.hp, self.max_hp = 120, 120
        self.attack, self.defense = 14, 12
        self.speed = 12

        self.boost_active = False
        self.boost_start_time = 0

        try:
            self.image = pygame.image.load('../../graphics/characters/street_car').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def special_ability(self):
        """Speed Boost: temporarily increases speed for 20 seconds."""
        if not self.boost_active:
            self.speed += 5
            self.boost_active = True
            self.boost_start_time = pygame.time.get_ticks()
            print(f"Speed boost activated! Speed increased to {self.speed}")

    def update(self):
        if self.boost_active:
            if pygame.time.get_ticks() - self.boost_start_time >= 20000:
                self.speed -= 5
                self.boost_active = False
                print(f"Speed boost ended. Speed back to {self.speed}")
        super().update()

    @staticmethod
    def get_display_name():
        return "Street Car"

    @staticmethod
    def get_description():
        return "A balanced car with a temporary speed boost ability."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/street_car.png'


class Character2(Character):
    """Muscle Car - High HP and attack with Ram Enforce ability"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)

        self.character_name = "muscle_car"
        self.hp, self.max_hp = 160, 160
        self.attack, self.defense = 18, 16
        self.speed = 8

        self.base_attack = self.attack
        self.special_active = False
        self.special_start_time = 0

        try:
            self.image = pygame.image.load('../../graphics/characters/muscle_car').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def special_ability(self):
        """Ram Enforce: boosts attack for 20 seconds."""
        if not self.special_active:
            self.attack += 5
            self.special_active = True
            self.special_start_time = pygame.time.get_ticks()
            print(f"Ram Enforce activated! Attack is now {self.attack}.")

    def update(self):
        if self.special_active:
            if pygame.time.get_ticks() - self.special_start_time >= 20000:
                self.attack = self.base_attack
                self.special_active = False
                print(f"Ram Enforce ended. Attack reset to {self.attack}.")
        super().update()

    @staticmethod
    def get_display_name():
        return "Muscle Car"

    @staticmethod
    def get_description():
        return "A powerful car built for strength and durability. Slower but great for crashing through obstacles."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/muscle_car.png'


class Character3(Character):
    """Drift Car - High speed with Drift Assist ability"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)

        self.character_name = "drift_car"
        self.hp, self.max_hp = 120, 120
        self.attack, self.defense = 10, 9
        self.speed = 16

        self.base_speed = self.speed
        self.handling = 1.0
        self.base_handling = 1.0
        self.special_active = False
        self.special_start_time = 0

        try:
            self.image = pygame.image.load('../../graphics/characters/drift_car/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def special_ability(self):
        """Drift Assist: improves speed and handling for 20 seconds."""
        if not self.special_active:
            self.speed += 4
            self.handling = 1.5
            self.special_active = True
            self.special_start_time = pygame.time.get_ticks()
            print(f"Drift Assist activated!")

    def update(self):
        if self.special_active:
            if pygame.time.get_ticks() - self.special_start_time >= 20000:
                self.speed = self.base_speed
                self.handling = self.base_handling
                self.special_active = False
                print(f"Drift Assist ended.")
        super().update()

    @staticmethod
    def get_display_name():
        return "Drift Car"

    @staticmethod
    def get_description():
        return "Drift Assist - improves handling and speed while turning."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/drift_car.png'


class Character4(Character):
    """Race Car - Extreme speed with Overdrive ability"""

    def __init__(self, pos, groups, obstacle_sprites, player_id=None, is_local=True):
        super().__init__(pos, groups, obstacle_sprites, player_id, is_local)

        self.character_name = "race_car"
        self.hp, self.max_hp = 100, 100
        self.attack, self.defense = 10, 8
        self.speed = 20

        self.base_speed = self.speed
        self.special_active = False
        self.special_start_time = 0

        try:
            self.image = pygame.image.load('../../graphics/characters/race_car/down/frame_000.png').convert_alpha()
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect.inflate(0, -26)
        except:
            pass

        if is_local:
            self.import_player_assets(animate=True)

    def special_ability(self):
        """Overdrive: massive speed boost for 10 seconds."""
        if not self.special_active:
            self.speed += 10
            self.special_active = True
            self.special_start_time = pygame.time.get_ticks()
            print(f"Overdrive activated!")

    def update(self):
        if self.special_active:
            if pygame.time.get_ticks() - self.special_start_time >= 10000:
                self.speed = self.base_speed
                self.special_active = False
                print(f"Overdrive ended.")
        super().update()

    @staticmethod
    def get_display_name():
        return "Race Car"

    @staticmethod
    def get_description():
        return "A super fast car with extreme speed and acceleration. Very fast but fragile if damaged."

    @staticmethod
    def get_preview_image():
        return '../../graphics/characters/race_car.png'


def get_all_character_classes():
    """Auto-discover all character classes"""
    character_classes = []
    for cls in Character.__subclasses__():
        if cls.__name__ != 'Character' and cls.__name__.startswith('Character'):
            character_classes.append(cls)
    return character_classes
