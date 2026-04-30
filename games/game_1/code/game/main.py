"""
main.py - Complete game with character selection and networking

Integrated version combining lab-03 and project-01
"""

import pygame
import sys
import argparse
import os
import json
import importlib.util
from pathlib import Path
from settings import *
from level import Level
from subcharacter import get_all_character_classes

try:
    from client.components.chat_overlay import ChatOverlay, ChatOverlayConfig
except Exception as exc:
    try:
        project_root = Path(__file__).resolve().parents[4]
        overlay_path = project_root / "client" / "components" / "chat_overlay.py"
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        spec = importlib.util.spec_from_file_location("_scorpions_chat_overlay", overlay_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load {overlay_path}")
        overlay_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(overlay_module)
        ChatOverlay = overlay_module.ChatOverlay
        ChatOverlayConfig = overlay_module.ChatOverlayConfig
    except Exception as fallback_exc:
        print(f"[CHAT] Chat overlay import failed: {exc}; fallback failed: {fallback_exc}")
        ChatOverlay = None
        ChatOverlayConfig = None

class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        try:
            self.font = pygame.font.Font(None, fontsize)
        except:
            self.font = pygame.font.SysFont('arial', fontsize)
        
        self.content = content
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.fg, self.bg = fg, bg

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False


class CharacterCard:
    """Visual card displaying a character option"""
    def __init__(self, x, y, character_class):
        self.character_class = character_class
        self.x, self.y = x, y
        self.width, self.height = 200, 280
        
        # Fonts
        try:
            self.name_font = pygame.font.Font(None, 28)
            self.desc_font = pygame.font.Font(None, 18)
        except:
            self.name_font = pygame.font.SysFont('arial', 28)
            self.desc_font = pygame.font.SysFont('arial', 18)
        
        # Load character preview image
        try:
            self.char_image = pygame.image.load(character_class.get_preview_image()).convert_alpha()
            self.char_image = pygame.transform.scale(self.char_image, (128, 128))
        except:
            # Fallback if image not found
            self.char_image = pygame.Surface((128, 128))
            self.char_image.fill((200, 200, 200))
        
        # Create card surface
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        
        self.selected = False
        self.hovered = False
        
    def draw(self, surface):
        """Draw the character card"""
        # Background color based on state
        if self.selected:
            bg_color = (100, 200, 100)  # Green if selected
        elif self.hovered:
            bg_color = (150, 150, 150)  # Light gray if hovered
        else:
            bg_color = (80, 80, 80)     # Dark gray
        
        self.image.fill(bg_color)
        
        # Draw border
        pygame.draw.rect(self.image, (255, 255, 255), [0, 0, self.width, self.height], 3)
        
        # Draw character image (centered at top)
        img_rect = self.char_image.get_rect(center=(self.width/2, 80))
        self.image.blit(self.char_image, img_rect)
        
        # Draw character name
        name_text = self.name_font.render(self.character_class.get_display_name(), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(self.width/2, 160))
        self.image.blit(name_text, name_rect)
        
        # Draw description (word wrap)
        desc = self.character_class.get_description()
        self.draw_wrapped_text(desc, self.desc_font, (255, 255, 255), 10, 190, self.width - 20)
        
        # Draw to screen
        surface.blit(self.image, self.rect)
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font.size(test_line)[0] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            self.image.blit(text_surface, (x, y + i * 20))
    
    def is_hovered(self, pos):
        """Check if mouse is over this card"""
        return self.rect.collidepoint(pos)
    
    def is_clicked(self, pos, pressed):
        """Check if this card was clicked"""
        if self.rect.collidepoint(pos) and pressed[0]:
            return True
        return False


class Game:
    def __init__(self, player_name, server_host='localhost', server_port=DEFAULT_PORT, serializer='text'):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        
        try:
            self.font = pygame.font.Font(None, 48)
            self.button_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.font = pygame.font.SysFont('arial', 48)
            self.button_font = pygame.font.SysFont('arial', 32)
            self.small_font = pygame.font.SysFont('arial', 20)
        
        pygame.display.set_caption(GAME_NAME + f' - {player_name} ({serializer.upper()})')
        self.clock = pygame.time.Clock()

        # Network settings
        self.player_name = player_name
        self.server_host = server_host
        self.server_port = normalize_server_port(server_port)
        self.serializer = serializer

        self.selected_character = None
        self.level = None
        self.running = True
        self.level_menu_open = False
        self.level_options = [
            {"name": "Level 1: Orchard Run", "enabled": True},
            {"name": "Level 2: Coming Soon", "enabled": False},
            {"name": "Level 3: Coming Soon", "enabled": False},
        ]
        self.chat_overlay = self.create_chat_overlay()
        self.result_written = False
        self.final_payload = None

    def create_chat_overlay(self):
        """Create the optional Scorpions Arcade chat overlay.

        The arcade launcher sets PYTHONPATH plus SCORPIONS_* environment values
        before starting this game. If the game is run directly without the
        arcade, the overlay quietly stays disabled and gameplay still works.
        Other team games can copy this small method plus the event/draw calls.
        """
        if ChatOverlay is None or ChatOverlayConfig is None:
            print("[CHAT] Chat overlay unavailable: client.components.ChatOverlay could not be imported.")
            return None
        if os.environ.get("SCORPIONS_CHAT_ENABLED", "1") == "0":
            print("[CHAT] Chat overlay disabled by SCORPIONS_CHAT_ENABLED=0.")
            return None
        session_id = os.environ.get("SCORPIONS_SESSION_ID", "fruit-collection-local")
        sender = os.environ.get("SCORPIONS_DISPLAY_NAME") or self.player_name
        title = os.environ.get("SCORPIONS_CHAT_TITLE", "Fruit Drop Rush Chat")
        storage_dir = os.environ.get("SCORPIONS_CHAT_DIR", "")
        try:
            overlay = ChatOverlay(ChatOverlayConfig(session_id=session_id, sender_name=sender, title=title, storage_dir=storage_dir))
            print(f"[CHAT] Overlay ready for session '{session_id}' as '{sender}'.")
            return overlay
        except Exception as exc:
            print(f"[CHAT] Chat overlay creation failed: {exc}")
            return None

    def character_select(self):
        """Character selection screen"""
        char_select = True
        
        title = self.font.render("Choose Your Character", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH/2, 50))
        
        # Network info
        network_info = self.small_font.render(
            f"Connecting as: {self.player_name} | Server: {self.server_host}:{self.server_port} | {self.serializer.upper()}", 
            True, (200, 200, 200)
        )
        network_info_rect = network_info.get_rect(center=(WIDTH/2, 600))
        
        # Get all available character classes
        character_classes = get_all_character_classes()
        
        # Create character cards
        cards = []
        card_spacing = 220
        start_x = (WIDTH - (len(character_classes) * card_spacing - 20)) / 2
        
        for i, char_class in enumerate(character_classes):
            card = CharacterCard(start_x + i * card_spacing, 120, char_class)
            cards.append(card)
        
        # Buttons
        button_width, button_height = 300, 50
        confirm_button_rect = pygame.Rect(WIDTH/2 - button_width/2, 480, button_width, button_height)
        
        selected_card = None
        clicked_this_frame = False
        
        while char_select:
            for event in pygame.event.get():
                if self.chat_overlay and self.chat_overlay.handle_event(event):
                    continue
                if event.type == pygame.QUIT:
                    char_select = False
                    self.return_to_arcade("Quit")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        char_select = False
                        self.return_to_arcade("Quit")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_this_frame = True
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            
            # Update card hover states and handle clicks
            for card in cards:
                card.hovered = card.is_hovered(mouse_pos)
                if clicked_this_frame and card.is_hovered(mouse_pos):
                    # Deselect all, select this one
                    for c in cards:
                        c.selected = False
                    card.selected = True
                    selected_card = card
            
            # Check confirm button
            if clicked_this_frame and selected_card and confirm_button_rect.collidepoint(mouse_pos):
                # Start game with selected character
                self.selected_character = selected_card.character_class
                char_select = False
            
            # Reset click flag
            if not mouse_pressed[0]:
                clicked_this_frame = False
            
            # Draw
            self.screen.fill((0, 0, 0))  # Black background
            self.screen.blit(title, title_rect)
            
            # Draw cards
            for card in cards:
                card.draw(self.screen)
            
            # Draw confirm button
            if selected_card:
                button_color = (50, 150, 50) if confirm_button_rect.collidepoint(mouse_pos) else (30, 100, 30)
            else:
                button_color = (100, 100, 100)  # Grayed out if nothing selected
            
            pygame.draw.rect(self.screen, button_color, confirm_button_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), confirm_button_rect, 2)
            confirm_text = self.button_font.render("Confirm", True, (255, 255, 255))
            confirm_rect = confirm_text.get_rect(center=confirm_button_rect.center)
            self.screen.blit(confirm_text, confirm_rect)
            
            # Draw network info
            self.screen.blit(network_info, network_info_rect)
            if self.chat_overlay:
                self.chat_overlay.update(self.clock.get_time())
                self.chat_overlay.draw(self.screen)
            
            self.clock.tick(FPS)
            pygame.display.update()

    def _game_over_panel_rect(self):
        return pygame.Rect(WIDTH // 2 - 275, HEIGHT // 2 - 200, 550, 365)

    def _game_over_button_rects(self):
        panel = self._game_over_panel_rect()
        control_y = panel.y + 316
        return {
            "restart": pygame.Rect(panel.centerx - 205, control_y, 185, 36),
            "arcade": pygame.Rect(panel.centerx + 20, control_y, 185, 36),
        }

    def handle_game_over_event(self, event):
        """Handle clickable Game Over controls only while the round is finished."""

        if not (self.level and self.level.game_over):
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            buttons = self._game_over_button_rects()
            if buttons["restart"].collidepoint(event.pos):
                self.restart_round()
                return True
            if buttons["arcade"].collidepoint(event.pos):
                self.return_to_arcade("Return to arcade")
                return True
        return False

    def draw_game_over(self):
        """Draw the finished-round screen over the current map."""

        if self.level is None:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel = self._game_over_panel_rect()
        glow = pygame.Surface((panel.width + 28, panel.height + 28), pygame.SRCALPHA)
        for inset, alpha in ((0, 35), (7, 52), (14, 80)):
            rect = glow.get_rect().inflate(-inset * 2, -inset * 2)
            pygame.draw.rect(glow, (54, 222, 210, alpha), rect, width=3, border_radius=18)
        self.screen.blit(glow, (panel.x - 14, panel.y - 14))

        pygame.draw.rect(self.screen, (10, 14, 24), panel, border_radius=14)
        pygame.draw.rect(self.screen, (54, 222, 210), panel, width=3, border_radius=14)
        inner = panel.inflate(-18, -18)
        pygame.draw.rect(self.screen, (255, 209, 67), inner, width=1, border_radius=10)

        title_font = pygame.font.Font(None, 38)
        score_font = pygame.font.Font(None, 64)
        label_font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)

        title = title_font.render("FRUIT DROP RUSH - GAME OVER", True, (255, 244, 172))
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 42)))

        score_label = small_font.render("FINAL SCORE", True, (132, 206, 255))
        self.screen.blit(score_label, score_label.get_rect(center=(panel.centerx, panel.y + 78)))
        score = score_font.render(f"{self.level.score:,}", True, (255, 255, 255))
        self.screen.blit(score, score.get_rect(center=(panel.centerx, panel.y + 126)))

        stats = [
            ("FRUITS", str(self.level.fruits_collected), (255, 210, 120)),
            ("GOLDEN", str(self.level.golden_fruits_collected), (255, 236, 128)),
            ("HP LEFT", f"{max(0, self.level.player.hp)}", (255, 116, 142)),
            ("HAZARD HITS", str(getattr(self.level, "hazard_hits", 0)), (201, 139, 255)),
        ]
        row_y = panel.y + 166
        for index, (label, value, color) in enumerate(stats):
            row = pygame.Rect(panel.x + 42 + (index % 2) * 238, row_y + (index // 2) * 48, 204, 36)
            pygame.draw.rect(self.screen, (18, 24, 38), row, border_radius=8)
            pygame.draw.rect(self.screen, color, row, width=2, border_radius=8)
            self.screen.blit(small_font.render(label, True, (170, 181, 203)), (row.x + 12, row.y + 5))
            value_surface = label_font.render(value, True, (245, 248, 255))
            self.screen.blit(value_surface, (row.right - value_surface.get_width() - 12, row.y + 8))

        reason = self.level.game_over_reason or "Round complete"
        warning = pygame.Rect(panel.x + 48, panel.y + 266, panel.width - 96, 32)
        pygame.draw.rect(self.screen, (58, 31, 43), warning, border_radius=8)
        pygame.draw.rect(self.screen, (255, 116, 142), warning, width=2, border_radius=8)
        reason_text = small_font.render(f"REASON: {reason}", True, (255, 218, 226))
        self.screen.blit(reason_text, reason_text.get_rect(center=warning.center))

        mouse_pos = pygame.mouse.get_pos()
        buttons = [
            ("restart", "R", "Restart"),
            ("arcade", "ESC", "Return to Arcade"),
        ]
        hovered_any = False
        button_rects = self._game_over_button_rects()
        for action, key, label in buttons:
            button = button_rects[action]
            hovered = button.collidepoint(mouse_pos)
            hovered_any = hovered_any or hovered
            fill = (30, 48, 78) if hovered else (20, 32, 52)
            border = (255, 230, 122) if hovered else (132, 206, 255)
            pygame.draw.rect(self.screen, fill, button, border_radius=9)
            pygame.draw.rect(self.screen, border, button, width=2, border_radius=9)
            key_box = pygame.Rect(button.x + 12, button.y + 7, 46, 22)
            pygame.draw.rect(self.screen, (8, 14, 24), key_box, border_radius=6)
            pygame.draw.rect(self.screen, (255, 209, 67), key_box, width=1, border_radius=6)
            key_surface = small_font.render(key, True, (245, 248, 255))
            self.screen.blit(key_surface, key_surface.get_rect(center=key_box.center))
            self.screen.blit(small_font.render(label, True, (230, 239, 252)), (key_box.right + 12, button.y + 10))
        try:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if hovered_any else pygame.SYSTEM_CURSOR_ARROW)
        except pygame.error:
            pass

    def start_level(self):
        """Load the currently available level map with the selected character."""

        if self.selected_character is None:
            return
        if self.level is not None:
            self.level.network.disconnect()
        self.level = Level(
            self.player_name,
            self.selected_character,
            self.server_host,
            self.server_port,
            self.serializer,
        )

    def restart_round(self):
        """Start a fresh Fruit Drop Rush round with the selected character."""

        if self.selected_character is None:
            return
        self.result_written = False
        self.final_payload = None
        self.level_menu_open = False
        try:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except pygame.error:
            pass
        self.start_level()

    def handle_level_menu_event(self, event):
        """Handle the lightweight level menu without interfering with chat."""

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.level_menu_open = False
                return True
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.restart_round()
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, option in enumerate(self.level_options):
                row = self._level_option_rect(index)
                if row.collidepoint(event.pos):
                    if option["enabled"]:
                        self.restart_round()
                    return True
        return False

    def _level_option_rect(self, index):
        panel = pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 - 145, 420, 290)
        return pygame.Rect(panel.x + 34, panel.y + 92 + index * 54, panel.width - 68, 40)

    def draw_level_menu(self):
        """Draw Level Select. Only Level 1 exists today; future slots are disabled."""

        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 128))
        self.screen.blit(shade, (0, 0))

        panel = pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 - 145, 420, 290)
        pygame.draw.rect(self.screen, (9, 14, 24), panel, border_radius=12)
        pygame.draw.rect(self.screen, (68, 232, 218), panel, width=2, border_radius=12)
        pygame.draw.rect(self.screen, (255, 218, 86), panel.inflate(-16, -16), width=1, border_radius=9)

        title_font = pygame.font.Font(None, 34)
        body_font = pygame.font.Font(None, 22)
        small_font = pygame.font.Font(None, 18)

        title = title_font.render("LEVEL SELECT", True, (255, 244, 172))
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 36)))
        hint = small_font.render("Press 1 or click Level 1. ESC closes.", True, (188, 199, 220))
        self.screen.blit(hint, hint.get_rect(center=(panel.centerx, panel.y + 64)))

        for index, option in enumerate(self.level_options):
            row = self._level_option_rect(index)
            enabled = bool(option["enabled"])
            fill = (20, 34, 48) if enabled else (24, 25, 32)
            border = (132, 206, 255) if enabled else (70, 74, 88)
            text_color = (245, 248, 255) if enabled else (120, 126, 140)
            pygame.draw.rect(self.screen, fill, row, border_radius=8)
            pygame.draw.rect(self.screen, border, row, width=2, border_radius=8)
            label = str(option["name"])
            self.screen.blit(body_font.render(label, True, text_color), (row.x + 14, row.y + 10))

        footer = small_font.render("Current map: Orchard Run", True, (255, 218, 86))
        self.screen.blit(footer, footer.get_rect(center=(panel.centerx, panel.bottom - 30)))

    def write_session_result(self, outcome="Quit"):
        """Write final score data for the arcade launcher, if a path is set."""

        if self.result_written:
            return

        game_id = os.environ.get("SCORPIONS_GAME_ID", "scorpions-arena")
        session_id = os.environ.get("SCORPIONS_SESSION_ID", "fruit-collection-local")

        if self.level is not None:
            payload = self.level.session_result_payload(self.player_name, game_id, session_id)
        else:
            payload = {
                "player_id": self.player_name,
                "game_id": game_id,
                "session_id": session_id,
                "score": 0,
                "outcome": outcome,
                "duration_seconds": 0,
                "metadata": {"fruits_collected": 0, "golden_fruits_collected": 0, "reason": outcome},
            }

        self.final_payload = payload
        result_path = os.environ.get("SCORPIONS_RESULT_PATH", "")
        if result_path:
            try:
                path = Path(result_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("w", encoding="utf-8") as file:
                    json.dump(payload, file)
            except OSError:
                # The game should still close cleanly even if the arcade result
                # temp file is not writable.
                pass

        self.result_written = True

    def return_to_arcade(self, outcome="Quit"):
        """Close this subprocess cleanly so the arcade launcher regains focus."""

        self.write_session_result(outcome)
        if self.chat_overlay is not None:
            try:
                self.chat_overlay.close()
            except Exception:
                pass
        if self.level is not None:
            self.level.network.disconnect()
        try:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except pygame.error:
            pass
        self.running = False
    
    def run(self):
        """Main game loop"""
        # Character selection
        self.character_select()
        
        if not self.running or self.selected_character is None:
            return
        
        # Create level with selected character
        self.start_level()
        
        # Game loop
        while self.running:
            events = []
            for event in pygame.event.get():
                if self.chat_overlay and self.chat_overlay.handle_event(event):
                    continue
                if event.type == pygame.QUIT:
                    self.return_to_arcade("Quit")
                    continue
                # Level select owns its input while open. Gameplay keeps drawing
                # behind it, but ESC/1/clicks are handled here first.
                if self.level_menu_open:
                    self.handle_level_menu_event(event)
                    continue
                if self.handle_game_over_event(event):
                    events = []
                    break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_l and not (
                    self.level and self.level.game_over
                ):
                    self.level_menu_open = True
                    continue
                events.append(event)
                if event.type == pygame.KEYDOWN:
                    if self.level and self.level.game_over:
                        if event.key == pygame.K_r:
                            self.restart_round()
                            events = []
                            break
                        if event.key == pygame.K_ESCAPE:
                            self.return_to_arcade("Return to arcade")
                    elif event.key == pygame.K_ESCAPE:
                        self.return_to_arcade("Quit")

            self.screen.fill('black')
            self.level.run(events)
            if self.level.game_over:
                self.write_session_result()
                self.draw_game_over()
            if self.level_menu_open:
                self.draw_level_menu()
            if self.chat_overlay:
                self.chat_overlay.update(self.clock.get_time())
                self.chat_overlay.draw(self.screen)
            pygame.display.update()
            self.clock.tick(FPS)

        if self.chat_overlay is not None:
            try:
                self.chat_overlay.close()
            except Exception:
                pass
        pygame.quit()
        return {"message": f"{GAME_NAME} returned control to Scorpions Arcade.", "session_result": self.final_payload}


def run_game(player_info=None, session_info=None):
    """Adapter entry point for launchers that prefer importing over subprocess.

    The arcade currently uses subprocess launch mode to preserve this game's
    relative asset paths. This adapter is still useful for tests or future
    launchers that can safely run games in-process.
    """

    player_info = player_info or {}
    session_info = session_info or {}
    player_name = player_info.get("display_name") or player_info.get("username") or "Player"
    server_host = (
        session_info.get("server_host")
        or os.environ.get("SCORPIONS_GAME_HOST")
        or os.environ.get("SCORPIONS_SERVER_HOST")
        or DEFAULT_SERVER
    )
    server_port = normalize_server_port(
        session_info.get("server_port")
        or os.environ.get("SCORPIONS_GAME_PORT")
        or os.environ.get("SCORPIONS_SERVER_PORT")
        or DEFAULT_PORT
    )
    serializer = session_info.get("serializer") or os.environ.get("SCORPIONS_GAME_SERIALIZER") or "json"
    game = Game(str(player_name), str(server_host), server_port, str(serializer))
    return game.run()


if __name__ == '__main__':
    default_server = os.environ.get("SCORPIONS_GAME_HOST") or os.environ.get("SCORPIONS_SERVER_HOST", DEFAULT_SERVER)
    default_port = normalize_server_port(os.environ.get("SCORPIONS_GAME_PORT") or os.environ.get("SCORPIONS_SERVER_PORT", DEFAULT_PORT))
    default_serializer = os.environ.get("SCORPIONS_GAME_SERIALIZER") or os.environ.get("SCORPIONS_SERIALIZER") or "json"

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Multiplayer Game Client with Character Selection')
    parser.add_argument('name', help='Your player name')
    parser.add_argument('--server', default=default_server,
                       help=f'Server hostname (default: {default_server})')
    parser.add_argument('--port', type=int, default=default_port,
                       help=f'Server port. Allowed: {ALLOWED_SERVER_PORTS}. Default: {DEFAULT_PORT}')
    parser.add_argument('--serializer', choices=['text', 'json', 'binary'], 
                       default=default_serializer if default_serializer in ['text', 'json', 'binary'] else 'json',
                       help='Serialization format: json (default for server_json_jitter), text, or binary')
    
    args = parser.parse_args()
    
    print("="*50)
    print(f"Starting game as '{args.name}'")
    safe_port = normalize_server_port(args.port)
    if safe_port != args.port:
        print(f"Unsupported port {args.port}; using allowed default {safe_port}.")
    print(f"Connecting to {args.server}:{safe_port}")
    print(f"Using {args.serializer.upper()} serialization")
    print("="*50)
    print()
    
    game = Game(args.name, args.server, safe_port, args.serializer)
    game.run()
