# Multiplayer Demo Scope

This build intentionally proves only the final-project multiplayer minimum:

- Launch the game with `SCORPIONS_GAME_PORT` / `SCORPIONS_GAME_HOST`.
- Use the `server_json_jitter` style protocol by default.
- Accept `CONNECTED|<id>` before treating the socket as connected.
- Send periodic `UPDATE|id|x|y|name|character_type|status` messages.
- Read `STATE||...` broadcasts and render remote players as lightweight ghost markers.

Chat uses the Python platform server in server mode. Messages are stored by
`session_id`, filtered before storage, and polled by each launched game overlay.
Score recording still starts in the game result file, then the launcher submits
that result to the Python platform server and refreshes local history/profile
state for the returning player.

If the real-time socket cannot connect or the handshake is not received, Fruit
Drop Rush continues as a local/session-based round. The on-screen HUD reports
the fallback reason, and final score/history/leaderboard behavior is unchanged.

Recommended demo layout:

```sh
# Terminal 1: Python platform/data server
python -m platform_server.server --host 0.0.0.0 --port 50068 --serializer json

# Terminal 2: C++ real-time gameplay relay
cd server
./server_json_jitter --port 50069

# Terminal 3+: client(s)
python main.py --server <host> --port 50068 --game-port 50069 --serializer json
```

To rebuild the intended C++ relay on Linux/WSL/ECE if needed:

```sh
cd server
make SERIALIZER=JSON BUFFER=JITTER
./server_json_jitter --port 50069
```

Then launch the arcade/game with `SCORPIONS_GAME_PORT=50069` or pass the same
port through the arcade `--game-port` option. If separate machines are used,
clients must use the host machine's LAN/server IP, not `localhost`.
