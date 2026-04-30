"""
level.py - Game level with character classes and networking

Integrated version combining lab-03 and project-01
"""

import pygame
import random
from settings import *
from tile import Tile
from map_loader import load_layer
from character import Character
from subcharacter import get_all_character_classes
from network_client import NetworkClient
from inventory_ui import InventoryUI
from item import create_example_items
from time_travel import TimeTravel
from enemy import Enemy, ENEMY_SPAWN_DATA
from datastructures.patrol_path import PatrolPath
from weapon import Weapon as WeaponSprite
import sys


class FruitSprite(pygame.sprite.Sprite):
    """Collectible fruit placed on the existing map.

    The sprite is intentionally simple and self-contained so it does not alter
    the uploaded map, character, inventory, or enemy systems.
    """

    def __init__(self, pos, groups, golden=False):
        super().__init__(groups)
        self.golden = golden
        self.points = GOLDEN_FRUIT_POINTS if golden else NORMAL_FRUIT_POINTS

        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
        if golden:
            pygame.draw.circle(self.image, (255, 209, 67), (17, 18), 13)
            pygame.draw.circle(self.image, (255, 244, 172), (12, 12), 5)
        else:
            pygame.draw.circle(self.image, (230, 67, 78), (17, 18), 12)
            pygame.draw.circle(self.image, (255, 125, 121), (12, 13), 4)
        pygame.draw.ellipse(self.image, (74, 171, 93), pygame.Rect(17, 4, 12, 7))

        self.rect = self.image.get_rect(center=pos)


class HazardSprite(pygame.sprite.Sprite):
    """Danger item that appears in the second half of the round."""

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((38, 38), pygame.SRCALPHA)
        points = [(19, 2), (25, 13), (36, 19), (25, 25), (19, 36), (13, 25), (2, 19), (13, 13)]
        pygame.draw.polygon(self.image, (122, 30, 156), points)
        pygame.draw.polygon(self.image, (250, 72, 102), points, width=3)
        pygame.draw.circle(self.image, (255, 229, 92), (19, 19), 6)
        pygame.draw.line(self.image, (255, 245, 170), (19, 8), (19, 30), 2)
        pygame.draw.line(self.image, (255, 245, 170), (8, 19), (30, 19), 2)
        self.rect = self.image.get_rect(center=pos)


class Level:
    def __init__(self, player_name, character_class, server_host='localhost', server_port=DEFAULT_PORT, serializer='text'):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # Combat sprite groups
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        
        self.visible_sprites = YSortCameraGroup()
        self.floor_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.fruit_sprites = pygame.sprite.Group()
        self.hazard_sprites = pygame.sprite.Group()


        # Store character class for player creation
        self.character_class = character_class

        # Sprite setup
        self.create_map()

        # Network setup with serializer
        self.network = NetworkClient(player_name, server_host, normalize_server_port(server_port), serializer)
        self.connected = self.network.connect()
        if self.connected:
            self.connection_status = f"Connected - player {self.network.my_player_id} ({self.network.serializer.upper()})"
        else:
            self.connection_status = "Session-based fallback: gameplay local, chat/scores still work"
            print(f"[NET] Real-time multiplayer unavailable. {self.network.disconnect_reason}")
            print("[NET] Fallback limitation: this client will continue as a local session; score/history/leaderboard reporting is unchanged.")

        # Track other players
        self.other_players = {}  # player_id -> Character sprite

        # Font for displaying names
        self.font = pygame.font.Font(None, 24)

        # Inventory UI
        self.inventory_ui = InventoryUI(self.player.inventory)
        self.inventory_ui.character = self.player   # equip-button needs this

        # Add starting items for testing
        self.add_starting_items()

        # Time travel system (Lab 4)
        self.time_travel = TimeTravel(max_history=180)
        self.is_time_traveling = False
        self.enemy_history = []   # parallel enemy state snapshots
        self.enemy_future  = []   # enemy future states for replay

        # Enemy system (Lab 5)
        self.enemies = pygame.sprite.Group()
        self.create_enemies()

