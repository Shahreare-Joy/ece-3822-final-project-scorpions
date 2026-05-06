# Scorpions Arcade API Documentation

This document describes the current API and message behavior used by the
Scorpions Arcade platform. It is written for the final demo/report and matches
the arcade work in this project: Pygame client, Python platform server, and C++
gameplay server.

## 1. System Roles

### Pygame Client

The client runs `main.py`. It handles the arcade UI, login screen, home page,
browse/search, game details, profiles, leaderboards, history, chat overlay, and
launching games.

### Python Platform Server

The Python platform server owns account lookup, catalog data, player search,
leaderboards, match history, session results, and chat storage.

Start command:

```bash
python -m platform_server.server --host 0.0.0.0 --port 50068 --serializer json
```

Default port:

```text
50068
```

### C++ Gameplay Server

The C++ gameplay server is used for real-time gameplay connection checks and
basic multiplayer state exchange.

Start command from the `server/` folder:

```bash
./server_json_jitter --port 50069
```

Default gameplay port:

```text
50069
```

### Client Server Mode

Run the arcade client in server mode:

```bash
python main.py --server 127.0.0.1 --port 50068 --game-port 50069 --serializer json
```

For SSH tunnels, replace the host/ports with the forwarded local tunnel values.

## 2. Wire Format

The Python platform server uses a simple TCP request/response protocol.

In JSON mode, each request is one JSON object followed by a newline:

```json
{"type": "health"}
```

Each response is one JSON object followed by a newline:

```json
{"ok": true, "type": "health", "message": "Python platform server is online."}
```

The server also accepts `action` as an alias for `type`:

```json
{"action": "leaderboard", "game_id": "game_1", "limit": 10}
```

Most requests use flat JSON fields instead of a deeply nested envelope. The
`submit_result` request also accepts either flat fields or a nested `payload`.

## 3. Standard Response Pattern

Most successful responses include:

```json
{
  "ok": true
}
```

Most rejected responses include:

```json
{
  "ok": false,
  "message": "Reason the request failed."
}
```

Some endpoints return extra fields such as `player`, `games`, `leaders`,
`sessions`, or `messages`.

## 4. Platform Server Requests

### 4.1 Health / Ping

Purpose: Check whether the Python platform server is online.

Request:

```json
{
  "type": "health"
}
```

Also supported:

```json
{
  "type": "ping"
}
```

Response:

```json
{
  "ok": true,
  "type": "health",
  "message": "Python platform server is online."
}
```

Used by: server-mode connection checks.

### 4.2 Login

Purpose: Validate a player login using demo accounts / loaded account data.

Request:

```json
{
  "type": "login",
  "username": "kevin",
  "password": "vek069"
}
```

Success response:

```json
{
  "ok": true,
  "message": "Login accepted.",
  "player": {
    "username": "kevin",
    "display_name": "Kevin"
  }
}
```

Failure response:

```json
{
  "ok": false,
  "message": "Invalid username or password."
}
```

Notes:

- Usernames are normalized to lowercase.
- Demo accounts are loaded from `data/demo_accounts.json`.
- If remote login is unavailable, the client can fall back to local account
  handling so the demo does not crash.

### 4.3 Search Players

Purpose: Search player records for the Search Players screen.

Request:

```json
{
  "type": "search_players",
  "query": "kev",
  "limit": 10
}
```

Response:

```json
{
  "ok": true,
  "players": [
    {
      "username": "kevin",
      "display_name": "Kevin"
    }
  ]
}
```

Notes:

- The server clamps the limit to a safe maximum of 100.
- Search data is indexed during server startup.
- The client also has local search/index fallback for demo safety.

### 4.4 Catalog

Purpose: Return game catalog rows for Home, Browse, and Game Details screens.

Request:

```json
{
  "type": "catalog",
  "limit": 120
}
```

Response:

```json
{
  "ok": true,
  "games": [
    {
      "game_id": "game_1",
      "title": "Fruit Drop Rush",
      "genre": "Arcade",
      "playable": true,
      "launch_path": "games/game_1/code/game/main.py",
      "thumbnail_path": "client/assets/thumbnails/fruit_drop_rush.png"
    }
  ]
}
```

Notes:

- The server loads catalog records from the project dataset/registry.
- The client also keeps local catalog indexes for fast browse/filter behavior.
- Team games do not use fake leaderboard/activity data for new scores.

### 4.5 History

Purpose: Return match/session history.

Request player history:

```json
{
  "type": "history",
  "username": "kevin",
  "limit": 25
}
```

Request game history:

```json
{
  "type": "history",
  "game_id": "game_1",
  "limit": 25
}
```

Response:

```json
{
  "ok": true,
  "sessions": [
    {
      "session_id": "local-game_1",
      "username": "kevin",
      "player_id": "kevin",
      "game_id": "game_1",
      "score": 42,
      "outcome": "Game Over",
      "duration_seconds": 61,
      "started_at": "2026-05-05T18:20:00Z"
    }
  ]
}
```

Notes:

- History is indexed by player and game.
- If neither `username` nor `game_id` is sent, the server returns recent session
  rows.
