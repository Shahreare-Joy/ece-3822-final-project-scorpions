from __future__ import annotations

import random
from collections import deque
from typing import Any

import pygame


# TEMP TEST GAME - SAFE TO DELETE LATER.
# This file is intentionally isolated from the arcade UI. Delete this whole
# folder plus the "snake-test" registry/catalog rows when the team no longer
# needs a simple playable launch-flow test.


def run_game(player_info: dict[str, Any] | None = None, session_info: dict[str, Any] | None = None) -> dict[str, object]:
    """Run a tiny local Snake game and return control to Scorpions Arcade.

    TODO(C++ SERVER): Real team games will use session_info values such as
    session_id, server_host, and server_port to join a multiplayer session.
    This temporary Snake test ignores networking on purpose.
    """
    if not pygame.get_init():
        pygame.init()

    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((1180, 760))

    previous_caption = pygame.display.get_caption()[0]
    pygame.display.set_caption("Snake Test - Temporary Flow Check")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    small_font = pygame.font.Font(None, 22)
    width, height = screen.get_size()
    cell = 22
    play_area = pygame.Rect(70, 98, width - 140, height - 178)
    play_area.width -= play_area.width % cell
    play_area.height -= play_area.height % cell

    cols = play_area.width // cell
    rows = play_area.height // cell
    snake = deque([(cols // 2, rows // 2), (cols // 2 - 1, rows // 2), (cols // 2 - 2, rows // 2)])
    direction = (1, 0)
    next_direction = direction
    food = _new_food(cols, rows, snake)
    score = 0
    game_over = False
    running = True

    player_name = "Guest"
    if player_info:
        player_name = str(player_info.get("display_name") or player_info.get("username") or "Guest")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_r and game_over:
                    snake = deque([(cols // 2, rows // 2), (cols // 2 - 1, rows // 2), (cols // 2 - 2, rows // 2)])
                    direction = (1, 0)
                    next_direction = direction
                    food = _new_food(cols, rows, snake)
                    score = 0
                    game_over = False
                elif event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    next_direction = (1, 0)

        if not game_over:
            direction = next_direction
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])
            hit_wall = new_head[0] < 0 or new_head[0] >= cols or new_head[1] < 0 or new_head[1] >= rows
            hit_self = new_head in snake
            if hit_wall or hit_self:
                game_over = True
            else:
                snake.appendleft(new_head)
                if new_head == food:
                    score += 10
                    food = _new_food(cols, rows, snake)
                else:
                    snake.pop()

        _draw(screen, play_area, cell, snake, food, score, player_name, game_over, font, small_font)
        pygame.display.flip()
        clock.tick(10)

    pygame.display.set_caption(previous_caption or "Scorpions Arcade")
    return {"ok": True, "message": f"Snake Test ended with {score} points. Returned control to Scorpions Arcade."}


def _new_food(cols: int, rows: int, snake: deque[tuple[int, int]]) -> tuple[int, int]:
    open_cells = [(x, y) for x in range(cols) for y in range(rows) if (x, y) not in snake]
    return random.choice(open_cells) if open_cells else (0, 0)


def _draw(
    screen: pygame.Surface,
    play_area: pygame.Rect,
    cell: int,
    snake: deque[tuple[int, int]],
    food: tuple[int, int],
    score: int,
    player_name: str,
    game_over: bool,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    screen.fill((13, 16, 24))
    pygame.draw.rect(screen, (28, 35, 48), play_area, border_radius=8)
    pygame.draw.rect(screen, (82, 190, 126), play_area, width=2, border_radius=8)

    title = font.render("Snake Test Lab", True, (235, 241, 246))
    subtitle = small_font.render("TEMP TEST GAME - ESC/Q exits, WASD/arrows move, R restarts after game over", True, (162, 174, 188))
    score_text = font.render(f"{player_name}  |  Score: {score}", True, (126, 226, 160))
    screen.blit(title, (play_area.x, 38))
    screen.blit(subtitle, (play_area.x, 68))
    screen.blit(score_text, (play_area.right - score_text.get_width(), 42))

    food_rect = pygame.Rect(play_area.x + food[0] * cell + 3, play_area.y + food[1] * cell + 3, cell - 6, cell - 6)
    pygame.draw.rect(screen, (228, 92, 112), food_rect, border_radius=5)

    for index, (x, y) in enumerate(snake):
        rect = pygame.Rect(play_area.x + x * cell + 2, play_area.y + y * cell + 2, cell - 4, cell - 4)
        color = (122, 232, 154) if index == 0 else (82, 190, 126)
        pygame.draw.rect(screen, color, rect, border_radius=5)

    if game_over:
        overlay = pygame.Surface(play_area.size, pygame.SRCALPHA)
        overlay.fill((4, 7, 12, 172))
        screen.blit(overlay, play_area.topleft)
        message = font.render("Game Over - press R to restart or ESC to return", True, (245, 248, 250))
        screen.blit(message, (play_area.centerx - message.get_width() // 2, play_area.centery - 18))
