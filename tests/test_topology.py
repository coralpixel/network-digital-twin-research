
from ndt.topology import create_baseline_topology


def test_baseline_topology_nodes_and_links():
    graph = create_baseline_topology()

    assert graph.number_of_nodes() == 6
    assert graph.number_of_edges() == 7


def test_link_attributes_exist():
    graph = create_baseline_topology()

    for _, _, data in graph.edges(data=True):
        assert data["capacity_mbps"] > 0
        assert data["delay_ms"] > 0


def test_baseline_is_connected():
    graph = create_baseline_topology()

    assert graph.number_of_nodes() > 0
    assert __import__("networkx").is_connected(graph)
