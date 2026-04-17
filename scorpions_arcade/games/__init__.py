"""Team game packages live here.

Each connected game should expose a run_game(player_info=None, session_info=None)
function from its own folder. The arcade launcher imports that function through
scorpions_arcade.services.game_launch_service, not from UI screen code.
"""

