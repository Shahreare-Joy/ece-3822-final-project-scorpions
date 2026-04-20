from __future__ import annotations

import pygame


def trim_text(text: str, font: pygame.font.Font, max_width: int) -> str:
    if font.size(text)[0] <= max_width:
        return text
    ending = "..."
    while text and font.size(text + ending)[0] > max_width:
        text = text[:-1]
    return text + ending if text else ending


def wrap_text(text: str, font: pygame.font.Font, max_width: int, max_lines: int | None = None) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = ""
    index = 0
    while index < len(words):
        word = words[index]
        test = word if not current else f"{current} {word}"
        if font.size(test)[0] <= max_width:
            current = test
            index += 1
            continue
        if current:
            lines.append(current)
        current = trim_text(word, font, max_width) if font.size(word)[0] > max_width else word
        index += 1
        if max_lines and len(lines) == max_lines - 1:
            remaining = " ".join([current] + words[index:])
            current = trim_text(remaining, font, max_width)
            break
    if current:
        lines.append(current)
    return lines[:max_lines] if max_lines else lines


def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], x: int, y: int, center: bool = False, max_width: int | None = None) -> pygame.Rect:
    if max_width:
        text = trim_text(text, font, max_width)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)
    return rect


def draw_wrapped(surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], area: pygame.Rect, align: str = "left", line_gap: int = 4, max_lines: int | None = None) -> None:
    y = area.y
    for line in wrap_text(text, font, area.width, max_lines=max_lines):
        rendered = font.render(line, True, color)
        rect = rendered.get_rect()
        if align == "center":
            rect.midtop = (area.centerx, y)
        elif align == "right":
            rect.topright = (area.right, y)
        else:
            rect.topleft = (area.x, y)
        surface.blit(rendered, rect)
        y += font.get_linesize() + line_gap
