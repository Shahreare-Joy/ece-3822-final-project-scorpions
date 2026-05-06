# Project Structure

```text
ece-3822-final-project-scorpions/
├── main.py                         # Top-level entry point; starts the Python/Pygame arcade client
├── README.md                       # Short project overview
│
├── client/                         # Pygame arcade UI and client-side application logic
│   ├── main.py                     # Client package entry point used by root main.py
│   ├── runtime_config.py           # Runtime mode, host, port, and serializer configuration
│   ├── core/                       # Main app loop, routing, layout, state, and theme
│   │   ├── app.py                  # ArcadeApp; owns startup, navigation, and event loop
│   │   ├── router.py               # Screen routing helpers
│   │   ├── screen_registry.py      # Registers all UI screens
│   │   └── state.py                # Current player, current screen, messages, and app state
│   ├── screens/                    # One Pygame screen per major UI page
│   │   ├── welcome.py              # Welcome/start screen
│   │   ├── login.py                # Login UI
│   │   ├── create_account.py       # Account creation UI
│   │   ├── home.py                 # Home dashboard
│   │   ├── browse.py               # Game browsing/catalog screen
│   │   ├── game_details.py         # Play/launch button and selected game details
│   │   ├── leaderboard.py          # Leaderboard UI
│   │   ├── history.py              # Match/session history UI
│   │   ├── search.py               # Player/game search UI
│   │   ├── profile.py              # Player profile UI
│   │   ├── session_chat.py         # Session chat screen
│   │   └── settings.py             # Settings/status screen
│   ├── services/                   # Client-facing feature services
│   │   ├── arcade_backend.py       # Facade connecting UI screens to services and integrations
│   │   ├── auth_service.py         # Login/account behavior
│   │   ├── account_store.py        # Demo account persistence
│   │   ├── catalog_service.py      # Game catalog access
│   │   ├── game_launch_registry.py # Maps catalog game IDs to games/game_N launch paths
│   │   ├── game_launch_service.py  # Launches playable games as subprocesses/adapters
│   │   ├── leaderboard_service.py  # Leaderboard queries and ranking display data
│   │   ├── history_service.py      # Session history filtering/access
│   │   ├── chat_service.py         # Platform/session chat service
│   │   ├── session_chat.py         # Session-scoped chat wrapper
│   │   └── session_result_service.py # Sends completed game results into the platform result flow
│   ├── integrations/               # External/server connection adapters
│   │   ├── cpp_server.py           # C++ gameplay server connection info and availability checks
│   │   ├── server_connection.py    # TCP connection helper for platform/server mode
│   │   ├── backend_api.py          # Placeholder backend API hook
│   │   └── dataset.py              # Dataset integration hook
│   ├── components/                 # Reusable Pygame drawing/widgets
│   │   ├── chat_overlay.py         # In-game chat overlay used by launched games
│   │   ├── button.py               # Button widget
│   │   ├── navbar.py               # Top navigation bar
│   │   ├── game_card.py            # Catalog game card
│   │   ├── list_row.py             # Leaderboard/history/search rows
│   │   ├── input_box.py            # Text input widget
│   │   └── text.py                 # Text wrapping/trimming helpers
│   ├── models/                     # Dataclasses/models for games, players, sessions, chat, results
│   ├── data/                       # Mock UI data used by the client facade
│   └── assets/                     # Client images, thumbnails, screenshots, and UI assets
│
├── platform_server/                # Python platform backend logic: accounts, data, chat, scores
│   ├── server.py                   # Platform server entry/facade
│   ├── accounts.py                 # Account creation/login backend logic
│   ├── catalog.py                  # Game catalog backend logic
│   ├── leaderboard.py              # Leaderboard storage/query logic
│   ├── history.py                  # Match/session history backend logic
│   ├── chat.py                     # Platform/session chat backend logic
│   ├── moderation.py               # Chat/message moderation helpers
│   ├── session_manager.py          # Matchmaking/session lifecycle manager
│   ├── session_results.py          # Completed score/result processing
│   ├── data_ingest.py              # Dataset loading/ingestion helpers
│   ├── persistence.py              # Persistence helpers for backend data
│   ├── search.py                   # Search backend logic
│   └── game_registry.py            # Backend game registration metadata
│
├── datastructures/                 # Project data structure implementations
│   ├── hash_table.py               # Hash table implementation
│   ├── bst.py                      # Binary search tree implementation
│   ├── heap.py                     # Heap/priority structure implementation
│   ├── graph.py                    # Graph implementation
│   ├── circular_buffer.py          # Circular buffer used by buffering/chat-style flows
│   ├── session_history.py          # Session history structure helpers
│   ├── linked_list.py              # Linked list implementation
│   ├── linked_queue.py             # Queue built with linked nodes
│   ├── linked_stack.py             # Stack built with linked nodes
│   └── array.py                    # Array helper structure
│       # Note: no bloom_filter.py exists in the current project tree.
│       # Sparse matrix lives inside individual game folders, not top-level datastructures/.
│
├── games/                          # Playable game folders launched by the arcade
│   ├── game_1/                     # Fruit Drop Rush / Scorpions Arena game folder
│   │   ├── code/game/main.py       # Required launch path for this game
│   │   └── graphics/               # Game art/assets
│   ├── game_2/                     # Team game folder with same launch convention
│   │   ├── code/game/main.py       # Required launch path
│   │   └── graphics/               # Game art/assets
│   ├── game_3/                     # Team game folder with same launch convention
│   │   ├── code/game/main.py       # Required launch path
│   │   └── graphics/               # Game art/assets
│   ├── game_4/                     # Team game folder with dialog/NPC additions
│   │   ├── code/game/main.py       # Required launch path
│   │   └── graphics/               # Game art/assets
│
├── server/                         # Active C++ real-time gameplay server
│   ├── Makefile                    # Builds serializer/buffer variants
│   ├── server_json_jitter          # JSON + jitter-buffer executable used for multiplayer demo
│   ├── server_text_jitter          # Text + jitter-buffer executable
│   ├── server_text_smoother        # Text + position-smoother executable
│   ├── src/server.cpp              # C++ socket server; accepts clients and broadcasts state
│   ├── src/json_serializer.cpp     # JSON player serialization
│   ├── src/text_serializer.cpp     # Text player serialization
│   ├── src/player.cpp              # C++ player state
│   ├── include/player.h            # C++ player interface
│   ├── include/jitter_buffer.h     # Jitter buffer for network smoothing
│   └── MAKEFILEGUIDE.md            # Build/run instructions for server variants
│
├── data/                           # Runtime/demo data files
│   ├── demo_accounts.json          # Stored demo accounts
│   ├── generate_dataset.py         # Dataset generation script
│   └── README.md                   # Data folder notes
│
├── tests/                          # Python unit/integration tests
│   ├── test_account_store.py       # Account storage tests
│   ├── test_bst.py                 # BST tests
│   ├── test_hash_table.py          # Hash table tests
│   ├── test_heap.py                # Heap tests
│   ├── test_graph_circular_buffer.py # Graph and circular buffer tests
│   ├── test_leaderboard.py         # Leaderboard tests
│   ├── test_chat_service.py        # Chat service tests
│   ├── test_connection_config.py   # Server/game port configuration tests
│   ├── test_game_network_client.py # Two-client gameplay protocol proof test
│   ├── test_session_manager.py     # Match/session manager tests
│   └── test_search.py              # Search tests
│
├── docs/                           # Project documentation for report, README, and presentation
│   ├── project_structure.md        # This structure overview
│   ├── multiplayer_demo.md         # Minimal multiplayer protocol and fallback notes
│   ├── CLASS_DEMO_ACCOUNTS.md      # Contains username and password for class
│   ├── API_DOCUMENTATION.md        # Platform API/message documentation
│   └── DATASET.md        
|
├── algorithms/                     # Sorting/search algorithm implementations
├── benchmarks/                     # Benchmark scripts for performance analysis
├── tools/                          # Utility scripts
└── cpp_server/                     # Older/placeholder C++ scaffolding; active gameplay server is server/
```

## Architecture Summary

The `client/` folder is the Pygame arcade application: it handles screens, navigation, launch buttons, chat overlay UI, and local client state.
The `platform_server/` folder contains Python backend logic for accounts, catalog data, chat, matchmaking/session management, leaderboards, history, and score result processing.
The `games/` folder stores each playable game; the arcade launches games through `games/game_N/code/game/main.py` using `client/services/game_launch_service.py`.
The active C++ real-time gameplay server is in `server/`, especially `server_json_jitter`, which accepts socket clients and broadcasts player state.
Gameplay clients connect through `SCORPIONS_GAME_HOST` and `SCORPIONS_GAME_PORT`, usually one of the approved ports such as `50068`.
The Python platform connection and the C++ gameplay connection are configured separately so score/history/leaderboard systems do not depend on real-time gameplay success.
If real-time gameplay is unavailable, the game can continue as a session-based/local round while still preserving chat, score reporting, history, and leaderboard flow.
