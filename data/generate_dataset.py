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

TODO (DONE)(DATASET QUALITY):
    The normal generator creates clean records with valid cross-references.
    Optional noisy data can be added with --include-noise for cleaning demos.
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_PLAYER_COUNT = 10_000
DEFAULT_SESSION_COUNT = 100_000
DEFAULT_CHAT_COUNT = 50_000
DEFAULT_GAME_COUNT = 120
DEFAULT_SEED = 3822

# set output folder and synthetic platform date range
DATASET_DIR = Path(__file__).resolve().parent / "synthetic_dataset"
START_DATE = datetime(2025, 4, 20, 8, 0, 0)
END_DATE = datetime(2026, 4, 20, 8, 0, 0)

# shared random choices used across generated records
GENRES = [
    "Action",
    "Adventure",
    "Racing",
    "Strategy",
    "Puzzle",
    "Arcade",
    "Co-op",
    "Platformer",
]

REGIONS = ["NA-East", "NA-West", "EU", "LATAM", "APAC"]
COUNTRIES = ["US", "CA", "MX", "BR", "GB", "DE", "JP", "KR", "IN", "AU"]
OUTCOMES = ["Win", "Loss", "Draw", "Quit"]

# simple reusable chat messages for fake chat history
CHAT_SNIPPETS = [
    "good luck",
    "nice round",
    "again?",
    "defend left",
    "push now",
    "great save",
    "gg",
    "one more match",
    "watch the timer",
    "close game",
]


def random_timestamp(rng: random.Random) -> str:
    '''generate random timestamp within platform date range'''
    """Return a timestamp within the platform's synthetic active year."""

    # calculate total seconds between start and end date
    total_seconds = int((END_DATE - START_DATE).total_seconds())

    # return random timestamp inside the active year
    return (START_DATE + timedelta(seconds=rng.randint(0, total_seconds))).isoformat(timespec="seconds")


def write_json(path: Path, rows: list[dict[str, object]]) -> None:
    '''write compact json file to disk'''
    """Write compact JSON so the committed dataset stays reasonably small."""

    # create parent directory if it does not exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # write json using compact separators to reduce file size
    with path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, separators=(",", ":"))


def generate_players(rng: random.Random, count: int) -> list[dict[str, object]]:
    '''generate synthetic player records'''

    # store generated player dictionaries
    players: list[dict[str, object]] = []

    for index in range(1, count + 1):
        # choose player genre preference and creation date
        genre = rng.choice(GENRES)
        created_at = random_timestamp(rng)

        # create one player row
        players.append(
            {
                "player_id": f"player_{index:05d}",
                "username": f"scorpion_{index:05d}",
                "display_name": f"Scorpion {index:05d}",
                "created_at": created_at,
                "region": rng.choice(REGIONS),
                "country": rng.choice(COUNTRIES),
                "favorite_genre": genre,
                "level": rng.randint(1, 100),
                "skill_rating": rng.randint(500, 2500),
                "total_score": rng.randint(0, 2_500_000),
                "games_played": rng.randint(1, 950),
                "wins": rng.randint(0, 600),
                "losses": rng.randint(0, 600),
                "avatar": f"avatar_{rng.randint(1, 24):02d}.png",
                "account_status": "active",
            }
        )

    return players


