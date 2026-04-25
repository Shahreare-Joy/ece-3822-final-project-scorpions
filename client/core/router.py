from __future__ import annotations

from enum import Enum


class ScreenName(str, Enum):
    WELCOME = "welcome"
    LOGIN = "login"
    CREATE_ACCOUNT = "create_account"
    HOME = "home"
    BROWSE = "browse"
    GAME_DETAILS = "game_details"
    SESSION_CHAT = "session_chat"
    PROFILE = "profile"
    LEADERBOARD = "leaderboard"
    HISTORY = "history"
    SEARCH = "search"
    SETTINGS = "settings"
