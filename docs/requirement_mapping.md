# Requirement Mapping

This file maps the professor-facing project requirements to the exact places in
the Scorpions Arcade scaffold where the team should complete the real work.

The current code is a runnable UI/client scaffold. Items marked TODO must be
implemented by the team as part of the final backend/data-structure/analysis
work.

## Requirement Map

| Assignment Requirement | Code Location | What The Template Provides | What The Team Must Implement |
| --- | --- | --- | --- |
| Run the arcade launcher | `main.py`, `client/main.py`, `client/core/app.py` | Pygame app loop, routing, state, and screens | Keep the app runnable while adding real logic |
| Large synthetic dataset | `data/generate_dataset.py`, `data/synthetic_dataset/`, `platform_server/data_ingest.py` | Deterministic generator, committed JSON files, validation/loading scaffold | Keep dataset committed; load records into final structures |
| Dataset cleaning | `platform_server/data_ingest.py`, `client/placeholders/dataset_cleaning.py` | Required field validation and noisy-record comments | Normalize, deduplicate, reject bad rows, document rules |
| Player model | `client/models/player.py` | Basic `Player` dataclass | Extend only if the final dataset needs more fields |
| Game model/catalog | `client/models/game.py`, `client/data/mock_games.py` | Mock catalog with genre/status/playability fields | Replace mock records with cleaned catalog data |
| Session model/history | `client/models/session.py`, `client/data/mock_sessions.py` | Basic `GameSession` dataclass and mock sessions | Build indexes for 100,000+ session lookups |
| Player search/autocomplete | `client/services/search_service.py`, `client/placeholders/data_structures.py` | Mock scan plus `PlayerIndexHook` / `autocomplete_players` interface | Implement Trie, Hash Table, BST, or chosen search structure |
| Player profile lookup | `client/services/profile_service.py` | Mock player lookup and aggregation placeholder | Compute games played, win rate, play time, score history |
| Game search/catalog browsing | `client/services/catalog_service.py`, `client/placeholders/data_structures.py` | Mock genre filter, search, creator filter, sort hooks | Build catalog indexes for genre, title/tags, creator, popularity |
| Catalog sorting | `client/services/catalog_service.py`, `client/placeholders/sorting_algorithms.py` | Temporary sorted calls and sorting placeholders | Implement required sorting algorithms and benchmark them |
| Leaderboard top-N | `client/services/leaderboard_service.py`, `client/placeholders/data_structures.py` | Mock top list and `LeaderboardIndexHook` | Implement Heap / Priority Queue or chosen top-N structure |
| Leaderboard rank lookup | `client/services/leaderboard_service.py` | `get_player_rank(...)` placeholder scan | Implement rank lookup with final ranking/index structure |
| Score range queries | `client/services/leaderboard_service.py`, `client/placeholders/data_structures.py` | `get_score_range(...)` placeholder | Implement BST/range-query structure or justified alternative |
| Match history lookup | `client/services/history_service.py`, `client/placeholders/data_structures.py` | Mock filters for player, game, result, date range | Implement username/game/date/outcome indexes for 100,000+ sessions |
| Match history sorting | `client/services/history_service.py`, `client/placeholders/sorting_algorithms.py` | `sorted_by_date(...)` placeholder | Implement and benchmark one required sorting algorithm here |
| Session-based chat | `client/services/chat_service.py`, `client/services/session_chat.py`, `client/placeholders/chat_buffer.py` | One chat log per session and bounded recent-message buffer | Connect to server broadcast; decide if circular buffer counts as final structure |
| Live chat networking | `client/integrations/cpp_server.py` | `send_chat_message(...)` placeholder | Implement C++ protocol for chat send/receive/broadcast |
| C++ multiplayer handoff | `client/services/game_launch_service.py`, `client/integrations/cpp_server.py` | Session request/response placeholders and `session_info` handoff | Implement server session creation/joining and token handling |
| Completed session result processing | `platform_server/session_results.py`, `client/services/session_result_service.py`, `client/models/session_result.py`, `client/services/session_result_service.py` | Result model, validation scaffold, launcher handoff, leaderboard/history/profile/persistence TODO hooks | Validate real results, update final data structures, persist accepted scores |
| Real playable game | `games/game_1/code/game/main.py`, `games/game_2/code/game/main.py`, etc.; `client/services/game_launch_registry.py` | Subprocess launch contract, team folder convention, temporary Snake test under `games/game_5/` | Add 4 team games; mark the real playable game connected |
| Placeholder games | `client/data/mock_games.py`, `client/services/game_launch_registry.py` | Safe not-connected messages | Replace placeholders when uploaded games are ready |
| Required data structures | `client/placeholders/data_structures.py` | Protocols for player, catalog, leaderboard, history, profile, chat, graph | Implement at least 5 structures, with 3 new to the assignment if required |
| Required sorting algorithms | `client/placeholders/sorting_algorithms.py` | Catalog, leaderboard, and history sort placeholders | Implement at least 2 sorting algorithms used by real features |
| Timing experiments | `client/placeholders/analysis.py` | `QueryMetrics` and brute-force comparison placeholder | Record timing/comparisons and summarize results for report |
| Complexity writeup | `docs/work_remaining.md`, `docs/build_guide.md`, `docs/scalability_notes.md` | Checklists and architecture notes | Fill in actual Big-O, benchmark results, and final conclusions |

