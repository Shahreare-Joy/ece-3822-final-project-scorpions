"""
widgets.py — Reusable UI primitives for the ECE 3822 Arcade pygame client.

All widgets are stateless-friendly: draw() takes a surface, handle_event() returns
True when the widget wants to signal an action (click / enter).
"""

import pygame
from constants import *

# ── Font cache ────────────────────────────────────────────────────────────────
_font_cache: dict = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        # try pixel font first, fall back gracefully
        try:
            _font_cache[key] = pygame.font.Font(None, size)
        except Exception:
            _font_cache[key] = pygame.font.SysFont("monospace", size, bold=bold)
    return _font_cache[key]


def load_pixel_fonts():
    """Call once after pygame.init() — tries to load Press Start 2P from system."""
    global _font_cache
    # We rely on pygame's default font; a real deployment would bundle the TTF.
    pass


# ── Draw helpers ──────────────────────────────────────────────────────────────

def draw_text(surf: pygame.Surface, text: str, size: int, color,
              x: int, y: int, center: bool = False, bold: bool = False,
              max_width: int = 0) -> pygame.Rect:
    font = get_font(size, bold)
    if max_width and font.size(text)[0] > max_width:
        # truncate with ellipsis
        while font.size(text + "…")[0] > max_width and len(text) > 0:
            text = text[:-1]
        text += "…"
    surf_ = font.render(text, True, color)
    r = surf_.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(surf_, r)
    return r


def draw_rect(surf: pygame.Surface, rect, color, radius: int = 6,
              border: int = 0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_circle(surf: pygame.Surface, cx: int, cy: int, r: int, color):
    pygame.draw.circle(surf, color, (cx, cy), r)


def draw_line(surf: pygame.Surface, color, start, end, width: int = 1):
    pygame.draw.line(surf, color, start, end, width)


def scanline_overlay(surf: pygame.Surface, alpha: int = 18):
    """Subtle CRT scanlines over a surface."""
    w, h = surf.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 4):
        pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (w, y))
    surf.blit(overlay, (0, 0))


def draw_avatar(surf: pygame.Surface, cx: int, cy: int, radius: int,
                initial: str, bg_color, text_color=BLACK):
    draw_circle(surf, cx, cy, radius, bg_color)
    draw_text(surf, initial.upper(), radius, text_color, cx, cy, center=True, bold=True)


# ── Button ────────────────────────────────────────────────────────────────────

class Button:
    """
    A retro pixel-style button.
    color     — border & text color (idle)
    bg        — fill color (idle); hover brightens slightly
    """
    def __init__(self, rect, label: str, color=CYAN, bg=PANEL,
                 font_size: int = 15, radius: int = 4):
        self.rect      = pygame.Rect(rect)
        self.label     = label
        self.color     = color
        self.bg        = bg
        self.font_size = font_size
        self.radius    = radius
        self._hover    = False
        self._pressed  = False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                self._pressed = False
                return True
            self._pressed = False
        return False

    def draw(self, surf: pygame.Surface):
        bg = CARD_HOVER if self._hover else self.bg
        draw_rect(surf, self.rect, bg, self.radius)
        bc = WHITE if self._hover else self.color
        draw_rect(surf, self.rect, (0,0,0,0), self.radius, 2, bc)
        tc = WHITE if self._hover else self.color
        draw_text(surf, self.label, self.font_size, tc,
                  self.rect.centerx, self.rect.centery, center=True)


# ── InputBox ──────────────────────────────────────────────────────────────────

