"""
level.py - Game level with character classes and networking
 
Integrated version combining lab-03 and project-01
"""
 
import pygame
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
 
class Level:
    def __init__(self, player_name, character_class, server_host='localhost', server_port=8080, serializer='text'):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()
        self.world_rect = pygame.Rect(0, 0, len(WORLD_MAP[0]) * TILESIZE, len(WORLD_MAP) * TILESIZE)
 
        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.ground_sprites = pygame.sprite.Group()
        self.object_sprites = pygame.sprite.Group()
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
        self.enemy_respawn_delay_ms = 3500
        self.enemy_respawn_queue = {}
        self.create_enemies()
 
        # Debug mode for showing enemy paths
        self.show_enemy_debug = False

        # Arcade scoring/timer state. Score counts defeated enemies, and the
        # countdown ends the run cleanly for the launcher result pipeline.
        self.score = 0
        self.game_duration_seconds = 60
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        self._game_over_time = 0
        self.outcome = "Finished"
        self.result = "lose"
        self._end_action = None
        self._go_font_large = pygame.font.Font(None, 80)
        self._go_font_med = pygame.font.Font(None, 48)
        self._go_font_small = pygame.font.Font(None, 32)
        button_width, button_height = 260, 55
        center_x = WIDTH // 2
        self._btn_play_again = pygame.Rect(center_x - button_width - 20, HEIGHT // 2 + 120, button_width, button_height)
        self._btn_arcade = pygame.Rect(center_x + 20, HEIGHT // 2 + 120, button_width, button_height)
 
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
 
    def _load_tilesets_from_tmx(self, tmx_dir):
        """Parse the TMX file in tmx_dir and return a combined tile_id -> Surface dict.
 
        The TMX format lists every <tileset> with a firstgid and a source .tsx file
        (or inline image).  Each tileset's tiles are numbered starting at firstgid.
        We slice each tileset image into TILESIZE×TILESIZE cells and offset the
        local tile index by firstgid so tile IDs match what the CSV layers export.
 
        Falls back to an empty dict if pytmx is unavailable or the TMX is missing.
        """
        import os, xml.etree.ElementTree as ET
 
        tmx_files = [f for f in os.listdir(tmx_dir) if f.endswith('.tmx')] if os.path.isdir(tmx_dir) else []
        if not tmx_files:
            print(f"[Map] No .tmx file found in {tmx_dir}, falling back to ground.png only")
            return {}
 
        tmx_path = os.path.join(tmx_dir, tmx_files[0])
        print(f"[Map] Loading tilesets from {tmx_path}")
 
        combined = {}
        try:
            tree = ET.parse(tmx_path)
            root = tree.getroot()
 
            for tileset_el in root.findall('tileset'):
                firstgid = int(tileset_el.get('firstgid', 1))
 
                # Tileset may be external (.tsx) or inline
                source = tileset_el.get('source')
                if source:
                    tsx_path = os.path.join(tmx_dir, source)
                    try:
                        tsx_tree = ET.parse(tsx_path)
                        tileset_el = tsx_tree.getroot()
                    except Exception as e:
                        print(f"[Map] Could not read {tsx_path}: {e}")
                        continue
 
                image_el = tileset_el.find('image')
                if image_el is None:
                    continue
 
                img_src = image_el.get('source', '')
                # Resolve relative to tmx_dir
                img_path = os.path.normpath(os.path.join(tmx_dir, img_src))
 
                tiles = self._load_tileset(img_path)
                if not tiles:
                    print(f"[Map] Could not load tileset image: {img_path}")
                    continue
 
                # Re-key with global tile IDs (firstgid offset)
                for local_id, surf in tiles.items():
                    global_id = firstgid + local_id
                    combined[global_id] = surf
 
                print(f"[Map] Tileset '{os.path.basename(img_path)}': "
                      f"{len(tiles)} tiles, firstgid={firstgid}")
 
        except Exception as e:
            print(f"[Map] TMX parse error: {e}")
 
        return combined
 
    def _find_player_spawn_from_tmx(self, tmx_dir):
        """Look for a Tiled object layer named 'Spawn' with an object named 'Player'.
 
        Returns (pixel_x, pixel_y) if found, else None so the WORLD_MAP fallback is used.
        """
        import os, xml.etree.ElementTree as ET
 
        tmx_files = [f for f in os.listdir(tmx_dir) if f.endswith('.tmx')] if os.path.isdir(tmx_dir) else []
        if not tmx_files:
            return None
 
        tmx_path = os.path.join(tmx_dir, tmx_files[0])
        try:
            root = ET.parse(tmx_path).getroot()
            for og in root.findall('objectgroup'):
                for obj in og.findall('object'):
                    if obj.get('name', '').lower() == 'player':
                        # Tiled stores pixel coords; snap to tile grid
                        px = int(float(obj.get('x', 0)))
                        py = int(float(obj.get('y', 0)))
                        # Align to tile grid
                        px = (px // TILESIZE) * TILESIZE
                        py = (py // TILESIZE) * TILESIZE
                        print(f"[Map] Player spawn from TMX: tile ({px//TILESIZE}, {py//TILESIZE})")
                        return (px, py)
        except Exception as e:
            print(f"[Map] Could not read player spawn from TMX: {e}")
        return None
 
    def _load_tmx_layers(self, tmx_path):
        """Read tile layers from the group's original Tiled town map."""
        import xml.etree.ElementTree as ET

        root = ET.parse(tmx_path).getroot()
        width = int(root.get("width", 0))
        height = int(root.get("height", 0))
        layers = []

        for layer_el in root.findall("layer"):
            data_el = layer_el.find("data")
            if data_el is None or data_el.get("encoding") != "csv":
                continue
            raw_values = data_el.text.replace("\n", "").split(",")
            gids = [int(value) for value in raw_values if value.strip()]
            if len(gids) != width * height:
                print(f"[Map] Skipping malformed layer {layer_el.get('name')}: {len(gids)} cells")
                continue
            layers.append({
                "name": layer_el.get("name", ""),
                "width": width,
                "height": height,
                "gids": gids,
            })

        return width, height, layers

    def _is_walkable_tile(self, tile_x, tile_y):
        return (
            0 <= tile_x < getattr(self, "map_width_tiles", 0)
            and 0 <= tile_y < getattr(self, "map_height_tiles", 0)
            and (tile_x, tile_y) not in getattr(self, "blocked_tiles", set())
        )

    def _nearest_walkable_tile(self, preferred_tile, min_player_distance=0):
        """Find a nearby open town-map tile for player/enemy placement."""
        preferred_x, preferred_y = preferred_tile
        player_tile = None
        if hasattr(self, "player"):
            player_tile = pygame.math.Vector2(
                self.player.rect.centerx / TILESIZE,
                self.player.rect.centery / TILESIZE,
            )

        best = None
        best_score = None
        for tile_x, tile_y in getattr(self, "walkable_tiles", []):
            if player_tile is not None and min_player_distance:
                if pygame.math.Vector2(tile_x, tile_y).distance_to(player_tile) < min_player_distance:
                    continue
            score = abs(tile_x - preferred_x) + abs(tile_y - preferred_y)
            if best_score is None or score < best_score:
                best = (tile_x, tile_y)
                best_score = score

        return best or preferred_tile

    def _blockify_town_tile(self, surface, is_blocked=False):
        """Keep the original art, but add a light tile edge for a block-map feel."""
        tile = surface.copy()
        overlay = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        edge_color = (0, 0, 0, 42) if is_blocked else (0, 0, 0, 24)
        highlight_color = (255, 255, 255, 18)
        pygame.draw.rect(overlay, edge_color, overlay.get_rect(), 2)
        pygame.draw.line(overlay, highlight_color, (1, 1), (TILESIZE - 2, 1), 1)
        pygame.draw.line(overlay, highlight_color, (1, 1), (1, TILESIZE - 2), 1)
        tile.blit(overlay, (0, 0))
        return tile

    def create_map(self):
        """Create the original road/store town map with a separate collision layer."""
        import os

        tmx_dir = os.path.join('..', '..', 'graphics', 'tilemap')
        tmx_path = os.path.join(tmx_dir, 'Map.tmx')

        all_tiles = self._load_tilesets_from_tmx(tmx_dir)
        if not all_tiles:
            raise RuntimeError("[Map] Could not load Game 3 town tilesets")

        map_width, map_height, layers = self._load_tmx_layers(tmx_path)
        self.map_width_tiles = map_width
        self.map_height_tiles = map_height
        self.world_rect = pygame.Rect(0, 0, map_width * TILESIZE, map_height * TILESIZE)
        self.blocked_tiles = set()

        # Draw the group's original visual layers first. Collision is handled
        # by invisible blockers so the map art can never cover the player.
        blocked_layer_names = {"FloorBlocks", "Objects"}
        for layer in layers:
            layer_name = layer["name"]
            visual_group = self.ground_sprites if layer_name == "Grass" else self.object_sprites
            for index, gid in enumerate(layer["gids"]):
                if gid == 0:
                    continue
                tile_x = index % map_width
                tile_y = index // map_width
                x = tile_x * TILESIZE
                y = tile_y * TILESIZE
                surface = all_tiles.get(gid)
                is_blocked = layer_name in blocked_layer_names
                if surface is not None:
                    Tile((x, y), [visual_group], 'grass', self._blockify_town_tile(surface, is_blocked))
                if is_blocked:
                    self.blocked_tiles.add((tile_x, tile_y))

        for tile_x, tile_y in self.blocked_tiles:
            Tile((tile_x * TILESIZE, tile_y * TILESIZE), [self.obstacle_sprites], 'boundary')

        self.walkable_tiles = [
            (x, y)
            for y in range(map_height)
            for x in range(map_width)
            if (x, y) not in self.blocked_tiles
        ]

        spawn_pos = self._find_player_spawn_from_tmx(tmx_dir)
        if spawn_pos is None:
            # The current TMX has no object-layer spawn marker. Start near the
            # central road intersection so the original town layout is visible.
            spawn_tile = (30, 16)
        else:
            spawn_tile = (spawn_pos[0] // TILESIZE, spawn_pos[1] // TILESIZE)

        if not self._is_walkable_tile(*spawn_tile):
            spawn_tile = self._nearest_walkable_tile(spawn_tile)

        self.player = self.character_class(
            (spawn_tile[0] * TILESIZE, spawn_tile[1] * TILESIZE),
            [self.visible_sprites],
            self.obstacle_sprites,
            is_local=True
        )
        self.player.create_attack_callback = self.create_attack
        self.player.destroy_attack_callback = self.destroy_attack

        print(
            f"[Map] Loaded original Game 3 town map: "
            f"{map_width}x{map_height}, {len(self.blocked_tiles)} blocked tiles."
        )

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
                    self._spawn_enemy(data)
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

    def _spawn_enemy(self, data):
        """Spawn one enemy from ENEMY_SPAWN_DATA and attach it to all gameplay groups."""
        spawn_x, spawn_y = self._safe_enemy_spawn(data)
        combat_kwargs = dict(
            health=data.get("health", 60),
            exp=data.get("exp", 30),
            attack_damage=data.get("attack_damage", 10),
            notice_radius=data.get("notice_radius", 200),
            attack_radius=data.get("attack_radius", 60),
            damage_player=self.damage_player,
        )

        if data["patrol_type"] == "random":
            enemy = Enemy(
                name=data["name"],
                start_x=spawn_x,
                start_y=spawn_y,
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
                if not self._is_walkable_tile(x, y):
                    x, y = self._nearest_walkable_tile((x, y))
                patrol_path.add_waypoint(x, y, wait_time=1.0)
            enemy = Enemy(
                name=data["name"],
                start_x=spawn_x,
                start_y=spawn_y,
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
        return enemy

    def _safe_enemy_spawn(self, data):
        """Spawn only on walkable town-map tiles and away from the player."""
        spawn_x, spawn_y = data["spawn"]
        if not hasattr(self, "player"):
            return spawn_x, spawn_y
        player_tile = pygame.math.Vector2(self.player.rect.centerx / TILESIZE, self.player.rect.centery / TILESIZE)
        candidates = [data["spawn"], *data.get("waypoints", [])]
        for candidate in candidates:
            if not self._is_walkable_tile(candidate[0], candidate[1]):
                continue
            pos = pygame.math.Vector2(candidate[0], candidate[1])
            if pos.distance_to(player_tile) >= 4:
                return candidate
        return self._nearest_walkable_tile((spawn_x, spawn_y), min_player_distance=4)

    def update_enemy_respawns(self):
        """Respawn defeated enemies after a short delay, away from the player."""
        now = pygame.time.get_ticks()
        alive_names = {enemy.name for enemy in self.enemies}
        for data in ENEMY_SPAWN_DATA:
            name = data["name"]
            if name not in alive_names and name not in self.enemy_respawn_queue:
                self.enemy_respawn_queue[name] = now + self.enemy_respawn_delay_ms

        for name, due_at in list(self.enemy_respawn_queue.items()):
            if now < due_at:
                continue
            data = next((item for item in ENEMY_SPAWN_DATA if item["name"] == name), None)
            if data is None:
                self.enemy_respawn_queue.pop(name, None)
                continue
            self._spawn_enemy(data)
            self.enemy_respawn_queue.pop(name, None)

    def clamp_player_to_world(self):
        """Stop the player from leaving the playable map rectangle."""
        if not hasattr(self, "player"):
            return
        self.player.hitbox.clamp_ip(self.world_rect)
        self.player.rect.center = self.player.hitbox.center
 
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
                    self.score += 1
                    self.player.exp += enemy.exp   # award XP exactly once on kill
 
    def damage_player(self, amount):
        """Called by enemies when they land an attack."""
        self.player.take_damage(amount)

    # ------------------------------------------------------------------
    # Arcade score/timer helpers
    # ------------------------------------------------------------------

    def elapsed_seconds(self):
        end_ticks = self._game_over_time if self.game_over else pygame.time.get_ticks()
        return max(0, (end_ticks - self.start_time) // 1000)

    def remaining_seconds(self):
        return max(0, self.game_duration_seconds - self.elapsed_seconds())

    def _format_seconds(self, seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def _finish_game(self, outcome):
        if self.game_over:
            return
        self.game_over = True
        self._game_over_time = pygame.time.get_ticks()
        self.outcome = outcome
        self.result = "win" if outcome == "Time Up" and self.score > 0 else "lose"

    def _check_game_over(self):
        if self.player.hp <= 0:
            self._finish_game("Game Over")
        elif self.remaining_seconds() <= 0:
            self._finish_game("Time Up")

    def _draw_score_timer_hud(self):
        text = self._go_font_small.render(
            f"Score: {self.score}   Time: {self._format_seconds(self.remaining_seconds())}",
            True,
            (255, 215, 0),
        )
        padding = 10
        panel = pygame.Rect(WIDTH - text.get_width() - 32, 10, text.get_width() + 20, text.get_height() + 10)
        panel_surf = pygame.Surface(panel.size, pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 150))
        self.display_surface.blit(panel_surf, panel.topleft)
        pygame.draw.rect(self.display_surface, (255, 215, 0), panel, 2, border_radius=6)
        self.display_surface.blit(text, (panel.x + padding, panel.y + 5))

    def draw_end_screen(self, events):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        self.display_surface.blit(overlay, (0, 0))

        center_x = WIDTH // 2
        title = self._go_font_large.render("RUN COMPLETE" if self.outcome == "Time Up" else "GAME OVER", True, (255, 215, 0))
        self.display_surface.blit(title, title.get_rect(center=(center_x, HEIGHT // 2 - 175)))

        score_text = self._go_font_med.render(f"Enemies Defeated: {self.score}", True, (180, 255, 180))
        self.display_surface.blit(score_text, score_text.get_rect(center=(center_x, HEIGHT // 2 - 95)))

        time_text = self._go_font_med.render(f"Time: {self._format_seconds(self.elapsed_seconds())}", True, (180, 220, 255))
        self.display_surface.blit(time_text, time_text.get_rect(center=(center_x, HEIGHT // 2 - 40)))

        reason_text = self._go_font_small.render(f"Result: {self.outcome}", True, (230, 230, 230))
        self.display_surface.blit(reason_text, reason_text.get_rect(center=(center_x, HEIGHT // 2 + 20)))

        mouse_pos = pygame.mouse.get_pos()
        clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)
        key_restart = any(event.type == pygame.KEYDOWN and event.key == pygame.K_r for event in events)
        key_arcade = any(event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE for event in events)

        for rect, label, action, hover_color, normal_color in [
            (self._btn_play_again, "Restart", "restart", (55, 150, 75), (30, 95, 50)),
            (self._btn_arcade, "Return to Arcade", "arcade", (160, 70, 70), (105, 40, 40)),
        ]:
            hovered = rect.collidepoint(mouse_pos)
            pygame.draw.rect(self.display_surface, hover_color if hovered else normal_color, rect, border_radius=8)
            pygame.draw.rect(self.display_surface, (255, 255, 255), rect, 2, border_radius=8)
            label_surf = self._go_font_small.render(label, True, (255, 255, 255))
            self.display_surface.blit(label_surf, label_surf.get_rect(center=rect.center))
            if clicked and hovered:
                self._end_action = action

        if key_restart:
            self._end_action = "restart"
        elif key_arcade:
            self._end_action = "arcade"
 
    # ------------------------------------------------------------------

    def dispose(self):
        """Remove sprites and disconnect the gameplay socket before restarting."""
        try:
            self.network.disconnect()
        except Exception as exc:
            print(f"[CLEANUP] Forgotten network disconnect failed: {exc}")

        for other_player in list(self.other_players.values()):
            other_player.kill()
        self.other_players.clear()
        if hasattr(self.player, "other_players"):
            self.player.other_players = []

        self.current_attack = None
        for group_name in (
            "attack_sprites",
            "attackable_sprites",
            "enemies",
            "visible_sprites",
            "ground_sprites",
            "object_sprites",
            "obstacle_sprites",
        ):
            group = getattr(self, group_name, None)
            if hasattr(group, "empty"):
                group.empty()
        self.enemy_respawn_queue.clear()
 
    # ------------------------------------------------------------------
 
    def update_network(self):
        """Handle network synchronization"""
        if not self.connected:
            self.connection_status = "Disconnected"
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
                if data.get('name') == self.network.player_name:
                    if player_id in self.other_players:
                        self.other_players[player_id].kill()
                        del self.other_players[player_id]
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
                        print(f"[WARNING] Unknown character type '{character_type}', using default")
 
                    other_player = CharClass(
                        (data['x'], data['y']),
                        [self.visible_sprites],
                        self.obstacle_sprites,
                        player_id=player_id,
                        is_local=False
                    )
                    other_player.name = data['name']
                    self.other_players[player_id] = other_player
                    print(f"[DEBUG] Created remote player {player_id} as {character_type}")
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
        """Draw HUD: connection, hints, health bar, XP, equipped weapon."""
        # Connection status
        status_color = (0, 255, 0) if self.connected else (255, 100, 100)
        self.display_surface.blit(
            self.font.render(self.connection_status, True, status_color), (10, 10))
 
        self.display_surface.blit(
            self.font.render("I: Inventory | SPACE: Attack", True, (255, 255, 255)), (10, 40))
 
        # Health bar
        bar_rect  = pygame.Rect(10, 70, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        ratio     = max(0.0, self.player.hp / max(1, self.player.max_hp))
        fill_rect = pygame.Rect(10, 70, int(HEALTH_BAR_WIDTH * ratio), BAR_HEIGHT)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR,     bar_rect)
        pygame.draw.rect(self.display_surface, HEALTH_COLOR,    fill_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bar_rect, 2)
        self.display_surface.blit(
            self.font.render(f"HP {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255)),
            (10 + HEALTH_BAR_WIDTH + 8, 70))
 
        # XP
        self.display_surface.blit(
            self.font.render(f"XP: {self.player.exp}", True, (255, 215, 0)), (10, 100))
 
        # Equipped weapon
        if self.player.equipped_weapon:
            w = self.player.equipped_weapon
            msg = f"Weapon: {w.name}  (+{w.attack_bonus} atk)"
            color = (255, 200, 100)
        else:
            msg   = "Weapon: none  (open I → select weapon → Equip)"
            color = (150, 150, 150)
        self.display_surface.blit(self.font.render(msg, True, color), (10, 125))
 
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
                while len(self.enemy_history) > self.time_travel._max_history:
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
        """Main update loop"""
        if self.game_over:
            self.visible_sprites.custom_draw(self.player, self.ground_sprites, self.object_sprites, self.world_rect)
            self.draw_names()
            self.draw_status()
            self._draw_score_timer_hud()
            self.draw_end_screen(events)
            return

        self.handle_events(events)
        self.handle_time_travel_input(events)
        self.handle_enemy_debug_input(events)
 
        self.update_network()
 
        # Update player and remote players
        self.player.update()
        self.clamp_player_to_world()
        for other_player in self.other_players.values():
            other_player.update()
 
        # Update enemies; freeze them while time-traveling
        if not self.is_time_traveling:
            for enemy in list(self.enemies):
                enemy.enemy_update(self.player)   # set combat AI state first
            self.enemies.update()                  # then move/animate/check death
            self.player_attack_logic()             # weapon collisions
            self.update_enemy_respawns()

        self._check_game_over()
 
        # Draw (Y-sorted; custom_draw does NOT call update())
        self.visible_sprites.custom_draw(self.player, self.ground_sprites, self.object_sprites, self.world_rect)
 
        self.record_player_state()
 
        self.draw_names()
        self.draw_status()
        self.draw_time_travel_ui()
        self.draw_enemy_debug()
        self._draw_score_timer_hud()

        if self.game_over:
            self.draw_end_screen(events)
 
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
 
    def custom_draw(self, player, ground_sprites=None, object_sprites=None, world_rect=None):
        """Draw static map layers first, then enemies, player, and UI."""
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        def draw_group(group):
            if not group:
                return
            for sprite in sorted(group.sprites(), key=lambda item: item.rect.centery):
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, offset_pos)

        # Keep map/ground out of the dynamic Y-sort so it never covers players.
        draw_group(ground_sprites)
        draw_group(object_sprites)
        self._draw_block_grid(world_rect)

        for sprite in sorted([sprite for sprite in self.sprites() if sprite is not player],
                             key=lambda item: item.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            if getattr(sprite, "max_health", None) is not None:
                pygame.draw.rect(
                    self.display_surface,
                    (255, 70, 70),
                    pygame.Rect(offset_pos.x, offset_pos.y, sprite.rect.width, sprite.rect.height),
                    2,
                )

        offset_pos = player.rect.topleft - self.offset
        self.display_surface.blit(player.image, offset_pos)

    def _draw_block_grid(self, world_rect):
        """Subtle tile grid that keeps the town map feeling block-based."""
        if world_rect is None:
            return
        overlay = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
        left = max(0, int(self.offset.x // TILESIZE) * TILESIZE)
        right = min(world_rect.right, int((self.offset.x + WIDTH) // TILESIZE + 2) * TILESIZE)
        top = max(0, int(self.offset.y // TILESIZE) * TILESIZE)
        bottom = min(world_rect.bottom, int((self.offset.y + HEIGHT) // TILESIZE + 2) * TILESIZE)
        line_color = (0, 0, 0, 22)

        for world_x in range(left, right + 1, TILESIZE):
            screen_x = int(world_x - self.offset.x)
            pygame.draw.line(overlay, line_color, (screen_x, 0), (screen_x, HEIGHT), 1)
        for world_y in range(top, bottom + 1, TILESIZE):
            screen_y = int(world_y - self.offset.y)
            pygame.draw.line(overlay, line_color, (0, screen_y), (WIDTH, screen_y), 1)

        self.display_surface.blit(overlay, (0, 0))
 
    def offset_from_world(self, world_pos):
        """Convert world position to screen position"""
        return pygame.math.Vector2(world_pos) - self.offset
