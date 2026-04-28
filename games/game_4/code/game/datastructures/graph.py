"""
graph.py - Graph data structure

Author: Kevin Le
Date:   2026-04-24
Lab:    Lab 7 - NPC Dialog with Graphs

Implement an adjacency-list graph that can be directed or undirected.

Each edge stores:
    (neighbor_id, weight, edge_data)

where weight defaults to 1 and edge_data is an arbitrary payload (used by
the dialog system to store the player's choice text on each edge).

Rule: you may NOT use Python's built-in dict or set inside this class.
Use your HashTable from Lab 6 as the adjacency map:

    from datastructures.hash_table import HashTable
"""

from datastructures.hash_table import HashTable


class Graph:
    """
    Adjacency-list graph.

    Nodes are identified by a hashable node_id (int, str, etc.).
    Edges carry an optional weight (default 1) and arbitrary edge_data.

    Parameters
    ----------
    directed : bool
        True  -> each add_edge call creates one directed edge.
        False -> each add_edge call creates edges in both directions (default).
    """

    def __init__(self, directed=False):
        """
        Initialize an empty graph.

        Time complexity: O(1)
        """
        # O(1)
        self.directed = directed
        self._adj = HashTable()
        self._data = HashTable()

    def _remove_from_neighbor_list(self, edges, to_id):
        """Remove one matching outgoing edge from a neighbor list."""
        for index, (neighbor_id, _, _) in enumerate(edges):
            if neighbor_id == to_id:
                edges.pop(index)
                return True
        return False

    def add_node(self, node_id, data=None):
        """
        Add a node with an optional data payload.

        If the node already exists, update its data without changing edges.

        Time complexity: O(1) average

        Args:
            node_id : Hashable identifier.
            data    : Arbitrary payload (default None).
        """
        # O(1) average
        if node_id not in self._adj:
            self._adj[node_id] = []
        self._data[node_id] = data

    def add_edge(self, from_id, to_id, weight=1, edge_data=None):
        """
        Add an edge from from_id to to_id.

        Creates either node automatically if it does not yet exist.
        For undirected graphs, also adds the reverse edge.

        Time complexity: O(1) average

        Args:
            from_id  : Source node.
            to_id    : Destination node.
            weight   : Numeric edge weight (default 1).
            edge_data: Arbitrary payload stored on this edge (default None).
        """
        # O(1) average
        if not self.has_node(from_id):
            self.add_node(from_id)
        if not self.has_node(to_id):
            self.add_node(to_id)

        self._adj[from_id].append((to_id, weight, edge_data))
        if not self.directed:
            self._adj[to_id].append((from_id, weight, edge_data))

    def remove_node(self, node_id):
        """
        Remove a node and all edges that touch it.

        Time complexity: O(V + E)

        Args:
            node_id: Node to remove.

        Raises:
            KeyError: If node_id does not exist.
        """
        # O(V + E)
        if not self.has_node(node_id):
            raise KeyError(node_id)

        for current_node in self.nodes():
            if current_node == node_id:
                continue
            filtered = []
            for neighbor_id, weight, edge_data in self._adj[current_node]:
                if neighbor_id != node_id:
                    filtered.append((neighbor_id, weight, edge_data))
            self._adj[current_node] = filtered

        del self._adj[node_id]
        del self._data[node_id]

    def remove_edge(self, from_id, to_id):
        """
        Remove the edge from from_id to to_id.

        For undirected graphs, also removes the reverse edge.

        Time complexity: O(degree(from_id))

        Args:
            from_id: Source node.
            to_id  : Destination node.

        Raises:
            KeyError: If either node does not exist or the edge is absent.
        """
        # O(degree(from_id))
        if not self.has_node(from_id) or not self.has_node(to_id):
            raise KeyError("One or both nodes do not exist")

        removed = self._remove_from_neighbor_list(self._adj[from_id], to_id)
        if not removed:
            raise KeyError(f"Edge {from_id!r} -> {to_id!r} does not exist")

        if not self.directed:
            reverse_removed = self._remove_from_neighbor_list(self._adj[to_id], from_id)
            if not reverse_removed:
                raise KeyError(f"Reverse edge {to_id!r} -> {from_id!r} does not exist")

    def get_neighbors(self, node_id):
        """
        Return all edges leaving node_id.

        Time complexity: O(1)

        Args:
            node_id: The node to query.

        Returns:
            list of (neighbor_id, weight, edge_data) tuples.
            Returns [] if the node has no outgoing edges.

        Raises:
            KeyError: If node_id does not exist.
        """
        # O(1)
        if not self.has_node(node_id):
            raise KeyError(node_id)
        return list(self._adj[node_id])

    def has_node(self, node_id):
        """
        Return True if node_id is in the graph.

        Time complexity: O(1) average
        """
        # O(1) average
        return node_id in self._adj

    def has_edge(self, from_id, to_id):
        """
        Return True if an edge from_id -> to_id exists.

        Time complexity: O(degree(from_id))
        """
        # O(degree(from_id))
        if not self.has_node(from_id):
            return False
        for neighbor_id, _, _ in self._adj[from_id]:
            if neighbor_id == to_id:
                return True
        return False

    def get_node_data(self, node_id):
        """
        Return the data payload stored at node_id, or None if none.

        Time complexity: O(1) average

        Raises:
            KeyError: If node_id does not exist.
        """
        # O(1) average
        if not self.has_node(node_id):
            raise KeyError(node_id)
        return self._data[node_id]

    def nodes(self):
        """
        Return a list of all node IDs.

        Time complexity: O(V)
        """
        # O(V)
        return self._adj.keys()

    def bfs(self, start_id):
        """
        Breadth-first traversal from start_id.

        Visits only nodes reachable from start_id.
        Time complexity: O(V + E)

        Args:
            start_id: Node to start from.

        Returns:
            list of node_ids in BFS discovery order.

        Raises:
            KeyError: If start_id does not exist.
        """
        # O(V + E)
        if not self.has_node(start_id):
            raise KeyError(start_id)

        order = []
        visited = HashTable()
        queue = [start_id]
        queue_index = 0
        visited[start_id] = True

        while queue_index < len(queue):
            current = queue[queue_index]
            queue_index += 1
            order.append(current)

            for neighbor_id, _, _ in self._adj[current]:
                if neighbor_id not in visited:
                    visited[neighbor_id] = True
                    queue.append(neighbor_id)

        return order

    def dfs(self, start_id):
        """
        Depth-first traversal from start_id (iterative).

        Visits only nodes reachable from start_id.
        Time complexity: O(V + E)

        Args:
            start_id: Node to start from.

        Returns:
            list of node_ids in DFS discovery order.

        Raises:
            KeyError: If start_id does not exist.
        """
        # O(V + E)
        if not self.has_node(start_id):
            raise KeyError(start_id)

        order = []
        visited = HashTable()
        stack = [start_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited[current] = True
            order.append(current)

            neighbors = self._adj[current]
            for index in range(len(neighbors) - 1, -1, -1):
                neighbor_id, _, _ = neighbors[index]
                if neighbor_id not in visited:
                    stack.append(neighbor_id)

        return order

    def shortest_path(self, start_id, end_id):
        """
        Find the path with the fewest edges between two nodes (BFS-based).

        Time complexity: O(V + E)

        Args:
            start_id: Starting node.
            end_id  : Destination node.

        Returns:
            list of node_ids from start_id to end_id inclusive,
            or [] if no path exists.

        Raises:
            KeyError: If either node does not exist.
        """
        # O(V + E)
        if not self.has_node(start_id) or not self.has_node(end_id):
            raise KeyError("One or both nodes do not exist")
        if start_id == end_id:
            return [start_id]

        queue = [start_id]
        queue_index = 0
        visited = HashTable()
        parent = HashTable()
        visited[start_id] = True
        parent[start_id] = None

        while queue_index < len(queue):
            current = queue[queue_index]
            queue_index += 1

            for neighbor_id, _, _ in self._adj[current]:
                if neighbor_id in visited:
                    continue
                visited[neighbor_id] = True
                parent[neighbor_id] = current

                if neighbor_id == end_id:
                    path = [end_id]
                    step = end_id
                    while parent[step] is not None:
                        step = parent[step]
                        path.append(step)
                    path.reverse()
                    return path

                queue.append(neighbor_id)

        return []

    def __len__(self):
        """Return the number of nodes.  Time: O(1)."""
        # O(1)
        return len(self._adj)

    def __str__(self):
        """Return a human-readable summary of the graph."""
        # O(V + E)
        return (
            f"Graph(directed={self.directed}, "
            f"nodes={len(self)}, node_ids={self.nodes()})"
        )