- The client uses this for Profile, History, Game Details Recent Activity, and
  Recently Played.

### 4.6 Leaderboard

Purpose: Return top scores for one game.

Request:

```json
{
  "type": "leaderboard",
  "game_id": "game_1",
  "limit": 10
}
```

Response:

```json
{
  "ok": true,
  "leaders": [
    {
      "game_id": "game_1",
      "username": "kevin",
      "score": 42,
      "timestamp": "2026-05-05T18:20:00Z"
    }
  ]
}
```

Notes:

- `game_id` is the key used to find that game's leaderboard.
- Each game leaderboard stores best score per player.
- Scores of `0` are not placed on the leaderboard.
- Zero-score sessions can still be recorded in history/profile if accepted.
- Team games start empty unless real submitted results exist.

Data structures used:

- Hash table: `game_id -> leaderboard`
- Hash table: `username -> best score`
- Max heap: top-N score lookup
- BST: score range lookup / ranking support

### 4.7 Chat Send

Purpose: Send a chat message to one game session.

Request:

```json
{
  "type": "chat_send",
  "session_id": "local-game_1",
  "sender": "kevin",
  "text": "good luck"
}
```

Success response:

```json
{
  "ok": true,
  "message": "Message stored."
}
```

Rejected response:

```json
{
  "ok": false,
  "message": "Message rejected by chat validation/moderation."
}
```

Behavior:

- Messages are tied to `session_id`.
- Messages from one session are not shown in another session.
- The server cleans text before storing.
- Bad words are filtered before storage/display.
- Empty, oversized, muted, or rate-limited messages are rejected.

Moderation features:

- Blocked-word filtering
- Case-insensitive keyword matching
- Basic toxicity/keyword score helper
- Per-player rate limiting
- Mute/unmute support in the moderation service

### 4.8 Chat Recent

Purpose: Fetch recent chat messages for one session.

Request:

```json
{
  "type": "chat_recent",
  "session_id": "local-game_1",
  "limit": 20
}
```

Response:

```json
{
  "ok": true,
  "messages": [
    {
      "session_id": "local-game_1",
      "sender": "kevin",
      "text": "good luck",
      "sent_at": "2026-05-05T18:20:00+00:00"
    }
  ]
}
```

Notes:

- Chat uses a bounded circular buffer per session.
- `chat_recent` should be polled only while the chat overlay or preview is
  active.
- The chat overlay stops polling when hidden/destroyed or when the player leaves
  the game.
- In local mode, chat can fall back to file-backed session chat in
  `data/runtime_chat/`.

### 4.9 Session Start

Purpose: Register an active game session on the Python platform server.

Request:

```json
{
  "type": "session_start",
  "session_id": "local-game_1",
  "player_id": "kevin",
  "game_id": "game_1"
}
```

Response:

```json
{
  "ok": true,
  "session": "local-game_1"
}
```

Notes:

- If `session_id` is empty, the session manager may generate/use a safe value.
- This is separate from the C++ gameplay socket connection.

### 4.10 Session End / Disconnect

Purpose: Clean up an active session when the player exits a game.

Request:

```json
{
  "type": "session_end",
  "session_id": "local-game_1"
}
```

Also supported:

```json
{
  "type": "disconnect",
  "session_id": "local-game_1"
}
```

Response:

```json
{
  "ok": true,
  "message": "Session cleaned up."
}
```

If the session was not active:

```json
{
  "ok": false,
  "message": "Session was not active."
}
```

Notes:

- Session cleanup prevents ghost players and stale active-session state.
- Chat history is kept available for Profile/History previews after exit.

### 4.11 Submit Result

Purpose: Send a completed game result to the platform so leaderboard, history,
profile stats, and persistence can update.

Flat request:

```json
{
  "type": "submit_result",
  "player_id": "kevin",
  "game_id": "game_1",
  "score": 42,
  "outcome": "Game Over",
  "duration_seconds": 61,
  "timestamp": "2026-05-05T18:20:00Z",
  "session_id": "local-game_1",
  "metadata": {
    "level": "Orchard Run"
  }
}
```

Nested request:

```json
{
  "type": "submit_result",
  "payload": {
    "player_id": "kevin",
    "game_id": "game_1",
    "score": 42,
    "result": "Game Over",
    "duration": 61,
    "session_id": "local-game_1"
  }
}
```

Success response:

```json
{
  "ok": true,
  "message": "Session result accepted and routed to available platform services.",
  "errors": []
}
```

Rejected response:

```json
{
  "ok": false,
  "message": "Session result rejected.",
  "errors": [
    "score must be non-negative"
  ]
}
```

Accepted fields:

| Field | Required | Notes |
| --- | --- | --- |
| `player_id` or `username` | Yes | Player who earned the result |
| `game_id` | Yes | Game that produced the result |
| `score` | Yes | Must be non-negative |
| `outcome` or `result` | No | Defaults to `Finished` |
| `duration_seconds` or `duration` | No | Must be non-negative |
| `timestamp` | No | Defaults to current server time |
| `session_id` | No | Used for duplicate protection |
| `metadata` | No | Extra game-specific details |

