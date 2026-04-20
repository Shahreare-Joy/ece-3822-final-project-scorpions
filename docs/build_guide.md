# Scorpions Arcade Build Guide

This guide explains how to finish the project from the current Scorpions Arcade
template. It is written for the team working inside this codebase, so every step
points to the files and folders you should edit.

## 1. What This Scaffold Already Gives Us

The template already includes the client/UI foundation:

- `main.py` starts the launcher.
- `client/core/` contains the app loop, routing, state, layout, theme,
  and configuration.
- `client/screens/` contains one Pygame screen per file.
- `client/components/` contains reusable UI drawing helpers and
  widgets.
- `client/models/` contains simple dataclasses for players, games,
  sessions, chat, filters, and leaderboard entries.
- `client/data/` contains temporary mock records only.
- `client/services/` contains feature logic for auth, catalog,
  profile, search, history, leaderboards, chat, and game launching.
- top-level `games/` contains pasted teammate game folders using
  `games/<game_id>/code/game/main.py`.
- `client/integrations/` contains future backend/C++/dataset hooks.
- `client/placeholders/` contains starter interfaces for the
  professor-required data structures, sorting, cleaning, and analysis work.
- `docs/requirement_mapping.md` maps each professor requirement to the files
  where the team should finish the real implementation.
- `docs/scalability_notes.md` explains how the service boundaries are intended
  to support 10,000+ players and 100,000+ sessions.

Important boundary: this scaffold is a UI/client foundation. The real final
project logic still belongs to the team.

## 2. Run The Project First

Feature: confirm the baseline runs before changing code.

Why it matters: if the baseline is broken, it becomes hard to know whether your
new change caused a bug.

Files to use:

- `main.py`
- `requirements.txt`

What to do:

```powershell
python main.py
```

Temporary mock login:

```text
username: joy
password: 123456
```

Compile check:

```powershell
python -B -m py_compile main.py (Get-ChildItem .\client -Recurse -Filter *.py)
```

Be careful:

- Do not start by editing many files at once.
- Test the app before and after each feature branch.
- Keep `main.py` as the entry point.

## 3. Understand The Folder Structure

Feature: know where each kind of code belongs.

Why it matters: the project will be easier for four people to work on if files
have one job each.

Main rule:

- UI drawing belongs in `screens/` and `components/`.
- Feature logic belongs in `services/`.
- Temporary sample records belong in `data/`.
- Dataclasses belong in `models/`.
- Future external systems belong in `integrations/`.
- Professor-required structures/algorithms belong in `placeholders/` until your
  team implements them for real.
- Playable game code belongs in `games/`.

Be careful:

- Do not put mock catalog data inside a screen file.
- Do not put search or leaderboard algorithms inside a drawing function.
- Do not hardcode a specific game folder inside a screen.
- Do not put C++ socket code directly inside UI components.

## 4. Polish Or Edit A Screen

Feature: change one launcher screen at a time.

Why it matters: each screen file owns one user-facing page.

Files to edit:

- Home: `client/screens/home.py`
- Browse: `client/screens/browse.py`
- Game details: `client/screens/game_details.py`
- Profile: `client/screens/profile.py`
- Leaderboard: `client/screens/leaderboard.py`
- Search: `client/screens/search.py`
- Match history: `client/screens/history.py`
- Login: `client/screens/login.py`
- Create account: `client/screens/create_account.py`
- Welcome: `client/screens/welcome.py`
- Settings/project notes: `client/screens/settings.py`

What code should go there:

- Screen layout rectangles.
- Calls to reusable components.
- Handling screen-specific button clicks.
- Calling `self.app.backend...` to request data.

What should not go there:

- Final data structures.
- Dataset cleaning.
- Sorting algorithms.
- C++ networking.
- Large mock data lists.

Tip:

- If a drawing pattern is repeated across multiple screens, move it to
  `client/components/`.

