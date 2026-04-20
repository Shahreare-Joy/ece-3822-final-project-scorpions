# Scalability Notes

This document explains how the scaffold is intended to support the larger final
project requirements after the team implements the real backend/data-structure
logic.

The current UI runs on mock data. The architecture is designed so the mock scans
can later be replaced behind the service layer without rewriting screens.

## Scale Targets

Expected final-project scale:

- 10,000+ players
- 100,000+ game sessions
- multiple game catalog rows, including 4 team games
- leaderboard ranking and range queries
- player search/autocomplete
- game search/filter/sort
- per-session chat
- timing/complexity experiments

## Key Architecture Idea

Screens should stay simple:

```text
screen -> service -> data structure / integration / dataset
```

This means:

- `screens/` draw UI and handle buttons.
- `services/` expose feature-level methods like `search_players(...)`,
  `get_leaderboard(...)`, and `get_sessions(...)`.
- `placeholders/` will hold the final data structures, sorting algorithms, and
  benchmark helpers.
- `integrations/` will load datasets and communicate with the C++ server.

When the real structures are implemented, screens should not need major changes.

## 10,000+ Players

Current scaffold:

- Mock players live in `client/data/mock_players.py`.
- Player lookup goes through `client/services/profile_service.py`.
- Player search goes through `client/services/search_service.py`.
- Future interfaces live in `client/placeholders/data_structures.py`.

Planned scalable design:

- Use a hash table for exact username lookup.
- Use a Trie or prefix-supporting structure for autocomplete.
- Optionally use a BST if ordered player traversal is part of the final design.

Why:

- A brute-force scan over 10,000 players may still run, but it is not a strong
  data-structure demonstration.
- Autocomplete needs prefix-aware lookup, which fits a Trie better than a list.
- Exact lookup should avoid scanning every player.

Where to implement:

- Add the final structure under `client/placeholders/data_structures.py`
  or a new team-owned module imported from there.
- Replace scan logic in `SearchService` and `ProfileService` with calls to that
  structure.
- Benchmark against the current brute-force scan using
  `client/placeholders/analysis.py`.

## 100,000+ Sessions

Current scaffold:

- Mock sessions live in `client/data/mock_sessions.py`.
- History lookup goes through `client/services/history_service.py`.
- Session model lives in `client/models/session.py`.

Planned scalable design:

- Build an index from `username -> sessions`.
- Build an index from `game_id -> sessions`.
- Build a date/time index for range queries.
- Keep a recent-session chronological structure for quick recent activity.

Why:

- Filtering 100,000 sessions repeatedly with list scans will feel slow and is a
  weak final design.
- Profile pages, game detail pages, and history screens all need different views
  of the same session dataset.
- Date range queries are a natural place to use a BST/tree-like structure.

Where to implement:

- Define the final interface in `client/placeholders/data_structures.py`.
- Replace scan logic in `client/services/history_service.py`.
- Use `client/placeholders/sorting_algorithms.py` when sorted session
  output is required.
- Record timing in `client/placeholders/analysis.py`.

## Responsive Leaderboards

Current scaffold:

- Mock leaderboard rows live in `client/data/mock_leaderboards.py`.
- Leaderboard queries go through `client/services/leaderboard_service.py`.

Planned scalable design:

- Use a heap / priority queue for top-N lookup.
- Use a BST or ordered score index for score range queries.
- Keep a player rank lookup path for profile pages and game details.
- Use required sorting algorithms for leaderboard display comparisons.

Why:

- Top-N and range queries are different operations and may need different
  structures.
- Rank lookup should not require recomputing a full sorted leaderboard every
  time.
- Leaderboards are a clear feature to explain in the final report.

Where to implement:

- `client/services/leaderboard_service.py`
- `client/placeholders/data_structures.py`
- `client/placeholders/sorting_algorithms.py`
- `client/placeholders/analysis.py`

## Game Catalog Search And Sorting

Current scaffold:

