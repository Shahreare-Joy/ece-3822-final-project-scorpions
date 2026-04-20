# Scorpions Arcade Project Foundation

## Short Review Of Current Gaps

The project already has a strong Pygame client shell, but the previous version
needed clearer boundaries between UI prototype code and final assignment work.
This foundation adds explicit hook files for data structures, future C++ server
communication, and game launch handoff. It also adds a project notes/settings
screen and a team workflow plan so the group can divide the remaining work.

The following are intentionally not solved here:

- real account backend
- real playable game logic
- required custom data structures
- dataset ingestion and cleaning
- sorting/ranking/query algorithms
- C++ multiplayer protocol
- performance analysis
- final report conclusions

## Proposed File Structure

```text
local_project/
  main.py                         # Entry point: run this file.
  README.md                       # Quick start and overview.
  PROJECT_TEMPLATE_PLAN.md         # Short template notes.
  requirements.txt                # Pygame dependency.
  docs/
    branch_plan.md                  # Team branch workflow.
    PROJECT_FOUNDATION.md          # Team plan, branches, checklist, file guide.
    project_notes.md                # What is scaffolded and how hooks connect.
    work_remaining.md               # Professor-facing remaining work checklist.
  client/
    __init__.py                    # Package marker.
    main.py                        # Package entry point used by root main.py.
    core/                          # App, routing, state, layout, config, theme.
    components/                    # Button, panel, input, card, fonts, rows, navbar.
    models/                        # Separate dataclass model files.
    data/                          # Separate mock data files by record type.
    games/                         # Uploaded games and temporary test games.
    screens/                       # One screen class per file.
    services/                      # Feature services: auth, catalog, search, etc.
    integrations/                  # C++, backend API, dataset hooks.
    placeholders/                  # Data structures, sorting, analysis, cleaning.
```

## Screen Coverage

- Welcome / Landing
- Login
- Create Account
- Home / Discover
- Browse Games with genre filtering
- Game Details
- Profile
- Leaderboards
- Search Players
- Match History
- Project Settings / Notes

## What Is Already Scaffolded

- Main Pygame app loop, navigation, and reusable components.
- Mock login/create account flow using temporary local players.
- Discover-style home page with Continue Playing, Recently Played, Popular
  Right Now, Recommended For You, and Featured / New sections.
- Browse screen with genre filter buttons and mock catalog counts.
- Game Details screen with art area, metadata, action buttons, leaderboard
  preview, and recent activity.
- One marked playable template game: Scorpions Arena.
- Three polished team placeholder games: Sky Raiders, Turbo Sprint, Crystal Run.
- Additional fake catalog games so the arcade feels active and established.
- Profile, Leaderboards, Search Players, Match History, and Settings screens.
- Starter hook modules for future data structures, networking, and game launch.
- Extra separation for `components/fonts.py`, `components/text.py`,
  `components/navbar.py`, `core/screen_registry.py`,
  `services/chat_service.py`, and `data/game_factory.py`.

## What Your Team Must Still Build

- Real playable game behavior.
- C++ session handoff and networking protocol.
- Real account flow or documented backend stub.
- Synthetic dataset ingestion and cleaning.
- Required custom data structures and their integration.
- Leaderboard/search/history/catalog query logic.
- Sorting/range-query/rank-lookup demonstrations.
- Performance measurement and complexity analysis.
- Final report, demo script, and screenshots.

## Data Structure Hook Map

- Hash Table:
  - `services/arcade_backend.py`: current facade where username/game_id lookup is exposed
  - `placeholders/data_structures.py`: `PlayerIndexHook`, `GameCatalogIndexHook`
  - likely use: exact player lookup, exact game lookup, secondary session indexes

- Binary Search Tree:
  - `placeholders/data_structures.py`: catalog sorted traversal, player rank ranges, score ranges
  - likely use: range queries, ordered leaderboards, title/popularity browsing

- Heap / Priority Queue:
  - `placeholders/data_structures.py`: `LeaderboardIndexHook`
  - likely use: top-K leaderboard scores and popular-now ranking

- Graph:
  - `placeholders/data_structures.py`: `RecommendationGraphHook`
  - likely use: player-game-genre recommendation graph, friend graph, lobby matching

- Another chosen structure:
  - suggested: custom linked list or indexed dynamic array for chronological match history
  - likely use: append sessions, recent sessions, replay history, filter by player/game/date

