
import networkx as nx


def calculate_link_loads(graph, traffic_matrix):
    """
    Distribute traffic demands over shortest-delay paths.

    Paths are calculated for analysis in the supplied graph.
    This is not a self-healing or SDN rerouting controller.
    """
    link_loads = {
        (min(u, v), max(u, v)): 0.0
        for u, v in graph.edges()
    }

    for (source, destination), demand in traffic_matrix.items():
        if source not in graph or destination not in graph:
            continue

        try:
            path = nx.dijkstra_path(
                graph,
                source,
                destination,
                weight="delay_ms",
            )
        except nx.NetworkXNoPath:
            continue

        for index in range(len(path) - 1):
            u, v = path[index], path[index + 1]
            edge = (min(u, v), max(u, v))
            link_loads[edge] += demand

    return link_loads


def calculate_link_utilization(graph, link_loads):
    """Calculate utilization as load divided by link capacity."""
    utilization = {}

    for u, v, data in graph.edges(data=True):
        edge = (min(u, v), max(u, v))
        capacity = data["capacity_mbps"]

        if capacity <= 0:
            raise ValueError("Link capacity must be positive.")

        utilization[edge] = link_loads.get(edge, 0.0) / capacity

    return utilization


def calculate_link_latency(graph, link_loads):
    """
    Estimate link latency using propagation delay and an
    M/M/1-inspired queueing approximation.

    Latency is reported in milliseconds.
    Queueing estimates become very large near saturation.
    """
    latencies = {}

    for u, v, data in graph.edges(data=True):
        edge = (min(u, v), max(u, v))
        capacity = data["capacity_mbps"]
        load = link_loads.get(edge, 0.0)

        if capacity <= 0:
            raise ValueError("Link capacity must be positive.")

        utilization = load / capacity
        propagation = data["delay_ms"]

        if utilization >= 1.0:
            latencies[edge] = float("inf")
        else:
            queueing_delay = (
                propagation * utilization / (1.0 - utilization)
            )
            latencies[edge] = propagation + queueing_delay

    return latencies


def estimate_packet_loss(graph, link_loads):
    """
    Estimate overload-related loss using utilization.

    This is a simplified model, not a packet-level simulation.
    """
    losses = {}

    for u, v, data in graph.edges(data=True):
        edge = (min(u, v), max(u, v))
        capacity = data["capacity_mbps"]
        load = link_loads.get(edge, 0.0)

        if capacity <= 0:
            raise ValueError("Link capacity must be positive.")

        utilization = load / capacity

        # Simplified overload-loss estimate.
        losses[edge] = min(
            1.0,
            max(0.0, (utilization - 0.9) / 0.1),
        )

    return losses


def analyze_performance(graph, traffic_matrix):
    """Calculate load, utilization, latency, and loss for a scenario."""
    link_loads = calculate_link_loads(graph, traffic_matrix)
    utilization = calculate_link_utilization(graph, link_loads)
    latency = calculate_link_latency(graph, link_loads)
    packet_loss = estimate_packet_loss(graph, link_loads)

    return {
        "link_loads_mbps": link_loads,
        "link_utilization": utilization,
        "link_latency_ms": latency,
        "estimated_packet_loss": packet_loss,
        "maximum_utilization": max(utilization.values(), default=0.0),
        "average_utilization": (
            sum(utilization.values()) / len(utilization)
            if utilization else 0.0
        ),
        "overloaded_links": [
            edge for edge, value in utilization.items()
            if value >= 1.0
        ],
        "unreachable_demands": sum(
            1
            for (source, destination) in traffic_matrix
            if source not in graph
            or destination not in graph
            or not nx.has_path(graph, source, destination)
        ),
    }