def generate_game_catalog(rng: random.Random, count: int) -> list[dict[str, object]]:
    '''generate game catalog including team games and placeholder games'''

    # store generated game records
    games: list[dict[str, object]] = []

    # fixed team games shown first in catalog
    team_games = [
        ("game_1", "Fruit Drop Rush", "Team Member 1", "Arcade"),
        ("game_2", "Escape the City", "Team Member 2", "Action"),
        ("game_3", "Forgotten", "Team Member 3", "Strategy"),
        ("game_4", "Mystical Bamboo", "Team Member 4", "Puzzle"),
        ("game_5", "Game 5 Snake Test", "Team Scorpions", "Arcade"),
    ]

    # project root used to check whether launch files exist
    project_root = Path(__file__).resolve().parents[1]

    for game_id, title, creator, genre in team_games:
        # use different launch path for test game
        if game_id == "game_5":
            launch_path = "games/game_5/main.py"
            playable = (project_root / launch_path).exists()
        else:
            launch_path = f"games/{game_id}/code/game/main.py"
            playable = (project_root / launch_path).exists()

        # generate current active player count
        active_players = rng.randint(0, 6_000)

        # create team game catalog row
        games.append(
            {
                "game_id": game_id,
                "title": title,
                "creator": creator,
                "genre": genre,
                "description": f"{title} is a {genre.lower()} team game entry with seasonal sessions, leaderboard data, and platform history.",
                "playable": playable,
                "launch_path": launch_path if playable else "",
                "thumbnail_path": f"client/assets/thumbnails/{game_id}.png",
                "screenshot_paths": [f"client/assets/screenshots/{game_id}_preview.png"],
                "created_at": random_timestamp(rng),
                "last_updated": random_timestamp(rng),
                "total_plays": rng.randint(10_000, 2_000_000),
                "currently_playing": active_players,
                "players_now": active_players,
                "min_players": 1,
                "max_players": rng.randint(1, 8),
                "supports_multiplayer": game_id not in ("game_1", "game_5"),
                "status": "TEMP TEST GAME - Safe to delete later" if game_id == "game_5" else ("Playable now" if playable else "Pending integration"),
                "tags": ["temp-test-game", genre.lower(), "safe-to-delete"] if game_id == "game_5" else ["team-game", genre.lower(), "folder-convention"],
            }
        )

    # fill remaining catalog with synthetic placeholder games
    for index in range(len(games) + 1, count + 1):
        # create fake game identity and genre
        game_id = f"catalog_game_{index:03d}"
        genre = rng.choice(GENRES)

        # create fake title from adjective + noun
        title = f"{rng.choice(['Neon', 'Cyber', 'Turbo', 'Pixel', 'Orbit', 'Shadow', 'Crystal'])} {rng.choice(['Arena', 'Run', 'Quest', 'Rally', 'Tower', 'Dash', 'League'])} {index:03d}"

        # generate current active player count
        active_players = rng.randint(0, 2_500)

        # create placeholder catalog row
        games.append(
            {
                "game_id": game_id,
                "title": title,
                "creator": f"Student Studio {rng.randint(1, 48):02d}",
                "genre": genre,
                "description": f"{title} is a long-running {genre.lower()} catalog game with realistic platform metadata.",
                "playable": False,
                "launch_path": "",
                "thumbnail_path": f"client/assets/thumbnails/{game_id}.png",
                "screenshot_paths": [f"client/assets/screenshots/{game_id}_preview.png"],
                "created_at": random_timestamp(rng),
                "last_updated": random_timestamp(rng),
                "total_plays": rng.randint(1_000, 900_000),
                "currently_playing": active_players,
                "players_now": active_players,
                "min_players": 1,
                "max_players": rng.randint(1, 10),
                "supports_multiplayer": rng.choice([True, False]),
                "status": "Catalog placeholder",
                "tags": ["student-game", genre.lower(), "synthetic"],
            }
        )

    return games


def generate_sessions(rng: random.Random, count: int, players: list[dict[str, object]], games: list[dict[str, object]]) -> list[dict[str, object]]:
    '''generate synthetic game session records'''

    # store generated session rows
    sessions: list[dict[str, object]] = []

    for index in range(1, count + 1):
        # randomly connect each session to a player and game
        player = rng.choice(players)
        game = rng.choice(games)

        # generate gameplay result data
        duration = rng.randint(45, 3_600)
        score = rng.randint(0, 250_000)

        # generate start and end timestamps
        started_at = random_timestamp(rng)
        ended_at = (datetime.fromisoformat(started_at) + timedelta(seconds=duration)).isoformat(timespec="seconds")

        # create session row
        sessions.append(
            {
                "session_id": f"session_{index:06d}",
                "player_id": player["player_id"],
                "username": player["username"],
                "game_id": game["game_id"],
                "game_title": game["title"],
                "started_at": started_at,
                "ended_at": ended_at,
                "duration_seconds": duration,
                "score": score,
                "outcome": rng.choices(OUTCOMES, weights=[42, 42, 8, 8], k=1)[0],
                "platform": rng.choice(["desktop", "laptop", "lab-pc"]),
                "server_region": rng.choice(REGIONS),
            }
        )

    # sort sessions from oldest to newest
    sessions.sort(key=lambda row: str(row["started_at"]))
    return sessions


