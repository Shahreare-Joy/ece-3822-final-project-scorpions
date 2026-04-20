from __future__ import annotations

"""Game registry scaffold for all arcade games.

Purpose:
- keep game metadata in one platform-server location
- support the 4 team games now and additional student games later
- avoid hardcoding game module paths inside Pygame screens

TODO(GAME REGISTRY):
- load this registry from the final catalog dataset
- validate that connected games expose `run_game(player)`
- add thumbnail/screenshot paths when assets are available
- keep placeholder games visible but safe to click
"""

from dataclasses import dataclass, field


REGISTRY_SCHEMA_VERSION = "scaffold-v1"


@dataclass(frozen=True)
class RegisteredGame:
    """Metadata needed by catalog, browse, details, and launch services."""

    game_id: str
    title: str
    creator: str
    genre: str
    playable: bool
    launch_path: str
    thumbnail_path: str = ""
    screenshot_paths: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    min_players: int = 1
    max_players: int = 4
    supports_multiplayer: bool = False
    is_team_game: bool = False
    is_student_submission: bool = True
    version: str = "0.1"
    api_contract: str = "run_game(player=None, session_info=None)"
    status: str = "Placeholder"


# Starter registry. This is mock/platform metadata, not final catalog storage.
# TODO(STUDENT GAMES): Add additional classmate games here or load them from
# data/synthetic_dataset/games.csv after the final ingestion pipeline exists.
# TODO(SCALE): If the class adds many games, build a custom hash table index for
# exact game_id lookup and separate genre/tag indexes for browsing.
GAME_REGISTRY: dict[str, RegisteredGame] = {
    "game_1": RegisteredGame(
        game_id="game_1",
        title="Fruit Drop Rush",
        creator="Team Member 1",
        genre="Arcade",
        playable=True,
        launch_path="games/game_1/code/game/main.py",
        thumbnail_path="client/assets/thumbnails/game_1.png",
        screenshot_paths=["client/assets/screenshots/game_1_preview.png"],
        tags=["team-game", "arcade", "folder-convention"],
        min_players=1,
        max_players=4,
        supports_multiplayer=False,
        is_team_game=True,
        status="Uses games/game_1/code/game/main.py",
    ),
    "game_2": RegisteredGame(
        game_id="game_2",
        title="Escape the City",
        creator="Team Member 2",
        genre="Action",
        playable=True,
        launch_path="games/game_2/code/game/main.py",
        thumbnail_path="client/assets/thumbnails/game_2.png",
        tags=["team-game", "combat", "placeholder"],
        is_team_game=True,
        status="Waiting for games/game_2/code/game/main.py",
    ),
    "game_3": RegisteredGame(
        game_id="game_3",
        title="Forgotten",
        creator="Team Member 3",
        genre="Strategy",
        playable=True,
        launch_path="games/game_3/code/game/main.py",
        thumbnail_path="client/assets/thumbnails/game_3.png",
        tags=["team-game", "strategy", "placeholder"],
        is_team_game=True,
        status="Waiting for games/game_3/code/game/main.py",
    ),
    "game_4": RegisteredGame(
        game_id="game_4",
        title="Mystical Bamboo",
        creator="Team Member 4",
        genre="Puzzle",
        playable=True,
        launch_path="games/game_4/code/game/main.py",
        thumbnail_path="client/assets/thumbnails/game_4.png",
        tags=["team-game", "puzzle", "placeholder"],
        is_team_game=True,
        status="Waiting for games/game_4/code/game/main.py",
    ),
    "game_5": RegisteredGame(
        game_id="game_5",
        title="Game 5 Snake Test",
        creator="Team Scorpions",
        genre="Arcade",
        playable=True,
        launch_path="games.game_5.main",
        thumbnail_path="client/assets/thumbnails/game_5.png",
        screenshot_paths=["client/assets/screenshots/game_5_preview.png"],
        tags=["temp-test-game", "arcade", "safe-to-delete"],
        min_players=1,
        max_players=1,
        supports_multiplayer=False,
        is_team_game=False,
        status="TEMP TEST GAME - Safe to delete later",
    ),
    "student_racer_demo": RegisteredGame(
        game_id="student_racer_demo",
        title="Campus Drift League",
        creator="Student Team Placeholder",
        genre="Racing",
        playable=False,
        launch_path="",
        thumbnail_path="client/assets/thumbnails/student_racer_demo.png",
        screenshot_paths=["client/assets/screenshots/student_racer_demo_1.png"],
        tags=["student-game", "racing", "extra-credit-ready"],
        min_players=1,
        max_players=6,
        supports_multiplayer=True,
        status="Registry only",
    ),
    "student_coop_demo": RegisteredGame(
        game_id="student_coop_demo",
        title="Signal Rescue Co-op",
        creator="Student Team Placeholder",
        genre="Co-op",
        playable=False,
        launch_path="",
        thumbnail_path="client/assets/thumbnails/student_coop_demo.png",
        screenshot_paths=["client/assets/screenshots/student_coop_demo_1.png"],
        tags=["student-game", "co-op", "network-ready"],
        min_players=2,
        max_players=4,
        supports_multiplayer=True,
        status="Registry only",
    ),
}


