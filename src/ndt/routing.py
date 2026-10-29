
import networkx as nx
from collections import deque


def bfs_shortest_path(
    graph: nx.Graph,
    source: str,
    destination: str,
) -> list[str] | None:
    """Find a minimum-hop path using BFS."""

    if source not in graph or destination not in graph:
        raise ValueError("Source or destination node does not exist.")

    queue = deque([[source]])
    visited = {source}

    while queue:
        path = queue.popleft()
        current = path[-1]

        if current == destination:
            return path

        for neighbor in sorted(graph.neighbors(current)):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None


def dijkstra_shortest_path(
    graph: nx.Graph,
    source: str,
    destination: str,
) -> list[str] | None:
    """Find a minimum-delay path using Dijkstra's algorithm."""

    if source not in graph or destination not in graph:
        raise ValueError("Source or destination node does not exist.")

    for _, _, data in graph.edges(data=True):
        if "delay_ms" not in data or data["delay_ms"] < 0:
            raise ValueError(
                "Every link must have a non-negative delay_ms."
            )

    try:
        return nx.dijkstra_path(
            graph,
            source=source,
            target=destination,
            weight="delay_ms",
        )
    except nx.NetworkXNoPath:
        return None


def calculate_path_delay(
    graph: nx.Graph,
    path: list[str] | None,
) -> float | None:
    """Calculate total propagation delay along a path."""

    if path is None:
        return None

    return sum(
        graph[path[i]][path[i + 1]]["delay_ms"]
        for i in range(len(path) - 1)
    )


def compare_routing_algorithms(
    graph: nx.Graph,
    source: str,
    destination: str,
) -> dict:
    """Compare BFS and Dijkstra paths."""

    bfs_path = bfs_shortest_path(graph, source, destination)
    dijkstra_path = dijkstra_shortest_path(
        graph, source, destination
    )

    return {
        "source": source,
        "destination": destination,
        "bfs_path": bfs_path,
        "bfs_hops": (
            len(bfs_path) - 1 if bfs_path is not None else None
        ),
        "bfs_delay_ms": calculate_path_delay(graph, bfs_path),
        "dijkstra_path": dijkstra_path,
        "dijkstra_hops": (
            len(dijkstra_path) - 1
            if dijkstra_path is not None else None
        ),
        "dijkstra_delay_ms": calculate_path_delay(
            graph, dijkstra_path
        ),
    }
