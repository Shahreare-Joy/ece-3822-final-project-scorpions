"""Client package entry point for Scorpions Arcade.

The repository-level main.py imports this file, so the launcher still starts
with `python main.py`. The active Pygame UI now lives in this `client/` package:

- `client/core/` owns the app loop, routing, state, layout, and theme.
- `client/screens/` owns one screen per file.
- `client/components/` owns reusable drawing/widgets.
- `client/services/` owns UI-facing feature adapters and launcher hooks.
- `client/data/` owns temporary UI mock data until platform_server is wired in.
"""

from client.core.app import ArcadeApp, main

__all__ = ["ArcadeApp", "main"]