def all_registered_games() -> list[RegisteredGame]:
    """Return starter registry rows for UI/catalog scaffolding."""
    return list(GAME_REGISTRY.values())


def get_registered_game(game_id: str) -> RegisteredGame | None:
    """Safe exact lookup for game metadata.

    TODO(DATA STRUCTURE): Replace this dict lookup with the team's custom hash
    table or final catalog index if the registry becomes part of the assignment.
    """
    return GAME_REGISTRY.get(game_id)


def register_game(game: RegisteredGame) -> bool:
    """Starter hook for adding many student games later.

    This mutates the scaffold registry so the UI can test new entries quickly.
    The final project should load records from the dataset or platform server
    storage and insert them into a custom catalog index.

    TODO(REGISTRY VALIDATION):
        Reject duplicate ids, invalid launch paths, unsupported genres, missing
        thumbnails, and games that do not expose the expected run_game function.
    """

    if not game.game_id or game.game_id in GAME_REGISTRY:
        return False
    GAME_REGISTRY[game.game_id] = game
    return True


def games_by_genre(genre: str) -> list[RegisteredGame]:
    """Safe scaffold filter for Browse UI.

    WARNING(SCALE): This is a simple scan for now. Replace it with a genre
    index when the catalog is loaded from the large dataset.
    """

    if genre == "All":
        return all_registered_games()
    return [game for game in GAME_REGISTRY.values() if game.genre == genre]


def playable_games() -> list[RegisteredGame]:
    """Return games that have a launch path and are marked playable."""

    return [game for game in GAME_REGISTRY.values() if game.playable and game.launch_path]


def registry_stats() -> dict[str, int]:
    """Small UI/debug helper for showing registry readiness.

    TODO(ANALYSIS): Replace this with richer counts once the final catalog
    dataset is loaded.
    """

    games = all_registered_games()
    return {
        "total_games": len(games),
        "playable_games": len(playable_games()),
        "placeholder_games": len([game for game in games if not game.playable]),
        "team_games": len([game for game in games if game.is_team_game]),
    }


def student_game_template() -> RegisteredGame:
    """Return a copyable example for adding another student's game.

    Add a new entry near GAME_REGISTRY or load it from the final dataset:
    - create a folder under games/
    - place the runnable file at code/game/main.py
    - preferably expose run_game(player_info=None, session_info=None)
    - add thumbnail/screenshot paths under client/assets/
    - mark playable=True only after launch testing
    """

    return RegisteredGame(
        game_id="replace_with_unique_id",
        title="Replace With Game Title",
        creator="Replace With Team Name",
        genre="Arcade",
        playable=False,
        launch_path="games.replace_folder.main",
        thumbnail_path="client/assets/thumbnails/replace_with_unique_id.png",
        screenshot_paths=["client/assets/screenshots/replace_with_unique_id_1.png"],
        tags=["student-game", "replace-tags"],
        status="Template only",
    )
