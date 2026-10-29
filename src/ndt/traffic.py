
import random

import networkx as nx


def generate_traffic_matrix(
    graph: nx.Graph,
    seed: int = 42,
    min_demand_mbps: float = 2.0,
    max_demand_mbps: float = 15.0,
) -> dict[tuple[str, str], float]:
    """Generate reproducible demands for every unordered node pair."""

    if min_demand_mbps < 0:
        raise ValueError("Minimum demand cannot be negative.")

    if max_demand_mbps < min_demand_mbps:
        raise ValueError("Maximum demand must be >= minimum demand.")

    nodes = sorted(graph.nodes())
    rng = random.Random(seed)
    traffic = {}

    for i, source in enumerate(nodes):
        for destination in nodes[i + 1:]:
            demand = rng.uniform(min_demand_mbps, max_demand_mbps)
            traffic[(source, destination)] = round(demand, 3)

    return traffic
