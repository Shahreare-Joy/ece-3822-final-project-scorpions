from __future__ import annotations

"""Game registry scaffold for all arcade games."""

from dataclasses import dataclass, field

from datastructures.hash_table import ChainedHashTable


REGISTRY_SCHEMA_VERSION = "scaffold-v1"


@dataclass(frozen=True)
class RegisteredGame:
    '''store metadata for one game entry'''

    # unique game identifier
    game_id: str

    # display title shown in UI
    title: str

    # creator/team name
    creator: str

    # genre category for browsing/filtering
    genre: str

    # whether game is currently playable
    playable: bool

    # path used to launch the game
    launch_path: str

    # optional thumbnail path
    thumbnail_path: str = ""

    # optional screenshot paths
    screenshot_paths: list[str] = field(default_factory=list)

    # tags used for filtering/search
    tags: list[str] = field(default_factory=list)

    # player limits
    min_players: int = 1
    max_players: int = 4

    # multiplayer support flag
    supports_multiplayer: bool = False

    # whether game is from team project
    is_team_game: bool = False

    # whether game is student submission
    is_student_submission: bool = True

    # version string
    version: str = "0.1"

    # expected API contract
    api_contract: str = "run_game(player=None, session_info=None)"

    # status text for UI/debug
    status: str = "Placeholder"


# starter registry dictionary
GAME_REGISTRY: dict[str, RegisteredGame] = {
    # team game 1
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

    # team game 2 (placeholder)
    "game_2": RegisteredGame(
        game_id="game_2",
        title="Escape the City",
        creator="Team Member 2",
        genre="Action",
        playable=False,
        launch_path="games/game_2/code/game/main.py",
        thumbnail_path="client/assets/thumbnails/game_2.png",
        tags=["team-game", "combat", "placeholder"],
        is_team_game=True,
        status="Waiting for games/game_2/code/game/main.py",
    ),

    # team game 3 (placeholder)
    "game_3": RegisteredGame(
        game_id="game_3",
        title="Forgotten",
        creator="Team Member 3",
        genre="Strategy",
        playable=False,
        launch_path="games/game_3/code/game/main.py",
        thumbnail_path="client/assets/thumbnails/game_3.png",
        tags=["team-game", "strategy", "placeholder"],
        is_team_game=True,
        status="Waiting for games/game_3/code/game/main.py",
    ),

    # team game 4 (placeholder)
    "game_4": RegisteredGame(
        game_id="game_4",
        title="Mystical Bamboo",
        creator="Team Member 4",
        genre="Puzzle",
        playable=False,
        launch_path="games/game_4/code/game/main.py",
        thumbnail_path="client/assets/thumbnails/game_4.png",
        tags=["team-game", "puzzle", "placeholder"],
        is_team_game=True,
        status="Waiting for games/game_4/code/game/main.py",
    ),

    # temporary test game
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

    # placeholder student game (racing)
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

    # placeholder student game (co-op)
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


def _build_registry_index() -> ChainedHashTable:
    '''build hash table index for fast game_id lookup'''

    index = ChainedHashTable(max(16, len(GAME_REGISTRY) * 2))

    # insert all games into hash table
    for game in GAME_REGISTRY.values():
        index.put(game.game_id, game)

    return index


# global index for fast lookup
GAME_REGISTRY_INDEX = _build_registry_index()


def all_registered_games() -> list[RegisteredGame]:
    '''return all registered games'''
    return list(GAME_REGISTRY.values())


def get_registered_game(game_id: str) -> RegisteredGame | None:
    '''lookup game by id safely'''

    # lookup using custom hash table
    value = GAME_REGISTRY_INDEX.get(game_id)

    # ensure correct type before returning
    return value if isinstance(value, RegisteredGame) else None


def register_game(game: RegisteredGame) -> bool:
    '''add new game to registry if valid'''

    # reject missing id or duplicate id
    if not game.game_id or game.game_id in GAME_REGISTRY:
        return False

    # reject playable game without launch path
    if game.playable and not game.launch_path:
        return False

    # add to registry and index
    GAME_REGISTRY[game.game_id] = game
    GAME_REGISTRY_INDEX.put(game.game_id, game)
    return True


def games_by_genre(genre: str) -> list[RegisteredGame]:
    '''filter games by genre'''

    # return all games if "All" selected
    if genre == "All":
        return all_registered_games()

    # scan registry for matching genre
    return [game for game in GAME_REGISTRY.values() if game.genre == genre]


def playable_games() -> list[RegisteredGame]:
    '''return games that can be launched'''

    return [game for game in GAME_REGISTRY.values() if game.playable and game.launch_path]


def registry_stats() -> dict[str, int]:
    '''return summary statistics for registry'''

    games = all_registered_games()

    return {
        "total_games": len(games),
        "playable_games": len(playable_games()),
        "placeholder_games": len([game for game in games if not game.playable]),
        "team_games": len([game for game in games if game.is_team_game]),
    }


def student_game_template() -> RegisteredGame:
    '''return template object for new student game'''

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