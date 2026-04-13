"""
game_launcher.py — Discovers and launches team games for ECE 3822 Arcade.

Looks for games in the GAMES/ folder at the repo root.
Each game follows this structure (same as your Excape_the_city):

    GAMES/
      Excape_the_city/
        code/
          game/
            main.py       ← entry point
            config.json   ← optional display metadata
      Joy_Game/
        code/
          game/
            main.py
      Kevin_Game/
        code/
          game/
            main.py
      Mykai_Game/
        code/
          game/
            main.py

config.json (optional, place inside code/game/):
{
    "name":        "Escape the City",
    "description": "RPG dungeon escape game",
    "players":     "1-4",
    "author":      "Hamza"
}

The launcher spawns each game as a subprocess so the arcade UI stays alive.
When the player closes the game, the arcade detects this and returns them to lobby.
"""

import os
import sys
import json
import subprocess
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────────

# arcadeui/ is one level below the repo root, so GAMES/ is at ../GAMES/
_ARCADE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT   = os.path.dirname(_ARCADE_DIR)

# Try both 'games' and 'GAMES' — handle case differences on the server
def _find_games_dir():
    for name in ("games", "GAMES", "Games"):
        p = os.path.join(_REPO_ROOT, name)
        if os.path.isdir(p):
            return p
    # fallback
    return os.path.join(_REPO_ROOT, "games")

GAMES_DIR = _find_games_dir()

# Subdirectory within each game folder that contains main.py
# Matches your structure: GAMES/<GameName>/code/game/main.py
GAME_SUBPATH = os.path.join("code", "game")



# ── Discovery ─────────────────────────────────────────────────────────────────

# Games that use positional name + --server (your existing game format)
SCORPIONS_FOLDERS = {"Excape_the_city"}

def _find_main(folder_path: str):
    """
    Try multiple locations for main.py:
      1. GAMES/<Folder>/code/game/main.py  (Excape_the_city layout)
      2. GAMES/<Folder>/main.py            (mini-games layout)
    Returns (game_path, main_py) or (None, None).
    """
    # Deep path first
    deep = os.path.join(folder_path, GAME_SUBPATH, "main.py")
    if os.path.isfile(deep):
        return os.path.dirname(deep), deep
    # Flat path
    flat = os.path.join(folder_path, "main.py")
    if os.path.isfile(flat):
        return folder_path, flat
    return None, None


