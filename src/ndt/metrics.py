
import networkx as nx


def analyze_structure(graph: nx.Graph) -> dict:
    """Calculate structural metrics for a network state."""

    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()

    if node_count == 0:
        return {
            "node_count": 0,
            "edge_count": edge_count,
            "component_count": 0,
            "is_connected": False,
            "largest_component_fraction": 0.0,
            "unreachable_pairs": 0,
            "average_shortest_path_length": None,
        }

    components = list(nx.connected_components(graph))
    largest_size = max(len(component) for component in components)

    # Count unordered node pairs that cannot reach one another.
    total_pairs = node_count * (node_count - 1) // 2
    reachable_pairs = sum(
        len(component) * (len(component) - 1) // 2
        for component in components
    )
    unreachable_pairs = total_pairs - reachable_pairs

    # Average shortest path is defined here over reachable pairs only.
    path_lengths = dict(nx.all_pairs_shortest_path_length(graph))
    distances = [
        distance
        for source, destinations in path_lengths.items()
        for destination, distance in destinations.items()
        if source != destination
    ]

    average_path_length = (
        sum(distances) / len(distances) if distances else None
    )

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "component_count": len(components),
        "is_connected": nx.is_connected(graph),
        "largest_component_fraction": largest_size / node_count,
        "unreachable_pairs": unreachable_pairs,
        "average_shortest_path_length": average_path_length,
    }


def compare_structures(
    baseline: nx.Graph,
    simulated: nx.Graph,
) -> dict:
    """Compare baseline and simulated network structures."""

    before = analyze_structure(baseline)
    after = analyze_structure(simulated)

    return {
        "baseline": before,
        "simulated": after,
        "changes": {
            "nodes_removed": before["node_count"] - after["node_count"],
            "links_removed": before["edge_count"] - after["edge_count"],
            "components_change": (
                after["component_count"] - before["component_count"]
            ),
            "unreachable_pairs_change": (
                after["unreachable_pairs"] - before["unreachable_pairs"]
            ),
            "largest_component_fraction_change": (
                after["largest_component_fraction"]
                - before["largest_component_fraction"]
            ),
        },
    }
