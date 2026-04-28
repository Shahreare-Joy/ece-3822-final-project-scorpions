"""
enemy.py - Enemy characters that patrol or wander the world

Patrol enemies use linked list patrol paths (lab exercise).

Lab: Lab 6 - Sparse World Map
"""

import pygame
import math
from datastructures.patrol_path import PatrolPath

# Enemy spawn data (Wandering Goblin removed)
ENEMY_SPAWN_DATA = [
    {
        "name": "Forest Guard",
        "spawn": (8, 8),
        "waypoints": [(5, 5), (15, 5), (15, 11), (5, 11)],
        "patrol_type": "circular",
        "speed": 1,
        "description": "Loops around the city raceway",
        "health": 60,  "exp": 30, "attack_damage": 8,
        "notice_radius": 150, "attack_radius": 60,
    },
    {
        "name": "Village Merchant",
        "spawn": (27, 7),
        "waypoints": [(23, 7), (33, 7)],
        "patrol_type": "back_and_forth",
        "speed": 0.9,
        "description": "Cruises the desert connector road",
        "health": 40,  "exp": 20, "attack_damage": 5,
        "notice_radius": 150, "attack_radius": 50,
    },
    {
        "name": "Temple Priest",
        "spawn": (8, 34),
        "waypoints": [(8, 34), (12, 31), (17, 35)],
        "patrol_type": "one_way",
        "speed": 0.8,
        "description": "Glides once through the oasis loop",
        "health": 40,  "exp": 20, "attack_damage": 5,
        "notice_radius": 150, "attack_radius": 50,
    },
    {
        "name": "Dungeon Scout",
        "spawn": (44, 28),
        "waypoints": [(40, 24), (52, 24), (52, 34), (40, 34)],
        "patrol_type": "circular",
        "speed": 1,
        "description": "Circles the salvage yard lanes",
        "health": 80,  "exp": 40, "attack_damage": 12,
        "notice_radius": 150, "attack_radius": 60,
    },
    {
        "name": "Market Vendor",
        "spawn": (48, 34),
        "waypoints": [(46, 33), (52, 33)],
        "patrol_type": "back_and_forth",
        "speed": 0.8,
        "description": "Watches the industrial straightaway",
        "health": 40,  "exp": 20, "attack_damage": 5,
        "notice_radius": 150, "attack_radius": 50,
    },
]

# Sprites that actually exist in graphics/enemies/
_KNOWN_SPRITES = {'forest_guard', 'village_merchant', 'temple_priest',
                  'dungeon_scout', 'market_vendor'}