Allowed outcomes:

```text
Win, Loss, Draw, Finished, DNF, Complete, Game Over, Time Up, Quit, Return to arcade
```

Result routing:

1. Validate required fields and score/duration.
2. Reject duplicate session result submissions.
3. Submit score to leaderboard if score is greater than `0`.
4. Record session in history.
5. Update profile-style aggregate stats.
6. Persist session result through the persistence layer.

Important:

- A score of `0` should not appear on the leaderboard.
- A score of `0` may still be useful in history/profile as a played session.
- Current anti-cheat is basic validation only; future real-time server authority
  would be stronger.

## 5. Text Serializer Compatibility

The platform server can also run with:

```bash
python -m platform_server.server --host 0.0.0.0 --port 50068 --serializer text
```

Supported simple text commands include:

```text
PING
HEALTH
LOGIN username password
SEARCH_PLAYERS query
```

JSON mode is the recommended mode for the final demo.

## 6. C++ Gameplay Server Protocol

The C++ gameplay server is separate from the Python platform API.

Current demo role:

- Accept gameplay socket connections.
- Send a `CONNECTED|...` style handshake.
- Allow two clients to connect to the same gameplay server port.
- Receive basic player state such as position.
- Broadcast received state so other clients can render a simple remote marker or
  ghost player.

Game clients receive connection settings through environment variables when the
arcade launcher starts a game:

```text
SCORPIONS_GAME_ID
SCORPIONS_SESSION_ID
SCORPIONS_GAME_HOST
SCORPIONS_GAME_PORT
SCORPIONS_GAME_SERIALIZER
SCORPIONS_SERVER_HOST
SCORPIONS_SERVER_PORT
SCORPIONS_SERIALIZER
SCORPIONS_PLAYER
SCORPIONS_DISPLAY_NAME
```

Chat uses the Python platform server, not the C++ gameplay server, because the
platform server already stores session-based chat and applies moderation.

## 7. Chat Environment Variables

The launcher passes these variables to games so the in-game chat overlay works:

```text
SCORPIONS_CHAT_ENABLED=1
SCORPIONS_SESSION_ID=<session id>
SCORPIONS_CHAT_DIR=<project>/data/runtime_chat
SCORPIONS_PLATFORM_CHAT=1 or 0
SCORPIONS_PLATFORM_HOST=<platform host>
SCORPIONS_PLATFORM_PORT=<platform port>
SCORPIONS_PLATFORM_SERIALIZER=json
```

Behavior:

- Server mode: chat sends/polls through `chat_send` and `chat_recent`.
- Local mode: chat uses local/file-backed session chat as fallback.
- If the chat server is unavailable, the overlay should stay visible and show a
  fallback/unavailable status instead of crashing the game.

## 8. Persistence

The platform persistence layer saves important data outside memory.

Current persistence paths are under:

```text
data/synthetic_dataset/
```

Main persisted data:

- Accounts / created account records
- Leaderboards
- Session history
- Catalog data
- Runtime game/session results

Purpose:

- If the Python platform server restarts, player/account/session data can be
  loaded again instead of being lost from memory.

## 9. Resilience Rules

The server is expected to survive bad input during demo/testing.

Handled or guarded cases:

- Invalid JSON
- Empty request
- Request that is not a JSON object
- Unknown request type
- Missing username/password
- Invalid login
- Bad or missing `game_id`
- Bad score values
- Negative duration
- Duplicate session result submission
- Empty chat messages
- Long chat messages
- Rate-limited chat messages
- Chat server unavailable on the client side

Unknown request example:

```json
{
  "ok": false,
  "message": "Unknown platform request: <empty>."
}
```

## 10. Data Structures Behind the API

The API is backed by custom data structures used throughout the platform:

| Feature | Data structure |
| --- | --- |
| Login/account lookup | Custom chained hash table |
| Player search | Search index over loaded players |
| Catalog lookup/filtering | Hash-table style indexes |
| Leaderboard board lookup | Hash table keyed by `game_id` |
| Best score per player | Hash table keyed by username |
| Top-N leaderboard | Max heap |
| Score range lookup | BST |
| Match history lookup | Hash table indexes by player/game/outcome |
| Chat recent messages | Circular buffer per session |
| Chat moderation | Hash tables for blocked words, mute state, and rate-limit buckets |

## 11. Demo Startup Checklist

Start the Python platform server:

```bash
python -m platform_server.server --host 0.0.0.0 --port 50068 --serializer json
```

Start the C++ gameplay server:

```bash
cd server
./server_json_jitter --port 50069
```

Start the client:

```bash
python main.py --server 127.0.0.1 --port 50068 --game-port 50069 --serializer json
```

Expected demo behavior:

- Login succeeds with demo accounts.
- Catalog and game details load.
- Games launch from the arcade.
- Chat overlay opens in supported games.
- Chat messages sync by session in server mode.
- Game results submit after game exit.
- Leaderboard/history/profile update from accepted results.
- If a server is down, the client should fail gracefully and use local fallback
  where available.