# Fruit Drop Rush round state. These values are read by main.py for
        # the game-over screen and final arcade session-result payload.
        self.score = 0
        self.fruits_collected = 0
        self.golden_fruits_collected = 0
        self.round_started_at = pygame.time.get_ticks()
        self.game_over = False
        self.game_over_reason = ""
        self.hazards_active = False
        self.hazard_hits = 0
        self.last_hazard_hit_at = 0
        self.create_fruits()

        # Debug mode for showing enemy paths
        self.show_enemy_debug = False

    def _load_tileset(self, path):
        """Load a tileset image and return a dict mapping tile_id -> Surface.

        Assumes tiles are arranged left-to-right, top-to-bottom in a grid of
        TILESIZE x TILESIZE cells.  Returns an empty dict if the file is
        missing or unreadable.
        """
        try:
            sheet = pygame.image.load(path).convert_alpha()
            cols = sheet.get_width()  // TILESIZE
            rows = sheet.get_height() // TILESIZE
            tiles = {}
            for r in range(rows):
                for c in range(cols):
                    tile_id = r * cols + c
                    surf = sheet.subsurface(pygame.Rect(c * TILESIZE, r * TILESIZE, TILESIZE, TILESIZE))
                    tiles[tile_id] = surf
            return tiles
        except Exception:
            return {}

    def create_map(self):
        """Create the game map and player from CSV layers."""
        grass_tiles = self._load_tileset('../../graphics/tilemap/ground.png')

        # Change this path if your objects live in another tileset image
        object_tiles = self._load_tileset('../../graphics/tilemap/objects.png')

        LAYERS = [
            ('map/map_FloorBlocks.csv', 'boundary',
            [self.visible_sprites, self.obstacle_sprites], {}),

            ('map/map_Grass.csv', 'grass',
            [self.floor_sprites], grass_tiles),

            ('map/map_Objects.csv', 'object',
            [self.visible_sprites, self.obstacle_sprites], object_tiles),
        ]

        floor_blocks_loaded = False

        for csv_path, sprite_type, groups, tileset in LAYERS:
            try:
                layer = load_layer(csv_path)
                entries = list(layer.items())

                if not entries:
                    print(f"[Map] {csv_path}: no entries")
                    continue

                print(f"[Map] {csv_path}: {len(entries)} tiles")

                for (row, col), tile_id in entries:

                    if sprite_type == 'object':
                        print(f"OBJECT at ({row}, {col}) -> tile_id {tile_id}")
                    else:
                        print(f"[Map] Missing tile id {tile_id} in {csv_path}")


                    x = col * TILESIZE
                    y = row * TILESIZE

                    if sprite_type == 'boundary':
                        Tile((x, y), groups, sprite_type)
                    else:
                        surf = tileset.get(tile_id)
                        if surf is not None:
                            Tile((x, y), groups, sprite_type, surf)
                        else:
                            print(f"[Map] Missing tile id {tile_id} in {csv_path}")

                if sprite_type == 'boundary':
                    floor_blocks_loaded = True

            except Exception as e:
                print(f"[Map] {csv_path} failed: {e}")

        # Player spawn fallback from WORLD_MAP
        player_spawned = False
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index * TILESIZE
                y = row_index * TILESIZE

                if col == 'x' and not floor_blocks_loaded:
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'boundary')

                if col == 'p':
                    self.player = self.character_class(
                        (x, y),
                        [self.visible_sprites],
                        self.obstacle_sprites,
                        is_local=True
                    )
                    self.player.create_attack_callback = self.create_attack
                    self.player.destroy_attack_callback = self.destroy_attack
                    player_spawned = True

        if not player_spawned:
            # Safe fallback spawn
            self.player = self.character_class(
                (5 * TILESIZE, 5 * TILESIZE),
                [self.visible_sprites],
                self.obstacle_sprites,
                is_local=True
            )
            self.player.create_attack_callback = self.create_attack
            self.player.destroy_attack_callback = self.destroy_attack

    def add_starting_items(self):
        """Add items defined in item.py's create_example_items() to the player's inventory."""
        print("Adding starting items to inventory...")

        for item in create_example_items():
            success = self.player.inventory.add_item(item)
            if success:
                print(f"  Added: {item.name}")
            else:
                print(f"  Inventory full! Couldn't add: {item.name}")

        print(f"Total items: {len(self.player.inventory.items)}")

        # Auto-equip the first weapon so combat works immediately on startup
        for item in self.player.inventory.items:
            if item.item_type == 'weapon':
                self.player.equipped_weapon = item
                print(f"Auto-equipped: {item.name}")
                break

        print("Press 'I' to open inventory and switch weapons. SPACE to attack!")

    def create_enemies(self):
        """Create enemies — patrol types use linked list paths (Lab 5), random type wanders freely."""
        try:
            print("Creating enemies...")

            for data in ENEMY_SPAWN_DATA:
                try:
                    combat_kwargs = dict(
                        health=data.get("health", 60),
                        exp=data.get("exp", 30),
                        attack_damage=data.get("attack_damage", 10),
                        notice_radius=data.get("notice_radius", 200),
                        attack_radius=data.get("attack_radius", 60),
                        damage_player=self.damage_player,
                    )

                    if data["patrol_type"] == "random":
                        # Random enemy: no patrol path needed
                        enemy = Enemy(
                            name=data["name"],
                            start_x=data["spawn"][0],
                            start_y=data["spawn"][1],
                            patrol_path=None,
                            patrol_type="random",
                            obstacle_sprites=self.obstacle_sprites,
                            speed=data["speed"],
                            sprite_name=data["name"].lower().replace(' ', '_'),
                            **combat_kwargs
                        )
                    else:
                        # Patrol enemy: build linked list path
                        patrol_path = PatrolPath(data["patrol_type"])
                        for waypoint in data["waypoints"]:
                            x, y = waypoint
                            patrol_path.add_waypoint(x, y, wait_time=1.0)

                        enemy = Enemy(
                            name=data["name"],
                            start_x=data["spawn"][0],
                            start_y=data["spawn"][1],
                            patrol_path=patrol_path,
                            obstacle_sprites=self.obstacle_sprites,
                            speed=data["speed"],
                            sprite_name=data["name"].lower().replace(' ', '_'),
                            **combat_kwargs
                        )

                    self.enemies.add(enemy)
                    self.visible_sprites.add(enemy)
                    self.obstacle_sprites.add(enemy)
                    self.attackable_sprites.add(enemy)

                    print(f"  Created: {data['name']} ({data['patrol_type']})")
                except Exception as e:
                    print(f"  Failed to create enemy {data['name']}: {e}")

            print(f"Total enemies created: {len(self.enemies)}")
            if len(self.enemies) > 0:
                print("Press 'N' to toggle enemy debug view!")
            else:
                print("No patrol enemies created - implement Waypoint and PatrolPath to see them!")

        except ImportError as e:
            print(f"Enemies not available yet: {e}")
            print("Complete the linked list implementation in datastructures/ to enable patrol enemies!")
        except Exception as e:
            print(f"Error setting up enemies: {e}")
            print("Check your Waypoint and PatrolPath implementations!")

    # ------------------------------------------------------------------
