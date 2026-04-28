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

Dataset realism:
    The generator intentionally avoids uniform random data. It gives games a
    popularity skew, players activity tiers and genre preferences, scores based
    partly on player skill, long-tail session durations, uneven chat volume,
    and genre/social overlap so recommendation features have real patterns to
    discover.
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

GENRE_AFFINITY = {
    "Action": ["Action", "Arcade", "Racing", "Adventure"],
    "Adventure": ["Adventure", "Platformer", "Co-op", "Puzzle"],
    "Racing": ["Racing", "Action", "Arcade", "Platformer"],
    "Strategy": ["Strategy", "Puzzle", "Co-op", "Arcade"],
    "Puzzle": ["Puzzle", "Strategy", "Co-op", "Adventure"],
    "Arcade": ["Arcade", "Action", "Racing", "Platformer"],
    "Co-op": ["Co-op", "Adventure", "Strategy", "Puzzle"],
    "Platformer": ["Platformer", "Arcade", "Adventure", "Racing"],
}

GENRE_TAGS = {
    "Action": ["action", "combat", "quickplay"],
    "Adventure": ["adventure", "exploration", "quests"],
    "Racing": ["racing", "time-trial", "speed"],
    "Strategy": ["strategy", "ranked", "planning"],
    "Puzzle": ["puzzle", "logic", "daily"],
    "Arcade": ["arcade", "score-chase", "fast-rounds"],
    "Co-op": ["co-op", "teamwork", "party"],
    "Platformer": ["platformer", "routes", "checkpoints"],
}

ACTIVITY_TIERS = [
    ("casual", 1, 35, 68),
    ("regular", 20, 180, 24),
    ("core", 140, 520, 7),
    ("marathon", 450, 1100, 1),
]


def clamp(value: int, low: int, high: int) -> int:
    """Clamp integer value into an inclusive range."""

    return max(low, min(high, value))


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
        secondary_genres = [candidate for candidate in GENRE_AFFINITY[genre] if candidate != genre][:2]
        tier, low_sessions, high_sessions, _weight = rng.choices(ACTIVITY_TIERS, weights=[tier[3] for tier in ACTIVITY_TIERS], k=1)[0]
        games_played = rng.randint(low_sessions, high_sessions)
        skill_rating = clamp(int(rng.gauss(1250, 360) + games_played * 0.55), 350, 2850)
        win_rate = clamp(int(18 + (skill_rating - 350) / 2500 * 58 + rng.gauss(0, 8)), 5, 88) / 100
        wins = min(games_played, int(games_played * win_rate))
        losses = max(0, games_played - wins - rng.randint(0, max(1, games_played // 12)))
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
                "preferred_genres": [genre, *secondary_genres],
                "activity_tier": tier,
                "level": clamp(int(skill_rating / 35) + rng.randint(-4, 8), 1, 100),
                "skill_rating": skill_rating,
                "total_score": max(0, int(games_played * rng.gauss(skill_rating * 8, skill_rating * 2))),
                "games_played": games_played,
                "wins": wins,
                "losses": losses,
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
        ("game_1", "Fruit Collection", "ECE 3822 Team Scorpions", "Arcade", ["collection", "fruit", "action"]),
        ("game_2", "Escape the City", "ECE 3822 Team Scorpions", "Action", ["escape", "racing", "city"]),
        ("game_3", "Forgotten", "ECE 3822 Team Scorpions", "Adventure", ["mystery", "exploration", "story"]),
        ("game_4", "Mystical Bamboo", "ECE 3822 Team Scorpions", "Platformer", ["bamboo", "routes", "precision"]),
        ("game_5", "Snake Lab", "Team Scorpions", "Arcade", ["fallback", "snake", "score-chase"]),
    ]

    # project root used to check whether launch files exist
    project_root = Path(__file__).resolve().parents[1]

    for rank, (game_id, title, creator, genre, extra_tags) in enumerate(team_games, start=1):
        # use different launch path for test game
        if game_id == "game_5":
            launch_path = "games/game_5/main.py"
            playable = (project_root / launch_path).exists()
        else:
            launch_path = f"games/{game_id}/code/game/main.py"
            playable = (project_root / launch_path).exists()

        # Popularity follows a long tail: top games get much more traffic.
        popularity_weight = 1.0 / (rank ** 0.72)
        active_players = int(rng.triangular(60, 6_000, 6_000 * popularity_weight))

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
                "total_plays": int(35_000 + popularity_weight * rng.randint(350_000, 2_500_000)),
                "currently_playing": active_players,
                "players_now": active_players,
                "popularity_weight": round(popularity_weight, 5),
                "min_players": 1,
                "max_players": rng.randint(1, 8),
                "supports_multiplayer": game_id not in ("game_1", "game_5"),
                "status": "Local fallback available" if game_id == "game_5" else ("Playable now" if playable else "Not connected yet"),
                "tags": ["team-game", genre.lower(), *GENRE_TAGS[genre], *extra_tags],
            }
        )

    # fill remaining catalog with synthetic placeholder games
    for index in range(len(games) + 1, count + 1):
        # create fake game identity and genre
        game_id = f"catalog_game_{index:03d}"
        genre = rng.choice(GENRES)
        rank = index
        popularity_weight = 1.0 / (rank ** 0.72)

        # create fake title from adjective + noun
        title = f"{rng.choice(['Neon', 'Cyber', 'Turbo', 'Pixel', 'Orbit', 'Shadow', 'Crystal'])} {rng.choice(['Arena', 'Run', 'Quest', 'Rally', 'Tower', 'Dash', 'League'])} {index:03d}"

        # Most catalog games have modest traffic; a few become hits.
        active_players = int(rng.triangular(0, 2_500, 2_500 * min(1.0, popularity_weight * 7)))

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
                "total_plays": int(1_000 + popularity_weight * rng.randint(75_000, 1_500_000)),
                "currently_playing": active_players,
                "players_now": active_players,
                "popularity_weight": round(popularity_weight, 5),
                "min_players": 1,
                "max_players": rng.randint(1, 10),
                "supports_multiplayer": rng.choice([True, False]),
                "status": "Not connected yet",
                "tags": ["student-game", genre.lower(), *GENRE_TAGS[genre], "synthetic"],
            }
        )

    return games