## 5. Improve Reusable UI Components

Feature: update shared UI behavior once, then reuse it everywhere.

Why it matters: buttons, rows, panels, and cards should stay consistent.

Files to edit:

- Buttons: `client/components/button.py`
- Panels and badges: `client/components/panel.py`
- Text wrapping: `client/components/text.py`
- Game cards: `client/components/game_card.py`
- List/history rows: `client/components/list_row.py`
- Input boxes: `client/components/input_box.py`
- Navigation bar: `client/components/navbar.py`
- Section headers: `client/components/section.py`
- Fonts: `client/components/fonts.py`

What code should go there:

- Reusable drawing helpers.
- Reusable UI event handling for shared widgets.
- Layout-safe text helpers.

Be careful:

- Do not make a component depend on one specific screen.
- Do not hardcode one game ID inside a reusable card.
- Keep components generic and pass data into them.

## 6. Update Mock Data Carefully

Feature: change temporary records used by the UI prototype.

Why it matters: mock data makes the arcade feel real while the real dataset is
unfinished.

Files to edit:

- Games: `client/data/mock_games.py`
- Players: `client/data/mock_players.py`
- Sessions/history: `client/data/mock_sessions.py`
- Leaderboards: `client/data/mock_leaderboards.py`
- Chat preview records: `client/data/mock_chat.py`
- Platform stats: `client/data/mock_stats.py`
- Game row helper: `client/data/game_factory.py`

What code should go there:

- Temporary sample records only.
- Clear comments when a record is temporary, such as `TEMP TEST GAME`.

Be careful:

- These files are not the final backend.
- Do not implement the professor-required data structures here.
- When the dataset is ready, services should call the real data layer instead
  of directly relying on these mock lists.

## 7. Add Or Replace A Game

Feature: add an uploaded team game under the game folder.

Why it matters: the launcher should call each game through a clean entry point,
not through hardcoded UI logic.

Files to edit:

- Paste the full game folder under top-level `games/game_1/`,
  `games/game_2/`, `games/game_3/`, or `games/game_4/`.
- Keep the runnable file at:
  `games/<game_id>/code/game/main.py`
- Register it in:
  `client/services/game_launch_registry.py`
- Add or update its catalog entry in:
  `client/data/mock_games.py`

Default behavior:

- The launcher runs `code/game/main.py` as a subprocess.
- The working directory is set to that same `code/game/` folder.
- This preserves relative asset paths such as `../../graphics`.

Optional clean adapter inside `code/game/main.py`:

```python
def run_game(player_info=None, session_info=None):
    # Start the game.
    # Return to the arcade when the game exits.
    return {"ok": True, "message": "Returned to Scorpions Arcade."}
```

Be careful:

- The subprocess launcher exists because copied games may call `sys.exit()` or
  `pygame.quit()`.
- Do not rewrite a teammate's game just to fit the arcade. Change the launch
  registry instead.
- If your game has unusual command-line arguments, update only the launch
  registry, not UI screens.
- Keep game-specific code inside that game's folder.
- Keep temporary games, such as `games/game_5`, clearly marked as safe to delete.

## 8. Connect The Play Button Correctly

Feature: make Play launch the selected game through the service layer.

Why it matters: the UI should not know import paths or game folder names.

Files to edit:

- Launch service: `client/services/game_launch_service.py`
- Launch registry: `client/services/game_launch_registry.py`
- Game details UI only if button layout/text changes:
  `client/screens/game_details.py`

What code should go there:

- Importing/adapting/subprocess-launching a game belongs in
  `game_launch_service.py`.
- Mapping catalog game IDs to `games/<folder>/code/game/main.py` belongs in
  `game_launch_registry.py`.
- Button drawing and click handling belongs in `game_details.py`.

Be careful:

- If a game folder or `main.py` is missing, the launcher should report that
  safely.