# Fruit Drop Rush rules
    # ------------------------------------------------------------------

    def create_fruits(self):
        """Seed the map with collectible fruit.

        Fruits use the existing camera/sprite system and are collected when the
        player walks into them. Golden fruit is rare and worth more points.
        """

        for _ in range(STARTING_FRUIT_COUNT):
            self.spawn_fruit()

    def spawn_fruit(self):
        """Place one fruit on a walkable tile without changing the map."""

        if not WORLD_MAP:
            return

        for _ in range(80):
            row_index = random.randrange(len(WORLD_MAP))
            col_index = random.randrange(len(WORLD_MAP[row_index]))
            tile = WORLD_MAP[row_index][col_index]

            if tile == 'x':
                continue

            x = col_index * TILESIZE + TILESIZE // 2
            y = row_index * TILESIZE + TILESIZE // 2
            test_rect = pygame.Rect(0, 0, 34, 34)
            test_rect.center = (x, y)

            if test_rect.colliderect(self.player.rect):
                continue
            if any(test_rect.colliderect(fruit.rect) for fruit in self.fruit_sprites):
                continue
            if any(test_rect.colliderect(sprite.rect) for sprite in self.obstacle_sprites):
                continue

            is_golden = random.random() < GOLDEN_FRUIT_CHANCE
            FruitSprite((x, y), [self.visible_sprites, self.fruit_sprites], golden=is_golden)
            return

    def activate_hazards(self):
        """Spawn fair second-half hazards.

        Rule: hazards only appear once half the timer is gone. Touching one
        removes a little HP and score, then moves that hazard elsewhere. A
        short cooldown prevents one bad step from draining all health at once.
        """

        if self.hazards_active:
            return
        self.hazards_active = True
        for _ in range(HAZARD_SPAWN_COUNT):
            self.spawn_hazard()

    def spawn_hazard(self):
        """Place one dangerous item away from walls, fruits, and the player."""

        if not WORLD_MAP:
            return

        for _ in range(100):
            row_index = random.randrange(len(WORLD_MAP))
            col_index = random.randrange(len(WORLD_MAP[row_index]))
            if WORLD_MAP[row_index][col_index] == 'x':
                continue

            x = col_index * TILESIZE + TILESIZE // 2
            y = row_index * TILESIZE + TILESIZE // 2
            test_rect = pygame.Rect(0, 0, 38, 38)
            test_rect.center = (x, y)

            if test_rect.colliderect(self.player.rect.inflate(96, 96)):
                continue
            if any(test_rect.colliderect(sprite.rect) for sprite in self.obstacle_sprites):
                continue
            if any(test_rect.colliderect(fruit.rect) for fruit in self.fruit_sprites):
                continue
            if any(test_rect.colliderect(hazard.rect) for hazard in self.hazard_sprites):
                continue

            HazardSprite((x, y), [self.visible_sprites, self.hazard_sprites])
            return

    def handle_hazards(self):
        """Enable midpoint hazards and apply collision damage safely."""

        if self.time_remaining() <= GAME_DURATION_SECONDS // 2:
            self.activate_hazards()
        if not self.hazards_active:
            return

        player_rect = getattr(self.player, "hitbox", self.player.rect)
        touched = [hazard for hazard in self.hazard_sprites if hazard.rect.colliderect(player_rect)]
        if not touched:
            return

        now = pygame.time.get_ticks()
        if now - self.last_hazard_hit_at < HAZARD_HIT_COOLDOWN_MS:
            return

        self.last_hazard_hit_at = now
        self.hazard_hits += 1
        self.score = max(0, self.score - HAZARD_SCORE_PENALTY)
        self.player.take_damage(HAZARD_DAMAGE)

        for hazard in touched:
            hazard.kill()
            self.spawn_hazard()

    def collect_fruits(self):
        """Increase score when the player touches fruit."""

        player_rect = getattr(self.player, "hitbox", self.player.rect)
        collected = [fruit for fruit in self.fruit_sprites if fruit.rect.colliderect(player_rect)]

        for fruit in collected:
            self.score += fruit.points
            self.fruits_collected += 1
            if fruit.golden:
                self.golden_fruits_collected += 1
            fruit.kill()
            self.spawn_fruit()

    def time_remaining(self):
        """Return seconds left in the round."""

        elapsed = (pygame.time.get_ticks() - self.round_started_at) / 1000
        return max(0, int(GAME_DURATION_SECONDS - elapsed))

    def check_round_end(self):
        """Stop gameplay when health reaches 0 or the countdown expires."""

        if self.game_over:
            return
        if self.player.hp <= 0:
            self.finish_round("Health reached 0")
        elif self.time_remaining() <= 0:
            self.finish_round("Time expired")

    def finish_round(self, reason):
        """Freeze the round and make final stats available to main.py."""

        self.game_over = True
        self.game_over_reason = reason

    def session_result_payload(self, player_name, game_id, session_id):
        """Build the arcade session-result payload for the launcher service."""

        elapsed = min(GAME_DURATION_SECONDS, (pygame.time.get_ticks() - self.round_started_at) / 1000)
        outcome = "Game Over" if self.player.hp <= 0 else "Complete"
        if self.game_over_reason == "Time expired":
            outcome = "Time Up"
        return {
            "player_id": player_name,
            "game_id": game_id,
            "session_id": session_id,
            "score": self.score,
            "outcome": outcome,
            "duration_seconds": int(elapsed),
            "metadata": {
                "fruits_collected": self.fruits_collected,
                "golden_fruits_collected": self.golden_fruits_collected,
                "health_remaining": self.player.hp,
                "hazard_hits": self.hazard_hits,
                "reason": self.game_over_reason,
            },
        }

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def create_attack(self):
        """Spawn a weapon sprite in front of the player (called on SPACE)."""
        self.current_attack = WeaponSprite(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        """Remove the weapon sprite when the attack cooldown ends."""
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        """Check weapon sprite vs every enemy each frame."""
        for attack_sprite in list(self.attack_sprites):
            for enemy in pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False):
                was_alive = enemy.health > 0
                enemy.get_damage(self.player)
                if was_alive and enemy.health <= 0:
                    self.player.exp += enemy.exp   # award XP exactly once on kill

    def damage_player(self, amount):
        """Called by enemies when they land an attack."""
        self.player.take_damage(amount)

    # ------------------------------------------------------------------

    def update_network(self):
        """Handle network synchronization"""
        self.connected = self.network.connected
        if not self.connected:
            reason = self.network.disconnect_reason or "gameplay server unavailable"
            self.connection_status = f"Session fallback: {reason}"
            return

        # Send our position, character type, and status to server
        character_type = self.player.character_name.lower()
        status = self.player.status.replace("_idle", "").replace("_attack", "")
        self.network.send_update(self.player.rect.x, self.player.rect.y, character_type, status)

        # Get updates from server
        updates = self.network.get_updates()

        if updates:
            self.connection_status = f"Connected - {len(updates)} players online ({self.network.serializer.upper()})"

            current_player_ids = set()

            for player_id, data in updates.items():
                current_player_ids.add(player_id)

                if player_id == self.network.my_player_id:
                    continue

                if player_id not in self.other_players:
                    character_type = data.get('character_type', '').lower()

                    all_classes = get_all_character_classes()
                    CharClass = None
                    for cls in all_classes:
                        if cls.get_display_name().lower() == character_type:
                            CharClass = cls
                            break

                    if CharClass is None:
                        CharClass = Character
                        print(f"[NET] Using ghost marker for remote player {player_id}; character_type='{character_type or 'missing'}'")

                    try:
                        other_player = CharClass(
                            (data['x'], data['y']),
                            [self.visible_sprites],
                            self.obstacle_sprites,
                            player_id=player_id,
                            is_local=False
                        )
                    except TypeError:
                        other_player = Character(
                            (data['x'], data['y']),
                            [self.visible_sprites],
                            self.obstacle_sprites,
                            player_id=player_id,
                            is_local=False
                        )
                    other_player.name = data['name']
                    self.other_players[player_id] = other_player
                    print(f"[NET] Created remote player marker {player_id} at ({data['x']}, {data['y']})")
                else:
                    other_player = self.other_players[player_id]
                    other_player.set_position(data['x'], data['y'])
                    other_player.name = data['name']
                    if 'status' in data:
                        other_player.status = data['status']

            disconnected = set(self.other_players.keys()) - current_player_ids
            for player_id in disconnected:
                self.other_players[player_id].kill()
                del self.other_players[player_id]

            self.player.other_players = list(self.other_players.values())

    def handle_events(self, events):
        """Handle pygame events (pass from main game loop)"""
        for event in events:
            self.inventory_ui.handle_event(event, self.player)

    def draw_names(self):
        """Draw player names above their heads"""
        if self.network.my_player_id is not None:
            name_text = f"{self.network.player_name} ({self.player.character_name})"
            name_surface = self.font.render(name_text, True, (0, 255, 0))
            name_rect = name_surface.get_rect(
                center=(self.player.rect.centerx, self.player.rect.top - 10)
            )
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

        for other_player in self.other_players.values():
            name_surface = self.font.render(other_player.name, True, (100, 100, 255))
            name_rect = name_surface.get_rect(
                center=(other_player.rect.centerx, other_player.rect.top - 10)
            )
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

    def draw_status(self):
        """Draw an arcade-style HUD that stays readable over the map."""

        panel = pygame.Rect(10, 10, 292, 140)
        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((6, 10, 18, 212))
        pygame.draw.rect(overlay, (68, 232, 218, 235), overlay.get_rect(), width=2, border_radius=8)
        pygame.draw.rect(overlay, (255, 218, 86, 215), pygame.Rect(7, 7, 6, panel.height - 14), border_radius=3)
        self.display_surface.blit(overlay, panel)

        title_font = pygame.font.Font(None, 22)
        small_font = pygame.font.Font(None, 18)
        tiny_font = pygame.font.Font(None, 16)
        status_color = (0, 255, 0) if self.connected else (255, 100, 100)
        status = "Connected" if self.connected else "Local fallback"
        self.display_surface.blit(
            title_font.render("Fruit Drop Rush", True, (255, 244, 172)), (panel.x + 20, panel.y + 8))
        self.display_surface.blit(
            tiny_font.render(status, True, status_color), (panel.right - 82, panel.y + 12))

        self.display_surface.blit(
            tiny_font.render("L Level | ESC Leave", True, (230, 239, 252)), (panel.x + 20, panel.y + 31))

        # Health bar
        hp_width = 148
        bar_rect  = pygame.Rect(panel.x + 50, panel.y + 50, hp_width, 14)
        ratio     = max(0.0, self.player.hp / max(1, self.player.max_hp))
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, int(hp_width * ratio), bar_rect.height)
        self.display_surface.blit(small_font.render("HP", True, (250, 252, 255)), (panel.x + 20, panel.y + 47))
        pygame.draw.rect(self.display_surface, UI_BG_COLOR,     bar_rect)
        pygame.draw.rect(self.display_surface, HEALTH_COLOR,    fill_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bar_rect, 2)
        self.display_surface.blit(
            tiny_font.render(f"{self.player.hp}/{self.player.max_hp}", True, (255, 255, 255)),
            (bar_rect.right + 7, bar_rect.y))

        left_x = panel.x + 20
        right_x = panel.x + 150
        base_y = panel.y + 76
        stats = [
            (f"Score {self.score}", (245, 248, 255), left_x, base_y),
            (f"Time {self.time_remaining()}s", (120, 210, 255), right_x, base_y),
            (f"Fruits {self.fruits_collected}", (255, 210, 120), left_x, base_y + 20),
            (f"Hazards -{HAZARD_DAMAGE} HP" if self.hazards_active else "Hazards at half-time", (255, 116, 142), right_x, base_y + 20),
        ]
        for text, color, x, y in stats:
            self.display_surface.blit(small_font.render(text, True, color), (x, y))

        if self.player.equipped_weapon:
            w = self.player.equipped_weapon
            msg = f"I/SPACE | XP {self.player.exp} | {w.name} +{w.attack_bonus}"
            color = (255, 200, 100)
        else:
            msg   = f"I/SPACE | XP {self.player.exp} | no weapon"
            color = (150, 150, 150)
        if len(msg) > 38:
            msg = msg[:35] + "..."
        self.display_surface.blit(tiny_font.render(msg, True, color), (left_x, base_y + 40))

    # ------------------------------------------------------------------
    # Time travel + enemy state snapshots
    # ------------------------------------------------------------------

    def _snapshot_enemies(self):
        """Capture full enemy state (position, patrol cursor, combat) for time-travel."""
        enemies = []
        for enemy in self.enemies:
            enemies.append({
                'x': enemy.rect.x,
                'y': enemy.rect.y,
                'target_waypoint': enemy.target_waypoint,
                'patrol_active': enemy.patrol_active,
                'is_waiting': enemy.is_waiting,
                'wait_timer': enemy.wait_timer,
                'patrol_current':   enemy.patrol_path.current   if enemy.patrol_path else None,
                'patrol_direction': enemy.patrol_path.direction if enemy.patrol_path else None,
                'wander_target': getattr(enemy, 'wander_target', None),
                'health': enemy.health,
                'combat_status': enemy.combat_status,
            })
        return {'enemies': enemies, 'player_hp': self.player.hp}

    def _restore_enemies(self, snapshot):
        """Restore full enemy state from a snapshot (also restores player HP)."""
        enemy_list = snapshot['enemies'] if isinstance(snapshot, dict) else snapshot
        for enemy, state in zip(self.enemies, enemy_list):
            enemy.rect.x = state['x']
            enemy.rect.y = state['y']
            enemy.x = float(enemy.rect.x)
            enemy.y = float(enemy.rect.y)
            enemy.hitbox.center = enemy.rect.center
            enemy.target_waypoint = state['target_waypoint']
            enemy.patrol_active = state['patrol_active']
            enemy.is_waiting = state['is_waiting']
            enemy.wait_timer = state['wait_timer']
            if enemy.patrol_path is not None:
                enemy.patrol_path.current   = state['patrol_current']
                enemy.patrol_path.direction = state['patrol_direction']
            if hasattr(enemy, 'wander_target'):
                enemy.wander_target = state['wander_target']
            enemy.health        = state.get('health', enemy.health)
            enemy.combat_status = state.get('combat_status', 'patrol')

        if isinstance(snapshot, dict):
            self.player.hp = snapshot.get('player_hp', self.player.hp)
            self.player.vulnerable = True   # reset after rewind

    def record_player_state(self):
        if not self.is_time_traveling and not self.connected:
            prev_size = self.time_travel.get_history_size()
            self.time_travel.record_state(
                self.player.rect.x,
                self.player.rect.y
            )
            # Only sync enemy history when TimeTravel actually recorded a frame
            if self.time_travel.get_history_size() > prev_size:
                self.enemy_history.append(self._snapshot_enemies())
                while len(self.enemy_history) > self.time_travel.max_history:
                    self.enemy_history.pop(0)
                self.enemy_future.clear()

    def handle_time_travel_input(self, events):
        if self.connected:
            self.is_time_traveling = False
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.time_travel.can_rewind():
                    state = self.time_travel.rewind()
                    if state:
                        self.player.rect.x = state.player_x
                        self.player.rect.y = state.player_y
                        self.player.hitbox.center = self.player.rect.center
                        self.is_time_traveling = True
                        if self.enemy_history:
                            self.enemy_future.append(self.enemy_history.pop())
                            if self.enemy_history:
                                self._restore_enemies(self.enemy_history[-1])

                elif event.key == pygame.K_f and self.time_travel.can_replay():
                    state = self.time_travel.replay()
                    if state:
                        self.player.rect.x = state.player_x
                        self.player.rect.y = state.player_y
                        self.player.hitbox.center = self.player.rect.center
                        self.is_time_traveling = True
                        if self.enemy_future:
                            snapshot = self.enemy_future.pop()
                            self.enemy_history.append(snapshot)
                            self._restore_enemies(snapshot)

                else:
                    self.is_time_traveling = False

    def draw_time_travel_ui(self):
        font_small = pygame.font.Font(None, 18)
        panel = pygame.Rect(WIDTH - 244, 10, 234, 58)
        overlay = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 174))
        pygame.draw.rect(overlay, (74, 92, 124, 210), overlay.get_rect(), width=2, border_radius=8)
        self.display_surface.blit(overlay, panel)

        if not self.connected:
            if self.is_time_traveling:
                font_large = pygame.font.Font(None, 48)
                text = font_large.render("TIME TRAVELING", True, (255, 100, 100))
                rect = text.get_rect(center=(WIDTH // 2, 50))
                self.display_surface.blit(text, rect)

            info = f"History: {self.time_travel.get_history_size()} | Future: {self.time_travel.get_future_size()}"
            text = font_small.render(info, True, (255, 255, 255))
            self.display_surface.blit(text, (panel.x + 10, panel.y + 10))

            hint = "R: Rewind | F: Replay"
            text = font_small.render(hint, True, (200, 200, 200))
            self.display_surface.blit(text, (panel.x + 10, panel.y + 32))
        else:
            text = font_small.render("Replay off: multiplayer", True, (150, 150, 150))
            self.display_surface.blit(text, (panel.x + 10, panel.y + 21))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self, events):
        """Main update loop"""
        self.handle_events(events)
        self.handle_time_travel_input(events)
        self.handle_enemy_debug_input(events)

        self.update_network()

        # Update player and remote players
        if not self.game_over:
            self.player.update()
            self.collect_fruits()
            self.handle_hazards()
        for other_player in self.other_players.values():
            if not self.game_over:
                other_player.update()

        # Update enemies; freeze them while time-traveling
        if not self.is_time_traveling and not self.game_over:
            for enemy in list(self.enemies):
                enemy.enemy_update(self.player)   # set combat AI state first
            self.enemies.update()                  # then move/animate/check death
            self.player_attack_logic()             # weapon collisions
            self.check_round_end()

        # Draw (Y-sorted; custom_draw does NOT call update())
        #self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.offset.x = self.player.rect.centerx - self.visible_sprites.half_width
        self.visible_sprites.offset.y = self.player.rect.centery - self.visible_sprites.half_height

        for sprite in self.floor_sprites:
            offset_pos = sprite.rect.topleft - self.visible_sprites.offset
            self.display_surface.blit(sprite.image, offset_pos)

        self.visible_sprites.custom_draw(self.player)
        
        if not self.game_over:
            self.record_player_state()

        self.draw_names()
        self.draw_status()
        self.draw_time_travel_ui()
        self.draw_enemy_debug()

        if self.inventory_ui.active:
            self.inventory_ui.draw(self.display_surface)

    # ------------------------------------------------------------------
    # Enemy debug
    # ------------------------------------------------------------------

    def handle_enemy_debug_input(self, events):
        """Handle enemy debug controls (Lab 5)."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.show_enemy_debug = not self.show_enemy_debug
                    status = "ON" if self.show_enemy_debug else "OFF"
                    count = len(self.enemies)
                    print(f"Enemy debug view: {status} ({count} enemies active)")

                elif event.key == pygame.K_m:
                    reset_count = 0
                    for enemy in self.enemies:
                        enemy.reset_patrol()
                        reset_count += 1
                    print(f"Reset {reset_count} enemy patrols")

    def draw_enemy_debug(self):
        """Draw enemy debug information (Lab 5)."""
        if not self.show_enemy_debug:
            return

        if len(self.enemies) == 0:
            font = pygame.font.Font(None, 24)
            text = font.render("No patrol enemies are active.", True, (255, 255, 100))
            self.display_surface.blit(text, (10, 160))
            return

        y_offset = 160
        for enemy in self.enemies:
            status = enemy.get_debug_status()
            font = pygame.font.Font(None, 20)
            text = font.render(status, True, (255, 255, 100))
            self.display_surface.blit(text, (10, y_offset))
            y_offset += 25

            enemy.draw_debug_info(self.display_surface,
                                  (self.visible_sprites.offset.x, self.visible_sprites.offset.y))

        instructions = [
            "Enemy Debug Controls:",
            "N: Toggle debug view",
            "M: Reset all patrols"
        ]
        font = pygame.font.Font(None, 18)
        for i, instruction in enumerate(instructions):
            color = (200, 200, 200) if i == 0 else (150, 150, 150)
            text = font.render(instruction, True, color)
            self.display_surface.blit(text, (WIDTH - 200, 10 + i * 20))


class YSortCameraGroup(pygame.sprite.Group):
    """Camera that follows player and sorts sprites by Y position"""

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        """Draw sprites sorted by Y position"""
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def offset_from_world(self, world_pos):
        """Convert world position to screen position"""
        return pygame.math.Vector2(world_pos) - self.offset
