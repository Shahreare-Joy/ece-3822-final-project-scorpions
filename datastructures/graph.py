from __future__ import annotations

"""Graph scaffold with working adjacency behavior.

Use cases:
- player-game-genre recommendation graph
- friend/player relationships
- matchmaking/lobby relationships

TODO (DONE)(GRAPH): Implement adjacency structure with custom storage. This
version uses the project hash table for vertex lookup. Neighbor lists are kept
small and readable for the scaffold; the team can replace them with custom
linked lists if graph analysis becomes a core graded feature.
"""

from dataclasses import dataclass

from .hash_table import ChainedHashTable


@dataclass
class Edge:
    # target vertex this edge points to
    target: str

    # edge weight for recommendations or rankings
    weight: float = 1.0


class Graph:
    def __init__(self) -> None:
        # TODO (DONE): initialize custom adjacency storage.

        # hash table maps vertex_id -> list of outgoing edges
        self._adjacency = ChainedHashTable()

    def add_vertex(self, vertex_id: str) -> None:
        '''add vertex if it does not already exist'''

        # create empty edge list for new vertex
        if not self._adjacency.contains(vertex_id):
            self._adjacency.put(vertex_id, [])

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        '''add directed edge from source to target'''

        # ensure both vertices exist
        self.add_vertex(source)
        self.add_vertex(target)

        # get source edge list
        edges = self._adjacency.get(source, [])

        # append new edge
        edges.append(Edge(target, weight))

        # save updated edge list
        self._adjacency.put(source, edges)

    def remove_edge(self, source: str, target: str) -> bool:
        '''remove edge from source to target if it exists'''

        # get source edge list
        edges = self._adjacency.get(source)

        # no edge list means source does not exist
        if not isinstance(edges, list):
            return False

        # keep all edges except target
        new_edges = [edge for edge in edges if edge.target != target]

        # return false if no edge was removed
        if len(new_edges) == len(edges):
            return False

        # save updated edges
        self._adjacency.put(source, new_edges)
        return True

    def neighbors(self, vertex_id: str) -> list[Edge]:
        '''return outgoing edges for vertex'''

        # return copy of neighbor list
        return list(self._adjacency.get(vertex_id, []))

    def bfs(self, start: str) -> list[str]:
        '''run breadth-first search from start vertex'''
        """Breadth-first traversal from start."""

        # return empty if start does not exist
        if not self._adjacency.contains(start):
            return []

        # track visited vertices
        visited = ChainedHashTable()

        # store traversal order
        order: list[str] = []

        # queue starts with start vertex
        queue: list[str] = [start]
        visited.put(start, True)

        while queue:
            # remove oldest item from queue
            vertex = queue.pop(0)
            order.append(vertex)

            # visit unvisited neighbors
            for edge in self.neighbors(vertex):
                if not visited.contains(edge.target):
                    visited.put(edge.target, True)
                    queue.append(edge.target)

        return order

    def dfs(self, start: str) -> list[str]:
        '''run depth-first search from start vertex'''
        """Depth-first traversal from start."""

        # return empty if start does not exist
        if not self._adjacency.contains(start):
            return []

        # track visited vertices
        visited = ChainedHashTable()

        # store traversal order
        order: list[str] = []

        # stack starts with start vertex
        stack: list[str] = [start]

        while stack:
            # remove newest item from stack
            vertex = stack.pop()

            # skip already visited vertices
            if visited.contains(vertex):
                continue

            visited.put(vertex, True)
            order.append(vertex)

            # add neighbors in reverse so traversal order is stable
            for edge in reversed(self.neighbors(vertex)):
                if not visited.contains(edge.target):
                    stack.append(edge.target)

        return order