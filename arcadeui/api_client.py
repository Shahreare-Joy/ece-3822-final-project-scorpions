"""
api_client.py — Platform client for ECE 3822 Arcade.

Priority:
  1. Try the Python Platform Server (localhost:5000)
  2. Fall back to local_db.py — persistent local JSON file

Accounts, sessions, leaderboards, chat and search all persist to
arcade_data.json next to this file, so they survive restarts and are
shared across all players on the same machine.
"""

import json
import urllib.request
import urllib.parse
from typing import Any, Optional
import local_db as db

PLATFORM_HOST    = "http://localhost:5000"
GAME_SERVER_HOST = "localhost"
GAME_SERVER_PORT = 9000

_server_online = False


def _get(path: str, params: dict = None) -> Any:
    url = PLATFORM_HOST + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return json.loads(r.read())
    except Exception:
        return None


def _post(path: str, data: dict) -> Any:
    url     = PLATFORM_HOST + path
    payload = json.dumps(data).encode()
    req     = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=2) as r:
            return json.loads(r.read())
    except Exception:
        return None


# ── Connectivity ──────────────────────────────────────────────────────────────

def ping() -> bool:
    global _server_online
    _server_online = _get("/ping") is not None
    return _server_online


# ── Auth ──────────────────────────────────────────────────────────────────────

def login(username: str, password: str) -> Optional[dict]:
    if _server_online:
        return _post("/login", {"username": username, "password": password})
    return db.login(username, password)


def register(username: str, password: str) -> Optional[dict]:
    result = db.register(username, password)
    if _server_online:
        _post("/register", {"username": username, "password": password})
    return result


def user_exists(username: str) -> bool:
    return db.user_exists(username)


# ── Profile ───────────────────────────────────────────────────────────────────

def get_profile(username: str) -> dict:
    if _server_online:
        result = _get(f"/profile/{username}")
        if result:
            return result
    return db.get_profile(username)


# ── Sessions ──────────────────────────────────────────────────────────────────

def add_session(username: str, game: str, score: int,
                outcome: str = "draw", duration: int = 0):
    db.add_session(username, game, score, outcome, duration)
    if _server_online:
        _post("/session", {"username": username, "game": game,
                           "score": score, "outcome": outcome, "duration": duration})


# ── History ───────────────────────────────────────────────────────────────────

def get_history(username: str, game: str = None, sort: str = "date") -> list:
    if _server_online:
        params = {"sort": sort}
        if game:
            params["game"] = game
        result = _get(f"/history/{username}", params)
        if result:
            return result
    return db.get_history(username, game, sort)


# ── Leaderboard ───────────────────────────────────────────────────────────────

def get_leaderboard(game: str, sort: str = "score", limit: int = 20) -> list:
    if _server_online:
        result = _get(f"/leaderboard/{game}", {"sort": sort, "limit": limit})
        if result:
            return result
    return db.get_leaderboard(game, sort, limit)


def get_player_rank(game: str, username: str) -> int:
    if _server_online:
        result = _get(f"/leaderboard/{game}/rank/{username}")
        if result and "rank" in result:
            return result["rank"]
    return db.get_player_rank(game, username)


def get_score_range(game: str, lo: int, hi: int) -> list:
    if _server_online:
        result = _get(f"/leaderboard/{game}/range", {"min": lo, "max": hi})
        if result:
            return result
    return db.get_score_range(game, lo, hi)


# ── Search ────────────────────────────────────────────────────────────────────

def search_players(prefix: str) -> list:
    if _server_online:
        result = _get("/search", {"prefix": prefix})
        if result:
            return result
    return db.search_players(prefix)


# ── Game catalog ──────────────────────────────────────────────────────────────

def get_catalog(sort: str = "most_played") -> list:
    if _server_online:
        result = _get("/games", {"sort": sort})
        if result:
            return result
    # game IDs must match folder names in games/ (lowercased)
    known = [
        ("excape_the_city",   "Escape the City",     True,  "RPG action dungeon game"),
        ("snakes",            "Snake",                True,  "Classic snake game"),
        ("pong",              "Pong",                 True,  "2-player paddle battle"),
        ("rock_paper_scisor", "Rock Paper Scissors",  True,  "Quick RPS vs CPU"),
        ("flappy_bird",       "Flappy Bird",          True,  "Tap to flap through pipes"),
        ("breakout",          "Breakout",             True,  "Smash all the bricks"),
        ("joy_game",          "Joy_Game",             False, "Coming soon — Joy"),
        ("kevin_game",        "Kevin_Game",           False, "Coming soon — Kevin"),
        ("mykai_game",        "Mykai_Game",           False, "Coming soon — Mykai"),
    ]
    # Also pull in any discovered local games not in the known list
    try:
        import game_launcher as _gl
        for gid, meta in _gl.discover_games().items():
            if not any(g[0] == gid for g in known):
                known.append((gid, meta["name"], True, meta.get("description","")))
    except Exception:
        pass
    all_sessions = db._load()["sessions"]
    counts = {}
    avgs   = {}
    for s in all_sessions:
        g = s["game"]
        counts[g] = counts.get(g, 0) + 1
        avgs.setdefault(g, []).append(s["score"])

    catalog = []
    for gid, name, playable, desc in known:
        sc = avgs.get(gid, [])
        catalog.append({
            "id":        gid,
            "name":      name,
            "playable":  playable,
            "desc":      desc,
            "sessions":  counts.get(gid, 0),
            "avg_score": round(sum(sc)/len(sc), 1) if sc else 0.0,
        })

    catalog.sort(key=lambda g: g["avg_score" if sort == "avg_score" else "sessions"],
                 reverse=True)
    return catalog


# ── Chat ──────────────────────────────────────────────────────────────────────

def get_chat(game: str, limit: int = 50) -> list:
    if _server_online:
        result = _get(f"/chat/{game}", {"limit": limit})
        if result:
            return result
    return db.get_chat(game, limit)


def send_chat(game: str, username: str, message: str) -> bool:
    db.send_chat(game, username, message)
    if _server_online:
        _post(f"/chat/{game}", {"username": username, "message": message})
    return True
