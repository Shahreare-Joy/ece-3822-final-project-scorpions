"""
api_client.py — HTTP client for the Python Platform Server.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Optional, List, Dict


PLATFORM_HOST = "http://localhost:5000"
GAME_SERVER_HOST = "localhost"
GAME_SERVER_PORT = 9000


def _get(path: str, params: dict = None) -> Any:
    url = PLATFORM_HOST + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return json.loads(r.read())
    except Exception:
        return None


def _post(path: str, data: dict) -> Any:
    url = PLATFORM_HOST + path
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as r:
            return json.loads(r.read())
    except Exception:
        return None


# ── Auth ──────────────────────────────────────────────────────────────────────

def ping() -> bool:
    result = _get("/ping")
    return result is not None


def login(username: str, password: str) -> Optional[Dict]:
    """Returns player dict on success, None on failure."""
    return _post("/login", {"username": username, "password": password})


def register(username: str, password: str) -> Optional[Dict]:
    return _post("/register", {"username": username, "password": password})


# ── Profile ───────────────────────────────────────────────────────────────────

def get_profile(username: str) -> Dict:
    result = _get(f"/profile/{username}")
    if result:
        return result

    return {
        "username": username,
        "total_playtime": 3620,
        "games_played": 47,
        "wins": 18,
        "win_rate": 0.383,
        "score_history": [120, 340, 80, 500, 210, 450, 300],
        "favorite_game": "dungeon_crawler",
        "rank": 42,
        "country": "US",
    }


# ── Leaderboard ───────────────────────────────────────────────────────────────

def get_leaderboard(game: str, sort: str = "score", limit: int = 20) -> List[Dict]:
    result = _get(f"/leaderboard/{game}", {"sort": sort, "limit": limit})
    if result:
        return result

    import random
    names = ["Hamza", "Alex", "Jordan", "Sam", "Chris", "Morgan",
             "Riley", "Casey", "Drew", "Taylor", "Phoenix", "Quinn"]

    return [
        {
            "rank": i + 1,
            "username": names[i % len(names)] + str(i),
            "score": 9999 - i * 120 + random.randint(-30, 30),
            "win_rate": round(0.9 - i * 0.03, 2),
            "playtime": 7200 - i * 180
        }
        for i in range(min(limit, 12))
    ]


def get_player_rank(game: str, username: str) -> int:
    result = _get(f"/leaderboard/{game}/rank/{username}")
    if result and "rank" in result:
        return result["rank"]
    return -1


def get_score_range(game: str, lo: int, hi: int) -> List[Dict]:
    result = _get(f"/leaderboard/{game}/range", {"min": lo, "max": hi})
    return result or []


# ── Player search ─────────────────────────────────────────────────────────────

def search_players(prefix: str) -> List[Dict]:
    if len(prefix) < 1:
        return []

    result = _get("/search", {"prefix": prefix})
    if result:
        return result

    sample = ["Hamza", "Hannah", "Harrison", "Harold", "Harper",
              "Harry", "Harvey", "Hassan", "Hayden", "Heath"]

    matches = [n for n in sample if n.lower().startswith(prefix.lower())]
    return [{"username": n, "score": 1000 - i * 50} for i, n in enumerate(matches)]


# ── Match history ─────────────────────────────────────────────────────────────

def get_history(username: str, game: str = None, sort: str = "date") -> List[Dict]:
    params = {"sort": sort}
    if game:
        params["game"] = game

    result = _get(f"/history/{username}", params)
    if result:
        return result

    import random, datetime
    games = ["dungeon_crawler", "space_shooter", "platform_runner", "tower_defense"]

    history = []
    for i in range(15):
        d = datetime.date.today() - datetime.timedelta(days=i * 2 + random.randint(0, 3))
        history.append({
            "game": random.choice(games),
            "date": str(d),
            "score": random.randint(50, 800),
            "duration_sec": random.randint(60, 900),
            "outcome": random.choice(["win", "loss", "draw"]),
        })

    return history


# ── Game catalog ──────────────────────────────────────────────────────────────

def get_catalog(sort: str = "most_played") -> List[Dict]:
    result = _get("/games", {"sort": sort})
    if result:
        return result

    games = [
        ("dungeon_crawler", "Dungeon Crawler", True, "RPG action dungeon game", 4200, 8.4),
        ("space_shooter", "Space Shooter", True, "Side-scroll shoot-em-up", 3800, 7.9),
    ]

    return [
        {"id": g[0], "name": g[1], "playable": g[2], "desc": g[3],
         "sessions": g[4], "avg_score": g[5]}
        for g in games
    ]


# ── Chat ──────────────────────────────────────────────────────────────────────

def get_chat(game: str, limit: int = 50) -> List[Dict]:
    result = _get(f"/chat/{game}", {"limit": limit})
    if result:
        return result

    return [
        {"username": "Alex", "message": "GG everyone!", "ts": "14:22"},
        {"username": "Jordan", "message": "Anyone want to party up?", "ts": "14:21"},
        {"username": "Sam", "message": "That boss was tough", "ts": "14:20"},
    ]


def send_chat(game: str, username: str, message: str) -> bool:
    result = _post(f"/chat/{game}", {"username": username, "message": message})
    return result is not None
