from __future__ import annotations

"""Game 5: temporary Snake test game.

TEMP TEST GAME - SAFE TO DELETE LATER.

This is only for testing the arcade launch flow. It should not be treated as
the final playable team game unless the team explicitly chooses to keep it.

TODO(REMOVE SNAKE):
    To delete this later, remove games/game_5/ and remove the game_5 registry
    entry from platform_server/game_registry.py and data/generate_dataset.py.
"""

import random
from collections import deque

import pygame


def run_game(player: object = None, session_info: object = None) -> dict[str, object]:
    """Run a tiny Snake game and return control to the arcade."""
    _ = (player, session_info)
    if not pygame.get_init():
        pygame.init()
    screen = pygame.display.get_surface() or pygame.display.set_mode((900, 640))
    pygame.display.set_caption("Scorpions Arcade - Game 5 Snake Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    cell = 24
    area = pygame.Rect(60, 82, 768, 480)
    cols = area.width // cell
    rows = area.height // cell
    snake = deque([(cols // 2, rows // 2), (cols // 2 - 1, rows // 2)])
    direction = (1, 0)
    food = _new_food(cols, rows, snake)
    score = 0
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    direction = (1, 0)
                elif event.key == pygame.K_r and game_over:
                    snake = deque([(cols // 2, rows // 2), (cols // 2 - 1, rows // 2)])
                    direction = (1, 0)
                    food = _new_food(cols, rows, snake)
                    score = 0
                    game_over = False

        if not game_over:
            head = snake[0]
            new_head = (head[0] + direction[0], head[1] + direction[1])
            if new_head[0] < 0 or new_head[0] >= cols or new_head[1] < 0 or new_head[1] >= rows or new_head in snake:
                game_over = True
            else:
                snake.appendleft(new_head)
                if new_head == food:
                    score += 10
                    food = _new_food(cols, rows, snake)
                else:
                    snake.pop()

        _draw(screen, area, cell, snake, food, score, game_over, font)
        pygame.display.flip()
        clock.tick(10)

    return {"ok": True, "score": score, "message": f"Game 5 Snake Test ended with {score} points."}


def _new_food(cols: int, rows: int, snake: deque[tuple[int, int]]) -> tuple[int, int]:
    open_cells = [(x, y) for x in range(cols) for y in range(rows) if (x, y) not in snake]
    return random.choice(open_cells) if open_cells else (0, 0)


def _draw(screen: pygame.Surface, area: pygame.Rect, cell: int, snake: deque[tuple[int, int]], food: tuple[int, int], score: int, game_over: bool, font: pygame.font.Font) -> None:
    screen.fill((13, 16, 24))
    pygame.draw.rect(screen, (28, 35, 48), area, border_radius=8)
    pygame.draw.rect(screen, (75, 198, 130), area, width=2, border_radius=8)
    screen.blit(font.render(f"Game 5 Snake Test | Score: {score} | ESC/Q exits", True, (240, 244, 252)), (area.x, 38))
    pygame.draw.rect(screen, (230, 90, 90), (area.x + food[0] * cell + 3, area.y + food[1] * cell + 3, cell - 6, cell - 6), border_radius=5)
    for index, (x, y) in enumerate(snake):
        color = (122, 232, 154) if index == 0 else (75, 198, 130)
        pygame.draw.rect(screen, color, (area.x + x * cell + 2, area.y + y * cell + 2, cell - 4, cell - 4), border_radius=5)
    if game_over:
        message = font.render("Game Over - press R to restart or ESC to exit", True, (245, 184, 75))
        screen.blit(message, message.get_rect(center=area.center))