## Future Integration Hook Map

- Login/account creation:
  - current: `MockArcadeBackend.authenticate`, `MockArcadeBackend.create_account`
  - future: call `integrations/cpp_server.py` or a real account service

- Dataset ingestion/cleaning:
  - current: `data/mock_*.py`
  - future: create a loader/cleaner module that validates messy records before
    building custom structures

- Game catalog indexing/filtering:
  - current: `MockArcadeBackend.filter_games`
  - future: replace list scan with genre index, hash table, or BST

- Leaderboards:
  - current: `MockArcadeBackend.get_leaderboard`
  - future: connect heap/BST/sorting module and add rank lookup/range queries

- Player search:
  - current: `MockArcadeBackend.search_players`
  - future: connect trie/hash table/BST depending on your final design

- Match history:
  - current: `MockArcadeBackend.get_sessions`
  - future: connect custom chronological session structure plus filters

- Playable game launch:
  - current: `services/game_launch_service.py`
  - future: ask C++ server for session id, host, port, and player token

- Chat and live scoreboard:
  - current: `integrations/cpp_server.py` placeholder methods
  - future: implement lobby chat, live score updates, and server events

## Recommended Branch Plan

Suggested rule: keep `main` runnable. Each feature branch should merge only
after `python -B -m py_compile` passes and the app opens from `main.py`.

- `main`
  - stable, runnable demo only
- `ui-foundation`
  - navigation, shared components, layout polish, settings/project notes
- `game-catalog-details`
  - catalog data views, genre filtering, game details, thumbnails/art replacement
- `real-playable-game`
  - actual Scorpions Arena gameplay module and launch flow
- `profile-leaderboards`
  - profile cards, leaderboard ranking views, rank lookup UI
- `history-search`
  - player search, match history filters, query screens
- `backend-hooks-cpp`
  - C++ server handoff, login protocol, chat/scoreboard hooks
- `data-structures-analysis`
  - required custom structures, sorting/query tests, performance measurements
- `dataset-cleaning`
  - synthetic data generation, messy record cleaning, validated dataset loader

## Suggested Team Ownership

- Person 1: UI foundation and navigation
  - Own `core/app.py`, `core/state.py`, `components/`, shared layout consistency, and settings/project notes.

- Person 2: Catalog, details, and playable game flow
  - Own Browse, Home game rows, Game Details, Scorpions Arena launch path, and game art.

- Person 3: Profiles, leaderboards, search, and history screens
  - Own Profile, Leaderboards, Search Players, Match History, and result formatting.

- Person 4: Backend hooks, C++ handoff, dataset, and data-structure prep
  - Own `services/arcade_backend.py`, `placeholders/data_structures.py`,
    `integrations/cpp_server.py`, `services/game_launch_service.py`,
    dataset cleaning, benchmarks, and integration planning.

## Work Remaining Checklist

- [ ] Replace mock login/account creation with real account flow.
- [ ] Build the real playable Scorpions Arena game.
- [ ] Connect Play / Launch to C++ multiplayer session creation.
- [ ] Define C++ server protocol for host, port, session id, player token, chat, and scores.
- [ ] Generate or ingest the final synthetic dataset.
- [ ] Clean messy dataset records and document the cleaning rules.
- [ ] Implement required custom data structures.
- [ ] Include at least five structures, with at least three new to this assignment if required.
- [ ] Add hash table lookup for players/games or explain alternative.
- [ ] Add BST/range-query structure or explain alternative.
- [ ] Add heap/priority queue leaderboard or popularity structure.
- [ ] Add graph recommendation/matchmaking structure.
- [ ] Add one additional chosen structure, such as linked list/history index/trie.
- [ ] Replace mock leaderboard generation with real ranking logic.
- [ ] Add rank lookup and score range queries.
- [ ] Replace mock player search with final search structure.
- [ ] Replace match history scan with indexed history queries.
- [ ] Replace catalog scans with index/filter/sort structures.
- [ ] Add sorting algorithm integration for leaderboard/history/catalog views.
- [ ] Add performance measurement hooks and collect benchmark results.
- [ ] Write complexity analysis for each major operation.
- [ ] Add live scoreboard updates from the server.
- [ ] Add chat/lobby integration.
- [ ] Prepare final demo script and report screenshots.
