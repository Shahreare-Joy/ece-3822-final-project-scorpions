from __future__ import annotations

import pygame

from client.components import Button, GameCard, InputBox, draw_panel, draw_text
from client.core import Palette
from client.models import ALL_GENRES

from .base_screen import BaseScreen


class BrowseScreen(BaseScreen):
    def __init__(self, app) -> None:
        # initialize base screen
        super().__init__(app)

        # default genre filter
        self.selected_genre = "All"

    def enter(self) -> None:
        '''prepare browse screen controls and game cards'''

        super().enter()

        # keep old search text when refreshing screen
        old_query = getattr(self, "query_box", None).text if hasattr(self, "query_box") else ""

        # create search input box
        self.query_box = InputBox((866, 230, 184, 32), "Search games", self.app.fonts.small)
        self.query_box.text = old_query
        self.inputs = [self.query_box]

        # TODO (DONE)(CATALOG INDEX): Genre counts are collected through backend catalog data.

        # build genre filter buttons
        genres = ["All"] + ALL_GENRES
        all_games = self.app.backend.get_games()

        # count all games and games per genre
        self.genre_counts = {"All": len(all_games)}
        for genre in ALL_GENRES:
            self.genre_counts[genre] = len([game for game in all_games if game.genre == genre])

        for index, genre in enumerate(genres):
            # place buttons in grid
            row = index // 6
            col = index % 6

            # show genre name with count
            label = f"{genre} ({self.genre_counts[genre]})"

            self.buttons.append(
                Button(
                    (44 + col * 126, 208 + row * 30, 118, 28),
                    label,
                    lambda value=genre: self.set_genre(value),
                    self.app.fonts.small,
                    selected=self.selected_genre == genre
                )
            )

        # add search button
        self.buttons.append(
            Button(
                (1060, 230, 92, 32),
                "Search",
                self.run_search,
                self.app.fonts.small,
                bg=Palette.ACCENT,
                hover=Palette.ACCENT_HOVER
            )
        )

        # create game cards from visible games
        rows = self.app.backend.get_home_rows(self.app.current_player)
        has_history = self.app.backend.has_player_history(self.app.current_player)
        self.personalized_rows = [
            ("Recently Played" if has_history else "Popular Right Now", rows.recently_played, 302),
            ("Recommended For You" if has_history else "Top Rated / Popular Games", rows.recommended, 410),
        ]
        for _, row_games, y in self.personalized_rows:
            for index, game in enumerate(row_games[:5]):
                self.cards.append(
                    GameCard(
                        (30 + index * 230, y, 218, 78),
                        game,
                        self.app.open_game,
                        self.app.fonts,
                        compact=True,
                    )
                )

        games = self.visible_games()
        for index, game in enumerate(games[:5]):
            row = index // 5
            col = index % 5
            self.cards.append(
                GameCard(
                    (30 + col * 230, 532 + row * 126, 218, 112),
                    game,
                    self.app.open_game,
                    self.app.fonts
                )
            )

    def visible_games(self) -> list:
        '''return games matching search and genre filter'''

        # get current search query
        query = self.query_box.text.strip()

        # search backend if query exists, otherwise load all games
        games = (
            self.app.backend.search_games(query, limit=len(self.app.backend.get_games()))
            if query
            else self.app.backend.get_games()
        )

        # apply genre filter
        if self.selected_genre != "All":
            games = [game for game in games if game.genre == self.selected_genre]

        return games

    def set_genre(self, genre: str) -> None:
        '''change selected genre and refresh browse screen'''

        # update selected genre
        self.selected_genre = genre

        # rebuild screen
        self.enter()

        # show feedback message
        self.app.show_message(
            f"Showing {genre} games." if genre != "All" else "Showing the full arcade catalog.",
            Palette.MUTED
        )

    def run_search(self) -> None:
        '''run search using current query text'''

        # rebuild cards based on query
        self.enter()

        # show search status message
        query = self.query_box.text.strip()
        message = f"Search results for '{query}'." if query else "Showing the full arcade catalog."
        self.app.show_message(message, Palette.MUTED)

    def handle_event(self, event: pygame.event.Event) -> None:
        '''handle browse screen events'''

        # let base screen process events first
        super().handle_event(event)

        # handle search box input
        result = self.query_box.handle_event(event)

        # run search when enter is pressed
        if result == "enter":
            self.run_search()

    def draw(self) -> None:
        '''draw browse page UI'''

        # draw page title and subtitle
        self.page_title("Browse Games", "Filter by genre, search the arcade catalog, and open a full detail page.")

        # draw genre filter panel
        filter_panel = pygame.Rect(30, 152, 792, 116)
        draw_panel(self.app.screen, filter_panel, Palette.PANEL_DARK, Palette.BORDER, radius=8, width=1)
        draw_text(self.app.screen, "Genre Filters", self.app.fonts.body, Palette.TEXT, filter_panel.x + 14, filter_panel.y + 12)
        draw_text(self.app.screen, f"Selected: {self.selected_genre}", self.app.fonts.small, Palette.ACCENT, filter_panel.x + 14, filter_panel.y + 36)

        # count visible games
        count = len(self.visible_games())

        # draw catalog summary panel
        summary = pygame.Rect(850, 152, 320, 116)
        draw_panel(self.app.screen, summary, Palette.PANEL_DARK, Palette.BORDER, radius=8, width=1)
        draw_text(self.app.screen, "Catalog Snapshot", self.app.fonts.body, Palette.TEXT, summary.x + 16, summary.y + 12)
        draw_text(self.app.screen, f"{count} matching games", self.app.fonts.small, Palette.ACCENT, summary.x + 16, summary.y + 36)
        draw_text(self.app.screen, f"{len(self.app.backend.get_games())} total catalog entries", self.app.fonts.tiny, Palette.MUTED, summary.x + 16, summary.y + 54)

        # draw search input
        self.query_box.draw(self.app.screen)

        # draw filter/search buttons
        for button in self.buttons:
            button.draw(self.app.screen)

        # draw personalized rows from indexed history/recommendation services
        for title, _, y in self.personalized_rows:
            draw_text(self.app.screen, title, self.app.fonts.body, Palette.TEXT, 30, y - 25)

        # draw game cards section
        draw_text(self.app.screen, "Games", self.app.fonts.body, Palette.TEXT, 30, 502)
        for card in self.cards:
            card.draw(self.app.screen)

        # draw screen message if active
        self.draw_message()