- Mock catalog records live in `client/data/mock_games.py`.
- Browse and home rows call `client/services/catalog_service.py`.

Planned scalable design:

- Use exact lookup by `game_id`.
- Add genre index for Browse filtering.
- Add title/tag/creator index for game search.
- Add sorting support for popularity, release year, play count, and recent
  activity.
- Use a graph if recommendations become part of the final data-structure plan.

Why:

- The Home screen should not sort or scan a large catalog every frame.
- Browse filtering should be a service/index concern, not a screen concern.
- Recommendations fit naturally as a graph explanation if the team chooses it.

Where to implement:

- `client/services/catalog_service.py`
- `client/placeholders/data_structures.py`
- `client/placeholders/sorting_algorithms.py`

## Chat And Session Memory

Current scaffold:

- Chat messages use `client/models/chat_message.py`.
- Chat service is in `client/services/chat_service.py`.
- One session log is represented by `client/services/session_chat.py`.
- Bounded storage is in `client/placeholders/chat_buffer.py`.

Planned scalable design:

- Keep one chat log per session.
- Store only the last N messages on the client.
- Broadcast and receive real messages through the future C++ server.
- Validate and sanitize messages before sending.

Why:

- Chat can grow forever if the client stores unlimited history.
- A circular buffer or bounded queue is a good fit because the UI usually needs
  only recent messages.
- Per-session logs prevent players from seeing messages from unrelated matches.

Where to implement:

- `client/services/chat_service.py`
- `client/services/session_chat.py`
- `client/placeholders/chat_buffer.py`
- `client/integrations/cpp_server.py`

## Dataset Pipeline

Current scaffold:

- Mock data is separated in `client/data/`.
- The required submitted dataset lives in `data/synthetic_dataset/`.
- The deterministic generator is `data/generate_dataset.py`.
- Platform loading/validation lives in `platform_server/data_ingest.py`.
- Cleaning hooks live in `client/placeholders/dataset_cleaning.py`.

Current generated target sizes:

- 10,000 players in `players.json`
- 100,000 sessions in `sessions.json`
- 50,000 chat messages in `chat_messages.json`
- 120 catalog games in `game_catalog.json`

Planned scalable design:

1. Load raw synthetic records.
2. Clean/validate records.
3. Convert cleaned records into model objects.
4. Build indexes/data structures.
5. Let services query those structures.

Examples of noisy data to handle:

- missing usernames
- duplicate player rows
- invalid game IDs
- negative scores
- malformed timestamps
- impossible play durations
- inconsistent genre labels
- missing session IDs

## Benchmarking And Complexity

Current scaffold:

- `QueryMetrics` lives in `client/placeholders/data_structures.py`.
- Benchmark placeholders live in `client/placeholders/analysis.py`.

Planned scalable design:

- Benchmark brute-force scan vs final structure for player search.
- Benchmark brute-force leaderboard sort vs heap/BST approach.
- Benchmark history scan vs indexed history lookup.
- Benchmark catalog scan/sort vs catalog indexes.

What to record:

- operation name
- structure name
- input size
- elapsed time
- comparison count if relevant
- Big-O explanation
- short notes for the report

Important:

- Do not run benchmarks inside Pygame draw methods.
- Run experiments from a separate script or controlled service call.
- Keep the UI responsive even when benchmark data grows.

## Brute-Force Replacement Checklist

Before the final submission, inspect service files for comments labeled
`BRUTE-FORCE MOCK WARNING`, `MOCK SORT WARNING`, or `MOCK AGGREGATION WARNING`.
Each one marks a code path that exists only to keep the UI prototype runnable.

Replace those paths with team-owned structures/algorithms, then record:

- which structure replaced the scan
- why that structure fits the operation
- expected Big-O
- measured timing on the final dataset size
- comparison against the brute-force baseline where required

## Summary

The scaffold is ready for scale because each major feature already has a service
boundary. Your team can replace mock scans with real data structures behind
those services while keeping the UI stable.
