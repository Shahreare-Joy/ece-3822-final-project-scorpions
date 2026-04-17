# Scorpions Arcade Implementation Guide

Follow this order so the team can work in parallel without mixing
responsibilities.

## 1. Confirm The App Runs

```powershell
python main.py
```

If this breaks, fix the client entry path before adding backend logic.

## 2. Implement Core Data Structures

Files:

- `datastructures/array.py`
- `datastructures/hash_table.py`
- `datastructures/bst.py`
- `datastructures/heap.py`
- `datastructures/graph.py`
- `datastructures/circular_buffer.py`

What to implement:

- custom storage
- insert/search/delete operations
- range queries where needed
- clear Big-O comments

Be careful:

- Do not use Python dict/list/set as the core final implementation unless your
  professor explicitly allows it.
- Add tests as each structure is implemented.

## 3. Implement Algorithms

Files:

- `algorithms/mergesort.py`
- `algorithms/heapsort.py`
- `algorithms/search_algorithms.py`

What to implement:

- at least two sorting algorithms
- brute-force baseline search for comparison
- optimized prefix/search wrapper for final structures

Use these algorithms from platform services, not from Pygame screens.

## 4. Build The Dataset Pipeline

Files:

- `data/synthetic_dataset/`
- `platform_server/server.py`
- existing docs in `docs/`

What to do:

- create 10,000+ player records
- create 100,000+ session records
- create catalog, leaderboard, and chat rows
- document any cleaning rules

## 5. Implement Platform Services

Files:

- `platform_server/accounts.py`
- `platform_server/search.py`
- `platform_server/leaderboard.py`
- `platform_server/history.py`
- `platform_server/chat.py`
- `platform_server/catalog.py`

What to connect:

- accounts -> hash table
- player/game search -> BST/Trie/hash table
- leaderboards -> heap and range-query tree
- history -> player/game/date/outcome indexes
- chat -> circular buffer
- catalog -> hash table, indexes, graph/recommendations

## 6. Add The Four Games

Files:

- `games/game_1/main.py`
- `games/game_2/main.py`
- `games/game_3/main.py`
- `games/game_4/main.py`

Requirements:

- keep `run_game(player)` as the public entry point
- keep game-specific code inside each game folder
- connect multiplayer/session data later through the client launch service and
  C++ server

## 7. Connect The Client To Platform Services

Files:

- `client/services/auth_service.py`
- `client/services/search_service.py`
- `client/services/leaderboard_service.py`
- `client/services/history_service.py`
- `client/services/game_launch_service.py`

Goal:

- the client asks services for data
- services call the platform server
- platform server calls custom structures
- screens only draw results

## 8. Implement C++ Server Handoff

Files:

- `cpp_server/main.cpp`
- `cpp_server/game_instance_manager/`
- `cpp_server/chat_relay/`

What to define:

- session_id
- server_host/server_port
- player token
- chat broadcast
- live score updates

## 9. Add Tests And Stress Tests

Files:

- `tests/test_hash_table.py`
- `tests/test_bst.py`
- `tests/test_leaderboard.py`
- `tests/test_search.py`
- `tests/test_load.py`

What to test:

- correctness of each structure
- search results
- leaderboard ranking
- history filters
- load tests with final dataset sizes

## 10. Benchmark And Write Analysis

Compare:

- brute-force player search vs final search structure
- brute-force session filtering vs indexed history
- full leaderboard sorting vs heap/range-query approach
- sorting algorithm A vs sorting algorithm B

Record:

- input size
- runtime
- comparison count if relevant
- Big-O explanation
- screenshots or tables for the final report

## Team Ownership Suggestion

- Person 1: `client/` UI and game launch flow
- Person 2: `platform_server/` search/catalog/history services
- Person 3: `datastructures/` and `algorithms/`
- Person 4: `games/`, `cpp_server/`, tests, and integration

## Final Checklist

- [ ] `python main.py` runs the arcade.
- [ ] Four games exist under `games/`.
- [ ] One game is playable.
- [ ] Accounts use a custom hash table.
- [ ] Player/game search uses custom structures.
- [ ] Leaderboards use heap/range-query logic.
- [ ] Match history supports player/game/date/outcome filters.
- [ ] Chat uses bounded circular buffers.
- [ ] Dataset includes required scale.
- [ ] Tests and stress tests run.
- [ ] Sorting/search benchmarks are documented.
