from __future__ import annotations

"""Large temporary game catalog rows for the UI prototype.

Purpose:
    Make the arcade feel like a platform that has been active for about a year.
    These records are UI mock data only. They are intentionally not final
    backend/data-structure logic.

TODO(DATASET):
    Replace these generated placeholder rows with cleaned records from
    data/synthetic_dataset/game_catalog.json after the team finishes the real
    ingestion and cleaning pipeline.

TODO(REAL GAMES):
    When a student/team game becomes real, add or update its catalog row in
    mock_games.py and register its launch target in services/game_launch_registry.py.
"""

from client.models import Game, Genre
from .game_factory import make_game


_TITLE_PREFIXES = [
    "Neon",
    "Crystal",
    "Turbo",
    "Pixel",
    "Sky",
    "Cyber",
    "Lunar",
    "Rapid",
    "Shadow",
    "Solar",
    "Frost",
    "Galaxy",
    "Jungle",
    "Rocket",
    "Mystic",
    "Prism",
]

_TITLE_NOUNS = [
    "Dash",
    "Riders",
    "Quest",
    "Circuit",
    "Legends",
    "Arena",
    "Run",
    "Forge",
    "Voyage",
    "Clash",
    "Towers",
    "Trials",
    "League",
    "Rush",
    "Grid",
    "Frontier",
]

_CREATORS = [
    "Orion Arcade Labs",
    "Temple Indie Guild",
    "Byte Harbor Studio",
    "North Star Games",
    "Looplight Collective",
    "Arc Furnace Team",
    "Cloudline Arcade",
    "Golden Pixel Works",
    "Signal Fox Studio",
    "Night Market Games",
    "Tiny Planet Crew",
    "Red Lantern Labs",
]

_STATUS_ROTATION = ["Live", "Trending", "Classic", "Seasonal", "New", "Live Event", "Archived Favorite"]
_UPDATE_ROTATION = [
    "Updated today",
    "Updated yesterday",
    "Updated 2 days ago",
    "Updated this week",
    "Updated last week",
    "Updated this month",
]

_GENRE_TAGS = {
    Genre.ACTION.value: ["action", "combat", "quickplay"],
    Genre.ADVENTURE.value: ["adventure", "exploration", "quests"],
    Genre.RACING.value: ["racing", "time-trial", "ghost-runs"],
    Genre.STRATEGY.value: ["strategy", "ranked", "planning"],
    Genre.PUZZLE.value: ["puzzle", "logic", "daily"],
    Genre.ARCADE.value: ["arcade", "score-chase", "fast-rounds"],
    Genre.COOP.value: ["co-op", "party", "teamwork"],
    Genre.PLATFORMER.value: ["platformer", "routes", "checkpoints"],
}

_GENRE_DESCRIPTIONS = {
    Genre.ACTION.value: "Fast action rounds with public matchmaking, seasonal badges, and score streak tracking.",
    Genre.ADVENTURE.value: "Exploration sessions with quest logs, rare route history, and active weekly objectives.",
    Genre.RACING.value: "Time-trial racing with split records, ghost comparisons, and rotating challenge tracks.",
    Genre.STRATEGY.value: "Short strategy matches with ranked tables, replay history, and tactical milestones.",
    Genre.PUZZLE.value: "Daily puzzle boards with streak tracking, hint records, and clean score history.",
    Genre.ARCADE.value: "Classic arcade scoring with quick sessions, combo chains, and lively leaderboards.",
    Genre.COOP.value: "Co-op missions with party queues, shared objectives, and session-based progress logs.",
    Genre.PLATFORMER.value: "Route-based platforming with checkpoints, best-time ghosts, and jump-chain stats.",
}


def build_large_placeholder_catalog(existing_ids: set[str], target_total: int = 112) -> list[Game]:
    """Return deterministic non-playable catalog rows until the catalog is large.

    Every generated entry is a placeholder. The UI can browse, filter, search,
    and open details for these games, but the Play button should report that
    the game is not connected yet.
    """

    placeholder_games: list[Game] = []
    needed = max(0, target_total - len(existing_ids))
    genres = [genre.value for genre in Genre]
    index = 0

    while len(placeholder_games) < needed:
        prefix = _TITLE_PREFIXES[index % len(_TITLE_PREFIXES)]
        noun = _TITLE_NOUNS[(index // len(_TITLE_PREFIXES)) % len(_TITLE_NOUNS)]
        title = f"{prefix} {noun}"
        game_id = f"catalog-{prefix.lower()}-{noun.lower()}-{index + 1:03d}".replace(" ", "-")
        index += 1

        if game_id in existing_ids:
            continue

        genre = genres[index % len(genres)]
        base_players = 45 + ((index * 137) % 2600)
        total_plays = 18_000 + (index * 23_917) % 1_350_000
        release_year = 2017 + (index % 10)
        color = (
            70 + (index * 37) % 135,
            82 + (index * 53) % 120,
            92 + (index * 71) % 120,
        )
        tags = [*_GENRE_TAGS[genre], "mock-catalog", f"season-{1 + index % 4}"]

        placeholder_games.append(
            make_game(
                game_id,
                title,
                genre,
                _GENRE_DESCRIPTIONS[genre],
                _CREATORS[index % len(_CREATORS)],
                base_players,
                total_plays,
                _STATUS_ROTATION[index % len(_STATUS_ROTATION)],
                False,
                color,
                tags,
                release_year,
                _UPDATE_ROTATION[index % len(_UPDATE_ROTATION)],
                f"{title} has active preview sessions, catalog stats, and leaderboard sample data.",
            )
        )
        existing_ids.add(game_id)

    return placeholder_games