- The launcher should show a friendly message instead of crashing.
- Future C++ values such as `session_id`, `server_host`, `server_port`, and
  player token should be added to the `session_info` dictionary when the server
  exists.

## 9. Replace Mock Auth Logic

Feature: connect login and account creation to real project logic.

Why it matters: the current login is only a UI prototype.

Files to edit:

- UI screens:
  - `client/screens/login.py`
  - `client/screens/create_account.py`
- Service:
  - `client/services/auth_service.py`
- Future backend hook:
  - `client/integrations/backend_api.py`
  - `client/integrations/cpp_server.py`

What code should go there:

- UI validation and messages stay in the screen files.
- Auth rules and backend calls go in `auth_service.py`.
- Server request/response code goes in `integrations/`.

Be careful:

- Do not put passwords, sockets, or account storage in the screen files.
- Mark unfinished backend work with TODO comments until the team implements it.

## 10. Replace Catalog/Profile/Search/History Logic

Feature: move from mock lists to real structures and queries.

Why it matters: this is where much of the professor-required logic will connect.

Files to edit:

- Catalog:
  - `client/services/catalog_service.py`
  - `client/placeholders/data_structures.py`
- Profile:
  - `client/services/profile_service.py`
- Search:
  - `client/services/search_service.py`
  - `client/placeholders/data_structures.py`
- Match history:
  - `client/services/history_service.py`
  - `client/placeholders/data_structures.py`
- Leaderboards:
  - `client/services/leaderboard_service.py`
  - `client/placeholders/data_structures.py`
  - `client/placeholders/sorting_algorithms.py`

What code should go there:

- Services should expose simple methods like `search_players(...)`,
  `get_sessions(...)`, and `get_leaderboard(...)`.
- Final data structures should live behind those service methods.
- Screens should keep calling the services and should not care which structure
  is used internally.

Be careful:

- Do not make screens sort or filter large datasets directly.
- Keep interfaces stable so UI work and data-structure work can happen in
  parallel.

## 11. Add Custom Data Structures

Feature: implement the professor-required structures.

Why it matters: the UI scaffold does not solve the backend/data-structure
assignment for you. This is team-owned work.

Files to edit:

- `client/placeholders/data_structures.py`
- Service files that will use those structures:
  - `catalog_service.py`
  - `search_service.py`
  - `leaderboard_service.py`
  - `history_service.py`

Likely structure connections:

- Hash table: exact username/game lookup.
- BST: score ranges, rank ranges, sorted catalog traversal.
- Heap / priority queue: top-K scores or popular games.
- Graph: recommendations, friend relationships, matchmaking/lobby links.
- One additional structure: trie for player search, linked list for history, or
  another structure approved by the team/professor.

Be careful:

- Document what each structure does.
- Add timing or comparison counters where needed for analysis.
- Keep final implementation separate from UI drawing.

## 12. Add Sorting Algorithms

Feature: implement and compare required sorting behavior.

Why it matters: sorting may be required for leaderboard, history, or catalog
views and for the final report.

Files to edit:

- `client/placeholders/sorting_algorithms.py`
- `client/services/leaderboard_service.py`
- `client/services/history_service.py`
- `client/services/catalog_service.py`

What code should go there:

- Sorting algorithm implementations go in `sorting_algorithms.py`.
- Services decide when to call sorting.
- Screens only display already-prepared results.

Be careful:

- Do not sort inside `draw()` methods.
- Keep benchmarking code separate enough that it can be explained in the report.

## 13. Add Dataset Ingestion And Cleaning

Feature: generate, commit, load, and clean the required synthetic dataset.

Why it matters: the final project needs realistic data and documented cleaning
rules. The dataset is now a submitted project artifact, not just optional mock
data.

Files to edit:

