from __future__ import annotations

"""Graph skeleton.

Use cases:
- player-game-genre recommendation graph
- friend/player relationships
- matchmaking/lobby relationships

TODO(GRAPH): Implement adjacency structure with custom storage. Do not use
plain dict-of-lists as the final assignment solution unless approved.
"""


class Graph:
    def __init__(self) -> None:
        # TODO: initialize custom adjacency storage.
        raise NotImplementedError("Team must implement graph.")

    def add_vertex(self, vertex_id: str) -> None:
        _ = vertex_id
        raise NotImplementedError

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        _ = (source, target, weight)
        raise NotImplementedError

    def neighbors(self, vertex_id: str) -> list[object]:
        _ = vertex_id
        raise NotImplementedError
