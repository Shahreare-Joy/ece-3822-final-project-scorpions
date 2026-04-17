from __future__ import annotations

"""Client entry point.

The polished launcher currently lives in `scorpions_arcade/`. This wrapper keeps
the new required project structure while preserving the working UI.

TODO(CLIENT REFACTOR): Gradually migrate reusable client code from
`scorpions_arcade/` into this `client/` package if the team wants the final
submission to use only the new top-level layout.
"""

from scorpions_arcade.main import main as run_existing_launcher


def main() -> None:
    """Run the Pygame arcade launcher."""
    run_existing_launcher()


if __name__ == "__main__":
    main()
