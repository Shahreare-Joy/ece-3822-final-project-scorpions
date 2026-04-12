"""
constants.py — Shared constants, colors, and theme for ECE 3822 Arcade UI
"""

# ── Window ────────────────────────────────────────────────────────────────────
WINDOW_W   = 1100
WINDOW_H   = 700
FPS        = 60
TITLE      = "ECE 3822 Arcade"

# ── Dark retro-pixel palette ─────────────────────────────────────────────────
BLACK       = (8,   8,   18)
BG          = (12,  12,  28)
PANEL       = (20,  20,  45)
CARD        = (28,  28,  58)
CARD_HOVER  = (35,  35,  72)
BORDER      = (55,  55,  100)
BORDER_LIT  = (90,  90,  160)

WHITE       = (255, 255, 255)
GRAY        = (120, 120, 150)
DGRAY       = (60,  60,  85)

CYAN        = (0,   230, 255)
CYAN_DIM    = (0,   130, 160)
YELLOW      = (255, 210, 0)
YELLOW_DIM  = (160, 130, 0)
PINK        = (255, 80,  160)
GREEN       = (0,   255, 130)
GREEN_DIM   = (0,   140, 70)
RED         = (230, 50,  60)
ORANGE      = (255, 140, 30)
PURPLE      = (160, 80,  255)
TEAL        = (0,   200, 180)

# player slot colors (up to 6)
PLAYER_COLORS = [CYAN, PINK, GREEN, YELLOW, ORANGE, PURPLE]

# ── Layout ────────────────────────────────────────────────────────────────────
SIDEBAR_W   = 220
TOP_BAR_H   = 60
PAD         = 16

# ── Screens ───────────────────────────────────────────────────────────────────
SCREEN_LOGIN      = "login"
SCREEN_LOBBY      = "lobby"
SCREEN_GAME_SELECT= "game_select"
SCREEN_LEADERBOARD= "leaderboard"
SCREEN_PROFILE    = "profile"
SCREEN_SEARCH     = "search"
SCREEN_CHAT       = "chat"
SCREEN_LAUNCHING  = "launching"
