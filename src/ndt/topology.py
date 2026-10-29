
import networkx as nx


def create_baseline_topology() -> nx.Graph:
    """Create the baseline network with link capacity and propagation delay."""

    graph = nx.Graph()

    # Add network nodes (representing routers)
    nodes = ["A", "B", "C", "D", "E", "F"]
    graph.add_nodes_from(nodes)

    # Link format: (source, destination, capacity_mbps, delay_ms)
    links = [
        ("A", "B", 100, 5),
        ("A", "D", 80, 8),
        ("B", "C", 100, 4),
        ("B", "E", 60, 10),
        ("C", "F", 100, 6),
        ("D", "E", 80, 3),
        ("E", "F", 70, 5),
    ]

    for source, destination, capacity, delay in links:
        graph.add_edge(
            source,
            destination,
            capacity_mbps=capacity,
            delay_ms=delay,
        )

    return graph