## Suggested Data Structure Placement

- Hash Table:
  - Exact player lookup in `SearchService` / `ProfileService`
  - Exact game lookup in `CatalogService`
  - Exact session lookup if session IDs are queried often

- Trie:
  - Player autocomplete in `SearchService.autocomplete_players(...)`
  - Optional game title autocomplete in `CatalogService.search_games(...)`

- BST / Balanced Tree:
  - Score range queries in `LeaderboardService.get_score_range(...)`
  - Date range queries in `HistoryService.get_sessions_by_date_range(...)`
  - Sorted catalog/rank traversal if your design needs ordered browsing

- Heap / Priority Queue:
  - Top-N leaderboard in `LeaderboardService.get_leaderboard(...)`
  - Popular games or active sessions if the team chooses that feature

- Graph:
  - Recommendations in `CatalogService.get_home_rows(...)`
  - Player-game-genre relationships or matchmaking/lobby links

- Additional chosen structure:
  - Linked list/deque/circular buffer for recent match or chat history
  - Trie for search if not already counted
  - Custom indexed array for chronological session browsing

## Scale-Critical Mock Code To Replace

The following code paths intentionally use brute-force or built-in mock logic so
the UI can run immediately. They should not be treated as final assignment
solutions:

- Player search:
  - `SearchService.search_players(...)`
  - Replace with Trie / Hash Table / BST-backed search and autocomplete.

- Game search and filtering:
  - `CatalogService.filter_games(...)`
  - `CatalogService.search_games(...)`
  - Replace with genre, title/tag, creator, and popularity indexes.

- Catalog sorting:
  - `CatalogService.sort_games(...)`
  - Replace or route through the team's required sorting algorithms.

- Leaderboards:
  - `LeaderboardService.get_leaderboard(...)`
  - `LeaderboardService.get_player_rank(...)`
  - `LeaderboardService.get_score_range(...)`
  - Replace with heap / priority queue, BST/range index, or documented
    alternatives.

- Match history:
  - `HistoryService.get_sessions(...)`
  - `HistoryService.filter_sessions(...)`
  - `HistoryService.get_sessions_by_date_range(...)`
  - Replace with indexes for username, game_id, date range, and outcome.

- Profiles:
  - `ProfileService.aggregate_profile_stats(...)`
  - Replace mock fields with aggregation from the final session/history index.

## Do Not Mix Responsibilities

- Do not implement data structures inside `screens/`.
- Do not load final datasets inside UI drawing functions.
- Do not open C++ sockets from components.
- Do not hide sorting algorithms inside a one-off screen method.
- Keep mock data in `data/` until it is replaced by the real ingestion pipeline.
- Keep service method names stable so UI teammates and data-structure teammates
  can work in parallel.
