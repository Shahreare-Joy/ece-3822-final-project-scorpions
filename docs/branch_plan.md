# Branch Plan

Keep `main` runnable. Each feature branch should compile before merge:

```powershell
python -B -m py_compile main.py (Get-ChildItem .\client -Recurse -Filter *.py)
```

## Recommended Branches

- `main`: stable demo baseline.
- `ui-foundation`: core app, layout, theme, shared UI components.
- `catalog-details`: mock catalog, genre filters, home rows, game details.
- `profile-search-history`: profile, search, match history, reusable rows.
- `leaderboards-analysis-ui`: leaderboard UI, rank display, analysis display hooks.
- `real-playable-game`: actual playable game and client-side launch flow.
- `backend-hooks-cpp`: C++ server handoff, login/session/chat/scoreboard protocol.
- `data-structures`: hash table, BST, heap, graph, and chosen additional structure.
- `dataset-cleaning`: dataset ingestion, messy record cleanup, validation notes.
- `report-demo`: screenshots, benchmark tables, complexity analysis, final script.

## Suggested Ownership

- Person 1: `core/`, `components/`, visual consistency, navigation, screen registry.
- Person 2: `data/`, `games/`, `screens/home.py`, `screens/browse.py`, `screens/game_details.py`.
- Person 3: `screens/profile.py`, `screens/search.py`, `screens/history.py`, `screens/leaderboard.py`.
- Person 4: `services/`, `integrations/`, `placeholders/`, dataset and C++ handoff planning.