class Enemy(pygame.sprite.Sprite):
    """
    Enemy character that follows a patrol path.

    Patrol types: one_way / circular / back_and_forth
    Uses a PatrolPath linked list to determine movement.
    """

    def __init__(self, name, start_x, start_y, patrol_path, obstacle_sprites,
                 speed=1.0, sprite_name=None, patrol_type=None,
                 health=60, exp=30, attack_damage=10,
                 notice_radius=200, attack_radius=60,
                 damage_player=None):
        super().__init__()

        self.name = name
        self.speed = speed
        self.patrol_path = patrol_path
        self.obstacle_sprites = obstacle_sprites

        # Resolve sprite name, fall back to dungeon_scout if not found
        raw_name = (sprite_name or name.lower().replace(' ', '_'))
        self.sprite_name = raw_name if raw_name in _KNOWN_SPRITES else 'dungeon_scout'

        # Determine movement mode
        self.patrol_type = patrol_path.patrol_type if patrol_path is not None else 'one_way'

        # Float position for sub-pixel accumulation (pygame Rects are integers)
        self.x = float(start_x * 64 + 32)
        self.y = float(start_y * 64 + 32)

        # Movement / animation
        self.direction = pygame.math.Vector2()
        self.status = 'down_idle'
        self.last_direction = 'down'

        # Patrol state
        if patrol_path is not None:
            self.target_waypoint = self.patrol_path.get_next_waypoint()
        else:
            self.target_waypoint = None
        self.wait_timer = 0
        self.is_waiting = False
        self.patrol_active = True

        # Sprites
        self.load_sprites()
        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.hitbox = self.rect.inflate(-10, -10)

        # Combat stats
        self.health = health
        self.max_health = health
        self.exp = exp
        self.attack_damage = attack_damage
        self.notice_radius = notice_radius
        self.attack_radius = attack_radius
        self.damage_player = damage_player

        # Combat state
        self.combat_status = 'patrol'        # 'patrol' | 'chase' | 'attack'
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 800

        # Hit invincibility
        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = 300

        self.frame_index = 0
        self.animation_speed = 0.15

    # ------------------------------------------------------------------
    # Sprite loading
    # ------------------------------------------------------------------

    def load_sprites(self):
        """Load directional sprite animations using the unified sprite system."""
        from sprite_loader import SpriteLoader
        self.animations = SpriteLoader.load_enemy_sprites(self.sprite_name)
        import os as _os
        _enemies_dir = _os.path.join(
            _os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'graphics', 'enemies')
        sprite_info = SpriteLoader.get_sprite_info(self.sprite_name, _enemies_dir)
        print(f"  Loaded {sprite_info['type']} sprites for {self.name}: {sprite_info}")

    # ------------------------------------------------------------------
    # Update loop
    # ------------------------------------------------------------------

    def update(self):
        """Update enemy behavior each frame."""
        if self.combat_status == 'chase':
            self.move()
        elif self.combat_status == 'attack':
            self.direction.x = 0
            self.direction.y = 0
            if self.can_attack and self.damage_player:
                self.damage_player(self.attack_damage)
                self.can_attack = False
                self.attack_time = pygame.time.get_ticks()
        else:
            self._update_patrol()

        self._cooldowns_combat()
        self.get_status()
        self.animate()
        self.check_death()

    # ------------------------------------------------------------------
    # Patrol logic (one_way / circular / back_and_forth)
    # ------------------------------------------------------------------

    def _update_patrol(self):
        """Move along the linked-list patrol path."""
        if not self.patrol_active or not self.target_waypoint:
            self.direction.x = 0
            self.direction.y = 0
            return

        if self.is_waiting:
            self.direction.x = 0
            self.direction.y = 0
            self.wait_timer -= 1 / 60
            if self.wait_timer <= 0:
                self.is_waiting = False
                self.target_waypoint = self.patrol_path.get_next_waypoint()
            return

        self._move_toward_target()

    def _move_toward_target(self):
        """Move toward the current waypoint."""
        if not self.target_waypoint:
            self.patrol_active = False
            self.direction.x = 0
            self.direction.y = 0
            return

        target_x = self.target_waypoint.x * 64 + 32
        target_y = self.target_waypoint.y * 64 + 32

        dx = target_x - self.hitbox.centerx
        dy = target_y - self.hitbox.centery
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.speed * 2:
            self.direction.x = 0
            self.direction.y = 0
            if self.target_waypoint.wait_time > 0:
                self.is_waiting = True
                self.wait_timer = self.target_waypoint.wait_time
            else:
                self.target_waypoint = self.patrol_path.get_next_waypoint()
        else:
            if distance > 0:
                self.direction.x = (dx / distance) * self.speed
                self.direction.y = (dy / distance) * self.speed
            self.move()

    # ------------------------------------------------------------------
    # Movement + collision (spatially culled for performance)
    # ------------------------------------------------------------------

    def move(self):
        """Move using float accumulators; only update Rect when integer pixel changes."""
        if self.direction.x != 0:
            self.x += self.direction.x
            new_cx = int(self.x)
            if new_cx != self.hitbox.centerx:
                self.hitbox.centerx = new_cx
                self.collision('horizontal')
                self.x = float(self.hitbox.centerx)

        if self.direction.y != 0:
            self.y += self.direction.y
            new_cy = int(self.y)
            if new_cy != self.hitbox.centery:
                self.hitbox.centery = new_cy
                self.collision('vertical')
                self.y = float(self.hitbox.centery)

        self.rect.center = self.hitbox.center

    def collision(self, direction):
        """Collision check against nearby obstacles only (spatially culled)."""
        ex = self.hitbox.centerx
        ey = self.hitbox.centery
        check_radius = 128  # only test sprites within ~2 tiles

        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite is self:
                    continue
                sprite_rect = getattr(sprite, 'hitbox', sprite.rect)
                if abs(sprite_rect.centerx - ex) > check_radius:
                    continue
                if abs(sprite_rect.centery - ey) > check_radius:
                    continue
                if sprite_rect.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite_rect.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite_rect.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite is self:
                    continue
                sprite_rect = getattr(sprite, 'hitbox', sprite.rect)
                if abs(sprite_rect.centerx - ex) > check_radius:
                    continue
                if abs(sprite_rect.centery - ey) > check_radius:
                    continue
                if sprite_rect.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite_rect.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite_rect.bottom

    # ------------------------------------------------------------------
    # Animation helpers
    # ------------------------------------------------------------------

    def get_status(self):
        """Set status string for animation based on current movement direction."""
        if self.direction.x == 0 and self.direction.y == 0:
            if 'idle' not in self.status:
                self.status = self.last_direction + '_idle'
        else:
            if abs(self.direction.x) > abs(self.direction.y):
                if self.direction.x > 0:
                    self.status = 'right'
                    self.last_direction = 'right'
                else:
                    self.status = 'left'
                    self.last_direction = 'left'
            else:
                if self.direction.y > 0:
                    self.status = 'down'
                    self.last_direction = 'down'
                else:
                    self.status = 'up'
                    self.last_direction = 'up'

    def animate(self):
        """Advance the animation frame."""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]

        # Flicker while invincible after being hit
        if not self.vulnerable:
            from math import sin
            self.image = self.image.copy()
            self.image.set_alpha(255 if sin(pygame.time.get_ticks() * 0.015) >= 0 else 80)

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def get_player_distance_direction(self, player):
        """Return (pixel_distance, normalized Vector2) toward player."""
        enemy_vec  = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance   = (player_vec - enemy_vec).magnitude()
        direction  = (player_vec - enemy_vec).normalize() if distance > 0 else pygame.math.Vector2()
        return distance, direction

    def enemy_update(self, player):
        """Update combat AI state (called from Level with player reference)."""
        distance, direction = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            self.combat_status = 'attack'
        elif distance <= self.notice_radius:
            self.combat_status = 'chase'
            self.direction.x = direction.x * self.speed
            self.direction.y = direction.y * self.speed
        else:
            self.combat_status = 'patrol'

    def get_damage(self, player):
        """Take weapon damage from player."""
        if self.vulnerable:
            self.health -= player.get_full_weapon_damage()
            self.vulnerable = False
            self.hit_time = pygame.time.get_ticks()

    def check_death(self):
        """Remove enemy and award XP when health reaches zero."""
        if self.health <= 0:
            self.kill()

    def _cooldowns_combat(self):
        """Restore can_attack and vulnerable after their cooldowns."""
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True
        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------

    def draw_debug_info(self, surface, camera_offset=(0, 0)):
        """Draw debug overlay: name, target line, hitbox."""
        font = pygame.font.Font(None, 20)
        text = font.render(self.name, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.centerx = self.rect.centerx - camera_offset[0]
        text_rect.bottom = self.rect.top - camera_offset[1] - 5
        surface.blit(text, text_rect)

        ex = self.rect.centerx - camera_offset[0]
        ey = self.rect.centery - camera_offset[1]

        if self.target_waypoint and self.patrol_active:
            tx = self.target_waypoint.x * 64 + 32 - camera_offset[0]
            ty = self.target_waypoint.y * 64 + 32 - camera_offset[1]
            pygame.draw.line(surface, (255, 255, 0), (ex, ey), (int(tx), int(ty)), 2)
            pygame.draw.circle(surface, (255, 0, 0), (int(tx), int(ty)), 8, 2)

        hitbox_rect = self.hitbox.copy()
        hitbox_rect.x -= camera_offset[0]
        hitbox_rect.y -= camera_offset[1]
        pygame.draw.rect(surface, (0, 255, 0), hitbox_rect, 1)

    def get_debug_status(self):
        """One-line status string for the debug overlay."""
        if not self.patrol_active:
            return f"{self.name}: Patrol Complete"
        if self.is_waiting:
            return f"{self.name}: Waiting ({self.wait_timer:.1f}s)"
        if self.target_waypoint:
            return f"{self.name}: Moving to ({self.target_waypoint.x}, {self.target_waypoint.y})"
        return f"{self.name}: No target"

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset_patrol(self):
        """Reset enemy to the start of its patrol."""
        self.direction.x = 0
        self.direction.y = 0
        self.patrol_path.reset()
        self.target_waypoint = self.patrol_path.get_next_waypoint()
        self.patrol_active = True
        self.is_waiting = False
        self.wait_timer = 0
