from __future__ import annotations

"""Synthetic dataset generator for Scorpions Arcade.

Purpose:
    Create the dataset that must be committed and submitted with the project.
    The generated records model an arcade platform that has been active for
    about one year.

Important:
    This script creates data only. It does not implement final search,
    leaderboard, history, chat, or custom data-structure logic.

Default target sizes:
    - 10,000 player records
    - 100,000 game session records
    - 50,000 chat message records
    - 120 game catalog records

Run:
    python data/generate_dataset.py

SUBMISSION REQUIREMENT:
    The generated files in data/synthetic_dataset/ MUST be committed and
    submitted with the final project. Do not add synthetic_dataset/ to
    .gitignore. Re-run this script if the files are missing, then commit.

TODO(DATASET QUALITY):
    Add optional noisy-data mode later if the professor expects cleaning tests:
    missing fields, duplicate usernames, invalid scores, bad timestamps, etc.

Field reference (all fields documented below per record type):

  players.json — one record per registered player
    player_id       : unique ID, e.g. "player_00001"
    username        : login handle, e.g. "scorpion_00001"
    display_name    : shown in UI, e.g. "Scorpion 00001"
    created_at      : ISO-8601 account creation timestamp
    region          : server region (NA-East, NA-West, EU, LATAM, APAC)
    country         : two-letter ISO 3166-1 alpha-2 country code, e.g. "US"
    favorite_genre  : player's preferred game genre
    level           : platform level derived from games_played (1–100)
    skill_rating    : matchmaking rating, 500–2500
    total_score     : cumulative score across all sessions
    games_played    : total sessions completed
    wins            : sessions with outcome == "Win"
    losses          : sessions with outcome == "Loss"
    avatar          : filename of chosen avatar image
    account_status  : always "active" in synthetic data

  sessions.json — one record per play session
    session_id      : unique ID, e.g. "session_000001"
    player_id       : foreign key → players.player_id
    username        : denormalised for fast display
    game_id         : foreign key → game_catalog.game_id
    game_title      : denormalised for fast display
    started_at      : ISO-8601 session start timestamp
    ended_at        : ISO-8601 session end (started_at + duration_seconds)
    duration_seconds: session length in seconds (45–3600)
    score           : points scored in this session (0–250,000)
    outcome         : Win | Loss | Draw | Quit
    platform        : client device type (desktop, laptop, lab-pc)
    server_region   : region that hosted the session

  chat_messages.json — one record per chat message
    message_id      : unique ID, e.g. "message_000001"
    session_id      : foreign key → sessions.session_id
    player_id       : foreign key → players.player_id
    username        : denormalised for fast display
    game_id         : game context for the message
    timestamp       : ISO-8601 send time  (also stored as sent_at for compat)
    sent_at         : ISO-8601 send time  (kept for backward compatibility)
    message         : message text        (also stored as text for compat)
    text            : message text        (kept for backward compatibility)
    moderation_status: always "clean" in synthetic data

  game_catalog.json — one record per game in the catalog
    game_id         : unique ID, e.g. "game_1" or "catalog_game_006"
    title           : display title
    creator         : author name or studio
    genre           : game genre
    description     : one-sentence summary of the game
    playable        : True if the game can be launched on this platform
    launch_path     : module or file path used to start the game
    thumbnail_path  : relative path to thumbnail image asset
    screenshot_paths: list of relative paths to preview screenshots
    created_at      : ISO-8601 catalog addition timestamp
    last_updated    : ISO-8601 last metadata update timestamp
    total_plays     : cumulative play count
    players_now     : current concurrent players  (also as currently_playing)
    currently_playing: current concurrent players (kept for backward compat)
    min_players     : minimum players required
    max_players     : maximum players supported
    supports_multiplayer: True if multiplayer is available
    status          : short human-readable status note
    tags            : list of classification tags
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_PLAYER_COUNT  = 10_000
DEFAULT_SESSION_COUNT = 100_000
DEFAULT_CHAT_COUNT    = 50_000
DEFAULT_GAME_COUNT    = 120
DEFAULT_SEED          = 3822

DATASET_DIR = Path(__file__).resolve().parent / "synthetic_dataset"
START_DATE  = datetime(2025, 4, 20, 8, 0, 0)
END_DATE    = datetime(2026, 4, 20, 8, 0, 0)

GENRES   = ["Action", "Adventure", "Racing", "Strategy",
            "Puzzle", "Arcade", "Co-op", "Platformer"]
REGIONS  = ["NA-East", "NA-West", "EU", "LATAM", "APAC"]
OUTCOMES = ["Win", "Loss", "Draw", "Quit"]

# ISO 3166-1 alpha-2 country codes — realistic spread across regions
COUNTRIES = [
    "US", "US", "US", "CA", "MX", "BR", "AR",   # NA / LATAM heavy
    "GB", "DE", "FR", "ES", "IT", "NL", "PL",   # EU
    "JP", "KR", "AU", "IN", "SG",               # APAC
]

CHAT_SNIPPETS = [
    "good luck", "nice round", "again?", "defend left", "push now",
    "great save", "gg", "one more match", "watch the timer", "close game",
]

# Short descriptions for synthetic catalog games — cycled by index
_CATALOG_DESCRIPTIONS = [
    "A fast-paced arcade experience with procedurally generated levels.",
    "Compete against others in this skill-based score attack game.",
    "Navigate obstacles and collect power-ups to climb the leaderboard.",
    "A strategic title where every decision affects your final score.",
    "Team up or go solo in this high-energy multiplayer challenge.",
    "Master combos and chain reactions to reach the top of the rankings.",
    "An endurance game — how long can you survive the increasing difficulty?",
    "Race the clock and outplay rivals in this competitive arena.",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_timestamp(rng: random.Random) -> str:
    """Return a random ISO-8601 timestamp within the platform's active year."""
    total_seconds = int((END_DATE - START_DATE).total_seconds())
    return (START_DATE + timedelta(seconds=rng.randint(0, total_seconds))).isoformat(timespec="seconds")