def discover_games() -> dict:
    """
    Scan GAMES/ folder and return dict of {game_id: metadata}.

    Supports two layouts:
      GAMES/<Folder>/main.py               (mini-games)
      GAMES/<Folder>/code/game/main.py     (Excape_the_city)

    arg_style is auto-detected:
      Folders in SCORPIONS_FOLDERS  ->  "scorpions"
      Everything else               ->  "standard"
    """
    found = {}

    if not os.path.isdir(GAMES_DIR):
        print(f"[launcher] GAMES/ folder not found at: {GAMES_DIR}")
        return found

    for folder_name in sorted(os.listdir(GAMES_DIR)):
        folder_path = os.path.join(GAMES_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        game_path, main_py = _find_main(folder_path)
        if main_py is None:
            print(f"[launcher] Skipping {folder_name} — no main.py found")
            continue

        # Load config.json from same dir as main.py
        config_path = os.path.join(game_path, "config.json")
        meta = {}
        if os.path.isfile(config_path):
            try:
                with open(config_path) as f:
                    meta = json.load(f)
            except Exception as e:
                print(f"[launcher] Warning: bad config.json in {folder_name}: {e}")

        # Auto-detect arg style
        if folder_name in SCORPIONS_FOLDERS:
            arg_style = "scorpions"
        else:
            arg_style = meta.get("arg_style", "standard")

        game_id = folder_name.lower().replace(" ", "_")

        found[game_id] = {
            "id":          game_id,
            "folder":      folder_name,
            "name":        meta.get("name",        folder_name.replace("_", " ").title()),
            "description": meta.get("description", "No description yet."),
            "players":     meta.get("players",     "1-4"),
            "author":      meta.get("author",      "Team Scorpions"),
            "arg_style":   arg_style,
            "path":        game_path,
            "main":        main_py,
            "playable":    True,
        }
        print(f"[launcher] Found: {game_id} ({arg_style}) -> {main_py}")

    return found


def get_game_meta(game_id: str) -> Optional[dict]:
    return discover_games().get(game_id)


# ── Launch ────────────────────────────────────────────────────────────────────

def launch_game(game_id: str,
                username:    str = "",
                server_host: str = "localhost",
                server_port: int = 9000) -> subprocess.Popen:
    """
    Launch a game as a subprocess.

    Supports two arg styles, set via config.json "arg_style":
      "scorpions"  ->  <name> --server <host> --port <port>
                       (matches your existing Escape the City argparse format)
      "standard"   ->  --username <name> --host <host> --port <port>
                       (used by the mini-games built for this arcade)
    """
    meta = get_game_meta(game_id)
    if not meta:
        raise FileNotFoundError(
            f"Game '{game_id}' not found.\n"
            f"Expected: {GAMES_DIR}/<folder>/{GAME_SUBPATH}/main.py\n"
            f"Available: {list(discover_games().keys()) or 'none'}"
        )

    arg_style = meta.get("arg_style", "standard")
    name = username or "Player"

    if arg_style == "scorpions":
        # Your existing game: positional name + --server + --port
        cmd = [
            sys.executable, meta["main"],
            name,
            "--server", server_host,
            "--port",   str(server_port),
        ]
    else:
        # New mini-games: --username + --host + --port
        cmd = [
            sys.executable, meta["main"],
            "--username", name,
            "--host",     server_host,
            "--port",     str(server_port),
        ]

    print(f"[launcher] Launching {meta['name']} (style={arg_style}): {name}@{server_host}:{server_port}")
    proc = subprocess.Popen(cmd, cwd=meta["path"])
    return proc


def is_running(proc: Optional[subprocess.Popen]) -> bool:
    if proc is None:
        return False
    return proc.poll() is None


def stop_game(proc: Optional[subprocess.Popen]):
    if proc and is_running(proc):
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


# ── Config helper ─────────────────────────────────────────────────────────────

def create_stub_games():
    """Write a config.json into each game folder that's missing one."""
    if not os.path.isdir(GAMES_DIR):
        print(f"[launcher] GAMES/ not found — nothing to stub.")
        return

    defaults = {
        "Excape_the_city": ("Escape the City", "RPG action dungeon game", "Hamza", "scorpions"),
        "Joy_Game":        ("Joy's Game",       "Coming soon",            "Joy"),
        "Kevin_Game":      ("Kevin's Game",     "Coming soon",            "Kevin"),
        "Mykai_Game":      ("Mykai's Game",     "Coming soon",            "Mykai"),
    }

    for folder_name in os.listdir(GAMES_DIR):
        folder_path = os.path.join(GAMES_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
        game_path = os.path.join(folder_path, GAME_SUBPATH)
        os.makedirs(game_path, exist_ok=True)
        conf = os.path.join(game_path, "config.json")
        if not os.path.exists(conf):
            entry = defaults.get(folder_name)
            if entry and len(entry) == 4:
                name, desc, author, arg_style = entry
            elif entry:
                name, desc, author = entry
                arg_style = "standard"
            else:
                name = folder_name.replace("_"," ").title()
                desc = "No description."; author = "Unknown"; arg_style = "standard"
            with open(conf, "w") as f:
                json.dump({"name": name, "description": desc,
                           "players": "1-4", "author": author,
                           "arg_style": arg_style}, f, indent=4)
            print(f"[launcher] Created config.json for {folder_name}")


# ── Quick test (run this file directly to verify paths) ──────────────────────

if __name__ == "__main__":
    print(f"Repo root : {_REPO_ROOT}")
    print(f"GAMES dir : {GAMES_DIR}")
    print(f"Subpath   : {GAME_SUBPATH}\n")
    games = discover_games()
    if games:
        print(f"Discovered {len(games)} game(s):")
        for gid, m in games.items():
            print(f"  {gid:30s} -> {m['main']}")
    else:
        print("No games with main.py found yet.")
    create_stub_games()
