# Data

Synthetic dataset files live under `data/synthetic_dataset/` and must be
committed/submitted with the final project.

Generate the dataset:

```powershell
python data/generate_dataset.py
```

Default output:

- `data/synthetic_dataset/players.json`: 10,000+ player records
- `data/synthetic_dataset/sessions.json`: 100,000+ game session records
- `data/synthetic_dataset/chat_messages.json`: 50,000+ chat records
- `data/synthetic_dataset/game_catalog.json`: 100+ game catalog records
- `data/synthetic_dataset/manifest.json`: generation metadata

Platform loading entry point:

- `platform_server/data_ingest.py`

TODO(DATASET CLEANING): Add optional noisy records and documented cleaning rules
if the professor expects a data-cleaning section in the report.
