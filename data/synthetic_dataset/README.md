# Synthetic Dataset

This folder stores the generated dataset that must be committed and submitted
with the project.

Generate or refresh the files from the repo root:

```powershell
python data/generate_dataset.py
```

Required generated files:

- `players.json`: player/account/profile-like records
- `sessions.json`: historical game session records
- `chat_messages.json`: synthetic per-session chat messages
- `game_catalog.json`: game catalog metadata
- `manifest.json`: counts, seed, and generation timestamp

Target sizes:

- 10,000+ players
- 100,000+ sessions
- 50,000+ chat messages
- 100+ catalog games

The current generated JSON includes realistic skew: popular games and active
players produce more sessions, each player has genre preferences, scores depend
partly on skill, durations/chat volume have long tails, and similar players
overlap in games played so recommendations are not random.

The current CSV files are legacy placeholders. The JSON files are the dataset
format expected by `platform_server/data_ingest.py`.

If the schema changes, update `data/generate_dataset.py`,
`platform_server/data_ingest.py`, `tools/verify_project.py`, and the
documentation together.