class InputBox:
    """Single-line text input with cursor blink."""
    def __init__(self, rect, placeholder: str = "", font_size: int = 16,
                 secret: bool = False, max_len: int = 32):
        self.rect        = pygame.Rect(rect)
        self.placeholder = placeholder
        self.font_size   = font_size
        self.secret      = secret
        self.max_len     = max_len
        self.text        = ""
        self.active      = False

    def handle_event(self, event) -> bool:
        """Returns True on Enter key while active."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif event.key not in (pygame.K_TAB, pygame.K_ESCAPE):
                if len(self.text) < self.max_len:
                    self.text += event.unicode
        return False

    def draw(self, surf: pygame.Surface):
        border_c = CYAN if self.active else BORDER
        draw_rect(surf, self.rect, PANEL, 4)
        draw_rect(surf, self.rect, (0,0,0,0), 4, 2, border_c)
        display = ("•" * len(self.text)) if self.secret else self.text
        if display:
            draw_text(surf, display, self.font_size, WHITE,
                      self.rect.x + 10, self.rect.centery, center=False)
        elif not self.active:
            draw_text(surf, self.placeholder, self.font_size, DGRAY,
                      self.rect.x + 10, self.rect.centery, center=False)
        # cursor
        if self.active and pygame.time.get_ticks() % 900 < 450:
            font = get_font(self.font_size)
            cx = self.rect.x + 10 + font.size(display)[0] + 2
            pygame.draw.rect(surf, CYAN,
                             (cx, self.rect.y + 8, 2, self.rect.height - 16))


# ── ScrollPanel ───────────────────────────────────────────────────────────────

class ScrollPanel:
    """
    A clipped scrollable surface.
    Usage:
        panel = ScrollPanel(rect, content_height)
        panel.surface  → draw your rows onto this
        panel.draw(screen)
        panel.handle_event(event)
    """
    def __init__(self, rect, content_height: int = 2000):
        self.rect           = pygame.Rect(rect)
        self.content_height = content_height
        self.surface        = pygame.Surface((rect.width, content_height))
        self.scroll_y       = 0
        self._dragging      = False
        self._drag_start    = 0

    def reset(self, content_height: int = None):
        if content_height:
            self.content_height = content_height
        self.surface = pygame.Surface((self.rect.width, self.content_height))
        self.surface.fill(BG)
        self.scroll_y = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y = max(0, min(
                    self.content_height - self.rect.height,
                    self.scroll_y - event.y * 24
                ))

    def draw(self, surf: pygame.Surface):
        clip = pygame.Rect(0, self.scroll_y, self.rect.width, self.rect.height)
        sub  = self.surface.subsurface(
            pygame.Rect(0, min(self.scroll_y, max(0, self.content_height - self.rect.height)),
                        self.rect.width,
                        min(self.rect.height, self.content_height))
        )
        surf.blit(sub, self.rect.topleft)
        # scrollbar
        if self.content_height > self.rect.height:
            bar_h  = max(30, int(self.rect.height * self.rect.height / self.content_height))
            bar_y  = self.rect.y + int(self.scroll_y / self.content_height * self.rect.height)
            bar_x  = self.rect.right - 6
            pygame.draw.rect(surf, BORDER,
                             (bar_x, self.rect.y, 4, self.rect.height), border_radius=2)
            pygame.draw.rect(surf, CYAN_DIM,
                             (bar_x, bar_y, 4, bar_h), border_radius=2)


# ── Tab Bar ───────────────────────────────────────────────────────────────────

class TabBar:
    def __init__(self, x: int, y: int, tabs: list[str], tab_w: int = 140, h: int = 36):
        self.tabs    = tabs
        self.active  = 0
        self.rects   = [pygame.Rect(x + i * (tab_w + 2), y, tab_w, h)
                        for i in range(len(tabs))]

    def handle_event(self, event) -> int:
        """Returns index of newly selected tab, or -1."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.active = i
                    return i
        return -1

    def draw(self, surf: pygame.Surface):
        for i, (tab, rect) in enumerate(zip(self.tabs, self.rects)):
            sel = i == self.active
            bg  = CARD if sel else PANEL
            bc  = CYAN if sel else BORDER
            draw_rect(surf, rect, bg, 4)
            draw_rect(surf, rect, (0,0,0,0), 4, 2, bc)
            draw_text(surf, tab, 13, CYAN if sel else GRAY,
                      rect.centerx, rect.centery, center=True)


# ── Notification toast ────────────────────────────────────────────────────────

class Toast:
    def __init__(self):
        self.msg     = ""
        self.color   = GREEN
        self.expires = 0

    def show(self, msg: str, color=GREEN, duration_ms: int = 2500):
        self.msg     = msg
        self.color   = color
        self.expires = pygame.time.get_ticks() + duration_ms

    def draw(self, surf: pygame.Surface):
        if pygame.time.get_ticks() > self.expires:
            return
        w = surf.get_width()
        r = pygame.Rect(w // 2 - 200, 10, 400, 36)
        draw_rect(surf, r, PANEL, 6)
        draw_rect(surf, r, (0,0,0,0), 6, 2, self.color)
        draw_text(surf, self.msg, 14, self.color, r.centerx, r.centery, center=True)


# ── Global toast singleton ────────────────────────────────────────────────────
toast = Toast()
