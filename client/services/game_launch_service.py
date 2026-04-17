"""Client game launch service.

TODO(GAME LAUNCH): Call the Python platform server for account/session metadata,
then pass C++ session connection info into games/<game>/main.py::run_game(...).
"""

from importlib import import_module


class ClientGameLaunchService:
    def launch(self, module_path: str, player: object) -> object:
        module = import_module(module_path)
        run_game = getattr(module, "run_game", None)
        if not callable(run_game):
            raise RuntimeError(f"{module_path} does not expose run_game(player).")
        return run_game(player)