def generate_sessions(rng: random.Random, count: int, players: list[dict[str, object]], games: list[dict[str, object]]) -> list[dict[str, object]]:
    '''generate synthetic game session records'''

    # store generated session rows
    sessions: list[dict[str, object]] = []
    games_by_genre: dict[str, list[dict[str, object]]] = {genre: [] for genre in GENRES}
    game_weights_by_genre: dict[str, list[float]] = {genre: [] for genre in GENRES}
    all_game_weights: list[float] = []

    for game in games:
        genre = str(game["genre"])
        weight = float(game.get("popularity_weight", 0.01)) * (1 + int(game.get("currently_playing", 0)) / 2500)
        games_by_genre.setdefault(genre, []).append(game)
        game_weights_by_genre.setdefault(genre, []).append(weight)
        all_game_weights.append(weight)

    player_weights = [
        max(1.0, float(player.get("games_played", 1)) ** 0.88)
        for player in players
    ]
    chosen_players = rng.choices(players, weights=player_weights, k=count)

    for index, player in enumerate(chosen_players, start=1):
        # Players mostly choose games in their preferred genres, but sometimes
        # try other games. This creates overlap for recommendation queries.
        preferred_genres = player.get("preferred_genres")
        if not isinstance(preferred_genres, list) or not preferred_genres:
            preferred_genres = [player.get("favorite_genre", rng.choice(GENRES))]
        if rng.random() < 0.82:
            genre = str(rng.choice(preferred_genres))
            genre_games = games_by_genre.get(genre) or games
            genre_weights = game_weights_by_genre.get(genre) or all_game_weights
            game = rng.choices(genre_games, weights=genre_weights, k=1)[0]
        else:
            game = rng.choices(games, weights=all_game_weights, k=1)[0]

        # generate gameplay result data
        skill = int(player.get("skill_rating", 1000) or 1000)
        duration = clamp(int(rng.lognormvariate(6.15, 0.72)), 45, 7_200)
        score_mean = skill * rng.uniform(18, 55)
        score = clamp(int(rng.lognormvariate(10.2, 0.62) + rng.gauss(score_mean, score_mean * 0.28)), 0, 500_000)
        if rng.random() < 0.03:
            score = clamp(score * rng.randint(2, 5), 0, 900_000)
        win_chance = clamp(int(18 + (skill / 2850) * 62), 8, 82)
        outcome = rng.choices(
            OUTCOMES,
            weights=[win_chance, max(10, 86 - win_chance), 7, 5],
            k=1,
        )[0]

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
                "outcome": outcome,
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
    chat_weights: list[float] = []
    for session in sessions:
        duration = int(session.get("duration_seconds", 60) or 60)
        score = int(session.get("score", 0) or 0)
        # Chat is uneven: longer, higher-score, and randomly social sessions
        # get many more messages, while many sessions receive none.
        social_burst = rng.random()
        burst_multiplier = 8.0 if social_burst > 0.965 else (3.0 if social_burst > 0.82 else 1.0)
        chat_weights.append(max(0.05, (duration / 600) * burst_multiplier + min(score, 300_000) / 300_000))

    chosen_sessions = rng.choices(sessions, weights=chat_weights, k=count)

    for index, session in enumerate(chosen_sessions, start=1):
        # connect message to a weighted session
        duration = int(session.get("duration_seconds", 60) or 60)
        started_at = datetime.fromisoformat(str(session["started_at"]))

        # generate message time and text
        sent_at = (started_at + timedelta(seconds=rng.randint(0, max(1, duration)))).isoformat(timespec="seconds")
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
        "realism_note": "Weighted popularity, player activity tiers, genre preferences, skill-influenced scores, long-tail durations, uneven chat, and co-play overlap.",
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
