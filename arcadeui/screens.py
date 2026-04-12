"""
screens.py — All UI screens for the ECE 3822 Arcade pygame client.

Each screen class exposes:
    handle_event(event) -> str | None   (returns next screen name or None)
    update()                            (called every frame)
    draw(surf)                          (render to surface)

App state is shared via the AppState dataclass passed to every screen.
"""

import pygame
import datetime
from dataclasses import dataclass, field
from typing import Optional
from constants import *
from widgets import (Button, InputBox, ScrollPanel, TabBar, toast,
                     draw_text, draw_rect, draw_circle, draw_avatar,
                     draw_line, scanline_overlay)
import api_client as api


# ── Shared app state ──────────────────────────────────────────────────────────

@dataclass
class AppState:
    username:      str  = ""
    current_game:  str  = "dungeon_crawler"   # selected game id
    online:        bool = False               # platform server reachable
    players_online:int  = 0
    local_games:   dict = field(default_factory=dict)  # populated by game_launcher


# ════════════════════════════════════════════════════════════════════════════
# TOP BAR  (drawn by App, not a screen)
# ════════════════════════════════════════════════════════════════════════════

def draw_top_bar(surf: pygame.Surface, state: AppState):
    r = pygame.Rect(0, 0, WINDOW_W, TOP_BAR_H)
    draw_rect(surf, r, PANEL, 0)
    pygame.draw.line(surf, BORDER, (0, TOP_BAR_H), (WINDOW_W, TOP_BAR_H), 1)

    # title
    draw_text(surf, "PIXEL ARCADE", 22, YELLOW, 20, 18, bold=True)
    draw_text(surf, "ECE 3822", 11, YELLOW_DIM, 23, 38)

    # online status
    dot_c = GREEN if state.online else RED
    pygame.draw.circle(surf, dot_c, (WINDOW_W - 160, 30), 6)
    status = "SERVER ONLINE" if state.online else "OFFLINE MODE"
    draw_text(surf, status, 11, dot_c, WINDOW_W - 148, 24)

    # user
    if state.username:
        draw_avatar(surf, WINDOW_W - 40, 30, 18,
                    state.username[0], CYAN_DIM, BLACK)
        draw_text(surf, state.username, 12, GRAY,
                  WINDOW_W - 65, 23, center=False, max_width=80)


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAV  (drawn by App)
# ════════════════════════════════════════════════════════════════════════════

NAV_ITEMS = [
    (SCREEN_LOBBY,       "LOBBY"),
    (SCREEN_GAME_SELECT, "GAMES"),
    (SCREEN_LEADERBOARD, "SCORES"),
    (SCREEN_PROFILE,     "PROFILE"),
    (SCREEN_SEARCH,      "SEARCH"),
    (SCREEN_CHAT,        "CHAT"),
]


def draw_sidebar(surf: pygame.Surface, active_screen: str) -> Optional[str]:
    """Draw sidebar nav; returns clicked screen id or None."""
    r = pygame.Rect(0, TOP_BAR_H, SIDEBAR_W, WINDOW_H - TOP_BAR_H)
    draw_rect(surf, r, PANEL, 0)
    pygame.draw.line(surf, BORDER,
                     (SIDEBAR_W, TOP_BAR_H), (SIDEBAR_W, WINDOW_H), 1)

    icons = ["⬡", "◈", "▲", "◉", "⊕", "☰"]
    for i, (sid, label) in enumerate(NAV_ITEMS):
        y = TOP_BAR_H + 20 + i * 52
        item_r = pygame.Rect(8, y, SIDEBAR_W - 16, 42)
        sel = sid == active_screen
        bg  = CARD if sel else PANEL
        bc  = CYAN if sel else None
        draw_rect(surf, item_r, bg, 6)
        if sel:
            draw_rect(surf, item_r, (0,0,0,0), 6, 2, CYAN)
            # accent bar
            pygame.draw.rect(surf, CYAN, (0, y + 2, 3, 38), border_radius=2)
        draw_text(surf, icons[i], 16, CYAN if sel else GRAY, 24, y + 12)
        draw_text(surf, label, 12, WHITE if sel else GRAY, 48, y + 14)

    return None   # click detection handled in App


def sidebar_click(pos, active_screen: str) -> Optional[str]:
    mx, my = pos
    if mx > SIDEBAR_W:
        return None
    for i, (sid, _) in enumerate(NAV_ITEMS):
        y = TOP_BAR_H + 20 + i * 52
        if y <= my <= y + 42:
            return sid
    return None


