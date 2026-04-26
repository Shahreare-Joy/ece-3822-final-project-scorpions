from __future__ import annotations

"""Graph with custom adjacency and traversal helpers.

Use cases:
- player-game-genre recommendation graph
- friend/player relationships
- matchmaking/lobby relationships

TODO (DONE)(GRAPH): Implement adjacency structure with custom storage. This
version uses the project hash table for vertex lookup, linked lists for
adjacency, a linked queue for BFS, and a linked stack for DFS.
"""

from dataclasses import dataclass

from .hash_table import ChainedHashTable
from .linked_list import LinkedList
from .linked_queue import LinkedQueue
from .linked_stack import LinkedStack


@dataclass
class Edge:
    # target vertex this edge points to
    target: str

    # edge weight for recommendations or rankings
    weight: float = 1.0


class Graph:
    def __init__(self) -> None:
        # TODO (DONE): initialize custom adjacency storage.

        # hash table maps vertex_id -> LinkedList of outgoing edges
        self._adjacency = ChainedHashTable()

    def add_vertex(self, vertex_id: str) -> None:
        '''add vertex if it does not already exist'''

        # create empty edge list for new vertex
        if not self._adjacency.contains(vertex_id):
            self._adjacency.put(vertex_id, LinkedList())

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        '''add directed edge from source to target'''

        # ensure both vertices exist
        self.add_vertex(source)
        self.add_vertex(target)

        # get source edge linked list
        edges = self._adjacency.get(source)

        # append new edge
        edges.append(Edge(target, weight))

        # save updated edge list
        self._adjacency.put(source, edges)

    def remove_edge(self, source: str, target: str) -> bool:
        '''remove edge from source to target if it exists'''

        # get source edge linked list
        edges = self._adjacency.get(source)

        # no edge list means source does not exist
        if not isinstance(edges, LinkedList):
            return False

        # remove without list comprehension so adjacency stays node-based
        return edges.remove_first_matching(lambda edge: edge.target == target)

    def neighbors(self, vertex_id: str) -> list[Edge]:
        '''return outgoing edges for vertex'''

        # return Python list for compatibility with existing tests/UI callers.
        # Internally the graph still stores neighbors in LinkedList.
        edges = self._adjacency.get(vertex_id)
        if not isinstance(edges, LinkedList):
            return []
        return edges.to_list()

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

        # queue starts with start vertex, implemented as linked nodes
        queue: LinkedQueue[str] = LinkedQueue()
        queue.enqueue(start)
        visited.put(start, True)

        while not queue.is_empty():
            # remove oldest item from queue in O(1)
            vertex = queue.dequeue()
            order.append(vertex)

            # visit unvisited neighbors
            for edge in self.neighbors(vertex):
                if not visited.contains(edge.target):
                    visited.put(edge.target, True)
                    queue.enqueue(edge.target)

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

        # stack starts with start vertex, implemented as linked nodes
        stack: LinkedStack[str] = LinkedStack()
        stack.push(start)

        while not stack.is_empty():
            # remove newest item from stack in O(1)
            vertex = stack.pop()

            # skip already visited vertices
            if visited.contains(vertex):
                continue

            visited.put(vertex, True)
            order.append(vertex)

            # add neighbors in reverse so traversal order is stable
            edges = self._adjacency.get(vertex)
            if not isinstance(edges, LinkedList):
                continue
            for edge in edges.reversed_values():
                if not visited.contains(edge.target):
                    stack.push(edge.target)

        return order
