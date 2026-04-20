# Scorpions Arcade API Documentation Scaffold

This file documents the planned platform-server message shapes. It is a contract
template, not a finished backend implementation.

The Python/Pygame client should eventually send these requests to the Python
platform server. The platform server may then coordinate with the future C++
multiplayer game server for live sessions.

## General Message Envelope

Every request should eventually use a consistent envelope:

```json
{
  "type": "request_type",
  "request_id": "client-generated-id",
  "player_id": "optional-player-id",
  "payload": {}
}
```

Expected response shape:

```json
{
  "ok": true,
  "request_id": "client-generated-id",
  "error": null,
  "payload": {}
}
```

TODO(API RESILIENCE): Define standard error codes for invalid JSON, missing
fields, unauthorized players, unavailable games, and server failures.

## Message Type Summary

Planned request types:

- `login`
- `create_account`
- `player_search`
- `player_autocomplete`
- `catalog_query`
- `game_details`
- `game_launch_request`
- `session_result_submit`
- `leaderboard_query`
- `match_history_query`
- `chat_send`
- `chat_fetch`
- `chat_moderation_action`
- `session_heartbeat`

TODO(API ROUTER): Keep this list synchronized with `platform_server/server.py`
when the real request router is implemented.

## Login

Request:

```json
{
  "type": "login",
  "request_id": "req-001",
  "payload": {
    "username": "scorpion42",
    "password": "student-owned-password-handling"
  }
}
```

Expected behavior:

- Validate required fields.
- Look up the account through the final account index.
- Return player profile summary if successful.
- Return a safe error response if the username/password is invalid.

TODO(ACCOUNTS): Implement password handling and account lookup in
`platform_server/accounts.py`.

## Create Account

Request:

```json
{
  "type": "create_account",
  "request_id": "req-002",
  "payload": {
    "username": "new_player",
    "display_name": "New Player",
    "password": "student-owned-password-handling"
  }
}
```

Expected behavior:

- Reject duplicate usernames.
- Validate username length and allowed characters.
- Persist the new account after creation.

TODO(PERSISTENCE): Save accounts through `platform_server/persistence.py` after
signup.

## Player Search

Request:

```json
{
  "type": "player_search",
  "request_id": "req-003",
  "payload": {
    "query": "sha",
    "limit": 10
  }
}
```

Expected behavior:

- Return matching players quickly for 10,000+ player records.
- Support exact lookup and autocomplete if the team implements it.

TODO(SEARCH): Replace brute-force scans with a Trie, BST, Hash Table, or a
documented combination in `platform_server/search.py`.

## Player Autocomplete

Request:

```json
{
  "type": "player_autocomplete",
  "request_id": "req-003b",
  "payload": {
    "prefix": "sco",
    "limit": 8
  }
}
```

Expected behavior:

- Return short suggestions suitable for the Search Players screen.
- Use a prefix-friendly structure for 10,000+ players.
- Benchmark against brute force.

TODO(AUTOCOMPLETE): Implement in `platform_server/search.py` after the chosen
Trie/BST/hash-table strategy is approved by the team.

## Game Catalog Query

Request:

```json
{
  "type": "catalog_query",
  "request_id": "req-004",
  "payload": {
    "genre": "Arcade",
    "sort_by": "popular",
    "limit": 25
  }
}
```

Expected behavior:

- Filter by genre, creator/team, playable status, and popularity.
- Return thumbnail/screenshot metadata for the client UI.
- Support many student games without hardcoding screen logic.

TODO(CATALOG): Build final indexes in `platform_server/catalog.py` and
`platform_server/game_registry.py`.

## Game Details

Request:

```json
{
  "type": "game_details",
  "request_id": "req-004b",
  "payload": {
    "game_id": "game_1"
  }
}
```

Expected behavior:

- Return title, creator/team, genre, tags, playable status, launch status,
  player count ranges, thumbnail path, screenshot paths, and description.
- Return safe placeholder data if a game is registered but not connected yet.

TODO(GAME REGISTRY): Use the central registry first, then merge in final
dataset-backed catalog fields when the team implements ingestion.

## Game Launch Request

Request:

```json
{
  "type": "game_launch_request",
  "request_id": "req-004c",
  "player_id": "player_123",
  "payload": {
    "game_id": "game_1",
    "requested_mode": "solo"
  }
}
```

Expected behavior:

- Confirm the game is registered and playable.
- Create or reserve a future session id.
- Return future C++ server connection data when multiplayer is ready.
- Return a clear safe error when the game is only a placeholder.

Example successful future response:

```json
{
  "ok": true,
  "request_id": "req-004c",
  "error": null,
  "payload": {
    "game_id": "game_1",
    "session_id": "session_9001",
    "server_host": "127.0.0.1",
    "server_port": 7000,
    "launch_path": "games.game_1.main"
  }
}
```

TODO(C++ HANDOFF): Define the real `session_id`, `server_host`, `server_port`,
and player token flow with `cpp_server/`.

## Session Result Submit

Request:

```json
{
  "type": "session_result_submit",
  "request_id": "req-004d",
  "player_id": "player_123",
  "payload": {
    "session_id": "session_9001",
    "game_id": "game_1",
    "score": 18420,
    "outcome": "Win",
    "duration_seconds": 315,
    "timestamp": "2026-04-20T18:30:00Z",
    "metadata": {
      "level": 4,
      "coins": 88
    }
  }
}
```