def add_seconds_to_iso(iso: str, seconds: int) -> str:
    """Add `seconds` to an ISO-8601 timestamp string and return the result."""
    dt = datetime.fromisoformat(iso)
    return (dt + timedelta(seconds=seconds)).isoformat(timespec="seconds")


def write_json(path: Path, rows: list[dict[str, object]]) -> None:
    """Write compact JSON so the committed dataset stays reasonably small."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_players(rng: random.Random, count: int) -> list[dict[str, object]]:
    """
    Generate `count` player records.

    level   : 1 + (games_played // 10), capped at 100.
              Represents platform progression visible on player profiles.
    wins    : synthetic win count — roughly 42 % of games_played.
    losses  : synthetic loss count — roughly 42 % of games_played.
              Remaining ~16 % are draws or quits (matches OUTCOMES weights).
    country : random ISO 3166-1 alpha-2 code; distribution skewed toward
              US/EU/LATAM to match realistic arcade platform demographics.
    """
    players: list[dict[str, object]] = []
    for index in range(1, count + 1):
        genre       = rng.choice(GENRES)
        created_at  = random_timestamp(rng)
        games_played = rng.randint(1, 950)
        wins         = int(games_played * rng.uniform(0.35, 0.50))
        losses       = int(games_played * rng.uniform(0.35, 0.50))
        level        = min(100, 1 + games_played // 10)
        players.append({
            "player_id":      f"player_{index:05d}",
            "username":       f"scorpion_{index:05d}",
            "display_name":   f"Scorpion {index:05d}",
            "created_at":     created_at,
            "region":         rng.choice(REGIONS),
            "country":        rng.choice(COUNTRIES),   # NEW — ISO 3166-1 alpha-2
            "favorite_genre": genre,
            "level":          level,                   # NEW — 1–100 platform level
            "skill_rating":   rng.randint(500, 2500),
            "total_score":    rng.randint(0, 2_500_000),
            "games_played":   games_played,
            "wins":           wins,                    # NEW — win count
            "losses":         losses,                  # NEW — loss count
            "avatar":         f"avatar_{rng.randint(1, 24):02d}.png",
            "account_status": "active",
        })
    return players


def generate_game_catalog(rng: random.Random, count: int) -> list[dict[str, object]]:
    """
    Generate the game catalog.

    The first 5 entries are the team's real games.
    The remaining entries are synthetic catalog placeholders.

    description  : one-sentence summary used in the browse/search UI.
    players_now  : current concurrent player count (snapshot).
                   Also written as currently_playing for backward compat.
    """
    games: list[dict[str, object]] = []

    # Team's real games — fixed IDs and titles
    team_game_descriptions = {
        "game_1": "Drop and match falling fruit in this colourful arcade puzzle.",
        "game_2": "Race through a city under siege and escape before time runs out.",
        "game_3": "Unravel a forgotten mystery across increasingly difficult strategy stages.",
        "game_4": "Guide a panda through a mystical bamboo forest in this zen puzzler.",
        "game_5": "Classic snake gameplay used for internal team testing.",
    }
    team_games = [
        ("game_1", "Fruit Drop Rush",    "Team Member 1", "Arcade",   True),
        ("game_2", "Escape the City",    "Team Member 2", "Action",   True),
        ("game_3", "Forgotten",          "Team Member 3", "Strategy", True),
        ("game_4", "Mystical Bamboo",    "Team Member 4", "Puzzle",   True),
        ("game_5", "Game 5 Snake Test",  "Team Scorpions","Arcade",   True),
    ]
    for game_id, title, creator, genre, playable in team_games:
        players_now = rng.randint(0, 6_000)
        games.append({
            "game_id":            game_id,
            "title":              title,
            "creator":            creator,
            "genre":              genre,
            "description":        team_game_descriptions[game_id],   # NEW
            "playable":           playable,
            "launch_path":        (
                f"games/{game_id}/code/game/main.py"
                if game_id in {"game_1", "game_2", "game_3", "game_4"}
                else (f"games.{game_id}.main" if playable else "")
            ),
            "thumbnail_path":     f"client/assets/thumbnails/{game_id}.png",
            "screenshot_paths":   [f"client/assets/screenshots/{game_id}_preview.png"],
            "created_at":         random_timestamp(rng),
            "last_updated":       random_timestamp(rng),
            "total_plays":        rng.randint(10_000, 2_000_000),
            "players_now":        players_now,                        # NEW (canonical)
            "currently_playing":  players_now,                        # kept for compat
            "min_players":        1,
            "max_players":        rng.randint(1, 8),
            "supports_multiplayer": game_id not in ("game_1", "game_5"),
            "status": (
                "TEMP TEST GAME - Safe to delete later"
                if game_id == "game_5"
                else f"Uses games/{game_id}/code/game/main.py"
            ),
            "tags": (
                ["temp-test-game", genre.lower(), "safe-to-delete"]
                if game_id == "game_5"
                else ["team-game", genre.lower(), "folder-convention"]
            ),
        })

    # Synthetic catalog placeholders
    adjectives = ["Neon", "Cyber", "Turbo", "Pixel", "Orbit", "Shadow", "Crystal"]
    nouns      = ["Arena", "Run", "Quest", "Rally", "Tower", "Dash", "League"]
    for index in range(len(games) + 1, count + 1):
        game_id     = f"catalog_game_{index:03d}"
        genre       = rng.choice(GENRES)
        title       = f"{rng.choice(adjectives)} {rng.choice(nouns)} {index:03d}"
        description = _CATALOG_DESCRIPTIONS[index % len(_CATALOG_DESCRIPTIONS)]
        players_now = rng.randint(0, 2_500)
        games.append({
            "game_id":            game_id,
            "title":              title,
            "creator":            f"Student Studio {rng.randint(1, 48):02d}",
            "genre":              genre,
            "description":        description,           # NEW
            "playable":           False,
            "launch_path":        "",
            "thumbnail_path":     f"client/assets/thumbnails/{game_id}.png",
            "screenshot_paths":   [f"client/assets/screenshots/{game_id}_preview.png"],
            "created_at":         random_timestamp(rng),
            "last_updated":       random_timestamp(rng),
            "total_plays":        rng.randint(1_000, 900_000),
            "players_now":        players_now,           # NEW (canonical)
            "currently_playing":  players_now,           # kept for compat
            "min_players":        1,
            "max_players":        rng.randint(1, 10),
            "supports_multiplayer": rng.choice([True, False]),
            "status":             "Catalog placeholder",
            "tags":               ["student-game", genre.lower(), "synthetic"],
        })
    return games


def generate_sessions(
    rng: random.Random,
    count: int,
    players: list[dict[str, object]],
    games: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Generate `count` session records.

    ended_at : derived from started_at + duration_seconds.
               Stored as ISO-8601 so history queries can filter by end time.
    """
    sessions: list[dict[str, object]] = []
    for index in range(1, count + 1):
        player   = rng.choice(players)
        game     = rng.choice(games)
        duration = rng.randint(45, 3_600)
        score    = rng.randint(0, 250_000)
        started  = random_timestamp(rng)
        sessions.append({
            "session_id":       f"session_{index:06d}",
            "player_id":        player["player_id"],
            "username":         player["username"],
            "game_id":          game["game_id"],
            "game_title":       game["title"],
            "started_at":       started,
            "ended_at":         add_seconds_to_iso(started, duration),  # NEW
            "duration_seconds": duration,
            "score":            score,
            "outcome":          rng.choices(OUTCOMES, weights=[42, 42, 8, 8], k=1)[0],
            "platform":         rng.choice(["desktop", "laptop", "lab-pc"]),
            "server_region":    rng.choice(REGIONS),
        })
    sessions.sort(key=lambda row: str(row["started_at"]))
    return sessions


def generate_chat_messages(
    rng: random.Random,
    count: int,
    sessions: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Generate `count` chat message records.

    timestamp : canonical send-time field required by the task spec.
    sent_at   : kept alongside timestamp for backward compatibility with
                any existing code that already reads sent_at.
    message   : canonical message-text field required by the task spec.
    text      : kept alongside message for backward compatibility.
    """
    messages: list[dict[str, object]] = []
    for index in range(1, count + 1):
        session   = rng.choice(sessions)
        send_time = random_timestamp(rng)
        msg_text  = rng.choice(CHAT_SNIPPETS)
        messages.append({
            "message_id":        f"message_{index:06d}",
            "session_id":        session["session_id"],
            "player_id":         session["player_id"],
            "username":          session["username"],
            "game_id":           session["game_id"],
            "timestamp":         send_time,   # NEW — canonical field
            "sent_at":           send_time,   # kept for backward compat
            "message":           msg_text,    # NEW — canonical field
            "text":              msg_text,    # kept for backward compat
            "moderation_status": "clean",
        })
    messages.sort(key=lambda row: str(row["timestamp"]))
    return messages


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def generate_dataset(
    player_count: int,
    session_count: int,
    chat_count: int,
    game_count: int,
    seed: int,
) -> None:
    """Generate all dataset files and write them to DATASET_DIR."""
    rng      = random.Random(seed)
    games    = generate_game_catalog(rng, game_count)
    players  = generate_players(rng, player_count)
    sessions = generate_sessions(rng, session_count, players, games)
    chat     = generate_chat_messages(rng, chat_count, sessions)

    write_json(DATASET_DIR / "players.json",      players)
    write_json(DATASET_DIR / "game_catalog.json", games)
    write_json(DATASET_DIR / "sessions.json",     sessions)
    write_json(DATASET_DIR / "chat_messages.json", chat)

    # manifest.json is a single-element list so it matches the same
    # write_json / read_json pattern used for all other dataset files.
    manifest = {
        "generated_at":       datetime.now().isoformat(timespec="seconds"),
        "seed":               seed,
        "player_count":       len(players),
        "session_count":      len(sessions),
        "chat_message_count": len(chat),
        "game_catalog_count": len(games),
        "date_range": {
            "start": START_DATE.isoformat(timespec="seconds"),
            "end":   END_DATE.isoformat(timespec="seconds"),
        },
        "minimum_requirements": {
            "players":       10_000,
            "sessions":      100_000,
            "chat_messages": 50_000,
            "games":         100,
        },
        "requirements_met": {
            "players":       len(players)  >= 10_000,
            "sessions":      len(sessions) >= 100_000,
            "chat_messages": len(chat)     >= 50_000,
            "games":         len(games)    >= 100,
        },
        # SUBMISSION REQUIREMENT — do not remove this note.
        "submission_note": (
            "These files MUST be committed and submitted with the project. "
            "Do not add data/synthetic_dataset/ to .gitignore."
        ),
    }
    write_json(DATASET_DIR / "manifest.json", [manifest])

    # Print a validation summary so the team can confirm counts at a glance.
    print(f"\nDataset written to: {DATASET_DIR}")
    print(f"  players       : {len(players):>8,}  (min 10,000)")
    print(f"  sessions      : {len(sessions):>8,}  (min 100,000)")
    print(f"  chat messages : {len(chat):>8,}  (min 50,000)")
    print(f"  game catalog  : {len(games):>8,}  (min 100)")
    all_ok = all(manifest["requirements_met"].values())
    print(f"\n  All requirements met: {'YES ✓' if all_ok else 'NO ✗ — check counts above'}")
    print("\nReminder: commit data/synthetic_dataset/*.json with the final project.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the Scorpions Arcade synthetic dataset."
    )
    parser.add_argument("--players",  type=int, default=DEFAULT_PLAYER_COUNT)
    parser.add_argument("--sessions", type=int, default=DEFAULT_SESSION_COUNT)
    parser.add_argument("--chat",     type=int, default=DEFAULT_CHAT_COUNT)
    parser.add_argument("--games",    type=int, default=DEFAULT_GAME_COUNT)
    parser.add_argument("--seed",     type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_dataset(args.players, args.sessions, args.chat, args.games, args.seed)


if __name__ == "__main__":
    main()