def generate_chat_messages(rng: random.Random, count: int, sessions: list[dict[str, object]]) -> list[dict[str, object]]:
    '''generate synthetic chat message records'''

    # store generated chat messages
    messages: list[dict[str, object]] = []

    for index in range(1, count + 1):
        # connect message to a random session
        session = rng.choice(sessions)

        # generate message time and text
        sent_at = random_timestamp(rng)
        text = rng.choice(CHAT_SNIPPETS)

        # create chat message row
        messages.append(
            {
                "message_id": f"message_{index:06d}",
                "session_id": session["session_id"],
                "player_id": session["player_id"],
                "username": session["username"],
                "game_id": session["game_id"],
                "sent_at": sent_at,
                "timestamp": sent_at,
                "text": text,
                "message": text,
                "moderation_status": "clean",
            }
        )

    # sort messages from oldest to newest
    messages.sort(key=lambda row: str(row["sent_at"]))
    return messages


def add_noisy_records(players: list[dict[str, object]], sessions: list[dict[str, object]], chat_messages: list[dict[str, object]]) -> None:
    '''add intentionally bad rows for optional cleaning tests'''
    """Add a tiny number of intentionally bad rows for cleaning demonstrations."""

    # duplicate first player to test duplicate detection
    if players:
        duplicate = dict(players[0])
        duplicate["display_name"] = "Duplicate Demo Player"
        players.append(duplicate)

    # add bad session row with missing IDs, bad date, invalid score, and bad outcome
    sessions.append({"session_id": "bad_session_negative_score", "player_id": "", "username": "", "game_id": "missing_game", "started_at": "bad-date", "duration_seconds": -1, "score": -25, "outcome": "Unknown"})

    # add bad chat row with empty fields
    chat_messages.append({"message_id": "bad_message_empty", "session_id": "", "player_id": "", "game_id": "", "sent_at": "bad-date", "text": ""})


def generate_dataset(player_count: int, session_count: int, chat_count: int, game_count: int, seed: int, include_noise: bool = False) -> None:
    '''generate all synthetic dataset files'''

    # create deterministic random generator using seed
    rng = random.Random(seed)

    # generate each dataset table
    games = generate_game_catalog(rng, game_count)
    players = generate_players(rng, player_count)
    sessions = generate_sessions(rng, session_count, players, games)
    chat_messages = generate_chat_messages(rng, chat_count, sessions)

    # optionally add invalid/noisy records for cleaning demos
    if include_noise:
        add_noisy_records(players, sessions, chat_messages)

    # write dataset files
    write_json(DATASET_DIR / "players.json", players)
    write_json(DATASET_DIR / "game_catalog.json", games)
    write_json(DATASET_DIR / "sessions.json", sessions)
    write_json(DATASET_DIR / "chat_messages.json", chat_messages)

    # store dataset summary metadata
    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "seed": seed,
        "player_count": len(players),
        "session_count": len(sessions),
        "chat_message_count": len(chat_messages),
        "game_catalog_count": len(games),
        "date_range": {"start": START_DATE.isoformat(timespec="seconds"), "end": END_DATE.isoformat(timespec="seconds")},
        "submission_note": "Commit data/synthetic_dataset/*.json with the project submission.",
        "include_noise": include_noise,
    }

    # write manifest as one-row list for consistent JSON loading
    write_json(DATASET_DIR / "manifest.json", [manifest])


def parse_args() -> argparse.Namespace:
    '''parse command line options'''

    # build CLI parser for dataset generator
    parser = argparse.ArgumentParser(description="Generate the Scorpions Arcade synthetic dataset.")

    # dataset size options
    parser.add_argument("--players", type=int, default=DEFAULT_PLAYER_COUNT)
    parser.add_argument("--sessions", type=int, default=DEFAULT_SESSION_COUNT)
    parser.add_argument("--chat", type=int, default=DEFAULT_CHAT_COUNT)
    parser.add_argument("--games", type=int, default=DEFAULT_GAME_COUNT)

    # reproducibility and noisy-data option
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--include-noise", action="store_true", help="Add a few intentionally invalid rows for cleaning demonstrations.")

    return parser.parse_args()


def main() -> None:
    '''main script entry point'''

    # parse CLI arguments
    args = parse_args()

    # generate dataset using requested arguments
    generate_dataset(args.players, args.sessions, args.chat, args.games, args.seed, args.include_noise)

    # print final reminder
    print(f"Synthetic dataset written to {DATASET_DIR}")
    print("Reminder: commit data/synthetic_dataset/*.json with the final project.")


if __name__ == "__main__":
    main()