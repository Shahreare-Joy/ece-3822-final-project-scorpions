"""Package entry point for Scorpions Arcade.

The repository-level main.py imports this file so the launcher still starts with
`python main.py`, while the app logic stays inside the package.
"""

from scorpions_arcade.core.app import ArcadeApp, main

__all__ = ["ArcadeApp", "main"]
