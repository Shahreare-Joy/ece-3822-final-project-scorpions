from __future__ import annotations

from typing import TYPE_CHECKING

from client.screens import (
    BaseScreen,
    BrowseScreen,
    CreateAccountScreen,
    GameDetailsScreen,
    HistoryScreen,
    HomeScreen,
    LeaderboardScreen,
    LoginScreen,
    ProfileScreen,
    SearchPlayersScreen,
    SettingsScreen,
    WelcomeScreen,
)

from .router import ScreenName

if TYPE_CHECKING:
    from .app import ArcadeApp


def create_screens(app: ArcadeApp) -> dict[ScreenName, BaseScreen]:
    """Create all screen instances in one routing-focused place."""
    return {
        ScreenName.WELCOME: WelcomeScreen(app),
        ScreenName.LOGIN: LoginScreen(app),
        ScreenName.CREATE_ACCOUNT: CreateAccountScreen(app),
        ScreenName.HOME: HomeScreen(app),
        ScreenName.BROWSE: BrowseScreen(app),
        ScreenName.GAME_DETAILS: GameDetailsScreen(app),
        ScreenName.PROFILE: ProfileScreen(app),
        ScreenName.LEADERBOARD: LeaderboardScreen(app),
        ScreenName.HISTORY: HistoryScreen(app),
        ScreenName.SEARCH: SearchPlayersScreen(app),
        ScreenName.SETTINGS: SettingsScreen(app),
    }

