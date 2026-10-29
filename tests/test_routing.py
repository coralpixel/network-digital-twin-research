
import networkx as nx
import pytest

from ndt.topology import create_baseline_topology
from ndt.twin import NetworkDigitalTwin
from ndt.failures import simulate_link_failure
from ndt.routing import (
    bfs_shortest_path,
    dijkstra_shortest_path,
    calculate_path_delay,
    compare_routing_algorithms,
)


def test_bfs_shortest_path():
    graph = create_baseline_topology()

    path = bfs_shortest_path(graph, "A", "F")

    assert path is not None
    assert path[0] == "A"
    assert path[-1] == "F"
    assert len(path) - 1 == nx.shortest_path_length(
        graph, "A", "F"
    )


def test_dijkstra_shortest_path():
    graph = create_baseline_topology()

    path = dijkstra_shortest_path(graph, "A", "F")

    assert path is not None
    assert calculate_path_delay(graph, path) == pytest.approx(
        nx.dijkstra_path_length(
            graph, "A", "F", weight="delay_ms"
        )
    )


def test_routing_after_link_failure():
    twin = NetworkDigitalTwin(create_baseline_topology())

    simulate_link_failure(twin, "B", "C")

    path = dijkstra_shortest_path(twin.twin, "A", "F")

    assert path is not None
    assert path[0] == "A"
    assert path[-1] == "F"
    assert not any(
        set((path[i], path[i + 1])) == {"B", "C"}
        for i in range(len(path) - 1)
    )


def test_disconnected_network():
    graph = nx.Graph()
    graph.add_nodes_from(["A", "B"])

    assert bfs_shortest_path(graph, "A", "B") is None
    assert dijkstra_shortest_path(graph, "A", "B") is None


def test_invalid_node():
    graph = create_baseline_topology()

    with pytest.raises(ValueError):
        bfs_shortest_path(graph, "A", "Z")


def test_compare_algorithms():
    graph = create_baseline_topology()

    result = compare_routing_algorithms(graph, "A", "F")

    assert result["bfs_hops"] == 3
    assert result["dijkstra_delay_ms"] == pytest.approx(15.0)