- Dataset generator: `data/generate_dataset.py`
- Generated dataset folder: `data/synthetic_dataset/`
- Dataset loading hook: `platform_server/data_ingest.py`
- Cleaning hook: `client/placeholders/dataset_cleaning.py`
- Temporary mock files until replaced:
  - `client/data/mock_games.py`
  - `client/data/mock_players.py`
  - `client/data/mock_sessions.py`
  - `client/data/mock_leaderboards.py`

What code should go there:

- Synthetic record generation belongs in `data/generate_dataset.py`.
- Raw JSON loading and required field validation belongs in
  `platform_server/data_ingest.py`.
- Cleaning and normalization rules belong in `dataset_cleaning.py`.
- Services should consume cleaned records or built indexes.

Generate the current required dataset:

```powershell
python data/generate_dataset.py
```

Expected generated files:

- `data/synthetic_dataset/players.json`
- `data/synthetic_dataset/sessions.json`
- `data/synthetic_dataset/chat_messages.json`
- `data/synthetic_dataset/game_catalog.json`
- `data/synthetic_dataset/manifest.json`

Be careful:

- The generated JSON files must be committed and submitted with the project.
- Do not hide cleaning rules inside UI code.
- Document any record you drop or modify.
- Keep messy raw data separate from cleaned records if your final design needs
  both.

## 14. Connect The C++ Server Handoff

Feature: connect Python launcher actions to the future C++ multiplayer server.

Why it matters: the final playable game flow should eventually create or join a
real multiplayer session.

Files to edit:

- C++ hook: `client/integrations/cpp_server.py`
- Launch service: `client/services/game_launch_service.py`
- Auth service if login moves to server:
  `client/services/auth_service.py`
- Game entry files:
  `games/game_1/code/game/main.py`, `games/game_2/code/game/main.py`, etc.

What code should go there:

- Socket/API connection methods go in `cpp_server.py`.
- Session request logic goes in `game_launch_service.py`.
- The selected game runs as a subprocess by default. If it exposes an adapter,
  it can receive session info through `run_game(...)`.

Be careful:

- Do not put socket logic inside `screens/game_details.py`.
- Keep server details in `session_info`, not hardcoded in game files.
- Keep a safe fallback message when the C++ server is not running.

## 15. Connect Chat And Session Features

Feature: make each active game session support recent chat and session data.

Why it matters: the current chat scaffold is client-side and temporary.

Files to edit:

- Chat service: `client/services/chat_service.py`
- Session chat log: `client/services/session_chat.py`
- Circular/bounded buffer scaffold:
  `client/placeholders/chat_buffer.py`
- C++ networking hook:
  `client/integrations/cpp_server.py`
- Chat model:
  `client/models/chat_message.py`

What code should go there:

- UI requests recent messages from `chat_service.py`.
- Bounded recent-message storage stays in `session_chat.py` or
  `chat_buffer.py`.
- Real broadcast/send/receive logic belongs in `cpp_server.py`.

Be careful:

- Keep one chat log per session.
- Validate/sanitize messages before sending them to a server.
- Do not store unlimited chat messages in memory.

## 16. Mark TODOs As Completed

Feature: remove or update TODOs only after the team has implemented the real
logic.

Why it matters: TODOs show what is scaffolded versus final.

Files to check:

- `client/integrations/`
- `client/placeholders/`
- `client/services/game_launch_service.py`
- `docs/work_remaining.md`
- `NEXT_STEPS.md`

What to do:

- When a TODO is completed, update the comment or remove it.
- Update the checklist in `docs/work_remaining.md`.
- Add report notes if the completed work affects complexity analysis or
  performance results.

Be careful:

- Do not mark TODOs complete just because the UI looks finished.
- Backend/data-structure TODOs should be completed by the team as part of the
  assignment work.

## Where To Edit For Common Tasks

- Change the Home screen layout:
  `client/screens/home.py`
- Change the Browse screen or genre filter UI:
  `client/screens/browse.py`
- Change Game Details layout:
  `client/screens/game_details.py`
- Update reusable game cards:
  `client/components/game_card.py`
