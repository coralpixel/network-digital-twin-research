
import networkx as nx

from ndt.topology import create_baseline_topology
from ndt.twin import NetworkDigitalTwin
from ndt.failures import simulate_link_failure, simulate_node_failure
from ndt.metrics import analyze_structure, compare_structures


def test_baseline_structure():
    graph = create_baseline_topology()
    result = analyze_structure(graph)

    assert result["node_count"] == 6
    assert result["edge_count"] == 7
    assert result["component_count"] == 1
    assert result["is_connected"] is True
    assert result["unreachable_pairs"] == 0


def test_link_failure_impact():
    twin = NetworkDigitalTwin(create_baseline_topology())
    simulate_link_failure(twin, "B", "C")

    result = compare_structures(twin.baseline, twin.twin)

    assert result["changes"]["links_removed"] == 1
    assert result["simulated"]["component_count"] == 1
    assert result["simulated"]["unreachable_pairs"] == 0


def test_node_failure_impact():
    twin = NetworkDigitalTwin(create_baseline_topology())
    simulate_node_failure(twin, "C")

    result = compare_structures(twin.baseline, twin.twin)

    assert result["changes"]["nodes_removed"] == 1
    assert result["simulated"]["node_count"] == 5


def test_disconnected_graph():
    graph = nx.Graph()
    graph.add_edges_from([("A", "B"), ("C", "D")])

    result = analyze_structure(graph)

    assert result["component_count"] == 2
    assert result["is_connected"] is False
    assert result["unreachable_pairs"] == 4