# ════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ════════════════════════════════════════════════════════════════════════════

class LoginScreen:
    def __init__(self, state: AppState):
        self.state     = state
        cx = WINDOW_W // 2
        self.inp_user  = InputBox((cx - 160, 280, 320, 44), "Username")
        self.inp_pass  = InputBox((cx - 160, 340, 320, 44), "Password", secret=True)
        self.btn_login = Button((cx - 160, 405, 150, 42), "LOG IN",    CYAN)
        self.btn_reg   = Button((cx + 10,  405, 150, 42), "REGISTER",  PINK)
        self._error    = ""
        self._blink    = 0

    def handle_event(self, event) -> Optional[str]:
        for inp in (self.inp_user, self.inp_pass):
            inp.handle_event(event)

        if self.btn_login.handle_event(event):
            return self._do_login()
        if self.btn_reg.handle_event(event):
            return self._do_register()

        if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
                and (self.inp_user.active or self.inp_pass.active)):
            return self._do_login()
        return None

    def _do_login(self) -> Optional[str]:
        u = self.inp_user.text.strip()
        p = self.inp_pass.text.strip()
        if not u:
            self._error = "Enter a username"; return None
        result = api.login(u, p)
        if result or not self.state.online:
            # offline mode: accept anything
            self.state.username = u
            toast.show(f"Welcome, {u}!", GREEN)
            return SCREEN_LOBBY
        self._error = "Invalid credentials"
        return None

    def _do_register(self) -> Optional[str]:
        u = self.inp_user.text.strip()
        p = self.inp_pass.text.strip()
        if not u:
            self._error = "Enter a username"; return None
        result = api.register(u, p)
        if result or not self.state.online:
            self.state.username = u
            toast.show(f"Account created! Welcome {u}", GREEN)
            return SCREEN_LOBBY
        self._error = "Registration failed"
        return None

    def update(self): pass

    def draw(self, surf: pygame.Surface):
        surf.fill(BG)
        cx = WINDOW_W // 2

        # big title
        shadow = pygame.font.Font(None, 72).render("PIXEL ARCADE", True, (40, 30, 0))
        main   = pygame.font.Font(None, 72).render("PIXEL ARCADE", True, YELLOW)
        surf.blit(shadow, (cx - main.get_width()//2 + 3, 83))
        surf.blit(main,   (cx - main.get_width()//2,     80))

        draw_text(surf, "ECE 3822  •  SPRING 2026", 14, CYAN_DIM, cx, 150, center=True)
        draw_text(surf, "Connect. Play. Compete.", 16, GRAY, cx, 175, center=True)

        # card
        card = pygame.Rect(cx - 180, 240, 360, 230)
        draw_rect(surf, card, CARD, 10)
        draw_rect(surf, card, (0,0,0,0), 10, 2, BORDER)

        draw_text(surf, "SIGN IN", 14, CYAN, cx, 258, center=True)
        pygame.draw.line(surf, BORDER, (cx-80, 270), (cx+80, 270), 1)

        self.inp_user.draw(surf)
        self.inp_pass.draw(surf)
        self.btn_login.draw(surf)
        self.btn_reg.draw(surf)

        if self._error:
            draw_text(surf, self._error, 13, RED, cx, 460, center=True)

        draw_text(surf, "Offline mode: type any username to continue",
                  11, DGRAY, cx, 490, center=True)


# ════════════════════════════════════════════════════════════════════════════
# LOBBY SCREEN
# ════════════════════════════════════════════════════════════════════════════

class LobbyScreen:
    def __init__(self, state: AppState):
        self.state    = state
        self._players = []   # fetched from server
        self._refresh_t = 0
        self.btn_play = Button(
            (SIDEBAR_W + 20, WINDOW_H - 70, 200, 44),
            "PLAY A GAME >>>", CYAN)
        self.btn_scores = Button(
            (SIDEBAR_W + 240, WINDOW_H - 70, 160, 44),
            "LEADERBOARD", YELLOW)

    def handle_event(self, event) -> Optional[str]:
        if self.btn_play.handle_event(event):
            return SCREEN_GAME_SELECT
        if self.btn_scores.handle_event(event):
            return SCREEN_LEADERBOARD
        return None

    def update(self):
        now = pygame.time.get_ticks()
        if now - self._refresh_t > 5000:
            self._refresh_t = now

    def draw(self, surf: pygame.Surface):
        x0 = SIDEBAR_W + PAD
        w  = WINDOW_W - SIDEBAR_W - PAD * 2
        y0 = TOP_BAR_H + PAD

        draw_text(surf, f"Welcome back, {self.state.username or 'Player'}!",
                  20, WHITE, x0, y0, bold=True)
        draw_text(surf, "LIVE ARCADE LOBBY", 13, CYAN_DIM, x0, y0 + 28)

        # stat cards
        profile = api.get_profile(self.state.username)
        stats = [
            ("GAMES PLAYED",  str(profile.get("games_played", 0)),     CYAN),
            ("TOTAL WINS",    str(profile.get("wins", 0)),              GREEN),
            ("WIN RATE",      f"{profile.get('win_rate',0)*100:.0f}%",  YELLOW),
            ("GLOBAL RANK",   f"#{profile.get('rank', '?')}",           PINK),
        ]
        card_w = (w - PAD * 3) // 4
        for i, (label, val, color) in enumerate(stats):
            cx_ = x0 + i * (card_w + PAD)
            r   = pygame.Rect(cx_, y0 + 60, card_w, 80)
            draw_rect(surf, r, CARD, 8)
            draw_rect(surf, r, (0,0,0,0), 8, 2, BORDER)
            draw_text(surf, label, 10, GRAY, cx_ + card_w//2, y0 + 75, center=True)
            draw_text(surf, val, 24, color, cx_ + card_w//2, y0 + 103, center=True, bold=True)

        # recent activity
        draw_text(surf, "RECENT SESSIONS", 13, PINK, x0, y0 + 160)
        pygame.draw.line(surf, BORDER, (x0, y0 + 178), (x0 + w, y0 + 178), 1)

        history = api.get_history(self.state.username)[:8]
        game_colors = {
            "dungeon_crawler": PURPLE, "space_shooter": CYAN,
            "platform_runner": GREEN,  "tower_defense": ORANGE,
        }
        for i, h in enumerate(history):
            hy = y0 + 188 + i * 40
            row = pygame.Rect(x0, hy, w, 34)
            hover = row.collidepoint(pygame.mouse.get_pos())
            draw_rect(surf, row, CARD_HOVER if hover else CARD, 5)
            gc = game_colors.get(h.get("game",""), GRAY)
            pygame.draw.rect(surf, gc, (x0 + 2, hy + 4, 3, 26), border_radius=2)
            game_name = h.get("game","?").replace("_", " ").title()
            draw_text(surf, game_name, 13, WHITE, x0 + 14, hy + 10, max_width=160)
            draw_text(surf, h.get("date",""), 11, GRAY, x0 + 190, hy + 11)
            sc  = h.get("score", 0)
            out = h.get("outcome","")
            oc  = GREEN if out == "win" else (RED if out == "loss" else GRAY)
            draw_text(surf, out.upper(), 11, oc, x0 + 320, hy + 11)
            draw_text(surf, f"{sc} pts", 12, YELLOW, x0 + w - 80, hy + 10)

        if not history:
            draw_text(surf, "No sessions yet — play a game!", 13, DGRAY,
                      x0 + w//2, y0 + 220, center=True)

        self.btn_play.draw(surf)
        self.btn_scores.draw(surf)


# ════════════════════════════════════════════════════════════════════════════
# GAME SELECT SCREEN
# ════════════════════════════════════════════════════════════════════════════

class GameSelectScreen:
    def __init__(self, state: AppState):
        self.state    = state
        self._catalog = []
        self._loaded  = False
        self._tab     = TabBar(SIDEBAR_W + PAD, TOP_BAR_H + 50,
                               ["MOST PLAYED", "TOP RATED", "RECENT"], 140)
        self._panel   = ScrollPanel(
            pygame.Rect(SIDEBAR_W + PAD, TOP_BAR_H + 96,
                        WINDOW_W - SIDEBAR_W - PAD*2, WINDOW_H - TOP_BAR_H - 100),
            3000)
        self._sort_keys = ["most_played", "avg_score", "recent"]
        self._sort      = "most_played"
        self._launch_btn: Optional[Button] = None
        self._selected_game = None

    def _load(self):
        catalog = api.get_catalog(self._sort)
        # Mark locally installed games as playable
        local = self.state.local_games  # dict of {id: meta}
        for g in catalog:
            if g["id"] in local:
                g["playable"] = True
                g["name"]     = local[g["id"]].get("name", g["name"])
                g["desc"]     = local[g["id"]].get("description", g.get("desc",""))
        # Also prepend any local games not already in the catalog
        catalog_ids = {g["id"] for g in catalog}
        for gid, meta in local.items():
            if gid not in catalog_ids:
                catalog.insert(0, {
                    "id":       gid,
                    "name":     meta.get("name", gid.replace("_"," ").title()),
                    "desc":     meta.get("description",""),
                    "playable": True,
                    "sessions": 0,
                    "avg_score": 0.0,
                })
        self._catalog = catalog
        self._loaded  = True
        self._build_panel()

    def _build_panel(self):
        pw   = self._panel.rect.width - 12
        rows = len(self._catalog)
        ch   = max(rows * 70 + 20, self._panel.rect.height)
        self._panel.reset(ch)
        s    = self._panel.surface
        s.fill(BG)

        for i, g in enumerate(self._catalog):
            y    = 10 + i * 66
            row  = pygame.Rect(0, y, pw, 60)
            sel  = g["id"] == self.state.current_game
            draw_rect(s, row, CARD_HOVER if sel else CARD, 7)
            if sel:
                draw_rect(s, row, (0,0,0,0), 7, 2, CYAN)

            # playable badge
            if g.get("playable"):
                br = pygame.Rect(pw - 90, y + 18, 78, 22)
                draw_rect(s, br, (0, 80, 60), 4)
                draw_rect(s, br, (0,0,0,0), 4, 1, GREEN)
                draw_text(s, "PLAYABLE", 10, GREEN, br.centerx, br.centery, center=True)

            # rank badge
            rank_r = pygame.Rect(6, y + 16, 32, 28)
            draw_rect(s, rank_r, PANEL, 4)
            draw_text(s, f"#{i+1}", 11, GRAY, rank_r.centerx, rank_r.centery, center=True)

            draw_text(s, g["name"], 15, WHITE if sel else GRAY,
                      48, y + 10, bold=sel, max_width=300)
            draw_text(s, g.get("desc",""), 11, DGRAY, 48, y + 32, max_width=360)
            draw_text(s, f"{g.get('sessions',0):,} sessions",
                      11, CYAN_DIM, 430, y + 14)
            draw_text(s, f"★ {g.get('avg_score',0):.1f}",
                      11, YELLOW, 430, y + 34)

    def handle_event(self, event) -> Optional[str]:
        changed = self._tab.handle_event(event)
        if changed >= 0:
            self._sort = self._sort_keys[changed]
            self._load()

        self._panel.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            pr = self._panel.rect
            if pr.collidepoint(mx, my):
                local_y = my - pr.y + self._panel.scroll_y
                idx = int((local_y - 10) // 66)
                if 0 <= idx < len(self._catalog):
                    g = self._catalog[idx]
                    self.state.current_game = g["id"]
                    self._build_panel()
                    if g.get("playable"):
                        toast.show(f"Launching {g['name']}…", CYAN)
                        return SCREEN_LAUNCHING

        return None

    def update(self):
        if not self._loaded:
            self._load()

    def draw(self, surf: pygame.Surface):
        x0 = SIDEBAR_W + PAD
        draw_text(surf, "GAME CATALOG", 20, WHITE, x0, TOP_BAR_H + 12, bold=True)
        draw_text(surf, "Click a PLAYABLE game to launch it", 12, GRAY,
                  x0, TOP_BAR_H + 34)
        self._tab.draw(surf)
        # panel background
        draw_rect(surf, self._panel.rect, BG, 0)
        self._panel.draw(surf)


# ════════════════════════════════════════════════════════════════════════════
# LEADERBOARD SCREEN
# ════════════════════════════════════════════════════════════════════════════

class LeaderboardScreen:
    def __init__(self, state: AppState):
        self.state   = state
        self._data   = []
        self._loaded = False
        self._tab    = TabBar(SIDEBAR_W + PAD, TOP_BAR_H + 50,
                              ["BY SCORE", "WIN RATE", "PLAY TIME"], 140)
        self._sorts  = ["score", "winrate", "playtime"]
        self._sort   = "score"
        self._panel  = ScrollPanel(
            pygame.Rect(SIDEBAR_W + PAD, TOP_BAR_H + 96,
                        WINDOW_W - SIDEBAR_W - PAD*2, WINDOW_H - TOP_BAR_H - 110),
            3000)
        self._my_rank = -1
        # range query inputs
        rx = SIDEBAR_W + PAD
        ry = WINDOW_H - 58
        self._inp_lo = InputBox((rx, ry, 80, 34), "Min", font_size=13, max_len=6)
        self._inp_hi = InputBox((rx+90, ry, 80, 34), "Max", font_size=13, max_len=6)
        self._btn_range = Button((rx+180, ry, 100, 34), "RANGE", TEAL, font_size=12)

    def _load(self):
        game = self.state.current_game
        self._data = api.get_leaderboard(game, self._sort, 50)
        self._my_rank = api.get_player_rank(game, self.state.username)
        self._loaded = True
        self._build_panel()

    def _build_panel(self):
        pw  = self._panel.rect.width - 12
        ch  = max(len(self._data) * 56 + 20, self._panel.rect.height)
        self._panel.reset(ch)
        s   = self._panel.surface
        s.fill(BG)

        medal_colors = [YELLOW, (192,192,192), (205,127,50)]
        for i, row in enumerate(self._data):
            y   = 8 + i * 52
            r   = pygame.Rect(0, y, pw, 46)
            is_me = row.get("username","") == self.state.username
            draw_rect(s, r, CARD_HOVER if is_me else CARD, 6)
            if is_me:
                draw_rect(s, r, (0,0,0,0), 6, 2, CYAN)

            # rank
            rank_c = medal_colors[i] if i < 3 else GRAY
            draw_text(s, f"{row.get('rank',i+1)}", 14, rank_c, 16, y + 14, bold=(i<3))

            # avatar
            uname = row.get("username","?")
            draw_avatar(s, 60, y+23, 16, uname[0], CYAN_DIM if not is_me else CYAN, BLACK)

            draw_text(s, uname, 13, WHITE if is_me else GRAY, 84, y + 14,
                      max_width=200)
            if is_me:
                draw_text(s, "YOU", 9, CYAN, 84, y + 30)

            # value columns
            sc  = row.get("score", 0)
            wr  = row.get("win_rate", 0)
            pt  = row.get("playtime", 0)
            draw_text(s, f"{sc:,}",          12, YELLOW,   pw - 280, y + 14)
            draw_text(s, f"{wr*100:.0f}%",   12, GREEN,    pw - 180, y + 14)
            mins = pt // 60
            draw_text(s, f"{mins}m",         12, CYAN_DIM, pw - 100, y + 14)

        # headers
        draw_text(s, "SCORE", 10, DGRAY, pw - 280, 0)
        draw_text(s, "WIN%",  10, DGRAY, pw - 180, 0)
        draw_text(s, "TIME",  10, DGRAY, pw - 100, 0)

    def handle_event(self, event) -> Optional[str]:
        changed = self._tab.handle_event(event)
        if changed >= 0:
            self._sort = self._sorts[changed]
            self._load()
        self._panel.handle_event(event)
        for inp in (self._inp_lo, self._inp_hi):
            inp.handle_event(event)
        if self._btn_range.handle_event(event):
            self._do_range_query()
        return None

    def _do_range_query(self):
        try:
            lo = int(self._inp_lo.text or "0")
            hi = int(self._inp_hi.text or "9999")
        except ValueError:
            toast.show("Enter valid numbers", RED); return
        results = api.get_score_range(self.state.current_game, lo, hi)
        if results is not None:
            self._data = results
            self._build_panel()
            toast.show(f"Found {len(results)} players in range", TEAL)
        else:
            toast.show("Range query failed", RED)

    def update(self):
        if not self._loaded:
            self._load()

    def draw(self, surf: pygame.Surface):
        x0 = SIDEBAR_W + PAD
        gname = self.state.current_game.replace("_"," ").title()
        draw_text(surf, f"LEADERBOARD — {gname}", 18, WHITE, x0, TOP_BAR_H+12, bold=True)
        if self._my_rank > 0:
            draw_text(surf, f"Your rank: #{self._my_rank}", 12, CYAN, x0, TOP_BAR_H+34)
        self._tab.draw(surf)
        draw_rect(surf, self._panel.rect, BG, 0)
        self._panel.draw(surf)
        # range query bar
        draw_text(surf, "Score range:", 11, GRAY,
                  SIDEBAR_W + PAD, WINDOW_H - 58 + 10)
        self._inp_lo.draw(surf)
        self._inp_hi.draw(surf)
        self._btn_range.draw(surf)


# ════════════════════════════════════════════════════════════════════════════
# PROFILE SCREEN
# ════════════════════════════════════════════════════════════════════════════

class ProfileScreen:
    def __init__(self, state: AppState):
        self.state   = state
        self._data   = {}
        self._hist   = []
        self._loaded = False
        self._tab    = TabBar(SIDEBAR_W + PAD, TOP_BAR_H + 130,
                              ["OVERVIEW", "HISTORY", "STATS"], 130)

    def _load(self):
        self._data   = api.get_profile(self.state.username)
        self._hist   = api.get_history(self.state.username)
        self._loaded = True

    def handle_event(self, event) -> Optional[str]:
        self._tab.handle_event(event)
        return None

    def update(self):
        if not self._loaded:
            self._load()

    def draw(self, surf: pygame.Surface):
        x0 = SIDEBAR_W + PAD
        d  = self._data
        w  = WINDOW_W - SIDEBAR_W - PAD * 2

        # header card
        hcard = pygame.Rect(x0, TOP_BAR_H + 12, w, 108)
        draw_rect(surf, hcard, CARD, 10)
        draw_rect(surf, hcard, (0,0,0,0), 10, 2, BORDER)

        draw_avatar(surf, x0 + 52, TOP_BAR_H + 66, 36,
                    (self.state.username or "?")[0], CYAN_DIM, BLACK)
        draw_text(surf, self.state.username, 20, WHITE, x0+100, TOP_BAR_H+34, bold=True)
        draw_text(surf, d.get("country",""), 12, GRAY, x0+100, TOP_BAR_H+58)
        draw_text(surf, f"RANK #{d.get('rank','?')}", 13, YELLOW, x0+100, TOP_BAR_H+78)

        # mini stats
        mini = [
            (f"{d.get('games_played',0)}",           "PLAYED"),
            (f"{d.get('wins',0)}",                   "WINS"),
            (f"{d.get('win_rate',0)*100:.0f}%",       "WIN RATE"),
            (f"{d.get('total_playtime',0)//60}m",    "PLAYTIME"),
        ]
        for i, (val, lbl) in enumerate(mini):
            mx = x0 + 340 + i * 110
            draw_text(surf, val, 18, CYAN, mx, TOP_BAR_H + 44, center=True, bold=True)
            draw_text(surf, lbl, 10, GRAY, mx, TOP_BAR_H + 70, center=True)

        self._tab.draw(surf)
        tab = self._tab.active
        y0 = TOP_BAR_H + 176

        if tab == 0:  # overview
            sh = self._data.get("score_history", [])
            if sh:
                draw_text(surf, "SCORE HISTORY", 12, PINK, x0, y0)
                # mini sparkline
                chart_r = pygame.Rect(x0, y0+20, w, 120)
                draw_rect(surf, chart_r, CARD, 6)
                if len(sh) > 1:
                    mn, mx_ = min(sh), max(sh)
                    rng = max(mx_ - mn, 1)
                    pts = []
                    for j, v in enumerate(sh):
                        px_ = chart_r.x + 20 + j * (chart_r.width-40)//(len(sh)-1)
                        py_ = chart_r.bottom - 15 - int((v-mn)/rng * (chart_r.height-30))
                        pts.append((px_, py_))
                    if len(pts) >= 2:
                        pygame.draw.lines(surf, CYAN, False, pts, 2)
                    for p in pts:
                        pygame.draw.circle(surf, CYAN, p, 4)

            fav = d.get("favorite_game","")
            if fav:
                draw_text(surf, f"Favorite: {fav.replace('_',' ').title()}",
                          13, YELLOW, x0, y0 + 160)

        elif tab == 1:  # history
            draw_text(surf, "MATCH HISTORY", 12, PINK, x0, y0)
            for i, h in enumerate(self._hist[:12]):
                hy  = y0 + 24 + i * 36
                row = pygame.Rect(x0, hy, w, 30)
                draw_rect(surf, row, CARD, 4)
                gname = h.get("game","").replace("_"," ").title()
                draw_text(surf, gname, 12, WHITE, x0+8, hy+9, max_width=180)
                draw_text(surf, h.get("date",""), 10, GRAY, x0+200, hy+10)
                out = h.get("outcome","")
                oc  = GREEN if out=="win" else (RED if out=="loss" else GRAY)
                draw_text(surf, out.upper(), 10, oc, x0+340, hy+10)
                draw_text(surf, f"{h.get('score',0)} pts", 11, YELLOW, x0+w-90, hy+9)

        elif tab == 2:  # stats
            draw_text(surf, "PERFORMANCE STATS", 12, PINK, x0, y0)
            rows = [
                ("Total sessions",    str(d.get("games_played",0))),
                ("Total wins",        str(d.get("wins",0))),
                ("Win rate",          f"{d.get('win_rate',0)*100:.1f}%"),
                ("Total playtime",    f"{d.get('total_playtime',0)//60} min"),
                ("Global rank",       f"#{d.get('rank','?')}"),
                ("Favorite game",     d.get("favorite_game","N/A").replace("_"," ").title()),
            ]
            for i, (k, v) in enumerate(rows):
                ry  = y0 + 28 + i * 38
                rr  = pygame.Rect(x0, ry, w, 32)
                draw_rect(surf, rr, CARD, 4)
                draw_text(surf, k, 12, GRAY, x0+10, ry+10)
                draw_text(surf, v, 13, WHITE, x0+w-10-len(v)*8, ry+10)


# ════════════════════════════════════════════════════════════════════════════
# SEARCH SCREEN
# ════════════════════════════════════════════════════════════════════════════

class SearchScreen:
    def __init__(self, state: AppState):
        self.state      = state
        self._results   = []
        self._selected  = None
        self._sel_data  = {}
        x0 = SIDEBAR_W + PAD
        self._inp = InputBox((x0, TOP_BAR_H+48, 360, 40), "Search by name prefix…")
        self._inp.active = True

    def handle_event(self, event) -> Optional[str]:
        self._inp.handle_event(event)
        if event.type == pygame.KEYDOWN and self._inp.active:
            self._results = api.search_players(self._inp.text)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            x0 = SIDEBAR_W + PAD
            for i, r in enumerate(self._results):
                row = pygame.Rect(x0, TOP_BAR_H + 108 + i*48, 360, 42)
                if row.collidepoint(mx, my):
                    self._selected = r["username"]
                    self._sel_data = api.get_profile(r["username"])
        return None

    def update(self): pass

    def draw(self, surf: pygame.Surface):
        x0 = SIDEBAR_W + PAD
        draw_text(surf, "PLAYER SEARCH", 20, WHITE, x0, TOP_BAR_H+12, bold=True)
        draw_text(surf, "Autocomplete prefix search", 12, GRAY, x0, TOP_BAR_H+32)
        self._inp.draw(surf)

        for i, r in enumerate(self._results[:10]):
            y   = TOP_BAR_H + 108 + i * 48
            row = pygame.Rect(x0, y, 360, 42)
            sel = r["username"] == self._selected
            draw_rect(surf, row, CARD_HOVER if sel else CARD, 6)
            if sel:
                draw_rect(surf, row, (0,0,0,0), 6, 2, CYAN)
            draw_avatar(surf, x0+22, y+21, 14, r["username"][0], CYAN_DIM, BLACK)
            draw_text(surf, r["username"], 13, WHITE, x0+42, y+14)
            draw_text(surf, f"{r.get('score',0):,} pts", 11, YELLOW, x0+42, y+30)

        # detail panel
        if self._sel_data:
            d   = self._sel_data
            px  = SIDEBAR_W + 400
            pw  = WINDOW_W - px - PAD
            pc  = pygame.Rect(px, TOP_BAR_H+48, pw, WINDOW_H-TOP_BAR_H-60)
            draw_rect(surf, pc, CARD, 10)
            draw_rect(surf, pc, (0,0,0,0), 10, 2, BORDER)
            draw_avatar(surf, px + pw//2, TOP_BAR_H+100, 30,
                        (self._selected or "?")[0], PINK, BLACK)
            draw_text(surf, self._selected or "", 16, WHITE,
                      px+pw//2, TOP_BAR_H+142, center=True, bold=True)
            rows = [
                ("Rank",       f"#{d.get('rank','?')}"),
                ("Played",     str(d.get("games_played",0))),
                ("Wins",       str(d.get("wins",0))),
                ("Win rate",   f"{d.get('win_rate',0)*100:.0f}%"),
                ("Playtime",   f"{d.get('total_playtime',0)//60}m"),
                ("Country",    d.get("country","?")),
            ]
            for j, (k, v) in enumerate(rows):
                ry = TOP_BAR_H + 172 + j*38
                draw_text(surf, k, 11, GRAY, px+16, ry)
                draw_text(surf, v, 12, WHITE, px+pw-16-len(v)*8, ry)
                draw_line(surf, BORDER, (px+10, ry+22), (px+pw-10, ry+22))


# ════════════════════════════════════════════════════════════════════════════
# CHAT SCREEN
# ════════════════════════════════════════════════════════════════════════════

class ChatScreen:
    def __init__(self, state: AppState):
        self.state     = state
        self._messages = []
        self._refresh_t= 0
        self._inp = InputBox(
            (SIDEBAR_W + PAD, WINDOW_H - 58, WINDOW_W - SIDEBAR_W - PAD*2 - 90, 40),
            "Type a message…", max_len=120)
        self._send_btn = Button(
            (WINDOW_W - PAD - 80, WINDOW_H - 58, 76, 40), "SEND", CYAN)

    def handle_event(self, event) -> Optional[str]:
        self._inp.handle_event(event)
        if self._send_btn.handle_event(event) or (
                event.type == pygame.KEYDOWN and
                event.key == pygame.K_RETURN and
                self._inp.active and self._inp.text.strip()):
            self._send()
        return None

    def _send(self):
        msg = self._inp.text.strip()
        if not msg: return
        api.send_chat(self.state.current_game, self.state.username, msg)
        now = datetime.datetime.now().strftime("%H:%M")
        self._messages.append({
            "username": self.state.username, "message": msg, "ts": now})
        self._inp.text = ""

    def update(self):
        now = pygame.time.get_ticks()
        if now - self._refresh_t > 3000:
            self._refresh_t = now
            fresh = api.get_chat(self.state.current_game)
            if fresh:
                self._messages = fresh

    def draw(self, surf: pygame.Surface):
        x0 = SIDEBAR_W + PAD
        w  = WINDOW_W - SIDEBAR_W - PAD * 2
        gname = self.state.current_game.replace("_"," ").title()
        draw_text(surf, f"LIVE CHAT — {gname}", 18, WHITE, x0, TOP_BAR_H+12, bold=True)
        draw_text(surf, "Chat refreshes every 3 seconds", 11, GRAY, x0, TOP_BAR_H+34)

        chat_area = pygame.Rect(x0, TOP_BAR_H+56, w, WINDOW_H - TOP_BAR_H - 120)
        draw_rect(surf, chat_area, CARD, 8)

        msgs = self._messages[-24:]
        for i, m in enumerate(msgs):
            y   = chat_area.y + 8 + i * 28
            me  = m.get("username","") == self.state.username
            uc  = CYAN if me else PINK
            draw_text(surf, m.get("ts",""), 10, DGRAY, x0+10, y+6)
            draw_text(surf, m.get("username",""), 11, uc, x0+52, y+6, bold=True)
            draw_text(surf, m.get("message",""), 12, WHITE, x0+52+
                      len(m.get("username",""))*8+8, y+6, max_width=w-200)

        self._inp.draw(surf)
        self._send_btn.draw(surf)


# ════════════════════════════════════════════════════════════════════════════
# LAUNCHING SCREEN  (transition to game server)
# ════════════════════════════════════════════════════════════════════════════

class LaunchingScreen:
    def __init__(self, state: AppState):
        self.state = state
        self._t    = 0
        self._dots = 0

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return SCREEN_GAME_SELECT
        return None

    def update(self):
        self._t += 1
        if self._t % 20 == 0:
            self._dots = (self._dots + 1) % 4

    def draw(self, surf: pygame.Surface):
        import math
        surf.fill(BG)
        cx, cy = WINDOW_W // 2, WINDOW_H // 2
        gname  = self.state.current_game.replace("_", " ").upper()
        draw_text(surf, "LAUNCHING", 32, YELLOW, cx, cy - 80, center=True, bold=True)
        draw_text(surf, gname, 22, CYAN, cx, cy - 36, center=True)
        dots = "." * self._dots
        draw_text(surf, f"Starting game{dots}", 14, GRAY, cx, cy + 10, center=True)
        draw_text(surf, f"Host: {api.GAME_SERVER_HOST}:{api.GAME_SERVER_PORT}",
                  11, DGRAY, cx, cy + 36, center=True)
        draw_text(surf, "Press ESC to cancel", 11, DGRAY, cx, cy + 60, center=True)

        # Spinner ring
        angle = (self._t * 5) % 360
        for i in range(12):
            a   = math.radians(angle + i * 30)
            px_ = int(cx + 40 * math.cos(a))
            py_ = int(cy + 100 + 14 * math.sin(a))
            brightness = int(80 + 175 * (i / 12))
            pygame.draw.circle(surf, (0, brightness, brightness), (px_, py_), 4)