- Update reusable list rows:
  `client/components/list_row.py`
- Change mock game catalog data:
  `client/data/mock_games.py`
- Change mock players:
  `client/data/mock_players.py`
- Change mock sessions:
  `client/data/mock_sessions.py`
- Connect real game launching:
  `client/services/game_launch_service.py`
- Register a game folder:
  `client/services/game_launch_registry.py`
- Add a real game:
  `games/<game_id>/code/game/main.py`
- Prepare backend/C++ hooks:
  `client/integrations/`
- Prepare custom data structures:
  `client/placeholders/data_structures.py`
- Prepare sorting:
  `client/placeholders/sorting_algorithms.py`
- Prepare dataset cleaning:
  `client/placeholders/dataset_cleaning.py`
- Update team checklist:
  `docs/work_remaining.md`

## Coding Hints

- Keep UI rendering inside `screens/` and `components/`.
- Keep feature logic inside `services/`.
- Keep mock/sample records out of screen files.
- Keep model dataclasses simple and readable.
- Avoid hardcoding game-specific logic inside reusable components.
- Use comments to mark unfinished professor-required logic.
- Use TODO comments for real backend/data-structure work that still belongs to
  the team.
- Test one feature at a time.
- Keep the app runnable from `main.py` after every merge.
- Prefer small, focused changes over huge mixed edits.

## Recommended 4-Person Work Order

### Person 1: UI Foundation And Navigation

Start here:

- `client/core/app.py`
- `client/core/state.py`
- `client/core/router.py`
- `client/components/`

Focus:

- Keep navigation stable.
- Keep shared components consistent.
- Help teammates avoid duplicated UI code.

### Person 2: Catalog, Details, And Game Launching

Start here:

- `client/screens/home.py`
- `client/screens/browse.py`
- `client/screens/game_details.py`
- `client/services/catalog_service.py`
- `client/services/game_launch_service.py`
- top-level `games/`

Focus:

- Polish catalog browsing.
- Add real game folders.
- Keep launch flow modular.

### Person 3: Profile, Leaderboards, Search, And History

Start here:

- `client/screens/profile.py`
- `client/screens/leaderboard.py`
- `client/screens/search.py`
- `client/screens/history.py`
- `client/services/profile_service.py`
- `client/services/leaderboard_service.py`
- `client/services/search_service.py`
- `client/services/history_service.py`

Focus:

- Keep list screens readable.
- Connect screens to service methods.
- Prepare UI for final ranking/search/history logic.

### Person 4: Data, Backend Hooks, And Analysis

Start here:

- `client/integrations/`
- `client/placeholders/`
- `client/data/`
- `docs/work_remaining.md`

Focus:

- Implement dataset ingestion/cleaning.
- Build final custom data structures.
- Add sorting and performance analysis hooks.
- Prepare C++ server handoff.

## Final Checklist

- [ ] App still runs with `python main.py`.
- [ ] All major screens still load.
- [ ] Mock data is clearly separated from final logic.
- [ ] Real game folders live under top-level `games/game_1/` through `games/game_4/`.
- [ ] Connected games follow `games/<game_folder>/code/game/main.py`.
- [ ] Connected games are registered in `game_launch_registry.py`.
- [ ] Placeholder games fail safely with a friendly message.
- [ ] Auth logic is no longer only mock data, or the mock is clearly documented.
- [ ] Dataset ingestion and cleaning are implemented and documented.
- [ ] Required custom data structures are implemented by the team.
- [ ] Sorting algorithms are implemented and benchmarked.
- [ ] Search, leaderboards, history, and catalog queries use the final structures.
- [ ] C++ server handoff is implemented or clearly documented as a final stub.
- [ ] Chat/session behavior is connected or clearly marked as scaffolded.
- [ ] TODOs in code and docs are updated.
- [ ] Compile check passes before merging.
- [ ] Final report explains structure choices, complexity, and performance.
