# Synthetic Dataset Guide

The final project now requires the synthetic dataset to be created, committed,
and submitted with the code.

## Generate The Dataset

From the repository root:

```powershell
python data/generate_dataset.py
```

The generator is deterministic by default, using seed `3822`, so teammates can
recreate the same dataset unless they intentionally change the seed.

Custom sizes:

```powershell
python data/generate_dataset.py --players 10000 --sessions 100000 --chat 50000 --games 120
```

## Output Location

Generated files live in:

```text
data/synthetic_dataset/
```

Required committed files:

- `players.json`
- `sessions.json`
- `chat_messages.json`
- `game_catalog.json`
- `manifest.json`

Do not submit only the generator. The generated JSON files must be included with
the project submission unless the professor explicitly says otherwise.

## Dataset Targets

- 10,000+ player records
- 100,000+ game session records
- 50,000+ chat messages
- 100+ game catalog records
- Synthetic activity spread across about one year

## Player Record Format

Example:

```json
{
  "player_id": "player_00001",
  "username": "scorpion_00001",
  "display_name": "Scorpion 00001",
  "created_at": "2025-09-18T14:20:00",
  "region": "NA-East",
  "favorite_genre": "Arcade",
  "skill_rating": 1530,
  "total_score": 812400,
  "games_played": 142,
  "avatar": "avatar_03.png",
  "account_status": "active"
}
```

Future use:

- account hash table
- profile lookup
- player search/autocomplete
- player-game graph relationships

## Session Record Format

Example:

```json
{
  "session_id": "session_000001",
  "player_id": "player_00001",
  "username": "scorpion_00001",
  "game_id": "game_1",
  "game_title": "Game 1 Snake",
  "started_at": "2026-01-22T18:30:15",
  "duration_seconds": 510,
  "score": 18420,
  "outcome": "Win",
  "platform": "desktop",
  "server_region": "NA-East"
}
```

Future use:

- match history indexes
- leaderboard builders
- profile aggregation
- performance benchmarks

## Chat Message Record Format

Example:

```json
{
  "message_id": "message_000001",
  "session_id": "session_000001",
  "player_id": "player_00001",
  "username": "scorpion_00001",
  "game_id": "game_1",
  "sent_at": "2026-01-22T18:34:10",
  "text": "gg",
  "moderation_status": "clean"
}
```

Future use:

- bounded per-session circular buffers
- chat moderation tests
- optional restart recovery snapshots

## Game Catalog Record Format

Example:

```json
{
  "game_id": "game_1",
  "title": "Game 1 Snake",
  "creator": "Team Scorpions",
  "genre": "Arcade",
  "playable": true,
  "launch_path": "games.game_1.main",
  "thumbnail_path": "client/assets/thumbnails/game_1.png",
  "screenshot_paths": ["client/assets/screenshots/game_1_preview.png"],
  "created_at": "2025-06-01T11:00:00",
  "last_updated": "2026-03-12T09:15:00",
  "total_plays": 120000,
  "currently_playing": 430,
  "min_players": 1,
  "max_players": 1,
  "supports_multiplayer": false,
  "status": "Playable starter",
  "tags": ["team-game", "arcade", "scaffold"]
}
```

Future use:

- catalog hash table
- genre filtering index
- game search
- game launch registry
- recommendations graph

## Platform Loading

Dataset loading starts in:

```text
platform_server/data_ingest.py
```

Useful checks:

```powershell
python - <<'PY'
from platform_server.data_ingest import DataIngestService
svc = DataIngestService()
print(svc.validate_all())
print({k: len(v) for k, v in svc.load_all().items()})
PY
```
