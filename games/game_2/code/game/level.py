"""
level.py - Game level with character classes and networking

Integrated version combining lab-03 and project-01
"""

import os
import pygame
from settings import *
from tile import Tile
from character import Character
from subcharacter import get_all_character_classes
from network_client import NetworkClient
from inventory_ui import InventoryUI
from item import create_example_items
from time_travel import TimeTravel
from enemy import Enemy, ENEMY_SPAWN_DATA
from datastructures.patrol_path import PatrolPath
from weapon import Weapon as WeaponSprite
from map_loader import load_layer
from support import import_csv_layout
import sys

class Level:
    def __init__(self, player_name, character_class, server_host='localhost', server_port=8080, serializer='text'):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        # Sprite group setup
        self.floor_sprites = pygame.sprite.Group()
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # Combat sprite groups
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # Store character class for player creation
        self.character_class = character_class

        # Sprite setup
        self.create_map()

        # Network setup with serializer
        self.network = NetworkClient(player_name, server_host, server_port, serializer)
        self.connected = self.network.connect()

        # Track other players
        self.other_players = {}  # player_id -> Character sprite

        # Font for displaying names
        self.font = pygame.font.Font(None, 24)

        # Connection status
        self.connection_status = "Connecting..."

        # Inventory UI
        self.inventory_ui = InventoryUI(self.player.inventory)
        self.inventory_ui.character = self.player

        # Add starting items for testing
        self.add_starting_items()

        # Time travel system (Lab 4)
        self.time_travel = TimeTravel(max_history=180)
        self.is_time_traveling = False
        self.enemy_history = []
        self.enemy_future  = []

        # Enemy system (Lab 5)
        self.enemies = pygame.sprite.Group()
        self.create_enemies()

        # Debug mode for showing enemy paths
        self.show_enemy_debug = False

        # ---------------------------------------------------------------
        # Leaderboard / scoring
        # ---------------------------------------------------------------
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        self._game_over_time = 0
        self._score_recorded = False

        # Fonts for the end screen / HUD
        self._go_font_large = pygame.font.Font(None, 80)
        self._go_font_med   = pygame.font.Font(None, 48)
        self._go_font_small = pygame.font.Font(None, 32)

        # End-screen buttons
        btn_w, btn_h = 260, 55
        cx = WIDTH // 2
        self._btn_play_again = pygame.Rect(cx - btn_w - 20, HEIGHT // 2 + 120, btn_w, btn_h)
        self._btn_arcade     = pygame.Rect(cx + 20,          HEIGHT // 2 + 120, btn_w, btn_h)
        self._end_action     = None   # 'restart' | 'arcade' | None

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def _on_enemy_death(self):
        """Fired by Enemy.check_death() — increment kill counter."""
        self.score += 1

    def _active_time_str(self):
        """Return elapsed play time as MM:SS."""
        if self.game_over:
            elapsed_ms = self._game_over_time - self.start_time
        else:
            elapsed_ms = pygame.time.get_ticks() - self.start_time
        total_sec = elapsed_ms // 1000
        return f"{total_sec // 60:02d}:{total_sec % 60:02d}"

    # ------------------------------------------------------------------
    # End screen
    # ------------------------------------------------------------------

    def _check_game_over(self):
        """Trigger game-over state the moment the player runs out of HP."""
        if not self.game_over and self.player.hp <= 0:
            self.game_over = True
            self._game_over_time = pygame.time.get_ticks()

    def draw_end_screen(self, events):
        """
        Draw the full-screen game-over overlay.
        Returns 'restart', 'arcade', or None.
        """
        # Semi-transparent dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.display_surface.blit(overlay, (0, 0))

        cx = WIDTH // 2

        # Title
        title = self._go_font_large.render("GAME OVER", True, (220, 60, 60))
        self.display_surface.blit(title, title.get_rect(center=(cx, HEIGHT // 2 - 180)))

        # Score
        score_surf = self._go_font_med.render(
            f"Enemies Defeated:  {self.score}", True, (255, 215, 0))
        self.display_surface.blit(score_surf, score_surf.get_rect(center=(cx, HEIGHT // 2 - 100)))

        # Active time
        time_surf = self._go_font_med.render(
            f"Active Time:  {self._active_time_str()}", True, (180, 220, 255))
        self.display_surface.blit(time_surf, time_surf.get_rect(center=(cx, HEIGHT // 2 - 45)))

        # Leaderboard header
        lb_hdr = self._go_font_small.render("— Session Leaderboard —", True, (200, 200, 200))
        self.display_surface.blit(lb_hdr, lb_hdr.get_rect(center=(cx, HEIGHT // 2 + 20)))

        # Persist leaderboard on the class so it survives Level restarts
        if not hasattr(Level, '_leaderboard'):
            Level._leaderboard = []

        if not self._score_recorded:
            Level._leaderboard.append({
                'name':  self._player_label(),
                'score': self.score,
                'time':  self._active_time_str(),
            })
            Level._leaderboard.sort(key=lambda e: e['score'], reverse=True)
            self._score_recorded = True

        for rank, entry in enumerate(Level._leaderboard[:5], 1):
            colour = (255, 215, 0) if rank == 1 else (200, 200, 200)
            row = self._go_font_small.render(
                f"#{rank}  {entry['name']}   {entry['score']} kills   {entry['time']}",
                True, colour
            )
            self.display_surface.blit(row, row.get_rect(center=(cx, HEIGHT // 2 + 20 + rank * 34)))

        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        clicked   = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        for rect, label, action, hover_col, normal_col in [
            (self._btn_play_again, "Play Again",       'restart', (60, 160, 60),  (35, 100, 35)),
            (self._btn_arcade,     "Return to Arcade", 'arcade',  (160, 60, 60),  (100, 35, 35)),
        ]:
            hovered = rect.collidepoint(mouse_pos)
            bg = hover_col if hovered else normal_col
            pygame.draw.rect(self.display_surface, bg,            rect, border_radius=8)
            pygame.draw.rect(self.display_surface, (255,255,255), rect, 2, border_radius=8)
            lbl = self._go_font_small.render(label, True, (255, 255, 255))
            self.display_surface.blit(lbl, lbl.get_rect(center=rect.center))
            if clicked and hovered:
                return action

        return None

    def _player_label(self):
        """Display name for the leaderboard."""
        try:
            return self.network.player_name
        except Exception:
            return "Player"

    # ------------------------------------------------------------------
    # Live score HUD
    # ------------------------------------------------------------------

    def _draw_score_hud(self):
        """Kill counter + timer in the top-right corner."""
        surf = self._go_font_small.render(
            f"Kills: {self.score}   Time: {self._active_time_str()}",
            True, (255, 215, 0)
        )
        self.display_surface.blit(surf, (WIDTH - surf.get_width() - 12, 10))

    # ------------------------------------------------------------------
    # Map creation
    # ------------------------------------------------------------------

    def create_map(self):
        """Create the game map from CSV layers and spawn the player."""
        map_dir = os.path.join(os.path.dirname(__file__), 'map')
        floorblocks_path = os.path.join(map_dir, 'map_FloorBlocks.csv')
        grass_path = os.path.join(map_dir, 'map_Grass.csv')
        objects_path = os.path.join(map_dir, 'map_Objects.csv')

        grass_layout = import_csv_layout(grass_path)
        self.map_rows = len(grass_layout)
        self.map_cols = len(grass_layout[0]) if grass_layout else 0
        self.map_pixel_width = self.map_cols * TILESIZE
        self.map_pixel_height = self.map_rows * TILESIZE

        self.ground_texture = self._load_tilemap_image('ground.png', alpha=False)
        terrain_tiles, object_tiles = self._build_tile_libraries()
        invisible_tile = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)

        for (row, col), _ in load_layer(floorblocks_path).items():
            Tile((col * TILESIZE, row * TILESIZE), [self.obstacle_sprites], 'boundary', invisible_tile)

        for (row, col), tile_id in load_layer(grass_path).items():
            surface = terrain_tiles.get(tile_id)
            if surface is None:
                continue
            Tile((col * TILESIZE, row * TILESIZE), [self.floor_sprites], 'grass', surface)

        for (row, col), tile_id in load_layer(objects_path).items():
            surface = object_tiles.get(tile_id)
            if surface is None:
                continue
            Tile((col * TILESIZE, row * TILESIZE), [self.visible_sprites, self.obstacle_sprites], 'object', surface)

        spawn_x = PLAYER_SPAWN_TILE[0] * TILESIZE - (96 - TILESIZE) // 2
        spawn_y = PLAYER_SPAWN_TILE[1] * TILESIZE - (96 - TILESIZE) // 2
        self.player = self.character_class(
            (spawn_x, spawn_y),
            [self.visible_sprites],
            self.obstacle_sprites,
            is_local=True
        )
        self.player.create_attack_callback = self.create_attack
        self.player.destroy_attack_callback = self.destroy_attack

    def _build_tile_libraries(self):
        terrain_tiles = {
            0: self._load_tilemap_image('asphalt.png'),
            1: self._load_tilemap_image('city_pavers.png'),
            2: self._load_tilemap_image('sand.png'),
            3: self._load_tilemap_image('canyon.png'),
            4: self._load_tilemap_image('scrub.png'),
            5: self._load_tilemap_image('oasis.png'),
            6: self._load_tilemap_image('steel.png'),
            7: self._load_tilemap_image('hazard.png'),
            8: self._load_tilemap_image('road_marks_h.png'),
            9: self._load_tilemap_image('road_marks_v.png'),
        }
        object_tiles = {
            0: self._load_tilemap_image('barricade.png'),
            1: self._load_tilemap_image('building.png'),
            2: self._load_tilemap_image('cactus.png'),
            3: self._load_tilemap_image('rock_spire.png'),
            4: self._load_tilemap_image('scrap_pile.png'),
            5: self._load_tilemap_image('grandstand.png'),
        }
        return terrain_tiles, object_tiles

    def _load_tilemap_image(self, filename, alpha=True):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        path = os.path.join(project_root, 'graphics', 'tilemap', filename)
        image = pygame.image.load(path)
        return image.convert_alpha() if alpha else image.convert()

    def add_starting_items(self):
        print("Adding starting items to inventory...")
        for item in create_example_items():
            success = self.player.inventory.add_item(item)
            if success:
                print(f"  Added: {item.name}")
            else:
                print(f"  Inventory full! Couldn't add: {item.name}")
        print(f"Total items: {len(self.player.inventory.items)}")
        for item in self.player.inventory.items:
            if item.item_type == 'weapon':
                self.player.equipped_weapon = item
                print(f"Auto-equipped: {item.name}")
                break
        print("Press 'I' to open inventory and switch weapons. SPACE to attack!")

    def create_enemies(self):
        """Create enemies with on_death callback for kill scoring."""
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
                        on_death=self._on_enemy_death,   # <-- score callback
                    )

                    if data["patrol_type"] == "random":
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
        except Exception as e:
            print(f"Error setting up enemies: {e}")

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def create_attack(self):
        self.current_attack = WeaponSprite(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        for attack_sprite in list(self.attack_sprites):
            for enemy in pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False):
                was_alive = enemy.health > 0
                enemy.get_damage(self.player)
                if was_alive and enemy.health <= 0:
                    self.player.exp += enemy.exp

    def damage_player(self, amount):
        self.player.take_damage(amount)

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def update_network(self):
        if not self.connected:
            self.connection_status = "Disconnected"
            return

        character_type = self.player.character_name.lower()
        status = self.player.status.replace("_idle", "").replace("_attack", "")
        self.network.send_update(self.player.rect.x, self.player.rect.y, character_type, status)

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
                    if not character_type:
                        continue
                    all_classes = get_all_character_classes()
                    CharClass = None
                    for cls in all_classes:
                        if cls.get_display_name().lower() == character_type:
                            CharClass = cls
                            break
                    if CharClass is None:
                        CharClass = Character
                    other_player = CharClass(
                        (data['x'], data['y']),
                        [self.visible_sprites],
                        self.obstacle_sprites,
                        player_id=player_id,
                        is_local=False
                    )
                    other_player.name = data['name']
                    self.other_players[player_id] = other_player
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

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            self.inventory_ui.handle_event(event, self.player)

    def draw_names(self):
        if self.network.my_player_id is not None:
            name_text = f"{self.network.player_name} ({self.player.character_name})"
            name_surface = self.font.render(name_text, True, (0, 255, 0))
            name_rect = name_surface.get_rect(
                center=(self.player.rect.centerx, self.player.rect.top - 10))
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

        for other_player in self.other_players.values():
            name_surface = self.font.render(other_player.name, True, (100, 100, 255))
            name_rect = name_surface.get_rect(
                center=(other_player.rect.centerx, other_player.rect.top - 10))
            offset_pos = self.visible_sprites.offset_from_world(name_rect.topleft)
            self.display_surface.blit(name_surface, offset_pos)

    def draw_status(self):
        status_color = (0, 255, 0) if self.connected else (255, 100, 100)
        self.display_surface.blit(
            self.font.render(self.connection_status, True, status_color), (10, 10))
        self.display_surface.blit(
            self.font.render("I: Inventory | SPACE: Attack", True, (255, 255, 255)), (10, 40))

        bar_rect  = pygame.Rect(10, 70, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        ratio     = max(0.0, self.player.hp / max(1, self.player.max_hp))
        fill_rect = pygame.Rect(10, 70, int(HEALTH_BAR_WIDTH * ratio), BAR_HEIGHT)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR,     bar_rect)
        pygame.draw.rect(self.display_surface, HEALTH_COLOR,    fill_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bar_rect, 2)
        self.display_surface.blit(
            self.font.render(f"HP {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255)),
            (10 + HEALTH_BAR_WIDTH + 8, 70))

        self.display_surface.blit(
            self.font.render(f"XP: {self.player.exp}", True, (255, 215, 0)), (10, 100))

        if self.player.equipped_weapon:
            w = self.player.equipped_weapon
            msg = f"Weapon: {w.name}  (+{w.attack_bonus} atk)"
            color = (255, 200, 100)
        else:
            msg   = "Weapon: none  (open I → select weapon → Equip)"
            color = (150, 150, 150)
        self.display_surface.blit(self.font.render(msg, True, color), (10, 125))

    # ------------------------------------------------------------------
    # Time travel
    # ------------------------------------------------------------------

    def _snapshot_enemies(self):
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
            self.player.vulnerable = True

    def record_player_state(self):
        if not self.is_time_traveling and not self.connected:
            prev_size = self.time_travel.get_history_size()
            self.time_travel.record_state(self.player.rect.x, self.player.rect.y)
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
        font_small = pygame.font.Font(None, 24)
        if not self.connected:
            if self.is_time_traveling:
                font_large = pygame.font.Font(None, 48)
                text = font_large.render("⏪ TIME TRAVELING", True, (255, 100, 100))
                rect = text.get_rect(center=(WIDTH // 2, 50))
                self.display_surface.blit(text, rect)
            info = f"History: {self.time_travel.get_history_size()} | Future: {self.time_travel.get_future_size()}"
            text = font_small.render(info, True, (255, 255, 255))
            self.display_surface.blit(text, (10, 100))
            hint = "R: Rewind | F: Replay"
            text = font_small.render(hint, True, (200, 200, 200))
            self.display_surface.blit(text, (10, 130))
        else:
            text = font_small.render("Time travel disabled (multiplayer)", True, (150, 150, 150))
            self.display_surface.blit(text, (10, 100))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self, events):
        """Main update and draw loop."""
        self.handle_events(events)
        self.handle_time_travel_input(events)
        self.handle_enemy_debug_input(events)

        # Check whether player just died
        self._check_game_over()

        if self.game_over:
            # Draw world underneath, then overlay end screen
            self.visible_sprites.custom_draw(
                self.player,
                floor_sprites=self.floor_sprites,
                ground_surface=self.ground_texture,
                map_size=(self.map_pixel_width, self.map_pixel_height)
            )
            action = self.draw_end_screen(events)
            if action:
                self._end_action = action
            return   # skip normal updates while end screen is showing

        # Normal gameplay
        self.update_network()

        self.player.update()
        for other_player in self.other_players.values():
            other_player.update()

        if not self.is_time_traveling:
            for enemy in list(self.enemies):
                enemy.enemy_update(self.player)
            self.enemies.update()
            self.player_attack_logic()

        self.visible_sprites.custom_draw(
            self.player,
            floor_sprites=self.floor_sprites,
            ground_surface=self.ground_texture,
            map_size=(self.map_pixel_width, self.map_pixel_height)
        )

        self.record_player_state()

        self.draw_names()
        self.draw_status()
        self.draw_time_travel_ui()
        self.draw_enemy_debug()
        self._draw_score_hud()   # live kill counter top-right

        if self.inventory_ui.active:
            self.inventory_ui.draw(self.display_surface)

    # ------------------------------------------------------------------
    # Enemy debug
    # ------------------------------------------------------------------

    def handle_enemy_debug_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.show_enemy_debug = not self.show_enemy_debug
                    status = "ON" if self.show_enemy_debug else "OFF"
                    print(f"Enemy debug view: {status} ({len(self.enemies)} enemies active)")
                elif event.key == pygame.K_m:
                    for enemy in self.enemies:
                        enemy.reset_patrol()
                    print(f"Reset {len(self.enemies)} enemy patrols")

    def draw_enemy_debug(self):
        if not self.show_enemy_debug:
            return
        if len(self.enemies) == 0:
            font = pygame.font.Font(None, 24)
            text = font.render("No patrol enemies - implement Waypoint and PatrolPath!", True, (255, 255, 100))
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

        instructions = ["Enemy Debug Controls:", "N: Toggle debug view", "M: Reset all patrols"]
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

    def custom_draw(self, player, floor_sprites=None, ground_surface=None, map_size=(0, 0)):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        if ground_surface is not None:
            self.draw_ground(ground_surface, map_size)

        if floor_sprites is not None:
            for sprite in floor_sprites:
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def draw_ground(self, ground_surface, map_size):
        map_width, map_height = map_size
        tile_w, tile_h = ground_surface.get_size()
        start_x = int(self.offset.x // tile_w) * tile_w
        start_y = int(self.offset.y // tile_h) * tile_h
        end_x = max(map_width, int(self.offset.x + self.display_surface.get_width()) + tile_w)
        end_y = max(map_height, int(self.offset.y + self.display_surface.get_height()) + tile_h)

        for world_y in range(start_y, end_y, tile_h):
            for world_x in range(start_x, end_x, tile_w):
                screen_pos = pygame.math.Vector2(world_x, world_y) - self.offset
                self.display_surface.blit(ground_surface, screen_pos)

    def offset_from_world(self, world_pos):
        return pygame.math.Vector2(world_pos) - self.offset
