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

TODO(DATASET QUALITY):
    Add optional noisy-data mode later if the professor expects cleaning tests:
    missing fields, duplicate usernames, invalid scores, bad timestamps, etc.
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

DATASET_DIR = Path(__file__).resolve().parent / "synthetic_dataset"
START_DATE = datetime(2025, 4, 20, 8, 0, 0)
END_DATE = datetime(2026, 4, 20, 8, 0, 0)

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
OUTCOMES = ["Win", "Loss", "Draw", "Quit"]
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
    """Return a timestamp within the platform's synthetic active year."""

    total_seconds = int((END_DATE - START_DATE).total_seconds())
    return (START_DATE + timedelta(seconds=rng.randint(0, total_seconds))).isoformat(timespec="seconds")


def write_json(path: Path, rows: list[dict[str, object]]) -> None:
    """Write compact JSON so the committed dataset stays reasonably small."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, separators=(",", ":"))


def generate_players(rng: random.Random, count: int) -> list[dict[str, object]]:
    players: list[dict[str, object]] = []
    for index in range(1, count + 1):
        genre = rng.choice(GENRES)
        created_at = random_timestamp(rng)
        players.append(
            {
                "player_id": f"player_{index:05d}",
                "username": f"scorpion_{index:05d}",
                "display_name": f"Scorpion {index:05d}",
                "created_at": created_at,
                "region": rng.choice(REGIONS),
                "favorite_genre": genre,
                "skill_rating": rng.randint(500, 2500),
                "total_score": rng.randint(0, 2_500_000),
                "games_played": rng.randint(1, 950),
                "avatar": f"avatar_{rng.randint(1, 24):02d}.png",
                "account_status": "active",
            }
        )
    return players


def generate_game_catalog(rng: random.Random, count: int) -> list[dict[str, object]]:
    games: list[dict[str, object]] = []
    team_games = [
        ("game_1", "Fruit Drop Rush", "Team Member 1", "Arcade", True),
        ("game_2", "Escape the City", "Team Member 2", "Action", True),
        ("game_3", "Forgotten", "Team Member 3", "Strategy", True),
        ("game_4", "Mystical Bamboo", "Team Member 4", "Puzzle", True),
        ("game_5", "Game 5 Snake Test", "Team Scorpions", "Arcade", True),
    ]
    for game_id, title, creator, genre, playable in team_games:
        games.append(
            {
                "game_id": game_id,
                "title": title,
                "creator": creator,
                "genre": genre,
                "playable": playable,
                "launch_path": f"games/{game_id}/code/game/main.py" if game_id in {"game_1", "game_2", "game_3", "game_4"} else (f"games.{game_id}.main" if playable else ""),
                "thumbnail_path": f"client/assets/thumbnails/{game_id}.png",
                "screenshot_paths": [f"client/assets/screenshots/{game_id}_preview.png"],
                "created_at": random_timestamp(rng),
                "last_updated": random_timestamp(rng),
                "total_plays": rng.randint(10_000, 2_000_000),
                "currently_playing": rng.randint(0, 6_000),
                "min_players": 1,
                "max_players": rng.randint(1, 8),
                "supports_multiplayer": game_id not in ("game_1", "game_5"),
                "status": "TEMP TEST GAME - Safe to delete later" if game_id == "game_5" else f"Uses games/{game_id}/code/game/main.py",
                "tags": ["temp-test-game", genre.lower(), "safe-to-delete"] if game_id == "game_5" else ["team-game", genre.lower(), "folder-convention"],
            }
        )

    for index in range(len(games) + 1, count + 1):
        game_id = f"catalog_game_{index:03d}"
        genre = rng.choice(GENRES)
        title = f"{rng.choice(['Neon', 'Cyber', 'Turbo', 'Pixel', 'Orbit', 'Shadow', 'Crystal'])} {rng.choice(['Arena', 'Run', 'Quest', 'Rally', 'Tower', 'Dash', 'League'])} {index:03d}"
        games.append(
            {
                "game_id": game_id,
                "title": title,
                "creator": f"Student Studio {rng.randint(1, 48):02d}",
                "genre": genre,
                "playable": False,
                "launch_path": "",
                "thumbnail_path": f"client/assets/thumbnails/{game_id}.png",
                "screenshot_paths": [f"client/assets/screenshots/{game_id}_preview.png"],
                "created_at": random_timestamp(rng),
                "last_updated": random_timestamp(rng),
                "total_plays": rng.randint(1_000, 900_000),
                "currently_playing": rng.randint(0, 2_500),
                "min_players": 1,
                "max_players": rng.randint(1, 10),
                "supports_multiplayer": rng.choice([True, False]),
                "status": "Catalog placeholder",
                "tags": ["student-game", genre.lower(), "synthetic"],
            }
        )
    return games


def generate_sessions(rng: random.Random, count: int, players: list[dict[str, object]], games: list[dict[str, object]]) -> list[dict[str, object]]:
    sessions: list[dict[str, object]] = []
    for index in range(1, count + 1):
        player = rng.choice(players)
        game = rng.choice(games)
        duration = rng.randint(45, 3_600)
        score = rng.randint(0, 250_000)
        sessions.append(
            {
                "session_id": f"session_{index:06d}",
                "player_id": player["player_id"],
                "username": player["username"],
                "game_id": game["game_id"],
                "game_title": game["title"],
                "started_at": random_timestamp(rng),
                "duration_seconds": duration,
                "score": score,
                "outcome": rng.choices(OUTCOMES, weights=[42, 42, 8, 8], k=1)[0],
                "platform": rng.choice(["desktop", "laptop", "lab-pc"]),
                "server_region": rng.choice(REGIONS),
            }
        )
    sessions.sort(key=lambda row: str(row["started_at"]))
    return sessions


def generate_chat_messages(rng: random.Random, count: int, sessions: list[dict[str, object]]) -> list[dict[str, object]]:
    messages: list[dict[str, object]] = []
    for index in range(1, count + 1):
        session = rng.choice(sessions)
        messages.append(
            {
                "message_id": f"message_{index:06d}",
                "session_id": session["session_id"],
                "player_id": session["player_id"],
                "username": session["username"],
                "game_id": session["game_id"],
                "sent_at": random_timestamp(rng),
                "text": rng.choice(CHAT_SNIPPETS),
                "moderation_status": "clean",
            }
        )
    messages.sort(key=lambda row: str(row["sent_at"]))
    return messages


def generate_dataset(player_count: int, session_count: int, chat_count: int, game_count: int, seed: int) -> None:
    rng = random.Random(seed)
    games = generate_game_catalog(rng, game_count)
    players = generate_players(rng, player_count)
    sessions = generate_sessions(rng, session_count, players, games)
    chat_messages = generate_chat_messages(rng, chat_count, sessions)

    write_json(DATASET_DIR / "players.json", players)
    write_json(DATASET_DIR / "game_catalog.json", games)
    write_json(DATASET_DIR / "sessions.json", sessions)
    write_json(DATASET_DIR / "chat_messages.json", chat_messages)

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "seed": seed,
        "player_count": len(players),
        "session_count": len(sessions),
        "chat_message_count": len(chat_messages),
        "game_catalog_count": len(games),
        "date_range": {"start": START_DATE.isoformat(timespec="seconds"), "end": END_DATE.isoformat(timespec="seconds")},
        "submission_note": "Commit data/synthetic_dataset/*.json with the project submission.",
    }
    write_json(DATASET_DIR / "manifest.json", [manifest])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the Scorpions Arcade synthetic dataset.")
    parser.add_argument("--players", type=int, default=DEFAULT_PLAYER_COUNT)
    parser.add_argument("--sessions", type=int, default=DEFAULT_SESSION_COUNT)
    parser.add_argument("--chat", type=int, default=DEFAULT_CHAT_COUNT)
    parser.add_argument("--games", type=int, default=DEFAULT_GAME_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_dataset(args.players, args.sessions, args.chat, args.games, args.seed)
    print(f"Synthetic dataset written to {DATASET_DIR}")
    print("Reminder: commit data/synthetic_dataset/*.json with the final project.")


if __name__ == "__main__":
    main()
