# Scorpions Arcade Project Notes

## What Is Scaffolded

- Pygame app startup and main event loop under `client/core/app.py`.
- Screen registration under `client/core/screen_registry.py`.
- Central routing enum under `client/core/router.py`.
- Shared layout/theme/config helpers under `client/core/`.
- Reusable UI components under `client/components/`.
- Separate model dataclasses under `client/models/`.
- Mock data split by type under `client/data/`.
- Major screens split into one file per screen under `client/screens/`.
- Temporary service layer split by feature under `client/services/`.
- Chat preview logic is isolated in `services/chat_service.py`.
- Per-session chat logs use `services/session_chat.py` plus the bounded
  circular-buffer scaffold in `placeholders/chat_buffer.py`.
- C++/backend/dataset hooks under `client/integrations/`.
- Data-structure/sorting/analysis/cleaning placeholders under `client/placeholders/`.
- Uploaded playable games should live under top-level `games/game_1/` through
  `games/game_4/` using `code/game/main.py` as the entry point.

## What Your Team Still Implements

- Real playable game behavior for Scorpions Arena or whichever game the team chooses.
- C++ multiplayer server handoff and session protocol.
- Dataset ingestion and cleaning pipeline.
- Required custom data structures and sorting/query logic.
- Leaderboard ranking, rank lookup, and range queries.
- Player search structure and benchmark results.
- Match history indexing and filters.
- Catalog indexing and recommendation logic.
- Performance measurement, complexity analysis, report, and demo.

## How Future Structures Connect

- `services/catalog_service.py` should call the final catalog index.
- `services/search_service.py` should call the final player search structure.
- `services/leaderboard_service.py` should call the final heap/BST/sorting structure.
- `services/history_service.py` should call the final session-history structure.
- `services/chat_service.py` should call the future C++ chat/lobby integration.
- `services/session_chat.py` should stay focused on one session's recent log.
- `placeholders/chat_buffer.py` can become the final bounded queue/circular
  buffer if your team chooses to analyze it as one of the required structures.
- `services/game_launch_service.py` should call the C++ session handoff.
- `services/game_launch_registry.py` maps arcade `game_id` values to game
  entry points under top-level `games/`.
- `placeholders/data_structures.py` describes the expected interfaces.
