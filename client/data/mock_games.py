from __future__ import annotations

from client.models import Game, Genre
from .catalog_placeholders import build_large_placeholder_catalog
from .game_factory import make_game as game


# Temporary UI mock catalog. TODO(DATASET): Replace with final cleaned catalog
# rows from data/synthetic_dataset/game_catalog.json after ingestion/cleaning.
#
# Only catalog rows with a real connected launch path should be marked
# playable=True. Most of this file is intentionally placeholder content so the
# UI feels like a large platform without pretending the backend is finished.
MOCK_GAMES: list[Game] = [
    # Team game 1: real playable template. The service will later ask the C++ server for a session.
    game("scorpions-arena", "Fruit Drop Rush", Genre.ARCADE.value, "Team Game 1. Shahreare's map-based fruit collection game launched from games/game_1/code/game/main.py while preserving its own graphics and relative paths.", "ECE 3822 Team Scorpions", 248, 98442, "Playable now", True, (210, 86, 98), ["team-game", "arcade", "fruit"], 2026, "Updated today", "Collect fruit around the map before the countdown ends.", True, "client/assets/thumbnails/fruit_drop_rush.png", "client/assets/screenshots/fruit_drop_rush.png"),
    # Team games 2-3 are connected through the same games/game_N/code/game/main.py convention.
    game("sky-raiders", "Escape the City", Genre.ACTION.value, "Team Game 2. A high-pressure city escape entry launched from games/game_2/code/game/main.py with its uploaded assets preserved.", "Scorpions Team - Game 2", 1248, 613028, "Playable now", True, (78, 132, 224), ["team-game", "action", "escape"], 2023, "Updated 2 days ago", "City escape sessions are open.", True, "client/assets/thumbnails/escape_the_city.png", "client/assets/screenshots/escape_the_city.png"),
    game("turbo-sprint", "Forgotten", Genre.ADVENTURE.value, "Team Game 3. A mystery-adventure entry launched from games/game_3/code/game/main.py with its uploaded assets preserved.", "Scorpions Team - Game 3", 741, 421776, "Playable now", True, (224, 116, 72), ["team-game", "adventure", "mystery"], 2022, "Updated last week", "Mystery adventure sessions are open.", True, "client/assets/thumbnails/forgotten.png", "client/assets/screenshots/forgotten.png"),
    game("crystal-run", "Mystical Bamboo", Genre.PLATFORMER.value, "Team Game 4. A polished bamboo-themed platformer entry prepared for games/game_4/code/game/main.py. It appears fully in the arcade while launch integration is still pending.", "Scorpions Team - Game 4", 398, 289410, "Pending integration", True, (210, 170, 76), ["team-game", "platformer", "bamboo"], 2024, "Updated 4 days ago", "Team game entry ready for teammate folder connection.", True),
    # TEMP TEST GAME - SAFE TO DELETE LATER:
    # Remove this one mock catalog row and the "snake-test" launch registry
    # block when the team no longer needs a simple arcade-flow test game.
    game("snake-test", "Snake Test Lab", Genre.ARCADE.value, "Temporary Snake game used for local launch-flow checks. It stays isolated from team games and can be hidden when the real games are connected.", "Local Test Harness", 12, 318, "Temporary test", False, (92, 190, 116), ["temporary", "test-game", "safe-to-delete"], 2026, "Local test build", "Local test game for launch checks. Safe to hide before final presentation.", False),
    game("dungeon-clash", "Dungeon Clash", Genre.ADVENTURE.value, "Party-based dungeon runs with relic drops and weekly boss records.", "Scorpions Catalog", 983, 711920, "Live", False, (138, 104, 212), ["co-op", "fantasy"], 2019, "Updated yesterday", "Weekly boss activity is high."),
    game("block-arena", "Block Arena", Genre.STRATEGY.value, "Compact tactics battles with ranked board control and replay review.", "Scorpions Catalog", 1522, 843190, "Live", False, (74, 170, 122), ["strategy", "ranked"], 2018, "Updated 3 days ago", "Ranked board-control queue is active."),
    game("neon-strikers", "Neon Strikers", Genre.ARCADE.value, "Arcade striker duels with bright arenas and fast matchmaking.", "Scorpions Catalog", 2517, 1203814, "Live Event", False, (66, 196, 190), ["arcade", "duel"], 2020, "Updated today", "Weekend striker event is trending."),
    game("castle-quest", "Castle Quest", Genre.COOP.value, "Two-player castle routes with puzzle gates and shared loot.", "Scorpions Catalog", 634, 311822, "Live", False, (194, 92, 152), ["co-op", "quest"], 2021, "Updated last month", "Co-op route history is available."),
    game("circuit-chef", "Circuit Chef", Genre.PUZZLE.value, "Kitchen circuit puzzles where players route ingredients through logic boards.", "Scorpions Catalog", 812, 205442, "New", False, (82, 166, 104), ["puzzle", "timed"], 2026, "Updated today", "Daily puzzle streaks reset at noon."),
    game("astro-miners", "Astro Miners", Genre.ADVENTURE.value, "Mine asteroids, dodge storms, and compare haul efficiency.", "Scorpions Catalog", 1096, 535108, "Live", False, (78, 156, 208), ["space", "resource"], 2022, "Updated 6 days ago", "Resource race sessions are active."),
    game("tiny-tactics", "Tiny Tactics", Genre.STRATEGY.value, "Small-board strategy with fast matches and seasonal ladders.", "Scorpions Catalog", 557, 188204, "Live", False, (178, 132, 78), ["strategy", "short-session"], 2025, "Updated 2 weeks ago", "Season 4 ladder preview is active."),
    game("logic-lab", "Logic Lab", Genre.PUZZLE.value, "Daily puzzle boards with streaks, hints, and solver history.", "Scorpions Catalog", 476, 244702, "Live", False, (128, 134, 210), ["puzzle", "daily"], 2020, "Updated yesterday", "Daily solver history is cached."),
    game("mech-yard", "Mech Yard", Genre.ACTION.value, "Loadout brawls with mech classes and ranked damage stats.", "Scorpions Catalog", 1163, 620881, "Live Event", False, (202, 92, 110), ["action", "loadout"], 2024, "Updated today", "Loadout event queue is crowded."),
    game("river-rally", "River Rally", Genre.RACING.value, "Boat racing with split-time leaderboards and weather mutators.", "Scorpions Catalog", 702, 355214, "Live", False, (66, 150, 178), ["racing", "time-trial"], 2021, "Updated 8 days ago", "Storm track rotation is live."),
    game("buddy-bots", "Buddy Bots", Genre.COOP.value, "Co-op robot repair challenges with shared objectives.", "Scorpions Catalog", 391, 179032, "Live", False, (112, 178, 128), ["co-op", "bots"], 2025, "Updated 5 days ago", "Repair streak sessions are rising."),
    game("tower-parkour", "Tower Parkour", Genre.PLATFORMER.value, "Vertical platforming towers with clean checkpoint history.", "Scorpions Catalog", 875, 498311, "Live", False, (198, 142, 88), ["platformer", "obby"], 2018, "Updated 2 days ago", "Checkpoint saves are busy."),
    game("orbit-outlaws", "Orbit Outlaws", Genre.ACTION.value, "Zero-gravity blaster rounds with team colors, quick respawns, and badge milestones.", "Scorpions Catalog", 1324, 734112, "Live", False, (118, 92, 210), ["action", "space"], 2020, "Updated today", "Low-gravity arena rotation started."),
    game("rune-garden", "Rune Garden", Genre.PUZZLE.value, "Tile-growth puzzles where players chain rune patterns for score multipliers.", "Scorpions Catalog", 268, 98214, "Classic", False, (98, 166, 118), ["puzzle", "classic"], 2017, "Updated 3 months ago", "Classic puzzle archive remains active."),
    game("metro-drift", "Metro Drift", Genre.RACING.value, "Night-city racing with drift chains, tunnel splits, and weekly ghost cars.", "Scorpions Catalog", 1456, 912445, "Trending", False, (188, 88, 138), ["racing", "drift"], 2023, "Updated yesterday", "Drift ghosts were refreshed."),
    game("island-forge", "Island Forge", Genre.ADVENTURE.value, "Build camps, explore ruins, and compare expedition logs with friends.", "Scorpions Catalog", 522, 301990, "Live", False, (84, 158, 138), ["adventure", "crafting"], 2021, "Updated 10 days ago", "Expedition history is stable."),
    game("chessbyte-royale", "Chessbyte Royale", Genre.STRATEGY.value, "A fast strategy remix where pieces upgrade through arcade-style capture chains.", "Scorpions Catalog", 689, 267830, "Live", False, (150, 136, 94), ["strategy", "board"], 2024, "Updated last week", "Opening book stats are refreshed."),
    game("pixel-patrol", "Pixel Patrol", Genre.ARCADE.value, "Wave-defense arcade missions with quick parties and public scoreboards.", "Scorpions Catalog", 1730, 1020440, "Hot", False, (92, 172, 202), ["arcade", "waves"], 2019, "Updated today", "Wave 30 badge chase is active."),
    game("mystic-mailroom", "Mystic Mailroom", Genre.COOP.value, "Two-player delivery routes through shifting rooms and timed portal doors.", "Scorpions Catalog", 344, 140982, "Live", False, (176, 104, 188), ["co-op", "timed"], 2025, "Updated 2 weeks ago", "Co-op route matching is active."),
    game("cloud-courier", "Cloud Courier", Genre.PLATFORMER.value, "Float between sky islands, chain jumps, and save best route ghosts.", "Scorpions Catalog", 932, 411725, "Live", False, (106, 162, 220), ["platformer", "routes"], 2022, "Updated 4 days ago", "Ghost route comparison is active."),
    game("laser-library", "Laser Library", Genre.PUZZLE.value, "Redirect beams through book stacks and compete on daily logic boards.", "Scorpions Catalog", 608, 198771, "Daily", False, (190, 118, 84), ["puzzle", "logic"], 2023, "Updated today", "Daily beam board is new."),
    game("dragon-dock", "Dragon Dock", Genre.ADVENTURE.value, "Trade, sail, and raid dragon ports with long-running session history.", "Scorpions Catalog", 1190, 884210, "Live Event", False, (198, 108, 72), ["adventure", "event"], 2018, "Updated yesterday", "Port raid event is underway."),
]

# Add enough realistic placeholder rows to make the launcher feel established.
# These are intentionally non-playable and should be replaced by real imported
# catalog data later.
MOCK_GAMES.extend(build_large_placeholder_catalog({game_row.game_id for game_row in MOCK_GAMES}, target_total=112))
