"""
local_db.py — Persistent local storage for the ECE 3822 Arcade.

Stores all data in arcade_data.json next to this file so it survives
restarts and is shared across all players on the same machine.

Data layout:
{
  "users": {
    "hamza": {
      "password": "abc123",          # plaintext (ok for class project)
      "created":  "2026-04-12",
      "display":  "Hamza"            # original-case username
    }
  },
  "sessions": [
    {
      "username": "hamza",
      "game":     "excape_the_city",
      "score":    420,
      "outcome":  "win",
      "date":     "2026-04-12",
      "duration": 312
    }
  ],
  "chat": {
    "excape_the_city": [
      {"username":"hamza","message":"gg","ts":"14:22"}
    ]
  }
}
"""

import os
import json
import datetime
from typing import Optional

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arcade_data.json")

_EMPTY = {"users": {}, "sessions": [], "chat": {}}


# ── Load / Save ───────────────────────────────────────────────────────────────

def _load() -> dict:
    if os.path.isfile(_DB_PATH):
        try:
            with open(_DB_PATH, "r") as f:
                data = json.load(f)
                # ensure all keys exist
                for k in _EMPTY:
                    if k not in data:
                        data[k] = _EMPTY[k]
                return data
        except Exception:
            pass
    return {k: v.copy() for k, v in _EMPTY.items()}