Expected behavior:

- Validate that the session was created by the server.
- Validate that the player belongs to the session.
- Validate score bounds and allowed outcome values for that game.
- Update leaderboard structures.
- Record match history.
- Update profile aggregate stats.
- Persist accepted changes for restart recovery.

TODO(RESULTS): Implement this in `platform_server/session_results.py` and route
the request through `platform_server/server.py`.

TODO(ANTI-CHEAT): Do not trust raw client scores in the final multiplayer
version. The C++ server should be authoritative for live game results.

## Leaderboard Query

Request:

```json
{
  "type": "leaderboard_query",
  "request_id": "req-005",
  "payload": {
    "game_id": "game_1",
    "query": "top_n",
    "n": 10
  }
}
```

Range query example:

```json
{
  "type": "leaderboard_query",
  "request_id": "req-006",
  "payload": {
    "game_id": "game_1",
    "query": "score_range",
    "low": 1000,
    "high": 5000
  }
}
```

Expected behavior:

- Return top-N rankings.
- Support player rank lookup.
- Support score range queries for analysis/report requirements.

TODO(LEADERBOARD): Use `datastructures/heap.py`, `datastructures/bst.py`, and
`algorithms/` as appropriate.

## Match History Query

Request:

```json
{
  "type": "match_history_query",
  "request_id": "req-007",
  "payload": {
    "player_id": "player_123",
    "game_id": "optional-game-filter",
    "outcome": "optional-outcome-filter",
    "start_date": "2026-01-01",
    "end_date": "2026-04-20",
    "limit": 50
  }
}
```

Expected behavior:

- Query 100,000+ session records through indexes, not full scans.
- Filter by player, game, date range, and outcome.
- Sort results by recency or score when requested.

TODO(HISTORY): Implement final indexes in `platform_server/history.py`.

## Chat Message Send

Request:

```json
{
  "type": "chat_send",
  "request_id": "req-008",
  "payload": {
    "session_id": "session_9001",
    "player_id": "player_123",
    "text": "Good luck!"
  }
}
```

Expected behavior:

- Validate the player belongs to the session.
- Run moderation checks.
- Append to the session circular buffer.
- Broadcast to other players in the same session.

TODO(CHAT): Connect `platform_server/chat.py`, `platform_server/moderation.py`,
and the future C++ chat relay.

## Chat Message Fetch

Request:

```json
{
  "type": "chat_fetch",
  "request_id": "req-009",
  "payload": {
    "session_id": "session_9001",
    "limit": 50
  }
}
```

Expected behavior:

- Return only recent messages for the requested session.
- Do not expose messages from other sessions.
- Keep memory bounded with a circular buffer.

TODO(CIRCULAR BUFFER): Finish `datastructures/circular_buffer.py` and connect it
through `platform_server/chat.py`.

## Chat Moderation Action

Request:

```json
{
  "type": "chat_moderation_action",
  "request_id": "req-010",
  "player_id": "moderator_1",
  "payload": {
    "action": "mute",
    "target_player_id": "player_456",
    "session_id": "session_9001",
    "duration_seconds": 300
  }
}
```

Expected behavior:

- Validate moderator permission.
- Apply session-level or global mute rules.
- Return a safe error if the target/session does not exist.

TODO(MODERATION): Complete `platform_server/moderation.py` rate limiting, word
filtering, toxicity hook, mute/unmute, and audit behavior.

## Session Heartbeat

Request:

```json
{
  "type": "session_heartbeat",
  "request_id": "req-011",
  "player_id": "player_123",
  "payload": {
    "session_id": "session_9001",
    "game_id": "game_1",
    "client_state": "playing"
  }
}
```

Expected behavior:

- Track whether a player is still connected to a session.
- Help clean up stale sessions.
- Coordinate with the future C++ server if real-time multiplayer is active.

TODO(SESSION MANAGER): Add this after the team defines session lifecycle rules.

## Persistence Events

The platform should eventually save data after:

- successful account creation or profile update
- validated leaderboard score update
- completed game session
- catalog/registry update
- optional bounded chat snapshot

TODO(PERSISTENCE): Implement these events through `platform_server/persistence.py`.
Avoid writing persistence logic directly inside UI screens.

## Error Handling Requirements

The final server should safely handle:

- Missing request type
- Unknown request type
- Missing payload fields
- Bad field types
- Unauthorized player/session access
- Malformed JSON
- Oversized chat messages
- Requests for games not connected yet
- Duplicate request ids, if the team chooses idempotency support
- Rate-limited chat messages
- Corrupt persisted files during restart recovery

TODO(RESILIENCE): Add safe try/except boundaries in `platform_server/server.py`
without hiding bugs during development. Return structured error responses.

## Standard Error Shape

Future error responses should look like:

```json
{
  "ok": false,
  "request_id": "req-unknown",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: game_id",
    "details": {}
  },
  "payload": {}
}
```

Suggested starter error codes:

- `INVALID_JSON`
- `INVALID_REQUEST`
- `UNAUTHORIZED`
- `NOT_FOUND`
- `GAME_NOT_CONNECTED`
- `RATE_LIMITED`
- `VALIDATION_FAILED`
- `SERVER_ERROR`

TODO(API RESILIENCE): Use these codes consistently in the real server router.