def _save(data: dict):
    try:
        with open(_DB_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[db] Warning: could not save data: {e}")


# ── Auth ──────────────────────────────────────────────────────────────────────

def register(username: str, password: str) -> Optional[dict]:
    """
    Create a new account. Returns user dict on success, None if taken.
    """
    db  = _load()
    key = username.lower().strip()
    if not key:
        return None
    if key in db["users"]:
        return None   # username taken
    db["users"][key] = {
        "password": password,
        "created":  str(datetime.date.today()),
        "display":  username.strip(),
    }
    _save(db)
    return db["users"][key]


def login(username: str, password: str) -> Optional[dict]:
    """
    Verify credentials. Returns user dict on success, None on failure.
    """
    db  = _load()
    key = username.lower().strip()
    u   = db["users"].get(key)
    if u and u["password"] == password:
        return u
    return None


def user_exists(username: str) -> bool:
    db = _load()
    return username.lower().strip() in db["users"]


def get_display_name(username: str) -> str:
    db  = _load()
    key = username.lower().strip()
    u   = db["users"].get(key)
    return u["display"] if u else username


# ── Sessions ──────────────────────────────────────────────────────────────────

def add_session(username: str, game: str, score: int,
                outcome: str = "draw", duration: int = 0):
    """Record a completed game session."""
    db = _load()
    db["sessions"].append({
        "username": username.lower().strip(),
        "game":     game,
        "score":    score,
        "outcome":  outcome,
        "date":     str(datetime.date.today()),
        "duration": duration,
    })
    _save(db)


def get_history(username: str, game: str = None, sort: str = "date") -> list:
    """Return session history for a player, newest first."""
    db   = _load()
    key  = username.lower().strip()
    rows = [s for s in db["sessions"] if s["username"] == key]
    if game:
        rows = [s for s in rows if s["game"] == game]
    if sort == "score":
        rows.sort(key=lambda s: s["score"], reverse=True)
    else:
        rows.sort(key=lambda s: s["date"], reverse=True)
    return rows


def get_profile(username: str) -> dict:
    """Compute profile stats from stored sessions."""
    db   = _load()
    key  = username.lower().strip()
    u    = db["users"].get(key, {})
    rows = [s for s in db["sessions"] if s["username"] == key]

    games_played = len(rows)
    wins         = sum(1 for s in rows if s["outcome"] == "win")
    win_rate     = round(wins / games_played, 3) if games_played else 0
    total_time   = sum(s.get("duration", 0) for s in rows)
    scores       = [s["score"] for s in rows]
    score_hist   = scores[-20:]   # last 20 scores for sparkline

    # best game
    game_wins = {}
    for s in rows:
        g = s["game"]
        if g not in game_wins: game_wins[g] = 0
        if s["outcome"] == "win": game_wins[g] += 1
    fav = max(game_wins, key=game_wins.get) if game_wins else ""

    # global rank by total score
    all_scores = {}
    for s in db["sessions"]:
        u2 = s["username"]
        all_scores[u2] = all_scores.get(u2, 0) + s["score"]
    ranked = sorted(all_scores, key=all_scores.get, reverse=True)
    rank = ranked.index(key) + 1 if key in ranked else 0

    return {
        "username":      u.get("display", username),
        "games_played":  games_played,
        "wins":          wins,
        "win_rate":      win_rate,
        "total_playtime":total_time,
        "score_history": score_hist,
        "favorite_game": fav,
        "rank":          rank,
        "country":       u.get("country", ""),
    }


# ── Leaderboard ───────────────────────────────────────────────────────────────

def get_leaderboard(game: str, sort: str = "score", limit: int = 20) -> list:
    """Return top players for a game."""
    db = _load()
    rows = [s for s in db["sessions"] if s["game"] == game]

    # Aggregate per user
    agg = {}
    for s in rows:
        u = s["username"]
        if u not in agg:
            agg[u] = {"username": u, "score": 0, "wins": 0, "total": 0, "playtime": 0}
        agg[u]["score"]    = max(agg[u]["score"], s["score"])
        agg[u]["total"]   += s["score"]
        agg[u]["playtime"] += s.get("duration", 0)
        agg[u]["total_games"] = agg[u].get("total_games", 0) + 1
        if s["outcome"] == "win":
            agg[u]["wins"] += 1

    players = list(agg.values())
    for p in players:
        tg = p.get("total_games", 1) or 1
        p["win_rate"] = round(p["wins"] / tg, 2)
        # use display name
        db_u = db["users"].get(p["username"], {})
        p["username"] = db_u.get("display", p["username"])

    if sort == "winrate":
        players.sort(key=lambda p: p["win_rate"], reverse=True)
    elif sort == "playtime":
        players.sort(key=lambda p: p["playtime"], reverse=True)
    else:
        players.sort(key=lambda p: p["score"], reverse=True)

    for i, p in enumerate(players):
        p["rank"] = i + 1

    return players[:limit]


def get_player_rank(game: str, username: str) -> int:
    board = get_leaderboard(game, limit=1000)
    key   = username.lower()
    for p in board:
        if p["username"].lower() == key:
            return p["rank"]
    return -1


def get_score_range(game: str, lo: int, hi: int) -> list:
    board = get_leaderboard(game, limit=1000)
    return [p for p in board if lo <= p["score"] <= hi]


# ── Search ────────────────────────────────────────────────────────────────────

def search_players(prefix: str) -> list:
    if not prefix:
        return []
    db  = _load()
    key = prefix.lower()
    out = []
    for ukey, u in db["users"].items():
        if ukey.startswith(key) or u["display"].lower().startswith(key):
            rows = [s for s in db["sessions"] if s["username"] == ukey]
            out.append({
                "username": u["display"],
                "score":    sum(s["score"] for s in rows),
            })
    return sorted(out, key=lambda x: x["score"], reverse=True)[:10]


# ── Chat ──────────────────────────────────────────────────────────────────────

def get_chat(game: str, limit: int = 50) -> list:
    db = _load()
    msgs = db["chat"].get(game, [])
    return msgs[-limit:]


def send_chat(game: str, username: str, message: str):
    db = _load()
    if game not in db["chat"]:
        db["chat"][game] = []
    import datetime as _dt
    db["chat"][game].append({
        "username": username,
        "message":  message,
        "ts":       _dt.datetime.now().strftime("%H:%M"),
    })
    # keep last 200 messages per game
    db["chat"][game] = db["chat"][game][-200:]
    _save(db)


# ── All users (for admin / demo) ──────────────────────────────────────────────

def all_users() -> list:
    db = _load()
    return [u["display"] for u in db["users"].values()]
